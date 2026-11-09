/**
 * STUDIO (verbeterlijst stap 3: video's en cijfers). Hulpjes voor de pijplijn, renders, scriptlezer,
 * stemmen, thumbnailmuur, doelen en het videorapport. Alles leest alleen: status.json (services/live),
 * de database (services/db) en projectbestanden via de files-capability. Niets wordt verzonnen:
 * ontbreekt iets, dan geeft een functie null terug en zegt de pagina dat eerlijk.
 */
import { filesApi, type Activity, type YTVideo } from './live';
import type { StatRow } from './db';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;

/* ---------- tijden en bronnen ---------- */
const TZ = 'Europe/Amsterdam';
/** '9 nov 17:00' (of '9 nov' zonder tijd) */
export function kortTijd(iso?: string | number | null, metTijd = true): string | null {
  if (iso == null || iso === '') return null;
  if (typeof iso === 'string' && !/^\d{4}-\d{2}-\d{2}/.test(iso)) return iso;
  const t = typeof iso === 'number' ? iso : Date.parse(/^\d{4}-\d{2}-\d{2}$/.test(iso) ? `${iso}T12:00:00` : iso);
  if (typeof iso === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(iso)) metTijd = false;
  if (isNaN(t)) return typeof iso === 'string' ? iso : null;
  return new Date(t).toLocaleString('nl-NL', { timeZone: TZ, day: 'numeric', month: 'short', ...(metTijd ? { hour: '2-digit', minute: '2-digit' } : {}) });
}
/** '5 min geleden', '3 uur geleden', anders de datum */
export function bronTijd(iso?: string | number | null): string | null {
  const t = typeof iso === 'number' ? iso : Date.parse(iso ?? '');
  if (!t || isNaN(t)) return null;
  const m = Math.max(0, Math.round((Date.now() - t) / 60000));
  return m < 1 ? 'net' : m < 60 ? `${m} min geleden` : m < 12 * 60 ? `${Math.round(m / 60)} uur geleden` : kortTijd(t);
}

/* ---------- mappen bekijken ---------- */
export interface Item { path: string; isDirectory: boolean; size: number }
/** Inhoud van een projectmap (null: geen toegang of geen map). */
export async function lijstMap(map: string, diep = false): Promise<Item[] | null> {
  const fs: Any = await filesApi();
  if (!fs?.list) return null;
  const path = map.replace(/^\/+/, '').replace(/\/+$/, '');
  const uit: Item[] = [];
  try {
    let cursor: string | undefined;
    for (let i = 0; i < 10; i++) {
      const r: Any = await fs.list({ path, recursive: diep, ...(cursor ? { cursor } : {}) });
      for (const e of Array.isArray(r?.entries) ? r.entries : []) if (e && typeof e.path === 'string') uit.push({ path: e.path.replace(/^\/+/, ''), isDirectory: !!e.isDirectory, size: Number(e.size) || 0 });
      cursor = typeof r?.cursor === 'string' && r.cursor ? r.cursor : undefined;
      if (!cursor) break;
    }
    return uit;
  } catch { return null; }
}
export const naamVan = (p: string) => p.split('/').pop() ?? p;
export const map = (folder: string) => folder.replace(/^\/+/, '').replace(/\/+$/, '');

/* ---------- renders uit de takenlijst en status.json ---------- */
export interface RenderStand {
  video?: number; titel: string; thread?: string; klaar?: number; totaal?: number; vrij?: string; eind?: string;
  tekst: string; at?: string; state: string; stil: boolean; kapot: boolean; frame?: string;
}
const RENDER = /\brender|\bscènes?\b.*\bklaar|\bblender\b/i;
export function renderStanden(activity: Activity[]): RenderStand[] {
  return activity.filter((a) => a.doing && RENDER.test(a.doing) && a.state !== 'done' && a.state !== 'stopped').map((a) => {
    const d = a.doing!;
    const sc = /(\d+)\s*(?:van de|van|\/)\s*(\d+)\s*(?:scènes|scenes|shots)/i.exec(d);
    const vrij = /(\d+[.,]?\d*\s*[GT]B)\s*vrij(?:\s*op\s*([A-Z]:))?/i.exec(d);
    const eind = d.split(/(?<=\.)\s+/).find((z) => /verwacht|klaar rond|\baf (?:op|rond|om)\b|\beindtijd\b|schatting/i.test(z));
    const leeftijd = (Date.now() - (Date.parse(a.lastIso ?? '') || Date.now())) / 36e5;
    const kapot = a.state === 'failed' || /crash|vastgelopen|mislukt|afgebroken|gestopt met fout/i.test(d);
    const frame = (/\b([\w./-]+\.(?:png|jpe?g|exr))\b/i.exec(d) ?? [])[1];
    return {
      video: a.video, titel: a.title, thread: a.id, klaar: sc ? +sc[1] : undefined, totaal: sc ? +sc[2] : undefined,
      vrij: vrij ? `${vrij[1].replace(/\s+/g, ' ')}${vrij[2] ? ` op ${vrij[2]}` : ''}` : undefined, eind,
      tekst: d, at: a.lastIso, state: a.state, stil: a.state === 'working' && leeftijd > 3, kapot, frame: frame && /\//.test(frame) ? frame : undefined,
    };
  });
}

