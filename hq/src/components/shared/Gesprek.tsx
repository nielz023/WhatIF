/**
 * HET HELE GESPREK van een thread of van de projectchat (v35: uit de projectbestanden, niet meer uit een connector).
 * Claude zet elk gesprek ongeveer elk uur als bestand in driftmark-hq/gesprekken/ (zie services/threads.ts). Het
 * paneel leest dat bestand zodra het opengaat en daarna elke minuut, zolang het open blijft. Oudste berichten
 * bovenaan, nieuwste onderaan. Staat niet alles in het bestand, dan staat bovenaan waar de rest te lezen is.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown, ExternalLink, ListChecks, MessageSquare, RefreshCw, X } from 'lucide-react';
import { create } from 'zustand';
import { loadGesprek, stateOf, useThreads, wanneerNl, type GesprekBestand, type Msg } from '../../services/threads';
import { threadUrl } from '../../data/driftmark';
import { useLive } from '../../services/live';
import { order } from '../../services/real';
import { useGame } from '../../store/useGame';
import { useAfkeuren } from './Afkeuren';

interface G {
  /** kind 'thread': thread is de thread-id (cmsg_...). session is van vroeger en wordt niet meer gebruikt. */
  open: { kind: 'thread' | 'project'; title: string; thread?: string; session?: string } | null;
  show: (o: G['open']) => void;
}
export const useGesprek = create<G>((set) => ({ open: null, show: (open) => set({ open }) }));
export const openGesprek = (o: NonNullable<G['open']>) => useGesprek.getState().show(o);

// alle tijden in de tijd van niels (Nederland), ook de indeling per dag; de bestanden geven UTC
const TZ = 'Europe/Amsterdam';
const fmt = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? '' : d.toLocaleString('nl-NL', { timeZone: TZ, weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }); };
const dayKey = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? '' : d.toLocaleDateString('sv-SE', { timeZone: TZ }); };
const dayLabel = (iso: string) => { const d = new Date(iso); return isNaN(+d) ? '' : d.toLocaleDateString('nl-NL', { timeZone: TZ, weekday: 'long', day: 'numeric', month: 'long' }); };
const PROJECT_URL = threadUrl('').replace(/\?.*$/, '');
const STAND: Record<string, string> = { working: 'bezig', blocked: 'wacht op jou', review_ready: 'klaar voor jou', done: 'klaar', failed: 'mislukt', stopped: 'gestopt' };
/** al om gevraagd in deze sessie (knop "Nu ophalen"), zodat niels niet twee keer dezelfde opdracht stuurt */
const gevraagdOp = new Set<string>();

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

const KLEUR: Record<string, string> = { '✓': '#21D6A0', '✱': '#398CFF', '○': '#64748B' };
/** Checklist zoals Claude hem bijhoudt (✓ klaar, ✱ bezig, ○ nog niet), als klein blok; alleen de nieuwste staat open. */
function Checklist({ m, open }: { m: Msg; open: boolean }) {
  const [head, ...rest] = m.text.split('\n').map((l) => l.trim()).filter(Boolean);
  const items = rest.map((l) => { const c = l[0]; return KLEUR[c] ? { c, t: l.slice(1).trim() } : { c: '', t: l }; });
  const tel = items.filter((x) => x.c).length; const klaar = items.filter((x) => x.c === '✓').length;
  return (
    <details open={open} className="group mx-auto w-full max-w-[92%] rounded-xl border border-white/10 bg-white/[.03] px-3 py-2 text-[12px]">
      <summary className="flex cursor-pointer list-none items-center gap-2 [&::-webkit-details-marker]:hidden">
        <ListChecks size={13} className="shrink-0 text-sky-300" />
        <span className="min-w-0 flex-1 truncate font-semibold text-white">{head || 'Checklist'}</span>
        {tel > 0 && <span className="shrink-0 text-[11px] text-slate-400">{klaar}/{tel} klaar</span>}
        <span className="shrink-0 text-[10px] text-slate-500">{fmt(m.at)}</span>
        <ChevronDown size={13} className="shrink-0 text-slate-500 transition group-open:rotate-180" />
      </summary>
      <div className="mt-1.5 space-y-0.5 border-t border-white/[.06] pt-1.5">
        {items.map((x, i) => <div key={i} className="flex gap-1.5 text-slate-300">{x.c && <span style={{ color: KLEUR[x.c] }}>{x.c}</span>}<span className="min-w-0">{x.t}</span></div>)}
      </div>
    </details>
  );
}

