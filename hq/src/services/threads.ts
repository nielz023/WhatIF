/**
 * LIVE THREADS (niels 2026-11-06: "voeg allle 2 de kanttekeningen toe").
 * 1. De stand van elke thread komt LIVE uit de connector "Claude Code Remote" (met niels' eigen inlog),
 *    niet meer alleen uit het uurlijkse status.json: list_sessions (alle threads in één keer, elke 30 s)
 *    en get_session (checklist en "wacht op jou"-regel van de open threads).
 * 2. De hele gesprekken: list_events geeft per thread (en voor de projectchat de coördinator-sessies) alle
 *    berichten van niels en de antwoorden van Claude, bladzijde voor bladzijde terug in de tijd.
 * Zonder connector valt alles terug op status.json; er gaat niets mis.
 */
import { create } from 'zustand';
import { useLive, type Activity } from './live';
import { useGame } from '../store/useGame';

export const SERVER = 'Claude Code Remote';
export type Bucket = 'working' | 'blocked' | 'review_ready' | 'done' | 'failed' | 'idle';
export interface SessionLive {
  id: string; title: string; bucket: Bucket; updatedAt?: string; createdAt?: string; tags?: string[];
  needs?: string; detail?: string; recent?: string; checklist?: string; parent?: string; at: number;
}
type Src = 'laden' | 'live' | 'geen' | 'fout';
interface S {
  sessions: Record<string, SessionLive>; src: Src; err?: string; checkedAt?: number;
  coordinators: string[]; // projectchat: alle coördinator-sessies, nieuwste eerst
}
export const useThreads = create<S>(() => ({ sessions: {}, src: 'laden', coordinators: [] }));

/* ---------- hulpjes ---------- */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
let mcpP: Promise<Any | null> | null = null;
function mcp(): Promise<Any | null> {
  if (!mcpP) mcpP = (async () => { try { const c = (window as Any).claude; return c?.use ? await c.use('mcp') : null; } catch { return null; } })();
  return mcpP;
}
/** antwoord van de connector: JSON (soms ingepakt in tekst of in {ccr: ...}) */
export function unwrap(r: Any): Any {
  let p = r?.payload ?? r;
  if (p && typeof p === 'object' && Array.isArray(p.content) && p.payload === undefined) {
    const t = p.content.find((b: Any) => b?.type === 'text')?.text; if (t) p = t;
  }
  if (typeof p === 'string') {
    const a = p.indexOf('{'), b = p.lastIndexOf('}');
    if (a >= 0 && b > a) { try { p = JSON.parse(p.slice(a, b + 1)); } catch { /* */ } }
  }
  return p?.ccr ?? p;
}
const BUCKET: Record<string, Bucket> = {
  SESSION_STATUS_BUCKET_WORKING: 'working', SESSION_STATUS_BUCKET_BLOCKED: 'blocked', SESSION_STATUS_BUCKET_REVIEW_READY: 'review_ready',
  SESSION_STATUS_BUCKET_COMPLETED: 'done', SESSION_STATUS_BUCKET_FAILED: 'failed', working: 'working', blocked: 'blocked', review_ready: 'review_ready', completed: 'done', failed: 'failed',
};
function toLive(s: Any, old?: SessionLive): SessionLive {
  const pts = s.external_metadata?.post_turn_summary ?? s.post_turn_summary ?? {};
  return {
    ...(old ?? {}), id: s.id, title: s.title ?? old?.title ?? '', bucket: BUCKET[s.status_bucket] ?? old?.bucket ?? 'idle',
    updatedAt: s.updated_at ?? old?.updatedAt, createdAt: s.created_at ?? old?.createdAt, tags: s.tags ?? old?.tags,
    needs: pts.needs_action || undefined, detail: pts.status_detail || undefined, recent: pts.recent_action || old?.recent,
    checklist: s.external_metadata?.status?.text ?? old?.checklist, parent: s.parent_session_id ?? old?.parent, at: Date.now(),
  };
}
export const sessionOfThread = (a: Activity) => a.session ?? null;

