/**
 * KENNIS (v35): alles wat in het project is opgeslagen, op één plek. niels 6 nov 15:33: "Echt letterlijk alles wat
 * in deze chat besproken wordt ... Ik wil gewoon dat alle informatie die is opgeslagen wordt gestopt in dit
 * programmaatje." Claude zet het ongeveer elk uur als bestanden in het project:
 *   driftmark-hq/kennis/geheugen.json     het hele projectgeheugen (index + elke notitie)
 *   driftmark-hq/kennis/documenten.json   artifacts, bijlagen uit gesprekken, bestanden en beelden van niels
 *   driftmark-hq/kennis/kennis.json       alles in stukjes om te doorzoeken (ook gebruikt door de coach)
 *   driftmark-hq/gesprekken/...           de threads en de projectchat (services/threads.ts)
 * Alles wordt gelezen via de files-capability, nooit via het netwerk. geheugen en documenten laden bij het eerste
 * bezoek aan Kennis en opnieuw als je na meer dan 5 minuten terugkomt; kennis.json (1,5 MB) pas bij Zoeken.
 * Alles is data: niets wordt als HTML of code gebruikt, kapotte stukjes vallen weg.
 */
import { create } from 'zustand';
import { filesApi } from './live';
import { leesJson, loadGesprek } from './threads';
import { useGame } from '../store/useGame';
import type { Fragment, Kennis } from './coach';
import { veiligPad, vouw } from '../lib/tekst';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;

/* ================= typen ================= */
export type NotitieSoort = 'project' | 'feedback' | 'user' | 'reference';
export interface Notitie { naam: string; bestand: string; titel: string; beschrijving: string; soort?: NotitieSoort; gewijzigd?: string; tekst: string }
export interface Geheugen { gemaakt?: string; index: string; notities: Notitie[] }
export interface Artifact { title: string; url: string; at?: string; thread?: string; threadTitle?: string }
export interface Bijlage { name: string; kind: string; at?: string; thread?: string; threadTitle?: string; msg?: string; href?: string }
export interface Bestand { path: string; name: string; size?: number; mtime?: string; soort: 'tekst' | 'pdf' | 'ander'; upload?: boolean }
export interface Beeld { path: string; size?: number; mtime?: string; type: string }
export interface Documenten { gemaakt?: string; artifacts: Artifact[]; bijlagen: Bijlage[]; bestanden: Bestand[]; beelden: Beeld[] }

/** laden · ok · ontbreekt (nog niet opgehaald) · geen-toegang (geen projectbestanden hier) · fout. data blijft staan als
 *  een nieuwe lees mislukt. */
export interface Laad<T> { fase: 'leeg' | 'laden' | 'ok' | 'ontbreekt' | 'geen-toegang' | 'fout'; data?: T; code?: string }

export const SOORT_NAAM: Record<NotitieSoort, string> = { project: 'Project', feedback: 'Afspraak', user: 'Over niels', reference: 'Link' };
/** de naam van de eerste "notitie": het overzicht (MEMORY.md) */
export const INDEX = 'MEMORY';

/* ================= tijden ================= */
/** "net", "12 min geleden", "3 uur geleden", "gisteren", "4 dagen geleden" */
export function geledenNl(iso?: string | number): string {
  const t = typeof iso === 'number' ? iso : Date.parse(iso ?? ''); if (isNaN(t)) return '';
  const m = Math.max(0, Math.round((Date.now() - t) / 60000));
  if (m < 1) return 'net';
  if (m < 60) return `${m} min geleden`;
  if (m < 24 * 60) return `${Math.round(m / 60)} uur geleden`;
  const d = Math.round(m / 1440);
  return d <= 1 ? 'gisteren' : `${d} dagen geleden`;
}
const TZ = 'Europe/Amsterdam';
/** "5 nov 2026" */
export const datumNl = (iso?: string) => { const d = new Date(iso ?? ''); return isNaN(+d) ? '' : d.toLocaleDateString('nl-NL', { timeZone: TZ, day: 'numeric', month: 'short', year: 'numeric' }); };

