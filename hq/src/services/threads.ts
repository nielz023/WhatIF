/**
 * THREADS UIT DE PROJECTBESTANDEN (v35). niels 6 nov 14:07: de connector voor de live stand bleef "Kan deze
 * connector niet laden" geven, wat de pagina ook deed. Daarom gebruikt de HQ geen connector meer. Claude zet de
 * stand van alle threads en de gesprekken zelf als bestanden in het project, ongeveer elk uur (en tussendoor op
 * verzoek, met de knop "Nu ophalen" in het gesprekspaneel):
 *   driftmark-hq/gesprekken/threads.json       stand van elke thread
 *   driftmark-hq/gesprekken/<threadId>.json    het gesprek van één thread
 *   driftmark-hq/gesprekken/projectchat.json   de projectchat
 * De pagina leest ze via de files-capability, net als status.json (services/live.ts): threads.json elke minuut
 * zolang de pagina zichtbaar is, een gesprek zodra het gesprekspaneel opengaat en daarna elke minuut.
 */
import { create } from 'zustand';
import { useLive, filesApi, type Activity } from './live';
import { useGame } from '../store/useGame';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;

/* ---------- tijden, altijd in de tijd van niels (Nederland) ---------- */
const MND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
const DELEN = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Amsterdam', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' });
const twee = (n: number) => String(n).padStart(2, '0');
function delen(t: number) {
  const p: Record<string, string> = {};
  for (const x of DELEN.formatToParts(new Date(t))) p[x.type] = x.value;
  // % 24: sommige browsers schrijven middernacht als 24
  return { j: Number(p.year), m: Number(p.month), d: Number(p.day), u: twee(Number(p.hour) % 24), mi: twee(Number(p.minute)) };
}
/** "6 nov 14:21": zoals de 'last'-regels in status.json */
export function kortNl(t: string | number | undefined): string {
  const n = typeof t === 'number' ? t : Date.parse(t ?? ''); if (isNaN(n)) return '';
  const x = delen(n); return `${x.d} ${MND[x.m - 1]} ${x.u}:${x.mi}`;
}
/** "vandaag 14:21", "gisteren 09:05" of "4 nov 18:30" */
export function wanneerNl(iso?: string): string {
  const n = Date.parse(iso ?? ''); if (isNaN(n)) return '';
  const x = delen(n); const zelfde = (y: ReturnType<typeof delen>) => x.j === y.j && x.m === y.m && x.d === y.d;
  return zelfde(delen(Date.now())) ? `vandaag ${x.u}:${x.mi}` : zelfde(delen(Date.now() - 864e5)) ? `gisteren ${x.u}:${x.mi}` : kortNl(n);
}

/* ---------- de stand van alle threads (threads.json) ---------- */
export type ThreadState = 'working' | 'blocked' | 'review_ready' | 'done' | 'failed' | 'stopped';
const STATES = new Set<string>(['working', 'blocked', 'review_ready', 'done', 'failed', 'stopped']);
export interface ThreadInfo {
  id: string; title: string; state: ThreadState; last?: string; resolved?: boolean;
  /** aantal berichten in het gespreksbestand, en of dat bestand er al is */
  msgs?: number; file?: boolean;
}
/** laden · ok · ontbreekt (threads.json is er nog niet) · geen-toegang (geen projectbestanden) · fout */
export type ThreadsSrc = 'laden' | 'ok' | 'ontbreekt' | 'geen-toegang' | 'fout';
interface S { threads: Record<string, ThreadInfo>; at?: string; src: ThreadsSrc }
export const useThreads = create<S>(() => ({ threads: {}, src: 'laden' }));

/** wat de stand voor niels betekent: een opgeloste thread is klaar, tenzij hij weer aan het werk is */
export const stateOf = (t: ThreadInfo): ThreadState => (t.resolved && t.state !== 'working' ? 'done' : t.state);

const DIR = 'driftmark-hq/gesprekken';
/** thread-id's (cmsg_...) en "projectchat": alleen letters, cijfers, _ en -, dus nooit een ander pad */
const VEILIG = /^[A-Za-z0-9_-]{1,160}$/;
type Lees = { ok: true; data: Any } | { ok: false; code: string; wacht?: number };
const pauze = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

