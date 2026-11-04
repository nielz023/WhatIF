import { useGame } from '../store/useGame';
import { PageHeader, Progress } from '../components/ui';
import { agentSlots } from '../modules/tasks/engine';
import { eur } from '../lib/util';
import type { GameData } from '../store/state';

export default function UpgradesPage() {
  const s = useGame();
  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader title="Office Upgrades" subtitle={`Saldo ${eur(s.company.balance)} · ${s.agents.length}/${agentSlots(s as unknown as GameData)} bureaus · reputatie ${Math.round(s.company.reputation)}/100`} />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {s.upgrades.map((u) => {
          const cost = Math.round(u.cost * (1 + u.level * 0.6));
          const maxed = u.level >= u.maxLevel;
          return (
            <div key={u.id} className="panel relative overflow-hidden p-5">
              <div className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full bg-indigo-500/20 blur-2xl" />
              <div className="flex items-start gap-3">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500/30 to-fuchsia-500/20 text-3xl">{u.icon}</div>
                <div className="flex-1">
                  <div className="font-display text-lg font-bold text-white">{u.name}</div>
                  <div className="text-xs text-slate-400">{u.description}</div>
                </div>
              </div>
              <div className="mt-3 text-sm text-cyan-300">{u.effect}</div>
              <div className="mt-3 flex items-center gap-2 text-xs text-slate-400">Level {u.level}/{u.maxLevel}<div className="flex-1"><Progress value={(u.level / u.maxLevel) * 100} h={5} color="#a855f7" /></div></div>
              <button
                className="btn-primary mt-4 w-full"
                disabled={maxed || s.company.balance < cost}
                onClick={() => s.askConfirm({ title: `Buy ${u.name}?`, body: `${u.name} naar niveau ${u.level + 1} voor ${eur(cost)}.\n${u.effect}.`, confirmLabel: `Pay ${eur(cost)}`, onConfirm: () => s.buyUpgrade(u.id) })}
              >
                {maxed ? 'Maxed out' : `Upgrade · ${eur(cost)}`}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
