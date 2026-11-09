/**
 * DE AFDELINGEN VAN HET NEON-KANTOOR.
 * Elke ruimte is een echte afdeling van Driftmark. Welke threads (Claude-taken)
 * bij een afdeling horen, bepalen we uit de titel en de "doing"-regel in
 * status.json. De medewerker van een afdeling krijgt de status van die taken.
 */
import type { Activity } from '../services/live';
import type { DepartmentId, PageId } from '../types';

export type RoomId = 'onderzoek' | 'creatief' | 'script' | 'stem' | 'productie' | 'thumbnail' | 'publicatie' | 'ceo' | 'crisis' | 'coach';

export interface RoomDef {
  id: RoomId;
  naam: string;
  sub: string;
  icon: string;
  color: string;
  slot: number; // plek in de ring (0 = ingang vooraan, met de klok mee), -1 = midden (receptie)
  agent: string; // naam van de vaste medewerker
  rol: string;
  match: RegExp; // welke threads bij deze afdeling horen
  game?: DepartmentId | 'warroom'; // afdeling in het spel (Studio)
  page?: PageId; // waar de echte inhoud staat
  pageLabel?: string;
  props: 'research' | 'creative' | 'script' | 'voice' | 'production' | 'thumbnail' | 'publishing' | 'ceo' | 'crisis' | 'coach';
  voorbeeld: string; // voorbeeldopdracht
}

export const ROOMS: RoomDef[] = [
  { id: 'onderzoek', naam: 'Onderzoek', sub: 'Niches, trends & onderwerpen', icon: '🔎', color: '#20D9FF', slot: 6, agent: 'Onderzoeker', rol: 'Zoekt onderwerpen, analyseert concurrenten en comments', match: /onderzoek|analyse|ifology|niche|trend|kijkers van|meer weergaven|comments/i, game: 'research', page: 'coach', pageLabel: 'Onderzoek in de Coachkamer', props: 'research', voorbeeld: 'Onderzoek drie nieuwe video-onderwerpen die passen bij Driftmark.' },
  { id: 'creatief', naam: 'Creatief', sub: 'Ideeën, concepten & titels', icon: '💡', color: '#A855F7', slot: 7, agent: 'Bedenker', rol: 'Bedenkt ideeën, verlopen, titels en hooks', match: /verloop|idee|titel|concept|branding|kanaalnaam|banner|hook/i, game: 'creative', page: 'videos', pageLabel: "Ideeën bij Video's", props: 'creative', voorbeeld: 'Bedenk 5 titels voor de volgende video volgens de cursusregels.' },
  { id: 'ceo', naam: 'CEO & Statistieken', sub: 'Strategie & prestaties', icon: '👑', color: '#FACC15', slot: 5, agent: 'Analist', rol: 'Volgt cijfers, CTR en kijkduur en geeft strategie', match: /hq|hoofdscherm|kanaal|stats|statistiek|groei|cursus|werkwijze/i, game: 'ceo', page: 'kanaal', pageLabel: 'Kanaalcijfers', props: 'ceo', voorbeeld: 'Vergelijk mijn laatste vijf video\'s en shorts en noem de grootste verschillen.' },
  { id: 'publicatie', naam: 'Publicatie', sub: 'Upload, planning & SEO', icon: '🚀', color: '#398CFF', slot: 4, agent: 'Uploadplanner', rol: 'Titels, beschrijving, tags, shorts-planning', match: /upload|beschrijving|tags|shorts|publi|seo|plann/i, game: 'publishing', page: 'videos', pageLabel: "Video's & shorts", props: 'publishing', voorbeeld: 'Maak de uploadtekst (titel, beschrijving, tags, hoofdstukken) voor de volgende video.' },
  { id: 'script', naam: 'Script', sub: 'Scripts & verhaallijn', icon: '📝', color: '#FF6A3D', slot: 8, agent: 'Scriptschrijver', rol: 'Schrijft en controleert elk script', match: /script/i, game: 'script', page: 'videos', pageLabel: "Scripts bij Video's", props: 'script', voorbeeld: 'Analyseer de eerste 30 seconden van het script dat nu in productie is.' },
  { id: 'thumbnail', naam: 'Thumbnail', sub: 'Design & CTR', icon: '🖼️', color: '#FF7A24', slot: 2, agent: 'Thumbnailmaker', rol: 'Ontwerpt thumbnails en 3 varianten voor Test & compare', match: /thumbnail/i, game: 'thumbnail', page: 'videos', pageLabel: "Thumbnails bij Video's", props: 'thumbnail', voorbeeld: 'Maak drie thumbnailvarianten voor de volgende video.' },
  { id: 'stem', naam: 'Stem', sub: 'Voice-overs & audio', icon: '🎙️', color: '#21D6C4', slot: 9, agent: 'Stemregisseur', rol: 'Voice-overs en dialoog in ElevenLabs', match: /stem|voice|audio|elevenlabs|geluid|muziek/i, game: 'voice', page: 'videos', pageLabel: "Stemmen bij Video's", props: 'voice', voorbeeld: 'Controleer of alle stemregels van de video in productie klaar zijn.' },
  { id: 'coach', naam: 'Claude · Coach', sub: 'Je AI-command center', icon: '✨', color: '#FF7A24', slot: -1, agent: 'Claude', rol: 'Je CEO Coach: gesprek, briefing, doelen en beslissingen', match: /coach/i, page: 'coach', pageLabel: 'Coachkamer openen', props: 'coach', voorbeeld: 'Geef me een briefing: wat is vandaag het belangrijkste?' },
  { id: 'productie', naam: 'Productie', sub: 'Animatie, render & montage', icon: '🎬', color: '#FF4DB8', slot: 1, agent: 'Producent', rol: 'Cast, sets, animatie, renders en montage', match: /animeer|animatie|render|montage|cast|sets|personage|bijfiguren|props|blender|unreal|scène/i, game: 'production', page: 'videos', pageLabel: "Productie bij Video's", props: 'production', voorbeeld: 'Geef de stand van de renders van de video in productie.' },
  { id: 'crisis', naam: 'Crisiskamer', sub: 'Analyse & oplossingen', icon: '⚠️', color: '#FF3B4E', slot: 3, agent: 'Crisismanager', rol: 'Pakt fouten, vastgelopen taken en waarschuwingen op', match: /$^/, game: 'warroom', page: 'overzicht', pageLabel: 'Vandaag openen', props: 'crisis', voorbeeld: 'Controleer of er iets vastloopt of misgaat en los het op.' },
];

