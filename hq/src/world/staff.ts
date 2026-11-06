/**
 * WIE ZIT ER IN ELK KANTOOR (niels 2026-11-06).
 * - "alle medewerkers zien eruit als het hoofdpersonage, maar ieder poppetje met een eigen stijl";
 *   kleding in de afdelingskleur. Het hoofdpersonage zelf (oranje hoodie, kaal) is de CEO.
 * - "bij elk kantoortje 3 agents bezig met het verbeteren van elke studio" (keuze A): elke agent toont
 *   een echt verbeterpunt van zijn studio en wordt groen als het af is. In de crisiskamer staat de derde
 *   bij het grote scherm (daar zijn maar twee bureaus).
 * - Wacht een echte thread van die afdeling op niels of loopt er iets mis, dan laat de eerste agent dat zien.
 */
import type { CrewMember, Look } from './crew';
import { hash } from './crew';
import { ROOMS, statusOf, type RoomId, type Status } from './rooms';
import type { Activity } from '../services/live';
import { puntenVoor, type Punt } from '../data/verbeter';
import type { Agent } from '../types';

type V2 = [number, number];
type V3 = [number, number, number];

/** het hoofdpersonage van de video's (maten en kleuren uit hoofdpersonage.glb) */
export const CEO_LOOK: Look = { top: 'hoodie', topColor: '#EB7A2B', hair: 'kaal', hairColor: '#2B1D14', pants: '#3E4150', shoes: '#F4F1EA' };

const STYLE: Record<string, [string, Omit<Look, 'pants' | 'shoes'>][]> = {
  ceo: [
    ['Analytics Agent', { top: 'jas', topColor: '#E0B10E', innerColor: '#F3F4F8', hair: 'kort', hairColor: '#17120F', glasses: '#1C1F2B' }],
    ['Strategie Agent', { top: 'shirt', topColor: '#FACC15', innerColor: '#FACC15', hair: 'knot', hairColor: '#7A4A22' }],
    ['Groei Agent', { top: 'trui', topColor: '#FACC15', hair: 'pet', hatColor: '#1F2433', hairColor: '#2B1D14', beard: true }],
  ],
  onderzoek: [
    ['Research Agent', { top: 'hoodie', topColor: '#20D9FF', hair: 'kuif', hairColor: '#2B1D14', glasses: '#1C1F2B' }],
    ['Trend Agent', { top: 'tee', topColor: '#20D9FF', hair: 'krul', hairColor: '#17120F', headphones: '#1C1F2B' }],
    ['Concurrentie Agent', { top: 'trui', topColor: '#17B5D6', hair: 'muts', hatColor: '#20D9FF', hairColor: '#2B1D14', beard: true }],
  ],
  creatief: [
    ['Creative Agent', { top: 'jas', topColor: '#A855F7', innerColor: '#F3F4F8', hair: 'lang', hairColor: '#D9A441' }],
    ['Titel Agent', { top: 'hoodie', topColor: '#A855F7', hair: 'pet', hatColor: '#FF7A24', hairColor: '#17120F' }],
    ['Concept Agent', { top: 'tee', topColor: '#A855F7', hair: 'kaal', hairColor: '#3A2A20', beard: true, glasses: '#FF7A24' }],
  ],
  script: [
    ['Script Agent', { top: 'trui', topColor: '#FF6A3D', hair: 'kort', hairColor: '#B8B8C0', glasses: '#1C1F2B', moustache: true }],
    ['Hook Agent', { top: 'shirt', topColor: '#FF6A3D', innerColor: '#FF6A3D', hair: 'knot', hairColor: '#2B1D14' }],
    ['Redactie Agent', { top: 'hoodie', topColor: '#FF6A3D', hair: 'muts', hatColor: '#1F2433', hairColor: '#7A4A22' }],
  ],
  stem: [
    ['Voice Agent', { top: 'hoodie', topColor: '#21D6C4', hair: 'krul', hairColor: '#2B1D14', headphones: '#1C1F2B' }],
    ['Audio Agent', { top: 'tee', topColor: '#21D6C4', hair: 'kaal', hairColor: '#3A2A20', headphones: '#FF7A24', beard: true }],
    ['Mix Agent', { top: 'jas', topColor: '#1DBFAE', innerColor: '#1F2433', hair: 'lang', hairColor: '#17120F' }],
  ],
  productie: [
    ['Production Agent', { top: 'hoodie', topColor: '#FF4DB8', hair: 'pet', hatColor: '#1F2433', hairColor: '#2B1D14', beard: true }],
    ['Animatie Agent', { top: 'trui', topColor: '#FF4DB8', hair: 'kuif', hairColor: '#E26D2C', glasses: '#1C1F2B' }],
    ['Render Agent', { top: 'tee', topColor: '#FF4DB8', hair: 'knot', hairColor: '#17120F', headphones: '#20D9FF' }],
  ],
  thumbnail: [
    ['Thumbnail Agent', { top: 'jas', topColor: '#FF7A24', innerColor: '#F3F4F8', hair: 'kuif', hairColor: '#17120F', glasses: '#1C1F2B' }],
    ['Design Agent', { top: 'tee', topColor: '#FF7A24', hair: 'lang', hairColor: '#7A4A22' }],
    ['CTR Agent', { top: 'trui', topColor: '#FF8F45', hair: 'muts', hatColor: '#398CFF', hairColor: '#2B1D14', moustache: true }],
  ],
  publicatie: [
    ['Publishing Agent', { top: 'shirt', topColor: '#398CFF', innerColor: '#398CFF', hair: 'kort', hairColor: '#2B1D14', glasses: '#1C1F2B' }],
    ['SEO Agent', { top: 'hoodie', topColor: '#398CFF', hair: 'krul', hairColor: '#D9A441' }],
    ['Planning Agent', { top: 'jas', topColor: '#398CFF', innerColor: '#F3F4F8', hair: 'kaal', hairColor: '#3A2A20', moustache: true, beard: true }],
  ],
  crisis: [
    ['Crisis Manager', { top: 'jas', topColor: '#FF3B4E', innerColor: '#1F2433', hair: 'kort', hairColor: '#17120F', headphones: '#1C1F2B' }],
    ['Monitor Agent', { top: 'hoodie', topColor: '#FF3B4E', hair: 'pet', hatColor: '#1F2433', hairColor: '#2B1D14' }],
    ['Herstel Agent', { top: 'trui', topColor: '#FF3B4E', hair: 'knot', hairColor: '#B8B8C0', glasses: '#1C1F2B' }],
  ],
};
const PANTS = ['#2B3A5C', '#3E4150', '#1F2433', '#6B5B45', '#4A4F5E', '#2E3B4E', '#5B4A6E'];
const SHOES = ['#F4F1EA', '#1C1F2B', '#8B5A2B', '#F4F1EA', '#E9EDF5'];

