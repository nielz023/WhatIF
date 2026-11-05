import { useState } from 'react';
import { ExternalLink, Clapperboard, Users, Map, ListChecks, Lightbulb, Wrench, Mic, Youtube, Play, Building2 } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Tabs } from '../components/ui';
import { RULES, CAST, VOICES, TOOLS, threadUrl, type RealVideo } from '../data/driftmark';
import { useLive, startLive } from '../services/live';
import { ToolsPanel, CostsPanel, RepliesPanel, Outputs } from './DriftmarkExtra';
import { useEffect } from 'react';
import gallery from '../data/gallery.json';
import { useReal } from '../services/real';
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;

const AVAIL: Record<string, [string, string]> = {
  laden: ['Verbinding controleren…', '#94a3b8'],
  available: ['Claude luistert mee', '#10b981'],
  no_session: ['Claude luistert nu niet: je opdracht wacht tot je hem opnieuw verstuurt', '#f59e0b'],
  writers_only: ['Alleen de eigenaar kan opdrachten sturen', '#f59e0b'],
  off: ['Versturen naar Claude staat hier uit', '#f43f5e'],
  geen: ['Alleen op de gepubliceerde pagina in claude.ai', '#f43f5e'],
};

function OrdersPanel() {
  const { orders, avail, send, resend } = useReal();
  const toast = useGame((s) => s.toast);
  const [text, setText] = useState('');
  const [label, color] = AVAIL[avail] ?? AVAIL.off;
  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    const o = await send(text.trim());
    setText('');
    toast(o.status === 'verstuurd' ? '✅ Opdracht naar Claude gestuurd' : `⏳ In de wachtrij: ${o.reason ?? ''}`, o.status === 'verstuurd' ? 'success' : 'warning');
  };
  return (
    <section id="orders-anchor" className="panel mb-4 border-emerald-400/30 p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="text-sm font-bold uppercase tracking-wider text-emerald-300">Geef Claude een opdracht</div>
        <span className="flex items-center gap-1.5 text-[11px]" style={{ color }}><span className="h-2 w-2 rounded-full" style={{ background: color }} />{label}</span>
      </div>
      <p className="mb-3 text-xs text-slate-400">Typ gewoon wat je wilt, zoals je het in de chat zou zeggen. Claude voert het echt uit en zet het antwoord hieronder. Uploaden naar YouTube doe je zelf in Studio.</p>
      <form onSubmit={submit} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="order-text" className="sr-only">Opdracht</label>
        <input id="order-text" className="input min-w-0 flex-1" value={text} onChange={(e) => setText(e.target.value)} placeholder="Typ een opdracht, bv. 'Maak de thumbnail voor video 3'" />
        <button className="btn-primary text-xs" type="submit">Stuur naar Claude</button>
      </form>
      {orders.length > 0 && (
        <ul className="mt-3 max-h-56 space-y-1.5 overflow-y-auto">
          {orders.slice(0, 20).map((o) => (
            <li key={o.id} className="flex items-start justify-between gap-2 rounded-lg bg-white/[.03] px-2.5 py-1.5 text-[11px]">
              <div className="min-w-0">
                <div className="whitespace-pre-line text-slate-200">{o.text.split('\n')[0]}</div>
                <div className="text-slate-500">{new Date(o.at).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}{o.reason ? ` · ${o.reason}` : ''}</div>
              </div>
              {o.status === 'verstuurd'
                ? <span className="shrink-0 text-emerald-300">✓ verstuurd</span>
                : <button className="shrink-0 text-amber-300 hover:text-white" onClick={() => void resend(o.id)}>Opnieuw versturen</button>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

const STATUS_COLOR: Record<string, string> = { Online: '#10b981', Klaar: '#38bdf8', 'In productie': '#f59e0b', Idee: '#94a3b8' };
const nice = (s: string) => s.replace(/^\d+_/, '').replace(/_/g, ' ');

function A({ href, children }: { href: string; children: React.ReactNode }) {
  return <a href={href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-indigo-300 hover:text-white">{children}<ExternalLink size={11} /></a>;
}

function VideoCard({ v }: { v: RealVideo }) {
  const c = STATUS_COLOR[v.status];
  const done = v.steps.filter((s) => s.done).length;
  return (
    <div className="panel relative overflow-hidden p-4">
      <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full opacity-30 blur-2xl" style={{ background: c }} />
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Video {v.nr} · {v.werktitel}</div>
          <div className="mt-0.5 font-display text-base font-bold leading-snug text-white">{v.title}</div>
        </div>
        <span className="chip shrink-0" style={{ background: `${c}22`, color: c, border: `1px solid ${c}55` }}>{v.status}</span>
      </div>
      <div className="mt-3 flex flex-wrap gap-1">
        {v.steps.map((s) => (
          <span key={s.label} title={s.label} className={`rounded-md px-1.5 py-0.5 text-[10px] ${s.active ? 'animate-pulse bg-amber-500/25 text-amber-200' : s.done ? 'bg-emerald-500/15 text-emerald-300' : 'bg-white/5 text-slate-500'}`}>{s.done ? '✓ ' : s.active ? '● ' : ''}{s.label}</span>
        ))}
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/5"><div className="h-full rounded-full" style={{ width: `${(done / v.steps.length) * 100}%`, background: c }} /></div>
      <div className="mt-3 space-y-1.5 text-xs text-slate-300">
        <div><span className="text-slate-500">Kern:</span> {v.kern}</div>
        <div><span className="text-slate-500">Twist:</span> {v.twist}</div>
        <div><span className="text-slate-500">Lengte:</span> {v.lengte}</div>
      </div>
      <ul className="mt-2 list-disc space-y-0.5 pl-4 text-[11px] text-slate-400">{v.notes.map((n) => <li key={n}>{n}</li>)}</ul>
      <Outputs nr={v.nr} />
      <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-white/5 pt-2 text-[11px]">
        {v.youtube && <A href={v.youtube}>Op YouTube</A>}
        {v.threads.map((t) => <A key={t.id} href={threadUrl(t.id)}>{t.title}</A>)}
      </div>
    </div>
  );
}

function Gallery({ items, cols = 'grid-cols-3 sm:grid-cols-4 lg:grid-cols-6' }: { items: [string, string][]; cols?: string }) {
  return (
    <div className={`grid gap-2 ${cols}`}>
      {items.map(([n, src]) => (
        <figure key={src} className="overflow-hidden rounded-xl border border-white/5 bg-black/20">
          <img src={src} alt={nice(n)} loading="lazy" className="aspect-[4/3] w-full object-cover" />
          <figcaption className="truncate px-2 py-1 text-[10px] capitalize text-slate-400">{nice(n)}</figcaption>
        </figure>
      ))}
    </div>
  );
}

function Section({ icon, title, children, right }: { icon: React.ReactNode; title: string; children: React.ReactNode; right?: React.ReactNode }) {
  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-200">{icon}{title}</div>
        {right}
      </div>
      {children}
    </section>
  );
}

type Tab = 'v1' | 'v2' | 'v3';
type View = 'overzicht' | 'threads' | 'videos' | 'shorts' | 'cast' | 'werkwijze' | 'gereedschap' | 'ideeen';
const VIEWS: { id: View; label: string; uitleg: string }[] = [
  { id: 'overzicht', label: 'Overzicht', uitleg: 'Wat er nu gebeurt en wat jij moet doen' },
  { id: 'threads', label: 'Alle threads', uitleg: 'Elke Claude-thread in je project, per video. Klik om hem te openen' },
  { id: 'videos', label: "Video's", uitleg: 'Elke lange video met zijn stappen en bestanden' },
  { id: 'shorts', label: 'Shorts', uitleg: 'Welke shorts er zijn en wanneer ze online gaan' },
  { id: 'cast', label: 'Cast & sets', uitleg: 'De figuren en decors per video' },
  { id: 'werkwijze', label: 'Werkwijze', uitleg: 'De vaste regels voor elke video' },
  { id: 'gereedschap', label: 'Gereedschap', uitleg: 'Blender, ElevenLabs, vidIQ en wat het kost' },
  { id: 'ideeen', label: 'Ideeën & links', uitleg: 'Onderwerpen voor de volgende video en alle documenten' },
];
const STATE: Record<string, [string, string]> = {
  working: ['aan het werk', '#10b981'], blocked: ['wacht op jou', '#f59e0b'], review_ready: ['klaar, kijk even', '#38bdf8'], done: ['klaar', '#64748b'],
};

function Step({ n, title, text }: { n: number; title: string; text: string }) {
  return (
    <div className="flex gap-3 rounded-xl bg-white/[.03] p-3">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-indigo-500/30 text-sm font-bold text-white">{n}</span>
      <div><div className="text-sm font-semibold text-white">{title}</div><div className="text-xs text-slate-400">{text}</div></div>
    </div>
  );
}

export default function DriftmarkPage() {
  const setPage = useGame((s) => s.setPage);
  const [view, setView] = useState<View>(() => { try { return (localStorage.getItem('driftmark-view') as View) || 'overzicht'; } catch { return 'overzicht'; } });
  const go = (v: View) => { setView(v); try { localStorage.setItem('driftmark-view', v); } catch { /* */ } };
  const [castTab, setCastTab] = useState<Tab>('v3');
  const [setTab, setSetTab] = useState<Tab>('v3');
  const g = gallery as unknown as Record<string, [string, string][]> & { banner: string };
  const live = useLive();
  useEffect(() => { startLive(); }, []);
  const { channel: CHANNEL, videos: VIDEOS, shorts: SHORTS, next: NEXT, ideas: IDEAS, links: LINKS, updated: UPDATED, activity } = live.data;
  const nu = VIDEOS.find((v) => v.status === 'In productie');
  const wachten = activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready');
  const bezig = activity.filter((a) => a.state === 'working');
  const srcLabel = live.source === 'live' ? ['● Live: ververst elke minuut', '#10b981'] : live.source === 'ingebouwd' ? ['Stand laden…', '#94a3b8'] : ['Live stand niet bereikbaar, je ziet de laatst bekende stand', '#f59e0b'];
  const cur = VIEWS.find((v) => v.id === view)!;

  const ActCard = ({ a }: { a: (typeof activity)[number] }) => {
    const [l, c] = STATE[a.state] ?? [a.state, '#64748b'];
    return (
      <a href={threadUrl(a.id)} target="_blank" rel="noreferrer" className="block min-w-0 overflow-hidden rounded-xl bg-white/[.03] p-3 hover:bg-white/[.07]">
        <div className="flex flex-wrap items-center justify-between gap-x-2"><span className="min-w-0 truncate text-sm font-semibold text-white">{a.title}</span><span className="flex shrink-0 items-center gap-1 text-[11px]" style={{ color: c }}><span className={`h-2 w-2 rounded-full ${a.state === 'working' ? 'animate-pulse' : ''}`} style={{ background: c }} />{l}</span></div>
        {a.doing && <div className="mt-0.5 line-clamp-2 text-xs text-slate-400">{a.doing}</div>}
        <div className="mt-0.5 text-[10px] text-slate-500">laatst actief {a.last} · klik om de thread te openen</div>
      </a>
    );
  };

  return (
    <div className="h-full overflow-y-auto p-3 pb-10 md:p-6 md:pb-10">
      {/* KOP */}
      <div className="panel relative mb-4 overflow-hidden">
        <img src="./img/hq_header.jpg" alt="Het hoofdpersonage tussen twee portalen in de nachtstad (Unreal Engine 5)" className="h-40 w-full object-cover object-[70%_45%] md:h-56" onError={(e) => { (e.currentTarget as HTMLImageElement).src = g.banner; }} />
        <div className="absolute inset-0 bg-gradient-to-t from-[#070b1d] via-[#070b1d]/20 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 flex flex-wrap items-end justify-between gap-3 p-4">
          <div>
            <div className="font-display text-2xl font-bold text-white md:text-3xl">DRIFT<span className="text-gradient">MARK</span> HQ</div>
            <div className="text-xs text-slate-300">Het kantoor van je kanaal {CHANNEL.handle}. Alles hier is echt.</div>
            <div className="mt-1 flex flex-wrap items-center gap-2 text-[11px]" style={{ color: srcLabel[1] }}>{srcLabel[0]}<span className="text-slate-500">· stand {UPDATED}</span><button className="text-indigo-300 underline hover:text-white" onClick={() => void live.refresh()}>Nu verversen</button></div>
          </div>
          <div className="flex flex-wrap gap-2">
            <a className="btn-primary text-xs" href={CHANNEL.url} target="_blank" rel="noreferrer"><Youtube size={14} />Naar je kanaal</a>
            <button className="btn-ghost text-xs" onClick={() => setPage('hq')}><Building2 size={14} />3D-kantoor bekijken</button>
          </div>
        </div>
      </div>

      {/* TABBLADEN */}
      <div className="sticky -top-3 z-20 -mx-3 mb-4 bg-[#070b1a]/95 px-3 pb-2 pt-3 backdrop-blur md:-top-6 md:-mx-6 md:px-6 md:pt-6">
        <div className="flex gap-1.5 overflow-x-auto">
          {VIEWS.map((v) => (
            <button key={v.id} onClick={() => go(v.id)} className={`shrink-0 rounded-full px-3.5 py-1.5 text-sm font-semibold transition ${view === v.id ? 'bg-indigo-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>{v.label}</button>
          ))}
        </div>
        <div className="mt-1 text-[11px] text-slate-500">{cur.uitleg}</div>
      </div>

      {view === 'overzicht' && (<>
        <div className="mb-4 grid gap-2 md:grid-cols-3">
          <Step n={1} title="Kijk wat er gebeurt" text="Hieronder zie je welke Claude-threads aan het werk zijn en wat er op jou wacht." />
          <Step n={2} title="Geef een opdracht" text="Typ in het groene vak wat je wilt. Claude voert het echt uit." />
          <Step n={3} title="Lees het antwoord" text="Het antwoord en de bestanden verschijnen hier vanzelf, ook in de tabbladen." />
        </div>

        <section className={`panel mb-4 p-4 ${wachten.length ? 'border-amber-400/50' : 'border-emerald-400/30'}`}>
          <div className="mb-2 text-sm font-bold uppercase tracking-wider text-amber-300">Wacht op jou</div>
          {wachten.length ? <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">{wachten.map((a) => <ActCard key={a.id} a={a} />)}</div>
            : <div className="text-sm text-slate-300">Niets. Alles loopt, je hoeft nu niets te doen.</div>}
        </section>

        <div className="mb-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
          {CHANNEL.stats.map((s) => (
            <div key={s.label} className="panel min-w-0 p-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">{s.label}</div>
              <div className="font-display text-2xl font-bold text-white">{s.value}</div>
              <div className="text-[11px] text-slate-400">{s.note}</div>
            </div>
          ))}
        </div>

        <OrdersPanel />
        <RepliesPanel />

        <div className="mb-4 grid gap-4 lg:grid-cols-3">
          <section className="panel p-4 lg:col-span-2">
            <div className="mb-2 text-sm font-bold uppercase tracking-wider text-slate-200">Nu aan het werk ({bezig.length})</div>
            {bezig.length ? <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">{bezig.map((a) => <ActCard key={a.id} a={a} />)}</div> : <div className="text-sm text-slate-400">Er werkt nu geen thread.</div>}
          </section>
          <section className="panel border-amber-400/30 p-4">
            <div className="mb-2 flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-amber-300"><Play size={14} />Hierna</div>
            {nu && <div className="mb-2 text-sm text-white">Nu in productie: <b>video {nu.nr}, {nu.werktitel}</b></div>}
            <ol className="list-decimal space-y-1 pl-4 text-xs text-slate-300">{NEXT.map((n) => <li key={n}>{n}</li>)}</ol>
          </section>
        </div>
        <div className="panel p-3 text-xs text-slate-300"><span className="font-semibold text-amber-300">Wat de cijfers zeggen:</span> {CHANNEL.insight}</div>
      </>)}

      {view === 'threads' && (
        <div className="grid gap-4">
          <div className="flex flex-wrap gap-3 text-xs text-slate-300">
            <span>{activity.length} threads</span>
            <span style={{ color: STATE.working[1] }}>● {bezig.length} aan het werk</span>
            <span style={{ color: STATE.blocked[1] }}>● {wachten.length} wacht op jou</span>
            <span className="text-slate-500">● {activity.filter((a) => a.state === 'done').length} klaar</span>
          </div>
          {[...new Set([...VIDEOS.map((v) => v.nr).sort((a, b) => b - a), 0])].map((nr) => {
            const list = activity.filter((a) => (a.video ?? 0) === nr);
            if (!list.length) return null;
            const v = VIDEOS.find((x) => x.nr === nr);
            return (
              <Section key={nr} icon={<Users size={16} />} title={nr ? `Video ${nr}${v ? ` · ${v.werktitel}` : ''}` : 'Kanaal, HQ en overig'}>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">{list.map((a) => <ActCard key={a.id} a={a} />)}</div>
              </Section>
            );
          })}
        </div>
      )}

      {view === 'videos' && <div className="grid gap-3 xl:grid-cols-3">{[...VIDEOS].reverse().map((v) => <VideoCard key={v.nr} v={v} />)}</div>}

      {view === 'shorts' && (
        <Section icon={<Clapperboard size={16} />} title="Shorts">
          <div className="grid gap-2 sm:grid-cols-2">
            {SHORTS.map((s) => (
              <div key={s.title} className="rounded-xl bg-white/[.03] p-3">
                <div className="flex items-center justify-between gap-2"><span className="text-xs font-semibold text-white">{s.title}</span><span className="text-[10px] text-emerald-300">{s.status}</span></div>
                <ul className="mt-1 space-y-0.5 text-[11px] text-slate-400">{s.items.map((i) => <li key={i}>• {i}</li>)}</ul>
                <div className="mt-1 text-[10px] text-slate-500">{s.where}</div>
              </div>
            ))}
          </div>
          {(live.data.youtube?.videos?.length ?? 0) > 0 && (<>
            <div className="mb-1 mt-4 text-xs font-bold uppercase tracking-wider text-slate-400">Op YouTube (via vidIQ)</div>
            <div className="space-y-1">{live.data.youtube!.videos!.map((y: Any) => (
              <a key={y.id ?? y.title} href={y.url} target="_blank" rel="noreferrer" className="flex items-center justify-between gap-2 rounded-lg bg-white/[.03] px-2.5 py-1.5 text-[11px] hover:bg-white/[.07]">
                <span className="truncate text-slate-200">{y.type === 'long' ? '🎬 ' : '📱 '}{y.title}</span>
                <span className="shrink-0 text-slate-400">{y.status && y.status !== 'public' ? y.status : `${Number(y.views ?? 0).toLocaleString('nl-NL')} views`}</span>
              </a>
            ))}</div>
          </>)}
        </Section>
      )}

      {view === 'cast' && (
        <div className="grid gap-4">
          <Section icon={<Users size={16} />} title="Cast" right={<Tabs value={castTab} onChange={setCastTab} items={[{ id: 'v1', label: 'Video 1' }, { id: 'v2', label: 'Video 2' }, { id: 'v3', label: 'Video 3' }]} />}>
            <div className="mb-2 text-[11px] text-slate-400">{CAST.hoofd}. Gezin: {CAST.gezin.join(', ')}. Vast: {CAST.vast.join(', ')}.</div>
            {castTab === 'v1' && <Gallery items={g.cast1} />}
            {castTab === 'v2' && <Gallery items={g.cast2} />}
            {castTab === 'v3' && <Gallery items={g.cast3} cols="grid-cols-1 sm:grid-cols-3" />}
          </Section>
          <Section icon={<Map size={16} />} title="Sets" right={<Tabs value={setTab} onChange={setSetTab} items={[{ id: 'v1', label: `Video 1 (${g.sets1.length})` }, { id: 'v2', label: `Video 2 (${g.sets2.length})` }, { id: 'v3', label: `Video 3 (${g.sets3.length})` }]} />}>
            {setTab === 'v1' && <Gallery items={g.sets1} />}
            {setTab === 'v2' && <Gallery items={g.sets2} />}
            {setTab === 'v3' && <Gallery items={g.sets3} />}
          </Section>
        </div>
      )}

      {view === 'werkwijze' && (
        <Section icon={<ListChecks size={16} />} title="Werkwijze & regels">
          <div className="grid gap-2 sm:grid-cols-2">
            {RULES.map((r) => (
              <div key={r.title} className="rounded-xl bg-white/[.03] p-3">
                <div className="text-xs font-semibold text-white">{r.title}</div>
                <ul className="mt-1 space-y-0.5 text-[11px] text-slate-400">{r.items.map((i) => <li key={i}>✓ {i}</li>)}</ul>
              </div>
            ))}
          </div>
        </Section>
      )}

      {view === 'gereedschap' && (
        <div className="grid gap-4 xl:grid-cols-2">
          <div className="xl:col-span-2"><ToolsPanel /></div>
          <Section icon={<Mic size={16} />} title="Stemmen (ElevenLabs v4)">
            <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
              {VOICES.map(([r, id]) => <div key={r} className="flex justify-between gap-2 rounded-lg bg-white/[.03] px-2 py-1 text-[11px]"><span className="text-slate-300">{r}</span><code className="text-slate-500">{id}</code></div>)}
            </div>
          </Section>
          <Section icon={<Wrench size={16} />} title="Waarvoor gebruik je wat">
            <div className="space-y-1.5">{TOOLS.map((t) => <div key={t.name} className="text-xs"><span className="font-semibold text-white">{t.name}</span> <span className="text-slate-400">· {t.use}</span></div>)}</div>
          </Section>
          <CostsPanel />
        </div>
      )}

      {view === 'ideeen' && (
        <div className="grid gap-4 xl:grid-cols-2">
          <Section icon={<Lightbulb size={16} />} title="Ideeën voor video 4+">
            <div className="flex flex-wrap gap-1.5">
              {IDEAS.map((i) => <span key={i.title} className="rounded-lg bg-white/[.04] px-2 py-1 text-[11px] text-slate-300"><span className="text-slate-500">{i.groep}:</span> {i.title}</span>)}
            </div>
            <div className="mt-2 text-[11px] text-slate-500">Werkt goed bij IFOLOGY: tijd/snelheid, een getal in de titel, je lichaam dat verandert.</div>
          </Section>
          <Section icon={<ExternalLink size={16} />} title="Documenten & links">
            <div className="grid gap-1.5 sm:grid-cols-2">{LINKS.map((l) => <div key={l.url} className="text-xs"><A href={l.url}>{l.title}</A></div>)}</div>
          </Section>
        </div>
      )}
    </div>
  );
}
