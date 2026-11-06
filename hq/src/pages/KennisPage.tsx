/**
 * KENNIS (v35): alles wat is opgeslagen op één plek. Overzicht · Geheugen · Threads · Projectchat · Documenten · Zoeken.
 * De gegevens komen uit services/kennis.ts en services/threads.ts (projectbestanden via de files-capability).
 * Alle tekst is data: Markdown via components/shared/Md.tsx, nooit als HTML.
 */
import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { ArrowLeft, Brain, Download, FileText, FolderOpen, Image as ImageIcon, Library, MessageSquare, MessagesSquare, Paperclip, RefreshCw, Search, X, LayoutDashboard } from 'lucide-react';
import { Md, type MdLink } from '../components/shared/Md';
import { Berichten, openGesprek, volgLink } from '../components/shared/Gesprek';
import { useThreads, stateOf, wanneerNl, loadGesprek, type GesprekLees, type ThreadState } from '../services/threads';
import { useLive } from '../services/live';
import { useGame } from '../store/useGame';
import { laadKennis, useCoach } from '../services/coach';
import { treffers, vouw, zoekTermen } from '../lib/tekst';
import {
  useKennis, useKennisNav, bezoekKennis, openKennis, vindNotitie, geledenNl, datumNl, groepVanThread, groepVanBestand, artifactRijen,
  zoekKennis, knipsel, leesBestand, downloadBestand, laadBeeld,
  SOORT_NAAM, INDEX, GROEPEN, BESTAND_GROEPEN, ZOEK_FILTERS,
  type KennisTab, type Laad, type Notitie, type Beeld, type Bestand, type BestandLees, type ZoekGroep, type ZoekItem,
} from '../services/kennis';

const TABS: { id: KennisTab; label: string; icon: typeof Search; uitleg: string }[] = [
  { id: 'overzicht', label: 'Overzicht', icon: LayoutDashboard, uitleg: 'Wat er is opgeslagen, de vaste regels en het nieuwste' },
  { id: 'geheugen', label: 'Geheugen', icon: Brain, uitleg: 'Alle regels en lessen uit het projectgeheugen' },
  { id: 'threads', label: 'Threads', icon: MessagesSquare, uitleg: 'Elke thread met het hele gesprek' },
  { id: 'projectchat', label: 'Projectchat', icon: MessageSquare, uitleg: 'De hele projectchat' },
  { id: 'documenten', label: 'Documenten', icon: FolderOpen, uitleg: 'Artifacts, bestanden, beelden en bijlagen' },
  { id: 'zoeken', label: 'Zoeken', icon: Search, uitleg: 'Zoek door alles heen' },
];
const NIET_OPGEHAALD = 'Nog niet opgehaald. Dit wordt elk uur bijgewerkt.';
const GEEN_TOEGANG = 'Open de HQ in claude.ai om dit te zien.';
const nl = (n: number) => n.toLocaleString('nl-NL');

/* ---------- kleine bouwstenen ---------- */
function Leeg({ children, icon: Icon = FolderOpen }: { children: ReactNode; icon?: typeof Search }) {
  return <div className="rounded-2xl border border-white/10 bg-white/[.03] p-6 text-center text-[14px] leading-relaxed text-slate-300"><Icon size={22} className="mx-auto mb-2 text-slate-500" />{children}</div>;
}
/** wat je ziet zolang een bestand er niet is */
function Stand<T>({ l, children }: { l: Laad<T>; children: (d: T) => ReactNode }) {
  if (l.data) return <>{children(l.data)}</>;
  if (l.fase === 'geen-toegang') return <Leeg>{GEEN_TOEGANG}</Leeg>;
  if (l.fase === 'ontbreekt') return <Leeg>{NIET_OPGEHAALD}</Leeg>;
  if (l.fase === 'fout') return <Leeg>Dit kon nu niet geladen worden. <button className="text-sky-300 underline hover:text-white" onClick={() => void bezoekKennis(true)}>Opnieuw proberen</button></Leeg>;
  return <Leeg icon={RefreshCw}>Laden…</Leeg>;
}
function Kop({ icon: Icon, children, extra }: { icon: typeof Search; children: ReactNode; extra?: ReactNode }) {
  return <div className="mb-2 flex items-center gap-2"><Icon size={17} className="shrink-0 text-orange-300" /><h2 className="min-w-0 flex-1 font-display text-[17px] font-bold text-white">{children}</h2>{extra}</div>;
}
function Veld({ value, onChange, placeholder, groot }: { value: string; onChange: (v: string) => void; placeholder: string; groot?: boolean }) {
  return (
    <div className="relative">
      <Search size={groot ? 18 : 15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
      <input type="search" value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} aria-label={placeholder}
        className={`w-full rounded-xl border border-white/10 bg-[#0b1230] text-white placeholder:text-slate-500 focus:border-sky-400/60 focus:outline-none ${groot ? 'py-3 pl-10 pr-3 text-[16px]' : 'py-2 pl-9 pr-3 text-[14px]'}`} />
    </div>
  );
}
const STAND: Record<ThreadState, { t: string; c: string }> = {
  working: { t: 'bezig', c: 'bg-sky-500/20 text-sky-300' }, blocked: { t: 'wacht op jou', c: 'bg-orange-500/20 text-orange-300' },
  review_ready: { t: 'klaar voor jou', c: 'bg-amber-500/20 text-amber-300' }, done: { t: 'klaar', c: 'bg-emerald-500/15 text-emerald-300' },
  failed: { t: 'mislukt', c: 'bg-red-500/20 text-red-300' }, stopped: { t: 'gestopt', c: 'bg-slate-500/20 text-slate-300' },
};
const SOORT_KLEUR: Record<string, string> = { project: 'bg-sky-500/15 text-sky-300', feedback: 'bg-orange-500/15 text-orange-300', user: 'bg-violet-500/15 text-violet-300', reference: 'bg-emerald-500/15 text-emerald-300' };
const grootte = (n?: number) => (n == null ? '' : n < 1024 ? `${n} B` : n < 1048576 ? `${Math.round(n / 1024)} kB` : `${(n / 1048576).toFixed(1).replace('.', ',')} MB`);

