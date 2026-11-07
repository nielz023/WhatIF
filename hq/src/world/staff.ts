/**
 * WIE ZIT ER IN ELK KANTOOR (niels 2026-11-06).
 * - "alle medewerkers zien eruit als het hoofdpersonage, maar ieder poppetje met een eigen stijl";
 *   kleding in de afdelingskleur. Het hoofdpersonage zelf (oranje hoodie, kaal) is de CEO.
 * - "bij elk kantoortje 3 agents bezig met het verbeteren van elke studio" (keuze A): elke agent toont
 *   een echt verbeterpunt van zijn studio en wordt groen als het af is. In de crisiskamer staat de derde
 *   bij het grote scherm (daar zijn maar twee bureaus).
 * - Wacht een echte thread van die afdeling op niels of loopt er iets mis, dan laat de eerste agent dat zien.
 * - De vaste cast van de video's (niels 2026-11-07) helpt mee waar het werk is: in de stemcabine bij de stemmen
 *   (om de beurt aan de microfoon), bij de briefing in de scriptkamer, in de crisiskamer als er iets mis is, voor de
 *   camera in de productiekamer en bij de fotoshoot in de thumbnailkamer (vooral het hoofdpersonage, de CEO).
 *   Zonder klus zijn ze boven in de kantine en de gamekamer.
 */
import type { CastAct, CrewMember, Look } from './crew';
import type { RealVideo } from '../data/driftmark';
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

/* ---------- de vaste cast van de video's ---------- */
const CAST: { id: string; label: string; look: Look; small?: boolean }[] = [
  { id: 'moeder', label: 'Moeder', look: { top: 'trui', topColor: '#E8739E', hair: 'lang', hairColor: '#8A5A2B', pants: '#3B4466', shoes: '#F4F1EA' } },
  { id: 'vader', label: 'Vader', look: { top: 'tee', topColor: '#F2A93B', hair: 'kort', hairColor: '#4A3424', beard: true, glasses: '#1C1F2B', pants: '#2E3B4E', shoes: '#8B5A2B' } },
  { id: 'broertje', label: 'Broertje', small: true, look: { top: 'hoodie', topColor: '#3FB8F0', hair: 'kuif', hairColor: '#5A3A1E', pants: '#2B3A5C', shoes: '#E23B3B' } },
  { id: 'opa', label: 'Opa', look: { top: 'jas', topColor: '#6E5A44', innerColor: '#E9E4D8', hair: 'pet', hatColor: '#5B5248', hairColor: '#DADAE0', moustache: true, glasses: '#3A3226', pants: '#4A4F5E', shoes: '#1C1F2B' } },
  { id: 'oma', label: 'Oma', look: { top: 'trui', topColor: '#9B7BC8', hair: 'krul', hairColor: '#E4E4EA', glasses: '#B0B4C4', pants: '#5B4A6E', shoes: '#F4F1EA' } },
  { id: 'vriend', label: 'Beste vriend', look: { top: 'hoodie', topColor: '#2FBF71', hair: 'pet', hatColor: '#E23B3B', hairColor: '#17120F', pants: '#1F2433', shoes: '#F4F1EA' } },
  { id: 'pestkop', label: 'Pestkop', look: { top: 'jas', topColor: '#262A36', innerColor: '#C0392B', hair: 'kuif', hairColor: '#17120F', pants: '#1F2433', shoes: '#1C1F2B' } },
];
type Job = 'crisis' | 'stem' | 'script' | 'thumbnail' | 'productie';
interface Place { u: number; v: number; fu: number; fv: number; act: CastAct; fixed?: boolean; doing: string }
/** plekken per klus (u langs de ring, v naar buiten; fu/fv = waar ze naar kijken). De eerste van de fotoshoot is voor het hoofdpersonage. */
const PLACES: Record<Job, Place[]> = {
  crisis: [[-1.4, -1.5], [-0.6, -1.85], [0.2, -1.5], [-0.6, -1.15]].map(([u, v]) => ({ u, v, fu: 0, fv: 3.95, act: 'listen' as CastAct, doing: 'helpt in de crisiskamer' })),
  stem: [
    { u: 0, v: 2.78, fu: 0, fv: 2.0, act: 'mic', fixed: true, doing: 'neemt zijn tekst op in de stemcabine' },
    { u: -2.0, v: 1.75, fu: 0, fv: 2.3, act: 'listen', doing: 'wacht op zijn beurt in de stemcabine' },
    { u: -2.05, v: 2.6, fu: 0, fv: 2.3, act: 'listen', doing: 'wacht op zijn beurt in de stemcabine' },
    { u: 1.75, v: 1.75, fu: 0, fv: 2.3, act: 'listen', doing: 'wacht op zijn beurt in de stemcabine' },
  ],
  script: [[-2.75, 1.6], [-2.0, 1.42], [-1.28, 1.62]].map(([u, v]) => ({ u, v, fu: -2.05, fv: 2.8, act: 'listen' as CastAct, doing: 'krijgt de briefing van het nieuwe script' })),
  thumbnail: [
    { u: 0, v: 3.2, fu: 0, fv: 2.3, act: 'pose', doing: 'poseert voor de thumbnail' },
    { u: -1.05, v: 3.1, fu: 0, fv: 2.3, act: 'pose', doing: 'poseert voor de thumbnail' },
    { u: 1.05, v: 3.1, fu: 0, fv: 2.3, act: 'pose', doing: 'poseert voor de thumbnail' },
  ],
  productie: [[-2.5, 2.25], [-1.75, 2.5], [-1.0, 2.25]].map(([u, v]) => ({ u, v, fu: -1.75, fv: 1.55, act: 'act' as CastAct, doing: 'speelt een scène voor de camera' })),
};
/** zonder klus: boven in kleine groepjes (kantine-kant en lounge) */
const BOVEN: [V2, V2][] = [
  [[5.7, -2.5], [6.1, -1.0]], [[6.5, -1.6], [6.1, -1.0]], [[2.2, 6.9], [2.4, 6.0]], [[3.0, 6.3], [2.4, 6.0]], [[1.7, 6.0], [2.4, 6.0]],
  [[-4.9, 4.9], [-4.6, 5.6]], [[-4.3, 6.3], [-4.6, 5.6]],
];
const STEP_JOB: Record<string, Job> = { Script: 'script', Stemmen: 'stem', Cast: 'productie', Sets: 'productie', Animatie: 'productie', Render: 'productie', Montage: 'productie' };
const working = (l?: Activity[]) => !!l?.some((a) => a.state === 'working' || a.state === 'review_ready' || a.state === 'blocked');
/** welke klussen er nu zijn, belangrijkste eerst */
export function castJobs(per: Record<RoomId, Activity[]>, all: Activity[], videos: RealVideo[]): Job[] {
  const steps = new Set<Job>();
  for (const v of videos) {
    if (v.status === 'Online' || v.steps.every((x) => x.done)) continue;
    for (const st of v.steps) if (st.active && STEP_JOB[st.label]) steps.add(STEP_JOB[st.label]);
  }
  const out: Job[] = [];
  if (statusOf(per.crisis ?? []) === 'probleem' || all.some((a) => a.state === 'failed')) out.push('crisis');
  for (const j of ['stem', 'script', 'thumbnail', 'productie'] as Job[]) if (steps.has(j) || working(per[j])) out.push(j);
  return out;
}

