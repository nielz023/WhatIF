import { motion } from 'framer-motion';
import { X } from 'lucide-react';
import type { ReactNode } from 'react';
import { reducedMotion } from './useWorld';

export const EASE = [0.22, 1, 0.36, 1] as const;

/** Zwevend holografisch glaspaneel boven het kantoor. */
export function HoloPanel({ title, sub, accent = '#FF7A24', onClose, children, className = '', bare }: { title?: ReactNode; sub?: ReactNode; accent?: string; onClose?: () => void; children: ReactNode; className?: string; bare?: boolean }) {
  const rm = reducedMotion();
  return (
    <motion.section
      className={`holo-panel pointer-events-auto flex flex-col ${className}`}
      style={{ ['--accent' as string]: accent }}
      initial={rm ? { opacity: 0 } : { opacity: 0, y: 28, scale: 0.965, rotateX: 5 }}
      animate={{ opacity: 1, y: 0, scale: 1, rotateX: 0 }}
      exit={rm ? { opacity: 0 } : { opacity: 0, y: 16, scale: 0.98 }}
      transition={{ duration: rm ? 0.15 : 0.75, ease: EASE }}
    >
      <span className="holo-scan" aria-hidden />
      {bare && onClose && (
        <button onClick={onClose} className="absolute right-3 top-3 z-20 rounded-lg border border-white/10 bg-[#0a1124]/80 p-1.5 text-slate-300 backdrop-blur transition hover:border-white/25 hover:text-white" aria-label="Sluiten" title="Terug naar het kantoor (Esc)"><X size={16} /></button>
      )}
      {!bare && (title || onClose) && (
        <header className="flex shrink-0 items-center gap-3 border-b border-white/[.07] px-5 py-3">
          <span className="h-2 w-2 rounded-full" style={{ background: accent, boxShadow: `0 0 10px ${accent}` }} />
          <div className="min-w-0 flex-1">
            <div className="truncate font-display text-[17px] font-bold tracking-wide text-white">{title}</div>
            {sub && <div className="truncate text-[12px] text-slate-400">{sub}</div>}
          </div>
          {onClose && (
            <button onClick={onClose} className="rounded-lg border border-white/10 bg-white/[.04] p-1.5 text-slate-300 transition hover:border-white/25 hover:text-white" aria-label="Sluiten" title="Terug naar het kantoor (Esc)">
              <X size={16} />
            </button>
          )}
        </header>
      )}
      <div className="holo-body min-h-0 flex-1 overflow-y-auto">{children}</div>
    </motion.section>
  );
}
