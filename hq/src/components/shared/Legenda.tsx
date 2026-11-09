import { KLEUR, UITLEG, type Soort } from '../../lib/status';

/** Kleine legenda van de statuskleuren (verbeterlijst punt 21). */
export default function Legenda({ className = '' }: { className?: string }) {
  return (
    <div className={`flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-slate-400 ${className}`} aria-label="Wat de kleuren betekenen">
      {(Object.keys(KLEUR) as Soort[]).map((k) => (
        <span key={k} className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-full" style={{ background: KLEUR[k], boxShadow: `0 0 6px ${KLEUR[k]}` }} />{UITLEG[k]}</span>
      ))}
    </div>
  );
}
