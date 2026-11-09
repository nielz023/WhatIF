/**
 * STEMMENPANEEL (verbeterlijst punt 54). Per personage de ElevenLabs-stem, met een afspeelknop als er een
 * opgenomen regel van dat personage in de map staat, en "Wisselen" (een opdracht voor Claude).
 * Stemmen: videos/<map>/stemmen.tsv als die er is, anders de vaste lijst in het HQ.
 * Tegoed: de ElevenLabs-koppeling geeft geen tegoed door, dus we tonen de laatst bekende kosten uit status.json.
 */
import { useEffect, useState } from 'react';
import { Play, Mic } from 'lucide-react';
import { useLive } from '../../services/live';
import { useTools } from '../../services/tools';
import { leesBestand } from '../../services/kennis';
import { lijstMap, leesTsv, map, naamVan, type Item } from '../../services/studio';
import { VOICE_SETS, type RealVideo } from '../../data/driftmark';
import { openBestand } from '../../components/shared/BestandViewer';
import { openOpdracht } from '../../services/real';
import Bron from '../../components/shared/Bron';
import Blok from '../../components/shared/Blok';

const plat = (s: string) => s.toLowerCase().normalize('NFD').replace(/[^a-z0-9]/g, '');

function Video({ v }: { v: RealVideo }) {
  const [stemmen, setStemmen] = useState<{ rol: string; id: string }[] | null>(null);
  const [uitBestand, setUitBestand] = useState(false);
  const [audio, setAudio] = useState<Item[] | null | 'laden'>('laden');
  useEffect(() => {
    let weg = false;
    const vast = VOICE_SETS.find((s) => s.video.startsWith(`Video ${v.nr} `))?.stemmen.map(([rol, id]) => ({ rol, id })) ?? [];
    void leesBestand(`${map(v.folder)}/stemmen.tsv`).then((r) => {
      if (weg) return;
      if (r.kind === 'tekst') { const rows = leesTsv(r.tekst).map(([rol, id]) => ({ rol, id })); if (rows.length) { setStemmen(rows); setUitBestand(true); return; } }
      setStemmen(vast);
    });
    void lijstMap(`${map(v.folder)}/audio`, true).then((l) => { if (!weg) setAudio(l); });
    return () => { weg = true; };
  }, [v.folder, v.nr]);
  const mp3 = Array.isArray(audio) ? audio.filter((a) => !a.isDirectory && /\.(mp3|wav)$/i.test(a.path)) : [];
  const voorbeeld = (rol: string) => mp3.find((a) => plat(naamVan(a.path).replace(/\.\w+$/, '').split('_').slice(1).join('')) === plat(rol))?.path;
  if (!stemmen) return <div className="text-[13px] text-slate-400">Stemmen laden…</div>;
  return (
    <section className="panel p-4">
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <span className="font-display text-[17px] font-bold text-white">Video {v.nr} · {v.werktitel}</span>
        <span className="text-[12px] text-slate-500">{uitBestand ? `uit ${map(v.folder)}/stemmen.tsv` : stemmen.length ? 'vaste lijst in het HQ' : ''}{audio === 'laden' ? ' · opnames zoeken…' : mp3.length ? ` · ${mp3.length} opnames gevonden` : ' · geen opnames gevonden'}</span>
      </div>
      {stemmen.length ? (
        <ul className="grid gap-1.5 sm:grid-cols-2">
          {stemmen.map((s) => {
            const p = voorbeeld(s.rol);
            return (
              <li key={s.rol} className="flex items-center gap-2 rounded-lg bg-white/[.03] px-2.5 py-1.5">
                <button disabled={!p} onClick={() => p && openBestand(p)} title={p ? `Afspelen: ${naamVan(p)}` : 'Geen opname van dit personage gevonden'} aria-label={`Stem van ${s.rol} afspelen`}
                  className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${p ? 'bg-orange-500 text-white hover:bg-orange-400' : 'bg-white/5 text-slate-600'}`}><Play size={14} /></button>
                <span className="min-w-0 flex-1"><span className="block truncate text-[14px] font-semibold text-white">{s.rol}</span><code className="block truncate text-[11px] text-slate-500">{s.id}</code></span>
                <button className="btn-ghost shrink-0 !px-2 !py-1 text-[12px]" onClick={() => openOpdracht({ titel: `Stem van ${s.rol} wisselen`, text: `Video ${v.nr} (${v.werktitel}): wissel de stem van ${s.rol} (nu ElevenLabs ${s.id}). Stel 3 andere stemmen voor met een korte proefregel, dan kies ik. Genereer daarna alleen in deze thread.` })}>Wisselen</button>
              </li>
            );
          })}
        </ul>
      ) : <p className="text-[14px] text-slate-400">Voor deze video zijn nog geen stemmen gekozen.</p>}
    </section>
  );
}

export default function Stemmen() {
  const videos = useLive((s) => s.data.videos);
  const costs = useLive((s) => s.data.costs) ?? [];
  const el = useTools((s) => s.tools.elevenlabs);
  const kosten = costs.filter((c) => /elevenlabs/i.test(c.wat));
  const lijst = [...videos].filter((v) => v.folder).reverse().slice(0, 4);
  return (
    <div className="grid gap-3">
      <section className="panel p-4">
        <div className="flex items-center gap-2 font-display text-[17px] font-bold text-white"><Mic size={16} className="text-orange-300" />ElevenLabs-tegoed</div>
        <p className="mt-1 text-[13px] text-slate-300">Het tegoed zelf kan het HQ niet uitlezen: de koppeling geeft alleen je stem-flows door{el?.status === 'ok' ? ' (koppeling werkt)' : el?.status === 'geen' ? ' (en die werkt alleen op de gepubliceerde pagina)' : ''}. Kijk voor het tegoed op elevenlabs.io.</p>
        {kosten.length ? (
          <ul className="mt-2 space-y-1 text-[13px] text-slate-300">{kosten.slice(0, 4).map((c, i) => (
            <li key={i} className="rounded-lg bg-white/[.03] px-2.5 py-1.5"><b className="text-white">{c.wat}</b>{c.credits ? ` · ${c.credits} credits` : ''}{c.notitie ? ` · ${c.notitie}` : ''} <Bron bron="kostenlijst" at={c.datum} schatting={/schatting|~/.test(c.credits ?? '')} /></li>
          ))}</ul>
        ) : <p className="mt-1 text-[13px] text-slate-500">Er zijn nog geen ElevenLabs-kosten genoteerd.</p>}
      </section>
      {lijst.map((v) => <Blok key={v.nr} naam={`Stemmen video ${v.nr}`}><Video v={v} /></Blok>)}
    </div>
  );
}
