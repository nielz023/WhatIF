/**
 * ZELF GAMEN in de game room (niels 2026-11-09: "de game room geupgrade ... iets groter en je kan zelf ook gamen in de
 * rondloopmodus"). Gedeelde stand tussen het 3D-kantoor (Upstairs.tsx zoekt welke machine er vlak voor je staat) en de
 * schermlaag (GamePanel.tsx: het spel zelf). Alle spellen zijn eigen, verzonnen spellen (games.ts).
 * Highscores blijven in de browser (localStorage), per spel.
 */
import { create } from 'zustand';
import { G } from './upstairs';
import { walkLock } from './walkState';

export type GameId = 'break' | 'hop' | 'orbit' | 'dash' | 'comet' | 'snail' | 'gp' | 'hockey' | 'claw';

/** de machines in de game room: midden (bovenverdieping, x/z), maat (w langs x, d langs z) en hoe dichtbij je bij de
 *  rand moet staan om te kunnen spelen */
export interface Machine { id: GameId; naam: string; kleur: string; c: [number, number]; w: number; d: number; reach: number }

/** de zes gamekasten langs de achterwand (zelfde volgorde als ARCADE in Upstairs.tsx) */
export const KASTEN: { id: GameId; naam: string; a: string; b: string }[] = [
  { id: 'break', naam: 'NEON BREAK', a: '#20D9FF', b: '#FF4DB8' },
  { id: 'hop', naam: 'SKY HOP', a: '#4ADE80', b: '#FACC15' },
  { id: 'orbit', naam: 'ORBIT RUN', a: '#A855F7', b: '#FF7A24' },
  { id: 'dash', naam: 'DRIFT DASH', a: '#FF3B4E', b: '#20D9FF' },
  { id: 'comet', naam: 'COMET CATCH', a: '#FACC15', b: '#398CFF' },
  { id: 'snail', naam: 'SNAIL RUN', a: '#FF7A24', b: '#4ADE80' },
];

export const MACHINES: Machine[] = [
  ...KASTEN.map((k, i) => ({ id: k.id, naam: k.naam, kleur: k.a, c: [G.arcadeX, G.arcadeZ[i]] as [number, number], w: 0.78, d: 0.74, reach: 1.15 })),
  ...G.raceX.map((x) => ({ id: 'gp' as GameId, naam: 'DRIFT GP', kleur: '#FF7A24', c: [x, G.raceZ] as [number, number], w: 0.82, d: 1.95, reach: 1.2 })),
  { id: 'hockey', naam: 'AIRHOCKEY', kleur: '#20D9FF', c: G.hockey.c, w: G.hockey.w, d: G.hockey.d, reach: 1.2 },
  { id: 'claw', naam: 'GRIJPMACHINE', kleur: '#FF4DB8', c: G.claw.c, w: G.claw.w, d: G.claw.d, reach: 1.1 },
];

/** d = afstand tot de rand van de machine */
export interface PlayNear { id: GameId; naam: string; kleur: string; d: number }

interface PlayState {
  /** de machine vlak voor je (rondlopen, bovenverdieping) */
  near: PlayNear | null;
  /** het spel dat nu open staat */
  open: GameId | null;
  /** beste scores (deze browser) */
  best: Partial<Record<GameId, number>>;
  setNear: (n: PlayNear | null) => void;
}

const leesBest = (): Partial<Record<GameId, number>> => { try { return JSON.parse(localStorage.getItem('dm-highscores') || '{}'); } catch { return {}; } };

export const usePlay = create<PlayState>((set) => ({
  near: null, open: null, best: leesBest(),
  setNear: (n) => set((s) => {
    if (s.near?.id === n?.id) { if (s.near && n) s.near.d = n.d; return {}; }
    return { near: n };
  }),
}));

export function speel(id: GameId) {
  try { if (document.pointerLockElement) document.exitPointerLock(); } catch { /* */ }
  walkLock.on = true;
  usePlay.setState({ open: id });
}
export function stopSpel() {
  usePlay.setState({ open: null });
  walkLock.on = false;
}
/** nieuwe score: geeft true als het een nieuw record is */
export function score(id: GameId, n: number): boolean {
  const b = usePlay.getState().best; if (n <= (b[id] ?? 0)) return false;
  const nb = { ...b, [id]: Math.round(n) };
  try { localStorage.setItem('dm-highscores', JSON.stringify(nb)); } catch { /* */ }
  usePlay.setState({ best: nb }); return true;
}
