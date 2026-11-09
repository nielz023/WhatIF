/**
 * OPDRACHTBALK (verbeterlijst punten 1, 2, 3, 4, 9 en 14).
 * - Overal te openen met de toets K of de knop bovenin. Typ of spreek in (microfoon in het veld, Alt+M).
 * - Het HQ kiest zelf de afdeling en, als het kan, de thread die er al aan werkt. Aanpassen kan met één klik.
 * - Nu versturen, of eerst in het mandje en dan alles samen (één toestemmingsklik).
 * - Snelknoppen vullen een complete opdracht volgens het productiehandboek in.
 * - "Mijn opdrachten": per opdracht verstuurd, ontvangen, bezig, klaar, met het antwoord erbij.
 *   Komt er een antwoord binnen, dan een melding, een zacht geluidje en een oranje stip op de knop.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { create } from 'zustand';
import { X, Send, ShoppingBasket, Trash2, Zap, ListChecks, FileText, ExternalLink } from 'lucide-react';
import { useReal, type Order } from '../../services/real';
import { useLive, type Reply, type Activity } from '../../services/live';
import { useGame } from '../../store/useGame';
import { play } from '../../world/sound';
import { prefs } from '../../lib/prefs';
import { openBestand } from './BestandViewer';
import { openGesprek } from './Gesprek';
import { KLEUR } from '../../lib/status';

/* ---------------- afdelingen kiezen ---------------- */
export const AFDELINGEN: { id: string; naam: string; re: RegExp }[] = [
  { id: 'onderzoek', naam: 'Onderzoek', re: /\b(idee|ideeën|onderwerp|onderzoek|concurrent|ifology|niche|trend)/i },
  { id: 'script', naam: 'Script', re: /\b(script|verloop|hook|scène-?tekst|dialoog|verhaal)/i },
  { id: 'stem', naam: 'Stem', re: /\b(stem|stemmen|voice|voice-?over|elevenlabs|verteller)/i },
  { id: 'productie', naam: 'Productie', re: /\b(anim|render|blender|scène|scene|cast|set|sets|personage|montage|unreal)/i },
  { id: 'thumbnail', naam: 'Thumbnail', re: /\b(thumbnail|thumb|titel|titels|banner)/i },
  { id: 'publicatie', naam: 'Publicatie', re: /\b(upload|beschrijving|tags|hoofdstuk|short|shorts|publiceer|planning)/i },
  { id: 'cijfers', naam: 'Cijfers', re: /\b(cijfers|weergaven|abonnee|analyse|rapport|kijkduur|klikratio|statistiek)/i },
  { id: 'hq', naam: 'HQ', re: /\b(hq|dashboard|pagina|kantoor|knop|menu)/i },
];
export function kiesAfdeling(t: string) { return AFDELINGEN.find((a) => a.re.test(t))?.naam ?? 'Algemeen'; }
/** de thread die er al aan werkt: zelfde video en past bij de afdeling, anders de lopende thread van die video */
function kiesThread(t: string, act: Activity[], afd: string): Activity | undefined {
  const nr = Number(t.match(/video\s*(\d+)/i)?.[1] ?? 0);
  const open = act.filter((a) => a.id && a.state !== 'done');
  const afdRe = AFDELINGEN.find((a) => a.naam === afd)?.re;
  const kand = open.filter((a) => (nr ? a.video === nr : true) && (afdRe ? afdRe.test(a.title) : false));
  if (kand.length) return kand[0];
  return nr ? open.find((a) => a.video === nr) : undefined;
}

/* ---------------- snelknoppen (punt 9) ---------------- */
export const SNELKNOPPEN: [string, string][] = [
  ['Nieuwe video starten', 'Start een nieuwe video over: [onderwerp]. Volg het productiehandboek: verloop met escalatie (leuk, indrukwekkend, gevaarlijk, schokkend) en een donkere twist, script in het Engels met de hook binnen 5 seconden en de abonneeroproep rond 60%.'],
  ['Script schrijven', 'Schrijf het script voor video [nummer] volgens het productiehandboek en de retentieregels: spannendste beeld binnen 5 s, teller op beeld, kijker als "jij", abonneeroproep rond 60%, geen verwijzing naar de volgende video.'],
  ['Titels bedenken', 'Bedenk 10 titels voor video [nummer] volgens de cursusregels (What IF, getal, Elk Woord Met Hoofdletter, kort genoeg voor mobiel) en kies de beste 3 met uitleg.'],
  ['Thumbnailvarianten', 'Maak 3 thumbnailvarianten voor video [nummer] in de glans-look, passend bij de titel en wat de eerste seconden laten zien.'],
  ['Teaser-short maken', 'Maak een teaser-short voor video [nummer] met een cliffhanger aan het eind, gekoppeld aan de lange video.'],
  ['Uploadpakket klaarzetten', 'Zet het uploadpakket voor video [nummer] klaar in youtube_upload.md: titel, beschrijving, tags, hoofdstukken, vastgezette reactie en thumbnail.'],
  ['Weekrapport', 'Maak het weekrapport: wat ging goed, wat niet, de vergelijking met vorige week en drie acties voor deze week.'],
];

