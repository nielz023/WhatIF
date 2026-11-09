import { useState } from 'react';
import { Clapperboard, ClipboardList } from 'lucide-react';
import { useGame } from '../store/useGame';
import { Empty, PageHeader, PriorityBadge, Progress, StatusBadge, Tabs, Avatar, STATUS_NL } from '../components/ui';
import PipelineStepper from '../components/shared/Pipeline';
import TaskCard from '../components/shared/TaskCard';
import { PIPELINE, stageProgress } from '../modules/workflows/pipeline';
import { deptById } from '../modules/departments/departments';
import { projectQuality } from '../modules/tasks/engine';
import { fmtTick } from '../lib/util';
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
        title="Projecten"
        subtitle="Elke echte video als project, met de stappen van idee tot upload. Afgekeurd werk gaat terug naar de afdeling die het maakte."
        actions={<>
          <Tabs value={view} onChange={setView} items={[{ id: 'board', label: 'Bord' }, { id: 'list', label: 'Lijst' }, { id: 'tasks', label: 'Taken' }]} />
          <button className="btn-ghost text-[13px]" onClick={() => s.openModal('assignTask')}><ClipboardList size={14} />Taak geven</button>
          <button className="btn-primary text-[13px]" onClick={() => s.openModal('newVideo')}><Clapperboard size={14} />Nieuwe video</button>
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
                  <div className="flex items-center justify-between text-[13px] font-bold text-white"><span>{st.label}</span><span className="rounded-full bg-black/30 px-1.5">{items.length}</span></div>
                  <div className="text-[12px] text-slate-400">{deptById(st.department).short} · {working} bezig{st.manual ? ' · jouw akkoord' : ''}</div>
                </div>
                <div className="space-y-2">
                  {items.map((p) => {
                    const ch = s.channels.find((c) => c.id === p.channelId);
                    const t = s.tasks.find((x) => x.projectId === p.id && x.stage === p.stage && !['Completed', 'Rejected'].includes(x.status));
                    const ag = s.agents.find((a) => a.id === t?.agentId);
                    return (
                      <button key={p.id} onClick={() => s.selectProject(p.id)} className="panel w-full p-3 text-left transition hover:-translate-y-0.5 hover:border-sky-400/50">
                        <div className="mt-0.5 text-sm font-semibold leading-snug text-white">{p.title}</div>
                        <div className="mt-2 flex items-center gap-2">
                          {t && <StatusBadge status={p.status === 'Active' ? t.status : p.status} />}
                          {p.rejections > 0 && <span className="chip bg-rose-500/10 text-rose-300">↩ {p.rejections}</span>}
                        </div>
                        {t && t.status === 'In Progress' && <div className="mt-2"><Progress value={t.progress} h={4} color={color} /></div>}
                        <div className="mt-2 flex items-center justify-between text-[12px] text-slate-500">
                          <span className="flex items-center gap-1">{ag && <Avatar agent={ag} size={18} />}{ag?.name.split(' ')[0] ?? (p.status === 'Active' ? 'wacht op teamlid' : '')}</span>
                          <span className={p.deadlineTick < s.tick ? 'text-rose-400' : ''}>{fmtTick(p.deadlineTick)}</span>
                        </div>
                      </button>
                    );
                  })}
                  {items.length === 0 && <div className="rounded-xl border border-dashed border-hq-line/60 p-3 text-center text-[13px] text-slate-600">Leeg</div>}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {view === 'list' && (
        <div className="space-y-2">
          {projects.length === 0 && <Empty>Nog geen projecten.</Empty>}
          {projects.map((p) => {
            const ch = s.channels.find((c) => c.id === p.channelId);
            return (
              <button key={p.id} onClick={() => s.selectProject(p.id)} className="panel flex w-full flex-wrap items-center gap-4 p-3 text-left hover:border-sky-400/50">
                <span className="text-2xl">{ch?.logo.emoji}</span>
                <div className="min-w-[200px] flex-1">
                  <div className="font-semibold text-white">{p.title}</div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-[13px] text-slate-400"><span>{ch?.name}</span><StatusBadge status={p.status} /><PriorityBadge p={p.priority} /></div>
                </div>
                <div className="hidden md:block"><PipelineStepper project={p} small /></div>
                <div className="w-24 text-[13px] text-slate-400">Kwaliteit {projectQuality(p) || '—'}</div>
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
              <button key={st} onClick={() => setTaskStatus(st)} className={`chip px-3 py-1 ring-1 ${taskStatus === st ? 'bg-sky-500/25 text-white ring-sky-400/60' : 'text-slate-400 ring-slate-700'}`}>
                {st === 'all' ? 'Alles' : (STATUS_NL[st] ?? st)} <span className="text-slate-500">{st === 'all' ? s.tasks.length : s.tasks.filter((t) => t.status === st).length}</span>
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
