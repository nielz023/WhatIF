/**
 * BOVENVERDIEPING: indeling (niels 2026-11-07): "een kantine met koffiezetapparaten, een keukentje, tafels waar ze
 * aan zitten en waar ze tegenaan praten ... Een kamer waar allemaal gameconsoles staan, zoals van die gamekasten, van
 * die race seats met zo'n stuur en gaspedaal en een scherm erachter ... wat meer planten, wat meer attributen,
 * maar niet te veel dat het te druk is."
 *
 * Eén bron voor drie dingen: het tekenen (Upstairs.tsx), de looproutekaart boven (buildNav1) en de plekken waar
 * medewerkers iets gaan doen (SPOTS, gebruikt door crew.tsx). Coördinaten: x/z zoals beneden, hoogte t.o.v. Y1.
 *   rechts (+x): kantine · links (-x): gamekamer · voor (+z): lounge met pingpong · achter (-z): aquarium-hoek
 */
import { UP_R, STAIR_LAND } from './floors';
import { mainArea, type Nav } from './nav';

type V2 = [number, number];

export interface Rect { c: V2; w: number; d: number; ry?: number }
export interface Circle { c: V2; r: number }

/** binnenstraal van de achthoek (afstand tot de rechte zijden); de zijden staan haaks op 0°, 45°, 90° ... */
export const UP_IN = UP_R * Math.cos(Math.PI / 8);
export const VIDE_R = 2.75; // gat rond de hologramzuil (je kijkt naar beneden op de receptie)
export const RAIL_R = 2.95;
/** gat in de vloer boven de zijtrap; de kant bij z = -5,65 is open (daar stap je de trap af of op) */
export const HOLE = { x0: -4.62, x1: -2.72, z0: -5.65, z1: -1.4 };

/* ---------- kantine (rechts) ---------- */
export const K = {
  wall: { c: [14.25, 0] as V2, w: 0.2, d: 11.4 },
  counter: { c: [13.5, -0.2] as V2, w: 0.72, d: 6.6 }, // z -3.5 .. 3.1
  fridge: { c: [13.5, 3.75] as V2, w: 0.78, d: 0.8 },
  cooler: { c: [13.55, -4.35] as V2, r: 0.3 },
  island: { c: [11.05, 0] as V2, w: 0.95, d: 3.7 },
  coffeeZ: [-3.0, -2.3, -1.6],
  sinkZ: 0.4, microZ: 1.9,
  stoolsZ: [-1.25, 0, 1.25], stoolX: 10.22,
  tables: [[7.7, 4.7], [10.5, 7.2], [7.7, -4.7], [10.5, -7.2]] as V2[],
};
/* ---------- gamekamer (links), sinds 9 nov groter: glas op x = -5,9 en zijwanden op z = ±6,6 ---------- */
export const G = {
  wall: { c: [-14.3, 0] as V2, w: 0.2, d: 11.4 },
  /** binnenkant van de kamer (glaswand met de ingang tussen z -1,0 en 1,1) */
  x1: -5.9, zMax: 6.6,
  glass: [{ c: [-5.9, -3.8] as V2, w: 0.08, d: 5.6 }, { c: [-5.9, 3.85] as V2, w: 0.08, d: 5.5 }],
  /** zijwanden van glas, van de ingangswand tot de balustrade */
  side: [{ c: [-9.79, -6.6] as V2, w: 7.78, d: 0.08 }, { c: [-9.79, 6.6] as V2, w: 7.78, d: 0.08 }],
  arcadeZ: [-3.4, -2.35, -1.3, -0.25, 0.8, 1.85], arcadeX: -13.55,
  raceX: [-12.4, -10.6, -8.8], raceZ: 4.3, // midden van het frame; stoel op +0,45, scherm op -0,8
  tv: { c: [-10.2, -6.15] as V2, w: 2.3, d: 0.35 },
  sofa: { c: [-10.2, -4.15] as V2, w: 2.2, d: 0.9 },
  table: { c: [-10.2, -5.15] as V2, w: 1.0, d: 0.45 },
  beans: [[-12.25, -4.85], [-8.15, -4.85]] as V2[],
  /** airhockeytafel (lang in de z-richting) en grijpmachine (voorkant naar +z) */
  hockey: { c: [-9.3, 0.3] as V2, w: 1.1, d: 2.0 },
  claw: { c: [-6.75, -5.95] as V2, w: 0.86, d: 0.86 },
  /** bord met de highscores aan de achterwand */
  board: { c: [-14.15, -4.85] as V2 },
};
/* ---------- lounge vooraan en hoek achteraan ---------- */
export const L = {
  pingpong: { c: [0, 9.7] as V2, w: 2.74, d: 1.52 },
  foos: { c: [-4.7, 10.7] as V2, w: 1.25, d: 0.75 },
  sofa: { c: [4.7, 11.6] as V2, w: 2.2, d: 0.9, ry: Math.PI },
  table: { c: [4.7, 10.05] as V2, w: 1.1, d: 0.5 },
  jukebox: { c: [8.2, 10.9] as V2, w: 0.9, d: 0.6, ry: -Math.PI / 4 - Math.PI },
  aquarium: { c: [0.6, -12.9] as V2, w: 4.6, d: 0.7 },
  chairs: [[-0.6, -10.6], [1.8, -10.6]] as V2[],
  vending: [{ c: [5.8, -11.7] as V2, w: 1.0, d: 0.8, ry: -Math.PI / 4 }, { c: [6.95, -10.55] as V2, w: 1.0, d: 0.8, ry: -Math.PI / 4 }],
};
/** planten: [x, z, grootte, soort] */
export const PLANTS: [number, number, number, number][] = [
  [13.0, -5.45, 1.15, 0], [12.7, 5.3, 1.0, 1], [6.3, 7.2, 0.8, 2], [6.3, -7.2, 0.85, 1], [9.9, 9.9, 0.9, 0], [9.9, -9.9, 0.9, 2],
  [-13.3, -6.0, 1.05, 1], [-7.75, -6.15, 0.8, 2], [-13.2, 5.6, 0.95, 0], [-6.6, 5.9, 0.8, 1],
  [-2.6, 13.0, 1.0, 0], [2.6, 13.0, 1.0, 2], [-9.2, 9.6, 0.9, 1],
  [-2.4, -12.4, 0.9, 0], [3.5, -12.6, 0.85, 1], [-6.0, -10.6, 1.0, 2],
];

