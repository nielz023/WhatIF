/**
 * LOOPROUTES voor de medewerkers (niels 2026-11-06: "medewerkers die lopen, typen en naar elkaar toe gaan").
 * De kaart komt uit Blender (hq/blender/nav_build.py): een raster van 5 cm waarin bureaus, wanden,
 * planten en glas zwart zijn. Hier zoeken we met A* een route en maken die daarna recht waar het kan.
 */
export interface NavMeta { half: number; res: number; n: number; doors: Record<string, { o: [number, number]; i: [number, number] }>; coffee: Record<string, { p: [number, number]; l: [number, number] }> }
export interface Nav { meta: NavMeta; free: Uint8Array; n: number }

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
        return { meta, free, n: meta.n };
      } catch (e) { console.warn('[HQ] looproutekaart niet geladen', e); return null; }
    })();
  }
  return promise;
}

const toCell = (nav: Nav, x: number, z: number): [number, number] => [Math.floor((x + nav.meta.half) / nav.meta.res), Math.floor((z + nav.meta.half) / nav.meta.res)];
const toWorld = (nav: Nav, i: number, j: number): [number, number] => [(i + 0.5) * nav.meta.res - nav.meta.half, (j + 0.5) * nav.meta.res - nav.meta.half];
export const isFree = (nav: Nav, x: number, z: number) => { const [i, j] = toCell(nav, x, z); return i >= 0 && j >= 0 && i < nav.n && j < nav.n && nav.free[j * nav.n + i] === 1; };

/** dichtstbijzijnde vrije plek (spiraal-zoektocht tot ~1,5 m) */
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

/** A* over het raster (8 richtingen), daarna touwtje-trekken voor rechte stukken */
export function findPath(nav: Nav, from: [number, number], to: [number, number]): [number, number][] | null {
  const a = nearestFree(nav, from[0], from[1]); const b = nearestFree(nav, to[0], to[1]);
  if (!a || !b) return null;
  if (lineFree(nav, a[0], a[1], b[0], b[1])) return [a, b];
  const n = nav.n; const [si, sj] = toCell(nav, a[0], a[1]); const [ti, tj] = toCell(nav, b[0], b[1]);
  const start = sj * n + si, goal = tj * n + ti;
  const g = new Float32Array(n * n).fill(Infinity); const came = new Int32Array(n * n).fill(-1); const closed = new Uint8Array(n * n);
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
