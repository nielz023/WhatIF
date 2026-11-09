import { bronTijd, kortTijd } from '../../services/studio';

/**
 * Bron en datum bij een cijfer (verbeterlijst punt 40): "vidIQ, 9 nov 17:00" of "YouTube-feed, 5 min geleden".
 * schatting = het getal is berekend of geschat, niet gemeten. Zonder tijd staat er "datum onbekend".
 */
export default function Bron({ bron, at, schatting, relatief, className = '' }: { bron: string; at?: string | number | null; schatting?: boolean; relatief?: boolean; className?: string }) {
  const t = relatief ? bronTijd(at) : kortTijd(at);
  return (
    <span className={`text-[11px] text-slate-500 ${className}`}>
      {bron}, {t ?? 'datum onbekend'}
      {schatting && <span className="ml-1 rounded bg-amber-400/15 px-1 font-semibold text-amber-200">schatting</span>}
    </span>
  );
}
