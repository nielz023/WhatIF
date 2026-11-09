import { play } from '../world/sound';
/**
 * ECHT-MODUS: acties in de app worden echte opdrachten voor Claude.
 * Elke actie wordt als reactie op de pagina geplaatst en naar Claude gestuurd
 * (comments.sendToClaude). Claude voert hem dan in het project echt uit.
 * Lukt versturen niet, dan blijft de opdracht in de wachtrij (alleen in deze browser).
 *
 * Verbeterlijst punt 2 en 3: elke opdracht krijgt een kenmerk (ref, bv. "o-k3f9"). Claude zet in
 * driftmark-hq/status.json onder replies[] een regel met dezelfde ref en een stand
 * (ontvangen, bezig, klaar). Zo ziet niels per opdracht waar hij staat. Het mandje verzamelt
 * opdrachten en verstuurt ze samen, met één toestemmingsklik van claude.ai.
 */
import { create } from 'zustand';

export interface Order {
  id: string; at: number; text: string; status: 'verstuurd' | 'wachtrij' | 'fout'; reason?: string;
  /** kenmerk dat Claude terugzet in het antwoord */ ref?: string;
  /** afdeling of thread waar het heen moet */ doel?: string; thread?: string;
}
export interface MandItem { id: string; text: string; doel?: string; thread?: string }
type Avail = 'laden' | 'available' | 'writers_only' | 'no_session' | 'off' | 'geen';

const KEY = 'driftmark-orders';
const MKEY = 'driftmark-mandje';
const load = <T,>(k: string): T[] => { try { return JSON.parse(localStorage.getItem(k) || '[]'); } catch { return []; } };
const save = (k: string, o: unknown[]) => { try { localStorage.setItem(k, JSON.stringify(o.slice(0, 100))); } catch { /* ignore */ } };
const nieuweRef = () => 'o-' + Math.random().toString(36).slice(2, 6);

interface RealState {
  orders: Order[]; mandje: MandItem[]; avail: Avail;
  refresh: () => Promise<void>;
  send: (text: string, opts?: { doel?: string; thread?: string }) => Promise<Order>;
  resend: (id: string) => Promise<void>;
  inMandje: (text: string, opts?: { doel?: string; thread?: string }) => void;
  uitMandje: (id: string) => void;
  verstuurMandje: () => Promise<boolean>;
}

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
  await ready;
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

/** de tekst zoals Claude hem krijgt */
function bericht(o: Pick<Order, 'text' | 'ref' | 'doel' | 'thread'>) {
  const kop = [o.ref ? `ref ${o.ref}` : '', o.doel ? `afdeling ${o.doel}` : '', o.thread ? `thread ${o.thread}` : ''].filter(Boolean).join(' · ');
  return `${kop ? `(${kop})\n` : ''}${o.text}`;
}
const KOP = '[DRIFTMARK HQ · ECHTE OPDRACHT]';

export const useReal = create<RealState>((set, get) => ({
  orders: load<Order>(KEY),
  mandje: load<MandItem>(MKEY),
  avail: 'laden',
  refresh: async () => {
    await ready;
    if (!cm) { set({ avail: 'geen' }); return; }
    try { set({ avail: await cm.canSendToClaude() }); } catch { set({ avail: 'off' }); }
  },
  send: async (text, opts = {}) => {
    const o: Order = { id: Math.random().toString(36).slice(2), at: Date.now(), text, status: 'wachtrij', ref: nieuweRef(), ...opts };
    const orders = [o, ...get().orders]; set({ orders }); save(KEY, orders);
    const r = await deliver(`${KOP}\n${bericht(o)}`);
    const upd = get().orders.map((x) => (x.id === o.id ? { ...x, status: r.ok ? 'verstuurd' as const : 'wachtrij' as const, reason: r.reason } : x));
    set({ orders: upd }); save(KEY, upd);
    return { ...o, status: r.ok ? 'verstuurd' : 'wachtrij', reason: r.reason };
  },
  resend: async (id) => {
    const o = get().orders.find((x) => x.id === id); if (!o) return;
    const r = await deliver(`${KOP}\n${bericht(o)}`);
    const upd = get().orders.map((x) => (x.id === id ? { ...x, status: r.ok ? 'verstuurd' as const : 'wachtrij' as const, reason: r.reason } : x));
    set({ orders: upd }); save(KEY, upd);
  },
  inMandje: (text, opts = {}) => {
    const m = [...get().mandje, { id: Math.random().toString(36).slice(2), text, ...opts }];
    set({ mandje: m }); save(MKEY, m);
  },
  uitMandje: (id) => { const m = get().mandje.filter((x) => x.id !== id); set({ mandje: m }); save(MKEY, m); },
  verstuurMandje: async () => {
    const m = get().mandje; if (!m.length) return false;
    const nu = Date.now();
    const nieuw: Order[] = m.map((x, i) => ({ id: x.id, at: nu + i, text: x.text, doel: x.doel, thread: x.thread, ref: nieuweRef(), status: 'wachtrij' }));
    const tekst = `${KOP} · ${nieuw.length} opdrachten tegelijk\n\n` + nieuw.map((o, i) => `${i + 1}. ${bericht(o)}`).join('\n\n');
    const orders = [...nieuw.reverse(), ...get().orders]; set({ orders }); save(KEY, orders);
    const r = await deliver(tekst);
    const refs = new Set(nieuw.map((o) => o.id));
    const upd = get().orders.map((x) => (refs.has(x.id) ? { ...x, status: r.ok ? 'verstuurd' as const : 'wachtrij' as const, reason: r.reason } : x));
    set({ orders: upd, mandje: r.ok ? [] : m }); save(KEY, upd); if (r.ok) save(MKEY, []);
    return r.ok;
  },
}));

void useReal.getState().refresh();
setInterval(() => void useReal.getState().refresh(), 30000);

/** Stuurt een opdracht en laat een toast zien in de game. */
export function order(text: string, toast?: (t: string, k?: 'success' | 'info' | 'warning') => void, opts?: { doel?: string; thread?: string }) {
  play('send');
  void useReal.getState().send(text, opts).then((o) => {
    toast?.(o.status === 'verstuurd' ? '✅ Opdracht doorgegeven aan Claude. Je volgt hem onder Mijn opdrachten (toets K).' : `⏳ Opdracht in de wachtrij: ${o.reason ?? ''}`, o.status === 'verstuurd' ? 'success' : 'warning');
  });
}

/** opent de opdrachtbalk, eventueel met een tekst of doel erin */
export function openOpdracht(d: { text?: string; doel?: string; thread?: string; titel?: string; tab?: 'nieuw' | 'mijn' } = {}) {
  window.dispatchEvent(new CustomEvent('dm-opdracht', { detail: d }));
}
