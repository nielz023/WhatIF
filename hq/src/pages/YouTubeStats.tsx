/**
 * OP YOUTUBE (niels 2026-11-06: "mijn video's vanuit YouTube zien, met de statistieken via vidIQ, en alle shorts").
 * Alle lange video's en shorts zoals ze op YouTube staan, met hun echte cijfers:
 * - weergaven en likes: elk uur uit de openbare YouTube-feed (automation/videos.py, gratis)
 * - kijkduur, % bekeken, reacties, gedeeld, nieuwe abonnees: elke ochtend uit vidIQ (YouTube Analytics, 5 credits per dag)
 */
import { useEffect, useState } from 'react';
import { Eye, ThumbsUp, MessageCircle, Share2, Timer, UserPlus, Youtube, CalendarClock } from 'lucide-react';
import { useLive, readFile, type YTVideo } from '../services/live';

type Filter = 'alles' | 'long' | 'short';
type Sort = 'nieuw' | 'views' | 'avp' | 'likes';
const FILTERS: { id: Filter; label: string }[] = [{ id: 'alles', label: 'Alles' }, { id: 'long', label: "Lange video's" }, { id: 'short', label: 'Shorts' }];
const SORTS: { id: Sort; label: string }[] = [{ id: 'nieuw', label: 'Nieuwste' }, { id: 'views', label: 'Meeste weergaven' }, { id: 'avp', label: 'Best bekeken' }, { id: 'likes', label: 'Meeste likes' }];