/* ================= lezen en schoonmaken ================= */
const str = (x: unknown) => (typeof x === 'string' ? x : '');
const tijd = (x: unknown) => (typeof x === 'string' && !isNaN(Date.parse(x)) ? x : undefined);
const web = (x: unknown) => { const s = str(x).trim(); return /^https:\/\/[^\s"'<>]+$/i.test(s) || /^http:\/\/[^\s"'<>]+$/i.test(s) ? s : undefined; };
const ID = /^[A-Za-z0-9_-]{1,160}$/;
const id = (x: unknown) => { const s = str(x).trim(); return ID.test(s) ? s : undefined; };
const NOTITIE_SOORTEN = new Set(['project', 'feedback', 'user', 'reference']);
const BEELD_TYPES = new Set(['image/png', 'image/jpeg', 'image/gif', 'image/webp']);

function leesGeheugen(j: Any): Geheugen | null {
  if (!j || typeof j !== 'object' || !Array.isArray(j.notities)) return null;
  const notities: Notitie[] = []; const gezien = new Set<string>();
  for (const n of j.notities) {
    if (!n || typeof n !== 'object') continue;
    const naam = str(n.naam).trim(); const tekst = str(n.tekst);
    if (!naam || naam.length > 160 || gezien.has(naam.toLowerCase()) || !tekst.trim()) continue;
    gezien.add(naam.toLowerCase());
    notities.push({
      naam, bestand: str(n.bestand).trim() || `${naam}.md`, titel: str(n.titel).trim() || naam, beschrijving: str(n.beschrijving).trim(),
      soort: NOTITIE_SOORTEN.has(n.soort) ? n.soort : undefined, gewijzigd: tijd(n.gewijzigd), tekst,
    });
  }
  return { gemaakt: tijd(j.gemaakt), index: str(j.index), notities };
}

function leesDocumenten(j: Any): Documenten | null {
  if (!j || typeof j !== 'object') return null;
  const lijst = (x: unknown): Any[] => (Array.isArray(x) ? x.filter((y) => y && typeof y === 'object') : []);
  const artifacts: Artifact[] = [];
  for (const a of lijst(j.artifacts)) {
    const url = web(a.url); const title = str(a.title).trim();
    if (url && title) artifacts.push({ title, url, at: tijd(a.at), thread: id(a.thread), threadTitle: str(a.threadTitle).trim() || undefined });
  }
  const bijlagen: Bijlage[] = [];
  for (const b of lijst(j.bijlagen)) {
    const name = str(b.name).trim(); if (!name) continue;
    bijlagen.push({ name, kind: str(b.kind) || 'file', at: tijd(b.at), thread: id(b.thread), threadTitle: str(b.threadTitle).trim() || undefined, msg: id(b.msg), href: web(b.href) });
  }
  const bestanden: Bestand[] = [];
  for (const b of lijst(j.bestanden)) {
    const path = str(b.path).trim(); if (!veiligPad(path)) continue;
    const soort = b.soort === 'tekst' || b.soort === 'pdf' ? b.soort : /\.(md|txt|json|csv)$/i.test(path) ? 'tekst' : /\.pdf$/i.test(path) ? 'pdf' : 'ander';
    bestanden.push({ path, name: str(b.name).trim() || path.split('/').pop()!, size: Number.isFinite(b.size) ? Number(b.size) : undefined, mtime: tijd(b.mtime), soort, upload: b.upload === true || undefined });
  }
  const beelden: Beeld[] = [];
  for (const b of lijst(j.beelden)) {
    const path = str(b.path).trim(); const type = str(b.type).trim().toLowerCase();
    if (veiligPad(path) && BEELD_TYPES.has(type)) beelden.push({ path, type, size: Number.isFinite(b.size) ? Number(b.size) : undefined, mtime: tijd(b.mtime) });
  }
  return { gemaakt: tijd(j.gemaakt), artifacts, bijlagen, bestanden, beelden };
}

const pauze = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));
async function laadJson<T>(pad: string, lees: (j: Any) => T | null): Promise<Laad<T>> {
  let r = await leesJson(pad).catch(() => ({ ok: false as const, code: 'unavailable' }));
  if (!r.ok && ['changed', 'rate_limited', 'kapot'].includes(r.code)) { await pauze(2500); r = await leesJson(pad).catch(() => ({ ok: false as const, code: 'unavailable' })); }
  if (r.ok) { const d = lees(r.data); return d ? { fase: 'ok', data: d } : { fase: 'fout', code: 'vorm' }; }
  if (r.code === 'not_found') return { fase: 'ontbreekt' };
  if (r.code === 'geen-files' || r.code === 'not_granted') return { fase: 'geen-toegang', code: r.code };
  return { fase: 'fout', code: r.code };
}