const rank = (a: Activity) => (a.state === 'failed' ? 4 : a.state === 'blocked' ? 3 : a.state === 'review_ready' ? 2 : a.state === 'working' ? 1 : 0);
/** de thread die er voor niels het meest toe doet (mislukt > wacht op jou > bezig), nieuwste eerst */
function topThread(list: Activity[]) {
  return [...list].filter((a) => rank(a) > 0).sort((a, b) => rank(b) - rank(a) || (b.lastIso ?? '').localeCompare(a.lastIso ?? ''))[0];
}

/** De medewerkers van het echte kantoor (Home). `at` geeft een plek in een afdeling (u langs de ring, v naar buiten). */
export function staffFor(opts: {
  per: Record<RoomId, Activity[]>; all: Activity[]; punten: Punt[]; seats: Record<string, V3[]>;
  at: (room: RoomId, u: number, v: number) => V2; onOpen: (room: RoomId) => void;
}): CrewMember[] {
  const { per, all, punten, seats, at, onOpen } = opts;
  const out: CrewMember[] = [];
  for (const r of ROOMS) {
    if (r.slot < 0 || !STYLE[r.id]) continue;
    const list = per[r.id] ?? []; const st = statusOf(list); const top = topThread(list);
    const tasks = puntenVoor(r.id, punten);
    const nSeats = seats[r.id]?.length ?? 0;
    const open = () => onOpen(r.id);
    let first = 0;
    if (r.id === 'ceo') {
      // het hoofdpersonage: zijn status is die van het hele bedrijf (wacht er iets op niels, dan oranje)
      const cs = statusOf(all); const company: Status = cs === 'offline' ? 'bezig' : cs;
      const t = topThread(all);
      out.push({ key: 'ceo:main', room: r.id, seat: 0, status: company, label: 'Hoofdpersonage (CEO)', role: 'Driftmark', look: CEO_LOOK, big: true, thread: t ? `${t.title}${t.state === 'blocked' || t.state === 'review_ready' ? ' (wacht op jou)' : ''}` : undefined, onClick: open });
      first = 1;
    }
    STYLE[r.id].forEach(([name, look], k) => {
      const seat = first + k; const task = tasks[k];
      const stander = seat >= nSeats; // geen bureau meer vrij: staat bij het grote scherm
      if (stander && r.id !== 'crisis') return;
      const lead = k === 0 && r.id !== 'ceo';
      const status: Status = lead && (st === 'wacht' || st === 'probleem') ? st : task?.klaar ? 'klaar' : 'bezig';
      const i = r.slot * 3 + k;
      out.push({
        key: `${r.id}:${k}`, room: r.id, seat: stander ? -1 : seat, status, label: name, role: r.naam,
        task: task?.tekst, taskDone: !!task?.klaar, thread: lead && top ? top.title : undefined,
        look: { ...look, pants: PANTS[(i * 5 + 1) % PANTS.length], shoes: SHOES[(i * 3 + k) % SHOES.length] } as Look,
        big: lead, onClick: open,
        ...(stander ? { standAt: { p: at(r.id, 0.35, 2.85), face: at(r.id, 0, 3.95) } } : {}),
      });
    });
  }
  return out;
}

