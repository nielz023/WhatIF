/**
 * GEREEDSCHAP LIVE: leest je eigen tools uit via je claude.ai-connectors
 * (mcp-capability, met jouw eigen inlog). Alleen leesacties.
 */
import { create } from 'zustand';

export const CHANNEL_ID = 'UCJhUg9hdXlhRRc7GBU_nRgg';
type St = { status: 'laden' | 'ok' | 'fout' | 'geen'; data?: unknown; error?: string; at?: number };
interface S { tools: Record<string, St>; refresh: () => Promise<void> }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let mcp: any = undefined;
const MIN = 60000;
const CALLS: { key: string; server: string; tool: string; input: Record<string, unknown>; stale: number }[] = [
  { key: 'elevenlabs', server: 'ElevenLabs', tool: 'creative_list_flows', input: { context: 'Driftmark HQ toont de laatste stem-flows', page_size: 6 }, stale: 10 * MIN },
  { key: 'vidiq', server: 'vidIQ', tool: 'vidiq_balance', input: {}, stale: 30 * MIN },
  { key: 'vidiqch', server: 'vidIQ', tool: 'vidiq_user_channels', input: {}, stale: 60 * MIN },
  { key: 'higgsfield', server: 'Higgsfield', tool: 'balance', input: {}, stale: 30 * MIN },
  // NexLev heeft een weeklimiet (gratis: 50 calls), dus maximaal 1x per 6 uur
  { key: 'nexlev', server: 'NexLev', tool: 'youtube_channel_about', input: { channel_id: CHANNEL_ID }, stale: 360 * MIN },
];

export const useTools = create<S>((set, get) => ({
  tools: Object.fromEntries(CALLS.map((c) => [c.key, { status: 'laden' }])),
  refresh: async () => {
    try {
      if (mcp === undefined) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const c = (window as any).claude;
        mcp = c?.use ? await c.use('mcp') : null;
      }
    } catch { mcp = null; }
    if (!mcp) { set({ tools: Object.fromEntries(CALLS.map((c) => [c.key, { status: 'geen' as const }])) }); return; }
    for (const c of CALLS) {
      try {
        const r = await mcp.callTool(c.server, c.tool, c.input, { cache: { staleTime: c.stale, gcTime: Math.max(c.stale, 5 * MIN) } });
        let data = r?.payload;
        if (data === undefined) {
          const txt = r?.content?.find((b: { type: string; text?: string }) => b.type === 'text')?.text;
          try { data = txt ? JSON.parse(txt) : txt; } catch { data = txt; }
        }
        set({ tools: { ...get().tools, [c.key]: { status: 'ok', data, at: Date.now() } } });
      } catch (e) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const err = e as any;
        set({ tools: { ...get().tools, [c.key]: { status: 'fout', error: err?.message ?? err?.code ?? 'fout', at: Date.now() } } });
      }
    }
  },
}));

let started = false;
export function startTools() {
  if (started) return; started = true;
  setTimeout(() => void useTools.getState().refresh(), 2500);
  setInterval(() => void useTools.getState().refresh(), 10 * MIN);
}

/** Zoek een getal op naam in een onbekend antwoord (NexLev-vorm is nog niet gecontroleerd). */
export function findNum(o: unknown, re: RegExp, depth = 0): number | null {
  if (!o || typeof o !== 'object' || depth > 4) return null;
  for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
    if (re.test(k) && (typeof v === 'number' || (typeof v === 'string' && /^[\d.,]+[KkMm]?$/.test(v)))) {
      if (typeof v === 'number') return v;
      const n = parseFloat(v.replace(/,/g, '')); const m = /[Kk]$/.test(v) ? 1e3 : /[Mm]$/.test(v) ? 1e6 : 1; return Math.round(n * m);
    }
  }
  for (const v of Object.values(o as Record<string, unknown>)) { const r = findNum(v, re, depth + 1); if (r !== null) return r; }
  return null;
}