/* ---------- stand van alle threads ---------- */
const unsub: (() => void)[] = [];
let started = false;
export async function startThreads() {
  if (started) return; started = true;
  const m = await mcp();
  if (!m) { useThreads.setState({ src: 'geen' }); return; }
  const onList = (ev: Any) => {
    if (ev.type === 'error') { const code = ev.error?.code; useThreads.setState({ src: code === 'server_unavailable' ? useThreads.getState().src : 'fout', err: code }); return; }
    const p = unwrap(ev.result); const data: Any[] = Array.isArray(p?.data) ? p.data : [];
    const cur = { ...useThreads.getState().sessions };
    const coords: string[] = [];
    for (const s of data) {
      if (!s?.id) continue;
      const tags: string[] = s.tags ?? [];
      if (tags.includes('hearth-overview')) { cur[s.id] = toLive(s, cur[s.id]); coords.push(s.id); continue; }
      if (tags.length && !tags.includes('hearth-thread')) continue;
      cur[s.id] = toLive(s, cur[s.id]);
    }
    coords.sort((x, y) => (cur[y].createdAt ?? '').localeCompare(cur[x].createdAt ?? ''));
    useThreads.setState({ sessions: cur, src: 'live', checkedAt: Date.now(), coordinators: coords.length ? coords : useThreads.getState().coordinators });
    watchActive();
  };
  // eerst met het label-filter (alleen threads + projectchat); lukt dat niet, dan alle sessies en zelf filteren
  try {
    await m.callTool(SERVER, 'list_sessions', { tags: ['hearth-thread', 'hearth-overview'], limit: 100 }, { cache: { staleTime: 20000 } });
    unsub.push(m.watchTool(SERVER, 'list_sessions', { tags: ['hearth-thread', 'hearth-overview'], limit: 100 }, onList, { refetchInterval: 30000, cache: { staleTime: 20000 } }));
  } catch (e) {
    const code = (e as Any)?.code;
    if (code === 'not_in_manifest' || code === 'server_not_connected' || code === 'needs_reauth' || code === 'blocked_by_policy') { useThreads.setState({ src: 'geen', err: code }); return; }
    unsub.push(m.watchTool(SERVER, 'list_sessions', { limit: 100 }, onList, { refetchInterval: 30000, cache: { staleTime: 20000 } }));
  }
}

/** van de threads die open zijn (bezig, wacht op jou) ook de checklist en de "wacht op jou"-regel bijhouden */
const watching = new Map<string, () => void>();
function watchActive() {
  void mcp().then((m) => {
    if (!m) return;
    const S = useThreads.getState().sessions;
    const act = Object.values(S).filter((s) => !s.tags?.includes('hearth-overview') && (s.bucket === 'working' || s.bucket === 'blocked' || s.bucket === 'review_ready')).map((s) => s.id);
    for (const [id, off] of watching) if (!act.includes(id)) { off(); watching.delete(id); }
    for (const id of act) {
      if (watching.has(id)) continue;
      const off = m.watchTool(SERVER, 'get_session', { session_id: id }, (ev: Any) => {
        if (ev.type !== 'data') return;
        const s = unwrap(ev.result); if (!s?.id) return;
        const cur = useThreads.getState().sessions;
        useThreads.setState({ sessions: { ...cur, [s.id]: toLive(s, cur[s.id]) } });
      }, { refetchInterval: 30000, cache: { staleTime: 20000 } });
      watching.set(id, off);
    }
  });
}

/** eenmalig de details van één thread ophalen (bij het openen van het gesprek) */
export async function loadSession(id: string): Promise<SessionLive | null> {
  const m = await mcp(); if (!m) return null;
  try {
    const s = unwrap(await m.callTool(SERVER, 'get_session', { session_id: id }, { cache: { staleTime: 15000 } }));
    if (!s?.id) return null;
    const cur = useThreads.getState().sessions; const v = toLive(s, cur[s.id]);
    useThreads.setState({ sessions: { ...cur, [s.id]: v } });
    return v;
  } catch { return null; }
}