/** één JSON-bestand uit de projectbestanden, zoals live.ts status.json leest (eerst zonder, dan met / ervoor) */
async function leesJson(rel: string): Promise<Lees> {
  const fs = await filesApi();
  if (!fs) return { ok: false, code: 'geen-files' };
  const codes: string[] = [];
  for (const p of [rel, `/${rel}`]) {
    let bytes: Uint8Array;
    try { bytes = (await fs.read(p)).bytes; } catch (e) {
      const code = String((e as Any)?.code ?? 'unavailable');
      if (code === 'not_found' || code === 'bad_request') { codes.push(code); continue; }
      return { ok: false, code, wacht: Number((e as Any)?.retryAfterMs) || undefined };
    }
    // half geschreven of geen JSON: als fout melden, de volgende lees probeert het opnieuw
    try { return { ok: true, data: JSON.parse(new TextDecoder().decode(bytes)) }; } catch { return { ok: false, code: 'kapot' }; }
  }
  return { ok: false, code: codes.includes('not_found') ? 'not_found' : codes[0] ?? 'unavailable' };
}

function leesThreads(j: Any): { at?: string; threads: Record<string, ThreadInfo> } | null {
  const lijst: Any[] | null = Array.isArray(j?.threads) ? j.threads : null;
  if (!lijst) return null;
  const threads: Record<string, ThreadInfo> = {};
  for (const t of lijst) {
    const id = typeof t?.id === 'string' ? t.id.trim() : '';
    if (!VEILIG.test(id) || !STATES.has(t.state)) continue;
    threads[id] = {
      id, title: typeof t.title === 'string' ? t.title.trim() : '', state: t.state,
      last: typeof t.last === 'string' && !isNaN(Date.parse(t.last)) ? t.last : undefined,
      resolved: t.resolved === true || undefined,
      msgs: Number.isFinite(t.msgs) ? Number(t.msgs) : undefined, file: typeof t.file === 'boolean' ? t.file : undefined,
    };
  }
  return { at: typeof j.at === 'string' ? j.at : undefined, threads };
}

const zetSrc = (src: ThreadsSrc) => { if (useThreads.getState().src !== src) useThreads.setState({ src }); };
let bezig = false; let gelezen = 0; let weg = false; let opnieuw: ReturnType<typeof setTimeout> | undefined;
async function poll(herkansing = false) {
  if (bezig || weg) return;
  bezig = true; gelezen = Date.now(); clearTimeout(opnieuw);
  try {
    const r = await leesJson(`${DIR}/threads.json`);
    const heeft = Object.keys(useThreads.getState().threads).length > 0;
    if (r.ok) {
      const p = leesThreads(r.data);
      if (!p) { if (!heeft) zetSrc('fout'); return; }
      const cur = useThreads.getState();
      if (cur.src === 'ok' && cur.at === p.at && JSON.stringify(cur.threads) === JSON.stringify(p.threads)) return; // niets nieuws
      useThreads.setState({ threads: p.threads, at: p.at, src: 'ok' });
      return;
    }
    // geen projectbestanden in deze weergave, of niels gaf geen toestemming (dan niet blijven vragen)
    if (r.code === 'geen-files' || r.code === 'not_granted') { if (r.code === 'not_granted') weg = true; zetSrc('geen-toegang'); return; }
    // nog geen bestand: wat we al wisten blijft staan
    if (r.code === 'not_found') { if (!heeft) zetSrc('ontbreekt'); return; }
    if (!heeft) zetSrc('fout');
    // even bezet, net veranderd of half geschreven: zo meteen nog één keer
    if (!herkansing) opnieuw = setTimeout(() => void poll(true), Math.min(Math.max(r.wacht ?? 8000, 2000), 30000));
  } finally { bezig = false; }
}

let started = false;
/** Eén keer bij het starten van de app. Leest threads.json meteen na de eerste lees van status.json (dan vraagt
 *  claude.ai hooguit één keer om toegang) en daarna elke minuut, alleen zolang de pagina zichtbaar is. */
export function startThreads() {
  if (started) return; started = true;
  if (useLive.getState().checkedAt != null) void poll();
  else {
    const reserve = setTimeout(() => { klaar(); void poll(); }, 20000);
    const klaar = useLive.subscribe((s) => { if (s.checkedAt != null) { clearTimeout(reserve); klaar(); void poll(); } });
  }
  setInterval(() => { if (document.visibilityState === 'visible') void poll(); }, 60000);
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible' && Date.now() - gelezen >= 60000) void poll(); });
}