/* ---------------- stand per opdracht (punt 3) ---------------- */
export type Stand = 'wachtrij' | 'verstuurd' | 'ontvangen' | 'bezig' | 'klaar' | 'fout';
const STAND: Record<Stand, [string, string]> = {
  wachtrij: ['Nog niet verstuurd', KLEUR.stil], verstuurd: ['Verstuurd', KLEUR.stil], ontvangen: ['Ontvangen', KLEUR.bezig],
  bezig: ['Bezig', KLEUR.bezig], klaar: ['Klaar', KLEUR.klaar], fout: ['Mislukt', KLEUR.probleem],
};
const STAPPEN: Stand[] = ['verstuurd', 'ontvangen', 'bezig', 'klaar'];
export function antwoordVan(o: Order, replies: Reply[]): Reply | undefined { return o.ref ? replies.find((r) => r.ref === o.ref) : undefined; }
export function standVan(o: Order, r?: Reply): Stand { if (o.status !== 'verstuurd') return 'wachtrij'; return r?.stand ?? (r ? 'klaar' : 'verstuurd'); }

/* ---------------- nieuwe antwoorden bijhouden (punt 4) ---------------- */
const ZIEN = 'dm-ref-gezien';
const gezien = (): Record<string, string> => { try { return JSON.parse(localStorage.getItem(ZIEN) || '{}'); } catch { return {}; } };
interface NB { nieuw: number; open: boolean; tab: 'nieuw' | 'mijn'; voorvul: { text?: string; doel?: string; thread?: string; titel?: string } | null }
export const useBalk = create<NB>(() => ({ nieuw: 0, open: false, tab: 'nieuw', voorvul: null }));

/** draait altijd (App): kijkt of er een nieuw antwoord op een eigen opdracht is */
export function AntwoordWacht() {
  const replies = useLive((s) => s.data.replies);
  const orders = useReal((s) => s.orders);
  const toast = useGame((s) => s.toast);
  useEffect(() => {
    if (!replies?.length) return;
    const g = gezien(); let n = 0; const eerste = !Object.keys(g).length;
    for (const o of orders) {
      const r = antwoordVan(o, replies); if (!r || !o.ref) continue;
      const st = standVan(o, r);
      if (g[o.ref] !== st) {
        if (!eerste) {
          n++;
          if (prefs().meldingen) toast(st === 'klaar' ? `✅ Antwoord op "${o.text.slice(0, 50)}": ${r.antwoord.slice(0, 90)}` : `📬 Je opdracht "${o.text.slice(0, 50)}" is ${STAND[st][0].toLowerCase()}`, st === 'klaar' ? 'success' : 'info');
        }
        g[o.ref] = st;
      }
    }
    if (n) { if (prefs().meldingGeluid) play('notify'); useBalk.setState((s) => ({ nieuw: s.nieuw + n })); }
    try { localStorage.setItem(ZIEN, JSON.stringify(g)); } catch { /* */ }
  }, [replies, orders, toast]);
  return null;
}

/* ---------------- de knop bovenin ---------------- */
export function BalkKnop() {
  const nieuw = useBalk((s) => s.nieuw);
  const mand = useReal((s) => s.mandje.length);
  return (
    <button id="dm-balkknop" onClick={() => window.dispatchEvent(new CustomEvent('dm-opdracht', { detail: nieuw ? { tab: 'mijn' } : {} }))}
      className="relative flex items-center gap-2 rounded-xl border border-orange-400/40 bg-orange-500/10 px-2.5 py-2 text-[13px] font-semibold text-orange-100 hover:border-orange-400 hover:text-white md:min-w-[220px]"
      aria-label="Opdracht geven (toets K)" title="Opdracht geven aan Claude (toets K)">
      <Zap size={15} className="text-orange-300" /><span className="hidden md:inline">Opdracht geven…</span>
      <kbd className="ml-auto hidden rounded bg-white/10 px-1.5 font-mono text-[11px] text-slate-300 md:inline">K</kbd>
      {mand > 0 && <span className="absolute -left-1 -top-1 min-w-[18px] rounded-full bg-sky-500 px-1 text-center text-[11px] font-bold text-white" title={`${mand} in het mandje`}>{mand}</span>}
      {nieuw > 0 && <span className="absolute -right-1 -top-1 h-3 w-3 rounded-full bg-orange-400 shadow-[0_0_10px_#fb923c]" title="Nieuw antwoord" />}
    </button>
  );
}

