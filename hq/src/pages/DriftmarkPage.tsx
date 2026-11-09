import { useEffect, useState } from 'react';
import { ExternalLink, Clapperboard, Users, Map, ListChecks, Lightbulb, Wrench, Mic, Youtube, Play, Building2, MessageSquare } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Tabs } from '../components/ui';
import { RULES, CAST, VOICE_SETS, TOOLS, threadUrl, type RealVideo } from '../data/driftmark';
import { CursusCheck, TitelTester, CursusStappen, CursusTip } from './Cursus';
import { useLive, startLive } from '../services/live';
import { openGesprek } from '../components/shared/Gesprek';
import { AfkeurKnop } from '../components/shared/Afkeuren';
import { useThreads, wanneerNl } from '../services/threads';
import { ToolsPanel, CostsPanel, RepliesPanel, Outputs, AutomationPanel } from './DriftmarkExtra';
import gallery from '../data/gallery.json';
import { useReal, order } from '../services/real';
import { useDb } from '../services/db';
import { UploadCalendar, MetroLine } from './DriftmarkVideos';
import YouTubeStats from './YouTubeStats';
import { Library } from 'lucide-react';
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

/** tooltip bij het stipje op een taakkaart */
const UIT_THREADS = 'De stand komt uit de threads en wordt ongeveer elk uur bijgewerkt.';

/** waar de stand van de taken vandaan komt (Meer › Alle taken) */
function ThreadsStand() {
  const at = useThreads((s) => s.at); const src = useThreads((s) => s.src);
  const tekst = src === 'ok' ? `Stand van de threads: bijgewerkt ${wanneerNl(at) || 'onlangs'}. Die wordt ongeveer elk uur ververst.`
    : src === 'laden' ? 'Stand van de threads laden…'
    : src === 'ontbreekt' ? 'De stand van de threads is nog niet opgehaald. Je ziet nu de stand van de uurronde.'
    : src === 'geen-toegang' ? 'Deze pagina kan de projectbestanden hier niet lezen. Je ziet de laatst bekende stand.'
    : 'De stand van de threads kon nu niet gelezen worden. Je ziet de stand van de uurronde.';
  return <div className="flex items-center gap-2 text-[12px] text-slate-500"><span className={`h-2 w-2 shrink-0 rounded-full ${src === 'ok' ? 'bg-sky-400/80' : 'bg-slate-500'}`} />{tekst}</div>;
}

