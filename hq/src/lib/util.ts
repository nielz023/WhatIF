let counter = 0;
export const uid = (prefix = 'id') =>
  `${prefix}_${Date.now().toString(36)}${(counter++).toString(36)}${Math.random().toString(36).slice(2, 6)}`;

export const rand = (min: number, max: number) => min + Math.random() * (max - min);
export const randInt = (min: number, max: number) => Math.floor(rand(min, max + 1));
export const pick = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
export const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

/** 24 ticks per game day. Day 0 = 1 Jan 2026. */
export const TICKS_PER_DAY = 24;
export const START_DATE = new Date(Date.UTC(2026, 0, 1));
export const dayOf = (tick: number) => Math.floor(tick / TICKS_PER_DAY);
export const hourOf = (tick: number) => tick % TICKS_PER_DAY;
export const dateOfDay = (day: number) => new Date(START_DATE.getTime() + day * 86400000);
export const monthKey = (day: number) => dateOfDay(day).toISOString().slice(0, 7);
export const fmtDate = (day: number) =>
  dateOfDay(day).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });
export const fmtTick = (tick: number) =>
  `${dateOfDay(dayOf(tick)).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', timeZone: 'UTC' })} ${String(hourOf(tick)).padStart(2, '0')}:00`;

export const relTime = (tick: number, now: number) => {
  const d = now - tick;
  if (d <= 0) return 'just now';
  if (d < TICKS_PER_DAY) return `${d}h ago`;
  return `${Math.floor(d / TICKS_PER_DAY)}d ago`;
};

export const eur = (n: number, digits = 0) =>
  new Intl.NumberFormat('en-IE', { style: 'currency', currency: 'EUR', maximumFractionDigits: digits }).format(n);

export const compact = (n: number) =>
  new Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(n);

export const pct = (n: number, digits = 1) => `${n.toFixed(digits)}%`;