function Bubble({ m, open }: { m: Msg; open: boolean }) {
  if (m.who === 'systeem') return <div className="mx-auto max-w-[90%] text-center text-[11px] italic leading-snug text-slate-500" title={fmt(m.at)}><Rich text={m.text} /></div>;
  if (m.who === 'checklist') return <Checklist m={m} open={open} />;
  if (m.who === 'keuze') return (
    <div className="mx-auto w-full max-w-[92%] rounded-xl border border-amber-400/30 bg-amber-400/[.07] p-3 text-[13px] text-slate-200">
      <div className="mb-1 text-[11px] font-bold uppercase tracking-wider text-amber-300">{m.options ? 'Keuze voor jou' : 'Gekozen'}</div>
      <div className="whitespace-pre-wrap break-words"><Rich text={m.text} /></div>
      {m.options && <ul className="mt-2 space-y-1">{m.options.map((o, i) => <li key={i} className="rounded-lg border border-amber-400/20 bg-black/20 px-2.5 py-1 text-[12px] text-slate-200"><Rich text={o} /></li>)}</ul>}
      <div className="mt-1 text-right text-[10px] text-slate-500">{m.author ? `${m.author} · ` : ''}{fmt(m.at)}</div>
    </div>
  );
  const me = m.who === 'niels';
  return (
    <div className={`flex ${me ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[86%] rounded-2xl px-3.5 py-2 text-[13.5px] leading-relaxed shadow ${me ? 'rounded-br-md bg-orange-500/90 text-white' : 'rounded-bl-md border border-white/10 bg-[#121a36] text-slate-100'}`}>
        <div className="whitespace-pre-wrap break-words"><Rich text={m.text} /></div>
        <div className={`mt-1 text-[10px] ${me ? 'text-orange-100/80' : 'text-slate-500'}`}>{me ? (m.author ?? 'niels') : 'Claude'} · {fmt(m.at)}</div>
      </div>
    </div>
  );
}

const Uitleg = ({ children }: { children: React.ReactNode }) => <div className="rounded-xl border border-white/10 bg-white/[.03] p-3 text-[13px] leading-relaxed text-slate-300">{children}</div>;

type Fase = { fase: 'laden' } | { fase: 'ok'; g: GesprekBestand } | { fase: 'ontbreekt' } | { fase: 'geen-toegang' } | { fase: 'fout'; code: string } | { fase: 'geen-id' };

