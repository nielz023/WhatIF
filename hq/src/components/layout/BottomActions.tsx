import { Clapperboard, ClipboardList, BarChart3, Trophy } from 'lucide-react';
import { useGame } from '../../store/useGame';

/** Snelle knoppen onderin. Aannemen en kantoor upgraden zijn weg: dat hoorde bij het spel met speelgeld. */
export default function BottomActions() {
  const openModal = useGame((s) => s.openModal);
  const setPage = useGame((s) => s.setPage);
  const items = [
    { label: 'Nieuwe video', icon: Clapperboard, onClick: () => openModal('newVideo'), primary: true },
    { label: 'Taak geven', icon: ClipboardList, onClick: () => openModal('assignTask') },
    { label: 'Statistieken', icon: BarChart3, onClick: () => setPage('kanaal') },
    { label: 'Prestaties', icon: Trophy, onClick: () => setPage('achievements') },
  ];
  return (
    <div className="pointer-events-none absolute inset-x-0 bottom-3 z-40 flex justify-center px-3">
      <div className="glass-bar pointer-events-auto flex max-w-full gap-2 overflow-x-auto p-2">
        {items.map(({ label, icon: Icon, onClick, primary }) => (
          <button key={label} onClick={onClick} className={`${primary ? 'btn-primary' : 'glass-bar-btn'} shrink-0 whitespace-nowrap !px-4 !py-2.5 text-[14px]`}>
            <Icon size={15} />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
