import { Star, Building2, FolderKanban, Users, Tv, BarChart3, MessagesSquare, Wallet, Wrench, Trophy, Settings, ShieldAlert } from 'lucide-react';
import type { PageId } from '../../types';
import { useGame } from '../../store/useGame';
import { rankTitle } from '../../modules/gameplay/progression';

export const NAV: { id: PageId; label: string; icon: typeof Building2 }[] = [
  { id: 'driftmark', label: 'Driftmark HQ', icon: Star },
  { id: 'hq', label: '3D-kantoor (game)', icon: Building2 },
  { id: 'projects', label: 'Projects', icon: FolderKanban },
  { id: 'agents', label: 'Agents', icon: Users },
  { id: 'channels', label: 'Channels', icon: Tv },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'threads', label: 'Threads', icon: MessagesSquare },
  { id: 'finances', label: 'Finances', icon: Wallet },
  { id: 'warroom', label: 'War Room', icon: ShieldAlert },
  { id: 'upgrades', label: 'Upgrades', icon: Wrench },
  { id: 'achievements', label: 'Achievements', icon: Trophy },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  const level = useGame((s) => s.company.level);
  const approvals = useGame((s) => s.projects.filter((p) => p.status === 'Awaiting Approval' || p.status === 'Awaiting Publish').length);
  const warReady = useGame((s) => s.warCases.filter((w) => w.status === 'Ready').length);
  const unreadPosts = useGame((s) => s.posts.filter((p) => s.tick - p.tick < 6).length);

  const badge = (id: PageId) => (id === 'projects' ? approvals : id === 'warroom' ? warReady : id === 'threads' ? unreadPosts : 0);

  return (
    <aside className="z-40 flex h-full w-[68px] shrink-0 flex-col border-r border-hq-line/60 bg-[#080d22]/90 backdrop-blur-xl lg:w-[220px]">
      <div className="flex items-center gap-2.5 px-3 py-4 lg:px-4">
        <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-rose-500 via-fuchsia-500 to-indigo-500 shadow-[0_0_20px_rgba(217,70,239,.5)]">
          <svg viewBox="0 0 24 24" className="h-5 w-5 fill-white"><path d="M8 5.5v13l11-6.5z" /></svg>
        </div>
        <div className="hidden leading-tight lg:block">
          <div className="font-display text-[13px] font-bold tracking-wide text-white">DRIFTMARK</div>
          <div className="text-gradient font-display text-[13px] font-bold tracking-wide">YOUTUBE HQ</div>
        </div>
      </div>
      <nav className="flex-1 space-y-0.5 overflow-y-auto px-2">
        {NAV.map(({ id, label, icon: Icon }) => {
          const active = page === id;
          const b = badge(id);
          return (
            <button
              key={id}
              onClick={() => setPage(id)}
              title={label}
              className={`group relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition ${active ? 'bg-gradient-to-r from-indigo-500/25 to-fuchsia-500/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
            >
              {active && <span className="absolute left-0 top-2 h-[calc(100%-16px)] w-[3px] rounded-r bg-gradient-to-b from-cyan-400 to-fuchsia-500 shadow-[0_0_10px_#a855f7]" />}
              <Icon size={18} className={id === 'warroom' ? 'text-rose-400' : active ? 'text-cyan-300' : ''} />
              <span className="hidden lg:inline">{label}</span>
              {b > 0 && <span className="absolute right-2 top-1.5 min-w-[18px] rounded-full bg-rose-500 px-1 text-center text-[10px] font-bold text-white lg:static lg:ml-auto">{b}</span>}
            </button>
          );
        })}
      </nav>
      <div className="m-2 hidden rounded-xl border border-hq-line/70 bg-hq-panel/70 p-3 lg:block">
        <div className="text-[10px] uppercase tracking-wider text-slate-500">Company rank</div>
        <div className="font-display text-sm font-semibold text-white">{rankTitle(level)}</div>
        <div className="mt-1 text-[11px] text-slate-400">Driftmark HQ is echt · de game is een simulatie</div>
      </div>
    </aside>
  );
}
