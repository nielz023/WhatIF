import { useState } from 'react';
import { ExternalLink, Film, Clapperboard, Users, Map, ListChecks, Lightbulb, Wrench, Mic, Youtube, Play, Building2 } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Tabs } from '../components/ui';
import { CHANNEL, VIDEOS, SHORTS, RULES, CAST, VOICES, TOOLS, LINKS, IDEAS, NEXT, UPDATED, threadUrl, type RealVideo } from '../data/driftmark';
import gallery from '../data/gallery.json';
import { useReal } from '../services/real';

const AVAIL: Record<string, [string, string]> = {
  laden: ['Verbinding controleren…', '#94a3b8'],
  available: ['Claude luistert mee: knoppen in de app worden echte opdrachten', '#10b981'],
  no_session: ['Claude luistert nu niet mee: opdrachten wachten tot je ze opnieuw verstuurt', '#f59e0b'],
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
        <div className="text-sm font-bold uppercase tracking-wider text-emerald-300">Echt-modus · opdrachten aan Claude</div>
        <span className="flex items-center gap-1.5 text-[11px]" style={{ color }}><span className="h-2 w-2 rounded-full" style={{ background: color }} />{label}</span>
      </div>
      <p className="mb-3 text-xs text-slate-400">Wat je in de game doet, gebeurt ook echt. Start New Video, taken, goedkeuren, afkeuren, publiceren, werkregels van agents, berichten op Threads en War Room-aanbevelingen gaan als opdracht naar Claude, en Claude voert ze in het project uit. Uploaden naar YouTube blijft jouw eigen stap in Studio.</p>
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
      <div className="mt-3 flex flex-wrap gap-x-3 gap-y-1 border-t border-white/5 pt-2 text-[11px]">
        {v.youtube && <A href={v.youtube}>Op YouTube</A>}
        {v.threads.map((t) => <A key={t.id} href={threadUrl(t.id)}>{t.title}</A>)}
      </div>
      <div className="mt-1.5 text-[10px] text-slate-500">Script: {v.script} · Repo-branch: {v.repoBranch}</div>
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

export default function DriftmarkPage() {
  const setPage = useGame((s) => s.setPage);
  const [castTab, setCastTab] = useState<Tab>('v3');
  const [setTab, setSetTab] = useState<Tab>('v3');
  const g = gallery as unknown as Record<string, [string, string][]> & { banner: string };
  const nu = VIDEOS.find((v) => v.status === 'In productie');

  return (
    <div className="h-full overflow-y-auto p-3 pb-28 md:p-6 md:pb-28">
      {/* HERO */}
      <div className="panel relative mb-4 overflow-hidden">
        <img src={g.banner} alt="Driftmark banner" className="h-40 w-full object-cover opacity-70 md:h-56" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#070b1d] via-[#070b1d]/40 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 flex flex-wrap items-end justify-between gap-3 p-4">
          <div>
            <div className="text-[11px] font-bold uppercase tracking-[.2em] text-amber-300">Hoofdkwartier</div>
            <div className="font-display text-3xl font-bold text-white md:text-4xl">DRIFT<span className="text-gradient">MARK</span> HQ</div>
            <div className="text-xs text-slate-300">{CHANNEL.handle} · {CHANNEL.slogan} · echte stand van {UPDATED}</div>
          </div>
          <div className="flex flex-wrap gap-2">
            <a className="btn-primary text-xs" href={CHANNEL.url} target="_blank" rel="noreferrer"><Youtube size={14} />Kanaal</a>
            <button className="btn-ghost text-xs" onClick={() => setPage('hq')}><Building2 size={14} />3D-kantoor (game)</button>
          </div>
        </div>
      </div>

      {/* STATS + NU BEZIG */}
      <div className="mb-4 grid gap-3 lg:grid-cols-3">
        <div className="grid grid-cols-2 gap-3 lg:col-span-2">
          {CHANNEL.stats.map((s) => (
            <div key={s.label} className="panel p-3">
              <div className="text-[10px] uppercase tracking-wider text-slate-500">{s.label}</div>
              <div className="font-display text-2xl font-bold text-white">{s.value}</div>
              <div className="text-[11px] text-slate-400">{s.note}</div>
            </div>
          ))}
          <div className="panel col-span-2 p-3 text-xs text-slate-300"><span className="font-semibold text-amber-300">Les uit de stats:</span> {CHANNEL.insight}</div>
        </div>
        <div className="panel border-amber-400/40 p-4">
          <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-300"><Play size={14} />Nu bezig</div>
          {nu && <div className="mb-2 text-sm font-semibold text-white">Video {nu.nr}: {nu.werktitel}<div className="text-xs font-normal text-slate-300">{nu.notes[1]}</div></div>}
          <div className="mb-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">Volgende stappen</div>
          <ol className="list-decimal space-y-1 pl-4 text-xs text-slate-300">{NEXT.map((n) => <li key={n}>{n}</li>)}</ol>
        </div>
      </div>

      <OrdersPanel />

      {/* VIDEOS */}
      <div className="mb-2 flex items-center gap-2 text-sm font-bold uppercase tracking-wider text-slate-200"><Film size={16} />Video's</div>
      <div className="mb-4 grid gap-3 xl:grid-cols-3">{[...VIDEOS].reverse().map((v) => <VideoCard key={v.nr} v={v} />)}</div>

      <div className="grid gap-4 xl:grid-cols-2">
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
        </Section>

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

        <Section icon={<Lightbulb size={16} />} title="Ideeën voor video 4+">
          <div className="flex flex-wrap gap-1.5">
            {IDEAS.map((i) => <span key={i.title} className="rounded-lg bg-white/[.04] px-2 py-1 text-[11px] text-slate-300"><span className="text-slate-500">{i.groep}:</span> {i.title}</span>)}
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Werkt goed bij IFOLOGY: tijd/snelheid, een getal in de titel, je lichaam dat verandert.</div>
        </Section>

        <Section icon={<Mic size={16} />} title="Stemmen (ElevenLabs v4)">
          <div className="grid grid-cols-1 gap-1 sm:grid-cols-2">
            {VOICES.map(([r, id]) => <div key={r} className="flex justify-between gap-2 rounded-lg bg-white/[.03] px-2 py-1 text-[11px]"><span className="text-slate-300">{r}</span><code className="text-slate-500">{id}</code></div>)}
          </div>
        </Section>

        <Section icon={<Wrench size={16} />} title="Gereedschap">
          <div className="space-y-1.5">{TOOLS.map((t) => <div key={t.name} className="text-xs"><span className="font-semibold text-white">{t.name}</span> <span className="text-slate-400">· {t.use}</span></div>)}</div>
        </Section>

        <Section icon={<ExternalLink size={16} />} title="Documenten & links">
          <div className="grid gap-1.5 sm:grid-cols-2">{LINKS.map((l) => <div key={l.url} className="text-xs"><A href={l.url}>{l.title}</A></div>)}</div>
        </Section>
      </div>

      <div className="mt-4 text-center text-[11px] text-slate-500">Deze pagina toont de echte stand. In het 3D-kantoor, Projects, Agents en Finances lopen de cijfers als simulatie, maar jouw acties daar worden echte opdrachten.</div>
    </div>
  );
}
