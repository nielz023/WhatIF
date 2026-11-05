/**
 * LIVE: leest elke minuut de echte stand uit de projectbestanden
 * (driftmark-hq/status.json) via de `files`-capability. Claude en de threads
 * werken dat bestand bij zodra er iets verandert. Zonder toegang valt de
 * pagina terug op de ingebouwde stand uit data/driftmark.ts.
 */
import { create } from 'zustand';
import * as B from '../data/driftmark';

export interface Activity { title: string; id: string; state: string; last: string; doing?: string }
export interface Output { name: string; path: string; kind?: 'image' | 'video' | 'file' }
export interface Cost { datum: string; wat: string; bedrag?: number | null; credits?: string; notitie?: string }
export interface Reply { at: string; opdracht: string; antwoord: string; thread?: string }
export interface Blender { stand: string; wachtrij: { naam: string; status: string }[]; bijgewerkt: string }
export interface YT { subscribers?: number; views?: number; videos?: { title: string; views?: number; date?: string; type?: 'long' | 'short' }[]; bron?: string; datum?: string }
export interface Live {
  updated: string; channel: typeof B.CHANNEL; videos: B.RealVideo[]; shorts: B.ShortGroup[]; next: string[];
  ideas: typeof B.IDEAS; links: typeof B.LINKS; activity: Activity[];
  outputs?: Record<string, Output[]>; costs?: Cost[]; replies?: Reply[]; blender?: Blender; youtube?: YT;
}
const builtIn: Live = { updated: B.UPDATED, channel: B.CHANNEL, videos: B.VIDEOS, shorts: B.SHORTS, next: B.NEXT, ideas: B.IDEAS, links: B.LINKS, activity: B.ACTIVITY, youtube: B.YOUTUBE };

type Src = 'ingebouwd' | 'live' | 'geen-toegang' | 'fout';
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
      if (!fs) { set({ source: 'geen-toegang', checkedAt: Date.now() }); return; }
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
      set({ source: code === 'not_granted' ? 'geen-toegang' : 'fout', checkedAt: Date.now() });
    } catch { set({ source: 'fout', checkedAt: Date.now() }); }
  },
}));

let started = false;
export async function readFile(path: string): Promise<Uint8Array> {
  if (!fs) throw new Error('geen toegang');
  return (await fs.read(path)).bytes;
}
export async function downloadFile(path: string) { if (fs) await fs.download(path); }

export function startLive() {
  if (started) return; started = true;
  void import('./sync').then((m) => m.applyReal(builtIn));
  setTimeout(() => void useLive.getState().refresh(), 1500);
  setInterval(() => void useLive.getState().refresh(), 60000);
}
