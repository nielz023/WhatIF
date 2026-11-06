import { ShieldAlert, ShieldCheck } from 'lucide-react';
import { PageHeader } from '../components/ui';
import { useLive } from '../services/live';
import { useDb } from '../services/db';
import { alarmsFrom } from '../world/alarms';

/** Wat de crisiskamer bekijkt (zie world/alarms.ts). */
const CHECKS = [
  'Taken die mislukt zijn',
  'Taken die al meer dan 24 uur op jou wachten',
  'Een renderstatus die lang niet is bijgewerkt',
  'Een schijf die bijna vol is',
  'Fouten in de automatische ronde van de laatste 24 uur',
];

/**
 * Crisiskamer: alleen echte alarmen uit de stand van je project.
 * Geen verzonnen analyses of plannen meer (niels 2026-11-06).
 */
export default function WarRoomPage() {
  const live = useLive((x) => x.data);
  useDb((x) => x.log); // opnieuw tekenen als het logboek verandert
  const alarms = alarmsFrom(live);
  const rood = alarms.filter((a) => a.level === 'rood');
  const oranje = alarms.filter((a) => a.level === 'oranje');
  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28" style={{ background: 'radial-gradient(900px 500px at 50% 0%, rgba(239,68,68,.10), transparent)' }}>
      <PageHeader title="Crisiskamer" subtitle="Hier zie je wat er echt mis is in je project. Rood is vastgelopen of mislukt, oranje is let op." />
      {alarms.length === 0 ? (
        <div className="panel flex items-center gap-3 border-emerald-500/30 p-5">
          <ShieldCheck size={28} className="shrink-0 text-emerald-300" />
          <div>
            <div className="font-semibold text-white">Alles in orde</div>
            <div className="text-sm text-slate-400">Er is nu niets mislukt of vastgelopen.</div>
          </div>
        </div>
      ) : (
        <div className="space-y-2">
          {[...rood, ...oranje].map((a) => (
            <div key={a.key} className={`panel flex items-start gap-3 p-4 ${a.level === 'rood' ? 'border-rose-500/50' : 'border-amber-500/40'}`}>
              <ShieldAlert size={20} className={`mt-0.5 shrink-0 ${a.level === 'rood' ? 'text-rose-300' : 'text-amber-300'}`} />
              <div className="min-w-0">
                <div className={`text-[12px] font-bold uppercase tracking-wider ${a.level === 'rood' ? 'text-rose-300' : 'text-amber-300'}`}>{a.level === 'rood' ? 'Rood' : 'Oranje'}</div>
                <div className="text-sm text-white">{a.text}</div>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="panel mt-4 p-4">
        <div className="mb-2 text-sm font-semibold text-white">Waar de crisiskamer op let</div>
        <ul className="list-disc space-y-1 pl-5 text-[13px] text-slate-400">{CHECKS.map((c) => <li key={c}>{c}</li>)}</ul>
      </div>
    </div>
  );
}
