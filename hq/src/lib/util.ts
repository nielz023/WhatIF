let counter = 0;
export const uid = (prefix = 'id') =>
  `${prefix}_${Date.now().toString(36)}${(counter++).toString(36)}${Math.random().toString(36).slice(2, 6)}`;

export const rand = (min: number, max: number) => min + Math.random() * (max - min);
export const randInt = (min: number, max: number) => Math.floor(rand(min, max + 1));
export const pick = <T,>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];
export const clamp = (v: number, a: number, b: number) => Math.max(a, Math.min(b, v));

/** 1 tick = 1 echt uur. Tick 0 = 14 okt 2026 00:00 (Amsterdam). De game loopt gelijk met de echte klok. */
export const TICKS_PER_DAY = 24;
export const START_DATE = new Date('2026-10-13T22:00:00Z');
export const TZ = 'Europe/Amsterdam';
export const realTick = () => Math.max(0, Math.floor((Date.now() - START_DATE.getTime()) / 3600000));
export const dayOf = (tick: number) => Math.floor(tick / TICKS_PER_DAY);
export const hourOf = (tick: number) => Number(new Date(START_DATE.getTime() + tick * 3600000).toLocaleString('nl-NL', { hour: 'numeric', hour12: false, timeZone: TZ }));
export const dateOfDay = (day: number) => new Date(START_DATE.getTime() + day * 86400000 + 12 * 3600000);
export const monthKey = (day: number) => dateOfDay(day).toISOString().slice(0, 7);
export const fmtDate = (day: number) =>
  dateOfDay(day).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short', year: 'numeric', timeZone: TZ });
export const fmtTick = (tick: number) =>
  new Date(START_DATE.getTime() + tick * 3600000).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: TZ });

export const relTime = (tick: number, now: number) => {
  const d = now - tick;
  if (d <= 0) return 'zojuist';
  if (d < TICKS_PER_DAY) return `${d} u geleden`;
  return `${Math.floor(d / TICKS_PER_DAY)} d geleden`;
};

export const eur = (n: number, digits = 0) =>
  new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR', maximumFractionDigits: digits }).format(n);

export const compact = (n: number) =>
  new Intl.NumberFormat('nl-NL', { notation: 'compact', maximumFractionDigits: 1 }).format(n);

export const pct = (n: number, digits = 1) => `${n.toFixed(digits)}%`;