/* ---------- script lezen ---------- */
export interface Scene { kop: string; start: number; eind: number; tekst: string; vo: string[] }
export interface ScriptInfo { scenes: Scene[]; totaal: number; abonnee: { tijd: number; zin: string }[]; regels: string | null; hook: string | null }
export const tijdNaarS = (s: string) => { const p = s.split(':').map(Number); return p.length === 2 ? p[0] * 60 + p[1] : p.length === 3 ? p[0] * 3600 + p[1] * 60 + p[2] : NaN; };
export const sNaarTijd = (s: number) => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;
const KOP = /^(#{1,4})\s+(.+?)\s*[([]\s*(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})\s*[)\]](.*)$/;
const ZEGT = /^\s*[-*]?\s*\*\*(VO|[A-ZÀ-Ý][A-ZÀ-Ý '()-]{1,30})(?:\s*\([^)]*\))?:\*\*\s*(.+)$/;

export function leesScript(md: string): ScriptInfo {
  const regels = md.split('\n');
  const scenes: Scene[] = [];
  let cur: Scene | null = null;
  for (const r of regels) {
    const m = KOP.exec(r);
    if (m) {
      cur = { kop: `${m[2]}${m[5] ? ` ${m[5].trim()}` : ''}`.replace(/\s+·\s*$/, '').trim(), start: tijdNaarS(m[3]), eind: tijdNaarS(m[4]), tekst: '', vo: [] };
      scenes.push(cur);
      continue;
    }
    if (cur) {
      cur.tekst += r + '\n';
      const z = ZEGT.exec(r);
      if (z && (z[1] === 'VO' || /^["“\[]/.test(z[2].trim())) && !/^(HUD|SFX|SET|LICHT|MUZIEK|BEWEGING|CAMERA|NOTE)$/i.test(z[1])) cur.vo.push(`${z[1] === 'VO' ? '' : `${z[1]}: `}${z[2].replace(/\*\*/g, '').trim()}`);
    }
  }
  // dubbele deel-koppen eruit: een kop die precies de tijd van zijn eerste kind omvat en zelf geen tekst heeft
  const schoon = scenes.filter((s, i) => !(s.vo.length === 0 && scenes[i + 1] && scenes[i + 1].start === s.start && s.eind >= scenes[i + 1].eind && s.tekst.replace(/\s+/g, '').length < 40));
  const totaal = schoon.reduce((m, s) => Math.max(m, s.eind || 0), 0);
  const abonnee: ScriptInfo['abonnee'] = [];
  // tijd binnen de scène schatten naar de plek van de regel in de scènetekst
  for (const s of schoon) { const ls = s.tekst.split('\n'); ls.forEach((l, i) => { if (/subscribe/i.test(l) && /\bVO\b|"/.test(l)) abonnee.push({ tijd: Math.round(s.start + (i / Math.max(1, ls.length)) * Math.max(0, s.eind - s.start)), zin: l.replace(/^\s*[-*]\s*/, '').replace(/\*\*/g, '').trim() }); }); }
  const rs = /^#{2,4}\s+(Vaste animatieregels|Regels|Werkwijze)[^\n]*\n([\s\S]*?)(?=\n#{1,4}\s)/im.exec(md);
  const eerste = schoon.find((s) => s.vo.length);
  return { scenes: schoon, totaal, abonnee, regels: rs ? rs[2].trim() : null, hook: eerste?.vo[0] ?? null };
}

/* ---------- stemmen ---------- */
export function leesTsv(t: string): string[][] { return t.split('\n').map((r) => r.split('\t').map((c) => c.trim())).filter((r) => r.length >= 2 && r[0]); }

/* ---------- doelen en prognose ---------- */
/** groei per dag uit de meetpunten in de database (null: te weinig meetpunten) */
export function perDag(stats: StatRow[], k: 'subscribers' | 'views', dagen = 14): number | null {
  const s = stats.filter((r) => typeof r[k] === 'number' && Date.now() - +new Date(r.at) < dagen * 864e5);
  if (s.length < 2) return null;
  const d = (+new Date(s[s.length - 1].at) - +new Date(s[0].at)) / 864e5;
  return d >= 1 ? ((s[s.length - 1][k] as number) - (s[0][k] as number)) / d : null;
}
/** gemiddelde per dag sinds de eerste upload van dit soort (schatting, want per-dag-cijfers per video zijn er niet) */
export function sindsEerste(vids: YTVideo[], type: 'long' | 'short', f: (v: YTVideo) => number | undefined): { som: number; perDag: number | null; sinds?: string } {
  const l = vids.filter((v) => v.type === type && (v.status ?? 'public') === 'public');
  const som = l.reduce((a, v) => a + (f(v) ?? 0), 0);
  const eerste = l.map((v) => v.datum ?? v.date ?? '').filter(Boolean).sort()[0];
  if (!eerste) return { som, perDag: null };
  const d = (Date.now() - Date.parse(`${eerste.slice(0, 10)}T12:00:00`)) / 864e5;
  return { som, perDag: d >= 2 ? som / d : null, sinds: eerste.slice(0, 10) };
}
/** 'rond 14 dec 2026' of null */
export function haalDatum(nu: number, doel: number, perdag: number | null): string | null {
  if (nu >= doel) return 'gehaald';
  if (!perdag || perdag <= 0) return null;
  const dagen = (doel - nu) / perdag;
  if (dagen > 365 * 20) return 'meer dan 20 jaar';
  return new Date(Date.now() + dagen * 864e5).toLocaleDateString('nl-NL', { timeZone: TZ, day: 'numeric', month: 'short', year: 'numeric' });
}

/* ---------- klikratio en vertoningen (door niels ingevuld vanuit YouTube Studio) ---------- */
export interface Klik { ctr?: number; vertoningen?: number; at: string; bron: 'screenshot' | 'zelf' }
const KKEY = 'driftmark-klikratio';
export function leesKlik(): Record<string, Klik> { try { return JSON.parse(localStorage.getItem(KKEY) || '{}'); } catch { return {}; } }
export function bewaarKlik(id: string, k: Klik) { try { localStorage.setItem(KKEY, JSON.stringify({ ...leesKlik(), [id]: k })); } catch { /* geen opslag */ } }
