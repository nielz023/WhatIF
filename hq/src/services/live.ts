/**
 * LIVE: leest elke minuut (elke 20 s als een eigen opdracht loopt) de echte stand uit de projectbestanden
 * (driftmark-hq/status.json) via de `files`-capability. Claude en de threads
 * werken dat bestand bij zodra er iets verandert. Zonder toegang valt de
 * pagina terug op de ingebouwde stand uit data/driftmark.ts.
 */
import { create } from 'zustand';
import * as B from '../data/driftmark';
import { useDb, startDb } from './db';
import { nieuwsteEerst, toonTijd } from '../lib/tijd';
import { useReal } from './real';

export interface Activity {
  title: string; id: string; state: string; last: string; doing?: string; video?: number; lastIso?: string;
  /** oude sessie-id van de thread (session_...); niet meer nodig, de thread-id (id) is de sleutel */
  session?: string;
  /** live: de stand komt uit de threads (driftmark-hq/gesprekken/threads.json, ongeveer elk uur bijgewerkt);
   *  needs: wat er voor niels klaarstaat; recent en checklist: alleen nog als status.json ze meegeeft */
  live?: boolean; needs?: string; recent?: string; checklist?: string;
  /** keuzeknoppen bij een vraag aan niels (verbeterlijst punt 5); bestand = plaatje of geluid erbij */
  keuzes?: { label: string; bestand?: string }[] | string[];
}
export interface Output { name: string; path: string; kind?: 'image' | 'video' | 'file' }
export interface Cost { datum: string; wat: string; bedrag?: number | null; credits?: string; notitie?: string }
/** Antwoord op een opdracht uit het HQ. ref = het kenmerk van de opdracht (o-xxxx); stand = waar hij staat;
 *  bestand = een projectbestand met het resultaat (opent in de bestandenlezer); link = een url (artifact, thread). */
export interface Reply { at: string; opdracht: string; antwoord: string; thread?: string; ref?: string; stand?: 'ontvangen' | 'bezig' | 'klaar' | 'fout'; bestand?: string; link?: string }
export interface Blender { stand: string; wachtrij: { naam: string; status: string }[] | string; bijgewerkt: string }
/** Eén video of short zoals hij op YouTube staat (automation/videos.py): weergaven en likes elk uur uit de
 *  openbare YouTube-feed, de rest elke ochtend uit vidIQ (YouTube Analytics, loopt 1 à 2 dagen achter). */
export interface YTVideo {
  id?: string; title: string; type?: 'long' | 'short'; status?: string; url?: string;
  date?: string; datum?: string; tijd?: string;
  views?: number; likes?: number; comments?: number; shares?: number;
  /** nieuwe abonnees door deze video */ subs?: number;
  /** gemiddelde kijkduur in seconden */ avd?: number;
  /** gemiddeld percentage bekeken */ avp?: number;
  /** weergaven waarbij echt gekeken is */ engaged?: number;
  /** totale kijktijd in minuten */ minuten?: number;
  viewsAt?: string; statsAt?: string;
}
export interface YT { subscribers?: number; views?: number; videoCount?: number; videos?: YTVideo[]; bron?: string; datum?: string; feedAt?: string; vidiqAt?: string; vidiqTot?: string }
export interface Live {
  updated: string; channel: typeof B.CHANNEL; videos: B.RealVideo[]; shorts: B.ShortGroup[]; next: string[];
  ideas: typeof B.IDEAS; links: typeof B.LINKS; activity: Activity[];
  outputs?: Record<string, Output[]>; costs?: Cost[]; replies?: Reply[]; blender?: Blender; youtube?: YT;
  /** stand van de verbeterpunten per studio (id + klaar), zie data/verbeter.ts */
  verbeter?: { id: string; klaar?: boolean; af?: string; studio?: string; tekst?: string }[];
  /** begin van het script dat nu in productie is (whiteboard in de scriptkamer) */
  script?: { video?: number; regels: string[] };
  /** sessie(s) van de coördinator (projectchat), nieuwste eerst */
  coordinator?: string[];
}
const builtIn: Live = { updated: B.UPDATED, channel: B.CHANNEL, videos: B.VIDEOS, shorts: B.SHORTS, next: B.NEXT, ideas: B.IDEAS, links: B.LINKS, activity: B.ACTIVITY, youtube: B.YOUTUBE };

