import { UserPlus, ClipboardList, ShieldAlert } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Avatar, Drawer, Empty, Progress, StateDot } from '../ui';
import TaskCard from './TaskCard';
import { DEPARTMENTS } from '../../modules/departments/departments';
import { PIPELINE } from '../../modules/workflows/pipeline';
import { roleById } from '../../modules/agents/roles';
import { ISSUE_META } from '../../modules/warroom/warroom';

export default function DepartmentDrawer() {
  const s = useGame();
  const id = s.selectedDept;
  if (!id || s.page !== 'hq') return <Drawer open={false} onClose={() => s.selectDept(null)}>{null}</Drawer>;

  if (id === 'warroom') {
    const active = s.warCases.filter((w) => w.status === 'Investigating' || w.status === 'Ready');
    return (
      <Drawer open onClose={() => s.selectDept(null)} title={<span className="flex items-center gap-2 text-rose-300"><ShieldAlert size={18} />War Room</span>}>
        <p className="text-sm text-slate-400">The executive crisis room. Management agents investigate declining metrics and bring recommendations for your approval.</p>
        <div className="mt-4 space-y-2">
          {active.length === 0 && <Empty>No active cases. Convene the War Room to investigate a problem.</Empty>}
          {active.map((w) => (
            <div key={w.id} className="rounded-xl border border-rose-500/30 bg-rose-500/5 p-3 text-sm">
              <div className="font-semibold text-white">{ISSUE_META[w.type].icon} {w.title}</div>
              <div className="text-xs text-slate-400">{w.status} · {w.evidence}</div>
            </div>
          ))}
        </div>
        <button className="btn-primary mt-4" onClick={() => s.setPage('warroom')}>Open War Room dashboard</button>
      </Drawer>
    );
  }

  const dept = DEPARTMENTS.find((d) => d.id === id)!;
  const agents = s.agents.filter((a) => a.department === id);
  const stages = PIPELINE.filter((p) => p.department === id);
  const deptTasks = s.tasks.filter((t) => (t.stage && stages.some((st) => st.id === t.stage)) || (t.kind !== 'pipeline' && agents.some((a) => a.id === t.agentId)));
  const open = deptTasks.filter((t) => !['Completed', 'Rejected'].includes(t.status));
  const done = deptTasks.filter((t) => t.status === 'Completed');
  const avgQ = done.length ? Math.round(done.reduce((a, t) => a + (t.quality ?? 0), 0) / done.length) : 0;
  const approvals = s.projects.filter((p) => p.status === 'Awaiting Approval' || p.status === 'Awaiting Publish');

  return (
    <Drawer open onClose={() => s.selectDept(null)} title={<span style={{ color: dept.color }}>{dept.icon} {dept.name}</span>} width={560}>
      <p className="text-sm text-slate-400">{dept.description}</p>
      <div className="mt-4 grid grid-cols-4 gap-2 text-center text-xs">
        {[['Agents', agents.length], ['Working', agents.filter((a) => a.state === 'working').length], ['Open tasks', open.length], ['Avg quality', avgQ || '—']].map(([l, v]) => (
          <div key={l as string} className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">{l}</div><div className="font-display text-lg font-bold text-white">{v}</div></div>
        ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <button className="btn-ghost text-xs" onClick={() => s.openModal('hireAgent', { dept: id })}><UserPlus size={14} />Hire for {dept.short}</button>
        <button className="btn-ghost text-xs" onClick={() => s.openModal('assignTask', { agentId: agents[0]?.id })} disabled={!agents.length}><ClipboardList size={14} />Assign task</button>
        <select className="input !w-auto !py-1.5 text-xs" defaultValue="" onChange={(e) => { s.assignDeptToChannel(id, e.target.value || null); s.toast(`${dept.short} now works for ${e.target.value ? s.channels.find((c) => c.id === e.target.value)?.name : 'all channels'}.`, 'success'); }}>
          <option value="" disabled>Assign department to channel…</option>
          <option value="">All channels</option>
          {s.channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {id === 'ceo' && (
        <div className="mt-5">
          <div className="label">Pending CEO approvals</div>
          {approvals.length === 0 && <Empty>Nothing waiting for you.</Empty>}
          <div className="space-y-2">
            {approvals.map((p) => (
              <button key={p.id} onClick={() => s.selectProject(p.id)} className="flex w-full items-center justify-between rounded-xl border border-amber-400/30 bg-amber-500/5 p-3 text-left text-sm hover:bg-amber-500/10">
                <span className="text-white">{p.title}</span><span className="text-xs text-amber-300">{p.status}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {stages.map((st) => {
        const live = s.tasks.filter((t) => t.stage === st.id && !['Completed', 'Rejected'].includes(t.status));
        const recent = s.tasks.filter((t) => t.stage === st.id && t.status === 'Completed').slice(-3).reverse();
        return (
          <div key={st.id} className="mt-5">
            <div className="flex items-center justify-between">
              <div className="label !mb-0">Stage · {st.label}</div>
              <div className="text-[11px] text-slate-500">Deliverable: {st.deliverableName}</div>
            </div>
            <div className="mt-2 space-y-2">
              {live.length === 0 && <div className="text-xs text-slate-500">No active work in this stage.</div>}
              {live.map((t) => <TaskCard key={t.id} task={t} compact />)}
              {recent.length > 0 && <div className="pt-1 text-[11px] text-slate-500">Recently delivered</div>}
              {recent.map((t) => <TaskCard key={t.id} task={t} compact />)}
            </div>
          </div>
        );
      })}

      {open.filter((t) => t.kind !== 'pipeline').length > 0 && (
        <div className="mt-5">
          <div className="label">Assigned tasks</div>
          <div className="space-y-2">{open.filter((t) => t.kind !== 'pipeline').map((t) => <TaskCard key={t.id} task={t} />)}</div>
        </div>
      )}

      <div className="label mt-5">Team</div>
      <div className="space-y-1.5">
        {agents.map((a) => (
          <button key={a.id} onClick={() => s.selectAgent(a.id)} className="flex w-full items-center gap-3 rounded-xl bg-white/[.03] p-2.5 text-left hover:bg-white/[.06]">
            <Avatar agent={a} size={34} />
            <div className="min-w-0 flex-1"><div className="text-sm font-semibold text-white">{a.name}</div><div className="text-xs text-slate-400">{roleById(a.role).title} · Lv {a.level}</div></div>
            <div className="w-24"><Progress value={a.performance} h={4} color={dept.color} /></div>
            <StateDot state={a.state} />
          </button>
        ))}
      </div>
    </Drawer>
  );
}
