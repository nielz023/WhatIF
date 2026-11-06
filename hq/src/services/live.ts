/**
 * LIVE: leest elke minuut de echte stand uit de projectbestanden
 * (driftmark-hq/status.json) via de `files`-capability. Claude en de threads
 * werken dat bestand bij zodra er iets verandert. Zonder toegang valt de
 * pagina terug op de ingebouwde stand uit data/driftmark.ts.
 */
import { create } from 'zustand';
import * as B from '../data/driftmark';
import { useDb, startDb } from './db';

export interface Activity {
  title: string; id: string; state: string; last: string; doing?: string; video?: number; lastIso?: string;
  /** sessie van de thread bij Claude Code Remote (session_...), voor de live stand en het hele gesprek */
  session?: string;
  /** live uit de connector: staat er iets voor niels klaar, wat deed Claude net, en de checklist */
  live?: boolean; needs?: string; recent?: string; checklist?: string;
}
export interface Output { name: string; path: string; kind?: 'image' | 'video' | 'file' }
export interface Cost { datum: string; wat: string; bedrag?: number | null; credits?: string; notitie?: string }
export interface Reply { at: string; opdracht: string; antwoord: string; thread?: string }
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
          const data = { ...builtIn, ...j };
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
  const data = { ...builtIn, ...st } as Live;
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

export function startLive() {
  if (started) return; started = true;
  void startDb();
  void import('./sync').then((m) => m.applyReal(builtIn));
  setTimeout(() => void useLive.getState().refresh(), 1500);
  setInterval(() => void useLive.getState().refresh(), 60000);
}