/** Opschonen vóór gebruik (verbeterpunt 6 nov): één onvolledige regel in status.json of de
 *  database mag de HQ nooit leeg maken. Kapotte regels vallen weg, ontbrekende lijsten worden leeg,
 *  antwoorden staan met de nieuwste bovenaan en met overal dezelfde tijdnotatie. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const lijst = (x: any, reserve: any[] = []) => (Array.isArray(x) ? x : reserve);
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const obj = (x: any) => x && typeof x === 'object' && !Array.isArray(x);
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function schoon(j: any): Live {
  const d = { ...builtIn, ...(obj(j) ? j : {}) } as Live;
  d.activity = lijst(d.activity, builtIn.activity).filter((a: Activity) => obj(a) && typeof a.title === 'string' && typeof a.state === 'string')
    .map((a: Activity) => ({ ...a, id: typeof a.id === 'string' ? a.id : '', last: typeof a.last === 'string' ? a.last : '' }));
  d.videos = lijst(d.videos, builtIn.videos).filter((v: B.RealVideo) => obj(v) && typeof v.title === 'string')
    .map((v: B.RealVideo) => ({ ...v, steps: lijst(v.steps).filter(obj), notes: lijst(v.notes).filter((n: unknown) => typeof n === 'string') }));
  d.shorts = lijst(d.shorts, builtIn.shorts).filter(obj);
  d.next = lijst(d.next).filter((n: unknown) => typeof n === 'string');
  d.ideas = lijst(d.ideas, builtIn.ideas) as Live['ideas'];
  d.links = lijst(d.links, builtIn.links) as Live['links'];
  if (d.costs) d.costs = lijst(d.costs).filter(obj);
  if (d.replies) d.replies = nieuwsteEerst(lijst(d.replies).filter((r: Reply) => obj(r) && typeof r.antwoord === 'string')
    .map((r: Reply) => ({ ...r, opdracht: typeof r.opdracht === 'string' ? r.opdracht : '' }))).map((r) => ({ ...r, at: toonTijd(r.at) }));
  if (d.youtube && !obj(d.youtube)) d.youtube = builtIn.youtube;
  if (d.youtube?.videos) d.youtube = { ...d.youtube, videos: lijst(d.youtube.videos).filter((v: YTVideo) => obj(v) && typeof v.title === 'string') };
  return d;
}

/* ---------- BLIJFT WERKEN ALS IETS UITVALT (verbeterlijst punt 72) ----------
 * De laatst bekende YouTube-cijfers worden in deze browser bewaard. Mist de YouTube-feed of vidIQ in een
 * nieuwe stand (of is een lijst leeg), dan blijven de laatst bekende cijfers staan, met hun eigen tijd
 * (feedAt / vidiqAt), zodat de pagina's "bijgewerkt om …" tonen in plaats van een leeg vak of een nul. */
const LAATST = 'dm-laatst-yt';
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function metLaatst(raw: any, d: Live): Live {
  let oud: YT | null = null;
  try { oud = JSON.parse(localStorage.getItem(LAATST) || 'null'); } catch { oud = null; }
  const nieuw = obj(raw) && obj(raw.youtube) ? (d.youtube as YT) : null;
  const heeftCijfers = (y?: YT | null) => !!y && (y.subscribers != null || (y.videos?.length ?? 0) > 0);
  if (heeftCijfers(nieuw)) {
    const y = { ...nieuw! };
    if (oud) {
      // een deel ontbreekt (bv. vidIQ viel uit): dat deel uit de laatst bekende stand
      if (y.subscribers == null && oud.subscribers != null) { y.subscribers = oud.subscribers; y.vidiqAt = y.vidiqAt ?? oud.vidiqAt; }
      if (y.views == null && oud.views != null) y.views = oud.views;
      if (y.videoCount == null && oud.videoCount != null) y.videoCount = oud.videoCount;
      if (!(y.videos?.length) && oud.videos?.length) { y.videos = oud.videos; y.feedAt = y.feedAt ?? oud.feedAt; }
    }
    try { localStorage.setItem(LAATST, JSON.stringify(y)); } catch { /* vol of geblokkeerd: dan alleen zonder reserve */ }
    return { ...d, youtube: y };
  }
  if (heeftCijfers(oud)) return { ...d, youtube: { ...oud!, bron: oud!.bron ? `${oud!.bron} (laatst bekend)` : 'laatst bekend' } };
  return d;
}

type Src = 'ingebouwd' | 'live' | 'database' | 'geen-toegang' | 'fout';
interface S { data: Live; source: Src; checkedAt: number | null; refresh: () => Promise<void> }

const PATHS = ['driftmark-hq/status.json', '/driftmark-hq/status.json'];
// eslint-disable-next-line @typescript-eslint/no-explicit-any
let fs: any = undefined;

