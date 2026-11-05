/**
 * Alles wat op Home boven het kantoor zweeft: actieve projecten, statuslegenda,
 * het afdelingspaneel (na klik op een ruimte) en het profielpaneel van een medewerker.
 * Alles is echt: taken komen uit status.json, opdrachten gaan naar Claude.
 */
import { useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, ExternalLink, LayoutDashboard, Send, User } from 'lucide-react';
import { useGame } from '../store/useGame';
import { useLive, type Activity, type Live } from '../services/live';
import { useDb } from '../services/db';
import { order } from '../services/real';
import { threadUrl } from '../data/driftmark';
import { HoloPanel, EASE } from './HoloPanel';
import { ROOMS, roomById, threadsPerRoom, statusOf, STATUS, type RoomDef, type RoomId } from './rooms';
import { useWorld, reducedMotion } from './useWorld';

const STATE_NL: Record<string, { t: string; c: string }> = {
  working: { t: 'bezig', c: '#398CFF' }, blocked: { t: 'wacht op jou', c: '#FF9F1C' }, review_ready: { t: 'klaar voor jou', c: '#FF9F1C' },
  done: { t: 'klaar', c: '#21D6A0' }, failed: { t: 'mislukt', c: '#FF3B4E' }, stopped: { t: 'gestopt', c: '#64748B' },
};
const ORDER: Record<string, number> = { failed: 0, blocked: 1, review_ready: 1, working: 2, stopped: 3, done: 4 };

/** Een paar echte regels per afdeling, uit de live stand. */
function deptInfo(r: RoomDef, d: Live, log: { kind: string; text: string; at: string }[]): string[] {
  const inProd = d.videos.filter((v) => v.status !== 'Online');
  const yt = d.youtube;
  switch (r.id) {
    case 'ceo': return [yt?.subscribers != null ? `${yt.subscribers} abonnees · ${yt.views?.toLocaleString('nl-NL') ?? '—'} weergaven` : 'Nog geen kanaalcijfers geladen', `${d.videos.filter((v) => v.status === 'Online').length} lange video's online`];
    case 'productie': return [d.blender?.stand ? `Blender: ${d.blender.stand}` : 'Geen Blender-stand bekend', ...inProd.map((v) => `Video ${v.nr}: ${v.status}`)];
    case 'publicatie': { const shorts = (yt?.videos ?? []).filter((v) => v.type === 'short'); return [`${shorts.length} shorts online`, ...inProd.slice(0, 1).map((v) => `Volgende upload: video ${v.nr} (${v.werktitel})`)]; }
    case 'script': case 'stem': return inProd.map((v) => { const s = v.steps.find((x) => x.label === (r.id === 'script' ? 'Script' : 'Stemmen')); return `Video ${v.nr}: ${r.id === 'script' ? 'script' : 'stemmen'} ${s?.done ? 'klaar' : 'nog niet klaar'}`; });
    case 'crisis': { const bad = log.filter((l) => l.kind !== 'info').slice(0, 3); return bad.length ? bad.map((l) => `${l.kind}: ${l.text}`) : ['Geen fouten of waarschuwingen in het logboek']; }
    case 'onderzoek': return d.ideas ? [`${(d.ideas as unknown[]).length} ideeën in de ideeënlijst`] : [];
    case 'creatief': return inProd.map((v) => `Video ${v.nr}: "${v.title}"`);
    case 'thumbnail': return inProd.map((v) => `Video ${v.nr}: thumbnail ${(d.outputs?.[String(v.nr)] ?? []).some((o) => /thumb/i.test(o.path)) ? 'ligt klaar' : 'nog maken'}`);
    case 'coach': return ['Praat met Claude, bekijk je briefing, doelen en beslissingen'];
  }
}

