import { useGame } from '../store/useGame';
import { useWorld } from './useWorld';
import type { RoomDef, RoomId } from './rooms';
import type { WorldMode } from './NeonOffice';

/**
 * Wat een klik op een afdeling in het kantoor doet. Home: de camera vliegt erheen en het afdelingspaneel
 * gaat open. Studio: het spel van die afdeling. Een paneel (andere pagina): eerst terug naar Home.
 * Rondlopen gebruikt dezelfde handeling voor "Openen", zodat het menu precies zo opengaat als na een klik.
 */
export function selectRoom(r: RoomDef, mode: WorldMode) {
  const g = useGame.getState();
  if (mode === 'studio') { if (r.game) g.selectDept(r.game as never); else g.setPage(r.page ?? 'coach'); return; }
  if (mode === 'panel') g.setPage('driftmark');
  useWorld.getState().setFocus(r.id as RoomId);
}
