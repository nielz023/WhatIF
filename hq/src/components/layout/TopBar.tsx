import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bell, Users, Wallet, Eye, Tv, HelpCircle, Volume2, VolumeX } from 'lucide-react';
import { soundOn, setSound, onSoundChange } from '../../world/sound';
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

function SoundBtn() {
  const [on, setOn] = useState(soundOn());
  useEffect(() => onSoundChange(setOn), []);
  return (
    <button onClick={() => setSound(!on)} className="glass-stat p-2 text-slate-300 hover:text-white" aria-label={on ? 'Geluid uit' : 'Geluid aan'} title={on ? 'Geluidjes uitzetten' : 'Geluidjes aanzetten'}>
      {on ? <Volume2 size={18} /> : <VolumeX size={18} />}
    </button>
  );
}