function OrderBox({ r }: { r: RoomDef }) {
  const [text, setText] = useState('');
  const toast = useGame((s) => s.toast);
  const send = () => { const t = text.trim(); if (!t) return; order(`[Afdeling ${r.naam} · ${r.agent}] ${t}`, toast); setText(''); };
  return (
    <div className="rounded-xl border border-white/10 bg-black/20 p-3">
      <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Opdracht geven aan {r.agent}</div>
      <textarea className="input min-h-[64px] resize-none text-[13px]" value={text} onChange={(e) => setText(e.target.value)} placeholder={r.voorbeeld}
        onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) send(); }} />
      <div className="mt-2 flex items-center justify-between gap-2">
        <button className="text-[12px] text-slate-400 hover:text-white" onClick={() => setText(r.voorbeeld)}>Voorbeeld gebruiken</button>
        <button className="btn-primary !px-3 !py-1.5 text-[13px]" disabled={!text.trim()} onClick={send}><Send size={14} />Versturen</button>
      </div>
      <div className="mt-1.5 text-[11px] text-slate-500">Gaat als echte opdracht naar Claude. Het antwoord verschijnt bij Home onder Antwoorden.</div>
    </div>
  );
}

function TaskRow({ a }: { a: Activity }) {
  const s = STATE_NL[a.state] ?? { t: a.state, c: '#94A3B8' };
  return (
    <a href={threadUrl(a.id)} target="_blank" rel="noreferrer" className="group block rounded-lg border border-white/[.06] bg-white/[.025] px-3 py-2 transition hover:border-white/20 hover:bg-white/[.05]">
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: s.c, boxShadow: `0 0 8px ${s.c}` }} />
        <span className="min-w-0 flex-1 truncate text-[13px] font-semibold text-white">{a.title}</span>
        <span className="shrink-0 text-[11px] font-semibold" style={{ color: s.c }}>{s.t}</span>
        <ExternalLink size={12} className="shrink-0 text-slate-500 group-hover:text-white" />
      </div>
      {(a.doing || a.last) && <div className="mt-0.5 line-clamp-2 pl-4 text-[12px] text-slate-400">{a.doing ?? a.last}</div>}
    </a>
  );
}

function DeptPanel({ r }: { r: RoomDef }) {
  const d = useLive((s) => s.data);
  const log = useDb((s) => s.log);
  const setPage = useGame((s) => s.setPage);
  const { setFocus, openWorker } = useWorld();
  const list = useMemo(() => threadsPerRoom(d.activity)[r.id].slice().sort((a, b) => (ORDER[a.state] ?? 9) - (ORDER[b.state] ?? 9)), [d.activity, r.id]);
  const st = r.id === 'coach' ? 'werkt' : statusOf(list);
  const info = deptInfo(r, d, log);
  const n = (f: (a: Activity) => boolean) => list.filter(f).length;
  return (
    <HoloPanel title={<span><span className="mr-1.5">{r.icon}</span>{r.naam}</span>} sub={r.sub} accent={r.color} onClose={() => setFocus(null)} className="max-h-full">
      <div className="space-y-3 p-4">
        <button onClick={() => openWorker(r.id)} className="flex w-full items-center gap-3 rounded-xl border border-white/10 bg-white/[.03] p-3 text-left transition hover:border-white/25">
          <span className="flex h-10 w-10 items-center justify-center rounded-full" style={{ background: `${r.color}26`, boxShadow: `inset 0 0 0 1px ${r.color}66` }}><User size={18} style={{ color: r.color }} /></span>
          <span className="min-w-0 flex-1"><span className="block text-[14px] font-bold text-white">{r.agent}</span><span className="block truncate text-[12px] text-slate-400">{r.rol}</span></span>
          <span className="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold" style={{ color: STATUS[st].kleur, background: `${STATUS[st].kleur}1f` }}>{STATUS[st].label}</span>
        </button>
        <div className="grid grid-cols-3 gap-2 text-center">
          {[['Bezig', n((a) => a.state === 'working'), '#398CFF'], ['Wacht op jou', n((a) => a.state === 'blocked' || a.state === 'review_ready'), '#FF9F1C'], ['Klaar', n((a) => a.state === 'done'), '#21D6A0']].map(([l, v, c]) => (
            <div key={l as string} className="rounded-xl border border-white/[.07] bg-black/20 py-2"><div className="font-display text-xl font-bold" style={{ color: c as string }}>{v as number}</div><div className="text-[11px] text-slate-400">{l as string}</div></div>
          ))}
        </div>
        {info.length > 0 && (
          <div className="rounded-xl border border-white/[.07] bg-black/20 p-3 text-[13px] text-slate-300">
            {info.map((x, i) => <div key={i} className="flex gap-2"><span style={{ color: r.color }}>›</span><span className="min-w-0">{x}</span></div>)}
          </div>
        )}
        <div>
          <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Taken ({list.length})</div>
          <div className="space-y-1.5">
            {list.length === 0 && <div className="text-[13px] text-slate-500">Nog geen taken voor deze afdeling.</div>}
            {list.slice(0, 8).map((a) => <TaskRow key={a.id} a={a} />)}
          </div>
        </div>
        {r.page && (
          <button onClick={() => setPage(r.page!)} className="flex w-full items-center justify-between rounded-xl border px-3 py-2.5 text-[14px] font-semibold text-white transition hover:brightness-125" style={{ borderColor: `${r.color}66`, background: `${r.color}1a` }}>
            {r.pageLabel}<ArrowRight size={16} />
          </button>
        )}
        <OrderBox r={r} />
      </div>
    </HoloPanel>
  );
}