export const roomById = (id: RoomId | null | undefined) => ROOMS.find((r) => r.id === id) ?? null;

/** Wijs elke thread aan één afdeling toe (eerste match wint, productie vóór script bij "animeer"). */
export function roomOf(a: Activity): RoomId {
  if (a.state === 'failed' || a.state === 'stopped') return 'crisis';
  const t = `${a.title} ${a.doing ?? ''}`;
  const order: RoomId[] = ['thumbnail', 'productie', 'stem', 'publicatie', 'script', 'creatief', 'onderzoek', 'ceo', 'coach'];
  for (const id of order) if (roomById(id)!.match.test(a.title)) return id;
  for (const id of order) if (roomById(id)!.match.test(t)) return id;
  return 'ceo';
}

export type Status = 'werkt' | 'bezig' | 'wacht' | 'probleem' | 'offline' | 'klaar';
export const STATUS: Record<Status, { kleur: string; label: string }> = {
  werkt: { kleur: '#21D6A0', label: 'Aan het werk' },
  bezig: { kleur: '#398CFF', label: 'Bezig met een taak' },
  wacht: { kleur: '#FF9F1C', label: 'Wacht op jouw input' },
  probleem: { kleur: '#FF3B4E', label: 'Probleem' },
  offline: { kleur: '#64748B', label: 'Geen taak (offline)' },
  klaar: { kleur: '#4ADE80', label: 'Verbeterpunt klaar ✓' },
};

const recent = (a: Activity) => (a.lastIso ? Date.now() - new Date(a.lastIso).getTime() < 45 * 60e3 : false);

export function statusOf(list: Activity[]): Status {
  if (list.some((a) => a.state === 'failed')) return 'probleem';
  if (list.some((a) => a.state === 'blocked' || a.state === 'review_ready')) return 'wacht';
  const w = list.filter((a) => a.state === 'working');
  if (w.some(recent)) return 'werkt';
  if (w.length) return 'bezig';
  return 'offline';
}

export function threadsPerRoom(activity: Activity[]): Record<RoomId, Activity[]> {
  const out = Object.fromEntries(ROOMS.map((r) => [r.id, [] as Activity[]])) as Record<RoomId, Activity[]>;
  for (const a of activity) out[roomOf(a)].push(a);
  return out;
}

/* ---------- ring-indeling (zoals het referentiebeeld) ---------- */
export const SLOTS = 10; // 0 = trap/ingang vooraan
export const SPAN = (Math.PI * 2) / SLOTS;
export const R_HUB = 5.9; // receptie
export const R_IN = 6.9; // binnenrand van de afdelingen
export const R_OUT = 15.2; // buitenrand
export const R_BASE = 17.2;
export const slotAngle = (slot: number) => slot * SPAN; // 0 wijst naar de camera (+z)
/** middelpunt van een afdeling in wereldcoördinaten */
export function roomCenter(r: RoomDef): [number, number, number] {
  if (r.slot < 0) return [0, 0, 0];
  const a = slotAngle(r.slot), m = (R_IN + R_OUT) / 2;
  return [Math.sin(a) * m, 0, Math.cos(a) * m];
}