export default function GesprekDrawer() {
  const open = useGesprek((s) => s.open); const close = () => useGesprek.getState().show(null);
  const toast = useGame((s) => s.toast);
  const project = open?.kind === 'project';
  const id = !open ? '' : project ? 'projectchat' : open.thread ?? '';
  const info = useThreads((s) => (id ? s.threads[id] : undefined));
  const rij = useLive((s) => (!project && id ? s.data.activity.find((a) => a.id === id) : undefined));
  const [st, setSt] = useState<Fase>({ fase: 'laden' });
  const [poging, setPoging] = useState(0);
  const [, setGevraagd] = useState(0);
  const box = useRef<HTMLDivElement>(null); const stick = useRef(true);

  // lezen bij openen en daarna elke minuut zolang het paneel open is (en de pagina zichtbaar);
  // een lading van een vorig gesprek die nog onderweg is, schrijft niets meer weg
  useEffect(() => {
    if (!open) return;
    stick.current = true;
    if (!id) { setSt({ fase: 'geen-id' }); return; }
    setSt({ fase: 'laden' });
    let weg = false; let loopt = false;
    const lees = async () => {
      if (loopt) return; loopt = true;
      const r = await loadGesprek(id).catch((e) => ({ kind: 'fout' as const, code: String(e?.code ?? 'fout') }));
      loopt = false; if (weg) return;
      setSt((prev) => {
        if (r.kind === 'ok') return prev.fase === 'ok' && JSON.stringify(prev.g) === JSON.stringify(r.g) ? prev : { fase: 'ok', g: r.g };
        if (prev.fase === 'ok' && r.kind === 'fout') return prev; // even niet gelukt: het gesprek dat er stond blijft staan
        return r.kind === 'fout' ? { fase: 'fout', code: r.code } : { fase: r.kind };
      });
    };
    void lees();
    const t = setInterval(() => { if (document.visibilityState === 'visible') void lees(); }, 60000);
    return () => { weg = true; clearInterval(t); };
  }, [open, id, poging]);

  // onderaan blijven als je onderaan was (zo zie je meteen de nieuwste berichten)
  const n = st.fase === 'ok' ? st.g.msgs.length : -1;
  useEffect(() => { const b = box.current; if (b && stick.current) b.scrollTop = b.scrollHeight; }, [n, st.fase]);
  // Esc sluit alleen het gesprek (en niet ook nog het paneel of de afdeling eronder): vangen vóór de app-brede Esc.
  // Staat het Afkeuren-venster open, dan is die Esc voor dat venster.
  useEffect(() => {
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape' && useGesprek.getState().open && !useAfkeuren.getState().open) { e.stopPropagation(); close(); } };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, []);

  const g = st.fase === 'ok' ? st.g : null;
  const laatsteChecklist = useMemo(() => (g ? g.msgs.map((m) => m.who).lastIndexOf('checklist') : -1), [g]);
  const stand = info ? STAND[stateOf(info)] : rij ? STAND[rij.state] : undefined;
  const link = project ? PROJECT_URL : id ? threadUrl(id) : '';
  const waar = project ? 'projectchat' : 'thread';
  const gevraagd = gevraagdOp.has(id);
  const haalOp = () => {
    order(project ? 'Gesprek ophalen: projectchat.' : `Gesprek ophalen: thread ${id}.`, toast);
    gevraagdOp.add(id); setGevraagd((x) => x + 1);
  };
  // achtergrond /[.97]: Tailwind 3 kent /97 niet, dan kwam er geen achtergrond en scheen de pagina erdoorheen
  return (
    <AnimatePresence>
      {open && (
        <motion.div className="fixed inset-0 z-[70] flex justify-end bg-black/40 backdrop-blur-[2px]" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={close}>
          <motion.aside id="dm-gesprek" aria-label={project ? 'Projectchat' : `Gesprek: ${open.title}`} className="flex h-full w-full max-w-[560px] flex-col border-l border-white/10 bg-[#0a1024]/[.97] shadow-2xl" initial={{ x: 60, opacity: 0.6 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 60, opacity: 0 }} transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }} onClick={(e) => e.stopPropagation()}>
            <header className="flex items-start gap-3 border-b border-white/10 px-4 py-3">
              <MessageSquare size={18} className="mt-1 shrink-0 text-orange-300" />
              <div className="min-w-0 flex-1">
                <div className="truncate font-display text-[17px] font-bold text-white">{project ? 'Projectchat' : open.title}</div>
                <div className="flex flex-wrap items-center gap-x-1.5 text-[12px] text-slate-400">
                  {stand && <span className={stand === 'wacht op jou' || stand === 'klaar voor jou' ? 'text-orange-300' : ''}>{stand}</span>}
                  {g?.at ? <span>{stand && '· '}bijgewerkt {wanneerNl(g.at)}</span> : st.fase === 'ontbreekt' ? <span>{stand && '· '}nog niet opgehaald</span> : null}
                  {g && <span>· {g.msgs.length} {g.msgs.length === 1 ? 'bericht' : 'berichten'}</span>}
                </div>
              </div>
              {link && <a href={link} target="_blank" rel="noreferrer" className="btn-ghost !px-2 !py-1 text-[12px]" title={`Open de ${waar} in Claude`}><ExternalLink size={13} />Open</a>}
              <button onClick={close} className="rounded-lg border border-white/10 p-1.5 text-slate-300 hover:text-white" aria-label="Sluiten"><X size={16} /></button>
            </header>
            {rij?.needs && (rij.state === 'blocked' || rij.state === 'review_ready') && (
              <div className="border-b border-white/[.06] px-4 py-3">
                <div className="rounded-xl border border-orange-400/40 bg-orange-500/10 px-3 py-2 text-[13px] text-orange-100"><b className="text-orange-300">Wacht op jou: </b>{rij.needs}</div>
              </div>
            )}
            <div ref={box} className="min-h-0 flex-1 space-y-2.5 overflow-y-auto px-4 py-3" onScroll={(e) => { const b = e.currentTarget; stick.current = b.scrollHeight - b.scrollTop - b.clientHeight < 60; }}>
              {st.fase === 'laden' && <div className="py-10 text-center text-[13px] text-slate-400"><RefreshCw size={16} className="mx-auto mb-2 animate-spin" />Gesprek laden…</div>}
              {st.fase === 'geen-id' && <Uitleg>Bij deze taak hoort geen thread, dus er is hier geen gesprek om te lezen.</Uitleg>}
              {st.fase === 'geen-toegang' && (
                <Uitleg>
                  Het gesprek staat in de projectbestanden, en die kan deze pagina hier niet lezen. Open de HQ in claude.ai en geef de pagina toegang tot de bestanden.
                  {link && <> <a className="text-sky-300 underline hover:text-white" href={link} target="_blank" rel="noreferrer">Of lees het in de {waar} zelf.</a></>}
                </Uitleg>
              )}
              {st.fase === 'ontbreekt' && (
                <div className="mx-auto mt-6 max-w-[400px] rounded-2xl border border-white/10 bg-white/[.03] p-5 text-center">
                  <MessageSquare size={22} className="mx-auto mb-2 text-slate-500" />
                  <div className="text-[14px] leading-relaxed text-slate-200">Dit gesprek is nog niet opgehaald. Het wordt elk uur bijgewerkt.</div>
                  <button className="btn-primary mt-3 text-[13px]" disabled={gevraagd} onClick={haalOp}>{gevraagd ? 'Gevraagd ✓' : 'Nu ophalen'}</button>
                  {gevraagd && <div className="mt-2 text-[12px] text-slate-400">Claude haalt het op. Het gesprek verschijnt hier vanzelf; dit paneel kijkt elke minuut.</div>}
                </div>
              )}
              {st.fase === 'fout' && <Uitleg>Het gesprek kon nu niet geladen worden. <button className="text-sky-300 underline hover:text-white" onClick={() => setPoging((p) => p + 1)}>Opnieuw proberen</button></Uitleg>}
              {g && (g.hasMore
                ? <div className="rounded-xl border border-sky-400/25 bg-sky-500/[.06] px-3 py-2 text-center text-[12px] text-slate-300">Oudere berichten staan in de {waar} zelf. {link && <a className="text-sky-300 underline hover:text-white" href={link} target="_blank" rel="noreferrer">Open de {waar}</a>}</div>
                : g.msgs.length > 0 && <div className="text-center text-[11px] text-slate-500">Begin van het gesprek</div>)}
              {g && !g.msgs.length && <div className="py-10 text-center text-[13px] text-slate-500">Nog geen berichten.</div>}
              {g?.msgs.map((m, i) => (
                <div key={`${m.id}:${i}`}>
                  {dayKey(m.at) && (i === 0 || dayKey(g.msgs[i - 1].at) !== dayKey(m.at)) && <div className="my-2 text-center text-[11px] font-semibold uppercase tracking-wider text-slate-500">{dayLabel(m.at)}</div>}
                  <Bubble m={m} open={i === laatsteChecklist} />
                </div>
              ))}
            </div>
          </motion.aside>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
