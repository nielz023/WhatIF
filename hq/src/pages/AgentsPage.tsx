import { useState } from 'react';
import { useGame } from '../store/useGame';
import { Avatar, PageHeader, Progress, StateDot } from '../components/ui';
import { DEPARTMENTS, deptById } from '../modules/departments/departments';
import { roleById } from '../modules/agents/roles';
import type { DepartmentId } from '../types';

/** Teamleden: wie er is en waar ze aan werken. Geen loonkosten, niveaus, upgrades of aannemen meer (niels 2026-11-06). */
export default function AgentsPage() {
  const s = useGame();
  const [dept, setDept] = useState<DepartmentId | 'all'>('all');
  const [q, setQ] = useState('');
  const list = s.agents.filter((a) => (dept === 'all' || a.department === dept) && (a.name + roleById(a.role).title).toLowerCase().includes(q.toLowerCase()));
  const working = s.agents.filter((a) => a.state === 'working').length;

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader
        title="Teamleden"
        subtitle={`${s.agents.length} ${s.agents.length === 1 ? 'teamlid' : 'teamleden'} · ${working} aan het werk`}
      />
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input className="input !w-56 !py-1.5 text-[13px]" placeholder="Zoek een teamlid…" value={q} onChange={(e) => setQ(e.target.value)} />
        <button onClick={() => setDept('all')} className={`chip px-3 py-1 ring-1 ${dept === 'all' ? 'bg-sky-500/25 text-white ring-sky-400/60' : 'text-slate-400 ring-slate-700'}`}>Alle</button>
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
            <div key={a.id} role="button" tabIndex={0} onKeyDown={(e) => { if (e.key === 'Enter') s.selectAgent(a.id); }} onClick={() => s.selectAgent(a.id)} className="panel group cursor-pointer relative overflow-hidden p-4 text-left transition hover:-translate-y-0.5 hover:border-sky-400/50">
              <div className="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full opacity-20 blur-2xl" style={{ background: d.color }} />
              <div className="flex items-center gap-3">
                <Avatar agent={a} size={46} ring={a.state === 'working'} />
                <div className="min-w-0 flex-1">
                  <div className="truncate font-semibold text-white">{a.name}</div>
                  <div className="truncate text-[13px] text-slate-400">{roleById(a.role).title}</div>
                  <div className="text-[13px]" style={{ color: d.color }}>{d.icon} {d.short}</div>
                </div>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <StateDot state={a.state} />
                <span className="text-[12px] text-slate-500">{a.completed} {a.completed === 1 ? 'taak' : 'taken'} af</span>
              </div>
              <div className="mt-1 truncate text-[13px] text-slate-400">{task ? `▶ ${task.title}` : 'Geen lopende taak'}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