/* ---------------- het venster ---------------- */
export default function Opdrachtbalk() {
  const { open, tab, voorvul } = useBalk();
  const { send, inMandje, uitMandje, verstuurMandje, mandje, orders, resend, avail } = useReal();
  const activity = useLive((s) => s.data.activity);
  const replies = useLive((s) => s.data.replies) ?? [];
  const toast = useGame((s) => s.toast);
  const [text, setText] = useState('');
  const [afd, setAfd] = useState<string | null>(null);
  const [thread, setThread] = useState<string | null | undefined>(undefined); // undefined = automatisch, null = geen
  const veld = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const h = (e: Event) => {
      const d = (e as CustomEvent).detail ?? {};
      useBalk.setState({ open: true, tab: d.tab ?? 'nieuw', voorvul: d.text || d.thread ? d : null, nieuw: d.tab === 'mijn' ? 0 : useBalk.getState().nieuw });
    };
    window.addEventListener('dm-opdracht', h);
    return () => window.removeEventListener('dm-opdracht', h);
  }, []);
  useEffect(() => {
    if (!open) return;
    if (voorvul) { setText(voorvul.text ?? ''); setAfd(voorvul.doel ?? null); setThread(voorvul.thread ?? undefined); }
    setTimeout(() => veld.current?.focus(), 30);
  }, [open, voorvul]);
  useEffect(() => {
    if (!open) return;
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') { e.stopImmediatePropagation(); sluit(); } };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, [open]);

  const autoAfd = useMemo(() => kiesAfdeling(text), [text]);
  const doel = afd ?? autoAfd;
  const autoThread = useMemo(() => kiesThread(text, activity, doel), [text, activity, doel]);
  const doelThread = thread === undefined ? autoThread : thread ? activity.find((a) => a.id === thread) : undefined;
  const mijnAantal = orders.filter((o) => standVan(o, antwoordVan(o, replies)) !== 'klaar').length;

  function sluit() { useBalk.setState({ open: false, voorvul: null }); }
  function leeg() { setText(''); setAfd(null); setThread(undefined); }
  const opts = () => ({ doel, thread: doelThread?.id, });
  const tekstMet = () => (doelThread ? `${text.trim()}\n(voor thread "${doelThread.title}")` : text.trim());
  async function nu() {
    if (!text.trim()) return;
    play('send');
    const o = await send(tekstMet(), opts());
    toast(o.status === 'verstuurd' ? '✅ Opdracht doorgegeven. Je volgt hem onder Mijn opdrachten.' : `⏳ In de wachtrij: ${o.reason ?? ''}`, o.status === 'verstuurd' ? 'success' : 'warning');
    leeg(); useBalk.setState({ tab: 'mijn' });
  }
  function mand() { if (!text.trim()) return; inMandje(tekstMet(), opts()); play('click'); leeg(); veld.current?.focus(); }
  async function alles() {
    const n = mandje.length; play('send');
    const ok = await verstuurMandje();
    toast(ok ? `✅ ${n} opdrachten in één keer doorgegeven.` : 'Versturen lukte niet. Het mandje blijft staan.', ok ? 'success' : 'warning');
    if (ok) useBalk.setState({ tab: 'mijn' });
  }
  function snel(t: string) {
    setText(t); setAfd(null); setThread(undefined);
    setTimeout(() => { const el = veld.current; if (!el) return; el.focus(); const a = t.indexOf('['); const b = t.indexOf(']'); if (a >= 0 && b > a) el.setSelectionRange(a, b + 1); }, 20);
  }

  if (!open) return null;
  const lopend = activity.filter((a) => a.id && a.state !== 'done');
  return (
    <div className="fixed inset-0 z-[82] flex items-start justify-center bg-black/55 p-2 pt-[8vh] backdrop-blur-sm md:p-6 md:pt-[10vh]" role="dialog" aria-modal="true" aria-label="Opdrachtbalk" onClick={sluit}>
      <div className="dm-pop flex max-h-[84vh] w-full max-w-2xl flex-col overflow-hidden rounded-3xl border border-orange-400/40 bg-[#0d1430] shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-1 border-b border-white/10 px-3 pt-3">
          {([['nieuw', 'Nieuwe opdracht', Zap], ['mijn', `Mijn opdrachten${mijnAantal ? ` (${mijnAantal})` : ''}`, ListChecks]] as const).map(([id, l, I]) => (
            <button key={id} role="tab" aria-selected={tab === id} onClick={() => useBalk.setState({ tab: id, nieuw: id === 'mijn' ? 0 : useBalk.getState().nieuw })}
              className={`flex items-center gap-1.5 rounded-t-xl px-3 py-2 text-[14px] font-semibold ${tab === id ? 'bg-white/[.07] text-white' : 'text-slate-400 hover:text-white'}`}><I size={14} />{l}</button>
          ))}
          <button onClick={sluit} className="ml-auto mb-1 rounded-lg border border-white/10 p-1.5 text-slate-300 hover:text-white" aria-label="Sluiten"><X size={16} /></button>
        </div>

        {tab === 'nieuw' ? (
          <div className="min-h-0 overflow-y-auto p-4">
            {voorvul?.titel && <div className="mb-2 rounded-xl bg-orange-500/10 px-3 py-2 text-[13px] text-orange-100">{voorvul.titel}</div>}
            <label htmlFor="dm-balk" className="sr-only">Opdracht</label>
            <textarea id="dm-balk" ref={veld} rows={3} value={text} onChange={(e) => setText(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) { e.preventDefault(); void nu(); } }}
              placeholder="Typ of spreek in wat je wilt, bv. 'Maak drie thumbnails voor video 4'" className="input min-h-[92px] w-full resize-y text-[15px]" />
            <div className="mt-1 text-[12px] text-slate-500">Inspreken: klik op de microfoon in het veld of druk Alt+M. Versturen: Ctrl+Enter.</div>

            <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[13px]">
              <span className="text-slate-400">Gaat naar:</span>
              <select value={doel} onChange={(e) => setAfd(e.target.value)} className="rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-white" aria-label="Afdeling">
                {[...AFDELINGEN.map((a) => a.naam), 'Algemeen'].map((n) => <option key={n} value={n}>{n}{n === autoAfd && afd == null ? ' (automatisch)' : ''}</option>)}
              </select>
              <select value={thread === undefined ? 'auto' : thread ?? 'geen'} onChange={(e) => setThread(e.target.value === 'auto' ? undefined : e.target.value === 'geen' ? null : e.target.value)} className="max-w-[260px] rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-white" aria-label="Thread">
                <option value="auto">{autoThread ? `Automatisch: ${autoThread.title}` : 'Automatisch: Claude kiest de thread'}</option>
                <option value="geen">Nieuwe of eigen thread</option>
                {lopend.map((a) => <option key={a.id} value={a.id}>{a.title}</option>)}
              </select>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              <button className="btn-primary text-[14px]" disabled={!text.trim()} onClick={() => void nu()}><Send size={14} />Nu versturen</button>
              <button className="btn-ghost text-[14px]" disabled={!text.trim()} onClick={mand}><ShoppingBasket size={14} />In het mandje</button>
              <span className="ml-auto self-center text-[12px]" style={{ color: avail === 'available' ? KLEUR.klaar : KLEUR.wacht }}>● {avail === 'available' ? 'Claude luistert mee' : avail === 'laden' ? 'Verbinding controleren…' : 'Claude luistert nu niet; opdrachten wachten'}</span>
            </div>

            {mandje.length > 0 && (
              <div className="mt-4 rounded-2xl border border-sky-400/30 bg-sky-500/[.06] p-3">
                <div className="mb-2 flex items-center gap-2 text-[14px] font-semibold text-sky-200"><ShoppingBasket size={15} />Mandje ({mandje.length})
                  <button className="btn-primary ml-auto !py-1 text-[13px]" onClick={() => void alles()}>Alles versturen</button></div>
                <ul className="space-y-1">{mandje.map((m) => (
                  <li key={m.id} className="flex items-start gap-2 rounded-lg bg-black/20 px-2 py-1.5 text-[13px]">
                    <span className="chip shrink-0 bg-white/10 text-slate-300">{m.doel ?? 'Algemeen'}</span>
                    <span className="min-w-0 flex-1 whitespace-pre-line text-slate-200">{m.text}</span>
                    <button onClick={() => uitMandje(m.id)} className="shrink-0 text-slate-500 hover:text-rose-300" aria-label="Uit het mandje"><Trash2 size={14} /></button>
                  </li>
                ))}</ul>
                <div className="mt-1.5 text-[12px] text-slate-400">Samen versturen = één keer toestemming geven in claude.ai.</div>
              </div>
            )}

            <div className="mt-4">
              <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Snelknoppen</div>
              <div className="flex flex-wrap gap-1.5">{SNELKNOPPEN.map(([l, t]) => (
                <button key={l} type="button" onClick={() => snel(t)} className="rounded-full border border-hq-line bg-white/[.04] px-3 py-1.5 text-[13px] text-slate-200 hover:border-orange-400/60 hover:text-white">{l}</button>
              ))}</div>
            </div>
          </div>
        ) : (
          <MijnOpdrachten orders={orders} replies={replies} resend={resend} sluit={sluit} />
        )}
      </div>
    </div>
  );
}

