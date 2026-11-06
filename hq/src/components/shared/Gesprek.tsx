/**
 * HET HELE GESPREK van een thread of van de projectchat (niels 2026-11-06: "voeg allle 2 de kanttekeningen toe").
 * Leest via de connector "Claude Code Remote" alles wat niels schreef en wat Claude antwoordde, met de
 * nieuwste berichten onderaan. "Ouder laden" bladert terug tot het allereerste bericht; terwijl het paneel
 * open is komen nieuwe berichten er elke 20 seconden vanzelf bij. Bij de projectchat lopen we na de huidige
 * coördinator door naar de vorige (de projectchat wisselt af en toe van sessie).
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ExternalLink, MessageSquare, RefreshCw, X } from 'lucide-react';
import { create } from 'zustand';
import { loadPage, loadSession, useThreads, type Msg } from '../../services/threads';
import { threadUrl } from '../../data/driftmark';
import { useLive } from '../../services/live';

interface G { open: { kind: 'thread' | 'project'; session?: string; title: string; thread?: string } | null; show: (o: G['open']) => void }
export const useGesprek = create<G>((set) => ({ open: null, show: (open) => set({ open }) }));
export const openGesprek = (o: NonNullable<G['open']>) => useGesprek.getState().show(o);

// alle tijden in de tijd van niels (Nederland), ook de indeling per dag; de connector geeft UTC
const TZ = 'Europe/Amsterdam';
const fmt = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? '' : d.toLocaleString('nl-NL', { timeZone: TZ, weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); };
const dayKey = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? '' : d.toLocaleDateString('sv-SE', { timeZone: TZ }); };
const dayLabel = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? '' : d.toLocaleDateString('nl-NL', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' }); };

/** tekst met klikbare links ([tekst](url) en losse https-adressen) en **vet** */
function Rich({ text }: { text: string }) {
  const parts = useMemo(() => {
    const out: (string | { t: string; href?: string; b?: boolean })[] = [];
    const re = /\[([^\]]+)\]\((https?:\/\/[^)\s]+|#[^)\s]+|\/mnt\/[^)\s]+)\)|(https?:\/\/[^\s)]+)|\*\*([^*]+)\*\*/g;
    let last = 0; let m: RegExpExecArray | null;
    while ((m = re.exec(text))) {
      if (m.index > last) out.push(text.slice(last, m.index));
      if (m[1]) out.push({ t: m[1], href: /^https?:/.test(m[2]) ? m[2] : undefined });
      else if (m[3]) out.push({ t: m[3], href: m[3] });
      else if (m[4]) out.push({ t: m[4], b: true });
      last = m.index + m[0].length;
    }
    if (last < text.length) out.push(text.slice(last));
    return out;
  }, [text]);
  return <>{parts.map((p, i) => typeof p === 'string' ? <span key={i}>{p}</span> : p.href ? <a key={i} href={p.href} target="_blank" rel="noreferrer" className="text-sky-300 underline hover:text-white">{p.t}</a> : p.b ? <b key={i} className="text-white">{p.t}</b> : <span key={i} className="text-sky-200">{p.t}</span>)}</>;
}