/** De medewerkers van het echte kantoor (Home). `at` geeft een plek in een afdeling (u langs de ring, v naar buiten). */
export function staffFor(opts: {
  per: Record<RoomId, Activity[]>; all: Activity[]; punten: Punt[]; seats: Record<string, V3[]>; videos?: RealVideo[];
  at: (room: RoomId, u: number, v: number) => V2; onOpen: (room: RoomId) => void;
}): CrewMember[] {
  const { per, all, punten, seats, at, onOpen } = opts;
  const out: CrewMember[] = [];
  const jobs = castJobs(per, all, opts.videos ?? []);
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
      // bij de fotoshoot voor een thumbnail staat hij zelf voor de camera
      const shoot = jobs.includes('thumbnail') ? PLACES.thumbnail[0] : null;
      out.push({ key: 'ceo:main', room: r.id, seat: 0, status: company, label: 'Hoofdpersonage (CEO)', role: 'Driftmark', look: CEO_LOOK, big: true, thread: t ? `${t.title}${t.state === 'blocked' || t.state === 'review_ready' ? ' (wacht op jou)' : ''}` : undefined, onClick: open,
        ...(shoot ? { standAt: { p: at('thumbnail', shoot.u, shoot.v), face: at('thumbnail', shoot.fu, shoot.fv) }, act: shoot.act, stay: true, doing: shoot.doing } : {}) });
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
  // de cast: de klussen af in volgorde van belang, de rest boven
  const free = jobs.flatMap((j) => PLACES[j].map((p, k) => ({ j, p, k }))).filter((x) => !(x.j === 'thumbnail' && x.k === 0));
  CAST.forEach((c, i) => {
    const slot = free[i]; const base = { key: `cast:${c.id}`, seat: -1, label: c.label, role: "Cast van de video's", small: c.small, onClick: () => onOpen(slot ? (slot.j as RoomId) : 'coach') };
    if (slot) {
      const { j, p } = slot; const room = j as RoomId;
      out.push({ ...base, room, status: 'werkt', look: j === 'stem' ? { ...c.look, headphones: '#1C1F2B' } : c.look,
        standAt: { p: at(room, p.u, p.v), face: at(room, p.fu, p.fv), fixed: p.fixed }, act: p.act, stay: true, doing: p.doing });
    } else {
      const [pp, face] = BOVEN[i % BOVEN.length];
      out.push({ ...base, room: 'coach', status: 'offline', look: c.look, standAt: { p: pp, face, fl: 1 }, act: 'chat', guest: true, doing: 'kletst boven in de kantine' });
    }
  });
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
