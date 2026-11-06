/**
 * ZOEKEN ZONDER HOOFDLETTERS EN ACCENTEN (Kennis › Zoeken en het markeren van treffers).
 * vouw() geeft kleine letters zonder accenten en is precies even lang als de invoer, zodat een positie in de
 * gevouwen tekst dezelfde is als in de echte tekst (nodig om de treffers in de echte tekst te markeren).
 */
const ACCENT = /[À-ɏḀ-ỿ]/g;
const zonderAccent = (c: string) => { const b = c.normalize('NFD').replace(/[̀-ͯ]/g, ''); return b.length === 1 ? b : c; };

export function vouw(s: string): string {
  let uit = s.toLowerCase();
  // een paar tekens worden langer in kleine letters (bijv. İ): die laten we staan, zodat de lengte gelijk blijft
  if (uit.length !== s.length) uit = Array.from(s, (c) => { const l = c.toLowerCase(); return l.length === c.length ? l : c; }).join('');
  return uit.replace(ACCENT, zonderAccent);
}

/** De zoekwoorden uit wat niels typt: gevouwen, zonder leestekens, minstens 2 tekens, elk één keer (hooguit 8). */
export function zoekTermen(q: string): string[] {
  return [...new Set(vouw(q).split(/[^\p{L}\p{N}]+/u).filter((t) => t.length >= 2))].slice(0, 8);
}

/** Alle plekken waar een van de termen in de (gevouwen) tekst staat, van voor naar achter, zonder overlap. */
export function treffers(gevouwen: string, termen: string[], van = 0, tot = gevouwen.length): [number, number][] {
  const uit: [number, number][] = [];
  if (!termen.length) return uit;
  let i = van;
  while (i < tot) {
    let best = -1; let len = 0;
    for (const t of termen) { const p = gevouwen.indexOf(t, i); if (p >= 0 && p < tot && (best < 0 || p < best || (p === best && t.length > len))) { best = p; len = t.length; } }
    if (best < 0) break;
    uit.push([best, Math.min(best + len, tot)]);
    i = best + len;
  }
  return uit;
}

/** een pad binnen de projectbestanden, zonder trucs (geen .., geen \, geen lege stukken) */
export function veiligPad(p: string): boolean {
  return !!p && p.length < 600 && !p.startsWith('/') && !/[\\\0]/.test(p) && p.split('/').every((s) => s && s !== '..' && s !== '.');
}
