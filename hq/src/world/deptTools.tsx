/**
 * Eigen gereedschap per afdeling in het afdelingspaneel (verbeterpunten ronde 2):
 * CEO: videokaarten, grafiek met een stip per upload, weekrapport op maandag.
 * Onderzoek: shorts-tabel en de wekelijkse check van concurrenten.
 * Creatief: ideeënbord (slepen, met coach-score).  Script: hook-check van de eerste 5 seconden.
 * Stem: stand van de stemmen.  Productie: renderpaneel met schijfruimte.
 * Thumbnail: nieuwste thumbnails naast elkaar met een CTR-schatting.  Publicatie: 48-uurcheck en opdrachten.
 * Crisis: alle alarmen met de oorzaak.  Overal: notities per afdeling en "praat met deze afdeling".
 */
import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { ArrowLeft, ArrowRight, BarChart3, Clapperboard, FileText, HardDrive, Lightbulb, ListChecks, MessageSquare, Mic, Plus, Send, Siren, StickyNote, Timer, Trash2, Users, Wand2 } from 'lucide-react';
import { useLive, type Live } from '../services/live';
import { useDb, type StatRow } from '../services/db';
import { useReal } from '../services/real';
import { useCoach, maakRapport } from '../services/coach';
import { useGame } from '../store/useGame';
import { threadsPerRoom, type RoomDef, type RoomId } from './rooms';
import { alarmsFrom } from './alarms';
import { mergePunten, puntenVoor } from '../data/verbeter';

/* ---------- toegang tot database en Claude (alleen op de gepubliceerde pagina) ---------- */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
let dbP: Promise<Any> | null = null;
const getDb = () => (dbP ??= (async () => { try { const c = (window as Any).claude; return c?.use ? await c.use('db') : null; } catch { return null; } })());
let smP: Promise<Any> | null = null;
const getSample = () => (smP ??= (async () => { try { const c = (window as Any).claude; return c?.use ? await c.use('sample') : null; } catch { return null; } })());
const foutTekst = (e: unknown) => { const c = (e as Any)?.code; return c === 'not_granted' ? 'Claude mag nog niet antwoorden: sta het toe als claude.ai erom vraagt.' : c === 'rate_limited' ? 'Even rustig aan, probeer het zo nog eens.' : c === 'images_unavailable' ? 'Plaatjes meesturen mag hier niet.' : 'Dat lukte nu niet. Probeer het zo nog een keer.'; };

/** één document uit de database, live bijgewerkt; met opslaan */
function useDoc<T>(path: string): [T | null, (v: T) => Promise<boolean>, 'laden' | 'ok' | 'geen'] {
  const [v, setV] = useState<T | null>(null); const [st, setSt] = useState<'laden' | 'ok' | 'geen'>('laden');
  useEffect(() => {
    let on = true; let un: (() => void) | undefined;
    const t = setTimeout(() => { if (on) setSt((s) => (s === 'laden' ? 'geen' : s)); }, 10000);
    void getDb().then((db) => {
      if (!on) return; if (!db) { clearTimeout(t); setSt('geen'); return; }
      try { un = db.doc(path).onSnapshot((d: Any) => { clearTimeout(t); setSt('ok'); setV(d.exists ? (d.data() as T) : null); }, () => { clearTimeout(t); setSt('geen'); }); } catch { clearTimeout(t); setSt('geen'); }
    });
    return () => { on = false; clearTimeout(t); un?.(); };
  }, [path]);
  const save = async (val: T) => { setV(val); const db = await getDb(); if (!db) return false; try { await db.doc(path).set(val as object); return true; } catch { return false; } };
  return [v, save, st];
}

const nl = (n?: number | null) => (n == null ? '—' : n.toLocaleString('nl-NL'));
const short = (s: string, n = 46) => (s.length > n ? s.slice(0, n - 1) + '…' : s);
function Sec({ title, icon, right, children, color }: { title: string; icon?: ReactNode; right?: ReactNode; children: ReactNode; color?: string }) {
  return (
    <div className="rounded-xl border border-white/[.07] bg-black/20 p-3">
      <div className="mb-2 flex items-center justify-between gap-2">
        <span className="flex items-center gap-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400"><span style={{ color }}>{icon}</span>{title}</span>{right}
      </div>
      {children}
    </div>
  );
}
const Leeg = ({ children }: { children: ReactNode }) => <div className="text-[12px] leading-relaxed text-slate-500">{children}</div>;

