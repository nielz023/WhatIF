/**
 * VERSIE EN "WAT IS NIEUW" (verbeterlijst punt 70).
 * Eén plek voor het versienummer (rechtsonder in beeld) en de lijst met wijzigingen.
 * Bij een nieuwe versie: VERSIE ophogen en bovenaan NIEUW een blok toevoegen. Het venster
 * "Wat is nieuw" verschijnt dan één keer per browser (onthouden in localStorage).
 */
export const VERSIE = 'v44';

export interface Nieuw { versie: string; datum?: string; punten: string[] }

export const NIEUW: Nieuw[] = [
  { versie: 'v44', datum: '9 nov', punten: ['Het 3D-kantoor vult nu echt het hele scherm: de tekening bleef soms op een oude, smallere maat staan, waardoor rechts zwart bleef.'] },
  {
    versie: 'v42',
    datum: '9 nov',
    punten: [
      "Video's: per video de hele productielijn met 'volgende stap starten', renders live volgen, grote thumbnails, scriptlezer met tijdlijn, stemmenpaneel en thumbnailmuur.",
      'Kanaal: mooiere grafieken met je uploads als stipjes, een videorapport per video, doelen met prognose en het weekrapport. Bij elk cijfer staat de bron en de tijd.',
      'Klikratio uit een Studio-screenshot, uploadplanning en een ideeënbus.',
      '3D-kantoor in de glans-look, met jouw hoofdpersonage als CEO en de cast van je video\'s als team, plus rijdende auto\'s in de stad.',
      'Elke afdeling dezelfde opbouw: wat ze doet, wat loopt, wat op jou wacht, wat klaar is en snelknoppen. Met onderwerpenbord, titellab en scènebord.',
      'De coach als zijpaneel op elke pagina; de crisiskamer verschijnt alleen als er echt iets mis is.',
      'Kennis: vaste afspraken aanpassen, besluitenlogboek, versies van scripts vergelijken, zoeken met de toets /.',
      'Nieuwe huisstijl met Driftmark-logo, sneller openen (3D laadt pas als je het opent) en één volumeknop.',
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