function OrdersPanel({ quick = [] }: { quick?: string[] }) {
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
    <section id="orders-anchor" className="panel glow-blue mb-5 p-4 md:p-5">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <div className="font-display text-[20px] font-bold text-white">⚡ Geef Claude een opdracht</div>
        <span className="flex items-center gap-1.5 text-[13px]" style={{ color }}><span className="h-2 w-2 rounded-full" style={{ background: color }} />{label}</span>
      </div>
      <p className="mb-3 text-[13px] text-slate-400">Typ gewoon wat je wilt, zoals je het in de chat zou zeggen. Claude voert het echt uit en zet het antwoord hieronder. Uploaden naar YouTube doe je zelf in Studio.</p>
      {quick.length > 0 && <div className="mb-2 flex flex-wrap gap-1.5">{quick.map((q) => <button key={q} type="button" onClick={() => setText(q)} className="rounded-full border border-hq-line bg-white/[.04] px-3 py-1.5 text-[13px] text-slate-200 hover:border-orange-400/60 hover:text-white">{q}</button>)}</div>}
      <form onSubmit={submit} className="flex flex-col gap-2 sm:flex-row">
        <label htmlFor="order-text" className="sr-only">Opdracht</label>
        <input id="order-text" className="input min-w-0 flex-1" value={text} onChange={(e) => setText(e.target.value)} placeholder="Typ een opdracht, bv. 'Maak de thumbnail voor video 3'" />
        <button className="btn-primary text-[14px]" type="submit">Stuur naar Claude</button>
      </form>
      {orders.length > 0 && (
        <ul className="mt-3 max-h-56 space-y-1.5 overflow-y-auto">
          {orders.slice(0, 20).map((o) => (
            <li key={o.id} className="flex items-start justify-between gap-2 rounded-lg bg-white/[.03] px-2.5 py-1.5 text-[13px]">
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
  return <a href={href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sky-300 hover:text-white">{children}<ExternalLink size={11} /></a>;
}

function VideoCard({ v }: { v: RealVideo }) {
  const c = STATUS_COLOR[v.status] ?? '#ff8a3d';
  return (
    <div className="panel relative overflow-hidden p-4">
      <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full opacity-30 blur-2xl" style={{ background: c }} />
      <div className="flex items-start justify-between gap-2">
        <div>
          <div className="text-[13px] font-bold uppercase tracking-wider text-slate-400">Video {v.nr} · {v.werktitel}</div>
          <div className="mt-0.5 font-display text-base font-bold leading-snug text-white">{v.title}</div>
        </div>
        <span className="chip shrink-0" style={{ background: `${c}22`, color: c, border: `1px solid ${c}55` }}>{v.status}</span>
      </div>
      <MetroLine steps={v.steps} />
      <div className="mt-3 space-y-1.5 text-[13px] text-slate-300">
        <div><span className="text-slate-500">Kern:</span> {v.kern}</div>
        <div><span className="text-slate-500">Twist:</span> {v.twist}</div>
        <div><span className="text-slate-500">Lengte:</span> {v.lengte}</div>
      </div>
      <ul className="mt-2 list-disc space-y-0.5 pl-4 text-[13px] text-slate-400">{v.notes.map((n) => <li key={n}>{n}</li>)}</ul>
      <Outputs nr={v.nr} />
      <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-white/5 pt-2 text-[13px]">
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
          <figcaption className="truncate px-2 py-1 text-[12px] capitalize text-slate-400">{nice(n)}</figcaption>
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
type View = 'overzicht' | 'threads' | 'youtube' | 'videos' | 'cursus' | 'kalender' | 'shorts' | 'cast' | 'werkwijze' | 'gereedschap' | 'ideeen';
const VIEWS: { id: View; label: string; uitleg: string }[] = [
  { id: 'overzicht', label: 'Overzicht', uitleg: 'Wat er nu gebeurt en wat jij moet doen' },
  { id: 'threads', label: 'Alle taken', uitleg: 'Elke Claude-taak in je project, per video. Klik om hem te openen' },
  { id: 'youtube', label: 'Op YouTube', uitleg: "Al je video's en shorts zoals ze op YouTube staan, met weergaven, likes, reacties en kijkduur" },
  { id: 'videos', label: 'Productie', uitleg: 'Elke lange video met zijn productielijn en bestanden' },
  { id: 'cursus', label: 'Cursuscheck', uitleg: 'Checklist uit je cursus per video, plus de titeltester' },
  { id: 'kalender', label: 'Uploadkalender', uitleg: 'Wat er wanneer online ging en wat er ingepland staat' },
  { id: 'shorts', label: 'Shorts', uitleg: 'Welke shorts er zijn en wanneer ze online gaan' },
  { id: 'cast', label: 'Cast & sets', uitleg: 'De figuren en decors per video' },
  { id: 'werkwijze', label: 'Werkwijze', uitleg: 'De vaste regels voor elke video' },
  { id: 'gereedschap', label: 'Gereedschap', uitleg: 'Blender, ElevenLabs, vidIQ en wat het kost' },
  { id: 'ideeen', label: 'Ideeën & links', uitleg: 'Onderwerpen voor de volgende video en alle documenten' },
];
const STATE: Record<string, [string, string]> = {
  working: ['Claude is bezig', '#3db8ff'], blocked: ['wacht op jou', '#ff8a3d'], review_ready: ['klaar om te bekijken', '#ff8a3d'], done: ['klaar', '#3ddc97'], failed: ['mislukt', '#ff4d6d'], stopped: ['gestopt', '#94a3b8'],
};

function Step({ n, title, text }: { n: number; title: string; text: string }) {
  return (
    <div className="flex gap-3 rounded-xl bg-white/[.03] p-3">
      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-sky-500/30 text-sm font-bold text-white">{n}</span>
      <div><div className="text-sm font-semibold text-white">{title}</div><div className="text-[13px] text-slate-400">{text}</div></div>
    </div>
  );
}

type Mode = 'home' | 'videos' | 'meer';
const MODE_VIEWS: Record<Mode, View[]> = { home: [], videos: ['youtube', 'videos', 'cursus', 'kalender', 'shorts'], meer: ['threads', 'cast', 'werkwijze', 'gereedschap', 'ideeen'] };
const MODE_TITLE: Record<Mode, [string, string]> = {
  home: ['Home', ''],
  videos: ["Video's", "Je video's en shorts op YouTube met hun cijfers, en elke nieuwe video van idee tot upload."],
  meer: ['Meer', 'Alles om op terug te vallen: taken, regels, cast en gereedschap.'],
};

const greet = () => { const h = Number(new Date().toLocaleString('nl-NL', { hour: 'numeric', hour12: false, timeZone: 'Europe/Amsterdam' })); return h < 6 ? 'Goedenacht' : h < 12 ? 'Goedemorgen' : h < 18 ? 'Goedemiddag' : 'Goedenavond'; };
const QUICK = ['Maak 7 shorts van de nieuwste video', 'Maak een thumbnail met 3 varianten', 'Check de retentie van mijn laatste video', 'Bedenk 3 nieuwe What IF-ideeën'];

/** ISO-week-sleutel voor de upload-streak */
const weekKey = (d: Date) => { const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate())); const day = t.getUTCDay() || 7; t.setUTCDate(t.getUTCDate() + 4 - day); const y = t.getUTCFullYear(); return `${y}-${Math.ceil(((+t - Date.UTC(y, 0, 1)) / 864e5 + 1) / 7)}`; };
export function uploadStreak(vids: { type?: string; datum?: string; date?: string; status?: string }[] = []) {
  const weeks = new Set(vids.filter((v) => v.type === 'long' && (v.status ?? 'public') === 'public' && (v.datum || v.date)).map((v) => weekKey(new Date(v.datum || v.date!))));
  let n = 0; const d = new Date();
  if (!weeks.has(weekKey(d))) d.setDate(d.getDate() - 7);
  while (weeks.has(weekKey(d))) { n++; d.setDate(d.getDate() - 7); }
  return n;
}

function Info({ text }: { text: string }) {
  return <span title={text} aria-label={text} className="ml-1 inline-flex h-4 w-4 cursor-help items-center justify-center rounded-full bg-white/10 text-[11px] font-bold text-slate-300">i</span>;
}

function BigNum({ label, value, sub, info, color = '#f3f6ff' }: { label: string; value: React.ReactNode; sub?: React.ReactNode; info: string; color?: string }) {
  return (
    <div className="panel min-w-0 p-4 dm-pop">
      <div className="flex items-center text-[13px] font-semibold text-slate-400">{label}<Info text={info} /></div>
      <div className="mt-1 font-display text-3xl font-bold" style={{ color }}>{value}</div>
      {sub && <div className="mt-0.5 text-[13px] text-slate-400">{sub}</div>}
    </div>
  );
}

export function VideosPage() { return <DriftmarkPage mode="videos" />; }
export function MeerPage() { return <DriftmarkPage mode="meer" />; }

export default function DriftmarkPage({ mode = 'home' }: { mode?: Mode }) {
  const setPage = useGame((s) => s.setPage);
  const toast = useGame((s) => s.toast);
  const views = MODE_VIEWS[mode];
  // v34: nieuwe sleutel voor Video's, zodat het nieuwe tabblad Op YouTube één keer vanzelf opent
  const key = mode === 'videos' ? 'driftmark-view-videos-v34' : `driftmark-view-${mode}`;
  const [view, setView] = useState<View>(() => { try { const v = localStorage.getItem(key) as View; return v && views.includes(v) ? v : views[0] ?? 'overzicht'; } catch { return views[0] ?? 'overzicht'; } });
  const go = (v: View) => { setView(v); try { localStorage.setItem(key, v); } catch { /* */ } };
  // een melding kan vragen om een bepaald tabblad (bijv. Meer → Alle taken), ook als deze pagina al open staat
  useEffect(() => {
    const f = (e: Event) => { const d = (e as CustomEvent<{ mode: Mode; view: View }>).detail; if (d?.mode === mode && views.includes(d.view)) setView(d.view); };
    window.addEventListener('dm-view', f); return () => window.removeEventListener('dm-view', f);
  }, [mode, views]);
  const [castTab, setCastTab] = useState<Tab>('v3');
  const [setTab, setSetTab] = useState<Tab>('v3');
  const g = gallery as unknown as Record<string, [string, string][]> & { banner: string };
  const live = useLive();
  const stats = useDb((s) => s.stats);
  useEffect(() => { startLive(); }, []);
  const { channel: CHANNEL, videos: VIDEOS, shorts: SHORTS, next: NEXT, ideas: IDEAS, links: LINKS, updated: UPDATED, activity } = live.data;
  const yt = live.data.youtube;
  const nu = VIDEOS.find((v) => v.status === 'In productie');
  const wachten = activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready');
  const bezig = activity.filter((a) => a.state === 'working');
  const srcLabel = live.source === 'live' ? ['● Live: ververst elke minuut', '#3ddc97'] : live.source === 'database' ? ['● Live via de database (elk uur bijgewerkt)', '#3db8ff'] : live.source === 'ingebouwd' ? ['Stand laden…', '#94a3b8'] : ['Live stand niet bereikbaar, je ziet de laatst bekende stand', '#ff8a3d'];

  const ActCard = ({ a, big }: { a: (typeof activity)[number]; big?: boolean }) => {
    const [l, c] = STATE[a.state] ?? [a.state, '#64748b'];
    const v = VIDEOS.find((x) => x.nr === a.video);
    const pct = v ? Math.round((v.steps.filter((s) => s.done).length / v.steps.length) * 100) : null;
    return (
      <div className={`min-w-0 overflow-hidden rounded-2xl p-4 dm-pop ${big ? 'glow-orange bg-orange-500/[.07]' : 'bg-white/[.04]'}`}>
        <div className="flex flex-wrap items-center justify-between gap-x-2"><span className="min-w-0 font-display text-[17px] font-bold text-white">{a.title}</span><span className="flex shrink-0 items-center gap-1.5 text-[13px] font-semibold" style={{ color: c }}><span className={`h-2.5 w-2.5 rounded-full ${a.state === 'working' ? 'animate-pulse' : ''}`} style={{ background: c }} />{l}</span></div>
        {a.doing && <div className="mt-1 line-clamp-3 text-[14px] text-slate-300">{a.doing}</div>}
        {pct != null && !big && <div className="mt-2"><div className="h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-sky-400" style={{ width: `${pct}%` }} /></div><div className="mt-0.5 text-[12px] text-slate-500">Video {v!.nr}: {pct}% van de productielijn</div></div>}
        {a.needs && a.needs !== a.doing && (a.state === 'blocked' || a.state === 'review_ready') && <div className="mt-1.5 rounded-lg bg-orange-500/10 px-2.5 py-1.5 text-[13px] text-orange-100"><b className="text-orange-300">Jij: </b>{a.needs}</div>}
        <div className="mt-3 flex flex-wrap items-center gap-2">
          {a.id ? <a href={threadUrl(a.id)} target="_blank" rel="noreferrer" className={big ? 'btn-primary text-[13px]' : 'btn-ghost text-[13px]'}>Bekijk</a> : null}
          {a.id && <button className="btn-ghost text-[13px]" onClick={() => openGesprek({ kind: 'thread', thread: a.id, title: a.title })}><MessageSquare size={13} />Gesprek</button>}
          {big && a.state === 'review_ready' && (<>
            <button className="btn-success text-[13px]" onClick={() => order(`Goedgekeurd: taak "${a.title}"${a.id ? ` (thread ${a.id})` : ''}.`, toast)}>Goedkeuren</button>
            <AfkeurKnop title={a.title} id={a.id || undefined} className="text-[13px]" />
          </>)}
          <span className="text-[12px] text-slate-500">{a.live ? <span className="mr-1 cursor-help text-sky-400/80" title={UIT_THREADS} aria-label={UIT_THREADS}>●</span> : null}laatst actief {a.last}</span>
        </div>
      </div>
    );
  };

  // ---- cijfers voor Home
  const week = stats.filter((s) => s.subscribers != null && Date.now() - +new Date(s.at) < 7 * 864e5);
  const subDiff = week.length > 1 ? (week[week.length - 1].subscribers! - week[0].subscribers!) : null;
  const viewDiff = week.length > 1 ? (week[week.length - 1].views! - week[0].views!) : null;
  const online = VIDEOS.filter((v) => v.status === 'Online').length;
  const gepland = (yt?.videos ?? []).filter((v: Any) => v.status && v.status !== 'public' && v.datum).sort((a: Any, b: Any) => a.datum.localeCompare(b.datum));
  const streak = uploadStreak(yt?.videos as Any);
  const subs = yt?.subscribers ?? 0;
  const goal = subs < 100 ? 100 : subs < 500 ? 500 : subs < 1000 ? 1000 : Math.ceil((subs + 1) / 1000) * 1000;
  const perDay = (() => { const s = stats.filter((r) => r.subscribers != null); if (s.length < 2) return null; const d = (+new Date(s[s.length - 1].at) - +new Date(s[0].at)) / 864e5; return d > 0.5 ? (s[s.length - 1].subscribers! - s[0].subscribers!) / d : null; })();
  const eta = perDay && perDay > 0 ? Math.ceil((goal - subs) / perDay) : null;
  const [title, sub] = MODE_TITLE[mode];

  return (
    <div className="h-full overflow-y-auto p-3 pb-28 md:p-6 md:pb-10">
      {mode === 'home' ? (
        <div className="panel relative mb-5 overflow-hidden">
          <img src="./img/hq_header.jpg" alt="Het hoofdpersonage tussen twee portalen in de nachtstad (Unreal Engine 5)" className="h-36 w-full object-cover object-[70%_45%] md:h-60" onError={(e) => { (e.currentTarget as HTMLImageElement).src = g.banner; }} />
          <div className="absolute inset-x-0 top-0 h-36 bg-gradient-to-t from-[#0f1630] via-[#0f1630]/30 to-transparent md:inset-0 md:h-auto md:from-[#070b1a] md:via-[#070b1a]/40" />
          <div className="relative -mt-8 flex flex-wrap items-end justify-between gap-3 p-4 md:absolute md:bottom-0 md:left-0 md:right-0 md:mt-0 md:p-5">
            <div className="min-w-0">
              <div className="font-display text-[26px] font-bold leading-tight text-white md:text-[32px]">{greet()} niels 👋</div>
              <div className="mt-1 text-[15px] text-slate-200">Claude werkt aan <b className="text-sky-300">{bezig.length}</b> {bezig.length === 1 ? 'ding' : 'dingen'}{wachten.length ? <>, <b className="text-orange-300">{wachten.length}</b> {wachten.length === 1 ? 'ding wacht' : 'dingen wachten'} op jou.</> : '. Er wacht niets op jou.'}</div>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-[12px]" style={{ color: srcLabel[1] }}>{srcLabel[0]}<span className="text-slate-500">· stand {UPDATED}</span><button className="text-sky-300 underline hover:text-white" onClick={() => void live.refresh()}>Nu verversen</button></div>
            </div>
            <div className="flex flex-wrap gap-2">
              <button className="btn-primary text-[14px]" onClick={() => document.getElementById('orders-anchor')?.scrollIntoView({ behavior: 'smooth' })}>⚡ Geef Claude een opdracht</button>
              <a className="btn-ghost text-[14px]" href={CHANNEL.url} target="_blank" rel="noreferrer"><Youtube size={15} />Kanaal</a>
            </div>
          </div>
        </div>
      ) : (
        <div className="mb-4">
          <h1 className="font-display text-[28px] font-bold text-white">{title}</h1>
          <p className="text-[15px] text-slate-400">{sub}</p>
        </div>
      )}
      {mode === 'meer' && (
        <button onClick={() => setPage('kennis')} className="panel glow-blue mb-4 flex w-full items-center gap-3 p-4 text-left transition hover:-translate-y-0.5">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-sky-500/15 text-sky-300"><Library size={22} /></span>
          <span className="min-w-0 flex-1"><span className="block font-display text-[18px] font-bold text-white">Kennis: alles wat is opgeslagen</span><span className="block text-[13px] text-slate-400">Het hele geheugen met alle regels, elke thread met het hele gesprek, de projectchat, documenten en beelden. Alles op één plek doorzoeken.</span></span>
          <span className="shrink-0 text-sky-300" aria-hidden>→</span>
        </button>
      )}

      {views.length > 1 && (
        <div className="sticky -top-3 z-20 -mx-3 mb-4 bg-[#070b1a]/95 px-3 pb-2 pt-3 backdrop-blur md:-top-6 md:-mx-6 md:px-6 md:pt-6">
          <div className="flex gap-1.5 overflow-x-auto">
            {views.map((id) => { const v = VIEWS.find((x) => x.id === id)!; return (
              <button key={id} onClick={() => go(id)} className={`shrink-0 rounded-full px-4 py-2 text-[14px] font-semibold transition ${view === id ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>{v.label}</button>
            ); })}
            {mode === 'meer' && <button onClick={() => setPage('settings')} className="shrink-0 rounded-full bg-white/5 px-4 py-2 text-[14px] font-semibold text-slate-300 hover:bg-white/10">Koppelingen ↗</button>}
          </div>
          <div className="mt-1 text-[13px] text-slate-500">{VIEWS.find((x) => x.id === view)?.uitleg}</div>
        </div>
      )}

      {mode === 'home' && (<>
        <section className="mb-5">
          <h2 className="mb-2 flex items-center font-display text-[20px] font-bold text-orange-300">Wacht op jou<Info text="Dingen waar Claude jouw keuze of blik voor nodig heeft. Klik op Bekijk om de taak te openen." /></h2>
          {wachten.length ? <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">{wachten.map((a) => <ActCard key={a.id || a.session} a={a} big />)}</div>
            : <div className="panel flex items-center gap-3 p-4 text-[15px] text-slate-200"><span className="text-2xl">✅</span>Alles is bij, chill 😎 Je hoeft nu niets te doen.</div>}
        </section>

        <div className="mb-5 grid grid-cols-2 gap-3 lg:grid-cols-4">
          <BigNum label="Abonnees" value={subs ? subs.toLocaleString('nl-NL') : '—'} color="#ff8a3d" info="Hoeveel mensen je kanaal volgen. Elk uur opgehaald via vidIQ."
            sub={subDiff != null ? <span style={{ color: subDiff >= 0 ? '#3ddc97' : '#ff4d6d' }}>{subDiff >= 0 ? '▲ +' : '▼ '}{subDiff} deze week</span> : 'via vidIQ'} />
          <BigNum label="Weergaven" value={yt?.views != null ? yt.views.toLocaleString('nl-NL') : '—'} color="#3db8ff" info="Alle keren dat iemand een video of short van je bekeek, bij elkaar opgeteld."
            sub={viewDiff != null ? <span style={{ color: '#3ddc97' }}>▲ +{viewDiff.toLocaleString('nl-NL')} deze week</span> : 'totaal'} />
          <BigNum label="Video's online" value={online} info="Lange video's die op YouTube staan. Shorts tellen hier niet mee." sub={`${yt?.videoCount ?? '—'} uploads in totaal`} />
          <BigNum label="Volgende upload" value={<span className="text-[22px]">{gepland[0] ? new Date(gepland[0].datum!).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' }) : nu ? `Video ${nu.nr}` : '—'}</span>}
            info="Wat er als volgende online komt: een ingeplande video of de video die nu in productie is." sub={gepland[0] ? gepland[0].title : nu ? `${nu.werktitel}: in productie` : ''} />
        </div>

        <div className="mb-5 grid grid-cols-1 gap-3 md:grid-cols-2">
          <div className="panel flex items-center gap-4 p-4">
            <span className="text-4xl">{streak ? '🔥' : '🧊'}</span>
            <div><div className="font-display text-[22px] font-bold text-white">{streak} {streak === 1 ? 'week' : 'weken'} op rij</div><div className="text-[14px] text-slate-400">{streak ? 'Elke week een lange video online. Hou de vlam brandend!' : 'Zet deze week een lange video online om je streak te starten.'}</div></div>
          </div>
          <div className="panel p-4">
            <div className="flex items-baseline justify-between"><span className="font-display text-[18px] font-bold text-white">Op weg naar {goal.toLocaleString('nl-NL')} abonnees</span><span className="text-[14px] font-semibold text-orange-300">{subs}/{goal}</span></div>
            <div className="mt-2 h-3 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-gradient-to-r from-orange-400 to-sky-400" style={{ width: `${Math.min(100, (subs / goal) * 100)}%` }} /></div>
            <div className="mt-1 text-[13px] text-slate-400">{eta ? `In dit tempo haal je het over ongeveer ${eta} dagen.` : 'Na een paar dagen meten zie je hier wanneer je het haalt.'}</div>
          </div>
        </div>

        <OrdersPanel quick={QUICK} />

        <section className="mb-5">
          <h2 className="mb-2 flex items-center font-display text-[20px] font-bold text-sky-300">Nu bezig ({bezig.length})<Info text="Claude-taken die nu aan het werk zijn. Het balkje toont hoe ver de video is." /></h2>
          {bezig.length ? <div className="grid grid-cols-1 gap-3 md:grid-cols-2">{bezig.slice(0, 4).map((a) => <ActCard key={a.id || a.session} a={a} />)}</div> : <div className="panel p-4 text-[15px] text-slate-400">Er werkt nu geen taak.</div>}
          {bezig.length > 4 && <button className="mt-2 text-[14px] text-sky-300 hover:text-white" onClick={() => { try { localStorage.setItem('driftmark-view-meer', 'threads'); } catch { /* */ } setPage('meer'); }}>Alle {bezig.length} taken bekijken →</button>}
        </section>

        <div className="mb-4"><CursusTip /></div>
        <RepliesPanel />
        <AutomationPanel />

        <section className="panel mb-5 border-orange-400/30 p-4">
          <div className="mb-2 flex items-center gap-2 font-display text-[18px] font-bold text-orange-300"><Play size={16} />Hierna</div>
          {nu && <div className="mb-2 text-[15px] text-white">Nu in productie: <b>video {nu.nr}, {nu.werktitel}</b></div>}
          <ol className="list-decimal space-y-1 pl-5 text-[14px] text-slate-300">{NEXT.map((n) => <li key={n}>{n}</li>)}</ol>
          <div className="mt-3 text-[13px] text-slate-400"><span className="font-semibold text-orange-300">Wat de cijfers zeggen:</span> {CHANNEL.insight}</div>
        </section>
      </>)}

      {view === 'kalender' && <UploadCalendar vids={(yt?.videos ?? []) as Any} />}

      {view === 'threads' && (
        <div className="grid gap-4">
          <div className="flex flex-wrap gap-3 text-[13px] text-slate-300">
            <span>{activity.length} taken</span>
            <span style={{ color: STATE.working[1] }}>● {bezig.length} bezig</span>
            <span style={{ color: STATE.blocked[1] }}>● {wachten.length} wacht op jou</span>
            <span className="text-slate-500">● {activity.filter((a) => a.state === 'done').length} klaar</span>
            <button className="ml-auto btn-ghost !py-1 text-[13px]" onClick={() => openGesprek({ kind: 'project', title: 'Projectchat' })}><MessageSquare size={13} />Projectchat lezen</button>
          </div>
          <ThreadsStand />
          {[...new Set([...[...VIDEOS.map((v) => v.nr), ...activity.map((a) => a.video ?? 0)].filter((n) => n > 0).sort((a, b) => b - a), 0])].map((nr) => {
            const list = activity.filter((a) => (a.video ?? 0) === nr);
            if (!list.length) return null;
            const v = VIDEOS.find((x) => x.nr === nr);
            return (
              <Section key={nr} icon={<Users size={16} />} title={nr ? `Video ${nr}${v ? ` · ${v.werktitel}` : ''}` : 'Kanaal, HQ en overig'}>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 xl:grid-cols-3">{list.map((a) => <ActCard key={a.id || a.session} a={a} />)}</div>
              </Section>
            );
          })}
        </div>
      )}

      {view === 'youtube' && <YouTubeStats />}
      {view === 'cursus' && <><CursusCheck /><TitelTester /></>}
      {view === 'videos' && <div className="grid gap-3 lg:grid-cols-2">{[...VIDEOS].reverse().map((v) => <VideoCard key={v.nr} v={v} />)}</div>}

      {view === 'shorts' && (
        <Section icon={<Clapperboard size={16} />} title="Shorts">
          <div className="grid gap-2 sm:grid-cols-2">
            {SHORTS.map((s) => (
              <div key={s.title} className="rounded-xl bg-white/[.03] p-3">
                <div className="flex items-center justify-between gap-2"><span className="text-[13px] font-semibold text-white">{s.title}</span><span className="text-[12px] text-emerald-300">{s.status}</span></div>
                <ul className="mt-1 space-y-0.5 text-[13px] text-slate-400">{s.items.map((i) => <li key={i}>• {i}</li>)}</ul>
                <div className="mt-1 text-[12px] text-slate-500">{s.where}</div>
              </div>
            ))}
          </div>
          <button onClick={() => go('youtube')} className="btn-ghost mt-3 text-[13px]"><Youtube size={14} />Alle shorts met weergaven, likes en kijkduur staan in Op YouTube</button>
        </Section>
      )}

      {view === 'cast' && (
        <div className="grid gap-4">
          <Section icon={<Users size={16} />} title="Cast" right={<Tabs value={castTab} onChange={setCastTab} items={[{ id: 'v1', label: 'Video 1' }, { id: 'v2', label: 'Video 2' }, { id: 'v3', label: 'Video 3' }]} />}>
            <div className="mb-2 text-[13px] text-slate-400">{CAST.hoofd}. Gezin: {CAST.gezin.join(', ')}. Vast: {CAST.vast.join(', ')}.</div>
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

      {view === 'werkwijze' && <CursusStappen />}
      {view === 'werkwijze' && (
        <Section icon={<ListChecks size={16} />} title="Werkwijze & regels">
          <div className="grid gap-2 sm:grid-cols-2">
            {RULES.map((r) => (
              <div key={r.title} className="rounded-xl bg-white/[.03] p-3">
                <div className="text-[13px] font-semibold text-white">{r.title}</div>
                <ul className="mt-1 space-y-0.5 text-[13px] text-slate-400">{r.items.map((i) => <li key={i}>✓ {i}</li>)}</ul>
              </div>
            ))}
          </div>
        </Section>
      )}

      {view === 'gereedschap' && (
        <div className="grid gap-4 xl:grid-cols-2">
          <div className="xl:col-span-2"><ToolsPanel /></div>
          <Section icon={<Mic size={16} />} title="Stemmen (ElevenLabs v4)">
            {VOICE_SETS.map((set) => (
              <div key={set.video} className="mb-3 last:mb-0">
                <div className="mb-1 text-[12px] font-bold uppercase tracking-wider text-slate-400">{set.video}</div>
                <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
                  {set.stemmen.map(([r, id]) => <div key={r} className="flex justify-between gap-2 rounded-lg bg-white/[.03] px-2 py-1 text-[13px]"><span className="text-slate-300">{r}</span><code className="text-slate-500">{id}</code></div>)}
                </div>
              </div>
            ))}
          </Section>
          <Section icon={<Wrench size={16} />} title="Waarvoor gebruik je wat">
            <div className="space-y-1.5">{TOOLS.map((t) => <div key={t.name} className="text-[13px]"><span className="font-semibold text-white">{t.name}</span> <span className="text-slate-400">· {t.use}</span></div>)}</div>
          </Section>
          <CostsPanel />
        </div>
      )}

      {view === 'ideeen' && (
        <div className="grid gap-4 xl:grid-cols-2">
          <Section icon={<Lightbulb size={16} />} title="Ideeën voor video 4+">
            <div className="flex flex-wrap gap-1.5">
              {IDEAS.map((i) => <span key={i.title} className="rounded-lg bg-white/[.04] px-2 py-1 text-[13px] text-slate-300"><span className="text-slate-500">{i.groep}:</span> {i.title}</span>)}
            </div>
            <div className="mt-2 text-[13px] text-slate-500">Werkt goed bij IFOLOGY: tijd/snelheid, een getal in de titel, je lichaam dat verandert.</div>
          </Section>
          <Section icon={<ExternalLink size={16} />} title="Documenten & links">
            <div className="grid gap-1.5 sm:grid-cols-2">{LINKS.map((l) => <div key={l.url} className="text-[13px]"><A href={l.url}>{l.title}</A></div>)}</div>
          </Section>
        </div>
      )}
    </div>
  );
}
