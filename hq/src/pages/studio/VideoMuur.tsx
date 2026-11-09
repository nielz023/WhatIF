/**
 * GROTE THUMBNAILS IN HET VIDEO-OVERZICHT (verbeterlijst punt 29).
 * Lange video's breed (16:9), shorts staand (9:16) zoals op YouTube. Bij aanwijzen (of tikken op een telefoon)
 * verschijnen de belangrijkste cijfers, elk met zijn bron.
 */
import { useEffect, useState } from 'react';
import { readFile, type YTVideo } from '../../services/live';
import { kortTijd } from '../../services/studio';

const nl = (n?: number | null) => (n ?? 0).toLocaleString('nl-NL');
const mmss = (s?: number) => (s == null ? '' : `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`);

/** eerst de meegebouwde thumbnail, dan die uit de projectbestanden, anders niets */
export function useThumb(id?: string) {
  const [src, setSrc] = useState<string | null>(id ? `./thumbs/${id}.jpg` : null);
  const [stap, setStap] = useState(0);
  useEffect(() => () => { if (src?.startsWith('blob:')) URL.revokeObjectURL(src); }, [src]);
  const fout = async () => {
    if (stap === 0 && id) {
      setStap(1);
      try { const b = await readFile(`driftmark-hq/thumbs/${id}.jpg`); setSrc(URL.createObjectURL(new Blob([b as BlobPart], { type: 'image/jpeg' }))); return; } catch { /* geen bestand */ }
    }
    setSrc(null);
  };
  return { src, fout };
}

function Tegel({ v }: { v: YTVideo }) {
  const { src, fout } = useThumb(v.id);
  const [open, setOpen] = useState(false);
  const kort = v.type === 'short';
  return (
    <a href={v.url ?? (v.id ? `https://youtu.be/${v.id}` : undefined)} target="_blank" rel="noreferrer"
      className={`group relative block overflow-hidden rounded-2xl bg-[#0b1636] ring-1 ring-white/10 transition hover:ring-orange-400/60 ${kort ? 'aspect-[9/16]' : 'aspect-video sm:col-span-2'}`}
      onTouchStart={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      {src ? <img src={src} alt="" loading="lazy" className="h-full w-full object-cover transition group-hover:scale-105" onError={() => void fout()} />
        : <div className="flex h-full w-full items-center justify-center text-[34px]" aria-hidden>{kort ? '📱' : '🎬'}</div>}
      <span className={`absolute left-2 top-2 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-white ${kort ? 'bg-sky-600/90' : 'bg-orange-600/90'}`}>{kort ? 'Short' : 'Lang'}</span>
      <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-2 pt-8">
        <div className="line-clamp-2 text-[13px] font-semibold leading-snug text-white">{v.title}</div>
        <div className="text-[12px] text-slate-300">{nl(v.views)} weergaven · {kortTijd(v.datum ?? v.date, false) ?? ''}</div>
      </div>
      <div className={`absolute inset-0 flex flex-col justify-center gap-1 bg-[#070b1a]/90 p-3 text-[13px] text-slate-200 transition ${open ? 'opacity-100' : 'opacity-0 group-hover:opacity-100 group-focus-visible:opacity-100'}`}>
        <div className="line-clamp-2 font-semibold text-white">{v.title}</div>
        <div>👁 {nl(v.views)} weergaven</div>
        <div>👍 {nl(v.likes)} likes{v.views ? ` (${(((v.likes ?? 0) / v.views) * 100).toLocaleString('nl-NL', { maximumFractionDigits: 1 })} per 100)` : ''}</div>
        <div className="text-[11px] text-slate-500">YouTube-feed, {kortTijd(v.viewsAt) ?? 'datum onbekend'}</div>
        {v.avd != null ? (<>
          <div>⏱ {mmss(v.avd)} gemiddeld{v.avp != null ? ` (${v.avp.toLocaleString('nl-NL')}% bekeken)` : ''}</div>
          <div>➕ {v.subs != null ? `+${nl(v.subs)} abonnees` : 'abonnees onbekend'}</div>
          <div className="text-[11px] text-slate-500">vidIQ, {kortTijd(v.statsAt) ?? 'datum onbekend'}</div>
        </>) : <div className="text-slate-400">Kijkduur en abonnees komen 1 à 2 dagen na de upload (vidIQ).</div>}
      </div>
    </a>
  );
}

export default function VideoMuur({ vids }: { vids: YTVideo[] }) {
  if (!vids.length) return <div className="panel p-4 text-[14px] text-slate-400">Nog geen video's gevonden.</div>;
  return <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-6">{vids.map((v) => <Tegel key={v.id ?? v.title} v={v} />)}</div>;
}
