/**
 * LOOPROUTES voor de medewerkers (niels 2026-11-06: "medewerkers die lopen, typen en naar elkaar toe gaan").
 * De kaart komt uit Blender (hq/blender/nav_build.py): een raster van 5 cm waarin bureaus, wanden,
 * planten en glas zwart zijn. Hier zoeken we met A* een route en maken die daarna recht waar het kan.
 */
import { patchGround } from './floors';

export interface NavMeta { half: number; res: number; n: number; doors: Record<string, { o: [number, number]; i: [number, number] }>; coffee: Record<string, { p: [number, number]; l: [number, number] }> }
export interface Nav { meta: NavMeta; free: Uint8Array; n: number }

/** Alleen het grootste aaneengesloten loopgebied telt (kleine ingesloten hoekjes niet), zodat elke route lukt. */
export function mainArea(free: Uint8Array, n: number, seeds: [number, number][], half: number, res: number) {
  const reach = new Uint8Array(n * n); const q = new Int32Array(n * n);
  let best: Uint8Array | null = null; let bestN = 0;
  for (const [x, z] of seeds) {
    const i0 = Math.floor((x + half) / res), j0 = Math.floor((z + half) / res); const id0 = j0 * n + i0;
    if (i0 < 0 || j0 < 0 || i0 >= n || j0 >= n || !free[id0] || reach[id0]) continue;
    const mark = new Uint8Array(n * n); let h = 0, t = 0; q[t++] = id0; mark[id0] = 1; reach[id0] = 1;
    while (h < t) { const id = q[h++]; const i = id % n, j = (id / n) | 0;
      if (i > 0 && free[id - 1] && !mark[id - 1]) { mark[id - 1] = 1; reach[id - 1] = 1; q[t++] = id - 1; }
      if (i < n - 1 && free[id + 1] && !mark[id + 1]) { mark[id + 1] = 1; reach[id + 1] = 1; q[t++] = id + 1; }
      if (j > 0 && free[id - n] && !mark[id - n]) { mark[id - n] = 1; reach[id - n] = 1; q[t++] = id - n; }
      if (j < n - 1 && free[id + n] && !mark[id + n]) { mark[id + n] = 1; reach[id + n] = 1; q[t++] = id + n; } }
    if (t > bestN) { bestN = t; best = mark; }
  }
  return best ?? free;
}

let promise: Promise<Nav | null> | null = null;
export function loadNav(): Promise<Nav | null> {
  if (!promise) {
    promise = (async () => {
      try {
        const meta = (await (await fetch('./models/office_nav.json')).json()) as NavMeta;
        const img = new Image(); img.src = './models/office_nav.png';
        await img.decode();
        const c = document.createElement('canvas'); c.width = meta.n; c.height = meta.n;
        const g = c.getContext('2d', { willReadFrequently: true })!; g.drawImage(img, 0, 0);
        const d = g.getImageData(0, 0, meta.n, meta.n).data;
        const free = new Uint8Array(meta.n * meta.n);
        for (let i = 0; i < free.length; i++) free[i] = d[i * 4] > 127 ? 1 : 0;
        patchGround(free, meta.n, meta.half, meta.res); // podium en trap vooraan beloopbaar (floors.ts)
        const seeds = Object.values(meta.doors).map((x) => x.o);
        return { meta, free: mainArea(free, meta.n, seeds, meta.half, meta.res), n: meta.n };
      } catch (e) { console.warn('[HQ] looproutekaart niet geladen', e); return null; }
    })();
  }
  return promise;
}

const toCell = (nav: Nav, x: number, z: number): [number, number] => [Math.floor((x + nav.meta.half) / nav.meta.res), Math.floor((z + nav.meta.half) / nav.meta.res)];
const toWorld = (nav: Nav, i: number, j: number): [number, number] => [(i + 0.5) * nav.meta.res - nav.meta.half, (j + 0.5) * nav.meta.res - nav.meta.half];
export const isFree = (nav: Nav, x: number, z: number) => { const [i, j] = toCell(nav, x, z); return i >= 0 && j >= 0 && i < nav.n && j < nav.n && nav.free[j * nav.n + i] === 1; };

/** dichtstbijzijnde vrije plek in het loopgebied (spiraal-zoektocht tot ~1,5 m) */
export function nearestFree(nav: Nav, x: number, z: number): [number, number] | null {
  const [ci, cj] = toCell(nav, x, z);
  for (let r = 0; r < 30; r++) {
    let best: [number, number] | null = null; let bd = 1e9;
    for (let dj = -r; dj <= r; dj++) for (let di = -r; di <= r; di++) {
      if (Math.max(Math.abs(di), Math.abs(dj)) !== r) continue;
      const i = ci + di, j = cj + dj;
      if (i < 0 || j < 0 || i >= nav.n || j >= nav.n || !nav.free[j * nav.n + i]) continue;
      const dd = di * di + dj * dj; if (dd < bd) { bd = dd; best = [i, j]; }
    }
    if (best) return toWorld(nav, best[0], best[1]);
  }
  return null;
}

