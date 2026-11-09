/** Instellingen van niels die alleen in deze browser staan (verbeterlijst punt 73). */
export type Prefs = { minderBeweging: boolean; telefoon3d: boolean; meldingen: boolean; meldingGeluid: boolean };
const KEY = 'dm-prefs';
const STD: Prefs = { minderBeweging: false, telefoon3d: false, meldingen: true, meldingGeluid: true };
let cache: Prefs | null = null;
const fns = new Set<(p: Prefs) => void>();

export function prefs(): Prefs {
  if (cache) return cache;
  try { cache = { ...STD, ...(JSON.parse(localStorage.getItem(KEY) || '{}') as Partial<Prefs>) }; } catch { cache = { ...STD }; }
  return cache;
}
export function setPref<K extends keyof Prefs>(k: K, v: Prefs[K]) {
  cache = { ...prefs(), [k]: v };
  try { localStorage.setItem(KEY, JSON.stringify(cache)); } catch { /* */ }
  pasToe(); fns.forEach((f) => f(cache!));
}
export function onPrefs(f: (p: Prefs) => void) { fns.add(f); return () => { fns.delete(f); }; }
/** zet de klasse voor minder beweging op <html> */
export function pasToe() {
  try { document.documentElement.classList.toggle('dm-rustig', prefs().minderBeweging || matchMedia('(prefers-reduced-motion: reduce)').matches); } catch { /* */ }
}
