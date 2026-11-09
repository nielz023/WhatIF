/**
 * BESTANDEN OPENEN IN HET HQ (verbeterlijst punt 7).
 * Eén lezer voor elk projectbestand: tekst en Markdown (scripts, uploadteksten), beelden (thumbnails, renders),
 * geluid (voice-overclips) en korte video's. Openen kan overal met openBestand(pad).
 */
import { useEffect, useState } from 'react';
import { create } from 'zustand';
import { X, Download, FileText, RefreshCw } from 'lucide-react';
import { leesBestand, laadMedia, mediaType, downloadBestand, type BestandLees } from '../../services/kennis';
import { Md } from './Md';
import { useGame } from '../../store/useGame';

interface V { pad: string | null }
export const useBestand = create<V>(() => ({ pad: null }));
export const openBestand = (pad: string) => useBestand.setState({ pad: pad.replace(/^\/?mnt\/project-files\//, '').replace(/^\/+/, '') });

const naam = (p: string) => p.split('/').pop() ?? p;

function Media({ pad }: { pad: string }) {
  const [url, setUrl] = useState<string | null>(null);
  const [fout, setFout] = useState<string | null>(null);
  useEffect(() => {
    let u: string | null = null; let weg = false;
    setUrl(null); setFout(null);
    void laadMedia(pad).then((r) => { if (weg) { if ('url' in r) URL.revokeObjectURL(r.url); return; } if ('url' in r) { u = r.url; setUrl(r.url); } else setFout(r.fout); });
    return () => { weg = true; if (u) URL.revokeObjectURL(u); };
  }, [pad]);
  const t = mediaType(pad);
  if (fout) return <Melding>{fout === 'te-groot' ? 'Dit bestand is te groot om hier af te spelen. Download het.' : fout === 'not_found' || fout === 'ontbreekt' ? 'Dit bestand is er niet (meer).' : fout === 'geen-files' || fout === 'not_granted' ? 'Deze pagina kan de projectbestanden hier niet lezen. Open het HQ in claude.ai.' : 'Het bestand kon nu niet geladen worden.'}</Melding>;
  if (!url) return <Melding><RefreshCw size={16} className="mx-auto mb-2 animate-spin" />Laden…</Melding>;
  if (t.startsWith('audio')) return <div className="p-6"><audio controls autoPlay src={url} className="w-full" /></div>;
  if (t.startsWith('video')) return <video controls src={url} className="max-h-[75vh] w-full bg-black" />;
  return <img src={url} alt={naam(pad)} className="mx-auto max-h-[78vh] w-auto max-w-full object-contain" />;
}

function Tekst({ pad }: { pad: string }) {
  const [r, setR] = useState<BestandLees | null>(null);
  useEffect(() => { setR(null); void leesBestand(pad).then(setR); }, [pad]);
  if (!r) return <Melding><RefreshCw size={16} className="mx-auto mb-2 animate-spin" />Laden…</Melding>;
  if (r.kind === 'tekst') return /\.(md|markdown|txt)$/i.test(pad) || !/\.(json|py|tsv|csv)$/i.test(pad)
    ? <div className="p-5"><Md text={r.tekst} /></div>
    : <pre className="whitespace-pre-wrap p-5 font-mono text-[12px] text-slate-300">{r.tekst}</pre>;
  if (r.kind === 'beeld') return <Media pad={pad} />;
  if (r.kind === 'pdf') return <Melding><FileText size={20} className="mx-auto mb-2" />Een PDF kan hier niet getoond worden. Download hem om te lezen.</Melding>;
  if (r.kind === 'ontbreekt') return <Melding>Dit bestand is er niet (meer).</Melding>;
  if (r.kind === 'geen-toegang') return <Melding>Deze pagina kan de projectbestanden hier niet lezen. Open het HQ in claude.ai.</Melding>;
  return <Melding>Dit bestand kan hier niet getoond worden.</Melding>;
}

function Melding({ children }: { children: React.ReactNode }) {
  return <div className="px-6 py-16 text-center text-[14px] text-slate-400">{children}</div>;
}

export default function BestandViewer() {
  const pad = useBestand((s) => s.pad);
  const toast = useGame((s) => s.toast);
  useEffect(() => {
    if (!pad) return;
    const k = (e: KeyboardEvent) => { if (e.key === 'Escape') { e.stopPropagation(); useBestand.setState({ pad: null }); } };
    window.addEventListener('keydown', k, true); return () => window.removeEventListener('keydown', k, true);
  }, [pad]);
  if (!pad) return null;
  const media = !!mediaType(pad);
  const dl = async () => { const m = await downloadBestand(pad); if (m) toast(m, 'info'); };
  return (
    <div className="fixed inset-0 z-[85] flex items-center justify-center bg-black/60 p-2 backdrop-blur-sm md:p-6" role="dialog" aria-modal="true" aria-label={`Bestand: ${naam(pad)}`} onClick={() => useBestand.setState({ pad: null })}>
      <div className="dm-pop flex max-h-full w-full max-w-4xl flex-col overflow-hidden rounded-3xl border border-white/10 bg-[#0a1024] shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <header className="flex items-center gap-3 border-b border-white/10 px-4 py-3">
          <FileText size={18} className="shrink-0 text-orange-300" />
          <div className="min-w-0 flex-1"><div className="truncate font-display text-[17px] font-bold text-white">{naam(pad)}</div><div className="truncate text-[12px] text-slate-500">{pad}</div></div>
          <button className="btn-ghost !px-2 !py-1 text-[12px]" onClick={() => void dl()}><Download size={13} />Downloaden</button>
          <button onClick={() => useBestand.setState({ pad: null })} className="rounded-lg border border-white/10 p-1.5 text-slate-300 hover:text-white" aria-label="Sluiten"><X size={16} /></button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto">{media ? <Media pad={pad} /> : <Tekst pad={pad} />}</div>
      </div>
    </div>
  );
}