function Bubble({ m }: { m: Msg }) {
  if (m.who === 'systeem') return <div className="mx-auto max-w-[90%] text-center text-[11px] italic text-slate-500">{m.text}</div>;
  const me = m.who === 'niels';
  if (m.who === 'keuze') return (
    <div className="mx-auto w-full max-w-[92%] rounded-xl border border-amber-400/30 bg-amber-400/[.07] p-3 text-[13px] text-slate-200">
      <div className="mb-1 text-[11px] font-bold uppercase tracking-wider text-amber-300">{m.options ? 'Keuze voor jou' : 'Gekozen'}</div>
      <div className="whitespace-pre-wrap"><Rich text={m.text} /></div>
      {m.options && <ul className="mt-1.5 space-y-0.5 text-[12px] text-slate-300">{m.options.map((o, i) => <li key={i}>• {o}</li>)}</ul>}
      <div className="mt-1 text-right text-[10px] text-slate-500">{fmt(m.at)}</div>
    </div>
  );
  return (
    <div className={`flex ${me ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[86%] rounded-2xl px-3.5 py-2 text-[13.5px] leading-relaxed shadow ${me ? 'rounded-br-md bg-orange-500/90 text-white' : 'rounded-bl-md border border-white/10 bg-[#121a36] text-slate-100'}`}>
        <div className="whitespace-pre-wrap break-words"><Rich text={m.text} /></div>
        <div className={`mt-1 text-[10px] ${me ? 'text-orange-100/80' : 'text-slate-500'}`}>{me ? (m.author ?? 'niels') : 'Claude'} · {fmt(m.at)}</div>
      </div>
    </div>
  );
}

/** Checklist van de thread zoals Claude hem bijhoudt (✓ klaar, ✱ bezig, ○ nog niet). */
function Checklist({ text }: { text: string }) {
  const lines = text.split('\n').filter((l) => l.trim());
  const [head, ...rest] = lines;
  return (
    <div className="rounded-xl border border-white/10 bg-white/[.03] p-3 text-[12.5px]">
      <div className="mb-1 font-semibold text-white">{head}</div>
      {rest.map((l, i) => { const c = l.trim()[0]; const col = c === '✓' ? '#21D6A0' : c === '✱' ? '#398CFF' : '#64748B'; return <div key={i} className="flex gap-1.5 text-slate-300"><span style={{ color: col }}>{c}</span><span className="min-w-0">{l.trim().slice(1).trim()}</span></div>; })}
    </div>
  );
}