const TOPS: Look['top'][] = ['hoodie', 'trui', 'tee', 'jas', 'shirt'];
const HAIR: Look['hair'][] = ['kort', 'kuif', 'krul', 'knot', 'lang', 'muts', 'pet', 'kaal'];
const HCOL = ['#2B1D14', '#17120F', '#7A4A22', '#D9A441', '#B8B8C0', '#E26D2C'];
const GAME_STATUS: Record<string, Status> = { working: 'werkt', meeting: 'bezig', training: 'wacht', idle: 'offline' };

/** Studio (het spel): de spelers-agents, ook als het hoofdpersonage met een eigen stijl. */
export function gameStaff(agents: Agent[], onPick: (id: string) => void): CrewMember[] {
  const out: CrewMember[] = [];
  for (const r of ROOMS) {
    if (r.slot < 0 || !r.game || r.game === 'warroom') continue;
    agents.filter((a) => a.department === r.game).slice(0, 4).forEach((a, k) => {
      const h = hash(a.id); const h2 = hash(a.id + 'x');
      out.push({
        key: `g:${a.id}`, room: r.id, seat: k, status: GAME_STATUS[a.state] ?? 'bezig', label: a.name, role: r.naam,
        look: {
          top: TOPS[Math.floor(h * TOPS.length)], topColor: a.avatar.shirt, innerColor: r.color,
          hair: HAIR[Math.floor(h2 * HAIR.length)], hairColor: HCOL[Math.floor(h * 97) % HCOL.length], hatColor: r.color,
          glasses: h2 > 0.7 ? '#1C1F2B' : undefined, beard: h > 0.8, headphones: r.id === 'stem' ? '#1C1F2B' : undefined,
          pants: PANTS[Math.floor(h2 * 53) % PANTS.length], shoes: SHOES[Math.floor(h * 31) % SHOES.length],
        },
        onClick: () => onPick(a.id),
      });
    });
  }
  return out;
}

/** Het team van één studio voor het afdelingspaneel: wie zit er, waar werkt hij aan, en is het al af. */
export interface TeamRow { name: string; task?: string; done: boolean; color: string; main?: boolean }
export function teamFor(room: RoomId, punten: Punt[]): TeamRow[] {
  const tasks = puntenVoor(room, punten); const rows: TeamRow[] = [];
  if (room === 'ceo') rows.push({ name: 'Hoofdpersonage (CEO)', done: false, color: CEO_LOOK.topColor, main: true });
  (STYLE[room] ?? []).forEach(([name, look], k) => rows.push({ name, task: tasks[k]?.tekst, done: !!tasks[k]?.klaar, color: look.top === 'shirt' ? (look.innerColor ?? look.topColor) : look.topColor }));
  return rows;
}
