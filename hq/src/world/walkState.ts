/**
 * Gedeelde stand van RONDLOPEN tussen de camera (Walk.tsx, in het 3D-kantoor) en de schermlaag
 * (WalkHud.tsx: knop, vizier, hint, vraag bij een afdeling, joystick). Geen three.js hier, zodat de
 * knop in de bovenbalk het 3D-deel niet meetrekt.
 */
import { create } from 'zustand';
import type { RoomId } from './rooms';

interface WalkUi {
  /** het 3D-kantoor staat er: de knop Rondlopen mag zichtbaar zijn */
  ready: boolean;
  /** afdeling waar je nu staat (gangen tellen niet) */
  room: RoomId | null;
  /** vraag "menu openen?" voor deze afdeling; weg na Nee of als je de afdeling uit loopt */
  ask: RoomId | null;
  /** de muis is vastgezet (pointer lock) */
  locked: boolean;
  /** pointer lock geweigerd (bv. in de claude.ai-iframe): rondkijken met ingedrukte muisknop */
  noLock: boolean;
  /** bediening met aanraken: joystick linksonder en vegen om rond te kijken */
  touch: boolean;
  /** de camera meldt in welke afdeling je staat; een nieuwe afdeling stelt de vraag opnieuw */
  enter: (room: RoomId | null) => void;
  /** "Nee": niet meer vragen tot je de afdeling uit bent gelopen */
  dismiss: () => void;
}

export const useWalk = create<WalkUi>((set) => ({
  ready: false, room: null, ask: null, locked: false, noLock: false, touch: false,
  enter: (room) => set((s) => (room === s.room ? {} : { room, ask: room })),
  dismiss: () => set({ ask: null }),
}));

/** Joystick van de schermlaag voor de camera (-1..1, jy = vooruit), zonder React-renders per beweging. */
export const walkInput = { jx: 0, jy: 0 };
