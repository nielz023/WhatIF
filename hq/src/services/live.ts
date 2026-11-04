/**
 * LIVE: leest elke minuut de echte stand uit de projectbestanden
 * (driftmark-hq/status.json) via de `files`-capability. Claude en de threads
 * werken dat bestand bij zodra er iets verandert. Zonder toegang valt de
 * pagina terug op de ingebouwde stand uit data/driftmark.ts.
 */
import { create } from 'zustand';
import * as B from '../data/driftmark';

export interface Activity { title: string; id: string; state: string; last: string; doing?: string }
export interface Live {
  updated: string; channel: typeof B.CHANNEL; videos: B.RealVideo[]; shorts: B.ShortGroup[]; next: string[];
  ideas: typeof B.IDEAS; links: typeof B.LINKS; activity: Activity[];
}
const builtIn: Live = { updated: B.UPDATED, channel: B.CHANNEL, videos: B.VIDEOS, shorts: B.SHORTS, next: B.NEXT, ideas: B.IDEAS, links: B.LINKS, activity: [] };

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
          set({ data: { ...builtIn, ...j }, source: 'live', checkedAt: Date.now() });
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
export function startLive() {
  if (started) return; started = true;
  setTimeout(() => void useLive.getState().refresh(), 1500);
  setInterval(() => void useLive.getState().refresh(), 60000);
}
