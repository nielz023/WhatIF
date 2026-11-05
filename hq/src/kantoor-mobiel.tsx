/**
 * Het 3D-kantoor los, voor Driftmark HQ Mobiel (hq/mobiel). De telefoonpagina laadt dit
 * bestand pas als je het tabblad Kantoor opent: mount(el, onAgent).
 * Medewerkers = echte threads uit driftmark-hq/status.json (via services/live + sync).
 */
import { lazy, StrictMode, Suspense } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import './kantoor.css';
import { useGame } from './store/useGame';
import { startLive } from './services/live';
import { realTick } from './lib/util';
import { startDutch } from './lib/nl';

const OfficeScene = lazy(() => import('./components/office/OfficeScene'));

export interface AgentInfo { id: string; name: string; doing: string; state: string; department: string }
let root: Root | null = null;
let started = false;

/** Zet het kantoor in el. Roep unmount() aan als het tabblad dicht gaat, dan rendert de telefoon niets op de achtergrond. */
export function mount(el: HTMLElement, onAgent?: (a: AgentInfo | null) => void) {
  if (root) return;
  if (!started) {
    started = true;
    useGame.setState({ tick: realTick() });
    startLive();
    setInterval(() => { if (realTick() !== useGame.getState().tick) useGame.setState({ tick: realTick() }); }, 10000);
    useGame.subscribe((s, prev) => {
    if (s.selectedAgentId === prev.selectedAgentId && s.agents === prev.agents) return;
    const a = s.agents.find((x) => x.id === s.selectedAgentId);
      onAgent?.(a ? { id: a.id, name: a.name, doing: a.personality, state: a.state, department: a.department } : null);
    });
    startDutch(el);
  }
  root = createRoot(el);
  root.render(
    <StrictMode>
      <Suspense fallback={<div style={{ display: 'grid', placeItems: 'center', height: '100%', color: '#8f9bcb', font: '14px system-ui' }}>Kantoor laden…</div>}>
        <OfficeScene />
      </Suspense>
    </StrictMode>,
  );
}
export function unmount() { root?.unmount(); root = null; }
export function deselect() { useGame.getState().selectAgent(null); }
