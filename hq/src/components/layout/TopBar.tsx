import { useWorld } from '../../world/useWorld';
import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bell, Users, Wallet, Eye, Tv, HelpCircle, Volume2, VolumeX } from 'lucide-react';
import { soundOn, setSound, onSoundChange, officeVolume, setOfficeVolume, onOfficeVolume } from '../../world/sound';
import { useGame } from '../../store/useGame';
import { compact, relTime } from '../../lib/util';
import { DemoBadge } from '../ui';
import { useLive } from '../../services/live';

export default function TopBar() {
  const s = useGame();
  const live = useLive((x) => x.data);
  const unread = s.notifications.filter((n) => !n.read).length;

  const Stat = ({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: React.ReactNode; color: string }) => (
    <div className="glass-stat hidden items-center gap-2.5 px-3 py-1.5 md:flex">
      <span style={{ color }}>{icon}</span>
      <div className="leading-tight">
        <div className="text-[11px] font-semibold text-slate-400">{label}</div>
        <div className="text-sm font-bold text-white">{value}</div>
      </div>
    </div>
  );

  return (
    <header className="relative z-50 flex h-[64px] shrink-0 items-center gap-2 bg-gradient-to-b from-[#050816]/95 to-[#050816]/40 px-3 md:px-5">
      <div className="mr-2 flex items-center gap-2.5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-orange-400 via-orange-500 to-[#ff5f3d] shadow-[0_0_22px_rgba(255,122,36,.5)]"><svg viewBox="0 0 24 24" className="h-4 w-4 fill-white"><path d="M8 5.5v13l11-6.5z" /></svg></div>
        <span className="font-display text-[16px] font-bold leading-tight tracking-wide text-white md:text-[18px]">DRIFTMARK<br className="hidden md:block" /><span className="text-[#398CFF] md:text-[16px]"> HQ</span></span>
      </div>
      <Stat icon={<Users size={16} />} label="Claude bezig" value={live.activity.filter((a) => a.state === 'working').length} color="#3db8ff" />
      <Stat icon={<Tv size={16} />} label="Abonnees" value={live.youtube?.subscribers ?? '—'} color="#ff8a3d" />
      <Stat icon={<Eye size={16} />} label="Weergaven" value={live.youtube?.views != null ? compact(live.youtube.views) : (live.channel.stats[0]?.value ?? '—')} color="#3db8ff" />
      <Stat icon={<Wallet size={16} />} label="Video's online" value={live.videos.filter((v) => v.status === 'Online').length} color="#3ddc97" />
      {s.demoMode && <span className="hidden xl:inline"><DemoBadge /></span>}

      <div className="ml-auto flex items-center gap-2">
        {/* echte klok */}
        <span className="hidden sm:inline"><RealClock /></span>
        <QualityBtn />
        <SoundBtn />
        <button onClick={() => window.dispatchEvent(new Event('dm-tour'))} className="rounded-xl border border-hq-line/60 bg-hq-panel/60 p-2 text-slate-300 hover:text-white" aria-label="Uitleg: rondleiding" title="Rondleiding: hoe werkt het HQ?"><HelpCircle size={18} /></button>

        {/* notifications */}
        <div className="relative">
          <button onClick={() => s.setNotifOpen(!s.notifOpen)} className="relative rounded-xl border border-hq-line/60 bg-hq-panel/60 p-2 text-slate-300 hover:text-white" aria-label="Meldingen">
            <Bell size={18} />
            {unread > 0 && <span className="absolute -right-1 -top-1 min-w-[18px] rounded-full bg-rose-500 px-1 text-center text-[12px] font-bold text-white shadow-[0_0_10px_#f43f5e]">{unread > 99 ? '99+' : unread}</span>}
          </button>
          <AnimatePresence>
            {s.notifOpen && (
              <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} className="panel absolute right-0 top-12 w-[360px] max-w-[90vw] overflow-hidden border-sky-500/30">
                <div className="flex items-center justify-between border-b border-hq-line/70 px-4 py-2.5">
                  <span className="font-semibold text-white">Meldingen</span>
                  <button className="text-[13px] text-sky-300 hover:text-white" onClick={s.markAllRead}>Alles gelezen</button>
                </div>
                <div className="max-h-[420px] overflow-y-auto">
                  {s.notifications.length === 0 && <div className="p-4 text-sm text-slate-500">Geen nieuwe meldingen.</div>}
                  {s.notifications.slice(0, 40).map((n) => (
                    <button
                      key={n.id}
                      onClick={() => { useGame.setState((st) => { const x = st.notifications.find((y) => y.id === n.id); if (x) x.read = true; }); if (n.link) s.setPage(n.link); s.setNotifOpen(false); }}
                      className={`flex w-full gap-2 border-b border-hq-line/40 px-4 py-2.5 text-left text-sm hover:bg-white/5 ${n.read ? 'text-slate-400' : 'text-slate-100'}`}
                    >
                      {!n.read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-cyan-400" />}
                      <span className="flex-1">{n.text}</span>
                      <span className="shrink-0 text-[12px] text-slate-500">{relTime(n.tick, s.tick)}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
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
    <div className="flex items-center gap-2 rounded-xl border border-hq-line/60 bg-hq-panel/60 px-3 py-1.5" title="De game loopt gelijk met de echte tijd">
      <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
      <span className="text-[13px] font-semibold text-slate-200">{now.toLocaleString('nl-NL', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' })}</span>
      <span className="hidden text-[12px] uppercase tracking-wider text-slate-500 sm:inline">echte tijd</span>
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
  const [on, setOn] = useState(soundOn());
  const [vol, setVol] = useState(officeVolume());
  const [open, setOpen] = useState(false);
  const { theme, setTheme, focusMode, setFocusMode, quality, setQuality } = useWorld();
  useEffect(() => onSoundChange(setOn), []);
  useEffect(() => onOfficeVolume(setVol), []);
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
        {on ? <Volume2 size={18} /> : <VolumeX size={18} />}
      </button>
      <AnimatePresence>
        {open && (<>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <motion.div initial={{ opacity: 0, y: -6, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: 0.16 }}
            className="absolute right-0 top-12 z-50 w-[290px] space-y-3 rounded-2xl border border-white/10 bg-[#0b1130]/95 p-4 text-slate-200 shadow-2xl backdrop-blur">
            <div className="flex items-center justify-between">
              <span className="text-[13px] font-semibold">Geluidjes</span>
              <button onClick={() => setSound(!on)} className={`rounded-full px-3 py-1 text-[12px] font-bold ${on ? 'bg-emerald-500/20 text-emerald-300' : 'bg-white/10 text-slate-400'}`}>{on ? 'Aan' : 'Uit'}</button>
            </div>
            <label className="block">
              <div className="mb-1 flex justify-between text-[13px]"><span className="font-semibold">Kantoorgeluid</span><span className="text-slate-400">{Math.round(vol * 100)}%</span></div>
              <input type="range" min={0} max={1} step={0.05} value={vol} onChange={(e) => setOfficeVolume(parseFloat(e.target.value))} className="w-full accent-[#FF7A24]" aria-label="Volume van het kantoorgeluid" />
              <div className="text-[11px] text-slate-500">Geroezemoes en toetsenborden; harder als er meer agents werken.</div>
            </label>
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
