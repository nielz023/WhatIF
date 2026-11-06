import { useEffect, useState } from 'react';
import { Dices } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Avatar, Modal } from '../ui';
import type { Priority } from '../../types';
import { roleById } from '../../modules/agents/roles';
import { DEPARTMENTS } from '../../modules/departments/departments';
import { suggestTopic } from '../../modules/workflows/deliverables';

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
              <button key={c.id} onClick={() => { setChannelId(c.id); const t = suggestTopic(c.niche); setTopic(t); setTitle(t); }} className={`flex items-center gap-2 rounded-xl border p-2.5 text-left text-sm transition ${channelId === c.id ? 'border-sky-400 bg-sky-500/15' : 'border-hq-line hover:border-slate-500'}`}>
                <span className="flex h-8 w-8 items-center justify-center rounded-lg text-lg" style={{ background: `${c.logo.color}33` }}>{c.logo.emoji}</span>
                <span><span className="block font-semibold text-white">{c.name}</span><span className="text-[13px] text-slate-400">{c.niche}</span></span>
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
            <label className="label">Deadline (dagen)</label>
            <input className="input" type="number" min={1} max={30} value={deadline} onChange={(e) => setDeadline(Math.max(1, +e.target.value))} />
          </div>
        </div>
        <p className="rounded-xl bg-sky-500/10 p-3 text-[13px] text-sky-200">The project enters the pipeline at <b>Research</b> and flows through all 11 stages. You'll be asked to approve it at <b>CEO Approval</b> and to confirm before <b>Publishing</b>.</p>
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

// Aannemen (met saldo en kosten) is weg: dat hoorde bij het spel met speelgeld (niels 2026-11-06).

export function NewChannelModal() {
  const s = useGame();
  const open = s.modal === 'newChannel';
  const [f, setF] = useState({ name: '', niche: '', audience: '', emoji: '📺', color: '#22d3ee', perWeek: 2 });
  useEffect(() => { if (open) setF({ name: '', niche: '', audience: '', emoji: '📺', color: '#22d3ee', perWeek: 2 }); }, [open]);
  const submit = () => {
    if (!f.name.trim() || !f.niche.trim()) return;
    // geen verwachte RPM meer: geld speelt in het kantoor geen rol
    s.addChannel({ name: f.name.trim(), niche: f.niche.trim(), audience: f.audience.trim() || 'Algemeen publiek', logo: { emoji: f.emoji, color: f.color }, rpm: 0, uploadsPerWeek: f.perWeek, uploadSchedule: `${f.perWeek}x / week` });
    s.closeModal();
    s.toast(`Kanaal "${f.name}" gemaakt.`, 'success');
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
          <div><label className="label">Uploads per week</label><input className="input" type="number" min={1} max={14} value={f.perWeek} onChange={(e) => setF({ ...f, perWeek: Math.max(1, +e.target.value) })} /></div>
        </div>
        <p className="text-[13px] text-slate-500">This creates a simulated channel. Linking a real YouTube channel requires the YouTube Data API (see Settings).</p>
      </div>
    </Modal>
  );
}

export function AllModals() {
  return (<><NewVideoModal /><AssignTaskModal /><NewChannelModal /></>);
}

export { Avatar };
