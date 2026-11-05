import { play } from '../world/sound';
/**
 * ECHT-MODUS: acties in de app worden echte opdrachten voor Claude.
 * Elke actie wordt als reactie op de pagina geplaatst en naar Claude gestuurd
 * (comments.sendToClaude). Claude voert hem dan in het project echt uit.
 * Lukt versturen niet, dan blijft de opdracht in de wachtrij (alleen in deze browser).
 */
import { create } from 'zustand';

export interface Order { id: string; at: number; text: string; status: 'verstuurd' | 'wachtrij' | 'fout'; reason?: string }
type Avail = 'laden' | 'available' | 'writers_only' | 'no_session' | 'off' | 'geen';

const KEY = 'driftmark-orders';
const load = (): Order[] => { try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch { return []; } };
const save = (o: Order[]) => { try { localStorage.setItem(KEY, JSON.stringify(o.slice(0, 100))); } catch { /* ignore */ } };

interface RealState { orders: Order[]; avail: Avail; refresh: () => Promise<void>; send: (text: string) => Promise<Order>; resend: (id: string) => Promise<void> }

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let cm: any = null;
const ready: Promise<void> = (async () => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const c = (window as any).claude;
    cm = c?.use ? await c.use('comments') : null;
  } catch { cm = null; }
})();

async function deliver(text: string): Promise<{ ok: boolean; reason?: string }> {
  if (!cm) return { ok: false, reason: 'Versturen kan alleen op de gepubliceerde pagina in claude.ai.' };
  try {
    const st = await cm.canSendToClaude();
    if (st !== 'available') return { ok: false, reason: st === 'no_session' ? 'Claude luistert nu niet mee; de opdracht wacht.' : st === 'writers_only' ? 'Alleen de eigenaar kan opdrachten sturen.' : 'Versturen staat hier uit.' };
    const el = document.getElementById('orders-anchor') ?? document.getElementById('root')!;
    const anchor = await cm.anchorFor(el);
    await cm.sendToClaude({ anchor, text: text.slice(0, 3800) });
    return { ok: true };
  } catch (e) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const code = (e as any)?.code ?? 'fout';
    return { ok: false, reason: code === 'rate_limited' ? 'Te snel achter elkaar; probeer zo opnieuw.' : `Niet verstuurd (${code}).` };
  }
}

export const useReal = create<RealState>((set, get) => ({
  orders: load(),
  avail: 'laden',
  refresh: async () => {
    await ready;
    if (!cm) { set({ avail: 'geen' }); return; }
    try { set({ avail: await cm.canSendToClaude() }); } catch { set({ avail: 'off' }); }
  },
  send: async (text) => {
    const o: Order = { id: Math.random().toString(36).slice(2), at: Date.now(), text, status: 'wachtrij' };
    const orders = [o, ...get().orders]; set({ orders }); save(orders);
    const r = await deliver(`[DRIFTMARK HQ · ECHTE OPDRACHT]\n${text}`);
    const upd = get().orders.map((x) => (x.id === o.id ? { ...x, status: r.ok ? 'verstuurd' as const : 'wachtrij' as const, reason: r.reason } : x));
    set({ orders: upd }); save(upd);
    return { ...o, status: r.ok ? 'verstuurd' : 'wachtrij', reason: r.reason };
  },
  resend: async (id) => {
    const o = get().orders.find((x) => x.id === id); if (!o) return;
    const r = await deliver(`[DRIFTMARK HQ · ECHTE OPDRACHT]\n${o.text}`);
    const upd = get().orders.map((x) => (x.id === id ? { ...x, status: r.ok ? 'verstuurd' as const : 'wachtrij' as const, reason: r.reason } : x));
    set({ orders: upd }); save(upd);
  },
}));

void useReal.getState().refresh();
setInterval(() => void useReal.getState().refresh(), 30000);

/** Stuurt een opdracht en laat een toast zien in de game. */
export function order(text: string, toast?: (t: string, k?: 'success' | 'info' | 'warning') => void) {
  play('send');
  void useReal.getState().send(text).then((o) => {
    toast?.(o.status === 'verstuurd' ? '✅ Echte opdracht naar Claude gestuurd' : `⏳ Opdracht in de wachtrij: ${o.reason ?? ''}`, o.status === 'verstuurd' ? 'success' : 'warning');
  });
}