/* ---------- de live stand in de takenlijst (en dus ook in het 3D-kantoor) ---------- */
const STATE_OF: Record<Bucket, string> = { working: 'working', blocked: 'blocked', review_ready: 'review_ready', done: 'done', failed: 'failed', idle: 'done' };
const ago = (iso?: string) => {
  if (!iso) return ''; const m = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (m < 1) return 'net nu'; if (m < 60) return `${m} min geleden`; const h = Math.round(m / 60); if (h < 24) return `${h} uur geleden`; const d = Math.round(h / 24); return `${d} ${d === 1 ? 'dag' : 'dagen'} geleden`;
};
let raw: Activity[] | null = null; let merged: Activity[] | null = null;
function merge() {
  const L = useLive.getState(); const S = useThreads.getState().sessions;
  if (L.data.activity !== merged) raw = L.data.activity;
  if (!raw || !Object.keys(S).length) return;
  const seen = new Set<string>();
  const out = raw.map((a) => {
    const s = a.session ? S[a.session] : undefined; if (!s) return a;
    seen.add(s.id);
    // een afgeronde (opgeloste) thread blijft afgerond, ook als de sessie zelf nog "klaar voor review" zegt
    const state = a.state === 'done' && s.bucket !== 'working' ? 'done' : STATE_OF[s.bucket];
    const newer = !a.lastIso || (s.updatedAt ?? '') > a.lastIso;
    return {
      ...a, state, live: true, needs: s.needs, recent: s.recent, checklist: s.checklist,
      ...(newer && s.updatedAt ? { lastIso: s.updatedAt.slice(0, 19), last: ago(s.updatedAt) } : {}),
      ...(s.bucket === 'working' && s.recent ? { doing: s.recent } : s.needs && (s.bucket === 'blocked' || s.bucket === 'review_ready') ? { doing: s.needs } : {}),
    } as Activity;
  });
  // nieuwe threads die nog niet in status.json staan
  for (const s of Object.values(S)) {
    if (seen.has(s.id) || s.tags?.includes('hearth-overview') || raw.some((a) => a.session === s.id)) continue;
    if (s.bucket === 'done' && (s.updatedAt ?? '') < (useLive.getState().data.updated ?? '')) continue;
    out.unshift({ title: s.title, id: '', session: s.id, state: STATE_OF[s.bucket], last: ago(s.updatedAt), lastIso: s.updatedAt?.slice(0, 19), doing: s.recent ?? s.detail, live: true, needs: s.needs, checklist: s.checklist } as Activity);
  }
  merged = out;
  useLive.setState((st) => ({ data: { ...st.data, activity: out } }));
}
useThreads.subscribe(merge);
useLive.subscribe((st, prev) => { if (st.data.activity !== prev.data.activity && st.data.activity !== merged) merge(); });

/* ================= meldingen: als een thread klaar is, op jou wacht of misgaat ================= */
const lastBucket = new Map<string, Bucket>();
let meldReady = false;
useThreads.subscribe((st) => {
  const S = st.sessions; const ids = Object.keys(S); if (!ids.length) return;
  for (const id of ids) {
    const s = S[id]; const was = lastBucket.get(id); lastBucket.set(id, s.bucket);
    if (!meldReady || !was || was === s.bucket || s.tags?.includes('hearth-overview')) continue;
    const titel = s.title?.slice(0, 80) || 'Een thread';
    const m = s.bucket === 'review_ready' ? { t: `✅ Klaar om te bekijken: ${titel}`, k: 'success' as const }
      : s.bucket === 'blocked' ? { t: `👋 Wacht op jou: ${titel}${s.needs ? ` (${s.needs.slice(0, 80)})` : ''}`, k: 'approval' as const }
      : s.bucket === 'failed' ? { t: `⚠️ Mislukt: ${titel}`, k: 'warning' as const }
      : s.bucket === 'done' && was === 'working' ? { t: `✅ Afgerond: ${titel}`, k: 'success' as const } : null;
    if (!m) continue;
    const g = useGame.getState();
    useGame.setState((d: Any) => { d.notifications.unshift({ id: `m${Date.now()}${Math.random().toString(36).slice(2, 6)}`, tick: d.tick ?? 0, text: m.t, kind: m.k, read: false, link: 'threads' }); if (d.notifications.length > 80) d.notifications.length = 80; });
    g.toast(m.t, m.k === 'warning' ? 'warning' : m.k === 'approval' ? 'info' : 'success');
  }
  meldReady = true;
});

/* ================= gesprekken ================= */
export interface Msg { id: string; who: 'niels' | 'claude' | 'keuze' | 'checklist' | 'systeem'; text: string; at: string; author?: string; options?: string[] }
const ENT: Record<string, string> = { '&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"', '&#39;': "'", '&apos;': "'" };
const dec = (s: string) => s.replace(/&(lt|gt|amp|quot|#39|apos);/g, (m) => ENT[m] ?? m);
const attr = (attrs: string, k: string) => new RegExp(`\\b${k}="([^"]*)"`).exec(attrs)?.[1];
function textOf(content: Any): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) return content.filter((b: Any) => b?.type === 'text').map((b: Any) => b.text ?? '').join('\n');
  return '';
}

