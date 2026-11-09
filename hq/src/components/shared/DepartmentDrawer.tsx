import { ClipboardList, ShieldAlert } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Avatar, Drawer, Empty, Progress, StateDot, STATUS_NL } from '../ui';
import TaskCard from './TaskCard';
import { DEPARTMENTS } from '../../modules/departments/departments';
import { PIPELINE } from '../../modules/workflows/pipeline';
import { roleById } from '../../modules/agents/roles';
import { alarmsFrom } from '../../world/alarms';
import { useLive } from '../../services/live';

export default function DepartmentDrawer() {
  const s = useGame();
  const id = s.selectedDept;
  if (!id || s.page !== 'hq') return <Drawer open={false} onClose={() => s.selectDept(null)}>{null}</Drawer>;

  if (id === 'warroom') {
    // alleen echte alarmen, geen verzonnen zaken (niels 2026-11-06)
    const alarms = alarmsFrom(useLive.getState().data);
    return (
      <Drawer open onClose={() => s.selectDept(null)} title={<span className="flex items-center gap-2 text-rose-300"><ShieldAlert size={18} />Crisiskamer</span>}>
        <p className="text-sm text-slate-400">Hier zie je wat er echt mis is in je project: mislukte of lang wachtende taken, de renderstatus, de schijf en fouten in de automatische ronde.</p>
        <div className="mt-4 space-y-2">
          {alarms.length === 0 && <Empty>Alles in orde. Er is nu niets mislukt of vastgelopen.</Empty>}
          {alarms.map((a) => (
            <div key={a.key} className={`rounded-xl border p-3 text-sm text-white ${a.level === 'rood' ? 'border-rose-500/40 bg-rose-500/5' : 'border-amber-500/40 bg-amber-500/5'}`}>{a.text}</div>
          ))}
        </div>
        <button className="btn-primary mt-4" onClick={() => s.setPage('warroom')}>Crisiskamer openen</button>
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
      <div className="mt-4 grid grid-cols-4 gap-2 text-center text-[13px]">
        {[['Teamleden', agents.length], ['Bezig', agents.filter((a) => a.state === 'working').length], ['Open taken', open.length], ['Klaar', done.length]].map(([l, v]) => (
          <div key={l as string} className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">{l}</div><div className="font-display text-lg font-bold text-white">{v}</div></div>
        ))}
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <button className="btn-ghost text-[13px]" onClick={() => s.openModal('assignTask', { agentId: agents[0]?.id })} disabled={!agents.length}><ClipboardList size={14} />Taak geven</button>
      </div>

      {id === 'ceo' && (
        <div className="mt-5">
          <div className="label">Wacht op jouw akkoord</div>
          {approvals.length === 0 && <Empty>Er wacht niets op jou.</Empty>}
          <div className="space-y-2">
            {approvals.map((p) => (
              <button key={p.id} onClick={() => s.selectProject(p.id)} className="flex w-full items-center justify-between rounded-xl border border-amber-400/30 bg-amber-500/5 p-3 text-left text-sm hover:bg-amber-500/10">
                <span className="text-white">{p.title}</span><span className="text-[13px] text-amber-300">{STATUS_NL[p.status] ?? p.status}</span>
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
              <div className="label !mb-0">Stap · {st.label}</div>
              <div className="text-[13px] text-slate-500">Oplevering: {st.deliverableName}</div>
            </div>
            <div className="mt-2 space-y-2">
              {live.length === 0 && <div className="text-[13px] text-slate-500">Nu geen werk in deze stap.</div>}
              {live.map((t) => <TaskCard key={t.id} task={t} compact />)}
              {recent.length > 0 && <div className="pt-1 text-[13px] text-slate-500">Net opgeleverd</div>}
              {recent.map((t) => <TaskCard key={t.id} task={t} compact />)}
            </div>
          </div>
        );
      })}

      {open.filter((t) => t.kind !== 'pipeline').length > 0 && (
        <div className="mt-5">
          <div className="label">Losse taken</div>
          <div className="space-y-2">{open.filter((t) => t.kind !== 'pipeline').map((t) => <TaskCard key={t.id} task={t} />)}</div>
        </div>
      )}

      <div className="label mt-5">Teamleden</div>
      <div className="space-y-1.5">
        {agents.map((a) => (
          <button key={a.id} onClick={() => s.selectAgent(a.id)} className="flex w-full items-center gap-3 rounded-xl bg-white/[.03] p-2.5 text-left hover:bg-white/[.06]">
            <Avatar agent={a} size={34} />
            <div className="min-w-0 flex-1"><div className="text-sm font-semibold text-white">{a.name}</div><div className="text-[13px] text-slate-400">{roleById(a.role).title}</div></div>
            <StateDot state={a.state} />
          </button>
        ))}
      </div>
    </Drawer>
  );
}
