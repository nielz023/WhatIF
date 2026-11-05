import { useEffect, Component, type ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useGame } from './store/useGame';
import Sidebar, { MobileNav, StudioTabs, STUDIO } from './components/layout/Sidebar';
import Coach from './components/shared/Coach';
import Tour from './components/shared/Tour';
import TopBar from './components/layout/TopBar';
import BottomActions from './components/layout/BottomActions';
import { ConfirmDialog, Toasts } from './components/layout/Overlays';
import { AllModals } from './components/modals/Modals';
import AgentDrawer from './components/shared/AgentDrawer';
import ProjectDrawer from './components/shared/ProjectDrawer';
import DepartmentDrawer from './components/shared/DepartmentDrawer';
import HQPage from './pages/HQPage';
import ProjectsPage from './pages/ProjectsPage';
import AgentsPage from './pages/AgentsPage';
import ChannelsPage from './pages/ChannelsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ThreadsPage from './pages/ThreadsPage';
import FinancesPage from './pages/FinancesPage';
import UpgradesPage from './pages/UpgradesPage';
import AchievementsPage from './pages/AchievementsPage';
import SettingsPage from './pages/SettingsPage';
import WarRoomPage from './pages/WarRoomPage';
import DriftmarkPage, { VideosPage, MeerPage } from './pages/DriftmarkPage';
import KanaalPage from './pages/KanaalPage';
import CoachPage from './pages/CoachPage';
import type { PageId } from './types';
import { realTick } from './lib/util';
import { startLive } from './services/live';
import { startTools } from './services/tools';

const PAGES: Record<PageId, () => JSX.Element | null> = {
  driftmark: () => <DriftmarkPage />, videos: VideosPage, kanaal: KanaalPage, coach: CoachPage, meer: MeerPage, hq: HQPage, projects: ProjectsPage, agents: AgentsPage, channels: ChannelsPage, analytics: AnalyticsPage,
  threads: ThreadsPage, finances: FinancesPage, upgrades: UpgradesPage, achievements: AchievementsPage,
  settings: SettingsPage, warroom: WarRoomPage,
};

/** De klok loopt met de echte tijd mee: 1 tick = 1 echt uur. Na afwezigheid wordt bijgewerkt (max 30 dagen). */
function useSimulationLoop() {
  useEffect(() => {
    const sync = () => {
      const st = useGame.getState();
      // geen nepvoortgang meer: alleen de klok volgt de echte tijd, de rest komt uit de echte stand
      if (realTick() !== st.tick) useGame.setState({ tick: realTick() });
    };
    sync();
    startLive(); startTools();
    const id = setInterval(sync, 10000);
    return () => clearInterval(id);
  }, []);
}

/** Vangt een fout in één scherm op, zodat niet de hele HQ crasht. */
class PageBoundary extends Component<{ children: ReactNode }, { err: string | null }> {
  state = { err: null as string | null };
  static getDerivedStateFromError(e: unknown) { return { err: String((e as Error)?.message ?? e) }; }
  componentDidCatch(e: unknown) { console.error('[HQ] scherm-fout', e); }
  render() {
    if (!this.state.err) return this.props.children;
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="panel max-w-md p-6 text-center">
          <div className="text-3xl">🛠️</div>
          <div className="mt-2 font-display text-xl font-bold text-white">Dit scherm liep vast</div>
          <p className="mt-1 text-[14px] text-slate-300">De rest van de HQ werkt gewoon. Ga terug naar Home, of laat Claude weten welke knop je indrukte.</p>
          <p className="mt-2 break-words text-[12px] text-slate-500">{this.state.err}</p>
          <div className="mt-4 flex justify-center gap-2">
            <button className="btn-primary" onClick={() => useGame.getState().setPage('driftmark')}>Naar Home</button>
            <button className="btn-ghost" onClick={() => this.setState({ err: null })}>Opnieuw</button>
          </div>
        </div>
      </div>
    );
  }
}

export default function App() {
  useSimulationLoop();
  const page = useGame((s) => s.page);
  const Page = PAGES[page] ?? DriftmarkPage;

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.closest('input,textarea,select')) return;
            if (e.key === 'Escape') { const st = useGame.getState(); st.selectAgent(null); st.selectProject(null); st.selectDept(null); st.setNotifOpen(false); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="flex h-full w-full">
      <Sidebar />
      <div className="relative flex min-w-0 flex-1 flex-col">
        <TopBar />
        {STUDIO.some((x) => x.id === page) && <StudioTabs />}
        <main className="relative min-h-0 flex-1 pb-[64px] md:pb-0">
          <AnimatePresence mode="wait">
            <motion.div key={page} className="absolute inset-0" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
              <PageBoundary key={page}><Page /></PageBoundary>
            </motion.div>
          </AnimatePresence>
          {STUDIO.some((x) => x.id === page) && <BottomActions />}
        </main>
      </div>
      <MobileNav />
      <Coach />
      <Tour />
      <DepartmentDrawer />
      <ProjectDrawer />
      <AgentDrawer />
      <AllModals />
      <ConfirmDialog />
      <Toasts />
    </div>
  );
}
