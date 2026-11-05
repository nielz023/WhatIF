import { useEffect, useState } from 'react';
import { Sparkles, GraduationCap, ArrowUpCircle, ClipboardList, UserMinus, Share2 } from 'lucide-react';
import { useGame, MAX_LEVEL, maxUpgradeCost } from '../../store/useGame';
import { Avatar, Drawer, Progress, StateDot, StatusBadge } from '../ui';
import { roleById, xpForLevel } from '../../modules/agents/roles';
import { deptById } from '../../modules/departments/departments';
import { getLLM } from '../../services/adapters';
import { upgradeLevel, SALARY_FACTOR } from '../../modules/tasks/engine';
import { eur } from '../../lib/util';
import type { GameData } from '../../store/state';

export default function AgentDrawer() {
  const s = useGame();
  const a = s.agents.find((x) => x.id === s.selectedAgentId);
  const [instr, setInstr] = useState('');
  const [prompt, setPrompt] = useState('');
  const [out, setOut] = useState('');
  const [busy, setBusy] = useState(false);
  useEffect(() => { if (a) { setInstr(a.instructions); setOut(''); setPrompt(''); } }, [a?.id]); // eslint-disable-line
  if (!a) return <Drawer open={false} onClose={() => s.selectAgent(null)}>{null}</Drawer>;

  const role = roleById(a.role);
  const dept = deptById(a.department);
  const current = s.tasks.find((t) => t.id === a.currentTaskId);
  const history = a.taskHistory.map((id) => s.tasks.find((t) => t.id === id)).filter(Boolean).reverse().slice(0, 12);
  const lab = upgradeLevel(s as unknown as GameData, 'training_lab');
  const trainCost = Math.round(120 * a.level * (1 - lab * 0.25));
  const llm = getLLM(s.settings);

  const generate = async () => {
    setBusy(true); setOut('');
    try {
      const sys = `${a.instructions}\nPersonality: ${a.personality}\nCompany: Driftmark Studio (3D What If YouTube channel). Channels: ${s.channels.map((c) => `${c.name} (${c.niche})`).join(', ')}.`;
      setOut(await llm.generate(sys, prompt || `Geef me je beste oplevering als ${role.title.toLowerCase()} voor onze volgende video.`));
    } catch (e) {
      setOut(`⚠️ ${(e as Error).message}`);
    } finally { setBusy(false); }
  };

  return (
    <Drawer open onClose={() => s.selectAgent(null)} title="Agent profile" width={540}>
      <div className="flex items-center gap-4">
        <Avatar agent={a} size={68} ring />
        <div className="min-w-0 flex-1">
          <div className="font-display text-xl font-bold text-white">{a.name}</div>
          <div className="text-sm text-slate-400">{role.title} · <span style={{ color: dept.color }}>{dept.icon} {dept.short}</span></div>
          <div className="mt-1 flex items-center gap-3"><StateDot state={a.state} /><span className="text-xs text-slate-400">{eur(a.salary * SALARY_FACTOR, 2)}/day</span></div>
        </div>
        <div className="text-center">
          <div className="font-display text-2xl font-bold text-white">{a.level}</div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500">Level</div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
        <div className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">XP</div><div className="mb-1 font-semibold text-white">{Math.round(a.xp)}/{xpForLevel(a.level)}</div><Progress value={(a.xp / xpForLevel(a.level)) * 100} h={4} color="#a855f7" /></div>
        <div className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">Performance</div><div className="mb-1 font-semibold text-white">{a.performance}</div><Progress value={a.performance} h={4} color="#22c55e" /></div>
        <div className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">Morale</div><div className="mb-1 font-semibold text-white">{Math.round(a.morale)}</div><Progress value={a.morale} h={4} color="#f59e0b" /></div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button className="btn-ghost text-xs" onClick={() => s.openModal('assignTask', { agentId: a.id })}><ClipboardList size={14} />Assign task</button>
        <button className="btn-ghost text-xs" onClick={() => s.askConfirm({ title: `Upgrade ${a.name}?`, body: `${a.name} naar niveau ${a.level + 1} voor ${eur(250 * a.level)}. Alle vaardigheden +3; dagkosten iets hoger.`, confirmLabel: 'Upgrade', onConfirm: () => s.promoteAgent(a.id) && s.toast(`${a.name} upgraded!`, 'success') })}><ArrowUpCircle size={14} />Upgrade ({eur(250 * a.level)})</button>
        <button className="btn-primary text-xs" disabled={a.level >= MAX_LEVEL && Object.values(a.skills).every((v) => v >= 100)} onClick={() => s.askConfirm({ title: `${a.name} maximaal upgraden?`, body: `In één keer naar niveau ${MAX_LEVEL} met alle vaardigheden op 100, voor ${eur(maxUpgradeCost(a))} spelgeld.`, confirmLabel: 'Max upgraden', onConfirm: () => { s.maxUpgradeAgent(a.id); } })}><Sparkles size={14} />Max upgraden ({eur(maxUpgradeCost(a))})</button>
        <button className="btn-danger ml-auto text-xs" onClick={() => s.askConfirm({ title: `Let ${a.name} go?`, body: 'This agent will leave the company permanently. Their open tasks return to the queue. This cannot be undone.', confirmLabel: 'Remove agent', danger: true, onConfirm: () => s.fireAgent(a.id) })}><UserMinus size={14} />Remove</button>
      </div>

      <Section title="About">
        <p className="text-sm text-slate-300">{role.description}</p>
        <p className="mt-1 text-sm italic text-slate-400">“{a.personality}”</p>
      </Section>

      <Section title={`Skills · training ${eur(trainCost)} each`}>
        <div className="space-y-2">
          {Object.entries(a.skills).map(([k, v]) => (
            <div key={k} className="flex items-center gap-3">
              <div className="w-32 text-xs text-slate-300">{k}</div>
              <div className="flex-1"><Progress value={v} h={5} color={dept.color} /></div>
              <div className="w-7 text-right text-xs text-slate-400">{v}</div>
              <button className="rounded-lg border border-hq-line p-1 text-purple-300 hover:bg-purple-500/10 disabled:opacity-30" disabled={a.state === 'training' || !!a.currentTaskId || v >= 100} title={a.currentTaskId ? 'Busy with a task' : `Train ${k}`} onClick={() => s.trainAgent(a.id, k)}><GraduationCap size={14} /></button>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Instructions (system prompt)">
        <textarea className="input min-h-[90px] text-xs" value={instr} onChange={(e) => setInstr(e.target.value)} />
        <button className="btn-ghost mt-2 text-xs" disabled={instr === a.instructions} onClick={() => { s.updateAgent(a.id, { instructions: instr }); s.toast('Instructions saved.', 'success'); }}>Save instructions</button>
      </Section>

      <Section title="Channel assignment">
        <div className="flex flex-wrap gap-2">
          <button onClick={() => s.updateAgent(a.id, { channelIds: [] })} className={`chip px-3 py-1 ring-1 ${a.channelIds.length === 0 ? 'bg-indigo-500/20 text-white ring-indigo-400/50' : 'text-slate-400 ring-slate-600'}`}>All channels</button>
          {s.channels.map((c) => {
            const on = a.channelIds.includes(c.id);
            return <button key={c.id} onClick={() => s.updateAgent(a.id, { channelIds: on ? a.channelIds.filter((x) => x !== c.id) : [...a.channelIds, c.id] })} className={`chip px-3 py-1 ring-1 ${on ? 'bg-indigo-500/20 text-white ring-indigo-400/50' : 'text-slate-400 ring-slate-600'}`}>{c.logo.emoji} {c.name}</button>;
          })}
        </div>
      </Section>

      <Section title={<span className="flex items-center gap-2"><Sparkles size={13} />Work session · {llm.name}</span>}>
        <textarea className="input min-h-[60px] text-xs" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder={`Vraag ${a.name.split(' ')[0]} om iets, bv. "10 titelideeën voor de video over teleporteren"`} />
        <div className="mt-2 flex gap-2">
          <button className="btn-primary text-xs" onClick={generate} disabled={busy}>{busy ? 'Working…' : 'Generate'}</button>
          {out && !out.startsWith('⚠️') && <button className="btn-ghost text-xs" onClick={() => { s.createPost(`Report from ${a.name}:`, { title: `${role.title} deliverable`, body: out.slice(0, 1200) }); s.toast('Shared to internal Threads.', 'success'); }}><Share2 size={13} />Share to Threads</button>}
        </div>
        {llm.status() !== 'connected' && <p className="mt-2 text-[11px] text-slate-500">No AI model connected — output is simulated. Add a Claude or OpenAI key in Settings for real results.</p>}
        {out && <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-black/40 p-3 text-[11px] text-slate-200">{out}</pre>}
      </Section>

      <Section title="Current task">
        {current ? <div className="flex items-center justify-between gap-2 text-sm"><span className="text-white">{current.title}</span><StatusBadge status={current.status} /></div> : <div className="text-sm text-slate-500">{a.state === 'training' ? 'In training.' : 'Idle — waiting for work.'}</div>}
      </Section>

      <Section title={`Takengeschiedenis · ${a.completed} afgerond`}>
        <div className="space-y-1.5">
          {history.length === 0 && <div className="text-sm text-slate-500">No tasks yet.</div>}
          {history.map((t) => t && (
            <div key={t.id} className="flex items-center justify-between gap-2 rounded-lg bg-white/[.03] px-3 py-1.5 text-xs">
              <span className="truncate text-slate-300">{t.title}</span>
              <span className="flex shrink-0 items-center gap-2">{t.quality != null && <span className="text-slate-400">Q{t.quality}</span>}<StatusBadge status={t.status} /></span>
            </div>
          ))}
        </div>
      </Section>
    </Drawer>
  );
}

function Section({ title, children }: { title: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="mt-5">
      <div className="label">{title}</div>
      {children}
    </div>
  );
}
