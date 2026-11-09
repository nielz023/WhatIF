import { Home, Clapperboard, LineChart, Building2, FolderKanban, Users, ShieldAlert, Library } from 'lucide-react';
import type { PageId } from '../../types';
import { useGame } from '../../store/useGame';
import { useLive } from '../../services/live';

/** De vijf vaste knoppen (verbeterlijst 9 nov, punten 16-18). De Coach zit rechtsonder op elke pagina; Meer is opgegaan in Vandaag, Video's en Kennis. */
export const MAIN: { id: PageId; label: string; icon: typeof Home; uitleg: string }[] = [
  { id: 'overzicht', label: 'Vandaag', icon: Home, uitleg: 'Wat op jou wacht, wat nu loopt en wat net klaar is' },
  { id: 'videos', label: "Video's", icon: Clapperboard, uitleg: 'Elke video van idee tot upload, plus shorts, cast en ideeën' },
  { id: 'kanaal', label: 'Kanaal', icon: LineChart, uitleg: 'Abonnees, weergaven, kijkduur en groei' },
  { id: 'kennis', label: 'Kennis', icon: Library, uitleg: 'Geheugen, threads, documenten, werkwijze en gereedschap' },
  { id: 'driftmark', label: '3D-kantoor', icon: Building2, uitleg: 'Je 3D-kantoor: loop rond en zie wie waaraan werkt' },
];
/** Binnen het 3D-kantoor: team, projecten en crisiskamer. Het demokanaal-scherm is weg (punt 38). */
export const STUDIO: { id: PageId; label: string; icon: typeof Home }[] = [
  { id: 'hq', label: 'Team', icon: Building2 },
  { id: 'projects', label: 'Projecten', icon: FolderKanban },
  { id: 'agents', label: 'Teamleden', icon: Users },
  { id: 'warroom', label: 'Crisiskamer', icon: ShieldAlert },
];
/** oude naam, nog gebruikt door andere schermen */
export const NAV = [...MAIN, ...STUDIO.slice(1)];

export const mainOf = (p: PageId): PageId => (STUDIO.some((s) => s.id === p) || p === 'channels' ? 'driftmark' : p === 'settings' || p === 'meer' || p === 'coach' ? 'overzicht' : p);

function useWaiting() {
  return useLive((s) => s.data.activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready').length);
}

export default function Sidebar() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  const cur = mainOf(page);
  const waiting = useWaiting();
  return (
    <aside className="z-40 hidden h-full w-[76px] shrink-0 flex-col border-r border-hq-line bg-[#080d22]/95 backdrop-blur-xl md:flex lg:w-[220px]">
      <div className="flex items-center gap-2.5 px-3 py-4 lg:px-4">
        <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-orange-400 via-orange-500 to-sky-500 shadow-[0_0_20px_rgba(255,138,61,.45)]">
          <svg viewBox="0 0 24 24" className="h-5 w-5 fill-white"><path d="M8 5.5v13l11-6.5z" /></svg>
        </div>
        <div className="hidden leading-tight lg:block">
          <div className="font-display text-[15px] font-bold tracking-wide text-white">DRIFTMARK</div>
          <div className="text-gradient font-display text-[13px] font-bold tracking-wide">HQ</div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 px-2">
        {MAIN.map(({ id, label, icon: Icon, uitleg }, i) => {
          const active = cur === id;
          const b = id === 'overzicht' ? waiting : 0;
          return (
            <div key={id}>
              {i === 4 && <div className="mx-3 my-2 border-t border-hq-line" />}
              <button onClick={() => setPage(id)} title={uitleg}
                className={`group relative flex w-full items-center gap-3 rounded-xl px-3 py-3 text-[15px] font-semibold transition ${active ? 'bg-orange-500/15 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
                {active && <span className="absolute left-0 top-2.5 h-[calc(100%-20px)] w-[3px] rounded-r bg-orange-400 shadow-[0_0_10px_#ff8a3d]" />}
                <Icon size={20} className={active ? 'text-orange-300' : ''} />
                <span className="hidden lg:inline">{label}</span>
                {b > 0 && <span className="absolute right-2 top-1.5 min-w-[20px] rounded-full bg-orange-500 px-1 text-center text-[12px] font-bold text-white lg:static lg:ml-auto">{b}</span>}
              </button>
            </div>
          );
        })}
      </nav>
      <div className="hidden px-4 pb-4 text-[12px] leading-snug text-slate-500 lg:block">Alles toont je echte cijfers en taken. De Coach staat rechtsonder op elke pagina.</div>
    </aside>
  );
}

/** Telefoon: vaste balk onderin met dezelfde 5 knoppen. */
export function MobileNav() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  const cur = mainOf(page);
  const waiting = useWaiting();
  return (
    <nav className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t border-hq-line bg-[#080d22]/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl md:hidden">
      {MAIN.map(({ id, label, icon: Icon }) => {
        const active = cur === id;
        return (
          <button key={id} onClick={() => setPage(id)} className={`relative flex flex-col items-center gap-0.5 py-2.5 text-[12px] font-semibold ${active ? 'text-orange-300' : 'text-slate-400'}`}>
            <Icon size={22} />{label}
            {id === 'overzicht' && waiting > 0 && <span className="absolute right-[22%] top-1.5 h-2.5 w-2.5 rounded-full bg-orange-500" />}
          </button>
        );
      })}
    </nav>
  );
}

/** Bovenaan elk Studio-scherm: wat Studio is, plus de onderdelen. */
export function StudioTabs() {
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  return (
    <div className="shrink-0 border-b border-hq-line bg-[#080d22]/80 px-3 pt-2 backdrop-blur md:px-6">
      <div className="mb-1.5 text-[12px] text-slate-400"><span className="font-semibold text-sky-300">🏢 Team en projecten</span> in je 3D-kantoor, met je echte video's en taken. Knoppen als "Nieuwe video" en "Goedkeuren" worden echte opdrachten voor Claude.</div>
      <div className="flex gap-1 overflow-x-auto pb-2">
        {STUDIO.map(({ id, label, icon: Icon }) => (
          <button key={id} onClick={() => setPage(id)} className={`flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-[13px] font-semibold transition ${page === id ? 'bg-sky-500/20 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>
            <Icon size={14} />{label}
          </button>
        ))}
      </div>
    </div>
  );
}