/* ---------- plekken voor de medewerkers ---------- */
export type SpotPose = 'game' | 'race' | 'tv' | 'talk' | 'pour' | 'paddle' | 'foos' | 'look';
export interface Spot {
  id: string; zone: 'kantine' | 'game' | 'lounge';
  /** plek waar hij staat (of vanwaar hij gaat zitten) */
  p: V2;
  /** zitplek (stoel, kruk, racestoel, bank); leeg = staand */
  sit?: V2; seatH?: number;
  face: V2; pose: SpotPose;
  /** samen aan één tafel of spel: daar praten of spelen ze met elkaar */
  group?: string;
  /** wat de hover-tekst zegt */
  doing: string;
}
const chairOff: V2[] = [[0.82, 0], [-0.82, 0], [0, 0.82], [0, -0.82]];
function buildSpots(): Spot[] {
  const out: Spot[] = [];
  K.coffeeZ.forEach((z, i) => out.push({ id: `koffie${i}`, zone: 'kantine', p: [12.55, z], face: [13.5, z], pose: 'pour', doing: 'zet koffie in de kantine' }));
  K.stoolsZ.forEach((z, i) => out.push({ id: `kruk${i}`, zone: 'kantine', p: [9.55, z], sit: [K.stoolX, z], seatH: 0.72, face: [11.05, z], pose: 'talk', group: 'bar', doing: 'kletst aan de bar' }));
  K.tables.forEach(([tx, tz], t) => chairOff.forEach(([ox, oz], i) => {
    const c: V2 = [tx + ox, tz + oz]; const k = 1 + 0.5 / 0.82;
    out.push({ id: `tafel${t}_${i}`, zone: 'kantine', p: [tx + ox * k, tz + oz * k], sit: c, seatH: 0.47, face: [tx, tz], pose: 'talk', group: `tafel${t}`, doing: 'zit te kletsen in de kantine' });
  }));
  G.arcadeZ.forEach((z, i) => out.push({ id: `kast${i}`, zone: 'game', p: [G.arcadeX + 0.8, z], face: [G.arcadeX, z], pose: 'game', doing: 'speelt op een gamekast' }));
  G.raceX.forEach((x, i) => out.push({ id: `race${i}`, zone: 'game', p: [x + 0.7, G.raceZ + 1.15], sit: [x, G.raceZ + 0.5], seatH: 0.42, face: [x, G.raceZ - 0.8], pose: 'race', group: 'race', doing: 'racet in de racesimulator' }));
  [-1, 1].forEach((sd, i) => out.push({ id: `hockey${i}`, zone: 'game', p: [G.hockey.c[0], G.hockey.c[1] + sd * (G.hockey.d / 2 + 0.42)], face: G.hockey.c, pose: 'paddle', group: 'hockey', doing: 'speelt airhockey' }));
  out.push({ id: 'grijp', zone: 'game', p: [G.claw.c[0], G.claw.c[1] + 0.95], face: G.claw.c, pose: 'game', doing: 'probeert een knuffel te grijpen' });
  [-0.55, 0.55].forEach((dx, i) => out.push({ id: `bank${i}`, zone: 'game', p: [G.sofa.c[0] + dx, G.sofa.c[1] + 0.9], sit: [G.sofa.c[0] + dx, G.sofa.c[1] + 0.05], seatH: 0.45, face: [G.tv.c[0] + dx * 0.4, G.tv.c[1]], pose: 'tv', group: 'tv', doing: 'gamet op de bank' }));
  G.beans.forEach(([x, z], i) => out.push({ id: `zitzak${i}`, zone: 'game', p: [x + (x < G.sofa.c[0] ? 0.15 : -0.15), z + 0.85], sit: [x, z], seatH: 0.32, face: [G.tv.c[0], G.tv.c[1]], pose: 'tv', group: 'tv', doing: 'gamet op een zitzak' }));
  [-1, 1].forEach((sd, i) => out.push({ id: `pingpong${i}`, zone: 'lounge', p: [L.pingpong.c[0] + sd * 1.95, L.pingpong.c[1]], face: L.pingpong.c, pose: 'paddle', group: 'pingpong', doing: 'speelt pingpong' }));
  [-1, 1].forEach((sd, i) => out.push({ id: `voetbal${i}`, zone: 'lounge', p: [L.foos.c[0], L.foos.c[1] + sd * 0.82], face: L.foos.c, pose: 'foos', group: 'voetbal', doing: 'speelt tafelvoetbal' }));
  [-0.55, 0.55].forEach((dx, i) => out.push({ id: `lounge${i}`, zone: 'lounge', p: [L.sofa.c[0] + dx, L.sofa.c[1] - 0.95], sit: [L.sofa.c[0] + dx, L.sofa.c[1] - 0.05], seatH: 0.45, face: [L.sofa.c[0] + dx, L.table.c[1]], pose: 'talk', group: 'lounge', doing: 'kletst in de lounge' }));
  L.chairs.forEach(([x, z], i) => out.push({ id: `aquarium${i}`, zone: 'lounge', p: [x, z + 0.75], sit: [x, z], seatH: 0.45, face: [x * 0.6 + 0.24, L.aquarium.c[1]], pose: 'look', group: 'aquarium', doing: 'kijkt naar de vissen' }));
  return out;
}
export const SPOTS = buildSpots();
/** wie zit waar (spot-id → 1 onderweg, 2 staat of zit er); de pingpongbal kijkt hiernaar */
export const occupied = new Map<string, number>();

