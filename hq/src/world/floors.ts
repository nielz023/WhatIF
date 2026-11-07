/**
 * VERDIEPINGEN (niels 2026-11-07): "ik kan niet het trappetje op ... niet naar het middenconsole" en "in het
 * middenconsole een trap omhoog. Ik wil dat die ook in gebruik is. Dat poppetjes erop kunnen lopen en dat je rechts
 * in het midden van het beeld een klein knopje hebt om een verdieping hoger te gaan".
 *
 * - De begane grond krijgt hoogte: het podium van de receptie (0,5 m) en de brede trap vooraan zijn beloopbaar.
 *   De looproutekaart uit Blender had het hele podium zwart; patchGround() opent het podium en de trap en zet de
 *   balie, de zuil, de banken, de planten en de zijtrap er weer als obstakel in.
 * - De zijtrap links op het podium (9 treden, office_build.py) loopt naar de bovenverdieping op Y1. Daar staan de
 *   kantine en de gamekamer (Upstairs.tsx).
 * - useFloor: welke verdieping je bekijkt. Op de begane grond is de bovenverdieping weg (zoals bij een poppenhuis),
 *   boven ligt de vloer over het kantoor heen.
 */
import { create } from 'zustand';
import { R_HUB } from './rooms';

type V2 = [number, number];
type V3 = [number, number, number];

/** vloer van de bovenverdieping: één trede (0,32 m) boven de bovenste trede van de zijtrap */
export const Y1 = 3.38;
/** dikte van de vloerplaat (de wanden beneden zijn 3,0 m met neon tot ~3,06 m) */
export const SLAB = 0.28;
/** straal (hoekpunten van de achthoek) van de bovenverdieping; de rand van de begane grond blijft eronder zichtbaar */
export const UP_R = 15.9;

export type Floor = 0 | 1;
interface FloorStore {
  floor: Floor; setFloor: (f: Floor) => void;
  /** knop "verdieping hoger/lager": tijdens het rondlopen doet Walk.tsx de overgang, anders wisselt hij meteen */
  want: Floor; req: number; request: (f: Floor) => void;
}
export const useFloor = create<FloorStore>((set) => ({
  floor: 0, setFloor: (floor) => set({ floor, want: floor }),
  want: 0, req: 0, request: (want) => set((s) => ({ want, req: s.req + 1 })),
}));

/* ---------- zijtrap (zelfde maten als office_build.py) ---------- */
// trede i (0..8): midden x = -3.4 - 0.05 i, z = -1 - 0.55 i, bovenkant y = 0.54 + 0.32 i, 1,5 m breed, 0,5 m diep
export const STAIR_FOOT: V2 = [-3.4, -0.42]; // op het podium, net voor de eerste trede
export const STAIR_LAND: V2 = [-3.87, -6.3]; // boven, net voorbij de laatste trede
const Z0 = -0.75, Z1 = -5.67; // begin van trede 0 en eind van trede 8

/** hoogte van de trap onder een punt (z), traptreden als echte stappen */
export function stairStepY(z: number) {
  if (z >= Z0) return 0.5;
  if (z <= Z1) return Y1;
  const i = Math.max(0, Math.min(8, Math.round((-1 - z) / 0.55)));
  return 0.54 + 0.32 * i;
}
/** punt op de looplijn van de trap: u = 0 onderaan (podium), u = 1 boven op de verdieping */
export function stairPoint(u: number, smooth = false): V3 {
  const k = Math.max(0, Math.min(1, u));
  const x = STAIR_FOOT[0] + (STAIR_LAND[0] - STAIR_FOOT[0]) * k;
  const z = STAIR_FOOT[1] + (STAIR_LAND[1] - STAIR_FOOT[1]) * k;
  const y = smooth ? stairRampY(z) : stairStepY(z);
  return [x, y, z];
}
/** vloeiende hoogte langs de trap (voor de camera bij het rondlopen): zelfde helling als de treden */
export function stairRampY(z: number) {
  return 0.5 + Math.max(0, Math.min(1, (Z0 - z) / (Z0 - Z1 + 0.28))) * (Y1 - 0.5);
}
export const STAIR_LEN = Math.hypot(STAIR_LAND[0] - STAIR_FOOT[0], STAIR_LAND[1] - STAIR_FOOT[1]);
/** halve breedte van de looplijn op de trap (de trap is 1,5 m breed) */
export const STAIR_HALF = 0.42;
/** plek t.o.v. de trap: u langs de looplijn (0 onder, 1 boven), d zijwaarts in meters */
export function stairUV(x: number, z: number): [number, number] {
  const dx = STAIR_LAND[0] - STAIR_FOOT[0], dz = STAIR_LAND[1] - STAIR_FOOT[1];
  const px = x - STAIR_FOOT[0], pz = z - STAIR_FOOT[1];
  return [(px * dx + pz * dz) / (STAIR_LEN * STAIR_LEN), (px * dz - pz * dx) / STAIR_LEN];
}
/** staat dit punt op de looplijn van de trap? */
export function onStair(x: number, z: number) {
  const [u, d] = stairUV(x, z); return u >= -0.03 && u <= 1.04 && Math.abs(d) < STAIR_HALF;
}
/** waar je uitkomt met het knopje tijdens het rondlopen: boven net voorbij de trap, beneden aan de voet */
export const ARRIVE_UP: V2 = [-3.87, -6.85];
export const ARRIVE_DOWN: V2 = [-3.35, -0.1];