/** zet de ruwe gebeurtenissen om in berichten (wat niels schreef en wat Claude hem antwoordde) */
export function parseEvents(events: Any[]): Msg[] {
  const out: Msg[] = [];
  for (const ev of events) {
    const at: string = ev?.created_at ?? '';
    const u = ev?.user?.internal_anthropic_catchall?.message ?? ev?.user?.message;
    const a = ev?.assistant?.internal_anthropic_catchall?.message ?? ev?.assistant?.message;
    if (u) {
      const c = u.content;
      if (Array.isArray(c) && c.some((b: Any) => b?.type === 'tool_result')) continue; // uitvoer van gereedschap
      const t = textOf(c); if (!t) continue;
      const seenText = new Set<string>();
      // berichten van niels in een wake (thread of projectchat)
      for (const mm of t.matchAll(/<message\b([^>]*)>([\s\S]*?)<\/message>/g)) {
        const at2 = mm[1]; if (attr(at2, 'from') !== 'human') continue;
        const body = dec(mm[2].trim()); if (!body || seenText.has(body)) continue; seenText.add(body);
        out.push({ id: `${ev.user?.uuid ?? at}:${out.length}`, who: 'niels', text: body, at, author: attr(at2, 'author') });
      }
      // het eerste bericht van een thread komt als citaat via de coördinator
      for (const mm of t.matchAll(/<cited\b([^>]*)>([\s\S]*?)<\/cited>/g)) {
        const body = dec(mm[2].trim()); if (!body || seenText.has(body)) continue; seenText.add(body);
        out.push({ id: `${ev.user?.uuid ?? at}:c${out.length}`, who: 'niels', text: body, at, author: attr(mm[1], 'author') === 'user' ? 'niels' : attr(mm[1], 'author') });
      }
      // keuze op een beslissingskaart
      for (const mm of t.matchAll(/<decision\b([^>]*)>([\s\S]*?)<\/decision>/g)) out.push({ id: `${ev.user?.uuid ?? at}:d${out.length}`, who: 'keuze', text: dec(mm[2].trim()) || (attr(mm[1], 'chose') ?? ''), at });
      continue;
    }
    if (a && Array.isArray(a.content)) {
      for (const b of a.content) {
        if (b?.type !== 'tool_use') continue;
        const n: string = b.name ?? ''; const inp = b.input ?? {};
        if (/hearthbot__post_message$/.test(n) && inp.text) out.push({ id: b.id, who: 'claude', text: String(inp.text), at });
        else if (/hearthbot__edit_message$/.test(n) && inp.text) out.push({ id: b.id, who: 'systeem', text: `Bericht aangepast: ${String(inp.text).slice(0, 400)}`, at });
        else if (/hearthbot__request_decision$/.test(n)) out.push({ id: b.id, who: 'keuze', text: String(inp.question ?? 'Keuze'), options: (inp.options ?? []).map((o: Any) => `${o.label}${o.consequence ? `: ${o.consequence}` : ''}`), at });
        else if (/hearthbot__update_progress_checklist$/.test(n) && inp.text) out.push({ id: b.id, who: 'checklist', text: String(inp.text), at });
        else if (/hearthbot__post_widget$/.test(n)) out.push({ id: b.id, who: 'systeem', text: 'Claude stuurde een kaart (bijv. een concept om te versturen).', at });
      }
    }
  }
  return out;
}

export interface Page { msgs: Msg[]; firstId?: string; lastId?: string; hasMore: boolean }
/** één bladzijde (100 gebeurtenissen) van een sessie; zonder cursor de nieuwste */
export async function loadPage(session: string, cur?: { before?: string; after?: string }): Promise<Page> {
  const m = await mcp(); if (!m) throw Object.assign(new Error('geen connector'), { code: 'geen' });
  const input: Record<string, unknown> = { session_id: session, kinds: ['user', 'assistant'], limit: 100 };
  if (cur?.before) input.before_id = cur.before; if (cur?.after) input.after_id = cur.after;
  const r = unwrap(await m.callTool(SERVER, 'list_events', input, cur?.before ? { cache: { staleTime: 10 * 60000, gcTime: 10 * 60000 } } : { cache: false }));
  const data: Any[] = Array.isArray(r?.data) ? r.data : [];
  return { msgs: parseEvents(data), firstId: r?.first_id, lastId: r?.last_id, hasMore: !!r?.has_more };
}
