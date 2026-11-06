/**
 * Alles wat op Home boven het kantoor zweeft: actieve projecten, statuslegenda,
 * het afdelingspaneel (na klik op een ruimte) en het profielpaneel van een medewerker.
 * Alles is echt: taken komen uit status.json, opdrachten gaan naar Claude.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { play } from './sound';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowRight, ExternalLink, LayoutDashboard, MessageSquare, RotateCcw, Send, User } from 'lucide-react';
import { useGame } from '../store/useGame';
import { useLive, type Activity, type Live } from '../services/live';
import { useDb } from '../services/db';
import { order } from '../services/real';
import { threadUrl } from '../data/driftmark';
import { HoloPanel, EASE } from './HoloPanel';
import { ROOMS, roomById, threadsPerRoom, statusOf, STATUS, type RoomDef, type RoomId } from './rooms';
import { useWorld, reducedMotion, isPhone } from './useWorld';
import { teamFor } from './staff';
import { mergePunten, puntenVoor } from '../data/verbeter';
import { openGesprek } from '../components/shared/Gesprek';
import { DeptTools } from './deptTools';
import { useCoach } from '../services/coach';

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
    <div className="group rounded-lg border border-white/[.06] bg-white/[.025] px-3 py-2 transition hover:border-white/20 hover:bg-white/[.05]">
      <div className="flex items-center gap-2">
        <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: s.c, boxShadow: `0 0 8px ${s.c}` }} />
        <a href={a.id ? threadUrl(a.id) : undefined} target="_blank" rel="noreferrer" className="min-w-0 flex-1 truncate text-[13px] font-semibold text-white hover:underline">{a.title}</a>
        <span className="shrink-0 text-[11px] font-semibold" style={{ color: s.c }}>{s.t}</span>
        {a.session && <button className="shrink-0 rounded-md p-0.5 text-slate-400 hover:bg-white/10 hover:text-white" title="Hele gesprek lezen" onClick={() => openGesprek({ kind: 'thread', session: a.session, title: a.title, thread: a.id || undefined })}><MessageSquare size={13} /></button>}
        {a.id && <a href={threadUrl(a.id)} target="_blank" rel="noreferrer" title="Open in Claude"><ExternalLink size={12} className="shrink-0 text-slate-500 group-hover:text-white" /></a>}
      </div>
      {(a.needs || a.doing || a.last) && <div className="mt-0.5 line-clamp-2 pl-4 text-[12px] text-slate-400">{a.needs && (a.state === 'blocked' || a.state === 'review_ready') ? <span className="text-orange-200">Jij: {a.needs}</span> : a.doing ?? a.last}</div>}
    </div>
  );
}

/** De drie agents van de studio (en in het CEO-kantoor het hoofdpersonage) met hun verbeterpunt. */
function Team({ r }: { r: RoomDef }) {
  const verbeter = useLive((s) => s.data.verbeter);
  const punten = useMemo(() => mergePunten(verbeter), [verbeter]);
  const rows = teamFor(r.id, punten); const all = puntenVoor(r.id, punten);
  if (!rows.length) return null;
  const af = all.filter((p) => p.klaar).length;
  return (
    <div className="rounded-xl border border-white/[.07] bg-black/20 p-3">
      <div className="mb-2 flex items-center justify-between text-[12px] font-bold uppercase tracking-wider text-slate-400"><span>Team van {r.naam}</span><span className="normal-case tracking-normal text-[#4ADE80]">{af}/{all.length} verbeterpunten af</span></div>
      <div className="space-y-1.5">
        {rows.map((t) => (
          <div key={t.name} className="flex items-start gap-2 text-[13px]">
            <span className="mt-1 h-3 w-3 shrink-0 rounded-full border border-white/20" style={{ background: t.color }} />
            <div className="min-w-0 flex-1">
              <div className="font-semibold text-white">{t.name}</div>
              {t.main ? <div className="text-[12px] text-slate-400">Leidt het bedrijf: zijn kleur toont of er iets op jou wacht</div>
                : t.task && <div className={`text-[12px] ${t.done ? 'text-[#4ADE80]' : 'text-sky-200'}`}>{t.done ? '✓ Klaar: ' : 'Verbetert: '}{t.task}</div>}
            </div>
          </div>
        ))}
      </div>
      {all.length > rows.length - (r.id === 'ceo' ? 1 : 0) && (
        <details className="mt-2 text-[12px] text-slate-400"><summary className="cursor-pointer hover:text-white">Alle verbeterpunten van deze studio</summary>
          <ul className="mt-1 space-y-0.5">{all.map((p) => <li key={p.id} className={p.klaar ? 'text-[#4ADE80]' : ''}>{p.klaar ? '✓' : '○'} {p.tekst}</li>)}</ul>
        </details>
      )}
    </div>
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
        {r.id !== 'coach' && <Team r={r} />}
        {info.length > 0 && (
          <div className="rounded-xl border border-white/[.07] bg-black/20 p-3 text-[13px] text-slate-300">
            {info.map((x, i) => <div key={i} className="flex gap-2"><span style={{ color: r.color }}>›</span><span className="min-w-0">{x}</span></div>)}
          </div>
        )}
        <div>
          <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Taken ({list.length})</div>
          <div className="space-y-1.5">
            {list.length === 0 && <div className="text-[13px] text-slate-500">Nog geen taken voor deze afdeling.</div>}
            {list.slice(0, 8).map((a) => <TaskRow key={a.id || a.session} a={a} />)}
          </div>
        </div>
        {r.id !== 'coach' && <DeptTools r={r} />}
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
          <div className="space-y-1.5">{list.slice(0, 4).map((a) => <TaskRow key={a.id || a.session} a={a} />)}{list.length === 0 && <div className="text-[13px] text-slate-500">Nog niets.</div>}</div>
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

/* ---------- mijlpalen: confetti, applaus en een melding bovenin ---------- */
function milestonesFrom(L: Live): { key: string; text: string; rank: number }[] {
  const out: { key: string; text: string; rank: number }[] = [];
  const nl = (n: number) => n.toLocaleString('nl-NL');
  const subs = L.youtube?.subscribers; const views = L.youtube?.views;
  if (subs != null) for (const m of [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]) if (subs >= m) out.push({ key: `abo:${m}`, text: `${nl(m)} abonnees!`, rank: 4 });
  if (views != null) for (const m of [1000, 5000, 10000, 15000, 20000, 25000, 50000, 100000, 250000, 500000, 1000000]) if (views >= m) out.push({ key: `views:${m}`, text: `${nl(m)} weergaven op het kanaal!`, rank: 3 });
  const online = L.videos.filter((v) => v.status === 'Online').length;
  for (let n = 1; n <= online; n++) out.push({ key: `video:${n}`, text: n === 1 ? 'Eerste lange video online!' : `${n} lange video's online!`, rank: 2 });
  for (const v of L.youtube?.videos ?? []) {
    if (!v.views || !v.id) continue;
    for (const m of [1000, 5000, 10000, 50000, 100000, 1000000]) if (v.views >= m) out.push({ key: `vid:${v.id}:${m}`, text: `"${v.title}" haalde ${nl(m)} weergaven!`, rank: 1 });
  }
  return out;
}
// al gevierd in deze sessie (ook als localStorage geblokkeerd is, anders komt hetzelfde feestje steeds terug)
const celebrated = new Set<string>();
function useMilestones() {
  const live = useLive((s) => s.data); const source = useLive((s) => s.source);
  const celebrate = useWorld((s) => s.celebrate);
  // alleen opnieuw kijken als de mijlpalen zelf veranderen, niet bij elke verversing van de live stand
  const all = useMemo(() => milestonesFrom(live), [live]);
  const sig = all.map((m) => m.key).join('|');
  useEffect(() => {
    if (source !== 'live' && source !== 'database') return; // alleen met de echte stand
    if (!all.length) return;
    let seen: string[] | null = null; try { seen = JSON.parse(localStorage.getItem('dm-mijlpalen') ?? 'null'); } catch { /* */ }
    const fresh = all.filter((m) => !seen?.includes(m.key) && !celebrated.has(m.key)); if (!fresh.length) return;
    const best = fresh.reduce((a, b) => (b.rank > a.rank || (b.rank === a.rank && all.indexOf(b) > all.indexOf(a)) ? b : a));
    const more = seen ? fresh.length - 1 : 0;
    // pas als het feestje echt begint als "gezien" opslaan (een onderbroken wachttijd mag het niet laten verdwijnen)
    const t = setTimeout(() => {
      fresh.forEach((m) => celebrated.add(m.key));
      try { localStorage.setItem('dm-mijlpalen', JSON.stringify([...(seen ?? []), ...fresh.map((m) => m.key)].slice(-400))); } catch { /* */ }
      celebrate(best.text + (more > 0 ? ` En nog ${more} andere mijlpaal${more > 1 ? 'en' : ''}.` : ''));
    }, 3600);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sig, source, celebrate]);
}
function PartyToast() {
  const party = useWorld((s) => s.party); const text = useWorld((s) => s.partyText);
  const [show, setShow] = useState(false);
  // alleen feestjes van ná het openen van Home tonen (niet het vorige opnieuw bij terugkomen)
  const startParty = useRef(useWorld.getState().party);
  useEffect(() => {
    if (!party || party <= startParty.current) return;
    setShow(true); play('applause');
    const t = setTimeout(() => setShow(false), 6500); return () => clearTimeout(t);
  }, [party]);
  return (
    <AnimatePresence>
      {show && text && (
        <motion.div key={party} className="absolute left-1/2 top-16 z-20 -translate-x-1/2 md:top-5" initial={{ opacity: 0, y: -20, scale: 0.9 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -12 }} transition={{ type: 'spring', stiffness: 260, damping: 20 }}>
          <div className="pointer-events-auto flex items-center gap-3 rounded-2xl border border-amber-300/40 bg-gradient-to-r from-[#3a1d05]/90 via-[#2a1450]/90 to-[#08243a]/90 px-5 py-3 shadow-[0_0_40px_rgba(250,204,21,.35)] backdrop-blur">
            <span className="text-2xl">🎉</span>
            <div><div className="text-[11px] font-bold uppercase tracking-widest text-amber-300">Mijlpaal</div><div className="text-[15px] font-bold text-white">{text}</div></div>
            <button onClick={() => setShow(false)} className="ml-2 rounded-md px-1.5 text-slate-400 hover:bg-white/10 hover:text-white" aria-label="Sluiten">×</button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ---------- ochtendbriefing: één keer per dag, met 3 taken voor vandaag ---------- */
function vandaagKey() { return new Date().toLocaleDateString('sv-SE', { timeZone: 'Europe/Amsterdam' }); }
function MorningBriefing() {
  const live = useLive((s) => s.data); const source = useLive((s) => s.source); const stats = useDb((s) => s.stats);
  const intro = useWorld((s) => s.intro); const focusMode = useWorld((s) => s.focusMode);
  const setPage = useGame((s) => s.setPage);
  const briefing = useCoach((s) => s.briefing);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (source !== 'live' && source !== 'database') return;
    let seen: string | null = null; try { seen = localStorage.getItem('dm-briefing'); } catch { /* */ }
    if (seen === vandaagKey()) return;
    const t = setTimeout(() => setOpen(true), 4200); return () => clearTimeout(t);
  }, [source]);
  const sluit = () => { setOpen(false); try { localStorage.setItem('dm-briefing', vandaagKey()); } catch { /* */ } };
  const taken = useMemo(() => {
    const out: { t: string; sub?: string; c: string; a?: Activity }[] = [];
    for (const a of live.activity.filter((x) => x.state === 'blocked' || x.state === 'review_ready').slice(0, 2)) out.push({ t: a.state === 'review_ready' ? `Bekijk: ${a.title}` : `Reageer op: ${a.title}`, sub: a.needs, c: '#FF9F1C', a });
    const vandaag = vandaagKey();
    const up = (live.youtube?.videos ?? []).find((v) => (v.status ?? '').startsWith('gepland') && v.datum === vandaag);
    const tijd = up && /\b(\d{1,2}:\d{2})\b/.exec(up.status ?? '')?.[1];
    if (up) out.push({ t: `Vandaag online: ${up.title}`, sub: tijd ? `gepland om ${tijd}` : up.status, c: '#3ddc97' });
    // de briefing van de coach: zijn datum in Nederlandse tijd (hij schrijft een UTC-datum)
    const bDag = briefing?.gemaakt ? new Date(briefing.gemaakt).toLocaleDateString('sv-SE', { timeZone: 'Europe/Amsterdam' }) : briefing?.datum;
    for (const x of briefing && bDag === vandaag ? briefing.acties ?? [] : []) if (out.length < 3 && x.omschrijving) out.push({ t: x.omschrijving, sub: x.reden, c: '#A855F7' });
    for (const v of live.videos.filter((x) => x.status !== 'Online')) {
      if (out.length >= 3) break;
      const st = v.steps.find((x) => x.active)?.label ?? v.steps.find((x) => !x.done)?.label;
      if (st) out.push({ t: `Video ${v.nr}: ${st.toLowerCase()} gaat door`, sub: v.werktitel || v.title, c: '#398CFF' });
    }
    return out.slice(0, 3);
  }, [live, briefing]);
  const delta = useMemo(() => {
    // alleen rijen met echte getallen (als vidIQ niet bereikbaar was, schrijft de ronde lege rijen)
    const ok = stats.filter((r) => typeof r.subscribers === 'number' && typeof r.views === 'number');
    if (ok.length < 2) return null;
    const last = ok[ok.length - 1]; const dagGeleden = Date.parse(last.at) - 864e5;
    const prev = [...ok].reverse().find((r) => Date.parse(r.at) <= dagGeleden) ?? ok[0];
    return { subs: last.subscribers! - prev.subscribers!, views: last.views! - prev.views! };
  }, [stats]);
  const h = Number(new Date().toLocaleString('nl-NL', { hour: 'numeric', hour12: false, timeZone: 'Europe/Amsterdam' }));
  const groet = h < 12 ? 'Goedemorgen' : h < 18 ? 'Goedemiddag' : 'Goedenavond';
  return (
    <AnimatePresence>
      {open && !intro && !focusMode && (
        <motion.div key="brief" className="absolute left-1/2 top-[84px] z-20 w-[min(94vw,460px)] -translate-x-1/2 md:top-[70px]" initial={{ opacity: 0, y: -14, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.35, ease: EASE }}>
          <div className="pointer-events-auto rounded-2xl border border-white/10 bg-[#0b1130]/95 p-4 shadow-2xl backdrop-blur">
            <div className="flex items-start justify-between gap-2">
              <div><div className="text-[11px] font-bold uppercase tracking-widest text-[#FF9A52]">Briefing van vandaag</div><div className="text-[18px] font-bold text-white">{groet} niels ☀️</div></div>
              <button onClick={sluit} className="rounded-md px-1.5 text-lg leading-none text-slate-400 hover:bg-white/10 hover:text-white" aria-label="Sluiten">×</button>
            </div>
            <div className="mt-1 text-[13px] text-slate-300">{live.youtube?.subscribers ?? '—'} abonnees{delta && delta.subs ? ` (${delta.subs > 0 ? '+' : ''}${delta.subs} sinds gisteren)` : ''} · {live.youtube?.views?.toLocaleString('nl-NL') ?? '—'} weergaven{delta && delta.views > 0 ? ` (+${delta.views.toLocaleString('nl-NL')})` : ''}</div>
            <div className="mt-3 text-[12px] font-bold uppercase tracking-wider text-slate-400">3 taken voor vandaag</div>
            <ol className="mt-1.5 space-y-1.5">
              {taken.map((x, i) => (
                <li key={i} className="flex gap-2.5 rounded-lg border border-white/[.06] bg-white/[.03] px-2.5 py-2">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-bold text-white" style={{ background: x.c }}>{i + 1}</span>
                  <div className="min-w-0 flex-1"><div className="text-[13px] font-semibold text-white">{x.t}</div>{x.sub && <div className="line-clamp-2 text-[12px] text-slate-400">{x.sub}</div>}</div>
                  {x.a?.session && <button onClick={() => openGesprek({ kind: 'thread', session: x.a!.session, title: x.a!.title, thread: x.a!.id || undefined })} className="shrink-0 self-center rounded-md p-1 text-slate-400 hover:bg-white/10 hover:text-white" title="Gesprek openen"><MessageSquare size={14} /></button>}
                </li>
              ))}
              {!taken.length && <li className="text-[13px] text-slate-400">Niets dringends vandaag. Alles loopt.</li>}
            </ol>
            <div className="mt-3 flex gap-2">
              <button onClick={() => { sluit(); setPage('coach'); }} className="flex-1 rounded-xl bg-[#FF7A24]/25 px-3 py-2 text-[13px] font-semibold text-white hover:bg-[#FF7A24]/40">Volledige briefing</button>
              <button onClick={sluit} className="rounded-xl bg-white/10 px-3 py-2 text-[13px] font-semibold text-slate-200 hover:bg-white/20">Begrepen</button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ---------- focusmodus: kantoor gedimd, alleen wat op jou wacht ---------- */
function FocusOverlay() {
  const on = useWorld((s) => s.focusMode); const setOn = useWorld((s) => s.setFocusMode);
  const activity = useLive((s) => s.data.activity);
  const wacht = activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready');
  const bezig = activity.filter((a) => a.state === 'working');
  return (
    <AnimatePresence>
      {on && (
        <motion.div key="focus" className="absolute inset-0 z-10 flex items-start justify-center bg-[#030614]/70 px-3 pt-20 backdrop-blur-[3px] md:items-center md:pt-0" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.35 }}>
          <div className="pointer-events-auto w-full max-w-[560px] rounded-2xl border border-white/10 bg-[#0a1030]/90 p-5 shadow-2xl">
            <div className="mb-3 flex items-center justify-between">
              <div><div className="text-[11px] font-bold uppercase tracking-widest text-[#FF9A52]">Focusmodus</div><div className="text-[18px] font-bold text-white">{wacht.length ? `${wacht.length} ${wacht.length === 1 ? 'ding wacht' : 'dingen wachten'} op jou` : 'Niets wacht op jou'}</div></div>
              <button onClick={() => setOn(false)} className="rounded-full bg-white/10 px-3 py-1 text-[12px] font-bold text-slate-200 hover:bg-white/20">Focus uit</button>
            </div>
            <div className="max-h-[52vh] space-y-2 overflow-y-auto pr-1">
              {wacht.map((a) => <TaskRow key={a.id || a.session} a={a} />)}
              {!wacht.length && <div className="rounded-lg border border-emerald-400/20 bg-emerald-400/5 px-3 py-3 text-[13px] text-emerald-200">Alles loopt. {bezig.length ? `${bezig.length} ${bezig.length === 1 ? 'taak is' : 'taken zijn'} bezig zonder dat ze jou nodig hebben.` : ''}</div>}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default function HomeHud() {
  const { focus, worker, intro } = useWorld();
  const setPage = useGame((s) => s.setPage);
  const r = roomById(worker ?? focus);
  const rm = reducedMotion();
  useMilestones();
  return (
    <div className="pointer-events-none absolute inset-0">
      <PartyToast />
      <MorningBriefing />
      <FocusOverlay />
      <motion.div className="absolute left-3 top-3 right-3 flex flex-wrap items-start justify-start gap-2 md:left-5 md:top-4 xl:left-auto xl:right-5 xl:justify-end" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: rm ? 0 : 0.6, duration: 0.5 }}>
        <div className="holo-mini pointer-events-auto hidden px-3 py-2 text-[12px] text-slate-300 lg:block">Klik op een afdeling of medewerker · rechts slepen = schuiven · scrollen = zoomen · scrollknop ingedrukt = rond draaien</div>
        <button onClick={() => setPage('overzicht')} className="glass-chip pointer-events-auto xl:hidden" style={{ ['--c' as string]: '#FF7A24' }}><LayoutDashboard size={14} />Dagoverzicht</button>
      </motion.div>
      <motion.div className="absolute bottom-[92px] left-3 hidden space-y-2 md:block lg:left-5" initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: rm ? 0 : 0.7, duration: 0.6, ease: EASE }}>
        <Projects />
        <Legend />
      </motion.div>
      <div className="absolute inset-x-3 bottom-[76px] md:hidden"><RoomChips /></div>
      <button id="dm-reset" onClick={() => window.dispatchEvent(new Event('dm-reset-view'))} style={{ display: 'none', ['--c' as string]: '#22D3EE' }}
        className="glass-chip pointer-events-auto absolute bottom-[136px] left-1/2 -translate-x-1/2 md:bottom-[92px]"><RotateCcw size={14} />Vooraanzicht</button>
      <AnimatePresence>
        {intro && (
          <motion.div key="skip" className="absolute bottom-[136px] left-1/2 -translate-x-1/2 md:bottom-[92px]" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ delay: rm ? 0 : 0.8 }}>
            <div className="holo-mini px-3 py-1.5 text-[12px] text-slate-300">{isPhone() ? 'Tik om de intro over te slaan' : 'Klik of druk op een toets om de intro over te slaan'}</div>
          </motion.div>
        )}
      </AnimatePresence>
            <AnimatePresence mode="wait">
        {r && (
          <motion.div key={(worker ? 'w' : 'd') + r.id} className="absolute inset-x-2 bottom-[72px] top-24 flex md:inset-x-auto md:bottom-[84px] md:right-4 md:top-4 md:w-[400px]"
            initial={{ opacity: 0, x: rm ? 0 : 48, scale: rm ? 1 : 0.97 }} animate={{ opacity: 1, x: 0, scale: 1 }} exit={{ opacity: 0, x: rm ? 0 : 32 }} transition={{ duration: rm ? 0.15 : 0.32, ease: EASE }}>
            {worker ? <WorkerPanel r={r} /> : <DeptPanel r={r} />}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}


export type { RoomId };