export default function GesprekDrawer() {
  const open = useGesprek((s) => s.open); const close = () => useGesprek.getState().show(null);
  const sessions = useThreads((s) => s.sessions); const coordsLive = useThreads((s) => s.coordinators); const src = useThreads((s) => s.src);
  const coordsFile = useLive((s) => s.data.coordinator);
  const coords = useMemo(() => [...new Set([...(coordsLive ?? []), ...(coordsFile ?? [])])], [coordsLive, coordsFile]);
  const chain = useMemo(() => (open?.kind === 'project' ? coords : open?.session ? [open.session] : []), [open, coords]);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [state, setState] = useState<{ busy: boolean; err?: string; more: boolean; idx: number; first?: string; last?: string; scanned: number }>({ busy: false, more: false, idx: 0, scanned: 0 });
  const box = useRef<HTMLDivElement>(null); const stick = useRef(true); const st = useRef(state); st.current = state;
  const key = open ? `${open.kind}:${open.session ?? ''}` : '';
  const chainKey = chain.join(',');
  const chainRef = useRef(chain); chainRef.current = chain;
  // elke keer dat het paneel een ander gesprek toont gaat dit omhoog; een lading van het vorige gesprek die
  // nog onderweg is, ziet dan dat hij te laat is en schrijft niets meer weg
  const gen = useRef(0);

  const sess = open?.session ? sessions[open.session] : undefined;
  useEffect(() => { if (open?.session) void loadSession(open.session); }, [open?.session]);

  // laden: nieuwste bladzijde; als er weinig berichten op staan, meteen verder terug
  const older = async (fresh = false) => {
    const s0 = fresh ? { busy: false, more: true, idx: 0, scanned: 0 } as typeof state : st.current;
    const chain = chainRef.current; const my = gen.current;
    if (!chain.length || s0.busy) return;
    setState({ ...s0, busy: true, err: undefined });
    let { idx, first, more, scanned } = s0; let last = fresh ? undefined : s0.last;
    const got: Msg[] = []; let pages = 0;
    try {
      while (pages < 6 && got.length < 12 && idx < chain.length) {
        const p = await loadPage(chain[idx], first ? { before: first } : undefined); pages++; scanned++;
        if (my !== gen.current) return; // intussen een ander gesprek geopend
        if (!first && idx === 0) last = p.lastId;
        got.unshift(...p.msgs); first = p.firstId;
        more = p.hasMore;
        if (!p.hasMore) { idx++; first = undefined; more = idx < chain.length; }
      }
      const prevH = box.current?.scrollHeight ?? 0;
      setMsgs((m) => (fresh ? got : [...got, ...m]));
      setState({ busy: false, more, idx, first, last, scanned });
      if (!fresh) requestAnimationFrame(() => { if (box.current) box.current.scrollTop = box.current.scrollHeight - prevH; });
    } catch (e) {
      if (my !== gen.current) return;
      const code = (e as { code?: string })?.code;
      setState({ ...s0, busy: false, err: code === 'geen' || code === 'server_not_connected' ? 'geen' : code === 'needs_reauth' ? 'reauth' : code === 'not_in_manifest' ? 'nietToegestaan' : 'fout' });
    }
  };
  useEffect(() => { gen.current++; setMsgs([]); stick.current = true; if (open) void older(true); /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [key, chainKey]);

  // nieuwe berichten: elke 20 s de nieuwste gebeurtenissen erbij (bij een drukke beurt meerdere bladzijden)
  useEffect(() => {
    if (!open || !chainKey) return;
    let polling = false;
    const t = setInterval(async () => {
      const s = st.current; if (polling || s.busy || !s.last) return;
      const my = gen.current; const session = chainRef.current[0]; if (!session) return;
      polling = true;
      try {
        let last = s.last; const got: Msg[] = [];
        for (let i = 0; i < 5; i++) {
          const p = await loadPage(session, { after: last });
          if (my !== gen.current) return;
          got.push(...p.msgs); if (p.lastId) last = p.lastId;
          if (!p.hasMore || !p.lastId) break;
        }
        if (last !== s.last) setState((x) => ({ ...x, last }));
        if (got.length) setMsgs((m) => { const ids = new Set(m.map((x) => x.id)); return [...m, ...got.filter((x) => !ids.has(x.id))]; });
      } catch { /* volgende keer */ } finally { polling = false; }
    }, 20000);
    return () => clearInterval(t);
  }, [open, chainKey]);

  // onderaan blijven als je onderaan was
  useEffect(() => { const b = box.current; if (b && stick.current) b.scrollTop = b.scrollHeight; }, [msgs.length]);
  // Esc sluit alleen het gesprek (en niet ook nog het paneel of de afdeling eronder): vangen vóór de app-brede Esc
  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape' && useGesprek.getState().open) { e.stopPropagation(); close(); } };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, []);

  const shown = msgs.filter((m) => m.who !== 'checklist');
  const lastChecklist = sess?.checklist ?? [...msgs].reverse().find((m) => m.who === 'checklist')?.text;
  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[70] flex justify-end bg-black/40 backdrop-blur-[2px]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={close}>
          <motion.aside className="flex h-full w-full max-w-[560px] flex-col border-l border-white/10 bg-[#0a1024]/97 shadow-2xl" initial={{ x: 60, opacity: 0.6 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 60, opacity: 0 }} transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }} onClick={(e) => e.stopPropagation()}>
            <header className="flex items-start gap-3 border-b border-white/10 px-4 py-3">
              <MessageSquare size={18} className="mt-1 shrink-0 text-orange-300" />
              <div className="min-w-0 flex-1">
                <div className="truncate font-display text-[17px] font-bold text-white">{open.kind === 'project' ? 'Projectchat' : open.title}</div>
                <div className="flex flex-wrap items-center gap-x-2 text-[12px] text-slate-400">
                  {src === 'live' ? <span className="text-[#3ddc97]">● live</span> : <span>stand uit het uurbestand</span>}
                  {sess?.bucket && <span>· {({ working: 'bezig', blocked: 'wacht op jou', review_ready: 'klaar voor jou', done: 'klaar', failed: 'mislukt', idle: 'rust' } as const)[sess.bucket]}</span>}
                  {open.kind === 'project' && <span>· {coords.length} {coords.length === 1 ? 'sessie' : 'sessies'}</span>}
                </div>
              </div>
              {open.thread && <a href={threadUrl(open.thread)} target="_blank" rel="noreferrer" className="btn-ghost !px-2 !py-1 text-[12px]" title="Open de thread in Claude"><ExternalLink size={13} />Open</a>}
              <button onClick={close} className="rounded-lg border border-white/10 p-1.5 text-slate-300 hover:text-white" aria-label="Sluiten"><X size={16} /></button>
            </header>
            {(sess?.needs || lastChecklist) && (
              <div className="space-y-2 border-b border-white/[.06] px-4 py-3">
                {sess?.needs && <div className="rounded-xl border border-orange-400/40 bg-orange-500/10 px-3 py-2 text-[13px] text-orange-100"><b className="text-orange-300">Wacht op jou: </b>{sess.needs}</div>}
                {lastChecklist && <Checklist text={lastChecklist} />}
              </div>
            )}
            <div ref={box} className="min-h-0 flex-1 space-y-2.5 overflow-y-auto px-4 py-3" onScroll={(e) => { const b = e.currentTarget; stick.current = b.scrollHeight - b.scrollTop - b.clientHeight < 60; }}>
              {state.more && <div className="text-center"><button className="btn-ghost text-[12px]" disabled={state.busy} onClick={() => void older()}>{state.busy ? <><RefreshCw size={12} className="animate-spin" />Laden…</> : 'Oudere berichten laden'}</button></div>}
              {!state.more && shown.length > 0 && <div className="text-center text-[11px] text-slate-500">Begin van het gesprek</div>}
              {state.err === 'geen' && <div className="rounded-xl border border-white/10 bg-white/[.03] p-3 text-[13px] text-slate-300">Het gesprek is hier alleen te lezen als de connector <b>Claude Code Remote</b> aan staat voor deze pagina (claude.ai → Instellingen → Connectors). {open.thread && <a className="text-sky-300 underline" href={threadUrl(open.thread)} target="_blank" rel="noreferrer">Open de thread in Claude</a>}</div>}
              {state.err === 'reauth' && <div className="rounded-xl border border-orange-400/40 bg-orange-500/10 p-3 text-[13px] text-orange-100">Log opnieuw in bij Claude Code Remote (claude.ai → Instellingen → Connectors), dan verschijnt het gesprek hier.</div>}
              {state.err === 'nietToegestaan' && <div className="rounded-xl border border-white/10 bg-white/[.03] p-3 text-[13px] text-slate-300">Je hebt Claude Code Remote voor deze pagina uitgezet. Zet hem aan via het menu Rechten van deze pagina om de gesprekken te lezen.</div>}
              {state.err === 'fout' && <div className="rounded-xl border border-white/10 bg-white/[.03] p-3 text-[13px] text-slate-300">Het gesprek kon nu niet geladen worden. <button className="text-sky-300 underline" onClick={() => void older(true)}>Opnieuw proberen</button></div>}
              {state.busy && !shown.length && <div className="py-10 text-center text-[13px] text-slate-400"><RefreshCw size={16} className="mx-auto mb-2 animate-spin" />Gesprek laden…</div>}
              {!state.busy && !state.err && !shown.length && !state.more && <div className="py-10 text-center text-[13px] text-slate-500">Nog geen berichten.</div>}
              {shown.map((m, i) => (
                <div key={m.id + i}>
                  {(i === 0 || dayKey(shown[i - 1].at) !== dayKey(m.at)) && <div className="my-2 text-center text-[11px] font-semibold uppercase tracking-wider text-slate-500">{dayLabel(m.at)}</div>}
                  <Bubble m={m} />
                </div>
              ))}
            </div>
          </motion.aside>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
