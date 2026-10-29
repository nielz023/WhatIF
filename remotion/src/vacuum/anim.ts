// Small animation helpers. Times are in seconds.
export const FPS = 60;

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
/** 0..1 progress of x between a and b, clamped. */
export const inv = (a: number, b: number, x: number) => (b === a ? (x >= b ? 1 : 0) : clamp((x - a) / (b - a)));

export const easeInOutCubic = (u: number) => (u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2);
export const easeOutCubic = (u: number) => 1 - Math.pow(1 - u, 3);
export const easeInCubic = (u: number) => u * u * u;
export const easeInOutSine = (u: number) => -(Math.cos(Math.PI * u) - 1) / 2;
export const easeOutBack = (u: number, s = 1.70158) => 1 + (s + 1) * Math.pow(u - 1, 3) + s * Math.pow(u - 1, 2);

/** Scale for something popping in at t0: 0 -> overshoot -> 1. */
export const popIn = (t: number, t0: number, dur = 0.24, s = 2.4) => {
  const u = inv(t0, t0 + dur, t);
  return u <= 0 ? 0 : easeOutBack(u, s);
};
/** Scale for something popping out at t0: small swell, then shrink to 0. */
export const popOut = (t: number, t0: number, dur = 0.18) => {
  if (t < t0) return 1;
  const u = inv(t0, t0 + dur, t);
  return u >= 1 ? 0 : (1 + 0.15 * Math.sin(Math.PI * Math.min(1, u * 2))) * (1 - easeInCubic(u));
};
/** Decaying oscillation that starts at t0 (0 before). */
export const wobble = (t: number, t0: number, freq = 5, damp = 5) => {
  if (t < t0) return 0;
  const x = t - t0;
  return Math.exp(-damp * x) * Math.sin(2 * Math.PI * freq * x);
};
/** Smooth 0 -> 1 -> 0 bump centred on t0 with half width w. */
export const bump = (t: number, t0: number, w: number) => {
  const x = (t - t0) / w;
  return Math.abs(x) >= 1 ? 0 : 0.5 + 0.5 * Math.cos(Math.PI * x);
};

/**
 * Squash for a pose swap at tSwap. 'action': anticipation squash before the swap, then a
 * stretch that settles like a damped spring. 'turn': narrowest (scaleX ~0.8) on the swap frame.
 */
export function swapSquash(t: number, tSwap: number, kind: 'action' | 'turn' | 'soft' = 'action') {
  if (kind === 'turn') {
    const d = Math.abs(t - tSwap);
    if (d > 0.09) return {sx: 1, sy: 1};
    const w = 1 - 0.2 * (1 - d / 0.09);
    return {sx: w, sy: 1 + (1 - w) * 0.15};
  }
  const amp = kind === 'soft' ? 0.5 : 1;
  const pre = 0.08;
  if (t < tSwap - pre || t > tSwap + 0.45) return {sx: 1, sy: 1};
  if (t < tSwap) {
    const u = inv(tSwap - pre, tSwap, t);
    return {sx: 1 + 0.04 * u * amp, sy: 1 - 0.06 * u * amp};
  }
  const x = t - tSwap;
  const s = 0.05 * amp * Math.exp(-8 * x) * Math.cos(2 * Math.PI * 3.2 * x);
  return {sx: 1 - s * 0.6, sy: 1 + s};
}

/** Combine several swaps: multiply their squash factors. */
export function squashAll(t: number, swaps: {t: number; kind?: 'action' | 'turn' | 'soft'}[]) {
  let sx = 1;
  let sy = 1;
  for (const s of swaps) {
    const q = swapSquash(t, s.t, s.kind);
    sx *= q.sx;
    sy *= q.sy;
  }
  return {sx, sy};
}

/** Pick the active item of a time-sorted list ({t} = start time). */
export function activeAt<T extends {t: number}>(list: T[], t: number): T {
  let cur = list[0];
  for (const it of list) if (t >= it.t) cur = it;
  return cur;
}

/** Point on a cubic bezier. */
export function bez(p0: number[], p1: number[], p2: number[], p3: number[], s: number): [number, number] {
  const a = 1 - s;
  const x = a * a * a * p0[0] + 3 * a * a * s * p1[0] + 3 * a * s * s * p2[0] + s * s * s * p3[0];
  const y = a * a * a * p0[1] + 3 * a * a * s * p1[1] + 3 * a * s * s * p2[1] + s * s * s * p3[1];
  return [x, y];
}

/** Deterministic pseudo random in [0,1) from an integer seed. */
export const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

/** Screen shake: sum of sines times a decaying envelope, never random jumps. */
export function shake(t: number, events: {t: number; amp: number; decay?: number}[]) {
  let x = 0;
  let y = 0;
  for (const e of events) {
    if (t < e.t) continue;
    const d = t - e.t;
    const env = e.amp * Math.exp(-(e.decay ?? 7) * d);
    if (env < 0.05) continue;
    x += env * (Math.sin(2 * Math.PI * 13.3 * d) * 0.7 + Math.sin(2 * Math.PI * 7.1 * d + 1.3) * 0.3);
    y += env * (Math.sin(2 * Math.PI * 11.7 * d + 0.7) * 0.7 + Math.sin(2 * Math.PI * 5.3 * d + 2.1) * 0.3);
  }
  return {x, y};
}
