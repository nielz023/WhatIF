import { useState } from 'react';
import { useLive } from '../services/live';
import { useDb, type StatRow } from '../services/db';

const RANGES = [{ id: 7, label: '7 dagen' }, { id: 28, label: '28 dagen' }, { id: 0, label: 'Altijd' }] as const;

function Info({ text }: { text: string }) {
  return <span title={text} aria-label={text} className="ml-1.5 inline-flex h-4 w-4 cursor-help items-center justify-center rounded-full bg-white/10 text-[11px] font-bold text-slate-300">i</span>;
}

function Chart({ rows, k, color, label, info }: { rows: StatRow[]; k: 'subscribers' | 'views'; color: string; label: string; info: string }) {
  const pts = rows.filter((r) => typeof r[k] === 'number');
  const W = 600, H = 180, P = 28;
  const vals = pts.map((r) => r[k] as number);
  const min = Math.min(...vals), max = Math.max(...vals), span = max - min || 1;
  const t0 = pts.length ? +new Date(pts[0].at) : 0, t1 = pts.length ? +new Date(pts[pts.length - 1].at) : 1;
  const x = (r: StatRow) => P + ((+new Date(r.at) - t0) / ((t1 - t0) || 1)) * (W - 2 * P);
  const y = (v: number) => H - P - ((v - min) / span) * (H - 2 * P);
  const d = pts.map((r, i) => `${i ? 'L' : 'M'}${x(r).toFixed(1)},${y(r[k] as number).toFixed(1)}`).join(' ');
  const last = vals[vals.length - 1], diff = vals.length > 1 ? last - vals[0] : null;
  const fmtD = (t: number) => new Date(t).toLocaleDateString('nl-NL', { day: 'numeric', month: 'short' });
  return (
    <section className="panel p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="flex items-center text-[15px] font-semibold text-slate-300">{label}<Info text={info} /></span>
        {diff != null && <span className="text-[14px] font-semibold" style={{ color: diff >= 0 ? '#3ddc97' : '#ff4d6d' }}>{diff >= 0 ? '▲ +' : '▼ '}{diff.toLocaleString('nl-NL')} in deze periode</span>}
      </div>
      <div className="font-display text-[34px] font-bold" style={{ color }}>{last != null && Number.isFinite(last) ? last.toLocaleString('nl-NL') : '—'}</div>
      {pts.length > 1 ? (
        <svg viewBox={`0 0 ${W} ${H}`} className="mt-1 h-44 w-full" role="img" aria-label={`${label} over tijd`}>
          {[0, 0.5, 1].map((f) => <line key={f} x1={P} x2={W - P} y1={P + f * (H - 2 * P)} y2={P + f * (H - 2 * P)} stroke="rgba(255,255,255,.07)" />)}
          <text x={P} y={H - 6} fill="#8792b8" fontSize="12">{fmtD(t0)}</text>
          <text x={W - P} y={H - 6} fill="#8792b8" fontSize="12" textAnchor="end">{fmtD(t1)}</text>
          <text x={W - P} y={P - 8} fill="#8792b8" fontSize="12" textAnchor="end">{max.toLocaleString('nl-NL')}</text>
          <path d={`${d} L${x(pts[pts.length - 1])},${H - P} L${x(pts[0])},${H - P} Z`} fill={color} opacity=".12" />
          <path d={d} fill="none" stroke={color} strokeWidth="2.5" strokeLinejoin="round" />
          {pts.map((r, i) => <circle key={i} cx={x(r)} cy={y(r[k] as number)} r={i === pts.length - 1 ? 4.5 : 2.5} fill={color}><title>{new Date(r.at).toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam' })}: {(r[k] as number).toLocaleString('nl-NL')}</title></circle>)}
        </svg>
      ) : <div className="mt-2 rounded-xl bg-white/[.03] p-4 text-[14px] text-slate-400">De grafiek groeit vanzelf: elk uur komt er een meetpunt bij.</div>}
    </section>
  );
}

const RETENTIE = [
  { video: 'Video 1 · 2x sterker', kijkduur: '6:40 gemiddeld (26%)', curve: [100, 34, 31, 29, 28, 27, 26, 26, 25, 25], tip: '2 op de 3 kijkers haken af in de eerste minuut. Begin met het spannendste beeld binnen 5 seconden, zonder uitleg vooraf.' },
];

export default function KanaalPage() {
  const [range, setRange] = useState<number>(28);
  const allStats = useDb((s) => s.stats);
  const yt = useLive((s) => s.data.youtube);
  const stats = range ? allStats.filter((r) => Date.now() - +new Date(r.at) < range * 864e5) : allStats;
  const vids = yt?.videos ?? [];
  const top = (t: string) => [...vids].filter((v) => v.type === t && (v.status ?? 'public') === 'public').sort((a, b) => (b.views ?? 0) - (a.views ?? 0)).slice(0, 5);
  const longs = top('long'), shorts = top('short');
  const shortViews = vids.filter((v) => v.type === 'short').reduce((a, v) => a + (v.views ?? 0), 0);
  const longViews = vids.filter((v) => v.type === 'long').reduce((a, v) => a + (v.views ?? 0), 0);
  const subs = yt?.subscribers ?? 0;
  const goal = subs < 100 ? 100 : subs < 500 ? 500 : subs < 1000 ? 1000 : Math.ceil((subs + 1) / 1000) * 1000;

  const Row = ({ v, i }: { v: (typeof vids)[number]; i: number }) => (
    <a href={v.url} target="_blank" rel="noreferrer" className="flex items-center gap-3 rounded-xl bg-white/[.04] px-3 py-2.5 hover:bg-white/[.08]">
      <span className="w-6 shrink-0 text-center font-display text-[18px] font-bold text-slate-500">{i + 1}</span>
      {v.id && <img src={`https://i.ytimg.com/vi/${v.id}/mqdefault.jpg`} alt="" loading="lazy" className="hidden h-10 w-[72px] shrink-0 rounded-md object-cover sm:block" onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }} />}
      <span className="min-w-0 flex-1 truncate text-[14px] text-slate-100">{v.title}</span>
      <span className="shrink-0 text-[14px] font-semibold text-sky-300">{(v.views ?? 0).toLocaleString('nl-NL')}</span>
    </a>
  );

  return (
    <div className="h-full overflow-y-auto p-3 pb-28 md:p-6 md:pb-10">
      <h1 className="font-display text-[28px] font-bold text-white">Kanaal</h1>
      <p className="mb-4 text-[15px] text-slate-400">Je echte cijfers van YouTube, elk uur bijgewerkt via vidIQ.</p>

      <div className="mb-4 flex gap-1.5">{RANGES.map((r) => (
        <button key={r.id} onClick={() => setRange(r.id)} className={`rounded-full px-4 py-2 text-[14px] font-semibold ${range === r.id ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>{r.label}</button>
      ))}</div>

      <div className="mb-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <Chart rows={stats} k="subscribers" color="#ff8a3d" label="Abonnees" info="Mensen die je kanaal volgen. Elk uur een meetpunt." />
        <Chart rows={stats} k="views" color="#3db8ff" label="Weergaven" info="Alle keren dat iemand iets van je bekeek, bij elkaar opgeteld." />
      </div>

      <section className="panel mb-4 p-4">
        <div className="flex items-baseline justify-between"><span className="font-display text-[18px] font-bold text-white">Doel: {goal.toLocaleString('nl-NL')} abonnees</span><span className="text-[15px] font-semibold text-orange-300">{subs}/{goal}</span></div>
        <div className="mt-2 h-3 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-gradient-to-r from-orange-400 to-sky-400" style={{ width: `${Math.min(100, (subs / goal) * 100)}%` }} /></div>
      </section>

      <div className="mb-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <section className="panel p-4">
          <div className="mb-2 font-display text-[18px] font-bold text-white">🏆 Beste shorts</div>
          <div className="space-y-1.5">{shorts.length ? shorts.map((v, i) => <Row key={v.id ?? v.title} v={v} i={i} />) : <div className="text-[14px] text-slate-400">Nog geen cijfers.</div>}</div>
        </section>
        <section className="panel p-4">
          <div className="mb-2 font-display text-[18px] font-bold text-white">🎬 Lange video's</div>
          <div className="space-y-1.5">{longs.length ? longs.map((v, i) => <Row key={v.id ?? v.title} v={v} i={i} />) : <div className="text-[14px] text-slate-400">Nog geen cijfers.</div>}</div>
        </section>
      </div>

      <section className="panel mb-4 p-4">
        <div className="mb-2 flex items-center font-display text-[18px] font-bold text-white">Shorts vs lange video's<Info text="Hoeveel van al je weergaven van shorts komen en hoeveel van lange video's." /></div>
        <div className="flex h-4 overflow-hidden rounded-full bg-white/10">
          <div className="bg-sky-400" style={{ width: `${(shortViews / ((shortViews + longViews) || 1)) * 100}%` }} title="Shorts" />
          <div className="bg-orange-400" style={{ width: `${(longViews / ((shortViews + longViews) || 1)) * 100}%` }} title="Lange video's" />
        </div>
        <div className="mt-1 flex justify-between text-[13px]"><span className="text-sky-300">📱 Shorts {shortViews.toLocaleString('nl-NL')}</span><span className="text-orange-300">🎬 Lang {longViews.toLocaleString('nl-NL')}</span></div>
        <p className="mt-2 text-[14px] text-slate-300">Shorts trekken de meeste kijkers. Elke short linkt naar zijn lange video, dus hoe meer shorts goed lopen, hoe meer kans op kijkers voor de lange video.</p>
      </section>

      <section className="panel p-4">
        <div className="mb-2 flex items-center font-display text-[18px] font-bold text-white">Retentie<Info text="Hoeveel procent van de kijkers op elk moment nog kijkt. Hoe vlakker de lijn, hoe beter." /></div>
        {RETENTIE.map((r) => (
          <div key={r.video} className="rounded-xl bg-white/[.03] p-3">
            <div className="flex flex-wrap justify-between gap-2 text-[14px]"><span className="font-semibold text-white">{r.video}</span><span className="text-slate-400">kijkduur {r.kijkduur}</span></div>
            <svg viewBox="0 0 300 80" className="mt-2 h-20 w-full" preserveAspectRatio="none"><path d={r.curve.map((v, i) => `${i ? 'L' : 'M'}${(i / (r.curve.length - 1)) * 300},${80 - (v / 100) * 76}`).join(' ')} fill="none" stroke="#ff8a3d" strokeWidth="2.5" /></svg>
            <div className="text-[14px] text-orange-200">💡 {r.tip}</div>
          </div>
        ))}
        <div className="mt-2 text-[13px] text-slate-500">Video 2 heeft nog te weinig kijkers voor een betrouwbare retentiecurve.</div>
      </section>
    </div>
  );
}
