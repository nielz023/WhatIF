import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bell, Pause, Play, FastForward, Users, Wallet, Eye, Tv, Star } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { companyXpForLevel } from '../../modules/gameplay/progression';
import { compact, eur, fmtTick, relTime } from '../../lib/util';
import { DemoBadge } from '../ui';
import { useLive } from '../../services/live';

export default function TopBar() {
  const s = useGame();
  const live = useLive((x) => x.data);
  const xpNeed = companyXpForLevel(s.company.level);
  const views = s.channels.reduce((a, c) => a + c.views, 0);
  const unread = s.notifications.filter((n) => !n.read).length;

  const Stat = ({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: React.ReactNode; color: string }) => (
    <div className="hidden items-center gap-2 rounded-xl border border-hq-line/60 bg-hq-panel/60 px-3 py-1.5 md:flex">
      <span style={{ color }}>{icon}</span>
      <div className="leading-tight">
        <div className="text-[9px] font-semibold uppercase tracking-wider text-slate-500">{label}</div>
        <div className="text-sm font-bold text-white">{value}</div>
      </div>
    </div>
  );

  return (
    <header className="relative z-50 flex h-[64px] shrink-0 items-center gap-2 border-b border-hq-line/60 bg-[#080d22]/80 px-3 backdrop-blur-xl">
      {/* level & XP */}
      <button onClick={() => s.setPage('achievements')} className="flex items-center gap-2.5 rounded-xl border border-indigo-500/30 bg-indigo-500/10 px-3 py-1.5 transition hover:bg-indigo-500/20">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-fuchsia-500 font-display text-sm font-bold text-white shadow-neon">{s.company.level}</div>
        <div className="w-24 leading-tight">
          <div className="flex items-center justify-between text-[10px] text-slate-400"><span className="flex items-center gap-1"><Star size={10} />XP</span><span>{Math.round(s.company.xp)}/{xpNeed}</span></div>
          <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-slate-800"><div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-fuchsia-500" style={{ width: `${(s.company.xp / xpNeed) * 100}%` }} /></div>
        </div>
      </button>
      <Stat icon={<Users size={16} />} label="Threads aan het werk" value={`${s.agents.filter((a) => a.state === 'working').length}/${s.agents.length}`} color="#22d3ee" />
      <Stat icon={<Tv size={16} />} label="Abonnees" value={live.youtube?.subscribers ?? '—'} color="#fb923c" />
      <Stat icon={<Eye size={16} />} label={live.youtube?.views != null ? 'Weergaven totaal' : 'Weergaven 28 d'} value={live.youtube?.views != null ? compact(live.youtube.views) : (live.channel.stats[0]?.value ?? '—')} color="#a855f7" />
      <Stat icon={<Wallet size={16} />} label="Video's online" value={live.videos.filter((v) => v.status === 'Online').length} color="#22c55e" />
      {s.demoMode && <span className="hidden xl:inline"><DemoBadge /></span>}

      <div className="ml-auto flex items-center gap-2">
        {/* echte klok */}
        <RealClock />

        {/* notifications */}
        <div className="relative">
          <button onClick={() => s.setNotifOpen(!s.notifOpen)} className="relative rounded-xl border border-hq-line/60 bg-hq-panel/60 p-2 text-slate-300 hover:text-white" aria-label="Notifications">
            <Bell size={18} />
            {unread > 0 && <span className="absolute -right-1 -top-1 min-w-[18px] rounded-full bg-rose-500 px-1 text-center text-[10px] font-bold text-white shadow-[0_0_10px_#f43f5e]">{unread > 99 ? '99+' : unread}</span>}
          </button>
          <AnimatePresence>
            {s.notifOpen && (
              <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} className="panel absolute right-0 top-12 w-[360px] max-w-[90vw] overflow-hidden border-indigo-500/30">
                <div className="flex items-center justify-between border-b border-hq-line/70 px-4 py-2.5">
                  <span className="font-semibold text-white">Notifications</span>
                  <button className="text-xs text-indigo-300 hover:text-white" onClick={s.markAllRead}>Mark all read</button>
                </div>
                <div className="max-h-[420px] overflow-y-auto">
                  {s.notifications.length === 0 && <div className="p-4 text-sm text-slate-500">All caught up.</div>}
                  {s.notifications.slice(0, 40).map((n) => (
                    <button
                      key={n.id}
                      onClick={() => { useGame.setState((st) => { const x = st.notifications.find((y) => y.id === n.id); if (x) x.read = true; }); if (n.link) s.setPage(n.link); s.setNotifOpen(false); }}
                      className={`flex w-full gap-2 border-b border-hq-line/40 px-4 py-2.5 text-left text-sm hover:bg-white/5 ${n.read ? 'text-slate-400' : 'text-slate-100'}`}
                    >
                      {!n.read && <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-cyan-400" />}
                      <span className="flex-1">{n.text}</span>
                      <span className="shrink-0 text-[10px] text-slate-500">{relTime(n.tick, s.tick)}</span>
                    </button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
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
      <span className="text-xs font-semibold text-slate-200">{now.toLocaleString('nl-NL', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Amsterdam' })}</span>
      <span className="hidden text-[10px] uppercase tracking-wider text-slate-500 sm:inline">echte tijd</span>
    </div>
  );
}
