import { useEffect, useRef, Component, type ReactNode } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useGame } from './store/useGame';
import { MobileNav, StudioTabs, STUDIO, MAIN } from './components/layout/Sidebar';
import GlassNav, { GlassSide } from './components/layout/GlassNav';
import WorldLayer from './world/WorldLayer';
import HomeHud from './world/HomeHud';
import { HoloPanel } from './world/HoloPanel';
import { useWorld } from './world/useWorld';
import { startSounds, play } from './world/sound';
import type { WorldMode } from './world/NeonOffice';
import Coach from './components/shared/Coach';
import Tour from './components/shared/Tour';
import TopBar from './components/layout/TopBar';
import BottomActions from './components/layout/BottomActions';
import { ConfirmDialog, Toasts } from './components/layout/Overlays';
import { AllModals } from './components/modals/Modals';
import AgentDrawer from './components/shared/AgentDrawer';
import GesprekDrawer from './components/shared/Gesprek';
import AfkeurenVenster from './components/shared/Afkeuren';
import { startThreads } from './services/threads';
import ProjectDrawer from './components/shared/ProjectDrawer';
import DepartmentDrawer from './components/shared/DepartmentDrawer';
import HQPage from './pages/HQPage';
import ProjectsPage from './pages/ProjectsPage';
import AgentsPage from './pages/AgentsPage';
import ChannelsPage from './pages/ChannelsPage';
import SettingsPage from './pages/SettingsPage';
import WarRoomPage from './pages/WarRoomPage';
import DriftmarkPage, { VideosPage, MeerPage } from './pages/DriftmarkPage';
import KanaalPage from './pages/KanaalPage';
import CoachPage from './pages/CoachPage';
import KennisPage from './pages/KennisPage';
import type { PageId } from './types';
import { realTick } from './lib/util';
import { startLive } from './services/live';
import { startMic } from './lib/mic';
import { startTools } from './services/tools';

/** Schermen die weg zijn (speelgeld, upgrades, spelcijfers, prestaties, berichten): een oude link gaat terug naar het kantoor. */
function NaarKantoor() {
  useEffect(() => { useGame.getState().setPage('hq'); }, []);
  return null;
}

