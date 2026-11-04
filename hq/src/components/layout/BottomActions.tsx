import { Clapperboard, ClipboardList, UserPlus, Hammer, BarChart3, Trophy } from 'lucide-react';
import { useGame } from '../../store/useGame';

export default function BottomActions() {
  const openModal = useGame((s) => s.openModal);
  const setPage = useGame((s) => s.setPage);
  const items = [
    { label: 'Start New Video', icon: Clapperboard, onClick: () => openModal('newVideo'), primary: true },
    { label: 'Assign Task', icon: ClipboardList, onClick: () => openModal('assignTask') },
    { label: 'Hire Agent', icon: UserPlus, onClick: () => openModal('hireAgent') },
    { label: 'Upgrade Office', icon: Hammer, onClick: () => setPage('upgrades') },
    { label: 'Analytics', icon: BarChart3, onClick: () => setPage('analytics') },
    { label: 'Achievements', icon: Trophy, onClick: () => setPage('achievements') },
  ];
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-3 z-40 flex justify-center px-3">
      <div className="pointer-events-auto flex max-w-full gap-1.5 overflow-x-auto rounded-2xl border border-hq-line/70 bg-[#0a1029]/90 p-1.5 shadow-2xl backdrop-blur-xl">
        {items.map(({ label, icon: Icon, onClick, primary }) => (
          <button key={label} onClick={onClick} className={`${primary ? 'btn-primary' : 'btn-ghost'} shrink-0 whitespace-nowrap !px-3 !py-2 text-xs`}>
            <Icon size={15} />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
