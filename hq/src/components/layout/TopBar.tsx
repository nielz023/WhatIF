import { useWorld } from '../../world/useWorld';
import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bell, Users, MonitorPlay, Eye, Tv, HelpCircle, Settings } from 'lucide-react';
import { openGesprek } from '../shared/Gesprek';
import { useShallow } from 'zustand/react/shallow';
import { KLEUR } from '../../lib/status';
import Geluid, { GeluidIcoon } from '../shared/Geluid';
import { useGame } from '../../store/useGame';
import { compact, relTime } from '../../lib/util';
import { DemoBadge, Empty, Telt } from '../ui';
import { useLive } from '../../services/live';
import { WalkButton } from '../../world/WalkHud';
import Keuzes from '../shared/Keuzes';
import { BalkKnop } from '../shared/Opdrachtbalk';

/** meldingen over threads openen de echte takenlijst (Vandaag → Alle taken), ook als Vandaag al open staat */
export function openTaken() {
  try { localStorage.setItem('driftmark-view-home', 'threads'); } catch { /* */ }
  useGame.getState().setPage('overzicht');
  window.dispatchEvent(new CustomEvent('dm-view', { detail: { mode: 'home', view: 'threads' } }));
}

type NFilter = 'alles' | 'ongelezen' | 'klaar' | 'fout';
const NKLEUR: Record<string, string> = { success: KLEUR.klaar, warning: KLEUR.probleem, approval: KLEUR.wacht, achievement: KLEUR.klaar, info: KLEUR.bezig };