/* ================= de store ================= */
interface KS {
  geheugen: Laad<Geheugen>; documenten: Laad<Documenten>;
  /** het aantal berichten in de projectchat (voor de tellers op Overzicht) */
  projectchat?: number;
}
export const useKennis = create<KS>(() => ({ geheugen: { fase: 'leeg' }, documenten: { fase: 'leeg' } }));

let bezocht = 0; let bezig = false;
/** Bij het openen van Kennis: de eerste keer laden, en opnieuw als je na meer dan 5 minuten terugkomt. */
export async function bezoekKennis(dwing = false) {
  if (bezig || (!dwing && bezocht && Date.now() - bezocht < 5 * 60000)) return;
  bezig = true; bezocht = Date.now();
  const zet = <K extends 'geheugen' | 'documenten'>(k: K, r: KS[K]) => {
    const oud = useKennis.getState()[k];
    // mislukt terwijl er al iets stond: het oude blijft staan
    if (r.fase !== 'ok' && oud.data) useKennis.setState({ [k]: { ...oud, fase: 'ok' } } as Partial<KS>);
    else useKennis.setState({ [k]: r } as Partial<KS>);
  };
  try {
    for (const k of ['geheugen', 'documenten'] as const) if (!useKennis.getState()[k].data) useKennis.setState({ [k]: { fase: 'laden' } } as Partial<KS>);
    const [g, d, p] = await Promise.all([
      laadJson('driftmark-hq/kennis/geheugen.json', leesGeheugen),
      laadJson('driftmark-hq/kennis/documenten.json', leesDocumenten),
      loadGesprek('projectchat').catch(() => null),
    ]);
    zet('geheugen', g); zet('documenten', d);
    if (p?.kind === 'ok') useKennis.setState({ projectchat: p.g.msgs.length });
    // geen toegang: niet bij elk bezoek opnieuw vragen
    if (g.fase === 'geen-toegang' && g.code === 'not_granted') bezocht = Date.now() + 864e5;
  } finally { bezig = false; }
}

