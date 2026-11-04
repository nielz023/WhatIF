import { useEffect, useState } from 'react';
import { Dices } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Avatar, Modal } from '../ui';
import type { DepartmentId, Priority, RoleId } from '../../types';
import { ROLES, roleById } from '../../modules/agents/roles';
import { DEPARTMENTS } from '../../modules/departments/departments';
import { suggestTopic } from '../../modules/workflows/deliverables';
import { agentSlots, SALARY_FACTOR } from '../../modules/tasks/engine';
import { eur } from '../../lib/util';

const PRIORITIES: Priority[] = ['Low', 'Medium', 'High', 'Critical'];

export function NewVideoModal() {
  const { modal, closeModal, channels, startVideo, setPage, selectProject } = useGame();
  const [channelId, setChannelId] = useState(channels[0]?.id ?? '');
  const [topic, setTopic] = useState('');
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<Priority>('Medium');
  const [deadline, setDeadline] = useState(5);
  const open = modal === 'newVideo';
  useEffect(() => {
    if (open) { const ch = channels[0]; setChannelId(ch?.id ?? ''); const t = suggestTopic(ch?.niche ?? ''); setTopic(t); setTitle(t); }
  }, [open]); // eslint-disable-line
  const ch = channels.find((c) => c.id === channelId);
  const submit = () => {
    if (!title.trim() || !channelId) return;
    const id = startVideo({ channelId, title: title.trim(), topic: topic.trim() || title.trim(), priority, deadlineDays: deadline });
    closeModal();
    selectProject(id);
    setPage('projects');
  };
  return (
    <Modal open={open} onClose={closeModal} title="🎬 Start New Video" footer={<><button className="btn-ghost" onClick={closeModal}>Cancel</button><button className="btn-primary" onClick={submit} disabled={!title.trim() || !channelId}>Greenlight project</button></>}>
      <div className="grid gap-4">
        <div>
          <label className="label">Channel</label>
          <div className="grid grid-cols-2 gap-2">
            {channels.map((c) => (
              <button key={c.id} onClick={() => { setChannelId(c.id); const t = suggestTopic(c.niche); setTopic(t); setTitle(t); }} className={`flex items-center gap-2 rounded-xl border p-2.5 text-left text-sm transition ${channelId === c.id ? 'border-indigo-400 bg-indigo-500/15' : 'border-hq-line hover:border-slate-500'}`}>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg text-lg" style={{ background: `${c.logo.color}33` }}>{c.logo.emoji}</span>
                <span><span className="block font-semibold text-white">{c.name}</span><span className="text-xs text-slate-400">{c.niche}</span></span>
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="label">Topic</label>
          <div className="flex gap-2">
            <input className="input" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="What's the video about?" />
            <button className="btn-ghost" title="Ask Research for a suggestion" onClick={() => { const t = suggestTopic(ch?.niche ?? ''); setTopic(t); setTitle(t); }}><Dices size={16} /></button>
          </div>
        </div>
        <div>
          <label className="label">Working title</label>
          <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Priority</label>
            <select className="input" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>{PRIORITIES.map((p) => <option key={p}>{p}</option>)}</select>
          </div>
          <div>
            <label className="label">Deadline (game days)</label>
            <input className="input" type="number" min={1} max={30} value={deadline} onChange={(e) => setDeadline(Math.max(1, +e.target.value))} />
          </div>
        </div>
        <p className="rounded-xl bg-indigo-500/10 p-3 text-xs text-indigo-200">The project enters the pipeline at <b>Research</b> and flows through all 11 stages. You'll be asked to approve it at <b>CEO Approval</b> and to confirm before <b>Publishing</b>.</p>
      </div>
    </Modal>
  );
}

export function AssignTaskModal() {
  const { modal, modalPayload, closeModal, agents, projects, tasks, assignManualTask } = useGame();
  const open = modal === 'assignTask';
  const [title, setTitle] = useState('');
  const [desc, setDesc] = useState('');
  const [agentId, setAgentId] = useState<string>('');
  const [projectId, setProjectId] = useState<string>('');
  const [priority, setPriority] = useState<Priority>('Medium');
  const [deadline, setDeadline] = useState(2);
  const [dep, setDep] = useState('');
  useEffect(() => {
    if (open) { setTitle(''); setDesc(''); setAgentId((modalPayload?.agentId as string) ?? agents[0]?.id ?? ''); setProjectId(''); setDep(''); setPriority('Medium'); }
  }, [open]); // eslint-disable-line
  const submit = () => {
    if (!title.trim()) return;
    assignManualTask({ title: title.trim(), description: desc.trim(), agentId: agentId || null, priority, deadlineDays: deadline, projectId: projectId || null, dependencies: dep ? [dep] : [] });
    closeModal();
  };
  const openTasks = tasks.filter((t) => !['Completed', 'Rejected'].includes(t.status)).slice(-30);
  return (
    <Modal open={open} onClose={closeModal} title="📋 Assign Task" footer={<><button className="btn-ghost" onClick={closeModal}>Cancel</button><button className="btn-primary" onClick={submit} disabled={!title.trim()}>Assign</button></>}>
      <div className="grid gap-3">
        <div><label className="label">Title</label><input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Analyse top 10 competitor videos" /></div>
        <div><label className="label">Description / instructions</label><textarea className="input min-h-[80px]" value={desc} onChange={(e) => setDesc(e.target.value)} /></div>
        <div>
          <label className="label">Assigned agent</label>
          <select className="input" value={agentId} onChange={(e) => setAgentId(e.target.value)}>
            {DEPARTMENTS.map((d) => (
              <optgroup key={d.id} label={d.name}>
                {agents.filter((a) => a.department === d.id).map((a) => <option key={a.id} value={a.id}>{a.name} — {roleById(a.role).title} ({a.state})</option>)}
              </optgroup>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">Priority</label><select className="input" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>{PRIORITIES.map((p) => <option key={p}>{p}</option>)}</select></div>
          <div><label className="label">Deadline (days)</label><input className="input" type="number" min={1} value={deadline} onChange={(e) => setDeadline(Math.max(1, +e.target.value))} /></div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">Link to project</label><select className="input" value={projectId} onChange={(e) => setProjectId(e.target.value)}><option value="">— none —</option>{projects.filter((p) => p.status !== 'Published' && p.status !== 'Cancelled').map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}</select></div>
          <div><label className="label">Depends on</label><select className="input" value={dep} onChange={(e) => setDep(e.target.value)}><option value="">— no dependency —</option>{openTasks.map((t) => <option key={t.id} value={t.id}>{t.title.slice(0, 50)}</option>)}</select></div>
        </div>
      </div>
    </Modal>
  );
}

export function HireAgentModal() {
  const s = useGame();
  const open = s.modal === 'hireAgent';
  const [dept, setDept] = useState<DepartmentId>('research');
  const [role, setRole] = useState<RoleId>('researcher');
  const [channelId, setChannelId] = useState('');
  useEffect(() => {
    if (open) {
      const d = (s.modalPayload?.dept as DepartmentId) ?? 'research';
      setDept(d);
      setRole(ROLES.find((r) => r.department === d)!.id);
    }
  }, [open]); // eslint-disable-line
  const def = roleById(role);
  const slots = agentSlots(s as never);
  const full = s.agents.length >= slots;
  return (
    <Modal open={open} onClose={s.closeModal} title="👋 Hire AI Agent" width={680} footer={
      <>
        <span className="mr-auto self-center text-xs text-slate-400">Desks: {s.agents.length}/{slots} · Balance {eur(s.company.balance)}</span>
        <button className="btn-ghost" onClick={s.closeModal}>Cancel</button>
        <button className="btn-primary" disabled={full || s.company.balance < def.hireCost} onClick={() => { if (s.hireAgent(role, channelId ? [channelId] : [])) s.closeModal(); }}>Hire for {eur(def.hireCost)}</button>
      </>
    }>
      <div className="grid gap-4 md:grid-cols-[200px_1fr]">
        <div className="space-y-1">
          {DEPARTMENTS.map((d) => (
            <button key={d.id} onClick={() => { setDept(d.id); setRole(ROLES.find((r) => r.department === d.id)!.id); }} className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm ${dept === d.id ? 'bg-white/10 text-white' : 'text-slate-400 hover:bg-white/5'}`}>
              <span>{d.icon}</span>{d.short}
              <span className="ml-auto text-xs text-slate-500">{s.agents.filter((a) => a.department === d.id).length}</span>
            </button>
          ))}
        </div>
        <div className="space-y-3">
          <div className="grid gap-2">
            {ROLES.filter((r) => r.department === dept).map((r) => (
              <button key={r.id} onClick={() => setRole(r.id)} className={`rounded-xl border p-3 text-left transition ${role === r.id ? 'border-indigo-400 bg-indigo-500/10' : 'border-hq-line hover:border-slate-500'}`}>
                <div className="flex items-center justify-between"><span className="font-semibold text-white">{r.title}</span><span className="text-xs text-emerald-300">{eur(r.hireCost)} · {eur(r.baseSalary * SALARY_FACTOR, 2)}/day</span></div>
                <div className="mt-1 text-xs text-slate-400">{r.description}</div>
                <div className="mt-2 flex flex-wrap gap-1">{r.skills.map((sk) => <span key={sk} className="chip bg-slate-700/40 text-slate-300">{sk}</span>)}</div>
              </button>
            ))}
          </div>
          <div>
            <label className="label">Assign to channel</label>
            <select className="input" value={channelId} onChange={(e) => setChannelId(e.target.value)}>
              <option value="">All channels</option>
              {s.channels.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          {full && <p className="text-xs text-amber-300">All desks are taken. Buy an Office Expansion upgrade to hire more agents.</p>}
        </div>
      </div>
    </Modal>
  );
}

export function NewChannelModal() {
  const s = useGame();
  const open = s.modal === 'newChannel';
  const [f, setF] = useState({ name: '', niche: '', audience: '', emoji: '📺', color: '#22d3ee', rpm: 5, perWeek: 2 });
  useEffect(() => { if (open) setF({ name: '', niche: '', audience: '', emoji: '📺', color: '#22d3ee', rpm: 5, perWeek: 2 }); }, [open]);
  const submit = () => {
    if (!f.name.trim() || !f.niche.trim()) return;
    s.addChannel({ name: f.name.trim(), niche: f.niche.trim(), audience: f.audience.trim() || 'General audience', logo: { emoji: f.emoji, color: f.color }, rpm: f.rpm, uploadsPerWeek: f.perWeek, uploadSchedule: `${f.perWeek}x / week` });
    s.closeModal();
    s.toast(`Channel "${f.name}" created (local simulation).`, 'success');
  };
  return (
    <Modal open={open} onClose={s.closeModal} title="📺 Launch New Channel" footer={<><button className="btn-ghost" onClick={s.closeModal}>Cancel</button><button className="btn-primary" disabled={!f.name.trim() || !f.niche.trim()} onClick={submit}>Create channel</button></>}>
      <div className="grid gap-3">
        <div className="grid grid-cols-[1fr_80px_80px] gap-2">
          <div><label className="label">Channel name</label><input className="input" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} placeholder="e.g. Money Mechanics" /></div>
          <div><label className="label">Logo</label><input className="input text-center" value={f.emoji} maxLength={4} onChange={(e) => setF({ ...f, emoji: e.target.value })} /></div>
          <div><label className="label">Color</label><input className="input h-[38px] p-1" type="color" value={f.color} onChange={(e) => setF({ ...f, color: e.target.value })} /></div>
        </div>
        <div><label className="label">Niche</label><input className="input" value={f.niche} onChange={(e) => setF({ ...f, niche: e.target.value })} placeholder="e.g. Personal finance explainers" /></div>
        <div><label className="label">Target audience</label><input className="input" value={f.audience} onChange={(e) => setF({ ...f, audience: e.target.value })} placeholder="e.g. 22–40, US/EU, beginner investors" /></div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">Expected RPM (€)</label><input className="input" type="number" step={0.5} min={0.5} value={f.rpm} onChange={(e) => setF({ ...f, rpm: +e.target.value })} /></div>
          <div><label className="label">Uploads per week</label><input className="input" type="number" min={1} max={14} value={f.perWeek} onChange={(e) => setF({ ...f, perWeek: Math.max(1, +e.target.value) })} /></div>
        </div>
        <p className="text-xs text-slate-500">This creates a simulated channel. Linking a real YouTube channel requires the YouTube Data API (see Settings).</p>
      </div>
    </Modal>
  );
}

export function AllModals() {
  return (<><NewVideoModal /><AssignTaskModal /><HireAgentModal /><NewChannelModal /></>);
}

export { Avatar };
