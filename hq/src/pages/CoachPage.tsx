/**
 * COACHKAMER: de eigen afdeling van de CEO Coach (blueprint v2.0, Deel 9).
 * Praat · Briefing (+ actieplan) · Doelen · Beslissingen · Agents · Rapporten · Kennis · Geheugen
 */
import { useEffect, useRef, useState } from 'react';
import { MessageCircle, Sunrise, Target, Gavel, Users, FileText, BookOpen, Brain, Send, RefreshCw, Check, X, Plus, Trash2 } from 'lucide-react';
import { useLive } from '../services/live';
import { useDb } from '../services/db';
import { order } from '../services/real';
import { useGame } from '../store/useGame';
import { threadUrl } from '../data/driftmark';
import { AfkeurKnop } from '../components/shared/Afkeuren';
import {
  useCoach, startCoach, vraag, parse, maakBriefing, maakRapport, onthoud, bewaarGeheugen, bewaarDoelen, nieuwBesluit, zetBesluit, bewaarGesprek,
  VAK, type Msg, type Fragment, type Doel, type Besluit, type Actie,
} from '../services/coach';

type Tab = 'praat' | 'briefing' | 'doelen' | 'besluiten' | 'agents' | 'rapporten' | 'kennis' | 'geheugen';
const TABS: { id: Tab; label: string; icon: typeof Send; uitleg: string }[] = [
  { id: 'praat', label: 'Praat met Claude', icon: MessageCircle, uitleg: 'Persoonlijk gesprek met je CEO Coach' },
  { id: 'briefing', label: 'Briefing', icon: Sunrise, uitleg: 'Dagoverzicht en actieplan (max 5 acties)' },
  { id: 'doelen', label: 'Doelen', icon: Target, uitleg: 'Jouw doelen en bedrijfsdoelen' },
  { id: 'besluiten', label: 'Beslissingen', icon: Gavel, uitleg: 'Wat op jouw goedkeuring wacht' },
  { id: 'agents', label: 'Agents', icon: Users, uitleg: 'Wat de Claude-threads doen en hun antwoorden' },
  { id: 'rapporten', label: 'Rapporten', icon: FileText, uitleg: 'Weekrapport, maandrapport, strategisch advies' },
  { id: 'kennis', label: 'Kennis', icon: BookOpen, uitleg: 'De kennisbank van de coach' },
  { id: 'geheugen', label: 'Geheugen', icon: Brain, uitleg: 'Wat de coach blijvend over jou en Driftmark weet' },
];

/** heel kleine markdown: ## kop, - lijst, **vet** */
export function Md({ text }: { text: string }) {
  const vet = (t: string) => t.split(/(\*\*[^*]+\*\*)/g).map((p, i) => (p.startsWith('**') ? <strong key={i} className="text-white">{p.slice(2, -2)}</strong> : p));
  return (
    <div className="space-y-1.5">
      {text.split('\n').map((l, i) => {
        if (/^#{1,4}\s/.test(l)) return <div key={i} className="pt-2 font-display text-[16px] font-bold text-orange-200">{l.replace(/^#+\s/, '')}</div>;
        if (/^\s*[-*•]\s/.test(l)) return <div key={i} className="flex gap-2 pl-1"><span className="text-orange-400">•</span><span>{vet(l.replace(/^\s*[-*•]\s/, ''))}</span></div>;
        if (/^\s*\d+[.)]\s/.test(l)) return <div key={i} className="pl-1">{vet(l)}</div>;
        return l.trim() ? <p key={i}>{vet(l)}</p> : null;
      })}
    </div>
  );
}

const NIVEAU = { 1: 'advies', 2: 'Claude doet het na jouw klik', 3: 'jouw besluit nodig' } as const;
const PRIO: Record<string, string> = { hoog: 'bg-red-500/20 text-red-300', middel: 'bg-orange-500/20 text-orange-300', laag: 'bg-sky-500/20 text-sky-300' };