/** een notitie uit een link: [[naam]], naam.md, of MEMORY voor het overzicht */
export function vindNotitie(g: Geheugen | undefined, naam: string): string | null {
  if (!g) return null;
  const n = naam.trim().replace(/^\.\//, '').replace(/\.md$/i, '').toLowerCase();
  if (n === INDEX.toLowerCase() || n === 'memory' || n === 'index') return INDEX;
  const x = g.notities.find((y) => y.naam.toLowerCase() === n || y.bestand.toLowerCase().replace(/\.md$/, '') === n || y.titel.toLowerCase() === n);
  return x ? x.naam : null;
}

/* ================= navigatie binnen Kennis ================= */
export type KennisTab = 'overzicht' | 'geheugen' | 'threads' | 'projectchat' | 'documenten' | 'werk' | 'zoeken';
const TABS: KennisTab[] = ['overzicht', 'geheugen', 'threads', 'projectchat', 'documenten', 'zoeken'];
interface Nav {
  tab: KennisTab;
  /** geheugen: de open notitie */
  notitie: string | null;
  /** documenten: het open bestand, met de zoekwoorden om te markeren */
  bestand: { path: string; hl?: string[] } | null;
  /** zoeken: wat er in het zoekveld staat */
  zoek: string;
  /** zoekwoorden die in de open notitie gemarkeerd worden */
  hl?: string[];
}
const bewaardeTab = (): KennisTab => { try { const t = localStorage.getItem('kennis-tab') as KennisTab; return TABS.includes(t) ? t : 'overzicht'; } catch { return 'overzicht'; } };
export const useKennisNav = create<Nav>(() => ({ tab: bewaardeTab(), notitie: null, bestand: null, zoek: '' }));
useKennisNav.subscribe((s, p) => { if (s.tab !== p.tab) { try { localStorage.setItem('kennis-tab', s.tab); } catch { /* geen opslag */ } } });
/** Naar Kennis, naar een tab en eventueel meteen naar een notitie, bestand of zoekopdracht. */
export function openKennis(p: Partial<Nav> = {}) {
  useKennisNav.setState(p);
  const g = useGame.getState();
  if (g.page !== 'kennis') g.setPage('kennis');
}

/* ================= indelen ================= */
export const GROEPEN = ['Video 4', 'Video 3', 'Video 2', 'Video 1', 'Driftmark HQ', 'Kanaal en overig'] as const;
export type Groep = (typeof GROEPEN)[number];
const WOORDEN: [Groep, RegExp][] = [
  ['Video 1', /\b2x\b|sterker|video ?1\b/i],
  ['Video 2', /\b10x\b|sneller|video ?2\b/i],
  ['Video 3', /geen[ -]regels|video ?3\b/i],
  ['Video 4', /nooit|doodgaan|video ?4\b/i],
  ['Driftmark HQ', /\bHQ\b|telefoonversie/],
];
/** Bij welke video een thread hoort: eerst wat status.json zegt (video 1-4), anders aan de titel. */
export function groepVanThread(title: string, video?: number): Groep {
  if (video && video >= 1 && video <= 4) return `Video ${video}` as Groep;
  for (const [g, re] of WOORDEN) if (re.test(title)) return g;
  return 'Kanaal en overig';
}
export const BESTAND_GROEPEN = ['Video 1', 'Video 2', 'Video 3', 'Video 4', 'Shorts', 'Driftmark HQ', 'Werkwijze', 'Cursus', 'Van niels', 'Overig'] as const;
export type BestandGroep = (typeof BESTAND_GROEPEN)[number];
const MAPPEN: Record<string, BestandGroep> = { '2x-sterker': 'Video 1', '10x-sneller': 'Video 2', 'geen-regels': 'Video 3', 'nooit-dood': 'Video 4' };
export function groepVanBestand(b: Pick<Bestand, 'path' | 'name' | 'upload'>): BestandGroep {
  const [map, sub] = b.path.split('/');
  if (map === 'videos') { if (MAPPEN[sub]) return MAPPEN[sub]; const m = /video ?(\d)/i.exec(b.name); return m && +m[1] >= 1 && +m[1] <= 4 ? (`Video ${m[1]}` as BestandGroep) : 'Overig'; }
  if (map === 'shorts') return 'Shorts';
  if (map === 'driftmark-hq') return 'Driftmark HQ';
  if (map === 'werkwijze') return 'Werkwijze';
  if (map === 'kennis') return 'Cursus';
  if (map === 'uploads' || b.upload) return 'Van niels';
  const m = /video ?(\d)\b/i.exec(b.name) ?? /video(\d)\b/i.exec(b.path);
  return m && +m[1] >= 1 && +m[1] <= 4 ? (`Video ${m[1]}` as BestandGroep) : 'Overig';
}

/** Artifacts staan er vaak twee keer in (de gepubliceerde link en die uit de thread): samen als één rij. */
export function artifactRijen(lijst: Artifact[]): Artifact[] {
  const per = new Map<string, Artifact>();
  for (const a of lijst) {
    const k = a.title.trim().toLowerCase();
    const o = per.get(k);
    if (!o) { per.set(k, { ...a }); continue; }
    const gepubliceerd = (x: Artifact) => /^https:\/\/claude\.ai\/artifact\//.test(x.url);
    if (gepubliceerd(a) && !gepubliceerd(o)) o.url = a.url;
    if (!o.thread && a.thread) { o.thread = a.thread; o.threadTitle = a.threadTitle; }
    if ((Date.parse(a.at ?? '') || 0) > (Date.parse(o.at ?? '') || 0)) o.at = a.at;
  }
  return [...per.values()].sort((x, y) => (Date.parse(y.at ?? '') || 0) - (Date.parse(x.at ?? '') || 0));
}

/* ================= zoeken in kennis.json ================= */
export type ZoekGroep = 'geheugen' | 'gesprek' | 'document' | 'cursus';
export const ZOEK_FILTERS: { id: 'alles' | ZoekGroep; label: string }[] = [
  { id: 'alles', label: 'Alles' }, { id: 'geheugen', label: 'Geheugen' }, { id: 'gesprek', label: 'Gesprekken' }, { id: 'document', label: 'Documenten' }, { id: 'cursus', label: 'Cursus' },
];
export interface ZoekItem { f: Fragment; plat: string; kop: string; groep: ZoekGroep; tijd: number }
const indexCache = new WeakMap<Kennis, ZoekItem[]>();
const groepVan = (f: Fragment): ZoekGroep => (f.soort === 'cursus' ? 'cursus' : f.soort === 'geheugen' || f.bron?.type === 'geheugen' ? 'geheugen' : f.soort === 'gesprek' || f.bron?.type === 'gesprek' ? 'gesprek' : 'document');
/** de doorzoekbare vorm van elk fragment: één keer gemaakt, daarna bewaard */
export function zoekIndex(k: Kennis): ZoekItem[] {
  let ix = indexCache.get(k);
  if (!ix) {
    ix = k.fragmenten.map((f) => ({ f, plat: vouw(f.tekst), kop: vouw(`${f.doc} ${f.hoofdstuk} ${f.onderwerp}`), groep: groepVan(f), tijd: Date.parse(f.bron?.at ?? '') || 0 }));
    indexCache.set(k, ix);
  }
  return ix;
}
const GEWICHT: Record<ZoekGroep, number> = { geheugen: 1.3, cursus: 1.2, document: 1, gesprek: 0.9 };
const LETTER = /[\p{L}\p{N}]/u;
export interface ZoekUit { hits: { it: ZoekItem; s: number }[]; tel: Record<'alles' | ZoekGroep, number>; ms: number }
/** Alle fragmenten waar elk zoekwoord in staat (in de tekst of de titel), de beste eerst. */
export function zoekKennis(k: Kennis, termen: string[]): ZoekUit {
  const t0 = performance.now();
  const tel: ZoekUit['tel'] = { alles: 0, geheugen: 0, gesprek: 0, document: 0, cursus: 0 };
  const hits: ZoekUit['hits'] = [];
  if (termen.length) {
    for (const it of zoekIndex(k)) {
      let s = 0; let ok = true;
      for (const t of termen) {
        let p = it.plat.indexOf(t); const inKop = it.kop.includes(t);
        if (p < 0 && !inKop) { ok = false; break; }
        let n = 0; let heel = false;
        while (p >= 0 && n < 6) {
          n++;
          if (!heel && !LETTER.test(it.plat[p - 1] ?? ' ') && !LETTER.test(it.plat[p + t.length] ?? ' ')) heel = true;
          p = it.plat.indexOf(t, p + t.length);
        }
        s += n + (heel ? 2 : 0) + (inKop ? 4 : 0);
      }
      if (!ok) continue;
      // kort en raak weegt iets zwaarder dan een heel lang stuk waar het woord toevallig één keer in staat
      s = s * GEWICHT[it.groep] * (it.plat.length < 400 ? 1.15 : 1);
      hits.push({ it, s }); tel.alles++; tel[it.groep]++;
    }
    hits.sort((a, b) => b.s - a.s || b.it.tijd - a.it.tijd);
  }
  return { hits, tel, ms: performance.now() - t0 };
}

/** Een stukje tekst rond de eerste treffer, op woordgrenzen, met … als er iets is weggelaten. */
export function knipsel(it: ZoekItem, termen: string[], lengte = 240): string {
  const tekst = it.f.tekst;
  let p = -1;
  for (const t of termen) { const q = it.plat.indexOf(t); if (q >= 0 && (p < 0 || q < p)) p = q; }
  if (p < 0) p = 0;
  let a = Math.max(0, p - 70);
  if (a > 0) { const sp = tekst.lastIndexOf(' ', a + 12); if (sp > a - 20 && sp >= 0) a = sp + 1; }
  let b = Math.min(tekst.length, a + lengte);
  if (b < tekst.length) { const sp = tekst.indexOf(' ', b - 12); if (sp > 0 && sp < b + 20) b = sp; }
  return `${a > 0 ? '… ' : ''}${tekst.slice(a, b).replace(/\s+/g, ' ').trim()}${b < tekst.length ? ' …' : ''}`;
}

/* ================= bestanden lezen ================= */
export type BestandLees =
  | { kind: 'tekst'; tekst: string; afgekapt: boolean }
  | { kind: 'pdf' } | { kind: 'beeld'; type: string } | { kind: 'binair' }
  | { kind: 'ontbreekt' } | { kind: 'geen-toegang' } | { kind: 'fout'; code: string };
const MAX_TEKST = 3_000_000;
function soortVan(b: Uint8Array): 'pdf' | string | null {
  const h = (...x: number[]) => x.every((v, i) => b[i] === v);
  if (h(0x25, 0x50, 0x44, 0x46)) return 'pdf';
  if (h(0x89, 0x50, 0x4e, 0x47)) return 'image/png';
  if (h(0xff, 0xd8, 0xff)) return 'image/jpeg';
  if (h(0x47, 0x49, 0x46, 0x38)) return 'image/gif';
  if (h(0x52, 0x49, 0x46, 0x46) && b[8] === 0x57 && b[9] === 0x45) return 'image/webp';
  return null;
}
async function leesBytes(path: string, opts?: { length?: number }): Promise<{ ok: true; bytes: Uint8Array; size: number } | { ok: false; code: string; wacht?: number }> {
  const fs = await filesApi();
  if (!fs) return { ok: false, code: 'geen-files' };
  let laatste = 'not_found';
  for (const p of [path, `/${path}`]) {
    try { const r = await fs.read(p, opts); return { ok: true, bytes: r.bytes, size: Number(r.size) || r.bytes.length }; } catch (e) {
      const code = String((e as Any)?.code ?? 'unavailable');
      if (code === 'not_found' || code === 'bad_request') { laatste = code; continue; }
      return { ok: false, code, wacht: Number((e as Any)?.retryAfterMs) || undefined };
    }
  }
  return { ok: false, code: laatste };
}
/** Een projectbestand om te lezen: tekst (Markdown), of alleen wat voor soort het is (PDF, beeld, iets anders). */
export async function leesBestand(path: string): Promise<BestandLees> {
  if (!veiligPad(path)) return { kind: 'ontbreekt' };
  if (/\.pdf$/i.test(path)) return { kind: 'pdf' };
  let r = await leesBytes(path, { length: MAX_TEKST });
  if (!r.ok && ['not_found', 'changed', 'rate_limited'].includes(r.code)) { await pauze(Math.min(r.wacht ?? 2000, 8000)); r = await leesBytes(path, { length: MAX_TEKST }); }
  if (!r.ok) return r.code === 'not_found' || r.code === 'bad_request' ? { kind: 'ontbreekt' } : r.code === 'geen-files' || r.code === 'not_granted' ? { kind: 'geen-toegang' } : { kind: 'fout', code: r.code };
  const s = soortVan(r.bytes);
  if (s === 'pdf') return { kind: 'pdf' };
  if (s) return { kind: 'beeld', type: s };
  // veel nul-tekens: geen tekst
  let nul = 0; for (let i = 0; i < Math.min(r.bytes.length, 4000); i++) if (r.bytes[i] === 0) nul++;
  if (nul > 4) return { kind: 'binair' };
  return { kind: 'tekst', tekst: new TextDecoder().decode(r.bytes), afgekapt: r.size > r.bytes.length };
}

/** Download via claude.ai (niels kiest zelf of hij het opslaat). Geeft een korte melding terug, of null als het gelukt is. */
export async function downloadBestand(path: string): Promise<string | null> {
  const fs = await filesApi();
  if (!fs) return 'Open de HQ in claude.ai om dit te downloaden.';
  try { await fs.download(path); return null; } catch (e) {
    const code = String((e as Any)?.code ?? 'unavailable');
    return code === 'declined' ? 'Niet opgeslagen.'
      : code === 'not_found' ? 'Dit bestand is er niet (meer).'
      : code === 'rate_limited' ? 'Even te druk. Probeer het zo nog eens.'
      : code === 'not_granted' ? 'De pagina heeft geen toegang tot de projectbestanden.'
      : code === 'too_large' ? 'Dit bestand is te groot om hier te downloaden.'
      : code === 'bad_request' ? 'Dit soort bestand kan hier niet gedownload worden.'
      : 'Downloaden lukt nu niet. Probeer het zo nog eens.';
  }
}

/* ================= beelden: hooguit 3 tegelijk lezen ================= */
let actief = 0; const wachtrij: (() => void)[] = [];
const plek = () => new Promise<void>((ok) => { if (actief < 3) { actief++; ok(); } else wachtrij.push(() => { actief++; ok(); }); });
const vrij = () => { actief--; const v = wachtrij.shift(); if (v) v(); };
/** Leest een beeld en geeft een object-URL terug (de aanroeper ruimt hem op met URL.revokeObjectURL). */
export async function laadBeeld(path: string, type: string, signal?: AbortSignal): Promise<string> {
  await plek();
  try {
    if (signal?.aborted) throw Object.assign(new Error('weg'), { code: 'weg' });
    let r = await leesBytes(path);
    if (!r.ok && ['changed', 'rate_limited'].includes(r.code)) { await pauze(Math.min(r.wacht ?? 2000, 8000)); r = await leesBytes(path); }
    if (!r.ok) throw Object.assign(new Error(r.code), { code: r.code });
    const echt = soortVan(r.bytes);
    return URL.createObjectURL(new Blob([r.bytes], { type: echt && echt !== 'pdf' ? echt : type }));
  } finally { vrij(); }
}
