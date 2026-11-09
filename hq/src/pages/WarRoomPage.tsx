import { MessageSquare, Send, ShieldAlert, ShieldCheck } from 'lucide-react';
import { PageHeader } from '../components/ui';
import { useLive } from '../services/live';
import { useDb } from '../services/db';
import { order } from '../services/real';
import { useGame } from '../store/useGame';
import { KLEUR } from '../lib/status';
import { alarmsFrom, type Alarm } from '../world/alarms';
import { openGesprek } from '../components/shared/Gesprek';

/** Wat de crisiskamer bekijkt (zie world/alarms.ts). */
const CHECKS = [
  'Taken die mislukt zijn',
  'Taken die al meer dan 24 uur op jou wachten',
  'Een render die lang niet is bijgewerkt (vastgelopen)',
  'Een schijf die bijna vol is',
  'Fouten in de automatische ronde van de laatste 24 uur',
];

function Probleem({ a }: { a: Alarm }) {
  const toast = useGame((s) => s.toast);
  const c = a.level === 'rood' ? KLEUR.probleem : KLEUR.wacht;
  const rij = (kop: string, tekst: string | undefined, kleur: string) => (
    <div className="grid gap-0.5 sm:grid-cols-[150px_1fr] sm:gap-3">
      <div className="text-[12px] font-bold uppercase tracking-wider" style={{ color: kleur }}>{kop}</div>
      <div className="text-[14px] text-slate-200">{tekst ?? <span className="text-slate-500">Niet bekend.</span>}</div>
    </div>
  );
  return (
    <div className="panel p-4" style={{ borderColor: `${c}80` }}>
      <div className="mb-2 flex items-start gap-2">
        <ShieldAlert size={20} className="mt-0.5 shrink-0" style={{ color: c }} />
        <div className="min-w-0 flex-1 font-semibold text-white">{a.text}</div>
        <span className="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-bold" style={{ color: c, background: `${c}22` }}>{a.level === 'rood' ? 'probleem' : 'let op'}</span>
      </div>
      <div className="space-y-2">
        {rij('Wat ging mis', a.mis ?? a.text, KLEUR.probleem)}
        {rij('Wat Claude deed', a.gedaan, KLEUR.bezig)}
        {rij('Wat jij moet doen', a.jij, KLEUR.wacht)}
      </div>
      {(a.thread || a.opdracht) && (
        <div className="mt-3 flex flex-wrap gap-2">
          {a.thread && <button className="btn-ghost text-[13px]" onClick={() => openGesprek({ kind: 'thread', title: a.text, thread: a.thread })}><MessageSquare size={14} />Gesprek lezen</button>}
          {a.opdracht && <button className="btn-primary text-[13px]" onClick={() => order(a.opdracht!, toast, { doel: 'Crisiskamer', thread: a.thread })}><Send size={14} />Laat Claude het oplossen</button>}
        </div>
      )}
    </div>
  );
}

/**
 * Crisiskamer (verbeterlijst punt 60): alleen echte problemen uit de stand van je project, per probleem wat er
 * misging, wat Claude deed en wat jij moet doen. Staat alleen in het menu als er echt iets mis is.
 */
export default function WarRoomPage() {
  const live = useLive((x) => x.data);
  useDb((x) => x.log); // opnieuw tekenen als het logboek verandert
  const alarms = alarmsFrom(live);
  const rood = alarms.filter((a) => a.level === 'rood');
  const oranje = alarms.filter((a) => a.level === 'oranje');
  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28" style={{ background: 'radial-gradient(900px 500px at 50% 0%, rgba(239,68,68,.10), transparent)' }}>
      <PageHeader title="Crisiskamer" subtitle="Alleen als er echt iets mis is: per probleem wat er misging, wat Claude deed en wat jij moet doen." />
      {alarms.length === 0 ? (
        <div className="panel flex items-center gap-3 p-5" style={{ borderColor: `${KLEUR.klaar}55` }}>
          <ShieldCheck size={28} className="shrink-0" style={{ color: KLEUR.klaar }} />
          <div>
            <div className="font-semibold text-white">Alles in orde</div>
            <div className="text-sm text-slate-400">Er is nu niets mislukt of vastgelopen. Daarom staat de crisiskamer niet in het menu.</div>
          </div>
        </div>
      ) : (
        <div className="space-y-3">{[...rood, ...oranje].map((a) => <Probleem key={a.key} a={a} />)}</div>
      )}
      <div className="panel mt-4 p-4">
        <div className="mb-2 text-sm font-semibold text-white">Waar de crisiskamer op let</div>
        <ul className="list-disc space-y-1 pl-5 text-[13px] text-slate-400">{CHECKS.map((c) => <li key={c}>{c}</li>)}</ul>
      </div>
    </div>
  );
}
