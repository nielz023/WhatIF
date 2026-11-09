/**
 * UPLOADDAG-SCHERM (verbeterlijst punt 11 en 57).
 * Per video alles klaar om te plakken in YouTube Studio: titel, beschrijving, tags, hoofdstukken, vastgezette reactie,
 * thumbnail en waar het videobestand staat. Elk veld met een kopieerknop, met een afvinklijst ernaast.
 * Bron: videos/<map>/youtube_upload.md in de projectbestanden.
 */
import { useEffect, useState } from 'react';
import { Copy, Check, FileText, RefreshCw } from 'lucide-react';
import { leesBestand, laadBeeld } from '../services/kennis';
import { openBestand } from '../components/shared/BestandViewer';
import { useGame } from '../store/useGame';

const VIDEOS: { nr: number; naam: string; map: string; bestand?: string }[] = [
  { nr: 5, naam: 'Video 5 · Days Left', map: 'videos/dagen-over' },
  { nr: 4, naam: 'Video 4 · Never Die', map: 'videos/nooit-dood' },
  { nr: 3, naam: 'Video 3 · No Rules', map: 'videos/geen-regels', bestand: 'Documenten\\WHAT IF\\video3\\WHAT_IF_NO_RULES.mp4' },
  { nr: 2, naam: 'Video 2 · 10x Faster', map: 'videos/10x-sneller' },
  { nr: 1, naam: 'Video 1 · 2x Stronger', map: 'videos/2x-sterker', bestand: 'WHAT IF\\WHAT_IF_2x_STRONGER.mp4' },
];

interface Pakket { titel?: string; beschrijving?: string; tags?: string; hoofdstukken?: string; reactie?: string; thumb?: string; instellingen?: string }

