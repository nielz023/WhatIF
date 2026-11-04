import { useState } from 'react';
import { UserPlus } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Avatar, PageHeader, Progress, StateDot } from '../components/ui';
import { DEPARTMENTS, deptById } from '../modules/departments/departments';
import { ROLES, roleById } from '../modules/agents/roles';
import { agentSlots, SALARY_FACTOR } from '../modules/tasks/engine';
import { eur } from '../lib/util';
import type { DepartmentId } from '../types';
import type { GameData } from '../store/state';

export default function AgentsPage() {
  const s = useGame();
  const [dept, setDept] = useState<DepartmentId | 'all'>('all');
  const [q, setQ] = useState('');
  const list = s.agents.filter((a) => (dept === 'all' || a.department === dept) && (a.name + roleById(a.role).title).toLowerCase().includes(q.toLowerCase()));
  const missing = ROLES.filter((r) => !s.agents.some((a) => a.role === r.id));
  const payroll = s.agents.reduce((t, a) => t + a.salary, 0) * SALARY_FACTOR;

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader
        title="AI Agents"
        subtitle={`${s.agents.length}/${agentSlots(s as unknown as GameData)} desks filled · payroll ≈ ${eur(payroll)}/day`}
        actions={<button className="btn-primary text-xs" onClick={() => s.openModal('hireAgent', dept !== 'all' ? { dept } : undefined)}><UserPlus size={14} />Hire agent</button>}
      />
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input className="input !w-56 !py-1.5 text-xs" placeholder="Search agents…" value={q} onChange={(e) => setQ(e.target.value)} />
        <button onClick={() => setDept('all')} className={`chip px-3 py-1 ring-1 ${dept === 'all' ? 'bg-indigo-500/25 text-white ring-indigo-400/60' : 'text-slate-400 ring-slate-700'}`}>All</button>
        {DEPARTMENTS.map((d) => (
          <button key={d.id} onClick={() => setDept(d.id)} className={`chip px-3 py-1 ring-1 ${dept === d.id ? 'text-white' : 'text-slate-400 ring-slate-700'}`} style={dept === d.id ? { background: `${d.color}30`, boxShadow: `inset 0 0 0 1px ${d.color}` } : undefined}>
            {d.icon} {d.short} <span className="text-slate-500">{s.agents.filter((a) => a.department === d.id).length}</span>
          </button>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        {list.map((a) => {
          const d = deptById(a.department);
          const task = s.tasks.find((t) => t.id === a.currentTaskId);
          return (
            <button key={a.id} onClick={() => s.selectAgent(a.id)} className="panel group relative overflow-hidden p-4 text-left transition hover:-translate-y-0.5 hover:border-indigo-400/50">
              <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full opacity-20 blur-2xl" style={{ background: d.color }} />
              <div className="flex items-center gap-3">
                <Avatar agent={a} size={46} ring={a.state === 'working'} />
                <div className="min-w-0 flex-1">
                  <div className="truncate font-semibold text-white">{a.name}</div>
                  <div className="truncate text-xs text-slate-400">{roleById(a.role).title}</div>
                  <div className="text-[11px]" style={{ color: d.color }}>{d.icon} {d.short}</div>
                </div>
                <div className="text-center"><div className="font-display text-lg font-bold text-white">{a.level}</div><div className="text-[9px] uppercase text-slate-500">lvl</div></div>
              </div>
              <div className="mt-3 grid grid-cols-2 gap-2 text-[10px] text-slate-400">
                <div>Performance<Progress value={a.performance} h={4} color="#22c55e" /></div>
                <div>Morale<Progress value={a.morale} h={4} color="#f59e0b" /></div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <StateDot state={a.state} />
                <span className="text-[10px] text-slate-500">{a.completed} tasks done</span>
              </div>
              <div className="mt-1 truncate text-[11px] text-slate-400">{task ? `▶ ${task.title}` : a.channelIds.length ? `Channels: ${a.channelIds.map((id) => s.channels.find((c) => c.id === id)?.name).join(', ')}` : 'All channels'}</div>
            </button>
          );
        })}
      </div>

      {missing.length > 0 && (
        <div className="mt-6">
          <div className="label">Open roles you haven't hired yet</div>
          <div className="flex flex-wrap gap-2">
            {missing.map((r) => (
              <button key={r.id} onClick={() => s.openModal('hireAgent', { dept: r.department })} className="chip bg-slate-800/60 px-3 py-1.5 text-slate-300 ring-1 ring-slate-700 hover:ring-indigo-400">
                + {r.title} <span className="text-slate-500">{eur(r.hireCost)}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