const nl = (n: number | undefined | null) => (n ?? 0).toLocaleString('nl-NL');
const mmss = (s?: number) => (s == null ? '' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);
const MAAND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'];
function wanneer(v: YTVideo) {
  const d = (v.datum ?? v.date ?? '').slice(0, 10);
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d);
  return m ? `${+m[3]} ${MAAND[+m[2] - 1]}${v.tijd ? ` ${v.tijd}` : ''}` : '';
}
const tijdstip = (iso?: string) => (iso ? new Date(iso).toLocaleString('nl-NL', { timeZone: 'Europe/Amsterdam', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : null);
const isPublic = (v: YTVideo) => (v.status ?? 'public') === 'public';
const sortKey = (v: YTVideo) => `${v.datum ?? v.date ?? ''} ${v.tijd ?? ''}`;

/** cursus (Faceless YouTube Handboek): AVD onder 30% werk nodig, 30-40 oké, 40-50 goed, 50%+ geweldig (lange video's) */
function avpOordeel(v: YTVideo): [string, string] {
  const p = v.avp ?? 0;
  if (v.type !== 'long') return ['', '#3db8ff'];
  if (p >= 50) return ['geweldig', '#3ddc97'];
  if (p >= 40) return ['goed', '#3ddc97'];
  if (p >= 30) return ['oké', '#3db8ff'];
  return ['werk nodig', '#ff8a3d'];
}

/** thumbnail: eerst de meegebouwde, dan die uit de projectbestanden (nieuwe uploads), anders een vlak */
function Thumb({ v }: { v: YTVideo }) {
  const [src, setSrc] = useState<string | null>(v.id ? `./thumbs/${v.id}.jpg` : null);
  const [stap, setStap] = useState(0);
  useEffect(() => () => { if (src?.startsWith('blob:')) URL.revokeObjectURL(src); }, [src]);
  const fout = async () => {
    if (stap === 0 && v.id) {
      setStap(1);
      try {
        const b = await readFile(`driftmark-hq/thumbs/${v.id}.jpg`);
        setSrc(URL.createObjectURL(new Blob([b as BlobPart], { type: 'image/jpeg' })));
        return;
      } catch { /* geen toegang of geen bestand */ }
    }
    setSrc(null);
  };
  const box = 'relative aspect-video w-[132px] shrink-0 overflow-hidden rounded-lg sm:w-[168px]';
  if (!src) return <div className={`${box} flex items-center justify-center bg-gradient-to-br from-[#1b2a5a] to-[#0b1636] text-[26px]`} aria-hidden>{v.type === 'long' ? '🎬' : '📱'}</div>;
  return (
    <div className={box}>
      <img src={src} alt="" loading="lazy" className="h-full w-full object-cover" onError={() => void fout()} />
      {v.type === 'short' && <span className="absolute left-1 top-1 rounded bg-black/70 px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white">Short</span>}
    </div>
  );
}

function Cel({ icon, label, value, sub, title }: { icon: JSX.Element; label: string; value: string; sub?: string; title?: string }) {
  return (
    <div className="min-w-0 rounded-lg bg-white/[.04] px-2 py-1.5" title={title}>
      <div className="flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">{icon}{label}</div>
      <div className="truncate font-display text-[17px] font-bold text-white">{value}</div>
      {sub && <div className="truncate text-[11px] text-slate-400">{sub}</div>}
    </div>
  );
}

function Rij({ v }: { v: YTVideo }) {
  const [oordeel, kleur] = avpOordeel(v);
  const heeftStats = v.avd != null;
  const perHonderd = v.views ? ((v.likes ?? 0) / v.views) * 100 : 0;
  return (
    <a href={v.url ?? (v.id ? `https://youtu.be/${v.id}` : undefined)} target="_blank" rel="noreferrer"
      className="block rounded-2xl bg-white/[.03] p-2.5 ring-1 ring-white/5 transition hover:bg-white/[.06] hover:ring-white/15">
      <div className="flex gap-3">
        <Thumb v={v} />
        <div className="min-w-0 flex-1">
          <div className="line-clamp-2 text-[15px] font-semibold leading-snug text-white">{v.title}</div>
          <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[12px] text-slate-400">
            <span className={`rounded-full px-2 py-0.5 font-semibold ${v.type === 'long' ? 'bg-orange-500/15 text-orange-200' : 'bg-sky-500/15 text-sky-200'}`}>{v.type === 'long' ? 'Lange video' : 'Short'}</span>
            <span>{wanneer(v)}</span>
            <span className="inline-flex items-center gap-1 text-slate-500"><Youtube size={12} />openen</span>
          </div>
          {heeftStats && v.avp != null && (
            <div className="mt-2 hidden sm:block">
              <div className="flex items-baseline justify-between text-[12px]"><span className="text-slate-400">Gemiddeld bekeken</span><span className="font-semibold" style={{ color: kleur }}>{v.avp.toLocaleString('nl-NL')}%{oordeel ? ` · ${oordeel}` : ''}</span></div>
              <div className="mt-0.5 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full" style={{ width: `${Math.max(2, Math.min(100, v.avp))}%`, background: kleur }} /></div>
            </div>
          )}
        </div>
      </div>
      <div className="mt-2 grid grid-cols-3 gap-1.5 sm:grid-cols-6">
        <Cel icon={<Eye size={11} />} label="Weergaven" value={nl(v.views)} title="Elk uur bijgewerkt uit YouTube" />
        <Cel icon={<ThumbsUp size={11} />} label="Likes" value={nl(v.likes)} sub={v.views ? `${perHonderd.toLocaleString('nl-NL', { maximumFractionDigits: 1 })} per 100` : undefined} title="Likes per 100 weergaven (cursus: 1 per 100)" />
        <Cel icon={<MessageCircle size={11} />} label="Reacties" value={v.comments != null ? nl(v.comments) : '–'} />
        <Cel icon={<Share2 size={11} />} label="Gedeeld" value={v.shares != null ? nl(v.shares) : '–'} />
        <Cel icon={<Timer size={11} />} label="Kijkduur" value={heeftStats ? mmss(v.avd) : 'volgt'} sub={heeftStats && v.avp != null ? `${v.avp.toLocaleString('nl-NL')}% bekeken` : 'over 1-2 dagen'} title="Gemiddelde kijkduur per weergave (vidIQ). YouTube Analytics loopt 1 à 2 dagen achter." />
        <Cel icon={<UserPlus size={11} />} label="Abonnees" value={v.subs != null ? `+${nl(v.subs)}` : '–'} title="Nieuwe abonnees door deze video (vidIQ)" />
      </div>
    </a>
  );
}

export default function YouTubeStats() {
  const yt = useLive((s) => s.data.youtube);
  const [filter, setFilter] = useState<Filter>('alles');
  const [sort, setSort] = useState<Sort>('nieuw');
  const alle = yt?.videos ?? [];
  const zicht = alle.filter((v) => filter === 'alles' || v.type === filter);
  const k: Record<Sort, (v: YTVideo) => number | string> = { nieuw: sortKey, views: (v) => v.views ?? 0, avp: (v) => v.avp ?? -1, likes: (v) => v.likes ?? 0 };
  const online = zicht.filter(isPublic).sort((a, b) => { const x = k[sort](a), y = k[sort](b); return typeof x === 'string' ? String(y).localeCompare(x) : (y as number) - (x as number); });
  const gepland = zicht.filter((v) => !isPublic(v)).sort((a, b) => sortKey(a).localeCompare(sortKey(b)));

  const som = (f: (v: YTVideo) => number | undefined) => online.reduce((a, v) => a + (f(v) ?? 0), 0);
  const metAvp = online.filter((v) => v.avp != null && v.views);
  const gemAvp = metAvp.length ? metAvp.reduce((a, v) => a + v.avp! * v.views!, 0) / metAvp.reduce((a, v) => a + v.views!, 0) : null;
  const uren = som((v) => v.minuten) / 60;
  const urenLang = online.filter((v) => v.type === 'long').reduce((a, v) => a + (v.minuten ?? 0), 0) / 60;
  const u1 = (n: number) => n.toLocaleString('nl-NL', { maximumFractionDigits: 1 });
  const feed = tijdstip(yt?.feedAt); const vq = tijdstip(yt?.vidiqAt);

  return (
    <div className="space-y-3">
      <section className="panel p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap gap-1.5">{FILTERS.map((f) => (
            <button key={f.id} onClick={() => setFilter(f.id)} className={`rounded-full px-3.5 py-1.5 text-[13px] font-semibold ${filter === f.id ? 'bg-orange-500 text-white' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}>
              {f.label} <span className="opacity-70">{alle.filter((v) => isPublic(v) && (f.id === 'alles' || v.type === f.id)).length}</span>
            </button>
          ))}</div>
          <label className="flex items-center gap-2 text-[13px] text-slate-400">Sorteren
            <select value={sort} onChange={(e) => setSort(e.target.value as Sort)} className="rounded-lg border border-white/10 bg-black/40 px-2 py-1.5 text-[13px] text-white">
              {SORTS.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
            </select>
          </label>
        </div>
        <div className="mt-3 grid grid-cols-2 gap-1.5 sm:grid-cols-3 lg:grid-cols-6">
          <Cel icon={<Eye size={11} />} label="Weergaven" value={nl(som((v) => v.views))} />
          <Cel icon={<ThumbsUp size={11} />} label="Likes" value={nl(som((v) => v.likes))} />
          <Cel icon={<MessageCircle size={11} />} label="Reacties" value={nl(som((v) => v.comments))} />
          <Cel icon={<UserPlus size={11} />} label="Abonnees erbij" value={`+${nl(som((v) => v.subs))}`} />
          <Cel icon={<Timer size={11} />} label="Gem. bekeken" value={gemAvp != null ? `${gemAvp.toLocaleString('nl-NL', { maximumFractionDigits: 1 })}%` : '–'} sub="gewogen naar weergaven" />
          <Cel icon={<Timer size={11} />} label="Kijkuren" value={u1(uren)} sub={filter === 'short' ? 'tellen niet mee voor YPP' : filter === 'long' ? 'tellen mee voor YPP' : `${u1(urenLang)} lang (telt voor YPP)`} title="YouTube Partner Programma: 4.000 kijkuren uit lange video's in 12 maanden" />
        </div>
        <p className="mt-2 text-[12px] leading-snug text-slate-500">
          Weergaven en likes komen elk uur van YouTube{feed ? ` (laatst ${feed})` : ''}. Kijkduur, reacties, gedeeld en abonnees komen elke ochtend via vidIQ{vq ? ` (laatst ${vq})` : ''}.
          YouTube Analytics loopt 1 à 2 dagen achter, dus bij de nieuwste uploads volgt de kijkduur later. CTR en vertoningen geeft vidIQ niet: die staan alleen in YouTube Studio.
        </p>
      </section>

      {online.length ? <div className="grid gap-2 xl:grid-cols-2">{online.map((v) => <Rij key={v.id ?? v.title} v={v} />)}</div>
        : <div className="panel p-4 text-[14px] text-slate-400">Nog geen video's gevonden. De lijst vult zich bij de volgende uurronde.</div>}

      {gepland.length > 0 && (
        <section className="panel p-4">
          <div className="mb-2 flex items-center gap-2 font-display text-[16px] font-bold text-white"><CalendarClock size={16} className="text-sky-300" />Ingepland</div>
          <div className="space-y-1">{gepland.map((v) => (
            <div key={v.id ?? v.title} className="flex items-center justify-between gap-2 rounded-lg bg-white/[.03] px-2.5 py-1.5 text-[13px]">
              <span className="truncate text-slate-200">{v.type === 'long' ? '🎬 ' : '📱 '}{v.title}</span>
              <span className="shrink-0 text-slate-400">{(v.status ?? '').replace(/^gepland\s*/, '') || wanneer(v)}</span>
            </div>
          ))}</div>
        </section>
      )}
    </div>
  );
}