/* ---------- de stand in de takenlijst (en dus ook in het 3D-kantoor) ---------- */
const OPEN = new Set<string>(['working', 'blocked', 'review_ready']);
/** Legt de stand van één thread over zijn rij uit status.json. */
function overlay(a: Activity, t: ThreadInfo, at?: string): Activity {
  const rl = Date.parse(a.lastIso ?? '');
  const tl = Date.parse(t.last ?? '');
  // tot wanneer threads.json het weet: het moment van ophalen (anders de laatste activiteit van de thread)
  const peil = isNaN(Date.parse(at ?? '')) ? tl : Date.parse(at!);
  // status.json veranderde deze rij ná dat moment: de rij is nieuwer, laat hem zoals hij is
  if (!isNaN(rl) && !isNaN(peil) && rl > peil) return a;
  const nieuwer = !isNaN(tl) && (isNaN(rl) || tl > rl);
  let state: string = stateOf(t);
  // afgerond in status.json (bijv. na jouw Goedkeuren) en sindsdien niets nieuws in de thread: blijft klaar
  if (a.state === 'done' && state !== 'working' && !nieuwer) state = 'done';
  return { ...a, state, live: true, ...(nieuwer ? { lastIso: new Date(tl).toISOString(), last: kortNl(tl) } : {}) };
}

let raw: Activity[] | null = null; let merged: Activity[] | null = null; let mergedSig = '';
function merge() {
  const L = useLive.getState(); const { threads: T, at } = useThreads.getState();
  if (L.data.activity !== merged) raw = L.data.activity;
  if (!raw || !Object.keys(T).length) return;
  const gezien = new Set<string>();
  const rijen = raw.map((a) => { const t = a.id ? T[a.id] : undefined; if (!t) return a; gezien.add(t.id); return overlay(a, t, at); });
  // threads die nog niet in status.json staan: alleen als ze bezig zijn of op jou wachten
  const extra: Activity[] = [];
  for (const t of Object.values(T)) {
    const state = stateOf(t);
    if (gezien.has(t.id) || !OPEN.has(state)) continue;
    const tl = Date.parse(t.last ?? '');
    extra.push({ title: t.title || 'Nieuwe thread', id: t.id, state, last: kortNl(tl), lastIso: isNaN(tl) ? undefined : new Date(tl).toISOString(), live: true });
  }
  extra.sort((x, y) => (Date.parse(y.lastIso ?? '') || 0) - (Date.parse(x.lastIso ?? '') || 0));
  const out = [...extra, ...rijen];
  // niets veranderd: de store niet opnieuw zetten (anders draaien alle effecten die op de stand letten opnieuw)
  const sig = JSON.stringify(out);
  if (L.data.activity === merged && sig === mergedSig) return;
  merged = out; mergedSig = sig;
  useLive.setState((st) => ({ data: { ...st.data, activity: out } }));
}
useThreads.subscribe(merge);
useLive.subscribe((st, prev) => { if (st.data.activity !== prev.data.activity && st.data.activity !== merged) merge(); });

/* ================= meldingen: als een thread klaar is, op jou wacht of misgaat ================= */
// zoals eerder bij de live stand, nu op basis van threads.json; nooit bij de eerste keer laden
const vorige = new Map<string, ThreadState>();
let meldKlaar = false;
/** threads.json komt ongeveer elk uur: een korte taak staat er bij de eerste keer vaak al als klaar of wachtend in */
const MELD_NIEUW = new Set<ThreadState>(['review_ready', 'blocked', 'failed']);
useThreads.subscribe((st, prev) => {
  if (st.threads === prev.threads) return;
  let toasts = 0;
  for (const t of Object.values(st.threads)) {
    const nu = stateOf(t); const was = vorige.get(t.id); vorige.set(t.id, nu);
    // eerste keer laden: alleen onthouden. Daarna: een andere stand, of een nieuwe thread die al op jou wacht
    if (!meldKlaar || was === nu || (!was && !MELD_NIEUW.has(nu))) continue;
    const rij = (raw ?? useLive.getState().data.activity).find((a) => a.id === t.id);
    const titel = (rij?.title || t.title || 'Een thread').slice(0, 80);
    const m = nu === 'review_ready' ? { t: `✅ Klaar om te bekijken: ${titel}`, k: 'success' as const }
      : nu === 'blocked' ? { t: `👋 Wacht op jou: ${titel}${rij?.needs ? ` (${rij.needs.slice(0, 80)})` : ''}`, k: 'approval' as const }
      : nu === 'failed' ? { t: `⚠️ Mislukt: ${titel}`, k: 'warning' as const }
      : nu === 'done' && was === 'working' ? { t: `✅ Afgerond: ${titel}`, k: 'success' as const } : null;
    if (!m) continue;
    useGame.setState((d: Any) => { d.notifications.unshift({ id: `m${Date.now()}${Math.random().toString(36).slice(2, 6)}`, tick: d.tick ?? 0, text: m.t, kind: m.k, read: false, link: 'meer' }); if (d.notifications.length > 80) d.notifications.length = 80; });
    // veel tegelijk (bijv. na een tijd weg): hooguit drie meldingen in beeld, de rest staat bij de meldingen
    if (toasts++ < 3) useGame.getState().toast(m.t, m.k === 'warning' ? 'warning' : m.k === 'approval' ? 'info' : 'success');
  }
  meldKlaar = true;
});

