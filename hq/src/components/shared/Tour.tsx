/**
 * Uitleg per pagina (verbeterlijst punt 25): het ?-knopje (of de toets ?) laat in twee zinnen zien wat je
 * op deze pagina kunt doen, plus de sneltoetsen (punt 24). Geen lange rondleiding meer.
 */
import { useEffect, useState } from 'react';
import { useGame } from '../../store/useGame';
import type { PageId } from '../../types';

const UITLEG: Partial<Record<PageId, [string, string]>> = {
  overzicht: ['Vandaag', 'Bovenaan staat wat op jou wacht, daaronder wat Claude nu doet en wat net klaar is. Onder "Alle taken" vind je elke thread per video.'],
  videos: ["Video's", "Elke video en short zoals hij op YouTube staat, met cijfers, plus de productielijn van idee tot upload. Ook cast, sets en ideeën voor nieuwe video's staan hier."],
  kanaal: ['Kanaal', 'Je echte kanaalcijfers: abonnees, weergaven, kijkduur en groei per dag. Alles komt uit vidIQ en de YouTube-feed en wordt elk uur bijgewerkt.'],
  kennis: ['Kennis', 'Alles wat is opgeslagen: het projectgeheugen met je regels, elke thread met het hele gesprek, documenten, werkwijze en gereedschap. Zoek bovenaan door alles heen.'],
  driftmark: ['3D-kantoor', 'Je kantoor met een kamer per afdeling. Klik op een kamer of een teamlid om te zien waar het aan werkt, of loop rond met de knop Rondlopen.'],
  coach: ['Coachkamer', 'Je coach met briefing, doelen, beslissingen en rapporten. Stel hem een vraag over je kanaal; hij kent de echte stand.'],
  hq: ['Team', 'Je team en projecten in het kantoor. Knoppen als Nieuwe video en Goedkeuren worden echte opdrachten voor Claude.'],
  projects: ['Projecten', "Elke echte video als project met zijn stappen. Klik op een project voor de details."],
  agents: ['Teamleden', 'Elke lopende of afgeronde taak als teamlid. Klik op iemand om het gesprek te openen.'],
  warroom: ['Crisiskamer', 'Hier komt alleen iets te staan als er echt iets mis is, met wat er gebeurde en wat jij moet doen.'],
  settings: ['Instellingen', 'Geluid, beeldkwaliteit en meldingen. Alles wordt alleen in deze browser bewaard.'],
};

export const SNELTOETSEN: [string, string][] = [
  ['1 t/m 5', 'Vandaag, Video\'s, Kanaal, Kennis, 3D-kantoor'],
  ['K', 'Opdrachtbalk openen'],
  ['Esc', 'Sluiten / terug naar Vandaag'],
  ['?', 'Deze uitleg'],
];

export default function Tour() {
  const page = useGame((s) => s.page);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const h = () => setOpen((o) => !o);
    window.addEventListener('dm-tour', h);
    return () => window.removeEventListener('dm-tour', h);
  }, []);
  useEffect(() => { try { localStorage.setItem('dm-tour', 'gezien'); } catch { /* */ } }, []);
  if (!open) return null;
  const [t, uitleg] = UITLEG[page] ?? ['Driftmark HQ', 'Je digitale kantoor: alles over je kanaal en je video\'s op één plek.'];
  return (
    <div className="fixed inset-0 z-[80] flex items-end justify-center bg-black/45 p-4 backdrop-blur-sm md:items-center" role="dialog" aria-modal="true" aria-label={`Uitleg: ${t}`} onClick={() => setOpen(false)}>
      <div className="dm-pop w-full max-w-md rounded-3xl border border-orange-400/40 bg-[#0f1630] p-5 shadow-2xl" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center gap-3">
          <img src="./img/c1_hoofdpersonage.jpg" alt="" className="h-12 w-12 rounded-full object-cover ring-2 ring-orange-400" />
          <div><div className="text-[13px] font-semibold text-slate-400">Uitleg bij deze pagina</div><div className="font-display text-[22px] font-bold text-white">{t}</div></div>
        </div>
        <p className="mt-3 text-[15px] leading-relaxed text-slate-200">{uitleg}</p>
        <div className="mt-4 rounded-2xl bg-white/[.04] p-3">
          <div className="mb-1.5 text-[12px] font-bold uppercase tracking-wider text-slate-400">Sneltoetsen</div>
          <div className="grid gap-1">{SNELTOETSEN.map(([k, w]) => <div key={k} className="flex items-center gap-3 text-[13px]"><kbd className="min-w-[64px] rounded-md bg-white/10 px-2 py-0.5 text-center font-mono text-[12px] text-white">{k}</kbd><span className="text-slate-300">{w}</span></div>)}</div>
        </div>
        <div className="mt-4 flex justify-end"><button className="btn-primary text-[14px]" onClick={() => setOpen(false)}>Duidelijk</button></div>
      </div>
    </div>
  );
}