function WorkerPanel({ r }: { r: RoomDef }) {
  const d = useLive((s) => s.data);
  const openWorker = useWorld((s) => s.openWorker);
  const list = useMemo(() => threadsPerRoom(d.activity)[r.id], [d.activity, r.id]);
  const st = r.id === 'coach' ? 'werkt' : statusOf(list);
  const nu = list.find((a) => a.state === 'working') ?? list.find((a) => a.state === 'blocked' || a.state === 'review_ready');
  const results = (d.replies ?? []).filter((x) => r.match.test(x.opdracht) || x.opdracht.includes(r.naam)).slice(0, 4);
  return (
    <HoloPanel title={r.agent} sub={`${r.naam} · ${r.rol}`} accent={r.color} onClose={() => openWorker(null)} className="max-h-full">
      <div className="space-y-3 p-4">
        <div className="flex items-center gap-3">
          <span className="flex h-14 w-14 items-center justify-center rounded-2xl text-2xl" style={{ background: `${r.color}22`, boxShadow: `inset 0 0 0 1px ${r.color}77, 0 0 24px ${r.color}33` }}>{r.icon}</span>
          <div>
            <div className="flex items-center gap-2 text-[13px] font-bold" style={{ color: STATUS[st].kleur }}><span className="h-2.5 w-2.5 rounded-full" style={{ background: STATUS[st].kleur, boxShadow: `0 0 10px ${STATUS[st].kleur}` }} />{STATUS[st].label}</div>
            <div className="text-[12px] text-slate-400">Afdeling {r.naam}</div>
          </div>
        </div>
        <div className="rounded-xl border border-white/[.07] bg-black/20 p-3">
          <div className="text-[12px] font-bold uppercase tracking-wider text-slate-400">Huidige opdracht</div>
          <div className="mt-1 text-[14px] text-white">{nu ? nu.title : 'Geen lopende opdracht'}</div>
          {nu?.doing && <div className="mt-0.5 text-[12px] text-slate-400">{nu.doing}</div>}
        </div>
        <div>
          <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Laatste updates</div>
          <div className="space-y-1.5">{list.slice(0, 4).map((a) => <TaskRow key={a.id} a={a} />)}{list.length === 0 && <div className="text-[13px] text-slate-500">Nog niets.</div>}</div>
        </div>
        <div>
          <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Resultaten</div>
          {results.length === 0 && <div className="text-[13px] text-slate-500">Nog geen beantwoorde opdrachten voor deze afdeling.</div>}
          {results.map((x, i) => (
            <div key={i} className="mb-1.5 rounded-lg border border-white/[.06] bg-white/[.025] px-3 py-2 text-[12px]">
              <div className="font-semibold text-white">{x.opdracht}</div><div className="mt-0.5 line-clamp-3 text-slate-400">{x.antwoord}</div>
            </div>
          ))}
        </div>
        <OrderBox r={r} />
      </div>
    </HoloPanel>
  );
}