/* ---------- trap vooraan (ingang) ---------- */
const FRONT_N = 7, FRONT_D = (15.2 - R_HUB - 1) / FRONT_N, FRONT_Z0 = R_HUB + 0.3;
const frontHalfW = (i: number) => (3.6 + i * 0.22) / 2;
const FRONT_END = FRONT_Z0 + FRONT_N * FRONT_D;

/**
 * Vloerhoogte op de begane grond voor het podium en de trap vooraan; null = gewone vloer (de afdelingen en gangen
 * regelt crew.tsx zelf, met hun 6-7,5 cm vloer en tapijt).
 */
export function groundY(x: number, z: number): number | null {
  if (z > R_HUB - 0.2 && z < FRONT_END && Math.abs(x) < 2.7) {
    if (z < FRONT_Z0) return 0.5;
    const i = Math.floor((z - FRONT_Z0) / FRONT_D);
    return Math.max(0, 0.5 - (i + 1) * (0.6 / FRONT_N));
  }
  if (Math.hypot(x, z) < R_HUB + 0.05) return 0.5;
  return null;
}

/* ---------- obstakels op het podium (uit office_build.py, ~0,2 m opgedikt voor een halve medewerker) ---------- */
const PAD = 0.2;
interface Rect { c: V2; w: number; d: number; ry: number }
const SOFAS: Rect[] = [
  { c: [-4.2, 1.4], w: 2.0, d: 0.85, ry: Math.PI / 2 + 0.5 },
  { c: [4.2, 1.4], w: 2.0, d: 0.85, ry: -Math.PI / 2 - 0.5 },
];
const PLANTS: [number, number, number][] = [[3.4, -2.6, 0.85], [-2.0, -3.9, 0.9], [4.6, -1.0, 0.8], [-4.6, -1.0, 0.8], [3.0, 3.9, 0.75], [-3.0, 3.9, 0.75]];
/** lokale coördinaten t.o.v. een gedraaide rechthoek (zelfde draaiing als tf() in office_build.py) */
export function inRect(x: number, z: number, r: Rect, pad = 0) {
  const dx = x - r.c[0], dz = z - r.c[1]; const cs = Math.cos(r.ry), sn = Math.sin(r.ry);
  const px = dx * cs - dz * sn, pz = dx * sn + dz * cs;
  return Math.abs(px) <= r.w / 2 + pad && Math.abs(pz) <= r.d / 2 + pad;
}
function podiumBlocked(x: number, z: number) {
  const r = Math.hypot(x, z);
  if (r < 2.45 + PAD + 0.05) return true; // voet van de hologramzuil
  if (r < 2.95 + PAD && Math.abs(Math.atan2(x, z)) < 1.25 + 0.08) return true; // ronde balie vooraan
  for (const s of SOFAS) if (inRect(x, z, s, PAD)) return true;
  for (const [px, pz, s] of PLANTS) if (Math.hypot(x - px, z - pz) < 0.45 * s + PAD) return true;
  if (x > -4.25 - PAD && x < -2.55 + PAD && z < -0.78 && z > -6.0) return true; // zijtrap (je loopt hem op via de voet)
  return false;
}

/**
 * Opent het podium en de trap vooraan op de looproutekaart (wit = vrij). Werkt op het ruwe raster, vóór de keuze van
 * het grootste loopgebied in nav.ts.
 */
export function patchGround(free: Uint8Array, n: number, half: number, res: number) {
  for (let j = 0; j < n; j++) {
    const z = (j + 0.5) * res - half;
    if (z < -R_HUB - 0.5 || z > FRONT_END + 0.1) continue;
    for (let i = 0; i < n; i++) {
      const x = (i + 0.5) * res - half;
      if (Math.abs(x) > R_HUB + 0.5) continue;
      const id = j * n + i; const r = Math.hypot(x, z);
      let open = false;
      if (r < R_HUB - 0.25) open = !podiumBlocked(x, z);
      // trap vooraan: tussen de leuningen, met ~0,25 m afstand tot de rand
      if (z > R_HUB - 0.45 && z < FRONT_END - 0.05) {
        const k = z < FRONT_Z0 ? 0 : Math.min(FRONT_N - 1, Math.floor((z - FRONT_Z0) / FRONT_D));
        if (Math.abs(x) < frontHalfW(k) - 0.25) open = true;
      }
      if (open) free[id] = 1;
      else if (r < R_HUB - 0.25) free[id] = 0;
    }
  }
}
