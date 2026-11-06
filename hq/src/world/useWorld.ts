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
  quality: Quality;
  setQuality: (q: Quality) => void;
}
export type Quality = 'auto' | '4k' | 'snel';
const q0 = (() => { try { const v = localStorage.getItem('dm-kwaliteit'); return (v === '4k' || v === 'snel' ? v : 'auto') as Quality; } catch { return 'auto' as Quality; } })();

export const useWorld = create<W>((set) => ({
  focus: null, worker: null, hover: null, introKey: 0,
  setFocus: (focus) => set({ focus, worker: null }),
  openWorker: (worker) => set((s) => ({ worker, focus: worker ?? s.focus })),
  setHover: (hover) => set({ hover }),
  bump: () => set((s) => ({ introKey: s.introKey + 1 })),
  quality: q0,
  setQuality: (quality) => { try { localStorage.setItem('dm-kwaliteit', quality); } catch { /* */ } set({ quality }); },
}));
/** pixeldichtheid van het 3D-kantoor per kwaliteitsstand */
export function dprFor(q: Quality, auto: number) {
  const dev = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1;
  if (q === 'snel') return 1;
  if (q === '4k') return Math.min(3, Math.max(dev, 3840 / Math.max(1, window.innerWidth)));
  return Math.min(auto, Math.max(1, dev));
}

export const reducedMotion = () => typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

export function hasWebGL(): boolean {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch { return false; }
}