/** obstakels voor de looproutekaart (opgedikt met PAD) */
function obstacles(): { rects: Rect[]; circles: Circle[] } {
  const rects: Rect[] = [
    K.wall, K.counter, K.fridge, K.island,
    ...K.stoolsZ.map((z) => ({ c: [K.stoolX, z] as V2, w: 0.36, d: 0.36 })),
    ...K.tables.flatMap(([x, z]) => chairOff.map(([ox, oz]) => ({ c: [x + ox, z + oz] as V2, w: 0.46, d: 0.46 }))),
    G.wall, ...G.glass, ...G.side, G.hockey, G.claw,
    ...G.arcadeZ.map((z) => ({ c: [G.arcadeX, z] as V2, w: 0.78, d: 0.74 })),
    ...G.raceX.map((x) => ({ c: [x, G.raceZ] as V2, w: 0.82, d: 1.95 })),
    G.tv, G.sofa, G.table,
    L.pingpong, L.foos, L.sofa, L.table, L.jukebox, L.aquarium, ...L.vending,
    ...L.chairs.map(([x, z]) => ({ c: [x, z] as V2, w: 0.75, d: 0.75 })),
  ];
  const circles: Circle[] = [
    { c: K.cooler.c, r: K.cooler.r }, ...K.tables.map((c) => ({ c, r: 0.58 })),
    ...G.beans.map((c) => ({ c, r: 0.45 })),
    ...PLANTS.map(([x, z, s]) => ({ c: [x, z] as V2, r: 0.42 * s })),
  ];
  return { rects, circles };
}