export const useLive = create<S>((set) => ({
  data: builtIn, source: 'ingebouwd', checkedAt: null,
  refresh: async () => {
    try {
      if (fs === undefined) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const c = (window as any).claude;
        fs = c?.use ? await c.use('files') : null;
      }
      if (!fs) { if (!fromDb()) set({ source: 'geen-toegang', checkedAt: Date.now() }); return; }
      let lastErr: unknown = null;
      for (const p of PATHS) {
        try {
          const r = await fs.read(p);
          const j = JSON.parse(new TextDecoder().decode(r.bytes));
          const data = metLaatst(j, schoon(j));
          set({ data, source: 'live', checkedAt: Date.now() });
          try { (await import('./sync')).applyReal(data); } catch (e) { console.warn('sync', e); }
          return;
        } catch (e) { lastErr = e; }
      }
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const code = (lastErr as any)?.code;
      if (fromDb()) return;
      set({ source: code === 'not_granted' ? 'geen-toegang' : 'fout', checkedAt: Date.now() });
    } catch { if (!fromDb()) set({ source: 'fout', checkedAt: Date.now() }); }
  },
}));

/** Reserve: de kopie uit de ingebouwde database (hq/state), als de projectbestanden niet te lezen zijn. */
function fromDb(): boolean {
  const st = useDb.getState().state as Partial<Live> | null;
  if (!st || !st.activity) return false;
  const data = metLaatst(st, schoon(st));
  useLive.setState({ data, source: 'database', checkedAt: Date.now() });
  void import('./sync').then((m) => m.applyReal(data)).catch(() => {});
  return true;
}
useDb.subscribe((s, p) => { if (s.state && s.state !== p.state && useLive.getState().source !== 'live') fromDb(); });

let started = false;
export async function readFile(path: string): Promise<Uint8Array> {
  if (!fs) throw new Error('geen toegang');
  return (await fs.read(path)).bytes;
}
export async function downloadFile(path: string) { if (fs) await fs.download(path); }
/** De files-capability, op dezelfde manier opgevraagd als hierboven (ook voor services/threads.ts).
 *  null: deze weergave kan de projectbestanden niet lezen. */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function filesApi(): Promise<any | null> {
  if (fs === undefined) {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const c = (window as any).claude;
      fs = c?.use ? await c.use('files') : null;
    } catch { return null; }
  }
  return fs;
}

/* ---------- BELANGRIJKE DINGEN DIRECT DOORZETTEN (verbeterlijst punt 71) ----------
 * Normaal: elke minuut. Zolang het tabblad zichtbaar is én een eigen opdracht nog niet klaar is: elke 20 s.
 * Tabblad op de achtergrond: elke 3 minuten. Terug naar het tabblad: meteen kijken als het langer dan 20 s geleden is.
 * Zo blijft de belasting op de bestanden-API klein (hooguit 3 keer per minuut, en alleen als er iets loopt). */
const SNEL = 20_000, NORMAAL = 60_000, ACHTERGROND = 180_000;
/** opdrachten die als "open" tellen: verstuurd in de laatste 12 uur en nog geen antwoord met stand klaar of fout */
export function openOpdrachten(): number {
  const replies = useLive.getState().data.replies ?? [];
  const nu = Date.now();
  return useReal.getState().orders.filter((o) => {
    if (o.status !== 'verstuurd' || !o.ref || nu - o.at > 12 * 3600_000) return false;
    const r = replies.find((x) => x.ref === o.ref);
    return !r || (r.stand !== 'klaar' && r.stand !== 'fout' && r.stand !== undefined);
  }).length;
}
export function pollTempo(): number {
  if (typeof document !== 'undefined' && document.hidden) return ACHTERGROND;
  return openOpdrachten() > 0 ? SNEL : NORMAAL;
}
let timer: ReturnType<typeof setTimeout> | null = null;
function plan(ms = pollTempo()) {
  if (timer) clearTimeout(timer);
  timer = setTimeout(async () => { await useLive.getState().refresh(); plan(); }, ms);
}

export function startLive() {
  if (started) return; started = true;
  void startDb();
  void import('./sync').then((m) => m.applyReal(builtIn, false));
  plan(1500);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) return;
    const c = useLive.getState().checkedAt;
    if (!c || Date.now() - c > SNEL) plan(300); else plan();
  });
  // net een opdracht verstuurd: binnen 20 s opnieuw kijken in plaats van pas na een minuut
  useReal.subscribe((s, p) => { if (s.orders !== p.orders && pollTempo() === SNEL) { const c = useLive.getState().checkedAt ?? 0; plan(Math.max(1000, SNEL - (Date.now() - c))); } });
}