/** rechte lijn vrij? (stapjes van een halve cel) */
export function lineFree(nav: Nav, ax: number, az: number, bx: number, bz: number) {
  const L = Math.hypot(bx - ax, bz - az); const n = Math.ceil(L / (nav.meta.res * 0.5));
  for (let k = 0; k <= n; k++) { const t = n ? k / n : 0; if (!isFree(nav, ax + (bx - ax) * t, az + (bz - az) * t)) return false; }
  return true;
}

let buf: { n: number; g: Float32Array; came: Int32Array; closed: Uint8Array } | null = null; // hergebruikt per zoektocht
/** A* over het raster (8 richtingen), daarna touwtje-trekken voor rechte stukken */
export function findPath(nav: Nav, from: [number, number], to: [number, number]): [number, number][] | null {
  const a = nearestFree(nav, from[0], from[1]); const b = nearestFree(nav, to[0], to[1]);
  if (!a || !b) return null;
  if (lineFree(nav, a[0], a[1], b[0], b[1])) return [a, b];
  const n = nav.n; const [si, sj] = toCell(nav, a[0], a[1]); const [ti, tj] = toCell(nav, b[0], b[1]);
  const start = sj * n + si, goal = tj * n + ti;
  if (!buf || buf.n !== n) buf = { n, g: new Float32Array(n * n), came: new Int32Array(n * n), closed: new Uint8Array(n * n) };
  const { g, came, closed } = buf; g.fill(Infinity); came.fill(-1); closed.fill(0);
  // eenvoudige binaire heap
  const heap: number[] = []; const fsc: number[] = [];
  const push = (id: number, f: number) => { heap.push(id); fsc.push(f); let k = heap.length - 1; while (k > 0) { const p = (k - 1) >> 1; if (fsc[p] <= fsc[k]) break; [heap[p], heap[k]] = [heap[k], heap[p]]; [fsc[p], fsc[k]] = [fsc[k], fsc[p]]; k = p; } };
  const pop = () => { const top = heap[0]; const lh = heap.pop()!; const lf = fsc.pop()!; if (heap.length) { heap[0] = lh; fsc[0] = lf; let k = 0; for (;;) { const l = 2 * k + 1, r = l + 1; let m = k; if (l < heap.length && fsc[l] < fsc[m]) m = l; if (r < heap.length && fsc[r] < fsc[m]) m = r; if (m === k) break; [heap[m], heap[k]] = [heap[k], heap[m]]; [fsc[m], fsc[k]] = [fsc[k], fsc[m]]; k = m; } } return top; };
  const h = (id: number) => { const i = id % n, j = (id / n) | 0; const dx = Math.abs(i - ti), dy = Math.abs(j - tj); return Math.max(dx, dy) + 0.414 * Math.min(dx, dy); };
  g[start] = 0; push(start, h(start));
  const D = [[1, 0, 1], [-1, 0, 1], [0, 1, 1], [0, -1, 1], [1, 1, 1.414], [1, -1, 1.414], [-1, 1, 1.414], [-1, -1, 1.414]];
  let found = false; let guard = 0;
  while (heap.length && guard++ < 400000) {
    const cur = pop(); if (cur === goal) { found = true; break; }
    if (closed[cur]) continue; closed[cur] = 1;
    const ci = cur % n, cj = (cur / n) | 0;
    for (const [di, dj, c] of D) {
      const i = ci + di, j = cj + dj; if (i < 0 || j < 0 || i >= n || j >= n) continue;
      const id = j * n + i; if (!nav.free[id] || closed[id]) continue;
      if (di && dj && (!nav.free[cj * n + i] || !nav.free[j * n + ci])) continue; // geen hoekjes afsnijden
      const ng = g[cur] + c; if (ng < g[id]) { g[id] = ng; came[id] = cur; push(id, ng + h(id)); }
    }
  }
  if (!found) return null;
  const cells: [number, number][] = [];
  for (let id = goal; id !== -1; id = came[id]) cells.push(toWorld(nav, id % n, (id / n) | 0));
  cells.reverse(); cells[0] = a; cells[cells.length - 1] = b;
  // touwtje trekken
  const out: [number, number][] = [cells[0]]; let k = 0;
  while (k < cells.length - 1) {
    let far = k + 1;
    for (let m = cells.length - 1; m > k + 1; m--) if (lineFree(nav, cells[k][0], cells[k][1], cells[m][0], cells[m][1])) { far = m; break; }
    out.push(cells[far]); k = far;
  }
  return out;
}
