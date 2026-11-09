/**
 * Eén kleurensysteem voor status, overal in het HQ (verbeterlijst punt 21):
 * rood = probleem, oranje = wacht op jou, blauw = bezig, groen = klaar, grijs = staat stil.
 */
export const KLEUR = { probleem: '#ff4d6d', wacht: '#ff8a3d', bezig: '#3db8ff', klaar: '#3ddc97', stil: '#94a3b8' } as const;
export type Soort = keyof typeof KLEUR;
export const UITLEG: Record<Soort, string> = { probleem: 'probleem', wacht: 'wacht op jou', bezig: 'bezig', klaar: 'klaar', stil: 'staat stil' };
/** threadstatus (working, blocked, review_ready, done, failed, stopped) naar soort */
export const soortVan = (state?: string): Soort =>
  state === 'working' ? 'bezig' : state === 'blocked' || state === 'review_ready' ? 'wacht' : state === 'done' ? 'klaar' : state === 'failed' ? 'probleem' : 'stil';
