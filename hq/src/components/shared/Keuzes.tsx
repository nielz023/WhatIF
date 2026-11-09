/**
 * KIEZEN EN GOEDKEUREN MET KNOPPEN (verbeterlijst punt 5).
 * Bij elke taak die op niels wacht: de keuzes als knoppen (met een plaatje of geluid erbij als dat er is),
 * of Goedkeuren / Afkeuren, plus "Antwoord typen" dat de opdrachtbalk opent met de thread al gekozen.
 * Eén klik wordt een echte opdracht naar die thread.
 */
import { useState } from 'react';
import { Check, Play, Image as ImageIcon, PenLine } from 'lucide-react';
import type { Activity } from '../../services/live';
import { order, openOpdracht } from '../../services/real';
import { useGame } from '../../store/useGame';
import { AfkeurKnop } from './Afkeuren';
import { openBestand } from './BestandViewer';
import { mediaType } from '../../services/kennis';

const keuzeLijst = (a: Activity) => (a.keuzes ?? []).map((k) => (typeof k === 'string' ? { label: k } : k)).filter((k) => k && typeof k.label === 'string');

export default function Keuzes({ a, klein }: { a: Activity; klein?: boolean }) {
  const toast = useGame((s) => s.toast);
  const [gekozen, setGekozen] = useState<string | null>(null);
  if (a.state !== 'blocked' && a.state !== 'review_ready') return null;
  const ks = keuzeLijst(a);
  const tid = a.id || undefined;
  const maat = klein ? '!py-1 text-[12px]' : 'text-[13px]';
  const kies = (label: string) => {
    setGekozen(label);
    order(`Keuze van niels voor "${a.title}": ${label}`, toast, { thread: tid, doel: 'Algemeen' });
  };
  if (gekozen) return <div className="mt-2 flex items-center gap-1.5 text-[13px] text-emerald-300"><Check size={14} />Doorgegeven: {gekozen}</div>;
  return (
    <div className="mt-2 flex flex-wrap items-center gap-1.5" onClick={(e) => e.stopPropagation()}>
      {ks.length ? ks.map((k) => {
        const t = k.bestand ? mediaType(k.bestand) : '';
        return (
          <span key={k.label} className="inline-flex items-stretch overflow-hidden rounded-xl border border-orange-400/40">
            <button className={`btn bg-orange-500/15 text-orange-100 hover:bg-orange-500/30 ${maat} !rounded-none`} onClick={() => kies(k.label)}>{k.label}</button>
            {k.bestand && <button className="border-l border-orange-400/30 bg-black/20 px-2 text-orange-200 hover:text-white" title={t.startsWith('audio') ? 'Beluisteren' : 'Bekijken'} aria-label={`${k.label}: ${t.startsWith('audio') ? 'beluisteren' : 'bekijken'}`} onClick={() => openBestand(k.bestand!)}>{t.startsWith('audio') ? <Play size={12} /> : <ImageIcon size={12} />}</button>}
          </span>
        );
      }) : a.state === 'review_ready' ? (<>
        <button className={`btn-success ${maat}`} onClick={() => kies('Goedgekeurd, ga door.')}>Goedkeuren</button>
        <AfkeurKnop title={a.title} id={tid} className={maat} />
      </>) : null}
      <button className={`btn-ghost ${maat}`} onClick={() => openOpdracht({ thread: tid, titel: `Antwoord voor: ${a.title}${a.needs ? ` (${a.needs})` : ''}` })}><PenLine size={12} />Antwoord typen</button>
    </div>
  );
}
