/**
 * MOOIERE GRAFIEKEN (verbeterlijst punt 30): een vloeiende lijn, een uitleg bij aanwijzen, elke upload als stip
 * op de lijn en de vergelijking met de vorige lange video. Meetpunten: de database (stats/*, elk uur).
 */
import { useMemo, useRef, useState } from 'react';
import type { StatRow } from '../../services/db';
import type { YTVideo } from '../../services/live';
import { kortTijd } from '../../services/studio';
import Bron from '../../components/shared/Bron';

type K = 'subscribers' | 'views';
const W = 640, H = 200, PL = 8, PR = 8, PT = 18, PB = 26;
const nl = (n: number) => Math.round(n).toLocaleString('nl-NL');

/** vloeiende lijn door de punten (monotone kubische curve, schiet niet over) */
function pad(p: [number, number][]): string {
  if (p.length < 2) return '';
  const n = p.length, d: number[] = [], m: number[] = [];
  for (let i = 0; i < n - 1; i++) d.push((p[i + 1][1] - p[i][1]) / ((p[i + 1][0] - p[i][0]) || 1));
  m.push(d[0]); for (let i = 1; i < n - 1; i++) m.push(d[i - 1] * d[i] <= 0 ? 0 : (d[i - 1] + d[i]) / 2); m.push(d[n - 2]);
  let s = `M${p[0][0].toFixed(1)},${p[0][1].toFixed(1)}`;
  for (let i = 0; i < n - 1; i++) {
    const h = (p[i + 1][0] - p[i][0]) / 3;
    s += ` C${(p[i][0] + h).toFixed(1)},${(p[i][1] + m[i] * h).toFixed(1)} ${(p[i + 1][0] - h).toFixed(1)},${(p[i + 1][1] - m[i + 1] * h).toFixed(1)} ${p[i + 1][0].toFixed(1)},${p[i + 1][1].toFixed(1)}`;
  }
  return s;
}
const tijdVan = (v: YTVideo) => Date.parse(`${(v.datum ?? v.date ?? '').slice(0, 10)}T${v.tijd ?? '12:00'}:00`);
/** waarde op tijdstip t: het eerste meetpunt op of na t (binnen 6 uur), anders null */
function op(rows: StatRow[], k: K, t: number): number | null {
  const r = rows.find((x) => typeof x[k] === 'number' && +new Date(x.at) >= t);
  return r && +new Date(r.at) - t < 6 * 36e5 ? (r[k] as number) : null;
}

export function Vergelijking({ alle, k, vids, eenheid }: { alle: StatRow[]; k: K; vids: YTVideo[]; eenheid: string }) {
  const lang = vids.filter((v) => v.type === 'long' && (v.status ?? 'public') === 'public' && !isNaN(tijdVan(v))).sort((a, b) => tijdVan(b) - tijdVan(a));
  const [nu, vorige] = lang;
  if (!nu || !vorige) return <div className="text-[13px] text-slate-500">Vergelijken met de vorige video kan vanaf twee lange video's.</div>;
  const rows = alle.filter((r) => typeof r[k] === 'number');
  const laatste = rows[rows.length - 1];
  const t1 = tijdVan(nu), t0 = tijdVan(vorige);
  const venster = Math.min(laatste ? +new Date(laatste.at) - t1 : 0, t1 - t0);
  const a1 = op(rows, k, t1), b1 = op(rows, k, t1 + venster);
  const a0 = op(rows, k, t0), b0 = op(rows, k, t0 + venster);
  const dagen = Math.max(0, Math.round(venster / 864e5));
  if (a1 == null || b1 == null) return <div className="text-[13px] text-slate-500">De meetpunten beginnen pas na de upload van "{nu.title}". Vergelijken kan bij de volgende video.</div>;
  return (
    <div className="text-[13px] text-slate-300">
      In de eerste {dagen} {dagen === 1 ? 'dag' : 'dagen'} na <b className="text-white">"{nu.title}"</b>: <b style={{ color: '#3ddc97' }}>+{nl(b1 - a1)}</b> {eenheid}.{' '}
      {a0 != null && b0 != null ? <>Na de vorige ("{vorige.title}") in dezelfde tijd: <b className="text-white">+{nl(b0 - a0)}</b>.</> : <span className="text-slate-500">Van de vorige video zijn niet genoeg meetpunten om te vergelijken.</span>}
    </div>
  );
}