/** Actieve projecten linksonder (echte video's). */
function Projects() {
  const vids = useLive((s) => s.data.videos);
  const setPage = useGame((s) => s.setPage);
  const act = vids.filter((v) => v.status !== 'Online').sort((a, b) => b.nr - a.nr);
  if (!act.length) return null;
  return (
    <div className="holo-mini pointer-events-auto w-[290px] p-3">
      <div className="mb-2 flex items-center justify-between"><span className="text-[13px] font-bold text-white">Actieve projecten ({act.length})</span><button className="text-[12px] text-sky-300 hover:text-white" onClick={() => setPage('videos')}>Alle video's →</button></div>
      {act.map((v, i) => {
        const pct = Math.round((v.steps.filter((s) => s.done).length / Math.max(1, v.steps.length)) * 100);
        const c = i === 0 ? '#FF7A24' : '#20D9FF';
        return (
          <button key={v.nr} onClick={() => setPage('videos')} className="mb-2 block w-full text-left last:mb-0">
            <div className="flex items-center justify-between text-[13px]"><span className="truncate font-semibold text-slate-100">Video {v.nr} · {v.werktitel}</span><span className="ml-2 shrink-0 font-bold" style={{ color: c }}>{pct}%</span></div>
            <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-white/[.07]"><motion.div className="h-full rounded-full" style={{ background: c, boxShadow: `0 0 10px ${c}` }} initial={{ width: 0 }} animate={{ width: `${pct}%` }} transition={{ duration: 1, ease: EASE, delay: 0.3 }} /></div>
          </button>
        );
      })}
    </div>
  );
}

function Legend() {
  return (
    <div className="holo-mini pointer-events-auto flex flex-wrap items-center gap-x-3 gap-y-1 px-3 py-2 text-[11px] text-slate-300">
      {(Object.keys(STATUS) as (keyof typeof STATUS)[]).map((k) => <span key={k} className="flex items-center gap-1"><span className="h-2 w-2 rounded-full" style={{ background: STATUS[k].kleur }} />{STATUS[k].label}</span>)}
    </div>
  );
}

/** Snelkoppelingen naar elke afdeling (handig op telefoon en voor toetsenbord). */
function RoomChips() {
  const { focus, setFocus } = useWorld();
  const per = threadsPerRoom(useLive((s) => s.data.activity));
  return (
    <div className="pointer-events-auto flex max-w-full gap-1.5 overflow-x-auto pb-1">
      {ROOMS.map((r) => {
        const st = r.id === 'coach' ? 'werkt' : statusOf(per[r.id]);
        return (
          <button key={r.id} onClick={() => setFocus(focus === r.id ? null : r.id)} className="glass-chip shrink-0" style={{ ['--c' as string]: r.color }} data-active={focus === r.id}>
            <span>{r.icon}</span>{r.naam}<span className="h-1.5 w-1.5 rounded-full" style={{ background: STATUS[st].kleur }} />
          </button>
        );
      })}
    </div>
  );
}

export default function HomeHud() {
  const { focus, worker } = useWorld();
  const setPage = useGame((s) => s.setPage);
  const r = roomById(worker ?? focus);
  const rm = reducedMotion();
  return (
    <div className="pointer-events-none absolute inset-0">
      <motion.div className="absolute left-3 top-3 right-3 flex flex-wrap items-start justify-start gap-2 md:left-5 md:top-4 xl:left-auto xl:right-5 xl:justify-end" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: rm ? 0 : 0.6, duration: 0.5 }}>
        <div className="holo-mini pointer-events-auto hidden px-3 py-2 text-[12px] text-slate-300 lg:block">Klik op een afdeling of medewerker · sleep om te schuiven · scroll om te zoomen</div>
        <button onClick={() => setPage('overzicht')} className="glass-chip pointer-events-auto xl:hidden" style={{ ['--c' as string]: '#FF7A24' }}><LayoutDashboard size={14} />Dagoverzicht</button>
      </motion.div>
      <motion.div className="absolute bottom-[92px] left-3 hidden space-y-2 md:block lg:left-5" initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: rm ? 0 : 0.7, duration: 0.6, ease: EASE }}>
        <Projects />
        <Legend />
      </motion.div>
      <div className="absolute inset-x-3 bottom-[76px] md:hidden"><RoomChips /></div>
            <AnimatePresence mode="wait">
        {r && (
          <motion.div key={(worker ? 'w' : 'd') + r.id} className="absolute inset-x-2 bottom-[72px] top-24 flex md:inset-x-auto md:bottom-[84px] md:right-4 md:top-4 md:w-[400px]"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
            {worker ? <WorkerPanel r={r} /> : <DeptPanel r={r} />}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


export type { RoomId };