export default function CoachPage() {
  const [tab, setTab] = useState<Tab>(() => { try { return (localStorage.getItem('coach-tab') as Tab) || 'praat'; } catch { return 'praat'; } });
  const go = (t: Tab) => { setTab(t); try { localStorage.setItem('coach-tab', t); } catch { /* */ } };
  const c = useCoach();
  const open = c.besluiten.filter((b) => b.status === 'open').length + useLive((s) => s.data.activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready').length);
  useEffect(() => { void startCoach(); }, []);

  return (
    <div className="mx-auto max-w-6xl space-y-4 p-3 md:p-6">
      <div className="panel relative overflow-hidden p-4 md:p-5">
        <div className="absolute inset-0 bg-gradient-to-r from-orange-500/15 via-transparent to-sky-500/10" />
        <div className="relative flex items-center gap-4">
          <img src="./img/c1_hoofdpersonage.jpg" alt="" className="h-16 w-16 shrink-0 rounded-2xl object-cover ring-2 ring-orange-400" />
          <div className="min-w-0">
            <div className="text-[12px] font-bold uppercase tracking-widest text-orange-300">CEO Coach</div>
            <h1 className="font-display text-2xl font-bold text-white md:text-3xl">Coachkamer</h1>
            <p className="text-[14px] text-slate-300">Claude denkt mee. De agents voeren uit. Jij beslist.</p>
          </div>
          <div className="ml-auto hidden text-right text-[13px] text-slate-400 md:block">
            {c.kanVragen ? <span className="text-green-300">● Coach staat aan</span> : c.kanVragen === false ? <span>Coach praat alleen in claude.ai</span> : 'opstarten…'}<br />
            {c.dbOk ? 'Geheugen opgeslagen in de database' : 'Geheugen: nog niet verbonden'}
          </div>
        </div>
      </div>

      <div className="-mx-3 flex gap-2 overflow-x-auto px-3 pb-1">
        {TABS.map(({ id, label, icon: Icon, uitleg }) => (
          <button key={id} title={uitleg} onClick={() => go(id)} className={`relative flex shrink-0 items-center gap-2 rounded-full px-4 py-2 text-[14px] font-semibold ${tab === id ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>
            <Icon size={16} />{label}
            {id === 'besluiten' && open > 0 && <span className="rounded-full bg-white/90 px-1.5 text-[12px] font-bold text-orange-600">{open}</span>}
          </button>
        ))}
      </div>

      {tab === 'praat' && <Praat />}
      {tab === 'briefing' && <BriefingTab />}
      {tab === 'doelen' && <Doelen />}
      {tab === 'besluiten' && <Besluiten />}
      {tab === 'agents' && <Agents />}
      {tab === 'rapporten' && <Rapporten />}
      {tab === 'kennis' && <KennisTab />}
      {tab === 'geheugen' && <GeheugenTab />}
    </div>
  );
}

/* ---------- acties-knoppen onder een antwoord ---------- */
function Vervolg({ text }: { text: string }) {
  const toast = useGame((s) => s.toast);
  const { acties, besluiten, onthoud: mem } = parse(text);
  const [gedaan, setGedaan] = useState<Record<string, boolean>>({});
  const klaar = (k: string) => setGedaan((g) => ({ ...g, [k]: true }));
  if (!acties.length && !besluiten.length && !mem.length) return null;
  return (
    <div className="mt-2 space-y-1.5 border-t border-white/10 pt-2">
      {acties.map((a) => (
        <button key={a} disabled={gedaan[a]} onClick={() => { order(a, toast); klaar(a); }} className="btn-primary block w-full !px-3 !py-1.5 text-left text-[13px] disabled:opacity-50">
          {gedaan[a] ? '✓ Verstuurd: ' : '▶ Laat Claude doen: '}{a}
        </button>
      ))}
      {besluiten.map((b) => (
        <button key={b} disabled={gedaan[b]} onClick={() => { void nieuwBesluit(b, 'coach').then(() => toast('Op je lijst met beslissingen gezet', 'success')).catch((e) => toast(String(e.message ?? e), 'warning')); klaar(b); }} className="block w-full rounded-xl border border-orange-400/50 px-3 py-1.5 text-left text-[13px] text-orange-200 hover:bg-orange-500/10 disabled:opacity-50">
          {gedaan[b] ? '✓ Op de lijst: ' : '⚖ Zet bij beslissingen: '}{b}
        </button>
      ))}
      {mem.map((m) => (
        <button key={m.tekst} disabled={gedaan[m.tekst]} onClick={() => { void onthoud(m.vak, m.tekst).then(() => toast('Onthouden', 'success')).catch((e) => toast(String(e.message ?? e), 'warning')); klaar(m.tekst); }} className="block w-full rounded-xl border border-sky-400/40 px-3 py-1.5 text-left text-[13px] text-sky-200 hover:bg-sky-500/10 disabled:opacity-50">
          {gedaan[m.tekst] ? '✓ Onthouden: ' : '🧠 Onthouden ('}{gedaan[m.tekst] ? '' : VAK[m.vak] + '): '}{m.tekst}
        </button>
      ))}
    </div>
  );
}

/* ---------- 1. Praat ---------- */
const VOORBEELD = ['Wat is nu het belangrijkste voor Driftmark?', 'Waarom blijven mijn lange video\'s achter bij de shorts?', 'Beoordeel het idee: elke dag 1 jaar jonger', 'Ik wil een tweede kanaal starten. Goed idee?', 'Welke agent heeft aandacht nodig?', 'Geef 3 titels en een hook voor video 4'];
function Praat() {
  const d = useLive((s) => s.data);
  const stats = useDb((s) => s.stats);
  const gesprek = useCoach((s) => s.gesprek);
  const kan = useCoach((s) => s.kanVragen);
  const [msgs, setMsgs] = useState<Msg[]>(gesprek);
  const [bron, setBron] = useState<Record<number, Fragment[]>>({});
  const [q, setQ] = useState('');
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { if (!msgs.length && gesprek.length) setMsgs(gesprek); }, [gesprek]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }, [msgs, busy]);

  const stuur = async (t: string, lang = false) => {
    if (!t.trim() || busy) return;
    const next: Msg[] = [...msgs, { role: 'user', content: t.trim() }];
    setMsgs(next); setQ(''); setBusy(true);
    const r = await vraag(next, d, stats, (txt) => setMsgs([...next, { role: 'assistant', content: txt }]), { lang });
    const done: Msg[] = [...next, { role: 'assistant', content: r.tekst }];
    setMsgs(done); setBron((b) => ({ ...b, [done.length - 1]: r.bronnen })); setBusy(false);
    void bewaarGesprek(done);
  };

  return (
    <div className="panel flex h-[min(680px,calc(100vh-260px))] min-h-[420px] flex-col overflow-hidden">
      <div className="flex-1 space-y-3 overflow-y-auto p-3 md:p-4">
        {!msgs.length && (
          <div className="space-y-3">
            <div className="max-w-[640px] rounded-2xl rounded-tl-sm bg-white/[.06] p-3 text-[15px] text-slate-100">Hoi niels. Ik ben je CEO Coach. Ik ken je cijfers, je video's, je threads en je regels, en ik zeg het eerlijk als iets geen goed idee is. Waar wil je het over hebben?</div>
            <div className="grid gap-2 sm:grid-cols-2">{VOORBEELD.map((s) => <button key={s} onClick={() => void stuur(s)} className="rounded-xl border border-hq-line px-3 py-2 text-left text-[14px] text-slate-200 hover:border-orange-400/60">{s}</button>)}</div>
          </div>
        )}
        {msgs.map((m, i) => {
          const p = m.role === 'assistant' ? parse(m.content) : null;
          return (
            <div key={i} className={`max-w-[92%] rounded-2xl p-3 text-[15px] md:max-w-[75%] ${m.role === 'user' ? 'ml-auto rounded-tr-sm bg-orange-500/85 text-white' : 'rounded-tl-sm bg-white/[.06] text-slate-100'}`}>
              {p ? <Md text={p.schoon || (busy ? '…' : '')} /> : <div className="whitespace-pre-line">{m.content}</div>}
              {p && !(busy && i === msgs.length - 1) && <Vervolg text={m.content} />}
              {bron[i]?.length ? <div className="mt-2 text-[12px] text-slate-400">Gezocht in: {[...new Set(bron[i].map((f) => f.doc))].join(', ')}</div> : null}
            </div>
          );
        })}
        {busy && msgs[msgs.length - 1]?.role === 'user' && <div className="w-16 rounded-2xl bg-white/[.06] p-3 text-center text-slate-400">•••</div>}
        <div ref={end} />
      </div>
      <form onSubmit={(e) => { e.preventDefault(); void stuur(q); }} className="flex flex-wrap gap-2 border-t border-hq-line p-3">
        <label htmlFor="ceo-q" className="sr-only">Bericht aan je coach</label>
        <input id="ceo-q" className="input min-w-0 flex-1 text-[15px]" value={q} onChange={(e) => setQ(e.target.value)} placeholder={kan === false ? 'Praten werkt op de pagina in claude.ai' : 'Vraag of overleg iets…'} />
        <button className="btn-primary !px-4" disabled={busy || !q.trim()} aria-label="Versturen"><Send size={17} /></button>
        <button type="button" className="btn-ghost !px-3 text-[13px]" disabled={busy || !q.trim()} onClick={() => void stuur(q, true)} title="Grondiger antwoord, duurt langer">Diepe analyse</button>
        {msgs.length > 0 && <button type="button" className="btn-ghost !px-3 text-[13px]" onClick={() => { setMsgs([]); setBron({}); void bewaarGesprek([]); }}>Nieuw gesprek</button>}
      </form>
    </div>
  );
}

/* ---------- 2. Briefing + actieplan ---------- */
function ActieKaart({ a }: { a: Actie }) {
  const toast = useGame((s) => s.toast);
  const [klaar, setKlaar] = useState(false);
  const n = (a.niveau ?? 1) as 1 | 2 | 3;
  return (
    <div className="rounded-2xl border border-hq-line bg-white/[.03] p-3">
      <div className="flex flex-wrap items-center gap-2"><span className={`rounded-full px-2 py-0.5 text-[12px] font-bold uppercase ${PRIO[a.prioriteit] ?? PRIO.middel}`}>{a.prioriteit}</span><span className="text-[12px] text-slate-400">{a.wie} · {NIVEAU[n] ?? ''}</span></div>
      <div className="mt-1.5 font-semibold text-white">{a.omschrijving}</div>
      <div className="mt-1 text-[13px] text-slate-300"><b className="text-slate-200">Waarom:</b> {a.reden}</div>
      <div className="text-[13px] text-slate-300"><b className="text-slate-200">Resultaat:</b> {a.resultaat}</div>
      {n === 2 && <button disabled={klaar} onClick={() => { order(a.omschrijving, toast); setKlaar(true); }} className="btn-primary mt-2 !px-3 !py-1.5 text-[13px] disabled:opacity-50">{klaar ? '✓ Verstuurd naar Claude' : '▶ Laat Claude dit doen'}</button>}
      {n === 3 && <button disabled={klaar} onClick={() => { void nieuwBesluit(a.omschrijving, 'coach', a.reden, a.omschrijving).then(() => toast('Bij beslissingen gezet', 'success')).catch((e) => toast(String(e.message ?? e), 'warning')); setKlaar(true); }} className="mt-2 rounded-xl border border-orange-400/50 px-3 py-1.5 text-[13px] text-orange-200 disabled:opacity-50">{klaar ? '✓ Bij beslissingen' : '⚖ Zet bij beslissingen'}</button>}
    </div>
  );
}
function Lijst({ titel, items }: { titel: string; items: string[] }) {
  if (!items?.length) return null;
  return (<div className="panel p-4"><div className="mb-2 font-display text-[16px] font-bold text-white">{titel}</div><ul className="space-y-1.5 text-[14px] text-slate-200">{items.map((x, i) => <li key={i} className="flex gap-2"><span className="text-orange-400">•</span>{x}</li>)}</ul></div>);
}
function BriefingTab() {
  const d = useLive((s) => s.data);
  const stats = useDb((s) => s.stats);
  const b = useCoach((s) => s.briefing);
  const kan = useCoach((s) => s.kanVragen);
  const [busy, setBusy] = useState(false);
  const [fout, setFout] = useState('');
  const vandaag = new Date().toISOString().slice(0, 10);
  const maak = async () => { setBusy(true); setFout(''); const r = await maakBriefing(d, stats); if (typeof r === 'string') setFout(r); setBusy(false); };
  const auto = useRef(false);
  useEffect(() => { if (kan && !auto.current && (!b || b.datum !== vandaag)) { auto.current = true; const t = setTimeout(() => void maak(), 1500); return () => clearTimeout(t); } }, [kan, b?.datum]); // eslint-disable-line react-hooks/exhaustive-deps
  return (
    <div className="space-y-3">
      <div className="panel flex flex-wrap items-center gap-3 p-4">
        <div className="min-w-0 flex-1">
          <div className="font-display text-xl font-bold text-white">Daily CEO Briefing</div>
          <div className="text-[13px] text-slate-400">{b ? `Gemaakt ${new Date(b.gemaakt).toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam', dateStyle: 'medium', timeStyle: 'short' })}` : 'Nog geen briefing'} · elke dag automatisch een nieuwe zodra je de coachkamer opent</div>
        </div>
        <button className="btn-primary flex items-center gap-2" disabled={busy || kan === false} onClick={() => void maak()}><RefreshCw size={16} className={busy ? 'animate-spin' : ''} />{busy ? 'Bezig…' : 'Vernieuwen'}</button>
      </div>
      {fout && <div className="panel border-red-400/40 p-3 text-[14px] text-red-200">{fout}</div>}
      {busy && !b && <div className="panel p-6 text-center text-slate-300">De coach leest je cijfers, video's en threads…</div>}
      {b && (
        <>
          <div className="panel glow-orange p-4 text-[16px] text-white">{b.samenvatting}</div>
          <div>
            <div className="mb-2 font-display text-lg font-bold text-white">Actieplan van vandaag</div>
            <div className="grid gap-3 md:grid-cols-2">{b.acties.map((a, i) => <ActieKaart key={i} a={a} />)}</div>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <Lijst titel="📈 Kanaal" items={b.kanaal} /><Lijst titel="🎬 Productie" items={b.productie} />
            <Lijst titel="🤖 Agents" items={b.agents} /><Lijst titel="💶 Financiën" items={b.financien} />
            <Lijst titel="⚠️ Problemen" items={b.problemen} /><Lijst titel="✨ Kansen" items={b.kansen} />
          </div>
        </>
      )}
    </div>
  );
}

/* ---------- 3. Doelen ---------- */
function Doelen() {
  const doelen = useCoach((s) => s.doelen);
  const toast = useGame((s) => s.toast);
  const yt = useLive((s) => s.data.youtube);
  const [t, setT] = useState(''); const [meet, setMeet] = useState<Doel['meet']>('abonnees'); const [n, setN] = useState(''); const [dl, setDl] = useState('');
  const nu = (m?: Doel['meet']) => (m === 'abonnees' ? yt?.subscribers : m === 'weergaven' ? yt?.views : m === 'videos' ? yt?.videoCount : undefined);
  const bewaar = (l: Doel[]) => void bewaarDoelen(l).catch((e) => toast(String(e.message ?? e), 'warning'));
  const voeg = () => { if (!t.trim()) return; bewaar([...doelen, { id: `${Date.now()}`, tekst: t.trim(), meet, ...(n ? { doel: Number(n) } : {}), ...(dl ? { deadline: dl } : {}) }]); setT(''); setN(''); setDl(''); };
  const voorstel = [{ tekst: '100 abonnees', meet: 'abonnees' as const, doel: 100 }, { tekst: '50.000 weergaven', meet: 'weergaven' as const, doel: 50000 }, { tekst: 'Elke week 1 lange video', meet: 'vrij' as const }];
  return (
    <div className="space-y-3">
      <div className="panel space-y-2 p-4">
        <div className="font-display text-lg font-bold text-white">Nieuw doel</div>
        <div className="flex flex-wrap gap-2">
          <input className="input min-w-[200px] flex-1" placeholder="Bijv. 100 abonnees vóór de kerst" value={t} onChange={(e) => setT(e.target.value)} />
          <select className="input w-auto" value={meet} onChange={(e) => setMeet(e.target.value as Doel['meet'])}><option value="abonnees">abonnees</option><option value="weergaven">weergaven</option><option value="videos">video's</option><option value="vrij">geen getal</option></select>
          {meet !== 'vrij' && <input className="input w-28" type="number" placeholder="doel" value={n} onChange={(e) => setN(e.target.value)} />}
          <input className="input w-auto" type="date" value={dl} onChange={(e) => setDl(e.target.value)} aria-label="Deadline" />
          <button className="btn-primary flex items-center gap-1" onClick={voeg}><Plus size={16} />Toevoegen</button>
        </div>
        {!doelen.length && <div className="flex flex-wrap gap-2 pt-1 text-[13px]"><span className="text-slate-400">Snel:</span>{voorstel.map((v) => <button key={v.tekst} className="rounded-full bg-white/5 px-3 py-1 text-slate-200 hover:bg-white/10" onClick={() => bewaar([...doelen, { id: `${Date.now()}${v.tekst.length}`, ...v }])}>{v.tekst}</button>)}</div>}
      </div>
      {doelen.map((g) => {
        const cur = nu(g.meet); const pct = g.doel && cur != null ? Math.min(100, Math.round((cur / g.doel) * 100)) : null;
        return (
          <div key={g.id} className="panel flex items-center gap-3 p-4">
            <button aria-label="Gehaald" onClick={() => bewaar(doelen.map((x) => (x.id === g.id ? { ...x, klaar: !x.klaar } : x)))} className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full border-2 ${g.klaar || pct === 100 ? 'border-green-400 bg-green-500/30 text-green-200' : 'border-slate-500'}`}>{(g.klaar || pct === 100) && <Check size={15} />}</button>
            <div className="min-w-0 flex-1">
              <div className="font-semibold text-white">{g.tekst}</div>
              <div className="text-[13px] text-slate-400">{cur != null && g.doel ? `${cur.toLocaleString('nl-NL')} van ${g.doel.toLocaleString('nl-NL')} ${g.meet}` : 'Zelf afvinken'}{g.deadline ? ` · vóór ${new Date(g.deadline).toLocaleDateString('nl-NL')}` : ''}</div>
              {pct != null && <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-gradient-to-r from-orange-500 to-amber-300" style={{ width: `${pct}%` }} /></div>}
            </div>
            <button aria-label="Verwijderen" onClick={() => bewaar(doelen.filter((x) => x.id !== g.id))} className="p-1 text-slate-500 hover:text-red-300"><Trash2 size={16} /></button>
          </div>
        );
      })}
    </div>
  );
}

/* ---------- 4. Beslissingen ---------- */
function Besluiten() {
  const besluiten = useCoach((s) => s.besluiten);
  const act = useLive((s) => s.data.activity);
  const toast = useGame((s) => s.toast);
  const taken = act.filter((a) => a.state === 'blocked' || a.state === 'review_ready');
  const kies = (b: Besluit, ok: boolean) => {
    void zetBesluit(b, ok ? 'goedgekeurd' : 'afgewezen').catch((e) => toast(String(e.message ?? e), 'warning'));
    order(`${ok ? 'GOEDGEKEURD door de CEO' : 'AFGEWEZEN door de CEO'}: ${b.vraag}${ok && b.opdracht ? `\nVoer uit: ${b.opdracht}` : ''}`, toast);
  };
  const open = besluiten.filter((b) => b.status === 'open');
  const oud = besluiten.filter((b) => b.status !== 'open').slice(0, 10);
  return (
    <div className="space-y-3">
      <div className="text-[14px] text-slate-400">Hier staat alles wat jouw besluit nodig heeft (niveau 3): publiceren, uitgaven, grote strategiekeuzes, en taken die op jou wachten.</div>
      {taken.map((a) => (
        <div key={a.id || a.session} className="panel flex flex-wrap items-center gap-3 border-orange-400/40 p-4">
          <div className="min-w-0 flex-1"><div className="text-[12px] font-bold uppercase text-orange-300">Taak wacht op jou</div><div className="font-semibold text-white">{a.title}</div><div className="text-[13px] text-slate-300">{a.doing}</div></div>
          <button className="btn-primary" onClick={() => order(`Goedgekeurd: taak "${a.title}"${a.id ? ` (thread ${a.id})` : ''}. Ga door.`, toast)}>Goedkeuren</button>
          {/* btn-primary heeft geen rand: 1px minder ruimte boven en onder houdt Afkeuren even hoog */}
          <AfkeurKnop title={a.title} id={a.id || undefined} className="py-[7px]" />
          {a.id && <a className="btn-ghost" href={threadUrl(a.id)} target="_blank" rel="noreferrer">Bekijk</a>}
        </div>
      ))}
      {open.map((b) => (
        <div key={b.id} className="panel flex flex-wrap items-center gap-3 p-4">
          <div className="min-w-0 flex-1"><div className="text-[12px] font-bold uppercase text-sky-300">Voorstel van de coach</div><div className="font-semibold text-white">{b.vraag}</div>{b.waarom && <div className="text-[13px] text-slate-300">{b.waarom}</div>}</div>
          <button className="btn-primary flex items-center gap-1" onClick={() => kies(b, true)}><Check size={16} />Ja, doen</button>
          <button className="btn-ghost flex items-center gap-1" onClick={() => kies(b, false)}><X size={16} />Nee</button>
        </div>
      ))}
      {!taken.length && !open.length && <div className="panel p-6 text-center text-slate-300">Niks dat op jou wacht. 👍</div>}
      {oud.length > 0 && <div className="panel p-4"><div className="mb-2 font-semibold text-white">Eerder besloten</div>{oud.map((b) => <div key={b.id} className="flex gap-2 py-1 text-[13px] text-slate-300"><span className={b.status === 'goedgekeurd' ? 'text-green-300' : 'text-red-300'}>{b.status === 'goedgekeurd' ? '✓' : '✗'}</span>{b.vraag}<span className="ml-auto shrink-0 text-slate-500">{b.besloten ? new Date(b.besloten).toLocaleDateString('nl-NL') : ''}</span></div>)}</div>}
    </div>
  );
}

/* ---------- 5. Agents ---------- */
const VRAAG_AGENT = [
  { wie: 'Onderzoek', v: 'Onderzoek drie nieuwe video-onderwerpen die passen bij Driftmark (What IF, escalatie, twist) en vergelijk ze met IFOLOGY.' },
  { wie: 'Cijfers', v: 'Vergelijk mijn laatste vijf video\'s en shorts (vidIQ) en noem de belangrijkste verschillen in prestaties.' },
  { wie: 'Script', v: 'Analyseer de eerste 30 seconden van het script van de video die nu in productie is en stel verbeteringen voor.' },
  { wie: 'Thumbnail', v: 'Onderzoek hoe de thumbnails van mijn lange video\'s presteren en maak drie alternatieven voor de volgende video.' },
  { wie: 'Productie', v: 'Onderzoek waarom de productie van de laatste video zo lang duurde en waar het sneller kan.' },
];
const STATE: Record<string, [string, string]> = { working: ['bezig', 'text-sky-300'], blocked: ['wacht op jou', 'text-orange-300'], review_ready: ['klaar om te bekijken', 'text-orange-300'], done: ['klaar', 'text-green-300'], failed: ['mislukt', 'text-rose-300'], stopped: ['gestopt', 'text-slate-400'] };
function Agents() {
  const d = useLive((s) => s.data);
  const toast = useGame((s) => s.toast);
  const nu = Date.now();
  return (
    <div className="space-y-3">
      <div className="panel p-4">
        <div className="mb-2 font-display text-lg font-bold text-white">Agent raadplegen</div>
        <div className="mb-2 text-[13px] text-slate-400">Stuurt een echte opdracht. Claude start of vraagt de juiste thread en het antwoord komt hieronder bij Antwoorden.</div>
        <div className="grid gap-2 md:grid-cols-2">{VRAAG_AGENT.map((a) => <button key={a.wie} onClick={() => order(`[Coach raadpleegt ${a.wie}] ${a.v}`, toast)} className="rounded-xl border border-hq-line p-3 text-left text-[14px] text-slate-200 hover:border-orange-400/60"><b className="text-orange-200">{a.wie}:</b> {a.v}</button>)}</div>
      </div>
      <div className="panel p-4">
        <div className="mb-2 font-display text-lg font-bold text-white">Threads</div>
        <div className="divide-y divide-white/5">
          {d.activity.map((a) => {
            const [lab, col] = STATE[a.state] ?? [a.state, 'text-slate-300'];
            const oud = a.state === 'working' && a.lastIso && nu - Date.parse(a.lastIso) > 6 * 3600e3;
            return (
              <div key={a.id || a.session} className="flex flex-wrap items-center gap-2 py-2.5 text-[14px]">
                <span className={`w-36 shrink-0 font-semibold ${col}`}>{lab}{oud ? ' ⚠️' : ''}</span>
                <span className="min-w-0 flex-1"><span className="text-white">{a.title}</span><span className="block text-[13px] text-slate-400">{a.doing}</span></span>
                <span className="text-[12px] text-slate-500">{a.last}</span>
                {oud && <button className="btn-ghost !px-2 !py-1 text-[12px]" onClick={() => order(`Controleer thread "${a.title}"${a.id ? ` (${a.id})` : a.session ? ` (sessie ${a.session})` : ''}: al meer dan 6 uur geen update. Herstart als hij vastzit en meld wat er was.`, toast)}>Controleer</button>}
              </div>
            );
          })}
        </div>
      </div>
      <div className="panel p-4">
        <div className="mb-2 font-display text-lg font-bold text-white">Antwoorden</div>
        {(d.replies ?? []).slice(0, 10).map((r, i) => <div key={i} className="border-b border-white/5 py-2 text-[14px]"><div className="text-[12px] text-slate-500">{r.at} · {r.opdracht.slice(0, 90)}</div><div className="text-slate-200">{r.antwoord}</div></div>)}
        {!(d.replies ?? []).length && <div className="text-[14px] text-slate-400">Nog geen antwoorden.</div>}
      </div>
    </div>
  );
}

/* ---------- 6. Rapporten ---------- */
function Rapporten() {
  const d = useLive((s) => s.data);
  const stats = useDb((s) => s.stats);
  const r = useCoach((s) => s.rapporten);
  const kan = useCoach((s) => s.kanVragen);
  const [busy, setBusy] = useState<string | null>(null);
  const [fout, setFout] = useState('');
  const [open, setOpen] = useState<string | null>(null);
  const maak = async (s: 'week' | 'maand' | 'advies') => { setBusy(s); setFout(''); const x = await maakRapport(s, d, stats); if (typeof x === 'string') setFout(x); else setOpen(x.id); setBusy(null); };
  const NAAM = { week: 'Weekrapport', maand: 'Maandrapport', advies: 'Strategisch advies' };
  return (
    <div className="space-y-3">
      <div className="grid gap-2 sm:grid-cols-3">
        {(['week', 'maand', 'advies'] as const).map((s) => <button key={s} disabled={!!busy || kan === false} onClick={() => void maak(s)} className="panel p-4 text-left hover:border-orange-400/60 disabled:opacity-60"><div className="font-display text-lg font-bold text-white">{busy === s ? 'Bezig…' : NAAM[s]}</div><div className="text-[13px] text-slate-400">{s === 'week' ? 'Groei, kwaliteit, snelheid, kosten, agents, tips voor volgende week' : s === 'maand' ? 'Doelen, groei, strategie: voortzetten, aanpassen of uitbreiden' : 'De 3 belangrijkste strategische keuzes nu'}</div></button>)}
      </div>
      {fout && <div className="panel p-3 text-[14px] text-red-200">{fout}</div>}
      {r.map((x) => (
        <div key={x.id} className="panel p-4">
          <button className="flex w-full items-center gap-2 text-left" onClick={() => setOpen(open === x.id ? null : x.id)}><span className="font-semibold text-white">{NAAM[x.soort]}</span><span className="text-[13px] text-slate-400">{new Date(x.at).toLocaleString('nl-NL', { dateStyle: 'medium', timeStyle: 'short' })}</span><span className="ml-auto text-slate-400">{open === x.id ? '▲' : '▼'}</span></button>
          {open === x.id && <div className="mt-3 text-[14px] text-slate-200"><Md text={x.tekst} /></div>}
        </div>
      ))}
    </div>
  );
}

/* ---------- 7. Kennis ---------- */
function KennisTab() {
  const k = useCoach((s) => s.kennis);
  const [q, setQ] = useState('');
  const [hits, setHits] = useState<Fragment[] | null>(null);
  const cursus = k?.bronnen.filter((b) => b.soort === 'cursus') ?? [];
  const zoekNu = async () => { const { zoek } = await import('../services/coach'); if (k) setHits(zoek(k, q, 8)); };
  return (
    <div className="space-y-3">
      <div className={`panel p-4 ${cursus.length ? '' : 'border-orange-400/50'}`}>
        <div className="font-display text-lg font-bold text-white">Je cursus (Faceless Education)</div>
        {cursus.length ? <div className="text-[14px] text-slate-300">{cursus.map((c) => `${c.doc} (${c.taal.toUpperCase()}, ${c.fragmenten} stukjes)`).join(' · ')}</div>
          : <div className="text-[14px] text-orange-100">Nog niet in de kennisbank. Stuur de cursus (PDF of tekst) in de thread, dan zet ik hem erin.</div>}
      </div>
      <div className="panel p-4">
        <div className="mb-2 font-display text-lg font-bold text-white">Driftmark-documenten</div>
        <div className="flex flex-wrap gap-2">{k?.bronnen.filter((b) => b.soort === 'driftmark').map((b) => <span key={b.doc} className="rounded-full bg-white/5 px-3 py-1 text-[13px] text-slate-200">{b.doc} · {b.fragmenten}</span>)}</div>
        <div className="mt-2 text-[12px] text-slate-500">{k?.fragmenten.length ?? 0} stukjes · bijgewerkt {k?.gemaakt ? new Date(k.gemaakt).toLocaleString('nl-NL') : '?'}</div>
      </div>
      <div className="panel p-4">
        <form onSubmit={(e) => { e.preventDefault(); void zoekNu(); }} className="flex gap-2"><input className="input flex-1" placeholder="Zoek in de kennis, bijv. hook, retentie, thumbnail" value={q} onChange={(e) => setQ(e.target.value)} /><button className="btn-primary">Zoek</button></form>
        {hits && (hits.length ? hits.map((f, i) => <div key={i} className="mt-3 rounded-xl bg-white/[.03] p-3 text-[14px]"><div className="text-[12px] font-semibold text-orange-200">{f.doc} · {f.hoofdstuk} · {f.onderwerp}</div><div className="mt-1 whitespace-pre-line text-slate-300">{f.tekst.slice(0, 600)}{f.tekst.length > 600 ? '…' : ''}</div></div>) : <div className="mt-3 text-[14px] text-slate-400">Niks gevonden.</div>)}
      </div>
    </div>
  );
}

/* ---------- 8. Geheugen ---------- */
function GeheugenTab() {
  const g = useCoach((s) => s.geheugen);
  const dbOk = useCoach((s) => s.dbOk);
  const toast = useGame((s) => s.toast);
  const [nieuw, setNieuw] = useState<Record<string, string>>({});
  const bewaar = (x: typeof g) => void bewaarGeheugen(x).then(() => toast('Geheugen bijgewerkt', 'success')).catch((e) => toast(String(e.message ?? e), 'warning'));
  return (
    <div className="space-y-3">
      <div className="text-[14px] text-slate-400">Dit onthoudt de coach blijvend (in de database). Gewone gesprekken onthoudt hij niet, alleen wat hier staat.{!dbOk && ' De database is nog niet verbonden: wijzigingen worden niet bewaard.'}</div>
      <div className="grid gap-3 md:grid-cols-2">
        {(Object.keys(VAK) as (keyof typeof VAK)[]).map((k) => (
          <div key={k} className="panel p-4">
            <div className="mb-2 font-display text-[16px] font-bold text-white">{VAK[k]}</div>
            <ul className="space-y-1.5">{(g[k] ?? []).map((x, i) => <li key={i} className="group flex gap-2 text-[14px] text-slate-200"><span className="text-orange-400">•</span><span className="flex-1">{x}</span><button aria-label="Vergeten" onClick={() => bewaar({ ...g, [k]: g[k].filter((_, j) => j !== i) })} className="text-slate-600 hover:text-red-300"><X size={14} /></button></li>)}</ul>
            <form onSubmit={(e) => { e.preventDefault(); const v = (nieuw[k] ?? '').trim(); if (v) { bewaar({ ...g, [k]: [...(g[k] ?? []), v] }); setNieuw({ ...nieuw, [k]: '' }); } }} className="mt-2 flex gap-2"><input className="input flex-1 !py-1.5 text-[13px]" placeholder="Toevoegen…" value={nieuw[k] ?? ''} onChange={(e) => setNieuw({ ...nieuw, [k]: e.target.value })} /><button className="btn-ghost !px-2"><Plus size={15} /></button></form>
          </div>
        ))}
      </div>
    </div>
  );
}
