/**
 * WEEKRAPPORT ALS NETTE PAGINA (verbeterlijst punt 44). Leest de rapporten uit de database (collectie rapport,
 * gemaakt door de coach) en toont ze als een leesbare pagina. Oude rapporten blijven in de lijst.
 */
import { useEffect, useState } from 'react';
import { FileText, RefreshCw } from 'lucide-react';
import { useCoach, startCoach, maakRapport, type Rapport } from '../../services/coach';
import { useLive } from '../../services/live';
import { useDb } from '../../services/db';
import { openOpdracht } from '../../services/real';
import { useGame } from '../../store/useGame';
import { Md } from '../../components/shared/Md';
import { kortTijd } from '../../services/studio';

const SOORT: Record<Rapport['soort'], string> = { week: 'Weekrapport', maand: 'Maandrapport', advies: 'Strategisch advies' };

export default function Weekrapport() {
  useEffect(() => { void startCoach(); }, []);
  const rapporten = useCoach((s) => s.rapporten);
  const kan = useCoach((s) => s.kanVragen);
  const klaar = useCoach((s) => s.klaar);
  const data = useLive((s) => s.data); const stats = useDb((s) => s.stats);
  const toast = useGame((s) => s.toast);
  const lijst = [...rapporten].filter((r) => r && typeof r.tekst === 'string').sort((a, b) => (b.at ?? '').localeCompare(a.at ?? ''));
  const [kies, setKies] = useState<string | null>(null);
  const [bezig, setBezig] = useState(false);
  const r = lijst.find((x) => x.id === kies) ?? lijst.find((x) => x.soort === 'week') ?? lijst[0];
  const nieuw = async () => {
    if (!kan) { openOpdracht({ text: 'Maak het weekrapport: wat ging goed, wat niet, de vergelijking met vorige week en drie acties voor deze week. Bewaar het in de database onder rapport/.' }); return; }
    setBezig(true); const x = await maakRapport('week', data, stats); setBezig(false);
    if (typeof x === 'string') toast(x, 'warning'); else { setKies(x.id); toast('📊 Weekrapport klaar', 'success'); }
  };
  return (
    <section className="panel mb-4 p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <span className="flex items-center gap-2 font-display text-[18px] font-bold text-white"><FileText size={17} className="text-violet-300" />Weekrapport</span>
        <button className="btn-ghost !py-1 text-[13px]" onClick={() => void nieuw()} disabled={bezig}>{bezig ? <><RefreshCw size={13} className="animate-spin" />Bezig…</> : 'Nieuw weekrapport maken'}</button>
      </div>
      {!lijst.length ? (
        <p className="text-[14px] text-slate-400">{!klaar ? 'Rapporten laden…' : 'Er staat nog geen rapport in de database. Maak er een met de knop hierboven; daarna staan ze hier allemaal, ook de oude.'}</p>
      ) : (
        <div className="grid gap-3 lg:grid-cols-[220px_1fr]">
          <ul className="flex gap-1.5 overflow-x-auto lg:block lg:space-y-1 lg:overflow-visible">
            {lijst.map((x) => (
              <li key={x.id} className="shrink-0">
                <button onClick={() => setKies(x.id)} className={`w-full rounded-lg px-2.5 py-1.5 text-left text-[13px] ${x.id === r?.id ? 'bg-violet-500/20 text-white' : 'bg-white/[.03] text-slate-300 hover:bg-white/[.07]'}`}>
                  <div className="font-semibold">{SOORT[x.soort] ?? 'Rapport'}</div>
                  <div className="text-[12px] text-slate-500">{kortTijd(x.at) ?? 'datum onbekend'}</div>
                </button>
              </li>
            ))}
          </ul>
          {r && (
            <article className="min-w-0 rounded-2xl bg-white/[.03] p-4">
              <div className="mb-2 text-[12px] text-slate-500">{SOORT[r.soort] ?? 'Rapport'} · gemaakt door de coach op {kortTijd(r.at) ?? 'onbekende datum'} · bron: de cijfers van dat moment</div>
              <Md text={r.tekst} />
            </article>
          )}
        </div>
      )}
    </section>
  );
}
