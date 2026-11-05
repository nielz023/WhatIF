/**
 * DATABASE: de ingebouwde database van het HQ (db-capability).
 * - hq/state   : kopie van status.json (reserve als de projectbestanden niet te lezen zijn)
 * - hq/engine  : stand van de automatische routine (laatste/volgende run, controles)
 * - stats/*    : cijfergeschiedenis, één document per uur
 * - log/*      : logboek van de automatisering (info, waarschuwing, fout)
 * De routine "Driftmark HQ automatisering" schrijft dit elk uur. De pagina leest alleen.
 */
import { create } from 'zustand';

export interface StatRow { at: string; subscribers?: number; views?: number; videoCount?: number }
export interface LogRow { at: string; kind: 'info' | 'waarschuwing' | 'fout'; text: string }
export interface Engine { lastRun?: string; nextRun?: string; status?: string; checks?: { naam: string; ok: boolean; notitie?: string }[] }
interface S { ready: boolean; offline: boolean; stats: StatRow[]; log: LogRow[]; engine: Engine | null; state: Record<string, unknown> | null }

export const useDb = create<S>(() => ({ ready: false, offline: false, stats: [], log: [], engine: null, state: null }));

let started = false;
export async function startDb() {
  if (started) return; started = true;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const c = (window as any).claude;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let db: any = null;
  try { db = c?.use ? await c.use('db') : null; } catch { db = null; }
  if (!db) { useDb.setState({ offline: true }); return; }
  const timer = setTimeout(() => useDb.setState({ offline: true }), 10000);
  const ok = () => { clearTimeout(timer); useDb.setState({ ready: true, offline: false }); };
  const fail = (e: unknown) => { clearTimeout(timer); console.warn('[HQ] database', e); useDb.setState({ offline: true }); };
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    db.collection('stats').orderBy('at', 'desc').limit(24 * 60).onSnapshot((snap: any) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const rows = snap.docs.map((d: any) => d.data() as StatRow).reverse();
      useDb.setState({ stats: rows }); if (!snap.fromCache) ok();
    }, fail);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    db.collection('log').orderBy('at', 'desc').limit(30).onSnapshot((snap: any) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      useDb.setState({ log: snap.docs.map((d: any) => d.data() as LogRow) });
    }, fail);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    db.doc('hq/engine').onSnapshot((d: any) => useDb.setState({ engine: d.exists ? (d.data() as Engine) : null }), fail);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    db.doc('hq/state').onSnapshot((d: any) => useDb.setState({ state: d.exists ? d.data() : null }), fail);
  } catch (e) { fail(e); }
}