function MijnOpdrachten({ orders, replies, resend, sluit }: { orders: Order[]; replies: Reply[]; resend: (id: string) => Promise<void>; sluit: () => void }) {
  if (!orders.length) return <div className="px-6 py-14 text-center text-[14px] text-slate-400">Je hebt nog geen opdrachten gegeven vanuit dit HQ. Ze verschijnen hier met hun stand.</div>;
  return (
    <ul className="min-h-0 space-y-2 overflow-y-auto p-4">
      {orders.slice(0, 40).map((o) => {
        const r = antwoordVan(o, replies); const st = standVan(o, r); const [l, c] = STAND[st];
        const idx = STAPPEN.indexOf(st);
        return (
          <li key={o.id} className="rounded-2xl bg-white/[.04] p-3">
            <div className="flex items-start gap-2">
              <div className="min-w-0 flex-1">
                <div className="whitespace-pre-line text-[14px] text-white">{o.text.split('\n(voor thread')[0]}</div>
                <div className="mt-0.5 text-[12px] text-slate-500">{new Date(o.at).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}{o.doel ? ` · ${o.doel}` : ''}{o.ref ? ` · ${o.ref}` : ''}{o.reason && st === 'wachtrij' ? ` · ${o.reason}` : ''}</div>
              </div>
              <span className="chip shrink-0" style={{ background: `${c}22`, color: c }}>{l}</span>
            </div>
            {st !== 'wachtrij' && st !== 'fout' && (
              <div className="mt-2 flex items-center gap-1" aria-label={`Stand: ${l}`}>
                {STAPPEN.map((s, i) => <div key={s} className="flex flex-1 flex-col gap-0.5"><div className="h-1.5 rounded-full" style={{ background: i <= idx ? STAND[s][1] : 'rgba(255,255,255,.08)' }} /><span className={`text-[11px] ${i <= idx ? 'text-slate-300' : 'text-slate-600'}`}>{STAND[s][0]}</span></div>)}
              </div>
            )}
            {r?.antwoord && <div className="mt-2 rounded-xl bg-black/25 px-3 py-2 text-[13px] text-slate-200">{r.antwoord}</div>}
            <div className="mt-2 flex flex-wrap gap-2">
              {st === 'wachtrij' && <button className="btn-ghost !py-1 text-[12px]" onClick={() => void resend(o.id)}>Opnieuw versturen</button>}
              {r?.bestand && <button className="btn-ghost !py-1 text-[12px]" onClick={() => { sluit(); openBestand(r.bestand!); }}><FileText size={12} />Resultaat openen</button>}
              {r?.link && <a className="btn-ghost !py-1 text-[12px]" href={r.link} target="_blank" rel="noreferrer"><ExternalLink size={12} />Openen</a>}
              {(r?.thread || o.thread) && <button className="btn-ghost !py-1 text-[12px]" onClick={() => { sluit(); openGesprek({ kind: 'thread', thread: (r?.thread || o.thread)!, title: 'Gesprek' }); }}>Gesprek</button>}
            </div>
          </li>
        );
      })}
      {!orders.some((o) => o.ref) && <li className="text-[12px] text-slate-500">Oudere opdrachten hebben nog geen kenmerk; daarvan staat het antwoord onder Antwoorden op Vandaag.</li>}
    </ul>
  );
}