const PAD = 0.2;
let nav1: Nav | null = null;
/** looproutekaart van de bovenverdieping (zelfde raster als beneden: 5 cm, 36 x 36 m) */
export function buildNav1(): Nav {
  if (nav1) return nav1;
  const half = 18, res = 0.05, n = Math.round((2 * half) / res);
  const free = new Uint8Array(n * n);
  const inr = UP_IN - 0.35 - PAD; // glazen balustrade aan de rand
  const NRM = Array.from({ length: 8 }, (_, k) => [Math.sin((k * Math.PI) / 4), Math.cos((k * Math.PI) / 4)]);
  for (let j = 0; j < n; j++) {
    const z = (j + 0.5) * res - half;
    for (let i = 0; i < n; i++) {
      const x = (i + 0.5) * res - half;
      let inside = true;
      for (const [sx, sz] of NRM) if (x * sx + z * sz > inr) { inside = false; break; }
      if (!inside) continue;
      if (Math.hypot(x, z) < RAIL_R + 0.06 + PAD) continue;
      if (x > HOLE.x0 - 0.06 - PAD && x < HOLE.x1 + 0.06 + PAD && z > HOLE.z0 - 0.05 && z < HOLE.z1 + 0.06 + PAD) continue;
      free[j * n + i] = 1;
    }
  }
  const cell = (x: number, z: number): [number, number] => [Math.floor((x + half) / res), Math.floor((z + half) / res)];
  const { rects, circles } = obstacles();
  for (const r of rects) {
    const ry = r.ry ?? 0; const cs = Math.cos(ry), sn = Math.sin(ry);
    const ext = Math.hypot(r.w, r.d) / 2 + PAD;
    const [i0, j0] = cell(r.c[0] - ext, r.c[1] - ext); const [i1, j1] = cell(r.c[0] + ext, r.c[1] + ext);
    for (let j = Math.max(0, j0); j <= Math.min(n - 1, j1); j++) for (let i = Math.max(0, i0); i <= Math.min(n - 1, i1); i++) {
      const dx = (i + 0.5) * res - half - r.c[0], dz = (j + 0.5) * res - half - r.c[1];
      const px = dx * cs - dz * sn, pz = dx * sn + dz * cs;
      if (Math.abs(px) <= r.w / 2 + PAD && Math.abs(pz) <= r.d / 2 + PAD) free[j * n + i] = 0;
    }
  }
  for (const c of circles) {
    const rr = c.r + PAD; const [i0, j0] = cell(c.c[0] - rr, c.c[1] - rr); const [i1, j1] = cell(c.c[0] + rr, c.c[1] + rr);
    for (let j = Math.max(0, j0); j <= Math.min(n - 1, j1); j++) for (let i = Math.max(0, i0); i <= Math.min(n - 1, i1); i++) {
      if (Math.hypot((i + 0.5) * res - half - c.c[0], (j + 0.5) * res - half - c.c[1]) <= rr) free[j * n + i] = 0;
    }
  }
  nav1 = { meta: { half, res, n, doors: {}, coffee: {} }, free: mainArea(free, n, [STAIR_LAND], half, res), n };
  return nav1;
}