/* ================= gesprekken ================= */
export interface Msg { id: string; who: 'niels' | 'claude' | 'keuze' | 'checklist' | 'systeem'; text: string; at: string; author?: string; options?: string[] }
export interface GesprekBestand { id: string; title: string; at?: string; hasMore: boolean; msgs: Msg[] }
export type GesprekLees = { kind: 'ok'; g: GesprekBestand } | { kind: 'ontbreekt' } | { kind: 'geen-toegang' } | { kind: 'fout'; code: string };
const WIE: Record<string, Msg['who']> = { niels: 'niels', user: 'niels', claude: 'claude', assistant: 'claude', keuze: 'keuze', checklist: 'checklist', systeem: 'systeem' };

function leesGesprek(j: Any, id: string): GesprekBestand | null {
  if (!j || typeof j !== 'object' || Array.isArray(j)) return null;
  const msgs: Msg[] = [];
  (Array.isArray(j.msgs) ? j.msgs : []).forEach((m: Any, i: number) => {
    if (!m || typeof m !== 'object') return;
    const text = typeof m.text === 'string' ? m.text : '';
    const options = Array.isArray(m.options) ? m.options.filter((o: unknown): o is string => typeof o === 'string' && !!o.trim()) : [];
    if (!text.trim() && !options.length) return;
    msgs.push({
      id: typeof m.id === 'string' && m.id ? m.id : `m${i}`, who: WIE[String(m.who)] ?? 'systeem', text, at: typeof m.at === 'string' ? m.at : '',
      author: typeof m.author === 'string' && m.author.trim() ? m.author.trim() : undefined, options: options.length ? options : undefined,
    });
  });
  // oudste eerst, zo hoort het bestand te zijn; staat het andersom, dan draaien we het om
  if (msgs.length > 1 && Date.parse(msgs[0].at) > Date.parse(msgs[msgs.length - 1].at)) msgs.reverse();
  return { id: typeof j.id === 'string' ? j.id : id, title: typeof j.title === 'string' ? j.title : '', at: typeof j.at === 'string' ? j.at : undefined, hasMore: j.hasMore === true, msgs };
}

/** Het gesprek van een thread (id = cmsg_...) of van de projectchat (id = "projectchat"). */
export async function loadGesprek(id: string): Promise<GesprekLees> {
  if (!VEILIG.test(id)) return { kind: 'ontbreekt' };
  const pad = `${DIR}/${id}.json`;
  let r = await leesJson(pad);
  // een net geschreven bestand is soms een paar tellen nog niet te zien: zegt threads.json dat hij er is, dan nog één keer
  if (!r.ok && r.code === 'not_found' && useThreads.getState().threads[id]?.file) { await pauze(2500); r = await leesJson(pad); }
  else if (!r.ok && ['changed', 'rate_limited', 'kapot'].includes(r.code)) { await pauze(Math.min(r.wacht ?? 2000, 10000)); r = await leesJson(pad); }
  if (r.ok) { const g = leesGesprek(r.data, id); return g ? { kind: 'ok', g } : { kind: 'fout', code: 'vorm' }; }
  if (r.code === 'not_found') return { kind: 'ontbreekt' };
  if (r.code === 'geen-files' || r.code === 'not_granted') return { kind: 'geen-toegang' };
  return { kind: 'fout', code: r.code };
}