/** Leest youtube_upload.md: secties op ## koppen. */
export function leesPakket(md: string, map: string): Pakket {
  const secties: Record<string, string> = {};
  let kop = '';
  for (const r of md.split('\n')) {
    const m = r.match(/^##\s+(.*)/);
    if (m) { kop = m[1].toLowerCase(); secties[kop] = ''; continue; }
    if (kop) secties[kop] += r + '\n';
  }
  const zoek = (re: RegExp) => Object.entries(secties).find(([k]) => re.test(k))?.[1] ?? '';
  const p: Pakket = {};
  const t = zoek(/^titel/);
  p.titel = t.match(/\*\*(.+?)\*\*/)?.[1]?.trim() || t.trim().split('\n')[0];
  const b = zoek(/^beschrijving/);
  const delen = b.split(/^---\s*$/m);
  p.beschrijving = (delen.length >= 3 ? delen[1] : b).trim();
  p.hoofdstukken = (p.beschrijving.match(/^\d{1,2}:\d{2}(:\d{2})?\s.+$/gm) ?? []).join('\n') || undefined;
  const tg = zoek(/^tags/);
  p.tags = tg.match(/Komma-lijst[^\n]*\n+([^\n]+)/i)?.[1]?.trim() || tg.trim().split('\n\n')[0].split(/,\s*/).join(',');
  const rc = zoek(/vastgezette reactie/);
  p.reactie = rc.trim().split('\n\n')[0] || undefined;
  const inst = zoek(/instellingen/);
  p.instellingen = inst.trim() || undefined;
  const th = (inst + t + md).match(/`([^`]*thumbnail[^`]*\.(?:jpg|jpeg|png))`/i)?.[1];
  if (th) p.thumb = th.startsWith('videos/') ? th : `${map}/${th}`;
  return p;
}

function Veld({ naam, waarde, mono, rijen = 1 }: { naam: string; waarde?: string; mono?: boolean; rijen?: number }) {
  const [ok, setOk] = useState(false);
  const toast = useGame((s) => s.toast);
  const kopieer = async () => {
    try { await navigator.clipboard.writeText(waarde ?? ''); setOk(true); setTimeout(() => setOk(false), 2000); } catch { toast('Kopiëren lukte niet; selecteer de tekst en kopieer met Ctrl+C.', 'info'); }
  };
  return (
    <div className="rounded-2xl bg-white/[.04] p-3">
      <div className="mb-1.5 flex items-center justify-between gap-2">
        <span className="text-[12px] font-bold uppercase tracking-wider text-slate-400">{naam}{waarde ? <span className="ml-2 font-normal normal-case tracking-normal text-slate-500">{waarde.length} tekens</span> : null}</span>
        {waarde && <button className={`btn-ghost !py-1 text-[12px] ${ok ? 'text-emerald-300' : ''}`} onClick={() => void kopieer()}>{ok ? <><Check size={12} />Gekopieerd</> : <><Copy size={12} />Kopiëren</>}</button>}
      </div>
      {waarde ? <div className={`${rijen > 1 ? 'max-h-64 overflow-y-auto' : ''} whitespace-pre-wrap break-words text-[14px] text-slate-100 ${mono ? 'font-mono text-[12px]' : ''}`}>{waarde}</div>
        : <div className="text-[13px] text-slate-500">Nog niet klaar. Vraag Claude om het uploadpakket.</div>}
    </div>
  );
}

const CHECK = ['Video geüpload in Studio', 'Titel geplakt', 'Beschrijving geplakt', 'Tags geplakt', 'Thumbnail geüpload', 'Hoofdstukken kloppen', 'Eindscherm en kaart ingesteld', 'Playlist gekozen', 'Shorts gekoppeld', 'Vastgezette reactie geplaatst', 'Gepubliceerd of ingepland'];

function Afvink({ nr }: { nr: number }) {
  const key = `dm-upload-check-${nr}`;
  const [v, setV] = useState<string[]>(() => { try { return JSON.parse(localStorage.getItem(key) || '[]'); } catch { return []; } });
  const zet = (c: string) => { const n = v.includes(c) ? v.filter((x) => x !== c) : [...v, c]; setV(n); try { localStorage.setItem(key, JSON.stringify(n)); } catch { /* */ } };
  return (
    <div className="panel p-4">
      <div className="mb-2 flex items-baseline justify-between"><span className="font-semibold text-white">Afvinklijst</span><span className="text-[13px] text-slate-400">{v.length}/{CHECK.length}</span></div>
      <div className="mb-3 h-1.5 overflow-hidden rounded-full bg-white/10"><div className="h-full rounded-full bg-emerald-400" style={{ width: `${(v.length / CHECK.length) * 100}%` }} /></div>
      <ul className="space-y-1">{CHECK.map((c) => (
        <li key={c}><label className="flex cursor-pointer items-center gap-2 rounded-lg px-1.5 py-1 text-[14px] hover:bg-white/5">
          <input type="checkbox" checked={v.includes(c)} onChange={() => zet(c)} className="h-4 w-4 accent-emerald-400" /><span className={v.includes(c) ? 'text-slate-500 line-through' : 'text-slate-200'}>{c}</span>
        </label></li>
      ))}</ul>
      <p className="mt-3 text-[12px] text-slate-500">Uploaden doe je zelf in YouTube Studio; deze lijst blijft in deze browser bewaard.</p>
    </div>
  );
}

function Thumb({ pad }: { pad: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [fout, setFout] = useState(false);
  useEffect(() => {
    let u: string | null = null; let weg = false; setUrl(null); setFout(false);
    laadBeeld(pad, pad.endsWith('png') ? 'image/png' : 'image/jpeg').then((x) => { if (weg) URL.revokeObjectURL(x); else { u = x; setUrl(x); } }).catch(() => setFout(true));
    return () => { weg = true; if (u) URL.revokeObjectURL(u); };
  }, [pad]);
  return (
    <button className="block w-full overflow-hidden rounded-2xl border border-white/10 bg-black/30" onClick={() => openBestand(pad)} title="Groot bekijken of downloaden">
      {url ? <img src={url} alt="Thumbnail" className="aspect-video w-full object-cover" /> : <div className="flex aspect-video items-center justify-center text-[13px] text-slate-500">{fout ? 'Thumbnail niet te laden' : 'Laden…'}</div>}
      <div className="truncate px-2 py-1 text-left text-[12px] text-slate-400">{pad.split('/').pop()}</div>
    </button>
  );
}

export default function Uploaddag() {
  const [nr, setNr] = useState(() => { try { return Number(localStorage.getItem('dm-uploaddag') || 3); } catch { return 3; } });
  const v = VIDEOS.find((x) => x.nr === nr) ?? VIDEOS[2];
  const [st, setSt] = useState<{ fase: 'laden' | 'ok' | 'leeg' | 'geen'; p?: Pakket }>({ fase: 'laden' });
  const [n, setN] = useState(0);
  useEffect(() => {
    let weg = false; setSt({ fase: 'laden' });
    try { localStorage.setItem('dm-uploaddag', String(nr)); } catch { /* */ }
    void leesBestand(`${v.map}/youtube_upload.md`).then((r) => {
      if (weg) return;
      if (r.kind === 'tekst') setSt({ fase: 'ok', p: leesPakket(r.tekst, v.map) });
      else setSt({ fase: r.kind === 'geen-toegang' ? 'geen' : 'leeg' });
    });
    return () => { weg = true; };
  }, [nr, n, v.map]);
  const p = st.p;
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-1.5">
        {VIDEOS.map((x) => <button key={x.nr} onClick={() => setNr(x.nr)} className={`rounded-full px-3 py-1.5 text-[13px] font-semibold ${x.nr === nr ? 'bg-orange-500/25 text-white' : 'bg-white/5 text-slate-400 hover:text-white'}`}>{x.naam}</button>)}
        <button className="btn-ghost ml-auto !py-1 text-[12px]" onClick={() => setN((k) => k + 1)}><RefreshCw size={12} />Opnieuw lezen</button>
      </div>
      {st.fase === 'laden' && <div className="panel p-6 text-center text-[14px] text-slate-400">Uploadpakket laden…</div>}
      {st.fase === 'geen' && <div className="panel p-6 text-center text-[14px] text-slate-400">Deze pagina kan de projectbestanden hier niet lezen. Open het HQ in claude.ai.</div>}
      {st.fase === 'leeg' && (
        <div className="panel p-6 text-center">
          <div className="text-[15px] text-slate-200">Voor {v.naam} is er nog geen uploadpakket.</div>
          <button className="btn-primary mt-3 text-[14px]" onClick={() => window.dispatchEvent(new CustomEvent('dm-opdracht', { detail: { text: `Zet het uploadpakket voor video ${v.nr} klaar in ${v.map}/youtube_upload.md: titel, beschrijving, tags, hoofdstukken, vastgezette reactie en thumbnail.` } }))}>Uploadpakket laten maken</button>
        </div>
      )}
      {st.fase === 'ok' && p && (
        <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
          <div className="space-y-3">
            <Veld naam="Titel" waarde={p.titel} />
            <Veld naam="Beschrijving" waarde={p.beschrijving} rijen={10} />
            <Veld naam="Tags (komma-lijst voor Studio)" waarde={p.tags} mono />
            <Veld naam="Hoofdstukken" waarde={p.hoofdstukken} rijen={6} />
            <Veld naam="Vastgezette reactie" waarde={p.reactie} />
            {p.instellingen && <div className="rounded-2xl bg-white/[.03] p-3"><div className="mb-1 text-[12px] font-bold uppercase tracking-wider text-slate-400">Instellingen in Studio</div><div className="whitespace-pre-wrap text-[13px] text-slate-300">{p.instellingen.replace(/`/g, '')}</div></div>}
          </div>
          <div className="space-y-3">
            {p.thumb && <Thumb pad={p.thumb} />}
            <div className="rounded-2xl bg-white/[.04] p-3 text-[13px]">
              <div className="mb-1 text-[12px] font-bold uppercase tracking-wider text-slate-400">Videobestand</div>
              <div className="break-all text-slate-200">{v.bestand ?? 'Komt na de eindmontage op je pc (map WHAT IF).'}</div>
            </div>
            <button className="btn-ghost w-full text-[13px]" onClick={() => openBestand(`${v.map}/youtube_upload.md`)}><FileText size={13} />Heel uploaddocument openen</button>
            <Afvink nr={v.nr} />
          </div>
        </div>
      )}
    </div>
  );
}