const PAGES: Record<PageId, () => JSX.Element | null> = {
  driftmark: () => null, overzicht: () => <DriftmarkPage />, videos: VideosPage, kanaal: KanaalPage, coach: CoachPage, meer: MeerPage, hq: HQPage, projects: ProjectsPage, agents: AgentsPage, channels: ChannelsPage, analytics: NaarKantoor,
  threads: NaarKantoor, finances: NaarKantoor, upgrades: NaarKantoor, achievements: NaarKantoor,
  settings: SettingsPage, warroom: WarRoomPage,
  kennis: KennisPage,
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
    startLive(); startTools(); startSounds(); void startThreads(); startMic();
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

const TITLES: Partial<Record<PageId, { t: string; sub: string; c: string }>> = {
  overzicht: { t: 'Dagoverzicht', sub: 'Wat er nu gebeurt en wat op jou wacht', c: '#FF7A24' },
  videos: { t: "Video's", sub: 'Productie van idee tot upload, plus shorts', c: '#FF4DB8' },
  kanaal: { t: 'Kanaal', sub: 'Abonnees, weergaven, kijkduur en groei', c: '#FACC15' },
  coach: { t: 'Claude · CEO Coach', sub: 'Gesprek, briefing, doelen, beslissingen, agents en rapporten', c: '#FF7A24' },
  meer: { t: 'Meer', sub: 'Taken, cast & sets, werkwijze, gereedschap, ideeën, koppelingen', c: '#20D9FF' },
  settings: { t: 'Instellingen', sub: 'Koppelingen en opslag', c: '#94A3B8' },
};

export default function App() {
  useSimulationLoop();
  const page = useGame((s) => s.page);
  const setPage = useGame((s) => s.setPage);
  const bump = useWorld((s) => s.bump);
  const Page = PAGES[page] ?? DriftmarkPage;
  const studio = STUDIO.some((x) => x.id === page);
  const mode: WorldMode = page === 'driftmark' ? 'home' : page === 'hq' ? 'studio' : 'panel';
  const meta = TITLES[page] ?? (studio ? { t: `Studio · ${STUDIO.find((x) => x.id === page)?.label ?? ''}`, sub: 'Het kantoor beheren', c: '#398CFF' } : { t: MAIN.find((x) => x.id === page)?.label ?? '', sub: '', c: '#FF7A24' });

  const prevMode = useRef(mode);
  useEffect(() => { bump(); if (mode === 'panel') play('open'); else if (prevMode.current === 'panel') play('close'); prevMode.current = mode; }, [page, bump, mode]);
  const focus = useWorld((s) => s.focus); const worker = useWorld((s) => s.worker);
  useEffect(() => { if (focus || worker) play('zoom'); }, [focus, worker]);
  const walk = useWorld((s) => s.walk); // rondlopen: panelen, kaartjes en knoppen die het beeld bedekken gaan weg

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.closest('input,textarea,select')) return;
      if (e.key === 'Escape') {
        if (useWorld.getState().walk) return useWorld.getState().setWalk(false); // rondlopen: Esc stopt alleen het rondlopen
        const st = useGame.getState(); const w = useWorld.getState();
        if (st.selectedAgentId || st.selectedProjectId || st.selectedDept || st.notifOpen) { st.selectAgent(null); st.selectProject(null); st.selectDept(null); st.setNotifOpen(false); return; }
        if (w.worker) return w.openWorker(null);
        if (w.focus) return w.setFocus(null);
        if (st.page !== 'driftmark') st.setPage('driftmark');
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  return (
    <div className="relative h-full w-full overflow-hidden bg-[#050816]">
      <WorldLayer mode={mode} />
      <div className="pointer-events-none relative z-10 flex h-full w-full flex-col">
        <div className="pointer-events-auto"><TopBar /></div>
        {!walk && <GlassNav />}
        <main className="relative min-h-0 flex-1 pb-[64px] md:pb-0">
          {mode === 'home' && !walk && <GlassSide />}
          {mode === 'home' && <div hidden={walk}><HomeHud /></div>}
          {mode === 'studio' && (
            <div className="pointer-events-none absolute inset-0 flex flex-col">
              <div className="pointer-events-auto"><StudioTabs /></div>
              <div className="relative min-h-0 flex-1"><PageBoundary key={page}><Page /></PageBoundary></div>
            </div>
          )}
          <AnimatePresence mode="wait">
            {mode === 'panel' && (
              <motion.div key={page} className="absolute inset-0 flex justify-center px-2 pb-2 pt-1 md:px-10 md:pb-6 md:pt-2" exit={{ opacity: 0 }} transition={{ duration: 0.2 }}>
                <HoloPanel title={meta.t} sub={meta.sub} accent={meta.c} onClose={() => setPage(studio ? 'hq' : 'driftmark')} className="h-full w-full max-w-[1200px]" bare={!studio && page !== 'settings'}>
                  {studio && <StudioTabs />}
                  <div className="relative h-full min-h-[60vh]"><PageBoundary key={page}><Page /></PageBoundary></div>
                </HoloPanel>
              </motion.div>
            )}
          </AnimatePresence>
          {(mode === 'home' || studio) && !walk && <div className="pointer-events-auto"><BottomActions /></div>}
        </main>
      </div>
      <div className="relative z-20">{!walk && <MobileNav />}</div>
      <div className="relative z-30">
        <div hidden={walk}><Coach /></div>
        <Tour />
        <DepartmentDrawer />
        <ProjectDrawer />
        <AgentDrawer />
        <GesprekDrawer />
        <AfkeurenVenster />
        <AllModals />
        <ConfirmDialog />
        <Toasts />
      </div>
    </div>
  );
}