/* =================== CEO =================== */
function VideoCards() {
  const vids = useLive((s) => s.data.videos); const yt = useLive((s) => s.data.youtube?.videos);
  const cards = [...vids].sort((a, b) => a.nr - b.nr).slice(0, 5);
  const viewsOf = (url?: string) => { const id = url?.split('/').pop(); return yt?.find((y) => y.id === id)?.views; };
  return (
    <Sec title="Video's 1 t/m 5" icon={<Clapperboard size={13} />} color="#FACC15">
      <div className="grid grid-cols-5 gap-1.5">
        {Array.from({ length: 5 }, (_, i) => {
          const v = cards[i]; const id = v?.youtube?.split('/').pop();
          if (!v) return <div key={i} className="flex aspect-[3/4] flex-col items-center justify-center rounded-lg border border-dashed border-white/15 text-center text-[10px] text-slate-500"><Plus size={14} />Video {i + 1}</div>;
          const done = v.steps.filter((s) => s.done).length; const pct = Math.round((done / Math.max(1, v.steps.length)) * 100);
          const stap = v.steps.find((s) => s.active)?.label ?? v.steps.find((s) => !s.done)?.label ?? 'Online';
          const views = viewsOf(v.youtube);
          return (
            <a key={i} href={v.youtube || undefined} target="_blank" rel="noreferrer" title={`${v.title}\n${v.status}`} className="group flex flex-col overflow-hidden rounded-lg border border-white/10 bg-white/[.03] transition hover:border-white/30">
              <div className="relative aspect-video bg-gradient-to-br from-[#1b2660] to-[#3a1d4f]">
                {id && <img src={`./thumbs/${id}.jpg`} alt="" className="h-full w-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} />}
                <span className="absolute left-1 top-1 rounded bg-black/60 px-1 text-[10px] font-bold text-white">{v.nr}</span>
              </div>
              <div className="flex flex-1 flex-col justify-between p-1">
                <div className="line-clamp-2 text-[10px] font-semibold leading-tight text-slate-200">{v.werktitel || v.title}</div>
                <div className="mt-1">
                  <div className="h-1 rounded-full bg-white/10"><div className="h-1 rounded-full" style={{ width: `${pct}%`, background: v.status === 'Online' ? '#21D6A0' : '#FACC15' }} /></div>
                  <div className="mt-0.5 truncate text-[9px] text-slate-400">{v.status === 'Online' ? `👁 ${nl(views)}` : stap}</div>
                </div>
              </div>
            </a>
          );
        })}
      </div>
    </Sec>
  );
}

/** weergaven door de tijd, met een stip bij elke upload (oranje = lange video, blauw = short) */
function UploadChart() {
  const stats = useDb((s) => s.stats); const yt = useLive((s) => s.data.youtube);
  const [hover, setHover] = useState<string | null>(null);
  const W = 352, H = 110, P = 6;
  const data = useMemo(() => {
    const rows = stats.filter((r) => r.views != null && r.at).map((r) => ({ t: Date.parse(r.at), v: r.views! })).filter((r) => !isNaN(r.t));
    const from = Date.now() - 28 * 864e5;
    const pts = rows.filter((r) => r.t >= from);
    if (pts.length < 2) return null;
    const t0 = pts[0].t, t1 = pts[pts.length - 1].t, v0 = Math.min(...pts.map((p) => p.v)), v1 = Math.max(...pts.map((p) => p.v));
    const x = (t: number) => P + ((t - t0) / Math.max(1, t1 - t0)) * (W - 2 * P);
    const y = (v: number) => H - P - ((v - v0) / Math.max(1, v1 - v0)) * (H - 2 * P - 12);
    const valAt = (t: number) => { let best = pts[0]; for (const p of pts) if (Math.abs(p.t - t) < Math.abs(best.t - t)) best = p; return best.v; };
    const ups = (yt?.videos ?? []).map((v) => ({ ...v, t: Date.parse((v.datum ?? v.date ?? '') + 'T16:00:00') })).filter((v) => !isNaN(v.t) && v.t >= t0 && v.t <= t1 + 864e5 && (v.views ?? 0) > 0);
    return { line: pts.map((p, i) => `${i ? 'L' : 'M'}${x(p.t).toFixed(1)},${y(p.v).toFixed(1)}`).join(' '), ups: ups.map((u) => ({ id: u.id ?? u.title, title: u.title, long: u.type === 'long', cx: x(Math.min(u.t, t1)), cy: y(valAt(u.t)), datum: u.datum ?? u.date })), v0, v1 };
  }, [stats, yt]);
  return (
    <Sec title="Weergaven, 28 dagen" icon={<BarChart3 size={13} />} color="#3db8ff" right={data && <span className="text-[11px] text-slate-500">{nl(data.v0)} → {nl(data.v1)}</span>}>
      {!data ? <Leeg>De grafiek vult zich zodra de automatische ronde een paar uur cijfers heeft opgeslagen.</Leeg> : (
        <div className="relative">
          <svg viewBox={`0 0 ${W} ${H}`} className="w-full" role="img" aria-label="Weergaven van de laatste 28 dagen met een stip per upload">
            <path d={data.line} fill="none" stroke="#3db8ff" strokeWidth={2} strokeLinejoin="round" />
            {data.ups.map((u) => (
              <circle key={u.id} cx={u.cx} cy={u.cy} r={u.long ? 5 : 3.2} fill={u.long ? '#FF7A24' : '#22D3EE'} stroke="#0a1030" strokeWidth={1.5}
                onMouseEnter={() => setHover(`${u.datum}: ${u.title}`)} onMouseLeave={() => setHover(null)}><title>{`${u.datum}: ${u.title}`}</title></circle>
            ))}
          </svg>
          <div className="mt-1 flex items-center gap-3 text-[11px] text-slate-400">
            <span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-full bg-[#FF7A24]" />lange video</span>
            <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-full bg-[#22D3EE]" />short</span>
            {hover && <span className="truncate text-slate-200">{hover}</span>}
          </div>
        </div>
      )}
    </Sec>
  );
}

function WeekReport() {
  const rapporten = useCoach((s) => s.rapporten); const data = useLive((s) => s.data); const stats = useDb((s) => s.stats);
  const setPage = useGame((s) => s.setPage); const toast = useGame((s) => s.toast);
  const [bezig, setBezig] = useState(false);
  const maandag = (() => { const d = new Date(); const k = new Date(d); k.setHours(0, 0, 0, 0); k.setDate(k.getDate() - ((k.getDay() + 6) % 7)); return k.getTime(); })();
  const laatste = rapporten.find((r) => r.soort === 'week');
  const dezeWeek = laatste && Date.parse(laatste.at) >= maandag;
  const isMaandag = new Date().getDay() === 1;
  const maak = async () => { setBezig(true); const r = await maakRapport('week', data, stats); setBezig(false); if (typeof r === 'string') toast(r, 'warning'); else { toast('📊 Weekrapport klaar', 'success'); setPage('coach'); } };
  return (
    <Sec title="Weekrapport" icon={<FileText size={13} />} color="#A855F7">
      <div className="flex items-center justify-between gap-2">
        <div className="text-[12px] text-slate-300">{dezeWeek ? `Van deze week (${new Date(laatste!.at).toLocaleDateString('nl-NL', { weekday: 'long', day: 'numeric', month: 'short' })}).` : isMaandag ? 'Het is maandag: tijd voor het weekrapport.' : laatste ? `Laatste: ${new Date(laatste.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })}. Elke maandag een nieuwe.` : 'Elke maandag maakt de coach een weekrapport.'}</div>
        {dezeWeek
          ? <button onClick={() => setPage('coach')} className="shrink-0 rounded-lg bg-white/10 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-white/20">Lezen</button>
          : <button disabled={bezig} onClick={() => void maak()} className="shrink-0 rounded-lg bg-[#A855F7]/25 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#A855F7]/40 disabled:opacity-50">{bezig ? 'Bezig…' : 'Maak nu'}</button>}
      </div>
    </Sec>
  );
}

/* =================== ONDERZOEK =================== */
function ShortsTable() {
  const yt = useLive((s) => s.data.youtube);
  const rows = (yt?.videos ?? []).filter((v) => v.type === 'short' && (v.views ?? 0) > 0).sort((a, b) => (b.views ?? 0) - (a.views ?? 0));
  const max = rows[0]?.views ?? 1;
  const [alles, setAlles] = useState(false);
  return (
    <Sec title={`Shorts (${rows.length})`} icon={<BarChart3 size={13} />} color="#21D6A0" right={yt?.datum && <span className="text-[11px] text-slate-500">stand {yt.datum}</span>}>
      {!rows.length ? <Leeg>Nog geen shorts met weergaven bekend.</Leeg> : (
        <div className="space-y-1">
          {rows.slice(0, alles ? 40 : 6).map((v, i) => (
            <a key={v.id ?? v.title} href={v.url} target="_blank" rel="noreferrer" className="block rounded-md px-1 py-0.5 hover:bg-white/[.05]" title={v.title}>
              <div className="flex items-center gap-2 text-[12px]">
                <span className="w-4 shrink-0 text-right font-bold text-slate-500">{i + 1}</span>
                <span className="min-w-0 flex-1 truncate text-slate-200">{v.title}</span>
                <span className="shrink-0 font-semibold text-white">{nl(v.views)}</span>
              </div>
              <div className="ml-6 mt-0.5 h-1 rounded-full bg-white/[.06]"><div className="h-1 rounded-full bg-[#21D6A0]" style={{ width: `${Math.max(3, ((v.views ?? 0) / max) * 100)}%` }} /></div>
            </a>
          ))}
          {rows.length > 6 && <button onClick={() => setAlles(!alles)} className="mt-1 text-[12px] font-semibold text-[#21D6A0] hover:underline">{alles ? 'Minder tonen' : `Alle ${rows.length} tonen`}</button>}
        </div>
      )}
    </Sec>
  );
}

interface Concurrent { naam: string; url?: string; abonnees?: number; groei?: string; nieuw?: string; views?: number; notitie?: string }
function Competitors() {
  const [doc, , st] = useDoc<{ week?: string; at?: string; kanalen?: Concurrent[]; conclusie?: string }>('concurrenten/laatste');
  return (
    <Sec title="Concurrenten deze week" icon={<Users size={13} />} color="#21D6A0" right={doc?.at && <span className="text-[11px] text-slate-500">{new Date(doc.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })}</span>}>
      {!doc?.kanalen?.length ? <Leeg>{st === 'laden' ? 'Laden…' : 'Elke maandag kijkt de onderzoeker hoe IFOLOGY en andere What-If-kanalen het doen: groei, nieuwe video\'s en wat jij ervan kunt leren. De eerste check verschijnt hier.'}</Leeg> : (
        <div className="space-y-1.5">
          {doc.kanalen.slice(0, 6).map((k) => (
            <div key={k.naam} className="text-[12px]">
              <div className="flex items-center gap-2"><a href={k.url} target="_blank" rel="noreferrer" className="min-w-0 flex-1 truncate font-semibold text-white hover:underline">{k.naam}</a><span className="shrink-0 text-slate-300">{k.abonnees != null ? `${nl(k.abonnees)} abo's` : ''}</span>{k.groei && <span className="shrink-0 text-[#21D6A0]">{k.groei}</span>}</div>
              {(k.nieuw || k.notitie) && <div className="truncate text-slate-400">{k.nieuw ? `Nieuw: ${k.nieuw}${k.views != null ? ` (${nl(k.views)})` : ''}` : ''}{k.nieuw && k.notitie ? ' · ' : ''}{k.notitie ?? ''}</div>}
            </div>
          ))}
          {doc.conclusie && <div className="mt-1 rounded-lg bg-[#21D6A0]/10 px-2 py-1.5 text-[12px] text-emerald-100">💡 {doc.conclusie}</div>}
        </div>
      )}
    </Sec>
  );
}

/* =================== ONDERZOEK: onderwerpenlijst van het team =================== */
interface Onderwerp { nr: number; titel: string; waarom?: string; twist?: string; maak?: string }
function Onderwerpen() {
  const [doc, , st] = useDoc<{ at?: string; conclusie?: string; top?: Onderwerp[]; reserve?: string[]; lieverNiet?: string[]; volgorde?: string; pad?: string }>('bord/onderwerpen');
  const [open, setOpen] = useState<number | null>(null); const [alles, setAlles] = useState(false);
  const top = doc?.top ?? [];
  return (
    <Sec title="Goede onderwerpen voor de niche" icon={<Lightbulb size={13} />} color="#20D9FF" right={doc?.at && <span className="text-[11px] text-slate-500">{new Date(doc.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' })}</span>}>
      {!top.length ? <Leeg>{st === 'laden' ? 'Laden…' : 'Het team zoekt onderwerpen die nu goed werken in de What-If-niche. De lijst verschijnt hier.'}</Leeg> : (
        <div className="space-y-1">
          {doc?.conclusie && <div className="mb-1.5 rounded-lg bg-[#20D9FF]/10 px-2 py-1.5 text-[12px] leading-snug text-cyan-100">💡 {doc.conclusie}</div>}
          {(alles ? top : top.slice(0, 5)).map((o) => (
            <button key={o.nr} onClick={() => setOpen(open === o.nr ? null : o.nr)} className="block w-full rounded-lg border border-white/[.06] bg-white/[.02] px-2 py-1.5 text-left text-[12px] hover:border-white/20">
              <div className="flex items-start gap-2">
                <span className="mt-px w-5 shrink-0 font-bold text-[#20D9FF]">{o.nr}.</span>
                <span className="min-w-0 flex-1 font-semibold text-white">{o.titel}</span>
                {o.maak && <span className="shrink-0 rounded bg-white/10 px-1.5 text-[10px] text-slate-300" title="Hoeveel werk in Blender">{o.maak}</span>}
              </div>
              {open === o.nr && (
                <div className="mt-1 space-y-0.5 pl-7 leading-snug text-slate-300">
                  {o.waarom && <div><span className="text-slate-500">Waarom: </span>{o.waarom}</div>}
                  {o.twist && <div><span className="text-slate-500">Twist: </span>{o.twist}</div>}
                </div>
              )}
            </button>
          ))}
          {top.length > 5 && <button onClick={() => setAlles(!alles)} className="text-[12px] font-semibold text-[#20D9FF] hover:underline">{alles ? 'Minder tonen' : `Alle ${top.length} tonen`}</button>}
          {doc?.volgorde && <div className="mt-1 rounded-lg bg-white/[.04] px-2 py-1.5 text-[12px] leading-snug text-slate-200">🎬 {doc.volgorde}</div>}
          {!!doc?.reserve?.length && <div className="text-[11px] leading-snug text-slate-400"><span className="text-slate-500">Reserve: </span>{doc.reserve.join(' · ')}</div>}
          {!!doc?.lieverNiet?.length && <div className="text-[11px] leading-snug text-slate-400"><span className="text-slate-500">Liever niet: </span>{doc.lieverNiet.join(' ')}</div>}
          {doc?.pad && <div className="text-[11px] text-slate-500">Het hele onderzoek staat in Kennis ({doc.pad}).</div>}
        </div>
      )}
    </Sec>
  );
}

/* =================== CREATIEF: ideeënbord =================== */
type Kolom = 'idee' | 'uitwerken' | 'gekozen';
interface Kaart { id: string; tekst: string; kolom: Kolom; score?: number; waarom?: string }
const KOLOMMEN: [Kolom, string, string][] = [['idee', 'Ideeën', '#A855F7'], ['uitwerken', 'Uitwerken', '#FACC15'], ['gekozen', 'Gekozen', '#21D6A0']];
function IdeasBoard() {
  const ideas = useLive((s) => s.data.ideas);
  const [doc, save, st] = useDoc<{ kaarten: Kaart[]; at?: string }>('bord/ideeen');
  const kaarten = useMemo<Kaart[]>(() => doc?.kaarten ?? ideas.slice(0, 12).map((x, i) => ({ id: `i${i}`, tekst: x.title, kolom: 'idee' as Kolom })), [doc, ideas]);
  const [nieuw, setNieuw] = useState(''); const [drag, setDrag] = useState<string | null>(null); const [scoring, setScoring] = useState<string | null>(null);
  const [melding, setMelding] = useState<string | null>(null);
  const kaartenRef = useRef(kaarten); kaartenRef.current = kaarten; // nieuwste bord (na het wachten op de coach)
  const zet = async (lijst: Kaart[]) => { const ok = await save({ kaarten: lijst, at: new Date().toISOString() }); if (!ok) setMelding('Niet opgeslagen: het bord bewaart alleen op de gepubliceerde pagina.'); };
  const move = (id: string, kolom: Kolom) => void zet(kaarten.map((k) => (k.id === id ? { ...k, kolom } : k)));
  const step = (k: Kaart, d: 1 | -1) => { const i = KOLOMMEN.findIndex(([c]) => c === k.kolom) + d; if (i >= 0 && i < KOLOMMEN.length) move(k.id, KOLOMMEN[i][0]); };
  const add = () => { const t = nieuw.trim(); if (!t) return; setNieuw(''); void zet([{ id: `k${Date.now()}`, tekst: t, kolom: 'idee' }, ...kaarten]); };
  const score = async (k: Kaart) => {
    const sample = await getSample(); if (!sample) { setMelding('Scoren werkt alleen op de gepubliceerde pagina in claude.ai.'); return; }
    setScoring(k.id);
    try {
      const j = await sample.json(`Je bent de coach van Driftmark, een faceless YouTube-kanaal met 3D-animatie in de stijl "What IF ...?" (escalatie: eerst leuk, dan indrukwekkend, dan gevaarlijk, dan schokkend, met een twist of prijs aan het eind). Beste onderwerpen tot nu toe: tijd en snelheid, getallen in de titel, je lichaam dat verandert. Geef dit video-idee een score van 1 tot 10 voor kans op veel kijkers en kijktijd, en één korte zin waarom (Nederlands). Idee: "${k.tekst}". Antwoord als JSON: {"score": getal, "waarom": "zin"}`, { modelTier: 'quick' });
      const s = Math.max(1, Math.min(10, Math.round(Number(j?.score) || 0)));
      await zet(kaartenRef.current.map((x) => (x.id === k.id ? { ...x, score: s, waarom: String(j?.waarom ?? '').slice(0, 200) } : x)));
    } catch (e) { setMelding(foutTekst(e)); }
    setScoring(null);
  };
  const del = (id: string) => void zet(kaarten.filter((k) => k.id !== id));
  return (
    <Sec title="Ideeënbord" icon={<Lightbulb size={13} />} color="#A855F7" right={<span className="text-[11px] text-slate-500">sleep kaartjes</span>}>
      <form onSubmit={(e) => { e.preventDefault(); add(); }} className="mb-2 flex gap-1.5">
        <input value={nieuw} onChange={(e) => setNieuw(e.target.value)} placeholder="Nieuw idee: What IF…" className="min-w-0 flex-1 rounded-lg border border-white/10 bg-black/30 px-2 py-1 text-[12px] text-white placeholder:text-slate-500 focus:border-white/30 focus:outline-none" />
        <button className="rounded-lg bg-[#A855F7]/30 px-2 text-white hover:bg-[#A855F7]/50" aria-label="Idee toevoegen"><Plus size={14} /></button>
      </form>
      <div className="grid grid-cols-3 gap-1.5">
        {KOLOMMEN.map(([kol, naam, c]) => (
          <div key={kol} onDragOver={(e) => e.preventDefault()} onDrop={() => { if (drag) move(drag, kol); setDrag(null); }}
            className="min-h-[90px] rounded-lg border border-white/[.06] bg-white/[.02] p-1">
            <div className="mb-1 text-[10px] font-bold uppercase tracking-wider" style={{ color: c }}>{naam} ({kaarten.filter((k) => k.kolom === kol).length})</div>
            <div className="max-h-[220px] space-y-1 overflow-y-auto">
              {kaarten.filter((k) => k.kolom === kol).map((k) => (
                <div key={k.id} draggable onDragStart={() => setDrag(k.id)} onDragEnd={() => setDrag(null)} title={k.waarom ? `Coach: ${k.waarom}` : k.tekst}
                  className={`group cursor-grab rounded-md border border-white/10 bg-[#121a40] p-1 text-[10.5px] leading-tight text-slate-200 active:cursor-grabbing ${drag === k.id ? 'opacity-40' : ''}`}>
                  <div className="line-clamp-3">{k.tekst}</div>
                  <div className="mt-1 flex items-center gap-0.5">
                    {k.score != null
                      ? <span className="rounded px-1 text-[10px] font-bold" style={{ background: k.score >= 7 ? '#21D6A033' : k.score >= 5 ? '#FACC1533' : '#F43F5E33', color: k.score >= 7 ? '#6ee7b7' : k.score >= 5 ? '#fde68a' : '#fda4af' }}>{k.score}/10</span>
                      : <button onClick={() => void score(k)} disabled={scoring === k.id} className="rounded px-1 text-[10px] font-semibold text-[#c4a1ff] hover:bg-white/10" title="Laat de coach dit idee scoren">{scoring === k.id ? '…' : <span className="inline-flex items-center gap-0.5"><Wand2 size={10} />score</span>}</button>}
                    <span className="ml-auto flex opacity-60 group-hover:opacity-100">
                      {kol !== 'idee' && <button onClick={() => step(k, -1)} className="rounded p-0.5 hover:bg-white/10" aria-label="Naar links"><ArrowLeft size={10} /></button>}
                      {kol !== 'gekozen' && <button onClick={() => step(k, 1)} className="rounded p-0.5 hover:bg-white/10" aria-label="Naar rechts"><ArrowRight size={10} /></button>}
                      <button onClick={() => del(k.id)} className="rounded p-0.5 hover:bg-white/10" aria-label="Weghalen"><Trash2 size={10} /></button>
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      {(melding || st === 'geen') && <div className="mt-1.5 text-[11px] text-amber-200/80">{melding ?? 'Het bord bewaart alleen op de gepubliceerde pagina in claude.ai.'}</div>}
    </Sec>
  );
}

/* =================== SCRIPT: hook-check =================== */
const SLOW = /^(hi|hey|hello|welcome|today|in this video|so,|so |okay|ok,|let's|lets|have you ever wondered)/i;
const STRONG = /(\d|never|forever|die|dead|death|kill|destroy|explod|impossible|end of|last|only|nobody|everyone|stuck|trapped|can't|cannot|won't|still)/i;
function HookCheck() {
  const script = useLive((s) => s.data.script);
  const lines = (script?.regels ?? []).map((l) => l.replace(/\([^)]*\)/g, '').replace(/^["“”'\s]+|["“”'\s]+$/g, '').replace(/^[A-Z ]{2,20}:\s*/, '').trim()).filter(Boolean);
  const [coach, setCoach] = useState<string | null>(null); const [bezig, setBezig] = useState(false);
  if (!lines.length) return <Sec title="Hook-check" icon={<Timer size={13} />} color="#FF7A24"><Leeg>Zodra er een script in productie is, controleer ik hier de eerste 5 seconden.</Leeg></Sec>;
  const eerste = lines[0]; const woorden = eerste.split(/\s+/).length; const sec = woorden / 2.6; const twee = lines.slice(0, 2).join(' ');
  const regels: [boolean, string][] = [
    [sec <= 5.2, `Eerste zin duurt ~${sec.toFixed(1)} s (${woorden} woorden, max ~5 s)`],
    [/\byou\b|\byour\b|\byou'/i.test(twee), 'Spreekt de kijker aan met "you"'],
    [STRONG.test(twee), 'Spanning of een groot getal in de eerste zinnen'],
    [!SLOW.test(eerste), 'Geen trage intro ("Hi", "Today", "Welcome")'],
    [/\?|\.\.\.|…|\bbut\b|\buntil\b|\bwhat if\b|\bhow long\b/i.test(lines.slice(0, 3).join(' ')), 'Open vraag of cliffhanger in de eerste 3 zinnen'],
  ];
  const goed = regels.filter(([ok]) => ok).length;
  const vraagCoach = async () => {
    const sample = await getSample(); if (!sample) { setCoach('De coach-check werkt alleen op de gepubliceerde pagina in claude.ai.'); return; }
    setBezig(true); setCoach('');
    try {
      const r = await sample(`Je bent de scriptcoach van Driftmark (YouTube, "What IF"-video's met 3D-animatie). Regel: het spannendste beeld binnen 5 seconden, geen rustige opbouw in de eerste minuut, spreek de kijker aan met "you". Beoordeel deze opening (Engels script) in maximaal 3 korte zinnen in het Nederlands en geef daarna één betere eerste zin in het Engels.\n\nOpening:\n${lines.slice(0, 6).join('\n')}`, { modelTier: 'quick', cache: false, onText: ({ text }: { text: string }) => setCoach(text) });
      setCoach(r.text);
    } catch (e) { setCoach(foutTekst(e)); }
    setBezig(false);
  };
  return (
    <Sec title={`Hook-check video ${script?.video ?? ''}`} icon={<Timer size={13} />} color="#FF7A24" right={<span className="text-[12px] font-bold" style={{ color: goed >= 4 ? '#21D6A0' : goed >= 3 ? '#FACC15' : '#F43F5E' }}>{goed}/5</span>}>
      <div className="mb-2 rounded-lg bg-white/[.04] px-2 py-1.5 text-[12px] italic text-slate-200">“{eerste}”</div>
      <div className="space-y-0.5">
        {regels.map(([ok, t]) => <div key={t} className="flex gap-1.5 text-[12px]"><span className={ok ? 'text-emerald-400' : 'text-rose-400'}>{ok ? '✓' : '✗'}</span><span className="text-slate-300">{t}</span></div>)}
      </div>
      <button onClick={() => void vraagCoach()} disabled={bezig} className="mt-2 inline-flex items-center gap-1 rounded-lg bg-[#FF7A24]/20 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#FF7A24]/35 disabled:opacity-50"><Wand2 size={12} />{bezig ? 'Coach leest mee…' : 'Laat de coach meekijken'}</button>
      {coach != null && <div className="mt-2 whitespace-pre-wrap rounded-lg bg-black/30 px-2 py-1.5 text-[12px] text-slate-200">{coach || '…'}</div>}
    </Sec>
  );
}

/* =================== STEM =================== */
function VoiceStatus() {
  const vids = useLive((s) => s.data.videos);
  const rows = vids.filter((v) => v.status !== 'Online');
  return (
    <Sec title="Stemmen" icon={<Mic size={13} />} color="#22D3EE">
      {!rows.length ? <Leeg>Geen video in productie.</Leeg> : rows.map((v) => {
        const s = v.steps.find((x) => x.label === 'Stemmen');
        return <div key={v.nr} className="flex items-center gap-2 text-[12px]"><span className="min-w-0 flex-1 truncate text-slate-200">Video {v.nr}: {v.werktitel || v.title}</span><span className={s?.done ? 'text-emerald-400' : s?.active ? 'text-amber-300' : 'text-slate-500'}>{s?.done ? '✓ klaar' : s?.active ? 'bezig' : 'nog niet'}</span></div>;
      })}
      <div className="mt-1.5 text-[11px] text-slate-500">Voor elke nieuwe video vraag ik eerst of je stemmen wilt wisselen.</div>
    </Sec>
  );
}

/* =================== PRODUCTIE: renderpaneel =================== */
function RenderPanel() {
  const b = useLive((s) => s.data.blender);
  if (!b) return <Sec title="Render" icon={<HardDrive size={13} />} color="#FF4DB8"><Leeg>Geen renderstatus bekend.</Leeg></Sec>;
  const disk = /schijf\s*([\d.,]+)\s*GB/i.exec(b.stand ?? '')?.[1]; const gb = disk ? parseFloat(disk.replace(',', '.')) : null;
  const c = gb == null ? '#94A3B8' : gb < 8 ? '#F43F5E' : gb < 25 ? '#FF9F1C' : '#21D6A0';
  const queue = Array.isArray(b.wachtrij) ? b.wachtrij : null;
  const uren = Math.round((Date.now() - Date.parse(b.bijgewerkt)) / 36e5);
  return (
    <Sec title="Render op je pc" icon={<HardDrive size={13} />} color="#FF4DB8" right={<span className="text-[11px] text-slate-500">{isNaN(uren) ? '' : uren < 1 ? 'net bijgewerkt' : `${uren} uur geleden`}</span>}>
      {gb != null && (
        <div className="mb-2">
          <div className="mb-0.5 flex justify-between text-[12px]"><span className="font-semibold text-slate-200">Vrije schijf</span><span className="font-bold" style={{ color: c }}>{disk} GB</span></div>
          <div className="h-2 rounded-full bg-white/10"><div className="h-2 rounded-full" style={{ width: `${Math.min(100, (gb / 200) * 100)}%`, background: c }} /></div>
          <div className="mt-0.5 text-[11px] text-slate-500">{gb < 25 ? 'Bijna vol: de renderwachtrij wacht bij een volle schijf. Oude frames opruimen?' : 'Genoeg ruimte voor de wachtrij.'}</div>
        </div>
      )}
      <div className="text-[12px] leading-relaxed text-slate-300">{b.stand}</div>
      {queue ? <div className="mt-1.5 space-y-0.5">{queue.slice(0, 8).map((q) => <div key={q.naam} className="flex justify-between text-[12px]"><span className="text-slate-300">{q.naam}</span><span className="text-slate-400">{q.status}</span></div>)}</div>
        : typeof b.wachtrij === 'string' && b.wachtrij ? <div className="mt-1.5 text-[12px] text-slate-400">Wachtrij: {b.wachtrij}</div> : null}
    </Sec>
  );
}

/* =================== THUMBNAIL: vergelijken met CTR-schatting =================== */
function ThumbCompare() {
  const yt = useLive((s) => s.data.youtube);
  const longs = (yt?.videos ?? []).filter((v) => v.type === 'long' && v.id).sort((a, b) => (b.datum ?? '').localeCompare(a.datum ?? '')).slice(0, 2);
  const [res, setRes] = useState<{ ctr: string; oordeel: string }[] | null>(null); const [tips, setTips] = useState<string[]>([]);
  const [bezig, setBezig] = useState(false); const [fout, setFout] = useState<string | null>(null);
  const run = async () => {
    const sample = await getSample(); if (!sample) { setFout('De CTR-schatting werkt alleen op de gepubliceerde pagina in claude.ai.'); return; }
    setBezig(true); setFout(null);
    try {
      const lim = await sample.limits?.().catch(() => null);
      const blobs = lim?.images ? await Promise.all(longs.map((v) => fetch(`./thumbs/${v.id}.jpg`).then((r) => (r.ok ? r.blob() : null)).catch(() => null))) : [];
      const imgs = blobs.filter(Boolean) as Blob[];
      const j = await sample.json(`Je bent thumbnail-expert voor het YouTube-kanaal Driftmark (3D "What IF"-video's, klein kanaal, ${useLive.getState().data.youtube?.subscribers ?? 'een paar dozijn'} abonnees). ${imgs.length ? 'Bekijk de thumbnails (in deze volgorde).' : 'Je ziet de plaatjes niet, alleen de titels; zeg dat eerlijk.'} Titels: ${longs.map((v, i) => `${i + 1}) "${v.title}"`).join(' ')}. Schat per video de kans op een goede klikratio (CTR) voor dit soort kanaal, als een bereik zoals "3-5%", met één korte zin waarom. Geef daarna 2 concrete tips voor de volgende thumbnail. Nederlands. JSON: {"videos":[{"ctr":"x-y%","oordeel":"zin"}],"tips":["tip","tip"]}`, { modelTier: 'default', cache: false, ...(imgs.length ? { images: imgs } : {}) });
      setRes((j?.videos ?? []).slice(0, longs.length).map((x: Any) => ({ ctr: String(x?.ctr ?? '?'), oordeel: String(x?.oordeel ?? '') })));
      setTips((j?.tips ?? []).slice(0, 3).map(String));
    } catch (e) { setFout(foutTekst(e)); }
    setBezig(false);
  };
  if (!longs.length) return <Sec title="Thumbnails" icon={<Clapperboard size={13} />} color="#FACC15"><Leeg>Nog geen lange video's online.</Leeg></Sec>;
  return (
    <Sec title="Nieuwste thumbnails" icon={<Clapperboard size={13} />} color="#FACC15">
      <div className="grid grid-cols-2 gap-2">
        {longs.map((v, i) => (
          <a key={v.id} href={v.url} target="_blank" rel="noreferrer" className="block overflow-hidden rounded-lg border border-white/10 bg-white/[.03] hover:border-white/30">
            <div className="aspect-video bg-[#1b2660]"><img src={`./thumbs/${v.id}.jpg`} alt={v.title} className="h-full w-full object-cover" onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }} /></div>
            <div className="p-1.5">
              <div className="line-clamp-2 text-[11px] font-semibold leading-tight text-slate-200">{v.title}</div>
              <div className="mt-0.5 flex justify-between text-[11px] text-slate-400"><span>{v.datum}</span><span>👁 {nl(v.views)}</span></div>
              {res?.[i] && <div className="mt-1 rounded bg-[#FACC15]/10 px-1.5 py-1 text-[11px] text-amber-100"><b>CTR ~{res[i].ctr}</b> · {res[i].oordeel}</div>}
            </div>
          </a>
        ))}
      </div>
      {tips.length > 0 && <ul className="mt-2 list-disc space-y-0.5 pl-4 text-[12px] text-slate-300">{tips.map((t) => <li key={t}>{t}</li>)}</ul>}
      <button onClick={() => void run()} disabled={bezig} className="mt-2 inline-flex items-center gap-1 rounded-lg bg-[#FACC15]/20 px-2.5 py-1 text-[12px] font-semibold text-white hover:bg-[#FACC15]/35 disabled:opacity-50"><Wand2 size={12} />{bezig ? 'Claude kijkt…' : res ? 'Opnieuw schatten' : 'Schat de CTR'}</button>
      <div className="mt-1 text-[11px] text-slate-500">Een schatting door Claude op basis van het plaatje, geen echte cijfers uit YouTube Studio.</div>
      {fout && <div className="mt-1 text-[11px] text-amber-200/80">{fout}</div>}
    </Sec>
  );
}

/* =================== PUBLICATIE: 48-uurcheck en opdrachten =================== */
interface Check48 { video?: string; titel?: string; url?: string; upload?: string; at?: string; views?: number; likes?: number; reacties?: number; vergelijk?: string; oordeel?: string; acties?: string[] }
function Check48Panel() {
  const [doc, , st] = useDoc<Check48>('check48/laatste');
  return (
    <Sec title="48-uurcheck" icon={<ListChecks size={13} />} color="#3ddc97" right={doc?.at && <span className="text-[11px] text-slate-500">{new Date(doc.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>}>
      {!doc ? <Leeg>{st === 'laden' ? 'Laden…' : '48 uur na elke upload controleert de automatische ronde de weergaven, likes en reacties, en vergelijkt ze met je vorige video. Het resultaat verschijnt hier.'}</Leeg> : (
        <div className="text-[12px]">
          <a href={doc.url} target="_blank" rel="noreferrer" className="font-semibold text-white hover:underline">{doc.titel ?? doc.video}</a>
          <div className="mt-1 grid grid-cols-3 gap-1 text-center">
            {[['👁', doc.views], ['👍', doc.likes], ['💬', doc.reacties]].map(([i, v]) => <div key={i as string} className="rounded-md bg-white/[.04] py-1"><div className="font-bold text-white">{nl(v as number)}</div><div className="text-[10px] text-slate-400">{i as string}</div></div>)}
          </div>
          {doc.vergelijk && <div className="mt-1 text-slate-300">{doc.vergelijk}</div>}
          {doc.oordeel && <div className="mt-1 rounded-lg bg-[#3ddc97]/10 px-2 py-1 text-emerald-100">{doc.oordeel}</div>}
          {!!doc.acties?.length && <ul className="mt-1 list-disc pl-4 text-slate-300">{doc.acties.slice(0, 3).map((a) => <li key={a}>{a}</li>)}</ul>}
        </div>
      )}
    </Sec>
  );
}

function Orders() {
  const orders = useReal((s) => s.orders); const resend = useReal((s) => s.resend); const replies = useLive((s) => s.data.replies);
  const rows = [...orders].sort((a, b) => b.at - a.at).slice(0, 8);
  // vergelijk op de eigen tekst, zonder het vaste voorvoegsel "[Afdeling X · Agent]" (anders lijkt elk antwoord van die afdeling te passen)
  const kern = (t: string) => t.replace(/^\s*\[[^\]]*\]\s*/, '').trim().slice(0, 40);
  const reply = (text: string) => {
    const k = kern(text); if (k.length < 8) return undefined;
    return replies?.find((r) => { if (!r.opdracht) return false; const rk = kern(r.opdracht); return rk.length >= 8 && (r.opdracht.includes(k) || text.includes(rk)); });
  };
  return (
    <Sec title="Jouw opdrachten" icon={<Send size={13} />} color="#398CFF">
      {!rows.length ? <Leeg>Nog geen opdrachten vanuit het HQ. Geef er een via "Taak geven" of het vak onderaan een afdeling.</Leeg> : (
        <div className="space-y-1.5">
          {rows.map((o) => {
            const r = reply(o.text); const st = r ? ['Beantwoord', '#21D6A0'] : o.status === 'verstuurd' ? ['Verstuurd', '#398CFF'] : o.status === 'fout' ? ['Mislukt', '#F43F5E'] : ['Wachtrij', '#FF9F1C'];
            return (
              <div key={o.id} className="rounded-lg bg-white/[.03] px-2 py-1.5 text-[12px]">
                <div className="flex items-start gap-2"><span className="min-w-0 flex-1 text-slate-200">{short(o.text, 90)}</span><span className="shrink-0 rounded-full px-1.5 text-[10px] font-bold" style={{ color: st[1], background: `${st[1]}22` }}>{st[0]}</span></div>
                <div className="mt-0.5 flex items-center gap-2 text-[11px] text-slate-500"><span>{new Date(o.at).toLocaleString('nl-NL', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>{o.status === 'wachtrij' && !r && <button onClick={() => void resend(o.id)} className="font-semibold text-[#FF9F1C] hover:underline">opnieuw sturen</button>}</div>
                {r && <div className="mt-1 line-clamp-3 text-[11px] text-slate-400">↳ {r.antwoord}</div>}
              </div>
            );
          })}
        </div>
      )}
    </Sec>
  );
}

/* =================== CRISIS =================== */
function AlarmList() {
  const live = useLive((s) => s.data); const alarms = useMemo(() => alarmsFrom(live), [live]);
  return (
    <Sec title={`Alarmen (${alarms.length})`} icon={<Siren size={13} />} color="#F43F5E">
      {!alarms.length ? <div className="text-[12px] text-emerald-300">Geen alarmen. Alles loopt. 🟢</div> : (
        <div className="space-y-1">{alarms.map((a) => <div key={a.key} className="flex gap-2 text-[12px]"><span className="mt-1 h-2 w-2 shrink-0 rounded-full" style={{ background: a.level === 'rood' ? '#F43F5E' : '#FF9F1C', boxShadow: `0 0 8px ${a.level === 'rood' ? '#F43F5E' : '#FF9F1C'}` }} /><span className="text-slate-200">{a.text}</span></div>)}</div>
      )}
      <div className="mt-1.5 text-[11px] text-slate-500">Bij een rood alarm gaat het zwaailicht boven de crisiskamer draaien en klinkt één keer de sirene.</div>
    </Sec>
  );
}

/* =================== OVERAL: notities =================== */
function Notes({ r }: { r: RoomDef }) {
  const [doc, save, st] = useDoc<{ tekst: string; at: string }>(`notities/${r.id}`);
  const key = `dm-notitie-${r.id}`;
  const [tekst, setTekst] = useState(() => { try { return localStorage.getItem(key) ?? ''; } catch { return ''; } });
  const [status, setStatus] = useState<'' | 'bezig' | 'ok' | 'lokaal'>('');
  const dirty = useRef(false); const timer = useRef<number | undefined>(undefined);
  const pending = useRef<string | null>(null); const saveRef = useRef(save); saveRef.current = save;
  useEffect(() => { if (doc && !dirty.current) setTekst(doc.tekst ?? ''); }, [doc]);
  const change = (v: string) => {
    setTekst(v); dirty.current = true; setStatus('bezig');
    try { localStorage.setItem(key, v); } catch { /* */ }
    window.clearTimeout(timer.current); pending.current = v;
    timer.current = window.setTimeout(() => { pending.current = null; void save({ tekst: v, at: new Date().toISOString() }).then((ok) => { dirty.current = false; setStatus(ok ? 'ok' : 'lokaal'); }); }, 1200);
  };
  // paneel dicht binnen 1,2 s na typen: de laatste tekst toch opslaan (anders overschrijft de oude versie hem)
  useEffect(() => () => { window.clearTimeout(timer.current); if (pending.current !== null) void saveRef.current({ tekst: pending.current, at: new Date().toISOString() }); }, []);
  return (
    <Sec title="Notities" icon={<StickyNote size={13} />} color="#FFE66D" right={<span className="text-[11px] text-slate-500">{status === 'bezig' ? 'opslaan…' : status === 'ok' ? 'opgeslagen' : status === 'lokaal' || st === 'geen' ? 'alleen in deze browser' : doc?.at ? new Date(doc.at).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' }) : ''}</span>}>
      <textarea value={tekst} onChange={(e) => change(e.target.value)} rows={3} placeholder={`Notitie voor ${r.naam}…`}
        className="w-full resize-y rounded-lg border border-[#FFE66D]/20 bg-[#FFE66D]/[.06] px-2 py-1.5 text-[12px] text-amber-50 placeholder:text-amber-100/30 focus:border-[#FFE66D]/50 focus:outline-none" />
    </Sec>
  );
}

/* =================== OVERAL: praat met deze afdeling =================== */
function context(r: RoomDef, L: Live, stats: StatRow[]) {
  const threads = threadsPerRoom(L.activity)[r.id as RoomId].slice(0, 8).map((a) => `- ${a.title} [${a.state}]${a.needs ? ` wacht op niels: ${a.needs}` : ''}${a.doing ? ` nu: ${a.doing}` : ''}`).join('\n');
  const punten = puntenVoor(r.id as RoomId, mergePunten(L.verbeter)).map((p) => `- ${p.klaar ? '[klaar] ' : ''}${p.tekst}`).join('\n');
  const last = stats[stats.length - 1];
  const vids = L.videos.map((v) => `- Video ${v.nr} "${v.title}": ${v.status}`).join('\n');
  return `Kanaal: ${L.youtube?.subscribers ?? last?.subscribers ?? '?'} abonnees, ${L.youtube?.views ?? last?.views ?? '?'} weergaven.\nVideo's:\n${vids}\nThreads van deze afdeling:\n${threads || '- geen'}\nVerbeterpunten van deze afdeling:\n${punten || '- geen'}${r.id === 'productie' && L.blender ? `\nRender: ${L.blender.stand}` : ''}${r.id === 'script' && L.script ? `\nBegin script video ${L.script.video}:\n${L.script.regels.join('\n')}` : ''}`;
}
function AskDept({ r }: { r: RoomDef }) {
  const L = useLive((s) => s.data); const stats = useDb((s) => s.stats);
  const [q, setQ] = useState(''); const [a, setA] = useState<string | null>(null); const [vraag, setVraag] = useState(''); const [bezig, setBezig] = useState(false);
  const ask = async () => {
    const t = q.trim(); if (!t || bezig) return;
    const sample = await getSample(); if (!sample) { setA('Praten met een afdeling werkt alleen op de gepubliceerde pagina in claude.ai.'); return; }
    setVraag(t); setQ(''); setA(''); setBezig(true);
    try {
      const res = await sample(`Je bent ${r.agent}, ${r.rol} van de afdeling ${r.naam} bij Driftmark, het YouTube-kanaal van niels (3D-animatie "What IF ...?", kanaal @driftmark3d). niels is de CEO en praat met jouw afdeling in het HQ. Antwoord in het Nederlands, kort (maximaal 5 zinnen), concreet en eerlijk, alleen op basis van deze stand. Weet je iets niet, zeg dat dan. Doe geen beloftes over acties: voor echt werk geeft niels een opdracht met het vak "Opdracht geven".\n\n=== STAND ===\n${context(r, L, stats)}\n\n=== VRAAG VAN NIELS ===\n${t}`, { modelTier: 'quick', cache: false, onText: ({ text }: { text: string }) => setA(text) });
      setA(res.text);
    } catch (e) { setA(foutTekst(e)); }
    setBezig(false);
  };
  return (
    <Sec title={`Praat met ${r.naam}`} icon={<MessageSquare size={13} />} color={r.color}>
      {vraag && <div className="mb-1 ml-8 rounded-lg rounded-tr-sm bg-[#FF7A24]/20 px-2 py-1 text-[12px] text-orange-50">{vraag}</div>}
      {a != null && <div className="mb-2 mr-6 whitespace-pre-wrap rounded-lg rounded-tl-sm bg-white/[.06] px-2 py-1.5 text-[12px] text-slate-100">{a || '…'}</div>}
      <form onSubmit={(e) => { e.preventDefault(); void ask(); }} className="flex gap-1.5">
        <input value={q} onChange={(e) => setQ(e.target.value)} placeholder={`Vraag iets aan ${r.agent}…`} className="min-w-0 flex-1 rounded-lg border border-white/10 bg-black/30 px-2 py-1.5 text-[12px] text-white placeholder:text-slate-500 focus:border-white/30 focus:outline-none" />
        <button disabled={bezig || !q.trim()} className="rounded-lg px-2.5 text-white disabled:opacity-40" style={{ background: `${r.color}55` }} aria-label="Vraag versturen"><Send size={13} /></button>
      </form>
    </Sec>
  );
}

/** Het gereedschap van één afdeling, onder het team in het afdelingspaneel. */
export function DeptTools({ r }: { r: RoomDef }) {
  const id = r.id as RoomId;
  return (
    <div className="space-y-3">
      {id === 'ceo' && (<><VideoCards /><UploadChart /><WeekReport /></>)}
      {id === 'onderzoek' && (<><Onderwerpen /><ShortsTable /><Competitors /></>)}
      {id === 'creatief' && <IdeasBoard />}
      {id === 'script' && <HookCheck />}
      {id === 'stem' && <VoiceStatus />}
      {id === 'productie' && <RenderPanel />}
      {id === 'thumbnail' && <ThumbCompare />}
      {id === 'publicatie' && (<><Check48Panel /><Orders /></>)}
      {id === 'crisis' && <AlarmList />}
      {id !== 'coach' && <AskDept r={r} />}
      {id !== 'coach' && <Notes r={r} />}
    </div>
  );
}
