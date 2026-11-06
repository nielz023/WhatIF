/**
 * VERBETERPUNTEN PER STUDIO (niels 2026-11-06: "bij elk kantoortje 3 agents bezig met het verbeteren
 * van elke studio", keuze A: in beeld, met echte verbeterpunten).
 * Dit zijn de punten uit het verbeterdocument (https://claude.ai/artifact/7LPwH7wdqamb5NrTxtVYLp),
 * verdeeld over de studio's. De 3 agents in een kantoor tonen de open punten van hun studio;
 * een punt dat af is wordt groen. De echte stand komt uit status.json (veld "verbeter"),
 * deze lijst is de reserve als dat bestand niet te lezen is.
 */
import type { RoomId } from '../world/rooms';

export interface Punt { id: string; studio: RoomId; tekst: string; klaar: boolean; af?: string }

const P = (studio: RoomId, items: [string, string][]): Punt[] => items.map(([id, tekst]) => ({ id, studio, tekst, klaar: false }));

export const PUNTEN: Punt[] = [
  ...P('ceo', [
    ['e1', 'Muur van roem met je thumbnails en views'],
    ['e2', 'Ochtendbriefing met 3 taken voor vandaag'],
    ['e3', 'Videokaarten: video 1 t/m 5 naast elkaar'],
    ['e4', 'Grafieken met een stip bij elke upload'],
    ['e5', 'Weekrapport op maandag'],
    ['e6', 'Confetti en applaus bij mijlpalen'],
  ]),
  ...P('onderzoek', [
    ['o1', 'Scherm met je best scorende shorts'],
    ['o2', 'Wekelijkse check van je concurrenten'],
    ['o3', 'Shorts-tabel met weergaven per short'],
    ['o4', 'Echte Studio-cijfers zodra een koppeling het toelaat'],
    ['o5', 'Stad met gebouwen en ramen die aan en uit gaan'],
  ]),
  ...P('creatief', [
    ['c1', 'Ideeënbord: slepen met een coach-score'],
    ['c2', 'Scherm met de nieuwste ideeën'],
    ['c3', 'Praat met een afdeling'],
    ['c4', "Thema's Nacht, Dag en Feest, sneeuw in december"],
  ]),
  ...P('script', [
    ['s1', 'Whiteboard met het script van video 4'],
    ['s2', 'Hook-check: de eerste 5 seconden van elk script'],
    ['s3', 'Notities per afdeling'],
    ['s4', "Post-its en props: bekers, koptelefoons, kabels"],
    ['s5', 'Focusmodus: alleen jouw taken'],
  ]),
  ...P('stem', [
    ['v1', 'Golfvorm-scherm met de stand van de stemmen'],
    ['v2', 'Kantoorgeluid met een eigen volumeknop'],
    ['v3', 'Popfilter, koptelefoons en een dansende speaker'],
  ]),
  ...P('productie', [
    ['r1', 'Lopende band met een pakketje per video'],
    ['r2', 'Medewerkers die lopen, typen en mappen brengen'],
    ['r3', 'Licht in 8K gebakken en scherpere materialen'],
    ['r4', 'Renderpaneel met schijfruimte'],
    ['r5', 'Lucht en licht volgen de tijd van de dag'],
    ['r6', 'Laadscherm met logo en voortgang'],
  ]),
  ...P('thumbnail', [
    ['t1', 'Scherm: nieuwste thumbnail tegen je vorige'],
    ['t2', 'Thumbnails naast elkaar met CTR-voorspelling'],
    ['t3', 'Thumbnails op de schermen in het kantoor'],
  ]),
  ...P('publicatie', [
    ['p1', 'Scherm met wat er als volgende online gaat'],
    ['p2', 'Automatische 48-uurcheck na elke upload'],
    ['p3', 'Opdrachtenlijst met de stand per opdracht'],
    ['p4', 'Meldingen als iets klaar is of misgaat'],
    ['p5', 'Panelen schuiven in vanaf de afdeling'],
  ]),
  ...P('crisis', [
    ['k1', 'Rood zwaailicht en sirene met de oorzaak'],
    ['k2', 'Alarm bij een vastgelopen render of volle schijf'],
    ['k3', 'Automatisch terug van 4K als het hapert'],
    ['k4', 'Snellere versie voor je telefoon'],
  ]),
];

/** De punten van één studio: eerst de open punten (in volgorde), dan de afgeronde. */
export function puntenVoor(studio: RoomId, lijst: Punt[] = PUNTEN): Punt[] {
  const mine = lijst.filter((p) => p.studio === studio);
  return [...mine.filter((p) => !p.klaar), ...mine.filter((p) => p.klaar)];
}

/** Voeg de stand uit status.json samen met de ingebouwde lijst (status.json wint). */
export function mergePunten(liveIn?: { id?: string; klaar?: boolean; af?: string; studio?: string; tekst?: string }[] | null): Punt[] {
  const live = liveIn as Partial<Punt>[] | null | undefined;
  if (!Array.isArray(live) || !live.length) return PUNTEN;
  const byId = new Map(live.filter((p) => p && p.id).map((p) => [p.id!, p]));
  const out = PUNTEN.map((p) => ({ ...p, ...(byId.get(p.id) ?? {}) }) as Punt);
  for (const p of live) if (p?.id && p.studio && p.tekst && !PUNTEN.some((q) => q.id === p.id)) out.push({ klaar: false, ...p } as Punt);
  return out;
}
