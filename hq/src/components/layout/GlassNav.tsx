import { BarChart3, Clapperboard, LineChart, Sparkles, Layers, LayoutGrid, Home, LayoutDashboard } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { useLive } from '../../services/live';
import { mainOf } from './Sidebar';
import type { PageId } from '../../types';

/** De zwevende glazen hoofdnavigatie boven het kantoor. */
const ITEMS: { id: PageId; label: string; icon: typeof BarChart3; uitleg: string }[] = [
  { id: 'driftmark', label: 'Overzicht', icon: BarChart3, uitleg: 'Het 3D-kantoor: je hele bedrijf in één blik' },
  { id: 'videos', label: "Video's", icon: Clapperboard, uitleg: 'Elke video van idee tot upload, plus shorts' },
  { id: 'kanaal', label: 'Kanaal', icon: LineChart, uitleg: 'Abonnees, weergaven, kijkduur en cursusmeter' },
  { id: 'coach', label: 'Coach', icon: Sparkles, uitleg: 'Je CEO Coach: gesprek, briefing, doelen, beslissingen' },
  { id: 'hq', label: 'Studio', icon: Layers, uitleg: 'Het kantoor beheren: teamleden, projecten, spel' },
  { id: 'meer', label: 'Meer', icon: LayoutGrid, uitleg: 'Taken, werkwijze, cast, gereedschap, koppelingen' },
];

export default function GlassNav() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  const waiting = useLive((s) => s.data.activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready').length);
  const cur = mainOf(page);
  return (
    <nav className="pointer-events-auto relative z-40 hidden justify-center px-4 pb-1 pt-2 md:flex" aria-label="Hoofdnavigatie">
      <div className="flex gap-2 lg:gap-3" style={{ perspective: 900 }}>
        {ITEMS.map(({ id, label, icon: Icon, uitleg }, i) => {
          const active = cur === id;
          return (
            <button key={id} onClick={() => setPage(id)} title={uitleg} data-active={active} className="glass-btn group" style={{ ['--ry' as string]: `${(i - 2.5) * -5}deg` }} aria-current={active ? 'page' : undefined}>
              <Icon size={26} className="glass-btn-ico" />
              <span>{label}</span>
              {id === 'driftmark' && waiting > 0 && <span className="absolute -right-1.5 -top-1.5 min-w-[20px] rounded-full bg-[#FF7A24] px-1 text-center text-[11px] font-bold text-white shadow-[0_0_10px_#FF7A24]">{waiting}</span>}
            </button>
          );
        })}
      </div>
    </nav>
  );
}

const SIDE: { id: PageId; label: string; icon: typeof Home }[] = [
  { id: 'driftmark', label: 'HQ', icon: Home },
  { id: 'overzicht', label: 'Dagoverzicht', icon: LayoutDashboard },
  { id: 'videos', label: "Video's", icon: Clapperboard },
  { id: 'kanaal', label: 'Kanaal', icon: LineChart },
  { id: 'coach', label: 'Coach', icon: Sparkles },
  { id: 'hq', label: 'Studio', icon: Layers },
  { id: 'meer', label: 'Meer', icon: LayoutGrid },
];

/** Zwevende glazen zijbalk links (zoals op het referentiebeeld), alleen op grote schermen. */
export function GlassSide() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  return (
    <aside className="glass-side pointer-events-auto absolute left-4 top-2 z-30 hidden w-[190px] p-2.5 xl:block" aria-label="Zijbalk">
      {SIDE.map(({ id, label, icon: Icon }) => {
        const active = page === id || (id === 'hq' && mainOf(page) === 'hq');
        return (
          <button key={id} onClick={() => setPage(id)} data-active={active} className="glass-side-btn">
            <Icon size={20} /><span>{label}</span>
          </button>
        );
      })}
    </aside>
  );
}