export default function Grafiek({ rows, alle, k, color, label, info, vids }: { rows: StatRow[]; alle: StatRow[]; k: K; color: string; label: string; info: string; vids: YTVideo[] }) {
  const ref = useRef<SVGSVGElement>(null);
  const [hover, setHover] = useState<number | null>(null);
  const pts = useMemo(() => rows.filter((r) => typeof r[k] === 'number'), [rows, k]);
  const vals = pts.map((r) => r[k] as number);
  const min = Math.min(...vals), max = Math.max(...vals), span = max - min || 1;
  const t0 = pts.length ? +new Date(pts[0].at) : 0, t1 = pts.length ? +new Date(pts[pts.length - 1].at) : 1;
  const x = (t: number) => PL + ((t - t0) / ((t1 - t0) || 1)) * (W - PL - PR);
  const y = (v: number) => H - PB - ((v - min) / span) * (H - PT - PB);
  const xy: [number, number][] = pts.map((r) => [x(+new Date(r.at)), y(r[k] as number)]);
  const lijn = pad(xy);
  const uploads = vids.filter((v) => (v.status ?? 'public') === 'public').map((v) => ({ v, t: tijdVan(v) })).filter((u) => u.t >= t0 && u.t <= t1)
    .map((u) => { const val = op(pts, k, u.t) ?? (pts[pts.length - 1]?.[k] as number); return { ...u, cx: x(u.t), cy: y(val) }; });
  const last = vals[vals.length - 1], diff = vals.length > 1 ? last - vals[0] : null;
  const beweeg = (e: React.PointerEvent) => {
    const b = ref.current?.getBoundingClientRect(); if (!b || !xy.length) return;
    const px = ((e.clientX - b.left) / b.width) * W;
    let best = 0; for (let i = 1; i < xy.length; i++) if (Math.abs(xy[i][0] - px) < Math.abs(xy[best][0] - px)) best = i;
    setHover(best);
  };
  const h = hover != null ? pts[hover] : null;
  const dichtbij = h ? uploads.filter((u) => Math.abs(u.t - +new Date(h.at)) < 12 * 36e5) : [];
  return (
    <section className="panel p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="flex items-center text-[15px] font-semibold text-slate-300">{label}<span title={info} aria-label={info} className="ml-1.5 inline-flex h-4 w-4 cursor-help items-center justify-center rounded-full bg-white/10 text-[11px] font-bold text-slate-300">i</span></span>
        {diff != null && <span className="text-[14px] font-semibold" style={{ color: diff >= 0 ? '#3ddc97' : '#ff4d6d' }}>{diff >= 0 ? '▲ +' : '▼ '}{nl(diff)} in deze periode</span>}
      </div>
      <div className="font-display text-[34px] font-bold" style={{ color }}>{last != null && Number.isFinite(last) ? nl(last) : '—'}</div>
      {pts.length > 0 && <Bron bron="database, elk uur gemeten" at={pts[pts.length - 1].at} relatief />}
      {pts.length > 1 ? (
        <div className="relative mt-1">
          <svg ref={ref} viewBox={`0 0 ${W} ${H}`} className="h-48 w-full touch-none" role="img" aria-label={`${label} over tijd`} onPointerMove={beweeg} onPointerDown={beweeg} onPointerLeave={() => setHover(null)}>
            <defs><linearGradient id={`gr-${k}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor={color} stopOpacity=".32" /><stop offset="100%" stopColor={color} stopOpacity="0" /></linearGradient></defs>
            {[0, 0.5, 1].map((f) => <line key={f} x1={PL} x2={W - PR} y1={PT + f * (H - PT - PB)} y2={PT + f * (H - PT - PB)} stroke="rgba(255,255,255,.06)" />)}
            <text x={PL} y={H - 6} fill="#8792b8" fontSize="12">{kortTijd(t0, false)}</text>
            <text x={W - PR} y={H - 6} fill="#8792b8" fontSize="12" textAnchor="end">{kortTijd(t1, false)}</text>
            <text x={W - PR} y={PT - 5} fill="#8792b8" fontSize="12" textAnchor="end">{nl(max)}</text>
            <path d={`${lijn} L${xy[xy.length - 1][0]},${H - PB} L${xy[0][0]},${H - PB} Z`} fill={`url(#gr-${k})`} />
            <path d={lijn} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
            {uploads.map((u) => <circle key={(u.v.id ?? u.v.title) + u.t} cx={u.cx} cy={u.cy} r={u.v.type === 'long' ? 6 : 4} fill={u.v.type === 'long' ? '#ff8a3d' : '#3db8ff'} stroke="#070b1a" strokeWidth="2"><title>{u.v.type === 'long' ? 'Lange video' : 'Short'}: {u.v.title}</title></circle>)}
            {h && <><line x1={xy[hover!][0]} x2={xy[hover!][0]} y1={PT} y2={H - PB} stroke="rgba(255,255,255,.25)" strokeDasharray="3 3" /><circle cx={xy[hover!][0]} cy={xy[hover!][1]} r="5" fill={color} stroke="#fff" strokeWidth="1.5" /></>}
          </svg>
          {h && (
            <div className="pointer-events-none absolute top-0 z-10 max-w-[240px] rounded-xl border border-white/10 bg-[#0b1230]/95 px-3 py-2 text-[12px] shadow-xl"
              style={{ left: `${Math.min(70, Math.max(0, (xy[hover!][0] / W) * 100 - 15))}%` }}>
              <div className="text-slate-400">{kortTijd(h.at)}</div>
              <div className="font-display text-[16px] font-bold text-white">{nl(h[k] as number)} {label.toLowerCase()}</div>
              {dichtbij.map((u) => <div key={u.v.id ?? u.v.title} className="mt-0.5 text-slate-300">{u.v.type === 'long' ? '🎬' : '📱'} {u.v.title}</div>)}
            </div>
          )}
          <div className="mt-1 flex flex-wrap gap-3 text-[12px] text-slate-400"><span><span className="mr-1 inline-block h-2.5 w-2.5 rounded-full bg-[#ff8a3d]" />lange video online</span><span><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[#3db8ff]" />short online</span></div>
          <div className="mt-2 border-t border-white/5 pt-2"><Vergelijking alle={alle} k={k} vids={vids} eenheid={label.toLowerCase()} /></div>
        </div>
      ) : <div className="mt-2 rounded-xl bg-white/[.03] p-4 text-[14px] text-slate-400">De grafiek groeit vanzelf: elk uur komt er een meetpunt bij.</div>}
    </section>
  );
}
