import { useEffect, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Sparkles, X } from 'lucide-react';
import { VERSIE, NIEUW, gezieneVersie, markeerGezien, nieuwSinds, type Nieuw } from '../../lib/versie';

/**
 * Versienummer rechtsonder en een klein venster "Wat is nieuw" (verbeterlijst punt 70).
 * Het venster komt één keer per nieuwe versie (localStorage) en blokkeert niets; via het
 * versienummer is het altijd opnieuw te openen.
 */
export default function Versie() {
  const [open, setOpen] = useState(false);
  const [lijst, setLijst] = useState<Nieuw[]>([]);
  useEffect(() => {
    const g = gezieneVersie();
    if (g === VERSIE) return;
    const n = nieuwSinds(g);
    if (!n.length) { markeerGezien(); return; }
    // even wachten, zodat het eerst rustig opent
    const t = setTimeout(() => { setLijst(n); setOpen(true); }, 2500);
    return () => clearTimeout(t);
  }, []);
  const sluit = () => { setOpen(false); markeerGezien(); };
  const toon = () => { const hier = NIEUW.filter((x) => x.versie === VERSIE); setLijst(hier.length ? hier : NIEUW.slice(0, 1)); setOpen(true); };
  return (
    <>
      <button className="dm-versie hidden md:block" onClick={() => (open ? sluit() : toon())} title="Wat is nieuw in deze versie?" aria-label={`Versie ${VERSIE}: wat is nieuw`}>
        Driftmark HQ {VERSIE}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div role="dialog" aria-label="Wat is nieuw"
            initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="panel fixed right-3 top-[76px] z-[70] w-[min(360px,calc(100vw-24px))] border-orange-400/30 p-4 shadow-neon">
            <div className="flex items-start gap-3">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-orange-500/15 text-orange-300"><Sparkles size={16} /></span>
              <div className="min-w-0 flex-1">
                <div className="kop-2 text-lg">Wat is nieuw</div>
                <div className="text-xs text-slate-400">Driftmark HQ {VERSIE}</div>
              </div>
              <button onClick={sluit} className="rounded-lg p-1 text-slate-400 hover:bg-white/5 hover:text-white" aria-label="Sluiten"><X size={16} /></button>
            </div>
            <div className="mt-3 max-h-[50vh] space-y-3 overflow-y-auto pr-1">
              {lijst.map((n) => (
                <div key={n.versie}>
                  {lijst.length > 1 && <div className="kop-3 mb-1">{n.versie}{n.datum ? ` · ${n.datum}` : ''}</div>}
                  <ul className="space-y-1.5">
                    {n.punten.map((p, i) => <li key={i} className="flex gap-2 text-sm text-slate-200"><span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-orange-400" />{p}</li>)}
                  </ul>
                </div>
              ))}
            </div>
            <div className="mt-4 flex justify-end"><button className="btn-primary btn-sm" onClick={sluit}>Begrepen</button></div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
