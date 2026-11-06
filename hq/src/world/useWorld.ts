import { create } from 'zustand';
import type { RoomId } from './rooms';

export type Quality = 'auto' | '4k' | 'snel';
export type Theme = 'auto' | 'nacht' | 'dag' | 'feest';

interface W {
  focus: RoomId | null; // afdeling waar de camera naartoe vliegt (Home)
  worker: RoomId | null; // geopend profielpaneel van een medewerker
  hover: RoomId | null;
  introKey: number; // telt op bij elke paginawissel, voor de kleine camerabeweging
  setFocus: (r: RoomId | null, at?: { x: number; y: number }) => void;
  openWorker: (r: RoomId | null) => void;
  setHover: (r: RoomId | null) => void;
  bump: () => void;
  quality: Quality;
  setQuality: (q: Quality) => void;
  /** feestje: telt op bij elke mijlpaal (confetti, applaus, juichende medewerkers) */
  party: number; partyText: string | null; celebrate: (text: string) => void;
  /** thema van het kantoor: automatisch volgens de klok, of vast */
  theme: Theme; setTheme: (t: Theme) => void;
  /** focusmodus: kantoor gedimd, alleen je taken */
  focusMode: boolean; setFocusMode: (v: boolean) => void;
  /** plek op het scherm waar de laatste afdeling is aangeklikt (paneel schuift daarvandaan in) */
  clickAt: { x: number; y: number } | null;
  /** drone-intro bij openen loopt */
  intro: boolean; setIntro: (v: boolean) => void;
  /** rondlopen in eerste persoon (Walk.tsx); bij het starten gaan open afdelingspanelen dicht */
  walk: boolean; setWalk: (v: boolean) => void;
}
const read = (k: string) => { try { return localStorage.getItem(k); } catch { return null; } };
const write = (k: string, v: string) => { try { localStorage.setItem(k, v); } catch { /* */ } };
/** telefoon of klein scherm: lichtere versie van het kantoor */
export const isPhone = () => typeof window !== 'undefined' && (Math.min(window.innerWidth, window.innerHeight) < 700 || !!window.matchMedia?.('(pointer: coarse)').matches);
const q0 = (() => { const v = read('dm-kwaliteit'); return (v === '4k' || v === 'snel' || v === 'auto' ? v : isPhone() ? 'snel' : 'auto') as Quality; })();
const t0 = (() => { const v = read('dm-thema'); return (v === 'nacht' || v === 'dag' || v === 'feest' ? v : 'auto') as Theme; })();

export const useWorld = create<W>((set) => ({
  focus: null, worker: null, hover: null, introKey: 0,
  setFocus: (focus, at) => set((s) => ({ focus, worker: null, clickAt: at ?? (focus ? s.clickAt : null) })),
  openWorker: (worker) => set((s) => ({ worker, focus: worker ?? s.focus })),
  setHover: (hover) => set({ hover }),
  bump: () => set((s) => ({ introKey: s.introKey + 1 })),
  quality: q0,
  setQuality: (quality) => { write('dm-kwaliteit', quality); set({ quality }); },
  party: 0, partyText: null,
  celebrate: (partyText) => set((s) => ({ party: s.party + 1, partyText })),
  theme: t0, setTheme: (theme) => { write('dm-thema', theme); set({ theme }); },
  focusMode: read('dm-focus') === 'aan', setFocusMode: (focusMode) => { write('dm-focus', focusMode ? 'aan' : 'uit'); set({ focusMode }); },
  clickAt: null,
  intro: false, setIntro: (intro) => set({ intro }),
  walk: false, setWalk: (walk) => set((s) => (walk === s.walk ? {} : walk ? { walk, focus: null, worker: null, hover: null } : { walk })),
}));
/** pixeldichtheid van het 3D-kantoor per kwaliteitsstand */
export function dprFor(q: Quality, auto: number) {
  const dev = typeof window !== 'undefined' ? window.devicePixelRatio || 1 : 1;
  // haarscherp (niels 2026-11-06): nooit onder de resolutie van het scherm zelf; op een gewoon scherm een tikje erboven
  if (q === 'snel') return Math.min(1.5, Math.max(1, dev));
  if (q === '4k') return Math.min(3, Math.max(dev, 3840 / Math.max(1, window.innerWidth)));
  return Math.min(2, Math.max(auto, dev, 1));
}

export const reducedMotion = () => typeof window !== 'undefined' && !!window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

export function hasWebGL(): boolean {
  try {
    const c = document.createElement('canvas');
    return !!(c.getContext('webgl2') || c.getContext('webgl'));
  } catch { return false; }
}

/** Tijd van de dag voor licht en lucht: 0 = middernacht, 0.5 = middag. Thema kan het vastzetten. */
export function dayPhase(theme: Theme, d = new Date()): number {
  if (theme === 'nacht' || theme === 'feest') return 0.02;
  if (theme === 'dag') return 0.5;
  return (d.getHours() + d.getMinutes() / 60) / 24;
}

const smooth = (a: number, b: number, x: number) => { const t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
/** hoeveel daglicht er is (0 = nacht, 1 = dag) bij een dagfase; zon op rond 8 uur, onder rond 17 uur (november) */
export function dayAmount(ph: number): number {
  const h = ph * 24; return Math.max(0, Math.min(smooth(7.4, 8.8, h), 1 - smooth(16.6, 18.1, h)));
}

// alleen bij lokaal testen: de wereldstand bereikbaar maken voor testscripts
if (typeof window !== 'undefined' && window.location?.hostname === 'localhost') (window as unknown as { __dmWorld: typeof useWorld }).__dmWorld = useWorld;
