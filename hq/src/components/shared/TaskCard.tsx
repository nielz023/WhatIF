import { useState } from 'react';
import { ChevronDown, FileText, MessageSquare, Link2 } from 'lucide-react';
import type { Priority, Task } from '../../types';
import { useGame } from '../../store/useGame';
import { Avatar, PriorityBadge, Progress, StatusBadge } from '../ui';
import { fmtTick, relTime } from '../../lib/util';
import { roleById } from '../../modules/agents/roles';
import { stageById } from '../../modules/workflows/pipeline';

export default function TaskCard({ task, compact }: { task: Task; compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const [comment, setComment] = useState('');
  const [doc, setDoc] = useState<string | null>(null);
  const s = useGame();
  const agent = s.agents.find((a) => a.id === task.agentId);
  const overdue = !['Completed', 'Rejected'].includes(task.status) && task.deadlineTick < s.tick;
  const deps = task.dependencies.map((d) => s.tasks.find((t) => t.id === d)).filter(Boolean) as Task[];
  const nameOf = (id: string) => (id === 'player' ? 'niels' : id === 'system' ? 'HQ' : s.agents.find((a) => a.id === id)?.name ?? 'Oud teamlid');

  return (
    <div className={`rounded-xl border bg-hq-bg/50 transition ${open ? 'border-sky-400/50' : 'border-hq-line/70 hover:border-slate-500/70'}`}>
      <button className="flex w-full items-center gap-3 p-3 text-left" onClick={() => setOpen(!open)}>
        <Avatar agent={agent} size={30} />
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-semibold text-white">{task.title}</div>
          <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[13px] text-slate-400">
            <StatusBadge status={task.status} />
            {!compact && <PriorityBadge p={task.priority} />}
            <span>{agent ? agent.name : 'Nog niemand'}</span>
            {overdue && <span className="text-rose-400">· te laat</span>}
            {task.revision > 0 && <span className="text-amber-300">· versie {task.revision + 1}</span>}
          </div>
          {['In Progress', 'Assigned'].includes(task.status) && <div className="mt-1.5"><Progress value={task.progress} h={4} /></div>}
        </div>
        <ChevronDown size={16} className={`shrink-0 text-slate-500 transition ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="space-y-3 border-t border-hq-line/60 p-3 text-sm">
          <p className="text-slate-300">{task.description}</p>
          <div className="grid grid-cols-2 gap-2 text-[13px] text-slate-400">
            <div>Gemaakt: <span className="text-slate-200">{fmtTick(task.createdTick)}</span></div>
            <div>Deadline: <span className={overdue ? 'text-rose-300' : 'text-slate-200'}>{fmtTick(task.deadlineTick)}</span></div>
          </div>
          {deps.length > 0 && (
            <div className="text-[13px] text-slate-400"><Link2 size={12} className="mr-1 inline" />Hangt af van: {deps.map((d) => <span key={d.id} className="mr-2 text-slate-200">{d.title} <StatusBadge status={d.status} /></span>)}</div>
          )}
          {task.result && <div className="rounded-lg bg-emerald-500/10 px-3 py-2 text-[13px] text-emerald-200">Resultaat: {task.result}</div>}

          {task.documents.length > 0 && (
            <div>
              <div className="label">Documenten</div>
              <div className="flex flex-wrap gap-1.5">
                {task.documents.map((d) => (
                  <button key={d.id} onClick={() => setDoc(doc === d.id ? null : d.id)} className={`chip ring-1 ${doc === d.id ? 'bg-sky-500/20 text-white ring-sky-400/50' : 'bg-slate-700/30 text-slate-300 ring-slate-600/50'}`}>
                    <FileText size={11} />{d.name}
                  </button>
                ))}
              </div>
              {doc && <pre className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap rounded-lg bg-black/40 p-3 font-mono text-[13px] leading-relaxed text-slate-200">{task.documents.find((d) => d.id === doc)?.content}</pre>}
            </div>
          )}

          <div>
            <div className="label flex items-center gap-1"><MessageSquare size={11} />Opmerkingen ({task.comments.length})</div>
            <div className="max-h-40 space-y-1.5 overflow-y-auto">
              {task.comments.map((c) => (
                <div key={c.id} className="rounded-lg bg-white/[.03] px-2.5 py-1.5 text-[13px]"><span className="font-semibold text-slate-200">{nameOf(c.authorId)}</span> <span className="text-slate-500">· {relTime(c.tick, s.tick)}</span><div className="text-slate-300">{c.text}</div></div>
              ))}
            </div>
            <form className="mt-2 flex gap-2" onSubmit={(e) => { e.preventDefault(); if (comment.trim()) { s.commentTask(task.id, comment.trim()); setComment(''); } }}>
              <input className="input !py-1.5 text-[13px]" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Opmerking voor dit teamlid…" />
              <button className="btn-ghost !py-1.5 text-[13px]" disabled={!comment.trim()}>Sturen</button>
            </form>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {task.kind !== 'pipeline' && task.status === 'Review' && (
              <>
                <button className="btn-success !py-1.5 text-[13px]" onClick={() => s.reviewTask(task.id, true)}>Goedkeuren</button>
                <button className="btn-danger !py-1.5 text-[13px]" onClick={() => s.reviewTask(task.id, false, comment || undefined)}>Aanpassen</button>
              </>
            )}
            {!['Completed', 'Rejected'].includes(task.status) && task.stage !== 'approval' && task.stage !== 'publishing' && (
              <>
                <select className="input !w-auto !py-1.5 text-[13px]" value={task.priority} onChange={(e) => s.setTaskPriority(task.id, e.target.value as Priority)}>
                  {([['Low', 'Laag'], ['Medium', 'Normaal'], ['High', 'Hoog'], ['Critical', 'Spoed']] as const).map(([p, l]) => <option key={p} value={p}>{l}</option>)}
                </select>
                <select className="input !w-auto !py-1.5 text-[13px]" value="" onChange={(e) => e.target.value && s.reassignTask(task.id, e.target.value)}>
                  <option value="">Iemand anders geven…</option>
                  {s.agents.filter((a) => a.id !== task.agentId && (!task.stage || stageById(task.stage).roles.includes(a.role))).map((a) => <option key={a.id} value={a.id}>{a.name} ({roleById(a.role).title})</option>)}
                </select>
              </>
            )}
            {agent && <button className="btn-ghost !py-1.5 text-[13px]" onClick={() => s.selectAgent(agent.id)}>Teamlid openen</button>}
          </div>
        </div>
      )}
    </div>
  );
}
