/** Rondleiding van 4 stapjes: de eerste keer vanzelf, daarna via de ?-knop. */
import { useEffect, useState } from 'react';
import { useGame } from '../../store/useGame';
import type { PageId } from '../../types';

const STEPS: { title: string; text: string; page: PageId; emoji: string }[] = [
  { emoji: '🏠', page: 'driftmark', title: 'Home', text: 'Hier zie je in één blik wat Claude nu doet en wat op jou wacht. Oranje = jij moet iets, blauw = Claude is bezig, groen = klaar.' },
  { emoji: '⚡', page: 'driftmark', title: 'Opdracht geven', text: 'Typ wat je wilt in het opdrachtvak, of tik op een snelle keuze. Claude voert het echt uit en zet het antwoord op Home.' },
  { emoji: '🎬', page: 'videos', title: "Video's en Kanaal", text: "Bij Video's zie je elke video op de metrolijn van idee tot online. Bij Kanaal staan je echte cijfers en grafieken." },
  { emoji: '🎮', page: 'hq', title: 'Studio en de coach', text: 'Studio is het 3D-kantoor en het spel (met speelgeld). Rechtsonder zit je coach: vraag hem alles of wacht op een tip.' },
];

export default function Tour() {
  const setPage = useGame((s) => s.setPage);
  const [i, setI] = useState<number | null>(null);
  useEffect(() => {
    let seen = true;
    try { seen = localStorage.getItem('dm-tour') === 'gezien'; } catch { /* */ }
    if (!seen) setTimeout(() => setI(0), 1200);
    const h = () => setI(0);
    window.addEventListener('dm-tour', h);
    return () => window.removeEventListener('dm-tour', h);
  }, []);
  if (i == null) return null;
  const s = STEPS[i];
  const close = () => { setI(null); try { localStorage.setItem('dm-tour', 'gezien'); } catch { /* */ } };
  const go = (n: number) => { setI(n); setPage(STEPS[n].page); };
  return (
    <div className="fixed inset-0 z-[80] flex items-end justify-center bg-black/55 p-4 backdrop-blur-sm md:items-center" role="dialog" aria-modal="true" aria-label="Rondleiding">
      <div className="dm-pop w-full max-w-md rounded-3xl border border-orange-400/40 bg-[#0f1630] p-5 shadow-2xl">
        <div className="flex items-center gap-3">
          <img src="./img/c1_hoofdpersonage.jpg" alt="" className="h-14 w-14 rounded-full object-cover ring-2 ring-orange-400" />
          <div><div className="text-[13px] font-semibold text-slate-400">Rondleiding · {i + 1} van {STEPS.length}</div><div className="font-display text-[22px] font-bold text-white">{s.emoji} {s.title}</div></div>
        </div>
        <p className="mt-3 text-[15px] leading-relaxed text-slate-200">{s.text}</p>
        <div className="mt-4 flex items-center justify-between">
          <div className="flex gap-1.5">{STEPS.map((_, n) => <span key={n} className={`h-2 rounded-full transition-all ${n === i ? 'w-6 bg-orange-400' : 'w-2 bg-white/20'}`} />)}</div>
          <div className="flex gap-2">
            <button className="btn-ghost text-[14px]" onClick={close}>Overslaan</button>
            {i < STEPS.length - 1 ? <button className="btn-primary text-[14px]" onClick={() => go(i + 1)}>Volgende</button> : <button className="btn-primary text-[14px]" onClick={() => { close(); setPage('driftmark'); }}>Klaar! 🚀</button>}
          </div>
        </div>
      </div>
    </div>
  );
}
