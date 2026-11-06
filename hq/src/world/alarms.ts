/**
 * ALARMEN (verbeterpunt 8): wat er mis kan gaan, uit de echte stand.
 * Rood = er is iets vastgelopen of mislukt (crisiskamer gaat knipperen met zwaailicht en sirene).
 * Oranje = let op (renderstatus al lang niet bijgewerkt, schijf bijna vol, taak wacht al lang op jou).
 */
import type { Live } from '../services/live';
import { useDb } from '../services/db';

export interface Alarm { level: 'rood' | 'oranje'; text: string; key: string }

const hoursAgo = (iso?: string) => { if (!iso) return Infinity; const t = new Date(iso.length <= 16 ? iso + ':00' : iso).getTime(); return isNaN(t) ? Infinity : (Date.now() - t) / 3.6e6; };

export function alarmsFrom(L: Live): Alarm[] {
  const out: Alarm[] = [];
  for (const a of L.activity ?? []) {
    const id = a.id || a.session || a.title; // live threads die nog niet in status.json staan hebben (nog) geen id
    if (a.state === 'failed') out.push({ level: 'rood', text: `Taak mislukt: ${a.title}`, key: `f:${id}` });
    const h = hoursAgo(a.lastIso);
    if (a.state === 'blocked' && Number.isFinite(h) && h > 24) out.push({ level: 'oranje', text: `Wacht al ${Math.round(h)} uur op jou: ${a.title}`, key: `b:${id}` });
  }
  const b = L.blender;
  if (b) {
    const rendering = (L.videos ?? []).some((v) => v.steps.some((s) => s.active && (s.label === 'Animatie' || s.label === 'Render')));
    const h = hoursAgo(b.bijgewerkt);
    if (rendering && h > 12 && h < 24 * 30) out.push({ level: 'oranje', text: `Renderstatus al ${Math.round(h)} uur niet bijgewerkt (loopt de render nog?)`, key: 'render-stil' });
    const disk = /schijf\s*([\d.,]+)\s*GB/i.exec(b.stand ?? '')?.[1];
    if (disk) { const gb = parseFloat(disk.replace(',', '.')); if (gb < 25) out.push({ level: gb < 8 ? 'rood' : 'oranje', text: `Schijf bijna vol: ${disk} GB vrij (stand van ${b.bijgewerkt?.slice(5, 16).replace('T', ' ')})`, key: 'schijf' }); }
  }
  // fouten uit het automatische logboek van de laatste 24 uur
  const e = useDb.getState().log.find((x) => x.kind === 'fout' && hoursAgo(x.at) < 24);
  if (e) out.push({ level: 'rood', text: `Fout in de automatische ronde: ${e.text}`.slice(0, 120), key: `log:${e.at}` });
  return out;
}
