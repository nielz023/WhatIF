import { create } from 'zustand';
import type { RoomId } from './rooms';

interface W {
  focus: RoomId | null; // afdeling waar de camera naartoe vliegt (Home)
  worker: RoomId | null; // geopend profielpaneel van een medewerker
  hover: RoomId | null;
  introKey: number; // telt op bij elke paginawissel, voor de kleine camerabeweging
  setFocus: (r: RoomId | null) => void;
  openWorker: (r: RoomId | null) => void;
  setHover: (r: RoomId | null) => void;
  bump: () => void;
}

export const useWorld = create<W>((set) => ({
  focus: null, worker: null, hover: null, introKey: 0,
  setFocus: (focus) => set({ focus, worker: null }),
  openWorker: (worker) => set((s) => ({ worker, focus: worker ?? s.focus })),
  setHover: (hover) => set({ hover }),
  bump: () => set((s) => ({ introKey: s.introKey + 1 })),
}));

export const reducedMotion = () => typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

export function hasWebGL(): boolean {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch { return false; }
}
