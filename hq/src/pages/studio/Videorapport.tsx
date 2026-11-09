/**
 * VIDEORAPPORT PER VIDEO (verbeterlijst punt 41) en KLIKRATIO VIA SCREENSHOT (punt 42).
 * Weergaven, gemiddelde kijkduur, % bekeken, likes, reacties, nieuwe abonnees en (als bekend) klikratio en
 * vertoningen, met de vergelijking met je andere video's van hetzelfde soort. Elk cijfer met bron en datum.
 * Klikratio en vertoningen geeft vidIQ niet: niels sleept een screenshot uit YouTube Studio hierheen.
 * Kan deze pagina beelden aan Claude geven, dan leest Claude de twee getallen voor; anders typt niels ze over.
 * Pas na niels' "Opslaan" worden ze bewaard (in deze browser) en als opdracht doorgegeven.
 */
import { useEffect, useMemo, useState } from 'react';
import { ImagePlus } from 'lucide-react';
import { useLive, type YTVideo } from '../../services/live';
import { order } from '../../services/real';
import { useGame } from '../../store/useGame';
import { leesKlik, bewaarKlik, kortTijd, type Klik } from '../../services/studio';
import Bron from '../../components/shared/Bron';
import { KLEUR } from '../../lib/status';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Any = any;
const nl = (n: number, d = 0) => n.toLocaleString('nl-NL', { maximumFractionDigits: d });
const mmss = (s: number) => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`;
const dag = (v: YTVideo) => Date.parse(`${(v.datum ?? v.date ?? '').slice(0, 10)}T${v.tijd ?? '12:00'}:00`);
const mediaan = (a: number[]) => { if (!a.length) return null; const s = [...a].sort((x, y) => x - y); const m = Math.floor(s.length / 2); return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2; };

type Rij = { label: string; waarde: (v: YTVideo) => number | null | undefined; fmt: (n: number) => string; bron: 'feed' | 'vidiq' | 'studio' };
const RIJEN: Rij[] = [
  { label: 'Weergaven', waarde: (v) => v.views, fmt: (n) => nl(n), bron: 'feed' },
  { label: 'Gemiddelde kijkduur', waarde: (v) => v.avd, fmt: mmss, bron: 'vidiq' },
  { label: '% bekeken', waarde: (v) => v.avp, fmt: (n) => `${nl(n, 1)}%`, bron: 'vidiq' },
  { label: 'Likes', waarde: (v) => v.likes, fmt: (n) => nl(n), bron: 'feed' },
  { label: 'Reacties', waarde: (v) => v.comments, fmt: (n) => nl(n), bron: 'vidiq' },
  { label: 'Nieuwe abonnees', waarde: (v) => v.subs, fmt: (n) => `+${nl(n)}`, bron: 'vidiq' },
  { label: 'Klikratio', waarde: (v) => (v as Any).ctr ?? (v.id ? leesKlik()[v.id]?.ctr : undefined), fmt: (n) => `${nl(n, 1)}%`, bron: 'studio' },
  { label: 'Vertoningen', waarde: (v) => (v as Any).vertoningen ?? (v.id ? leesKlik()[v.id]?.vertoningen : undefined), fmt: (n) => nl(n), bron: 'studio' },
];

function Screenshot({ v, opgeslagen }: { v: YTVideo; opgeslagen: () => void }) {
  const toast = useGame((s) => s.toast);
  const [bestand, setBestand] = useState<File | null>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [ctr, setCtr] = useState(''); const [vert, setVert] = useState('');
  const [kanLezen, setKanLezen] = useState(false); const [leest, setLeest] = useState(false);
  const [melding, setMelding] = useState<string | null>(null);
  useEffect(() => {
    let weg = false;
    (async () => { try { const c = (window as Any).claude; const s = c?.use ? await c.use('sample') : null; const l = s?.limits ? await s.limits().catch(() => null) : null; if (!weg) setKanLezen(!!l?.images); } catch { /* geen sample */ } })();
    return () => { weg = true; };
  }, []);
  useEffect(() => () => { if (url) URL.revokeObjectURL(url); }, [url]);
  const kies = (f?: File | null) => { if (!f || !f.type.startsWith('image/')) return; setBestand(f); setUrl(URL.createObjectURL(f)); setMelding(null); };
  const lees = async () => {
    if (!bestand) return; setLeest(true); setMelding(null);
    try {
      const s = await (window as Any).claude.use('sample');
      const j = await s.json(`Dit is een screenshot uit YouTube Studio. Lees alleen wat er echt staat: de klikratio voor vertoningen (impressions click-through rate, in procenten) en het aantal vertoningen (impressions) voor de video "${v.title}". Geef JSON: {"ctr": getal of null, "vertoningen": getal of null}. Staat een getal er niet, geef null.`, { images: [bestand], modelTier: 'quick', cache: false });
      if (typeof j?.ctr === 'number') setCtr(String(j.ctr).replace('.', ','));
      if (typeof j?.vertoningen === 'number') setVert(String(Math.round(j.vertoningen)));
      setMelding(j?.ctr == null && j?.vertoningen == null ? 'Claude vond geen klikratio of vertoningen op deze screenshot. Typ ze zelf over.' : 'Controleer de getallen hieronder en druk op Opslaan.');
    } catch { setMelding('Voorlezen lukte niet. Typ de getallen zelf over.'); }
    setLeest(false);
  };
  const bewaar = () => {
    const c = parseFloat(ctr.replace(',', '.')); const n = parseInt(vert.replace(/\D/g, ''), 10);
    if (isNaN(c) && isNaN(n)) { setMelding('Vul minstens één getal in.'); return; }
    const k: Klik = { at: new Date().toISOString(), bron: bestand ? 'screenshot' : 'zelf', ...(isNaN(c) ? {} : { ctr: c }), ...(isNaN(n) ? {} : { vertoningen: n }) };
    if (v.id) bewaarKlik(v.id, k);
    order(`Cijfers uit YouTube Studio voor "${v.title}"${v.id ? ` (${v.id})` : ''}: ${isNaN(c) ? '' : `klikratio ${nl(c, 1)}%`}${!isNaN(c) && !isNaN(n) ? ', ' : ''}${isNaN(n) ? '' : `${nl(n)} vertoningen`} (stand ${kortTijd(Date.now())}, ingevuld door niels). Zet ze in status.json bij youtube.videos[] als ctr en vertoningen.`, toast, { doel: 'Cijfers' });
    setBestand(null); setUrl(null); setCtr(''); setVert(''); setMelding(null); opgeslagen();
  };
  return (
    <div className="mt-3 rounded-xl border border-dashed border-white/15 p-3"
      onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); kies(e.dataTransfer.files?.[0]); }}>
      <div className="flex items-center gap-2 text-[14px] font-semibold text-white"><ImagePlus size={15} className="text-sky-300" />Klikratio en vertoningen uit YouTube Studio</div>
      <p className="mt-0.5 text-[13px] text-slate-400">Sleep een screenshot van Studio › Analytics › Bereik hierheen, of kies er een. {kanLezen ? 'Claude kan de getallen voorlezen; jij controleert ze.' : 'Typ de twee getallen over; Claude zet ze daarna in de cijfers.'}</p>
      <div className="mt-2 flex flex-wrap items-start gap-3">
        <label className="btn-ghost cursor-pointer !py-1 text-[13px]">Screenshot kiezen<input type="file" accept="image/*" className="hidden" onChange={(e) => kies(e.target.files?.[0])} /></label>
        {url && <img src={url} alt="Gekozen screenshot" className="max-h-28 rounded-lg border border-white/10" />}
        {url && kanLezen && <button className="btn-ghost !py-1 text-[13px]" onClick={() => void lees()} disabled={leest}>{leest ? 'Claude leest…' : 'Laat Claude de getallen lezen'}</button>}
      </div>
      <div className="mt-2 flex flex-wrap items-end gap-2">
        <label className="text-[12px] text-slate-400">Klikratio (%)<input className="input mt-0.5 block w-28" inputMode="decimal" value={ctr} onChange={(e) => setCtr(e.target.value)} placeholder="bv. 4,2" /></label>
        <label className="text-[12px] text-slate-400">Vertoningen<input className="input mt-0.5 block w-32" inputMode="numeric" value={vert} onChange={(e) => setVert(e.target.value)} placeholder="bv. 1500" /></label>
        <button className="btn-primary text-[13px]" onClick={bewaar}>Opslaan en doorgeven</button>
      </div>
      {melding && <div className="mt-1 text-[13px] text-amber-200">{melding}</div>}
    </div>
  );
}

export default function Videorapport() {
  const yt = useLive((s) => s.data.youtube);
  const alle = useMemo(() => (yt?.videos ?? []).filter((v) => (v.status ?? 'public') === 'public').sort((a, b) => dag(b) - dag(a)), [yt]);
  const [id, setId] = useState<string>('');
  const [, ververs] = useState(0);
  const v = alle.find((x) => (x.id ?? x.title) === id) ?? alle.find((x) => x.type === 'long') ?? alle[0];
  if (!v) return <section className="panel mb-4 p-4 text-[14px] text-slate-400">Nog geen video's met cijfers.</section>;
  const anderen = alle.filter((x) => x !== v && x.type === v.type);
  const uren = (Date.now() - dag(v)) / 36e5;
  const klik = v.id ? leesKlik()[v.id] : undefined;
  const bronTekst = (b: Rij['bron']) => b === 'feed' ? <Bron bron="YouTube-feed" at={v.viewsAt ?? yt?.feedAt} relatief /> : b === 'vidiq' ? <Bron bron="vidIQ" at={v.statsAt} /> : (v as Any).ctr != null ? <Bron bron="YouTube Studio" at={yt?.datum} /> : klik ? <Bron bron={klik.bron === 'screenshot' ? 'jouw screenshot' : 'door jou ingevuld'} at={klik.at} /> : null;
  const v48 = (v as Any).views48 as number | undefined, v7 = (v as Any).views7d as number | undefined;
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <span className="font-display text-[18px] font-bold text-white">📋 Videorapport</span>
        <select value={v.id ?? v.title} onChange={(e) => setId(e.target.value)} className="max-w-full rounded-lg border border-white/10 bg-black/40 px-2 py-1.5 text-[13px] text-white" aria-label="Kies een video">
          {alle.map((x) => <option key={x.id ?? x.title} value={x.id ?? x.title}>{x.type === 'long' ? '🎬' : '📱'} {kortTijd(x.datum ?? x.date, false)} · {x.title}</option>)}
        </select>
      </div>
      <div className="text-[14px] text-slate-200">{v.type === 'long' ? 'Lange video' : 'Short'} · online sinds {kortTijd(dag(v)) ?? 'onbekend'} · vergeleken met {anderen.length} andere {v.type === 'long' ? "lange video's" : 'shorts'} (middelste waarde)</div>
      <div className="mt-3 grid gap-1.5 sm:grid-cols-2">
        {RIJEN.map((r) => {
          const w = r.waarde(v); const m = mediaan(anderen.map(r.waarde).filter((x): x is number => typeof x === 'number'));
          const beter = w != null && m != null ? w >= m : null;
          return (
            <div key={r.label} className="flex items-center justify-between gap-2 rounded-lg bg-white/[.03] px-3 py-2">
              <div className="min-w-0">
                <div className="text-[13px] text-slate-400">{r.label}</div>
                {w != null ? bronTekst(r.bron) : null}
              </div>
              <div className="shrink-0 text-right">
                <div className="font-display text-[18px] font-bold text-white">{w != null ? r.fmt(w) : <span className="text-[13px] font-normal text-slate-500">{r.bron === 'studio' ? 'nog niet ingevuld' : r.bron === 'vidiq' ? (uren < 48 ? 'volgt na 48 uur' : 'niet bekend') : 'niet bekend'}</span>}</div>
                {w != null && m != null && <div className="text-[12px]" style={{ color: beter ? KLEUR.klaar : KLEUR.wacht }}>{beter ? '▲' : '▼'} anderen: {r.fmt(m)}</div>}
              </div>
            </div>
          );
        })}
      </div>
      <div className="mt-3 rounded-xl bg-white/[.03] p-3 text-[13px] text-slate-300">
        <div className="font-semibold text-white">Na 48 uur en na 7 dagen</div>
        {uren < 48 ? <p>Deze video staat er {Math.max(0, Math.round(uren))} uur. De cijfers na 48 uur komen op {kortTijd(dag(v) + 48 * 36e5)}, na 7 dagen op {kortTijd(dag(v) + 7 * 864e5, false)}.</p>
          : v48 != null || v7 != null ? (
            <p>Na 48 uur: <b className="text-white">{v48 != null ? nl(v48) : 'onbekend'}</b> weergaven (anderen: {(() => { const m = mediaan(anderen.map((x) => (x as Any).views48).filter((x): x is number => typeof x === 'number')); return m != null ? nl(m) : 'onbekend'; })()}). Na 7 dagen: <b className="text-white">{v7 != null ? nl(v7) : uren < 168 ? `volgt op ${kortTijd(dag(v) + 7 * 864e5, false)}` : 'onbekend'}</b>{' '}(anderen: {(() => { const m = mediaan(anderen.map((x) => (x as Any).views7d).filter((x): x is number => typeof x === 'number')); return m != null ? nl(m) : 'onbekend'; })()}).</p>
          ) : <p className="text-slate-400">De uurronde bewaart nog geen weergaven per video op 48 uur en 7 dagen, dus die vergelijking kan nog niet. Hierboven zie je de stand van nu.{' '}
            <button className="text-sky-300 hover:text-white" onClick={() => order('Laat de uurronde per video de weergaven na 48 uur en na 7 dagen bewaren (youtube.videos[].views48 en views7d in status.json), zodat het videorapport video\'s eerlijk kan vergelijken.', useGame.getState().toast, { doel: 'Cijfers' })}>Vraag Claude om dit bij te houden</button></p>}
      </div>
      <Screenshot v={v} opgeslagen={() => ververs((n) => n + 1)} />
    </section>
  );
}
