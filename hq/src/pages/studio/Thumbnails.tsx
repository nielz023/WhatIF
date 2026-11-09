/**
 * THUMBNAILMUUR (verbeterlijst punt 55). Alle thumbnailvarianten van een video naast elkaar, klein (zoals in de
 * lijst naast een video op YouTube) en groot (zoals op de startpagina), met de echte titel eronder.
 * "Kies deze" stuurt de keuze als opdracht naar Claude. Varianten: de map thumbnail/ van de video en de
 * thumbnails die status.json bij de video noemt.
 */
import { useEffect, useState } from 'react';
import { useLive, type Output } from '../../services/live';
import { laadBeeld } from '../../services/kennis';
import { lijstMap, map, naamVan } from '../../services/studio';
import { order, openOpdracht } from '../../services/real';
import { openBestand } from '../../components/shared/BestandViewer';
import { useGame } from '../../store/useGame';
import type { RealVideo } from '../../data/driftmark';
import Blok from '../../components/shared/Blok';

const BEELD = /\.(jpe?g|png|webp)$/i;
const type = (p: string) => (/\.png$/i.test(p) ? 'image/png' : /\.webp$/i.test(p) ? 'image/webp' : 'image/jpeg');

function Plaatje({ pad, groot, titel, kanaal, gekozen, kies }: { pad: string; groot: boolean; titel: string; kanaal: string; gekozen: boolean; kies: () => void }) {
  const [url, setUrl] = useState<string | null>(null);
  const [fout, setFout] = useState(false);
  useEffect(() => {
    const ac = new AbortController(); let u: string | null = null;
    void laadBeeld(pad, type(pad), ac.signal).then((x) => { if (ac.signal.aborted) URL.revokeObjectURL(x); else { u = x; setUrl(x); } }).catch(() => { if (!ac.signal.aborted) setFout(true); });
    return () => { ac.abort(); if (u) URL.revokeObjectURL(u); };
  }, [pad]);
  return (
    <figure className={`${groot ? 'w-full sm:w-[360px]' : 'w-[168px]'} shrink-0`}>
      <button onClick={() => openBestand(pad)} className={`block aspect-video w-full overflow-hidden rounded-xl bg-white/5 ${gekozen ? 'ring-2 ring-emerald-400' : ''}`} title="Groot bekijken">
        {url ? <img src={url} alt={naamVan(pad)} className="h-full w-full object-cover" /> : <span className="flex h-full items-center justify-center text-[12px] text-slate-500">{fout ? 'kon niet laden' : 'laden…'}</span>}
      </button>
      <figcaption className="mt-1.5">
        <div className={`line-clamp-2 font-semibold leading-snug text-white ${groot ? 'text-[15px]' : 'text-[12px]'}`}>{titel}</div>
        <div className="text-[11px] text-slate-400">{kanaal}</div>
        <div className="mt-1 flex items-center justify-between gap-1">
          <span className="truncate text-[11px] text-slate-500" title={pad}>{naamVan(pad)}</span>
          {gekozen ? <span className="shrink-0 text-[12px] font-semibold text-emerald-300">gekozen</span> : <button className="btn-ghost shrink-0 !px-2 !py-0.5 text-[12px]" onClick={kies}>Kies deze</button>}
        </div>
      </figcaption>
    </figure>
  );
}

function Video({ v, groot }: { v: RealVideo; groot: boolean }) {
  const outs = (useLive((s) => s.data.outputs)?.[String(v.nr)] ?? []).filter((o): o is Output => !!o && typeof o === 'object' && typeof o.path === 'string');
  const kanaal = useLive((s) => s.data.channel.name);
  const toast = useGame((s) => s.toast);
  const [uitMap, setUitMap] = useState<string[] | null>(null);
  useEffect(() => { let weg = false; void lijstMap(`${map(v.folder)}/thumbnail`).then((l) => { if (!weg) setUitMap((l ?? []).filter((x) => !x.isDirectory && BEELD.test(x.path)).map((x) => x.path)); }); return () => { weg = true; }; }, [v.folder]);
  const gekozen = outs.find((o) => /thumb/i.test(o.path) && /definitief|gekozen/i.test(`${o.name} ${o.path}`))?.path;
  // dubbele (zelfde naam als .png en .jpg) en "origineel"-bestanden weglaten
  const alle = [...new Set([...outs.filter((o) => /thumb/i.test(o.path) && BEELD.test(o.path)).map((o) => o.path), ...(uitMap ?? [])])];
  const paden = alle.filter((p) => !/origineel/i.test(p) && !/^render_/i.test(naamVan(p)) && !(p.endsWith('.png') && alle.includes(p.replace(/\.png$/, '.jpg')))).slice(0, 10);
  return (
    <section className="panel p-4">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <span className="font-display text-[17px] font-bold text-white">Video {v.nr} · {v.werktitel}</span>
        <button className="btn-ghost !py-1 text-[13px]" onClick={() => openOpdracht({ titel: `Thumbnails video ${v.nr}`, text: `Video ${v.nr} (${v.werktitel}, "${v.title}"): maak 3 nieuwe thumbnailvarianten in ${map(v.folder)}/thumbnail/ (1280x720, grote tekst van max 3 woorden).` })}>Nieuwe varianten vragen</button>
      </div>
      {uitMap === null ? <p className="text-[13px] text-slate-400">Varianten zoeken…</p>
        : paden.length ? <div className={`flex flex-wrap gap-4 ${groot ? '' : 'gap-3'}`}>{paden.map((p) => (
          <Plaatje key={p} pad={p} groot={groot} titel={v.title} kanaal={kanaal} gekozen={p === gekozen}
            kies={() => order(`Video ${v.nr} (${v.werktitel}): ik kies deze thumbnail: ${p}. Maak hem definitief (1280x720) en zet hem in status.json bij de outputs.`, toast, { doel: 'Thumbnail' })} />
        ))}</div>
        : <p className="text-[13px] text-slate-400">Nog geen thumbnails gevonden in {map(v.folder)}/thumbnail/.</p>}
    </section>
  );
}

export default function Thumbnails() {
  const videos = useLive((s) => s.data.videos);
  const [groot, setGroot] = useState(false);
  const lijst = [...videos].filter((v) => v.folder).reverse().slice(0, 4);
  return (
    <div className="grid gap-3">
      <div className="flex items-center gap-1 justify-self-start rounded-lg bg-white/5 p-0.5 text-[13px]">
        <button onClick={() => setGroot(false)} className={`rounded-md px-3 py-1 ${!groot ? 'bg-white/15 text-white' : 'text-slate-400'}`}>Klein, zoals naast een video</button>
        <button onClick={() => setGroot(true)} className={`rounded-md px-3 py-1 ${groot ? 'bg-white/15 text-white' : 'text-slate-400'}`}>Groot, zoals op de startpagina</button>
      </div>
      {lijst.map((v) => <Blok key={v.nr} naam={`Thumbnails video ${v.nr}`}><Video v={v} groot={groot} /></Blok>)}
    </div>
  );
}
