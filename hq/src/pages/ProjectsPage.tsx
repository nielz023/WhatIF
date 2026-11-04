import { useState } from 'react';
import { Clapperboard, ClipboardList } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Empty, PageHeader, PriorityBadge, Progress, StatusBadge, Tabs, Avatar } from '../components/ui';
import PipelineStepper from '../components/shared/Pipeline';
import TaskCard from '../components/shared/TaskCard';
import { PIPELINE, stageProgress } from '../modules/workflows/pipeline';
import { deptById } from '../modules/departments/departments';
import { projectQuality } from '../modules/tasks/engine';
import { eur, fmtTick } from '../lib/util';
import type { TaskStatus } from '../types';

const STATUSES: TaskStatus[] = ['Pending', 'Assigned', 'In Progress', 'Review', 'Approved', 'Rejected', 'Completed'];

export default function ProjectsPage() {
  const s = useGame();
  const [view, setView] = useState<'board' | 'list' | 'tasks'>('board');
  const [channel, setChannel] = useState('all');
  const [taskStatus, setTaskStatus] = useState<TaskStatus | 'all'>('all');
  const projects = s.projects.filter((p) => channel === 'all' || p.channelId === channel);
  const live = projects.filter((p) => p.status !== 'Published' && p.status !== 'Cancelled');

  return (
    <div className="h-full overflow-y-auto p-4 pb-28 md:p-6 md:pb-28">
      <PageHeader
        title="Projects"
        subtitle="Every video moves through the 11-stage production pipeline. Rejected work loops back to the responsible department."
        actions={<>
          <select className="input !w-auto !py-1.5 text-xs" value={channel} onChange={(e) => setChannel(e.target.value)}>
            <option value="all">All channels</option>
            {s.channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <Tabs value={view} onChange={setView} items={[{ id: 'board', label: 'Pipeline board' }, { id: 'list', label: 'All projects' }, { id: 'tasks', label: 'Task engine' }]} />
          <button className="btn-ghost text-xs" onClick={() => s.openModal('assignTask')}><ClipboardList size={14} />Assign task</button>
          <button className="btn-primary text-xs" onClick={() => s.openModal('newVideo')}><Clapperboard size={14} />New video</button>
        </>}
      />

      {view === 'board' && (
        <div className="flex gap-3 overflow-x-auto pb-3">
          {PIPELINE.map((st) => {
            const items = live.filter((p) => p.stage === st.id);
            const color = deptById(st.department).color;
            const working = s.tasks.filter((t) => t.stage === st.id && t.status === 'In Progress').length;
            return (
              <div key={st.id} className="w-[230px] shrink-0">
                <div className="mb-2 rounded-xl border px-3 py-2" style={{ borderColor: `${color}55`, background: `${color}12` }}>
                  <div className="flex items-center justify-between text-xs font-bold text-white"><span>{st.label}</span><span className="rounded-full bg-black/30 px-1.5">{items.length}</span></div>
                  <div className="text-[10px] text-slate-400">{deptById(st.department).short} · {working} working{st.manual ? ' · needs CEO' : ''}</div>
                </div>
                <div className="space-y-2">
                  {items.map((p) => {
                    const ch = s.channels.find((c) => c.id === p.channelId);
                    const t = s.tasks.find((x) => x.projectId === p.id && x.stage === p.stage && !['Completed', 'Rejected'].includes(x.status));
                    const ag = s.agents.find((a) => a.id === t?.agentId);
                    return (
                      <button key={p.id} onClick={() => s.selectProject(p.id)} className="panel w-full p-3 text-left transition hover:-translate-y-0.5 hover:border-indigo-400/50">
                        <div className="text-xs text-slate-400">{ch?.logo.emoji} {ch?.name}</div>
                        <div className="mt-0.5 text-sm font-semibold leading-snug text-white">{p.title}</div>
                        <div className="mt-2 flex items-center gap-2">
                          {t && <StatusBadge status={p.status === 'Active' ? t.status : p.status} />}
                          {p.rejections > 0 && <span className="chip bg-rose-500/10 text-rose-300">↩ {p.rejections}</span>}
                        </div>
                        {t && t.status === 'In Progress' && <div className="mt-2"><Progress value={t.progress} h={4} color={color} /></div>}
                        <div className="mt-2 flex items-center justify-between text-[10px] text-slate-500">
                          <span className="flex items-center gap-1">{ag && <Avatar agent={ag} size={18} />}{ag?.name.split(' ')[0] ?? (p.status === 'Active' ? 'waiting for agent' : '')}</span>
                          <span className={p.deadlineTick < s.tick ? 'text-rose-400' : ''}>{fmtTick(p.deadlineTick)}</span>
                        </div>
                      </button>
                    );
                  })}
                  {items.length === 0 && <div className="rounded-xl border border-dashed border-hq-line/60 p-3 text-center text-[11px] text-slate-600">Empty</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {view === 'list' && (
        <div className="space-y-2">
          {projects.length === 0 && <Empty>No projects yet.</Empty>}
          {projects.map((p) => {
            const ch = s.channels.find((c) => c.id === p.channelId);
            return (
              <button key={p.id} onClick={() => s.selectProject(p.id)} className="panel flex w-full flex-wrap items-center gap-4 p-3 text-left hover:border-indigo-400/50">
                <span className="text-2xl">{ch?.logo.emoji}</span>
                <div className="min-w-[200px] flex-1">
                  <div className="font-semibold text-white">{p.title}</div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-slate-400"><span>{ch?.name}</span><StatusBadge status={p.status} /><PriorityBadge p={p.priority} /></div>
                </div>
                <div className="hidden md:block"><PipelineStepper project={p} small /></div>
                <div className="w-24 text-xs text-slate-400">Q {projectQuality(p) || '—'} · {eur(p.cost)}</div>
                <div className="w-28"><Progress value={p.status === 'Published' ? 100 : stageProgress(p.stage)} h={5} /></div>
              </button>
            );
          })}
        </div>
      )}

      {view === 'tasks' && (
        <div>
          <div className="mb-3 flex flex-wrap gap-1.5">
            {(['all', ...STATUSES] as const).map((st) => (
              <button key={st} onClick={() => setTaskStatus(st)} className={`chip px-3 py-1 ring-1 ${taskStatus === st ? 'bg-indigo-500/25 text-white ring-indigo-400/60' : 'text-slate-400 ring-slate-700'}`}>
                {st === 'all' ? 'All' : st} <span className="text-slate-500">{st === 'all' ? s.tasks.length : s.tasks.filter((t) => t.status === st).length}</span>
              </button>
            ))}
          </div>
          <div className="grid gap-2 xl:grid-cols-2">
            {[...s.tasks].reverse().filter((t) => taskStatus === 'all' || t.status === taskStatus).filter((t) => channel === 'all' || s.projects.find((p) => p.id === t.projectId)?.channelId === channel || !t.projectId).slice(0, 60).map((t) => <TaskCard key={t.id} task={t} />)}
          </div>
        </div>
      )}
    </div>
  );
}