/** links in notities en documenten: notities binnen Kennis, threads in het gesprekspaneel, bestanden in de lezer */
function useLinks() {
  const toast = useGame((s) => s.toast);
  return (l: MdLink) => {
    if (l.soort === 'notitie') {
      const n = vindNotitie(useKennis.getState().geheugen.data, l.naam);
      if (n) openKennis({ tab: 'geheugen', notitie: n, hl: undefined }); else toast('Die notitie staat niet (meer) in het geheugen.', 'info');
    } else volgLink(l);
  };
}

/** tekst met de zoekwoorden gemarkeerd (zonder Markdown: voor knipsels) */
function Gemarkeerd({ tekst, termen }: { tekst: string; termen: string[] }) {
  const delen = useMemo(() => {
    const h = treffers(vouw(tekst), termen); const uit: ReactNode[] = []; let i = 0;
    h.forEach(([a, b], n) => { if (a > i) uit.push(tekst.slice(i, a)); uit.push(<mark key={n} className="rounded-sm bg-amber-300/30 px-px text-amber-50">{tekst.slice(a, b)}</mark>); i = b; });
    if (i < tekst.length) uit.push(tekst.slice(i));
    return uit;
  }, [tekst, termen]);
  return <>{delen}</>;
}

/* ================= de pagina ================= */
export default function KennisPage() {
  const tab = useKennisNav((s) => s.tab);
  const go = (t: KennisTab) => useKennisNav.setState({ tab: t });
  useEffect(() => { void bezoekKennis(); }, []);
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => { box.current?.scrollIntoView({ block: 'start' }); }, [tab]);
  return (
    <div ref={box} translate="no" className="mx-auto max-w-6xl space-y-4 p-3 md:p-6">
      <div className="panel relative overflow-hidden p-4 md:p-5">
        <div className="absolute inset-0 bg-gradient-to-r from-sky-500/15 via-transparent to-orange-500/10" />
        <div className="relative flex items-center gap-4">
          <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-sky-500/15 text-sky-300 ring-2 ring-sky-400/60"><Library size={28} /></span>
          <div className="min-w-0">
            <h1 className="font-display text-2xl font-bold text-white md:text-3xl">Kennis</h1>
            <p className="text-[14px] text-slate-300">Alles wat is opgeslagen: het geheugen met alle regels, elke thread, de projectchat, documenten en beelden.</p>
          </div>
        </div>
      </div>
      <div className="-mx-3 flex gap-2 overflow-x-auto px-3 pb-1" role="tablist">
        {TABS.map(({ id, label, icon: Icon, uitleg }) => (
          <button key={id} role="tab" aria-selected={tab === id} title={uitleg} onClick={() => go(id)} className={`relative flex shrink-0 items-center gap-2 rounded-full px-4 py-2 text-[14px] font-semibold ${tab === id ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>
            <Icon size={16} />{label}
          </button>
        ))}
      </div>
      {tab === 'overzicht' && <Overzicht />}
      {tab === 'geheugen' && <GeheugenTab />}
      {tab === 'threads' && <ThreadsTab />}
      {tab === 'projectchat' && <ProjectchatTab />}
      {tab === 'documenten' && <DocumentenTab />}
      {tab === 'zoeken' && <ZoekenTab />}
    </div>
  );
}

/* ================= 1. Overzicht ================= */
function Overzicht() {
  const { geheugen, documenten, projectchat } = useKennis();
  const { threads, at, src } = useThreads();
  const onLink = useLinks();
  const [q, setQ] = useState('');
  const [alles, setAlles] = useState(false);
  const lijst = Object.values(threads);
  const berichten = lijst.reduce((s, t) => s + (t.msgs ?? 0), 0) + (projectchat ?? 0);
  const d = documenten.data; const g = geheugen.data;
  const tegels = [
    { n: g?.notities.length, label: 'notities', bij: g?.gemaakt, tab: 'geheugen' as const },
    { n: src === 'ok' ? lijst.length : undefined, label: 'threads', bij: at, tab: 'threads' as const },
    { n: src === 'ok' ? berichten : undefined, label: 'berichten', bij: at, tab: 'threads' as const },
    { n: d ? artifactRijen(d.artifacts).length + d.bestanden.length : undefined, label: 'documenten', bij: d?.gemaakt, tab: 'documenten' as const },
    { n: d?.beelden.length, label: 'beelden', bij: d?.gemaakt, tab: 'documenten' as const },
  ];
  const regels = g?.index ?? '';
  const r = regels.split('\n');
  const lang = r.length > 25;
  const nieuwste = useMemo(() => (g ? [...g.notities].sort((a, b) => (Date.parse(b.gewijzigd ?? '') || 0) - (Date.parse(a.gewijzigd ?? '') || 0)).slice(0, 5) : []), [g]);
  const gesprekken = useMemo(() => [...lijst].sort((a, b) => (Date.parse(b.last ?? '') || 0) - (Date.parse(a.last ?? '') || 0)).slice(0, 5), [threads]); // eslint-disable-line react-hooks/exhaustive-deps
  const zoek = (e: React.FormEvent) => { e.preventDefault(); if (q.trim()) openKennis({ tab: 'zoeken', zoek: q.trim() }); };
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
        {tegels.map((t) => (
          <button key={t.label} onClick={() => openKennis({ tab: t.tab })} className="panel p-3 text-left transition hover:-translate-y-0.5">
            <div className="font-display text-2xl font-bold text-white">{t.n == null ? '–' : nl(t.n)}</div>
            <div className="text-[13px] font-semibold text-slate-300">{t.label}</div>
            <div className="text-[11px] text-slate-500">{t.bij ? `bijgewerkt ${geledenNl(t.bij)}` : t.n == null ? 'nog niet opgehaald' : ''}</div>
          </button>
        ))}
      </div>
      <form onSubmit={zoek} className="panel flex flex-col gap-2 p-4 sm:flex-row">
        <div className="min-w-0 flex-1"><Veld groot value={q} onChange={setQ} placeholder="Zoek in alles: geheugen, gesprekken, documenten, cursus" /></div>
        <button className="btn-primary shrink-0 justify-center text-[14px]" type="submit"><Search size={16} />Zoeken</button>
      </form>
      <section className="panel p-4">
        <Kop icon={Brain} extra={g && <button className="text-[13px] text-sky-300 hover:text-white" onClick={() => openKennis({ tab: 'geheugen', notitie: INDEX })}>Openen</button>}>Regels en lessen voor goede video's</Kop>
        <Stand l={geheugen}>{() => regels.trim() ? (
          <div className="relative">
            <Md text={lang && !alles ? r.slice(0, 25).join('\n') : regels} onLink={onLink} className="text-[14px] leading-relaxed text-slate-200" />
            {lang && !alles && <div className="pointer-events-none absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#0d1430] to-transparent" />}
            {lang && <button className="btn-ghost mt-2 text-[13px]" onClick={() => setAlles((x) => !x)}>{alles ? 'Minder tonen' : `Alles tonen (${r.length} regels)`}</button>}
          </div>
        ) : <Leeg>{NIET_OPGEHAALD}</Leeg>}</Stand>
      </section>
      <div className="grid gap-4 md:grid-cols-2">
        <section className="panel p-4">
          <Kop icon={Brain}>Laatst bijgewerkt in het geheugen</Kop>
          <Stand l={geheugen}>{() => (
            <div className="space-y-1">
              {nieuwste.map((n) => (
                <button key={n.naam} onClick={() => openKennis({ tab: 'geheugen', notitie: n.naam, hl: undefined })} className="block w-full rounded-lg px-2 py-1.5 text-left hover:bg-white/5">
                  <div className="truncate text-[14px] font-semibold text-white">{n.titel}</div>
                  <div className="truncate text-[12px] text-slate-400">{geledenNl(n.gewijzigd)}{n.beschrijving ? ` · ${n.beschrijving}` : ''}</div>
                </button>
              ))}
            </div>
          )}</Stand>
        </section>
        <section className="panel p-4">
          <Kop icon={MessagesSquare}>Laatste gesprekken</Kop>
          {src === 'ok' ? (
            <div className="space-y-1">
              {gesprekken.map((t) => (
                <button key={t.id} onClick={() => openGesprek({ kind: 'thread', title: t.title, thread: t.id })} className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-left hover:bg-white/5">
                  <span className="min-w-0 flex-1"><span className="block truncate text-[14px] font-semibold text-white">{t.title}</span><span className="block text-[12px] text-slate-400">{wanneerNl(t.last)}{t.msgs ? ` · ${nl(t.msgs)} berichten` : ''}</span></span>
                  <span className={`chip shrink-0 ${STAND[stateOf(t)].c}`}>{STAND[stateOf(t)].t}</span>
                </button>
              ))}
            </div>
          ) : <Leeg>{src === 'geen-toegang' ? GEEN_TOEGANG : src === 'laden' ? 'Laden…' : NIET_OPGEHAALD}</Leeg>}
        </section>
      </div>
    </div>
  );
}

/* ================= 2. Geheugen ================= */
function GeheugenTab() {
  const geheugen = useKennis((s) => s.geheugen);
  const { notitie, hl } = useKennisNav();
  const [q, setQ] = useState('');
  const onLink = useLinks();
  const lezer = useRef<HTMLDivElement>(null);
  const g = geheugen.data;
  const termen = useMemo(() => zoekTermen(q), [q]);
  const lijst = useMemo(() => {
    if (!g) return [];
    const alle = [...g.notities].sort((a, b) => (Date.parse(b.gewijzigd ?? '') || 0) - (Date.parse(a.gewijzigd ?? '') || 0));
    if (!termen.length) return alle;
    return alle.filter((n) => { const h = vouw(`${n.titel} ${n.beschrijving} ${n.naam} ${n.tekst}`); return termen.every((t) => h.includes(t)); });
  }, [g, termen]);
  const open = notitie ?? INDEX;
  const n: Notitie | null = g ? (open === INDEX ? { naam: INDEX, bestand: 'MEMORY.md', titel: 'Overzicht van het geheugen', beschrijving: 'Alle vaste regels en lessen op een rij', tekst: g.index } : g.notities.find((x) => x.naam === open) ?? null) : null;
  // nieuwe notitie: bovenaan beginnen, of bij de eerste treffer
  useEffect(() => {
    const el = lezer.current; if (!el) return;
    el.scrollTop = 0;
    if (notitie && window.matchMedia('(max-width: 767px)').matches) el.scrollIntoView({ block: 'start' });
    const t = setTimeout(() => { const m = el.querySelector('mark[data-hl]'); if (m) m.scrollIntoView({ block: 'center' }); }, 60);
    return () => clearTimeout(t);
  }, [open, hl, notitie]);
  const kies = (naam: string) => useKennisNav.setState({ notitie: naam, hl: undefined });
  return (
    <Stand l={geheugen}>{(gh) => (
      <div className="grid gap-4 md:grid-cols-[minmax(0,340px)_minmax(0,1fr)]">
        <div className={`panel min-w-0 p-3 ${notitie ? 'hidden md:block' : ''}`}>
          <Veld value={q} onChange={setQ} placeholder={`Zoek in ${gh.notities.length} notities`} />
          <div className="mt-2 max-h-none space-y-1 md:max-h-[calc(100vh-290px)] md:overflow-y-auto md:pr-1">
            {!termen.length && (
              <button onClick={() => kies(INDEX)} data-active={open === INDEX} className="block w-full rounded-lg border border-orange-400/30 bg-orange-500/[.06] px-2.5 py-2 text-left hover:bg-orange-500/10 data-[active=true]:border-orange-400/70">
                <div className="text-[14px] font-semibold text-white">Overzicht van het geheugen</div>
                <div className="text-[12px] text-slate-400">Alle vaste regels en lessen op een rij</div>
              </button>
            )}
            {lijst.map((x) => (
              <button key={x.naam} onClick={() => kies(x.naam)} data-active={open === x.naam} className="block w-full rounded-lg px-2.5 py-2 text-left hover:bg-white/5 data-[active=true]:bg-white/[.08]">
                <div className="flex items-start gap-2">
                  <span className="min-w-0 flex-1 text-[14px] font-semibold leading-snug text-white">{termen.length ? <Gemarkeerd tekst={x.titel} termen={termen} /> : x.titel}</span>
                  {x.soort && <span className={`chip shrink-0 ${SOORT_KLEUR[x.soort]}`}>{SOORT_NAAM[x.soort]}</span>}
                </div>
                {x.beschrijving && <div className="line-clamp-2 text-[12px] leading-snug text-slate-400">{x.beschrijving}</div>}
                {x.gewijzigd && <div className="text-[11px] text-slate-500">{datumNl(x.gewijzigd)}</div>}
              </button>
            ))}
            {termen.length > 0 && !lijst.length && <div className="p-3 text-center text-[13px] text-slate-500">Geen notitie gevonden.</div>}
          </div>
        </div>
        <div ref={lezer} className={`panel min-w-0 scroll-mt-3 p-4 md:max-h-[calc(100vh-230px)] md:overflow-y-auto ${notitie ? '' : 'hidden md:block'}`}>
          <button className="btn-ghost mb-3 text-[13px] md:hidden" onClick={() => useKennisNav.setState({ notitie: null })}><ArrowLeft size={14} />Terug naar de lijst</button>
          {n ? (
            <article>
              <div className="mb-3 border-b border-white/10 pb-3">
                <div className="flex flex-wrap items-center gap-2">
                  <h2 className="font-display text-xl font-bold text-white">{n.titel}</h2>
                  {n.soort && <span className={`chip ${SOORT_KLEUR[n.soort]}`}>{SOORT_NAAM[n.soort]}</span>}
                </div>
                {n.beschrijving && <div className="mt-0.5 text-[13px] text-slate-400">{n.beschrijving}</div>}
                <div className="mt-0.5 text-[11px] text-slate-500">{n.naam === INDEX ? (gh.gemaakt ? `bijgewerkt ${geledenNl(gh.gemaakt)}` : '') : n.gewijzigd ? `gewijzigd ${datumNl(n.gewijzigd)}` : ''}</div>
              </div>
              {n.tekst.trim() ? <Md text={n.tekst} hl={hl ?? (termen.length ? termen : undefined)} onLink={onLink} className="text-[14px] leading-relaxed text-slate-200" /> : <Leeg>{NIET_OPGEHAALD}</Leeg>}
            </article>
          ) : <Leeg>Deze notitie staat niet (meer) in het geheugen.</Leeg>}
        </div>
      </div>
    )}</Stand>
  );
}

/* ================= 3. Threads ================= */
function ThreadsTab() {
  const { threads, src, at } = useThreads();
  const activity = useLive((s) => s.data.activity);
  const [q, setQ] = useState('');
  const termen = useMemo(() => zoekTermen(q), [q]);
  const groepen = useMemo(() => {
    const video = new Map<string, number>(); for (const a of activity) if (a.id && a.video != null) video.set(a.id, a.video);
    const per = new Map<string, typeof lijst>();
    const lijst = Object.values(threads).filter((t) => !termen.length || termen.every((w) => vouw(t.title).includes(w)));
    lijst.sort((a, b) => (Date.parse(b.last ?? '') || 0) - (Date.parse(a.last ?? '') || 0));
    for (const t of lijst) { const gr = groepVanThread(t.title, video.get(t.id)); per.set(gr, [...(per.get(gr) ?? []), t]); }
    return GROEPEN.map((gr) => ({ gr, lijst: per.get(gr) ?? [] })).filter((x) => x.lijst.length);
  }, [threads, activity, termen]);
  if (src !== 'ok') return <Leeg icon={MessagesSquare}>{src === 'geen-toegang' ? GEEN_TOEGANG : src === 'laden' ? 'Laden…' : src === 'fout' ? 'De threads konden nu niet geladen worden. Over een minuut wordt het opnieuw geprobeerd.' : NIET_OPGEHAALD}</Leeg>;
  const alle = Object.values(threads);
  return (
    <div className="space-y-4">
      <div className="panel flex flex-col gap-2 p-3 sm:flex-row sm:items-center">
        <div className="min-w-0 flex-1"><Veld value={q} onChange={setQ} placeholder="Filter op titel" /></div>
        <div className="shrink-0 text-[13px] text-slate-400">{nl(alle.length)} threads · {nl(alle.reduce((s, t) => s + (t.msgs ?? 0), 0))} berichten{at ? ` · bijgewerkt ${geledenNl(at)}` : ''}</div>
      </div>
      {!groepen.length && <Leeg icon={Search}>Geen thread gevonden.</Leeg>}
      {groepen.map(({ gr, lijst }) => (
        <section key={gr} className="panel p-3" data-groep={gr}>
          <div className="mb-1 flex items-center gap-2 px-1"><h2 className="font-display text-[16px] font-bold text-white">{gr}</h2><span className="text-[12px] text-slate-500">{lijst.length}</span></div>
          <div className="divide-y divide-white/[.05]">
            {lijst.map((t) => {
              const s = STAND[stateOf(t)];
              return (
                <button key={t.id} data-thread={t.id} onClick={() => openGesprek({ kind: 'thread', title: t.title, thread: t.id })} className="flex w-full items-center gap-3 rounded-lg px-2 py-2 text-left hover:bg-white/5">
                  <span className="min-w-0 flex-1">
                    <span className="block text-[14px] font-semibold leading-snug text-white">{t.title || 'Thread zonder titel'}</span>
                    <span className="block text-[12px] text-slate-400">{t.msgs != null ? `${nl(t.msgs)} berichten` : t.file === false ? 'nog niet opgehaald' : ''}{t.last ? ` · ${wanneerNl(t.last)}` : ''}</span>
                  </span>
                  <span className={`chip shrink-0 ${s.c}`}>{s.t}</span>
                </button>
              );
            })}
          </div>
        </section>
      ))}
    </div>
  );
}

/* ================= 4. Projectchat ================= */
function ProjectchatTab() {
  const [r, setR] = useState<GesprekLees | null>(null);
  const [poging, setPoging] = useState(0);
  useEffect(() => {
    let weg = false;
    void loadGesprek('projectchat').catch(() => ({ kind: 'fout' as const, code: 'fout' })).then((x) => { if (!weg) { setR(x); if (x.kind === 'ok') useKennis.setState({ projectchat: x.g.msgs.length }); } });
    return () => { weg = true; };
  }, [poging]);
  if (!r) return <Leeg icon={RefreshCw}>Projectchat laden…</Leeg>;
  if (r.kind === 'geen-toegang') return <Leeg icon={MessageSquare}>{GEEN_TOEGANG}</Leeg>;
  if (r.kind === 'ontbreekt') return <Leeg icon={MessageSquare}>{NIET_OPGEHAALD}</Leeg>;
  if (r.kind === 'fout') return <Leeg icon={MessageSquare}>De projectchat kon nu niet geladen worden. <button className="text-sky-300 underline hover:text-white" onClick={() => setPoging((p) => p + 1)}>Opnieuw proberen</button></Leeg>;
  return (
    <div className="panel overflow-hidden p-0">
      <div className="flex flex-wrap items-center gap-x-2 border-b border-white/10 px-4 py-3">
        <MessageSquare size={17} className="text-orange-300" />
        <h2 className="font-display text-[17px] font-bold text-white">Projectchat</h2>
        <span className="text-[12px] text-slate-400">{nl(r.g.msgs.length)} berichten{r.g.at ? ` · bijgewerkt ${wanneerNl(r.g.at)}` : ''}</span>
      </div>
      <Berichten key={r.g.id} g={r.g} waar="projectchat" onLink={volgLink} className="h-[calc(100vh-300px)] min-h-[420px]" />
    </div>
  );
}

/* ================= 5. Documenten ================= */
function DocumentenTab() {
  const documenten = useKennis((s) => s.documenten);
  const bestand = useKennisNav((s) => s.bestand);
  if (bestand) return <BestandLezer path={bestand.path} hl={bestand.hl} />;
  return <Stand l={documenten}>{(d) => <DocLijsten d={d} />}</Stand>;
}

function DocLijsten({ d }: { d: NonNullable<ReturnType<typeof useKennis.getState>['documenten']['data']> }) {
  const [meerA, setMeerA] = useState(false); const [meerB, setMeerB] = useState(false);
  const [groot, setGroot] = useState<{ b: Beeld; url: string } | null>(null);
  const toast = useGame((s) => s.toast);
  const artifacts = useMemo(() => artifactRijen(d.artifacts), [d]);
  const bestanden = useMemo(() => {
    const per = new Map<string, Bestand[]>();
    for (const b of [...d.bestanden].sort((x, y) => x.name.localeCompare(y.name, 'nl'))) { const gr = groepVanBestand(b); per.set(gr, [...(per.get(gr) ?? []), b]); }
    return BESTAND_GROEPEN.map((gr) => ({ gr, lijst: per.get(gr) ?? [] })).filter((x) => x.lijst.length);
  }, [d]);
  const bijlagen = useMemo(() => [...d.bijlagen].sort((a, b) => (Date.parse(b.at ?? '') || 0) - (Date.parse(a.at ?? '') || 0)), [d]);
  const dl = async (p: string) => { const m = await downloadBestand(p); if (m) toast(m, 'info'); };
  return (
    <div className="space-y-4">
      <section className="panel p-4">
        <Kop icon={FileText} extra={<span className="text-[12px] text-slate-500">{artifacts.length}</span>}>Documenten en artifacts</Kop>
        {!artifacts.length ? <Leeg>{NIET_OPGEHAALD}</Leeg> : (
          <div className="grid gap-x-4 md:grid-cols-2">
            {(meerA ? artifacts : artifacts.slice(0, 12)).map((a) => (
              <a key={a.url + a.title} href={a.url} target="_blank" rel="noreferrer" className="block rounded-lg px-2 py-1.5 hover:bg-white/5">
                <div className="truncate text-[14px] font-semibold text-sky-200">{a.title}</div>
                <div className="truncate text-[12px] text-slate-400">{datumNl(a.at)}{a.threadTitle ? ` · ${a.threadTitle}` : ''}</div>
              </a>
            ))}
          </div>
        )}
        {artifacts.length > 12 && <button className="btn-ghost mt-2 text-[13px]" onClick={() => setMeerA((x) => !x)}>{meerA ? 'Minder tonen' : `Alles tonen (${artifacts.length})`}</button>}
      </section>

      <section className="panel p-4">
        <Kop icon={FolderOpen} extra={<span className="text-[12px] text-slate-500">{d.bestanden.length}</span>}>Bestanden</Kop>
        {!bestanden.length ? <Leeg>{NIET_OPGEHAALD}</Leeg> : (
          <div className="grid gap-3 md:grid-cols-2">
            {bestanden.map(({ gr, lijst }) => (
              <div key={gr} className="rounded-xl bg-white/[.03] p-2">
                <div className="px-1 pb-1 text-[12px] font-bold uppercase tracking-wider text-slate-400">{gr}</div>
                {lijst.map((b) => (
                  <div key={b.path} className="flex items-center gap-2 rounded-lg px-1 py-1 hover:bg-white/5">
                    {b.soort === 'pdf' ? (
                      <>
                        <span className="min-w-0 flex-1"><span className="block truncate text-[13.5px] text-white">{b.name}</span><span className="block text-[11px] text-slate-500">PDF · {grootte(b.size)}</span></span>
                        <button className="btn-ghost shrink-0 !px-2 !py-1 text-[12px]" onClick={() => void dl(b.path)}><Download size={13} />Downloaden</button>
                      </>
                    ) : (
                      <button className="min-w-0 flex-1 text-left" onClick={() => openKennis({ bestand: { path: b.path } })} title={b.path}>
                        <span className="block truncate text-[13.5px] text-sky-200">{b.name}</span>
                        <span className="block truncate text-[11px] text-slate-500">{datumNl(b.mtime)}{b.size ? ` · ${grootte(b.size)}` : ''}</span>
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="panel p-4">
        <Kop icon={ImageIcon} extra={<span className="text-[12px] text-slate-500">{d.beelden.length}</span>}>Beelden van niels</Kop>
        {!d.beelden.length ? <Leeg>{NIET_OPGEHAALD}</Leeg> : (
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-6">
            {d.beelden.map((b) => <Beeldje key={b.path} b={b} onOpen={(url) => setGroot({ b, url })} />)}
          </div>
        )}
      </section>

      <section className="panel p-4">
        <Kop icon={Paperclip} extra={<span className="text-[12px] text-slate-500">{bijlagen.length}</span>}>Bijlagen uit gesprekken</Kop>
        {!bijlagen.length ? <Leeg>{NIET_OPGEHAALD}</Leeg> : (
          <div className="grid gap-x-4 md:grid-cols-2">
            {(meerB ? bijlagen : bijlagen.slice(0, 30)).map((b, i) => {
              const inhoud = <><span className="block truncate text-[13.5px] text-sky-200">{b.name}</span><span className="block truncate text-[11px] text-slate-500">{datumNl(b.at)}{b.threadTitle ? ` · ${b.threadTitle}` : ''}</span></>;
              return b.href
                ? <a key={i} href={b.href} target="_blank" rel="noreferrer" className="block rounded-lg px-2 py-1 hover:bg-white/5">{inhoud}</a>
                : <button key={i} disabled={!b.thread} onClick={() => b.thread && openGesprek(b.thread === 'projectchat' ? { kind: 'project', title: 'Projectchat', msg: b.msg } : { kind: 'thread', title: b.threadTitle ?? 'Thread', thread: b.thread, msg: b.msg })} className="block w-full rounded-lg px-2 py-1 text-left hover:bg-white/5">{inhoud}</button>;
            })}
          </div>
        )}
        {bijlagen.length > 30 && <button className="btn-ghost mt-2 text-[13px]" onClick={() => setMeerB((x) => !x)}>{meerB ? 'Minder tonen' : `Alles tonen (${bijlagen.length})`}</button>}
      </section>
      {groot && <GrootBeeld b={groot.b} url={groot.url} onClose={() => setGroot(null)} />}
    </div>
  );
}

/** een beeldje: pas gelezen als het in beeld komt (hooguit 3 tegelijk, zie laadBeeld), opgeruimd bij weggaan */
function Beeldje({ b, onOpen }: { b: Beeld; onOpen: (url: string) => void }) {
  const ref = useRef<HTMLButtonElement>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [fout, setFout] = useState(false);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    let weg = false; let u: string | null = null; const ac = new AbortController();
    const io = new IntersectionObserver((es) => {
      if (!es.some((e) => e.isIntersecting)) return;
      io.disconnect();
      laadBeeld(b.path, b.type, ac.signal).then((x) => { if (weg) URL.revokeObjectURL(x); else { u = x; setUrl(x); } }).catch(() => { if (!weg) setFout(true); });
    }, { rootMargin: '200px' });
    io.observe(el);
    return () => { weg = true; ac.abort(); io.disconnect(); if (u) URL.revokeObjectURL(u); };
  }, [b.path, b.type]);
  return (
    <button ref={ref} disabled={!url} onClick={() => url && onOpen(url)} data-beeld={url ? 'ok' : fout ? 'fout' : 'laden'} title={`${datumNl(b.mtime)} · ${grootte(b.size)}`} className="relative aspect-square overflow-hidden rounded-xl border border-white/10 bg-white/[.04] hover:border-sky-400/60">
      {url ? <img src={url} alt={`Beeld van ${datumNl(b.mtime)}`} decoding="async" className="h-full w-full object-cover" />
        : <span className="absolute inset-0 flex items-center justify-center text-[11px] text-slate-500">{fout ? 'Niet te laden' : <ImageIcon size={18} className="animate-pulse" />}</span>}
    </button>
  );
}
function GrootBeeld({ b, url, onClose }: { b: Beeld; url: string; onClose: () => void }) {
  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') { e.stopPropagation(); onClose(); } };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, [onClose]);
  return (
    <div className="fixed inset-0 z-[75] flex flex-col items-center justify-center gap-2 bg-black/85 p-4" onClick={onClose} role="dialog" aria-label="Beeld">
      <button className="absolute right-4 top-4 rounded-lg border border-white/20 p-2 text-white" aria-label="Sluiten" onClick={onClose}><X size={18} /></button>
      <img src={url} alt="" className="max-h-[85vh] max-w-full rounded-lg object-contain shadow-2xl" onClick={(e) => e.stopPropagation()} />
      <div className="text-[12px] text-slate-300">{datumNl(b.mtime)} · {grootte(b.size)}</div>
    </div>
  );
}

function BestandLezer({ path, hl }: { path: string; hl?: string[] }) {
  const [r, setR] = useState<BestandLees | null>(null);
  const [beeld, setBeeld] = useState<string | null>(null);
  const toast = useGame((s) => s.toast);
  const onLink = useLinks();
  const box = useRef<HTMLDivElement>(null);
  const info = useKennis((s) => s.documenten.data?.bestanden.find((b) => b.path === path));
  useEffect(() => {
    let weg = false; let u: string | null = null; setR(null); setBeeld(null);
    void leesBestand(path).then((x) => {
      if (weg) return; setR(x);
      if (x.kind === 'beeld') void laadBeeld(path, x.type).then((y) => { if (weg) URL.revokeObjectURL(y); else { u = y; setBeeld(y); } }).catch(() => {});
    });
    return () => { weg = true; if (u) URL.revokeObjectURL(u); };
  }, [path]);
  useEffect(() => {
    box.current?.scrollIntoView({ block: 'start' });
    if (r?.kind !== 'tekst' || !hl?.length) return;
    const t = setTimeout(() => box.current?.querySelector('mark[data-hl]')?.scrollIntoView({ block: 'center' }), 80);
    return () => clearTimeout(t);
  }, [r, hl]);
  const naam = info?.name ?? path.split('/').pop() ?? path;
  const dl = async () => { const m = await downloadBestand(path); if (m) toast(m, 'info'); };
  const isMd = /\.(md|markdown|txt)$/i.test(path) || !/\.[a-z0-9]{1,6}$/i.test(path);
  return (
    <div ref={box} className="panel scroll-mt-3 p-4">
      <div className="mb-3 flex flex-wrap items-center gap-2 border-b border-white/10 pb-3">
        <button className="btn-ghost text-[13px]" onClick={() => useKennisNav.setState({ bestand: null })}><ArrowLeft size={14} />Terug naar documenten</button>
        <div className="min-w-0 flex-1">
          <h2 className="truncate font-display text-lg font-bold text-white">{naam}</h2>
          <div className="truncate text-[12px] text-slate-500">{path}{info?.mtime ? ` · ${datumNl(info.mtime)}` : ''}</div>
        </div>
        <button className="btn-ghost shrink-0 text-[13px]" onClick={() => void dl()}><Download size={14} />Downloaden</button>
      </div>
      {!r ? <Leeg icon={RefreshCw}>Laden…</Leeg>
        : r.kind === 'tekst' ? (
          <>
            {r.afgekapt && <div className="mb-2 text-[12px] text-amber-300">Dit bestand is heel groot; hier staat het begin. Download het voor alles.</div>}
            <Md text={isMd ? r.tekst : '```\n' + r.tekst + '\n```'} hl={hl} onLink={onLink} className="text-[14px] leading-relaxed text-slate-200" />
          </>
        )
        : r.kind === 'pdf' ? <Leeg icon={FileText}>Dit is een PDF. <button className="text-sky-300 underline hover:text-white" onClick={() => void dl()}>Downloaden</button></Leeg>
        : r.kind === 'beeld' ? (beeld ? <img src={beeld} alt={naam} className="mx-auto max-h-[75vh] max-w-full rounded-lg object-contain" /> : <Leeg icon={ImageIcon}>Beeld laden…</Leeg>)
        : r.kind === 'binair' ? <Leeg icon={FileText}>Dit bestand kan hier niet getoond worden. <button className="text-sky-300 underline hover:text-white" onClick={() => void dl()}>Downloaden</button></Leeg>
        : r.kind === 'ontbreekt' ? <Leeg>Dit bestand is er niet (meer).</Leeg>
        : r.kind === 'geen-toegang' ? <Leeg>{GEEN_TOEGANG}</Leeg>
        : <Leeg>Het bestand kon nu niet gelezen worden.</Leeg>}
    </div>
  );
}

/* ================= 6. Zoeken ================= */
const GROEP_NAAM: Record<ZoekGroep, { t: string; c: string }> = {
  geheugen: { t: 'Geheugen', c: 'bg-orange-500/15 text-orange-300' }, gesprek: { t: 'Gesprek', c: 'bg-sky-500/15 text-sky-300' },
  document: { t: 'Document', c: 'bg-emerald-500/15 text-emerald-300' }, cursus: { t: 'Cursus', c: 'bg-violet-500/15 text-violet-300' },
};
function ZoekenTab() {
  const zoek = useKennisNav((s) => s.zoek);
  const k = useCoach((s) => s.kennis);
  const [q, setQ] = useState(zoek);
  const [filter, setFilter] = useState<'alles' | ZoekGroep>('alles');
  const [toon, setToon] = useState(50);
  const [los, setLos] = useState<ZoekItem | null>(null);
  useEffect(() => { void laadKennis(); }, []);
  // 250 ms na het typen pas zoeken
  useEffect(() => { const t = setTimeout(() => setQ(zoek), 250); return () => clearTimeout(t); }, [zoek]);
  const termen = useMemo(() => zoekTermen(q), [q]);
  const res = useMemo(() => (k && termen.length ? zoekKennis(k, termen) : null), [k, termen]);
  useEffect(() => { setToon(50); }, [q, filter]);
  const hits = res ? (filter === 'alles' ? res.hits : res.hits.filter((h) => h.it.groep === filter)) : [];
  const open = (it: ZoekItem) => {
    const b = it.f.bron;
    if (b?.type === 'geheugen') {
      const n = b.id === 'MEMORY' ? INDEX : vindNotitie(useKennis.getState().geheugen.data, b.id);
      if (n) { openKennis({ tab: 'geheugen', notitie: n, hl: termen }); return; }
    } else if (b?.type === 'gesprek') {
      const t = useThreads.getState().threads[b.id];
      openGesprek(b.id === 'projectchat' ? { kind: 'project', title: 'Projectchat', msg: b.msg } : { kind: 'thread', title: t?.title || it.f.doc.replace(/^Thread:\s*/, ''), thread: b.id, msg: b.msg });
      return;
    } else if (b?.type === 'document') { openKennis({ tab: 'documenten', bestand: { path: b.id, hl: termen } }); return; }
    setLos(it);
  };
  return (
    <div className="space-y-3">
      <div className="panel space-y-3 p-4">
        <Veld groot value={zoek} onChange={(v) => useKennisNav.setState({ zoek: v })} placeholder="Zoek in alles: geheugen, gesprekken, documenten, cursus" />
        <div className="flex flex-wrap gap-2">
          {ZOEK_FILTERS.map((f) => (
            <button key={f.id} onClick={() => setFilter(f.id)} className={`rounded-full px-3 py-1 text-[13px] font-semibold ${filter === f.id ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>
              {f.label}{res ? ` (${nl(res.tel[f.id])})` : ''}
            </button>
          ))}
        </div>
        {k?.uit === 'ingebouwd' && <div className="text-[12.5px] text-amber-300">{k.waarom === 'geen-files' || k.waarom === 'not_granted' ? `${GEEN_TOEGANG} Nu zoek je alleen in de ingebouwde cursus en werkwijze.` : `De volledige kennis is nog niet opgehaald (dit wordt elk uur bijgewerkt). Nu zoek je alleen in de ingebouwde cursus en werkwijze.`}</div>}
      </div>
      {!k ? <Leeg icon={RefreshCw}>Alle kennis laden…</Leeg>
        : !termen.length ? <Leeg icon={Search}>Typ een woord, bijvoorbeeld "abonneeroproep", "thumbnail" of "hook". Je zoekt in {nl(k.fragmenten.length)} stukjes.</Leeg>
        : !hits.length ? <Leeg icon={Search}>Niets gevonden voor "{q}".</Leeg>
        : (
          <>
            <div className="px-1 text-[12px] text-slate-500">{nl(hits.length)} treffers · {Math.max(1, Math.round(res!.ms))} ms</div>
            <div className="space-y-2">
              {hits.slice(0, toon).map(({ it }, i) => (
                <button key={i} data-groep={it.groep} onClick={() => open(it)} className="panel block w-full p-3 text-left transition hover:border-sky-400/40">
                  <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
                    <span className={`chip ${GROEP_NAAM[it.groep].c}`}>{GROEP_NAAM[it.groep].t}</span>
                    <span className="min-w-0 text-[14px] font-semibold text-white">{it.f.doc}</span>
                    {it.f.hoofdstuk && <span className="text-[12px] text-slate-400">· {it.f.hoofdstuk}</span>}
                  </div>
                  <div className="mt-1 text-[13px] leading-relaxed text-slate-300"><Gemarkeerd tekst={knipsel(it, termen)} termen={termen} /></div>
                </button>
              ))}
            </div>
            {hits.length > toon && <div className="text-center"><button className="btn-ghost text-[13px]" onClick={() => setToon((x) => x + 50)}>Meer ({nl(hits.length - toon)} over)</button></div>}
          </>
        )}
      {los && (
        <div className="fixed inset-0 z-[75] flex items-center justify-center bg-black/60 p-4" onClick={() => setLos(null)}>
          <div className="panel max-h-[85vh] w-full max-w-2xl overflow-y-auto p-5" onClick={(e) => e.stopPropagation()} role="dialog" aria-label={los.f.doc}>
            <div className="mb-2 flex items-start gap-2">
              <div className="min-w-0 flex-1"><div className="font-display text-lg font-bold text-white">{los.f.doc}</div><div className="text-[12px] text-slate-400">{los.f.hoofdstuk}{los.f.onderwerp ? ` · ${los.f.onderwerp}` : ''}</div></div>
              <button className="rounded-lg border border-white/10 p-1.5 text-slate-300 hover:text-white" aria-label="Sluiten" onClick={() => setLos(null)}><X size={16} /></button>
            </div>
            <Md text={los.f.tekst} hl={termen} className="text-[14px] leading-relaxed text-slate-200" />
          </div>
        </div>
      )}
    </div>
  );
}
