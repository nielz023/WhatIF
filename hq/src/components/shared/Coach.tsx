/**
 * DE COACH: het hoofdpersonage rechtsonder. Je kunt hem vragen stellen (via de
 * sample-capability, met de echte stand van je kanaal erbij) en hij geeft af en toe
 * een tip. Onder een tip staat "Doe dit": dat wordt een echte opdracht voor Claude.
 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { X, Send, Settings2 } from 'lucide-react';
import { useLive, type Live } from '../../services/live';
import { useDb } from '../../services/db';
import { order } from '../../services/real';
import { useGame } from '../../store/useGame';
import { startCoach, vraag, parse } from '../../services/coach';
import { useWorld } from '../../world/useWorld';

type Tip = { text: string; doe?: string };
type Msg = { role: 'user' | 'assistant'; content: string };

function tipsFor(d: Live): Tip[] {
  const t: Tip[] = [];
  const vids = d.youtube?.videos ?? [];
  const shorts = vids.filter((v) => v.type === 'short').sort((a, b) => (b.views ?? 0) - (a.views ?? 0));
  if (shorts[0]) t.push({ text: `Je beste short is "${shorts[0].title}" met ${(shorts[0].views ?? 0).toLocaleString('nl-NL')} views. Maak er nog een met zo'n soort hook.`, doe: `Maak een nieuwe teaser-short met dezelfde soort hook als "${shorts[0].title}" (beste short).` });
  const wacht = d.activity.filter((a) => a.state === 'blocked' || a.state === 'review_ready');
  if (wacht[0]) t.push({ text: `"${wacht[0].title}" wacht op jou. Even kijken, dan kan Claude door.` });
  const nu = d.videos.find((v) => v.status === 'In productie');
  if (nu && !(d.outputs?.[String(nu.nr)] ?? []).some((o) => /youtube_upload/.test(o.path))) t.push({ text: `Video ${nu.nr} (${nu.werktitel}) is in productie. Laat alvast de titel en thumbnail maken, dan ligt alles klaar voor de upload.`, doe: `Video ${nu.nr}: maak alvast 5 titels en 3 thumbnailvarianten zodat ze klaarliggen voor de upload.` });
  t.push(
    { text: 'Het spannendste beeld moet binnen 5 seconden in beeld. Bij video 1 haakte 2 op de 3 kijkers af in de eerste minuut.' },
    { text: 'Een getal in de titel werkt goed ("10x", "Day 1 to Day 40"). IFOLOGY scoort daar het best mee.' },
    { text: 'Shorts trekken veel meer kijkers dan je lange video\'s. Zet in elke short een duidelijke link naar de lange video.', doe: 'Controleer bij alle shorts of de link naar de lange video erin staat en zet hem erbij waar hij mist.' },
    { text: 'Reageer op comments in het eerste uur na een upload. Dat helpt het algoritme.', doe: 'Verzamel de nieuwe comments op mijn laatste video en stel antwoorden voor.' },
    { text: 'Hou de stem altijd centraal en de muziek zacht eronder, zonder plotselinge harde pieken.' },
    { text: 'Elke week een lange video houdt je streak 🔥 in leven. Plan de volgende alvast in.' },
  );
  return t;
}

export default function Coach() {
  const d = useLive((s) => s.data);
  const stats = useDb((s) => s.stats);
  const toast = useGame((s) => s.toast);
  const setPage = useGame((s) => s.setPage);
  const page = useGame((s) => s.page);
  const tips = useMemo(() => tipsFor(d), [d]);
  const [open, setOpen] = useState(false);
  const [bubble, setBubble] = useState<Tip | null>(null);
  const [tipsOn, setTipsOn] = useState(() => { try { return localStorage.getItem('coach-tips') !== 'uit'; } catch { return true; } });
  const [freq, setFreq] = useState<number>(() => { try { return Number(localStorage.getItem('coach-freq')) || 30; } catch { return 30; } });
  const [showSet, setShowSet] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [q, setQ] = useState('');
  const [busy, setBusy] = useState(false);
  const [canAsk, setCanAsk] = useState<boolean | null>(null);
  const idx = useRef(Math.floor(Math.random() * 100));
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    void startCoach();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const c = (window as any).claude;
    if (!c?.use) { setCanAsk(false); return; }
    c.use('sample').then((x: unknown) => setCanAsk(!!x)).catch(() => setCanAsk(false));
  }, []);

  // random tips: eerste na 20 s, daarna elke `freq` minuten
  useEffect(() => {
    if (!tipsOn) { setBubble(null); return; }
    const show = () => { idx.current++; setBubble(tips[idx.current % tips.length]); };
    const first = setTimeout(show, 20000);
    const id = setInterval(show, freq * 60000);
    return () => { clearTimeout(first); clearInterval(id); };
  }, [tipsOn, freq, tips]);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [msgs, busy]);

  const ask = async (text: string) => {
    if (!text.trim() || busy) return;
    const next: Msg[] = [...msgs, { role: 'user', content: text.trim() }];
    setMsgs(next); setQ(''); setBusy(true);
    const r = await vraag(next, d, stats, (t) => setMsgs([...next, { role: 'assistant', content: t }]));
    setMsgs([...next, { role: 'assistant', content: r.tekst }]);
    setBusy(false);
  };

  const doe = (t: string) => { order(t, toast); setBubble(null); };
  const opdrachtUit = (t: string) => parse(t).acties[0];
  const saveSet = (on: boolean, f: number) => { setTipsOn(on); setFreq(f); try { localStorage.setItem('coach-tips', on ? 'aan' : 'uit'); localStorage.setItem('coach-freq', String(f)); } catch { /* */ } };

  const panelOpen = useWorld((w) => !!(w.focus || w.worker));
  if (page === 'coach') return null;
  return (
    <div className="pointer-events-none fixed bottom-[76px] right-3 z-[60] flex flex-col items-end gap-2 md:bottom-4 md:right-4">
      {bubble && !open && !(panelOpen && page === 'driftmark') && (
        <div className="dm-pop pointer-events-auto w-[290px] max-w-[calc(100vw-24px)] rounded-2xl border border-orange-400/50 bg-[#0f1630] p-3 text-[14px] text-slate-100 shadow-2xl backdrop-blur">
          <div className="mb-1 flex items-center justify-between"><span className="text-[12px] font-bold uppercase tracking-wider text-orange-300">💡 Tip van je coach</span><button aria-label="Tip sluiten" onClick={() => setBubble(null)} className="text-slate-400 hover:text-white"><X size={15} /></button></div>
          {bubble.text}
          <div className="mt-2 flex gap-2">
            {bubble.doe && <button className="btn-primary !px-3 !py-1.5 text-[13px]" onClick={() => doe(bubble.doe!)}>Doe dit</button>}
            <button className="btn-ghost !px-3 !py-1.5 text-[13px]" onClick={() => { setOpen(true); setBubble(null); }}>Vraag meer</button>
          </div>
        </div>
      )}

      {open && (
        <div className="dm-pop pointer-events-auto flex h-[min(520px,calc(100vh-170px))] w-[360px] max-w-[calc(100vw-24px)] flex-col overflow-hidden rounded-2xl border border-hq-line bg-[#0b1128] shadow-2xl backdrop-blur-xl">
          <div className="flex items-center gap-2 border-b border-hq-line px-3 py-2.5">
            <img src="./img/c1_hoofdpersonage.jpg" alt="" className="h-9 w-9 rounded-full object-cover ring-2 ring-orange-400" />
            <div className="min-w-0 flex-1"><div className="font-display text-[16px] font-bold text-white">Je coach</div><div className="text-[12px] text-slate-400">{canAsk ? 'Vraag me alles over je kanaal' : canAsk === false ? 'Tips (vragen werkt in claude.ai)' : 'Even opstarten…'}</div></div>
            <button onClick={() => { setPage('coach'); setOpen(false); }} className="rounded-lg bg-orange-500/20 px-2 py-1 text-[12px] font-semibold text-orange-200 hover:bg-orange-500/30">Coachkamer</button>
            <button aria-label="Instellingen coach" onClick={() => setShowSet(!showSet)} className="p-1 text-slate-400 hover:text-white"><Settings2 size={17} /></button>
            <button aria-label="Coach sluiten" onClick={() => setOpen(false)} className="p-1 text-slate-400 hover:text-white"><X size={18} /></button>
          </div>
          {showSet && (
            <div className="space-y-2 border-b border-hq-line bg-white/[.03] p-3 text-[13px] text-slate-300">
              <label className="flex items-center justify-between gap-2">Random tips<input type="checkbox" checked={tipsOn} onChange={(e) => saveSet(e.target.checked, freq)} className="h-4 w-4 accent-orange-500" /></label>
              <label className="flex items-center justify-between gap-2">Hoe vaak
                <select className="rounded-lg border border-hq-line bg-[#070b1a] px-2 py-1" value={freq} onChange={(e) => saveSet(tipsOn, Number(e.target.value))}>
                  <option value={10}>elke 10 min</option><option value={30}>elk half uur</option><option value={60}>elk uur</option><option value={180}>elke 3 uur</option>
                </select>
              </label>
            </div>
          )}
          <div className="flex-1 space-y-2 overflow-y-auto p-3">
            {msgs.length === 0 && (
              <div className="space-y-2">
                <div className="rounded-2xl rounded-tl-sm bg-white/[.06] p-3 text-[14px] text-slate-100">Hoi niels! 👋 Ik ben je CEO Coach. Snelle vraag hier, of open de Coachkamer voor je briefing, doelen en beslissingen.</div>
                {['Hoe krijg ik meer kijkers op mijn lange video\'s?', 'Wat moet ik nu als eerste doen?', 'Welke short werkt het best en waarom?', 'Geef 3 titels voor video 4'].map((s) => (
                  <button key={s} onClick={() => void ask(s)} className="block w-full rounded-xl border border-hq-line px-3 py-2 text-left text-[13px] text-slate-200 hover:border-orange-400/60">{s}</button>
                ))}
                <div className="pt-1 text-[12px] font-bold uppercase tracking-wider text-slate-500">Tips</div>
                {tips.slice(0, 3).map((t) => (
                  <div key={t.text} className="rounded-xl bg-white/[.03] p-2.5 text-[13px] text-slate-300">{t.text}{t.doe && <button className="ml-1 font-semibold text-orange-300 hover:text-white" onClick={() => doe(t.doe!)}>Doe dit →</button>}</div>
                ))}
              </div>
            )}
            {msgs.map((m, i) => {
              const op = m.role === 'assistant' ? opdrachtUit(m.content) : undefined;
              return (
                <div key={i} className={`max-w-[88%] whitespace-pre-line rounded-2xl p-3 text-[14px] ${m.role === 'user' ? 'ml-auto rounded-tr-sm bg-orange-500/80 text-white' : 'rounded-tl-sm bg-white/[.06] text-slate-100'}`}>
                  {parse(m.content).schoon || (busy ? '…' : '')}
                  {op && <button className="btn-primary mt-2 !px-3 !py-1.5 text-[13px]" onClick={() => doe(op)}>Doe dit: {op.length > 40 ? op.slice(0, 40) + '…' : op}</button>}
                </div>
              );
            })}
            {busy && msgs[msgs.length - 1]?.role === 'user' && <div className="w-16 rounded-2xl bg-white/[.06] p-3 text-center text-slate-400">•••</div>}
            <div ref={endRef} />
          </div>
          <form onSubmit={(e) => { e.preventDefault(); void ask(q); }} className="flex gap-2 border-t border-hq-line p-2.5">
            <label htmlFor="coach-q" className="sr-only">Vraag aan je coach</label>
            <input id="coach-q" className="input min-w-0 flex-1 !py-2 text-[14px]" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Vraag iets…" />
            <button className="btn-primary !px-3" aria-label="Versturen" disabled={busy || !q.trim()}><Send size={16} /></button>
          </form>
        </div>
      )}

      <button onClick={() => { setOpen(!open); setBubble(null); }} aria-label={open ? 'Coach sluiten' : 'Coach openen'}
        className="pointer-events-auto relative h-14 w-14 overflow-hidden rounded-full border-2 border-orange-400 bg-[#0f1630] shadow-[0_0_24px_rgba(255,138,61,.5)] transition hover:scale-105">
        <img src="./img/c1_hoofdpersonage.jpg" alt="" className="h-full w-full object-cover" />
        {bubble && !open && <span className="absolute right-0.5 top-0.5 h-3 w-3 rounded-full bg-orange-500 ring-2 ring-[#070b1a]" />}
      </button>
    </div>
  );
}
