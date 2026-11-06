/**
 * TIJD: leest de tijden uit status.json in alle vormen die er staan
 * ('2026-11-05T22:15', '2026-11-05T01:00:00+01:00', '5 nov 22:27') en schrijft ze
 * overal hetzelfde: '6 nov 13:53' (Amsterdamse tijd).
 */
const MAANDEN = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];

export function leesTijd(s: unknown): Date | null {
  if (typeof s !== 'string' || !s.trim()) return null;
  const t = s.trim();
  if (/^\d{4}-\d{2}-\d{2}/.test(t)) {
    const d = new Date(t);
    return isNaN(d.getTime()) ? null : d;
  }
  const m = /^(\d{1,2})\s+([a-z]{3})\w*\.?\s*(?:(\d{4})\s*)?(?:(\d{1,2})[:.](\d{2}))?/i.exec(t);
  if (m) {
    const mi = MAANDEN.indexOf(m[2].toLowerCase().replace('mar', 'mrt').replace('may', 'mei').replace('oct', 'okt'));
    if (mi < 0) return null;
    const jaar = m[3] ? Number(m[3]) : new Date().getFullYear();
    const d = new Date(jaar, mi, Number(m[1]), m[4] ? Number(m[4]) : 0, m[5] ? Number(m[5]) : 0);
    return isNaN(d.getTime()) ? null : d;
  }
  return null;
}

const FMT = (() => {
  try { return new Intl.DateTimeFormat('nl-NL', { timeZone: 'Europe/Amsterdam', day: 'numeric', month: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }); } catch { return null; }
})();

/** '6 nov 13:53'; onleesbare tijden blijven zoals ze waren. */
export function toonTijd(s: unknown): string {
  const d = leesTijd(s);
  if (!d) return typeof s === 'string' ? s : '';
  if (FMT) {
    const p = Object.fromEntries(FMT.formatToParts(d).map((x) => [x.type, x.value]));
    return `${Number(p.day)} ${MAANDEN[Number(p.month) - 1]} ${p.hour}:${p.minute}`;
  }
  return `${d.getDate()} ${MAANDEN[d.getMonth()]} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

/** Nieuwste eerst; zonder leesbare tijd achteraan, in de oude volgorde. */
export function nieuwsteEerst<T extends { at?: unknown }>(lijst: T[]): T[] {
  return lijst.map((x, i) => ({ x, i, t: leesTijd(x.at)?.getTime() ?? -Infinity }))
    .sort((a, b) => (b.t - a.t) || (a.i - b.i)).map((y) => y.x);
}
