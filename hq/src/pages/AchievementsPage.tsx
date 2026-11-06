import { useGame } from '../store/useGame';
import { PageHeader, Progress } from '../components/ui';
import { ACHIEVEMENTS, missionTitle } from '../modules/gameplay/progression';
import { fmtTick } from '../lib/util';

/** Prestaties en missies, zonder punten, niveaus of geld: het kantoor is geen spel (niels 2026-11-06). */
export default function AchievementsPage() {
  const s = useGame();
  // alleen de prestaties die nog bestaan; de tekst komt uit de lijst, de datum uit de bewaarde stand
  const list = ACHIEVEMENTS.map((def) => ({ ...def, unlockedTick: s.achievements.find((a) => a.id === def.id)?.unlockedTick }));
  const unlocked = list.filter((a) => a.unlockedTick).length;
  const missions = s.missions.filter((m) => m.metric !== 'train' && m.metric !== 'hire');
  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Prestaties en missies" subtitle={`${unlocked} van ${list.length} prestaties gehaald`} />
      <div className="grid gap-4 lg:grid-cols-[1fr_1.4fr]">
        <div className="panel content-start p-5">
          <div className="mb-3 font-semibold text-white">Missies</div>
          <div className="space-y-3">
            {missions.length === 0 && <div className="text-sm text-slate-500">Geen missies op dit moment.</div>}
            {missions.map((m) => {
              const done = m.progress >= m.target;
              return (
                <div key={m.id} className={`rounded-xl border p-3 ${m.claimed ? 'border-emerald-500/30 opacity-60' : done ? 'border-amber-400/50 bg-amber-500/5' : 'border-hq-line'}`}>
                  <div className="text-sm text-white">{missionTitle(m)}</div>
                  <div className="mt-2 flex items-center gap-3">
                    <div className="flex-1"><Progress value={(m.progress / m.target) * 100} h={5} color={done ? '#f59e0b' : '#6366f1'} /></div>
                    <span className="text-[13px] text-slate-400">{m.progress} van {m.target}</span>
                    <button className="btn-success !px-2.5 !py-1 text-[13px]" disabled={!done || m.claimed} onClick={() => { s.claimMission(m.id); s.toast('Missie afgevinkt.', 'success'); }}>{m.claimed ? 'Afgevinkt' : 'Afvinken'}</button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
        <div className="grid content-start gap-3 sm:grid-cols-2">
          {list.map((a) => (
            <div key={a.id} className={`panel flex items-center gap-3 p-4 ${a.unlockedTick ? 'border-amber-400/40 shadow-[0_0_24px_rgba(245,158,11,.12)]' : 'opacity-60'}`}>
              <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-2xl ${a.unlockedTick ? 'bg-gradient-to-br from-amber-400/40 to-orange-600/30' : 'bg-slate-800 grayscale'}`}>{a.icon}</div>
              <div className="min-w-0">
                <div className="font-semibold text-white">{a.title}</div>
                <div className="text-[13px] text-slate-400">{a.description}</div>
                <div className="mt-0.5 text-[13px] text-slate-500">{a.unlockedTick ? `Gehaald ${fmtTick(a.unlockedTick)}` : 'Nog niet gehaald'}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
