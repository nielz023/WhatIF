import { useEffect, useState } from 'react';
import { useGame } from '../../store/useGame';
import { Avatar, Modal } from '../ui';
import type { Priority } from '../../types';
import { roleById } from '../../modules/agents/roles';
import { DEPARTMENTS } from '../../modules/departments/departments';

const PRIORITIES: [Priority, string][] = [['Low', 'Laag'], ['Medium', 'Normaal'], ['High', 'Hoog'], ['Critical', 'Spoed']];

/** Nieuwe video: wordt een echte opdracht voor Claude (via startVideo in de echt-modus). Geen demokanalen of dobbelsteen meer (punt 38). */
export function NewVideoModal() {
  const { modal, closeModal, channels, startVideo, setPage, selectProject } = useGame();
  const [topic, setTopic] = useState('');
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<Priority>('Medium');
  const [deadline, setDeadline] = useState(7);
  const open = modal === 'newVideo';
  useEffect(() => { if (open) { setTopic(''); setTitle(''); } }, [open]);
  const channelId = channels[0]?.id ?? '';
  const submit = () => {
    if (!topic.trim() || !channelId) return;
    const id = startVideo({ channelId, title: (title.trim() || topic.trim()), topic: topic.trim(), priority, deadlineDays: deadline });
    closeModal();
    selectProject(id);
    setPage('projects');
  };
  return (
    <Modal open={open} onClose={closeModal} title="🎬 Nieuwe video starten" footer={<><button className="btn-ghost" onClick={closeModal}>Annuleren</button><button className="btn-primary" onClick={submit} disabled={!topic.trim()}>Start de video</button></>}>
      <div className="grid gap-4">
        <div>
          <label className="label">Onderwerp</label>
          <input className="input" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Bijvoorbeeld: What IF you could fly higher every day?" autoFocus />
        </div>
        <div>
          <label className="label">Werktitel (mag leeg)</label>
          <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Claude bedenkt er anders een" />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Voorrang</label>
            <select className="input" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>{PRIORITIES.map(([p, l]) => <option key={p} value={p}>{l}</option>)}</select>
          </div>
          <div>
            <label className="label">Klaar binnen (dagen)</label>
            <input className="input" type="number" min={1} max={30} value={deadline} onChange={(e) => setDeadline(Math.max(1, +e.target.value))} />
          </div>
        </div>
        <p className="rounded-xl bg-sky-500/10 p-3 text-[13px] text-sky-200">Claude start de video volgens je productiehandboek: verloop, script, stemmen, cast en sets, animatie, montage, thumbnail en uploadtekst. Waar jouw keuze nodig is, komt het bij <b>Wacht op jou</b>. Uploaden doe je zelf.</p>
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
    <Modal open={open} onClose={closeModal} title="📋 Taak geven" footer={<><button className="btn-ghost" onClick={closeModal}>Annuleren</button><button className="btn-primary" onClick={submit} disabled={!title.trim()}>Taak geven</button></>}>
      <div className="grid gap-3">
        <div><label className="label">Wat moet er gebeuren</label><input className="input" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Bijvoorbeeld: analyseer de 10 beste video's van IFOLOGY" /></div>
        <div><label className="label">Uitleg (mag leeg)</label><textarea className="input min-h-[80px]" value={desc} onChange={(e) => setDesc(e.target.value)} /></div>
        <div>
          <label className="label">Teamlid</label>
          <select className="input" value={agentId} onChange={(e) => setAgentId(e.target.value)}>
            {DEPARTMENTS.map((d) => (
              <optgroup key={d.id} label={d.name}>
                {agents.filter((a) => a.department === d.id).map((a) => <option key={a.id} value={a.id}>{a.name}: {roleById(a.role).title}</option>)}
              </optgroup>
            ))}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">Voorrang</label><select className="input" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>{PRIORITIES.map(([p, l]) => <option key={p} value={p}>{l}</option>)}</select></div>
          <div><label className="label">Klaar binnen (dagen)</label><input className="input" type="number" min={1} value={deadline} onChange={(e) => setDeadline(Math.max(1, +e.target.value))} /></div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">Hoort bij video</label><select className="input" value={projectId} onChange={(e) => setProjectId(e.target.value)}><option value="">Geen</option>{projects.filter((p) => p.status !== 'Published' && p.status !== 'Cancelled').map((p) => <option key={p.id} value={p.id}>{p.title}</option>)}</select></div>
          <div><label className="label">Na deze taak</label><select className="input" value={dep} onChange={(e) => setDep(e.target.value)}><option value="">Meteen beginnen</option>{openTasks.map((t) => <option key={t.id} value={t.id}>{t.title.slice(0, 50)}</option>)}</select></div>
        </div>
      </div>
    </Modal>
  );
}

// Aannemen (met saldo en kosten) is weg: dat hoorde bij het spel met speelgeld (niels 2026-11-06).

export function AllModals() {
  return (<><NewVideoModal /><AssignTaskModal /></>);
}

export { Avatar };
