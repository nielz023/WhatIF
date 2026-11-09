/**
 * VERSIE EN "WAT IS NIEUW" (verbeterlijst punt 70).
 * Eén plek voor het versienummer (rechtsonder in beeld) en de lijst met wijzigingen.
 * Bij een nieuwe versie: VERSIE ophogen en bovenaan NIEUW een blok toevoegen. Het venster
 * "Wat is nieuw" verschijnt dan één keer per browser (onthouden in localStorage).
 */
export const VERSIE = 'v41';

export interface Nieuw { versie: string; datum?: string; punten: string[] }

export const NIEUW: Nieuw[] = [
  {
    // v42: de coördinator vult deze lijst bij het uitbrengen; tot dan staan hier de onderdelen van stap 4.
    versie: 'v42',
    punten: [
      'Eén vaste huisstijl: dezelfde kaarten, knoppen, letters en kleuren op elke pagina.',
      'Driftmark-logo en banner bovenin, nachtblauw met oranje gloed.',
      'Rustiger lettertype; cijfers staan netjes onder elkaar.',
      'Lege plekken leggen uit wat er komt, in plaats van een leeg vak of een nul.',
      'Kaarten komen zacht binnen en cijfers tellen op; bij verversen springt niets.',
      'Pagina\'s openen sneller: het 3D-kantoor laadt pas als je het opent, met een laadscherm.',
      'Geluid met één knop: één volumeschuif en dempen.',
      'Een eigen opdracht volg je sneller: zolang hij niet klaar is, kijkt het HQ elke 20 seconden.',
      'Valt YouTube of vidIQ even weg, dan zie je de laatst bekende cijfers met de tijd erbij.',
    ],
  },
  {
    versie: 'v41',
    punten: [
      'Opdrachtbalk (toets K), mandje en Mijn opdrachten.',
      'Keuzeknoppen en antwoordveld bij vragen van Claude.',
      'Bestanden openen in de bestandenlezer en de Uploaddag.',
    ],
  },
];

const KEY = 'dm-versie-gezien';
/** de versie die deze browser het laatst zag (null: nog nooit) */
export function gezieneVersie(): string | null { try { return localStorage.getItem(KEY); } catch { return null; } }
export function markeerGezien(v = VERSIE) { try { localStorage.setItem(KEY, v); } catch { /* */ } }
const nr = (v: string) => parseInt(v.replace(/\D/g, ''), 10) || 0;
/** wat er nieuw is sinds de laatst geziene versie, tot en met de huidige */
export function nieuwSinds(gezien: string | null): Nieuw[] {
  const tot = nr(VERSIE); const vanaf = gezien ? nr(gezien) : tot - 1;
  return NIEUW.filter((n) => nr(n.versie) > vanaf && nr(n.versie) <= tot);
}
