import { useGame } from '../store/useGame';
import { PageHeader, Progress } from '../components/ui';
import { companyXpForLevel, rankTitle } from '../modules/gameplay/progression';
import { eur, fmtTick } from '../lib/util';

export default function AchievementsPage() {
  const s = useGame();
  const need = companyXpForLevel(s.company.level);
  const unlocked = s.achievements.filter((a) => a.unlockedTick).length;
  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Achievements & Missions" subtitle={`${unlocked}/${s.achievements.length} achievements unlocked`} />
      <div className="grid gap-4 lg:grid-cols-[1fr_1.4fr]">
        <div className="space-y-4">
          <div className="panel relative overflow-hidden p-5">
            <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-fuchsia-500/25 blur-3xl" />
            <div className="text-xs uppercase tracking-wider text-slate-400">Company level</div>
            <div className="flex items-end gap-3"><div className="font-display text-5xl font-bold text-white">{s.company.level}</div><div className="pb-1.5 text-lg text-gradient font-display font-semibold">{rankTitle(s.company.level)}</div></div>
            <div className="mt-3 text-xs text-slate-400">{Math.round(s.company.xp)} / {need} XP to level {s.company.level + 1}</div>
            <div className="mt-1"><Progress value={(s.company.xp / need) * 100} h={8} color="#a855f7" /></div>
            <div className="mt-4 text-xs text-slate-400">Company reputation</div>
            <div className="mt-1"><Progress value={s.company.reputation} h={6} color="#22d3ee" /></div>
          </div>
          <div className="panel p-5">
            <div className="mb-3 flex items-center justify-between"><div className="font-semibold text-white">Daily missions</div><div className="text-xs text-slate-500">refresh every game day</div></div>
            <div className="space-y-3">
              {s.missions.map((m) => {
                const done = m.progress >= m.target;
                return (
                  <div key={m.id} className={`rounded-xl border p-3 ${m.claimed ? 'border-emerald-500/30 opacity-60' : done ? 'border-amber-400/50 bg-amber-500/5' : 'border-hq-line'}`}>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm text-white">{m.title}</span>
                      <span className="text-xs text-slate-400">+{m.rewardXp} XP · {eur(m.rewardCash)}</span>
                    </div>
                    <div className="mt-2 flex items-center gap-3">
                      <div className="flex-1"><Progress value={(m.progress / m.target) * 100} h={5} color={done ? '#f59e0b' : '#6366f1'} /></div>
                      <span className="text-xs text-slate-400">{m.progress}/{m.target}</span>
                      <button className="btn-success !px-2.5 !py-1 text-xs" disabled={!done || m.claimed} onClick={() => { s.claimMission(m.id); s.toast(`Missie voltooid! +${m.rewardXp} XP, +${eur(m.rewardCash)}`, 'success'); }}>{m.claimed ? 'Claimed' : 'Claim'}</button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        <div className="grid content-start gap-3 sm:grid-cols-2">
          {s.achievements.map((a) => (
            <div key={a.id} className={`panel flex items-center gap-3 p-4 ${a.unlockedTick ? 'border-amber-400/40 shadow-[0_0_24px_rgba(245,158,11,.12)]' : 'opacity-60'}`}>
              <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-2xl ${a.unlockedTick ? 'bg-gradient-to-br from-amber-400/40 to-orange-600/30' : 'bg-slate-800 grayscale'}`}>{a.icon}</div>
              <div className="min-w-0">
                <div className="font-semibold text-white">{a.title}</div>
                <div className="text-xs text-slate-400">{a.description}</div>
                <div className="mt-0.5 text-[11px] text-slate-500">{a.unlockedTick ? `Unlocked ${fmtTick(a.unlockedTick)}` : `+${a.xp} XP`}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