/** Meldingencentrum (verbeterlijst punt 20): wat op jou wacht blijft bovenaan, de rest is te filteren en per stuk op gelezen te zetten. */
function Meldingen({ close }: { close: () => void }) {
  const s = useGame();
  const wacht = useLive(useShallow((x) => x.data.activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready')));
  const [f, setF] = useState<NFilter>('alles');
  const lijst = s.notifications.filter((n) => f === 'alles' ? true : f === 'ongelezen' ? !n.read : f === 'klaar' ? n.kind === 'success' : n.kind === 'warning');
  const lees = (id: string) => useGame.setState((st) => { const x = st.notifications.find((y) => y.id === id); if (x) x.read = true; });
  const chips: [NFilter, string][] = [['alles', 'Alles'], ['ongelezen', 'Ongelezen'], ['klaar', 'Klaar'], ['fout', 'Fouten']];
  return (
    <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} className="panel absolute right-0 top-12 w-[380px] max-w-[92vw] overflow-hidden border-sky-500/30">
      <div className="flex items-center justify-between border-b border-hq-line/70 px-4 py-2.5">
        <span className="font-semibold text-white">Meldingen</span>
        <button className="text-[13px] text-sky-300 hover:text-white" onClick={s.markAllRead}>Alles gelezen</button>
      </div>
      <div className="max-h-[480px] overflow-y-auto">
        {wacht.length > 0 && (
          <div className="border-b border-hq-line/60 bg-orange-500/[.06] px-2 py-2">
            <div className="px-2 pb-1 text-[11px] font-bold uppercase tracking-widest text-orange-300">Wacht op jou ({wacht.length})</div>
            {wacht.map((a) => (
              <div key={a.id || a.title} className="rounded-lg px-2 py-1.5 hover:bg-white/5">
                <button onClick={() => { close(); if (a.id) openGesprek({ kind: 'thread', thread: a.id, title: a.title }); }} className="block w-full text-left">
                  <div className="flex items-center gap-2"><span className="h-2 w-2 shrink-0 rounded-full bg-orange-400 shadow-[0_0_8px_#ff9f1c]" /><span className="min-w-0 flex-1 truncate text-[13px] font-semibold text-white">{a.title}</span></div>
                  <div className="line-clamp-2 pl-4 text-[12px] text-slate-300">{a.needs || a.doing}</div>
                </button>
                <div className="pl-4"><Keuzes a={a} klein /></div>
              </div>
            ))}
          </div>
        )}
        <div className="flex gap-1 px-3 pt-2">
          {chips.map(([id, l]) => <button key={id} onClick={() => setF(id)} className={`rounded-full px-2.5 py-1 text-[12px] font-semibold ${f === id ? 'bg-sky-500/25 text-white' : 'bg-white/5 text-slate-400 hover:text-white'}`}>{l}</button>)}
        </div>
        {lijst.length === 0 && (
          <div className="p-3">
            <Empty icon={<Bell size={16} />} titel={f === 'alles' ? 'Nog geen meldingen' : 'Niets in deze lijst'}>
              {f === 'alles' ? 'Zodra een taak klaar is, iets misgaat of iets op jou wacht, zie je het hier.' : 'Kies Alles om alle meldingen te zien.'}
            </Empty>
          </div>
        )}
        {lijst.slice(0, 60).map((n) => (
          <div key={n.id} className={`group flex w-full items-start gap-2 border-b border-hq-line/40 px-4 py-2.5 text-left text-sm hover:bg-white/5 ${n.read ? 'text-slate-400' : 'text-slate-100'}`}>
            <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full" style={{ background: n.read ? 'transparent' : (NKLEUR[n.kind] ?? '#3db8ff'), border: n.read ? '1px solid #334155' : 'none' }} />
            <button className="flex-1 text-left" onClick={() => { lees(n.id); if (n.link === 'meer') openTaken(); else if (n.link) s.setPage(n.link); close(); }}>{n.text}</button>
            <span className="flex shrink-0 flex-col items-end gap-1">
              <span className="text-[12px] text-slate-500">{relTime(n.tick, s.tick)}</span>
              {!n.read && <button onClick={() => lees(n.id)} className="text-[11px] text-sky-300 opacity-70 hover:opacity-100" title="Op gelezen zetten">✓ gelezen</button>}
            </span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

/** cijfer in de kopbalk; buiten TopBar gedefinieerd, zodat hij niet bij elke render opnieuw begint met tellen */
function Stat({ icon, label, value, color, vanaf = 'md:flex' }: { icon: React.ReactNode; label: string; value: React.ReactNode; color: string; vanaf?: string }) {
  return (
    <div className={`glass-stat hidden items-center gap-2.5 px-3 py-1.5 ${vanaf}`}>
      <span style={{ color }}>{icon}</span>
      <div className="leading-tight">
        <div className="whitespace-nowrap text-[11px] font-semibold text-slate-400">{label}</div>
        <div className="getal text-sm text-white"><Telt value={value} /></div>
      </div>
    </div>
  );
}

export default function TopBar() {
  const s = useGame();
  const live = useLive((x) => x.data);
  const unread = s.notifications.filter((n) => !n.read).length + live.activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready').length;

  return (
    <header className="dm-kopbalk relative z-50 flex h-[64px] shrink-0 items-center gap-2 px-3 md:px-5" style={{ ['--dm-banner' as string]: 'url(./img/banner.jpg)' }}>
      {/* logo en woordmerk van het kanaal (verbeterlijst punt 27) */}
      <button onClick={() => s.setPage('overzicht')} className="mr-2 flex shrink-0 items-center gap-2.5" title="Naar Vandaag" aria-label="Driftmark HQ, naar Vandaag">
        <img src="./merk/logo.webp" alt="" width={40} height={40} className="dm-logo h-10 w-10" />
        <span className="hidden flex-col items-start leading-none sm:flex">
          <img src="./merk/woordmerk.webp" alt="Driftmark" width={118} height={21} className="dm-woordmerk h-[21px] w-[118px]" />
          <span className="mt-1 text-[10px] font-bold uppercase tracking-[.32em] text-[#7fb3ff]">Studio HQ</span>
        </span>
      </button>
      <Stat icon={<Users size={16} />} vanaf="lg:flex" label="Claude bezig" value={live.activity.filter((a) => a.state === 'working').length} color="#3db8ff" />
      <Stat icon={<Tv size={16} />} label="Abonnees" value={live.youtube?.subscribers ?? '—'} color="#ff8a3d" />
      <Stat icon={<Eye size={16} />} label="Weergaven" value={live.youtube?.views != null ? compact(live.youtube.views) : (live.channel.stats[0]?.value ?? '—')} color="#3db8ff" />
      <Stat icon={<MonitorPlay size={16} />} label="Video's online" value={live.videos.filter((v) => v.status === 'Online').length} color="#3ddc97" vanaf="2xl:flex" />
      {s.demoMode && <span className="hidden xl:inline"><DemoBadge /></span>}

      <div className="ml-auto flex items-center gap-2">
        <BalkKnop />
        <WalkButton />
        {/* echte klok */}
        <span className="hidden sm:inline"><RealClock /></span>
        <QualityBtn />
        <SoundBtn />
        <button onClick={() => s.setPage('settings')} className="hidden rounded-xl border border-hq-line/60 bg-hq-panel/60 p-2 text-slate-300 hover:text-white sm:block" aria-label="Instellingen" title="Instellingen"><Settings size={18} /></button>
        <button onClick={() => window.dispatchEvent(new Event('dm-tour'))} className="rounded-xl border border-hq-line/60 bg-hq-panel/60 p-2 text-slate-300 hover:text-white" aria-label="Uitleg: rondleiding" title="Rondleiding: hoe werkt het HQ?"><HelpCircle size={18} /></button>

        {/* notifications */}
        <div className="relative">
          <button onClick={() => s.setNotifOpen(!s.notifOpen)} className="relative rounded-xl border border-hq-line/60 bg-hq-panel/60 p-2 text-slate-300 hover:text-white" aria-label="Meldingen">
            <Bell size={18} />
            {unread > 0 && <span className="absolute -right-1 -top-1 min-w-[18px] rounded-full bg-rose-500 px-1 text-center text-[12px] font-bold text-white shadow-[0_0_10px_#f43f5e]">{unread > 99 ? '99+' : unread}</span>}
          </button>
          <AnimatePresence>{s.notifOpen && <Meldingen close={() => s.setNotifOpen(false)} />}
          </AnimatePresence>
        </div>
        <div className="hidden h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-[#FF4DB8] to-[#A855F7] text-[14px] font-bold text-white shadow-[0_0_14px_rgba(255,77,184,.45)] sm:flex" title="niels">N</div>
      </div>
    </header>
  );
}

function RealClock() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const id = setInterval(() => setNow(new Date()), 15000); return () => clearInterval(id); }, []);
  return (
    <div className="flex items-center gap-2 rounded-xl border border-hq-line/60 bg-hq-panel/60 px-3 py-1.5" title="Het HQ loopt gelijk met de echte tijd">
      <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
      <span className="whitespace-nowrap text-[13px] font-semibold text-slate-200">{now.toLocaleString('nl-NL', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' })}</span>
      <span className="hidden whitespace-nowrap text-[11px] uppercase tracking-wider text-slate-500 2xl:inline">echte tijd</span>
    </div>
  );
}

function QualityBtn() {
  const q = useWorld((s) => s.quality); const setQ = useWorld((s) => s.setQuality);
  const next = { auto: '4k', '4k': 'snel', snel: 'auto' } as const;
  const label = { auto: 'Auto', '4k': '4K', snel: 'Snel' }[q];
  const uitleg = { auto: 'Auto: scherp waar het kan, soepel waar het moet', '4k': '4K-scherp: het 3D-kantoor op volle schermresolutie (zwaarder)', snel: 'Snel: lagere resolutie voor de hoogste fps' }[q];
  return (
    <button onClick={() => setQ(next[q])} title={uitleg + ' · klik om te wisselen'} aria-label={'Beeldkwaliteit: ' + label} className="hidden items-center gap-1.5 rounded-xl border border-hq-line/60 bg-hq-panel/60 px-2 py-1.5 font-mono text-[11px] text-slate-300 hover:text-white lg:inline-flex">
      <span className={q === '4k' ? 'text-[#FF8A3D]' : q === 'snel' ? 'text-[#21D6A0]' : 'text-[#3db8ff]'}>{label}</span>
      <span id="dm-fps">— fps</span>
    </button>
  );
}

function SoundBtn() {
  const [open, setOpen] = useState(false);
  const { theme, setTheme, focusMode, setFocusMode, quality, setQuality } = useWorld();
  useEffect(() => {
    if (!open) return;
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', k); return () => window.removeEventListener('keydown', k);
  }, [open]);
  const Seg = <T extends string>({ value, opts, set }: { value: T; opts: [T, string][]; set: (v: T) => void }) => (
    <div className="grid grid-flow-col gap-1 rounded-lg bg-black/30 p-1">
      {opts.map(([v, l]) => (
        <button key={v} onClick={() => set(v)} className={`rounded-md px-2 py-1 text-[12px] font-semibold ${value === v ? 'bg-white/15 text-white' : 'text-slate-400 hover:text-white'}`}>{l}</button>
      ))}
    </div>
  );
  return (
    <div className="relative">
      <button onClick={() => setOpen(!open)} className="glass-stat p-2 text-slate-300 hover:text-white" aria-expanded={open} aria-label="Geluid, thema en beeld" title="Geluid, kantoorgeluid, thema en focusmodus">
        <GeluidIcoon />
      </button>
      <AnimatePresence>
        {open && (<>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <motion.div initial={{ opacity: 0, y: -6, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.16 }}
            className="panel absolute right-0 top-12 z-50 w-[290px] space-y-3 p-4 text-slate-200 shadow-2xl">
            <div>
              <div className="mb-1.5 text-[13px] font-semibold">Geluid</div>
              <Geluid breed />
              <div className="mt-1 text-[11px] text-slate-500">Eén schuif voor klikjes, meldingen en het kantoorgeluid.</div>
            </div>
            <div><div className="mb-1 text-[13px] font-semibold">Thema</div>
              <Seg value={theme} set={setTheme} opts={[['auto', 'Klok'], ['dag', 'Dag'], ['nacht', 'Nacht'], ['feest', 'Feest']]} />
              <div className="mt-1 text-[11px] text-slate-500">Klok: licht en lucht volgen de echte tijd.</div>
            </div>
            <div><div className="mb-1 text-[13px] font-semibold">Beeld</div>
              <Seg value={quality} set={setQuality} opts={[['auto', 'Auto'], ['4k', '4K'], ['snel', 'Snel']]} />
            </div>
            <div className="flex items-center justify-between">
              <div><div className="text-[13px] font-semibold">Focusmodus</div><div className="text-[11px] text-slate-500">Kantoor gedimd, alleen wat op jou wacht.</div></div>
              <button onClick={() => setFocusMode(!focusMode)} className={`rounded-full px-3 py-1 text-[12px] font-bold ${focusMode ? 'bg-[#FF7A24]/25 text-[#FFB27A]' : 'bg-white/10 text-slate-400'}`}>{focusMode ? 'Aan' : 'Uit'}</button>
            </div>
          </motion.div>
        </>)}
      </AnimatePresence>
    </div>
  );
}
