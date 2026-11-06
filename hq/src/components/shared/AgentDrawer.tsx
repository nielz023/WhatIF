import { useEffect, useState } from 'react';
import { Sparkles, ClipboardList, Share2 } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Avatar, Drawer, Progress, StateDot, StatusBadge } from '../ui';
import { roleById } from '../../modules/agents/roles';
import { deptById } from '../../modules/departments/departments';
import { getLLM } from '../../services/adapters';

/** Vaardigheden in het Nederlands (de namen in de rollen zijn Engels). */
const SKILL_NL: Record<string, string> = {
  'Data Mining': 'Data zoeken', 'Trend Spotting': 'Trends zien', Accuracy: 'Nauwkeurigheid', Speed: 'Snelheid', Curiosity: 'Nieuwsgierigheid',
  'Search Intent': 'Zoekgedrag', Creativity: 'Creativiteit', Formats: 'Formats', Copywriting: 'Tekstschrijven', 'CTR Psychology': 'Klikpsychologie',
  SEO: 'SEO', Hooks: 'Hooks', Retention: 'Kijkers vasthouden', Pacing: 'Tempo', Writing: 'Schrijven', Structure: 'Opbouw', Narrative: 'Verhaal',
  Emotion: 'Emotie', Research: 'Onderzoek', Rigor: 'Grondigheid', 'Attention to Detail': 'Oog voor detail', Policy: 'Richtlijnen', Direction: 'Regie',
  Tone: 'Toon', Audio: 'Geluid', Clarity: 'Helderheid', Editing: 'Montage', Motion: 'Beweging', Sourcing: 'Materiaal zoeken', Licensing: 'Rechten',
  Leadership: 'Leiding geven', Design: 'Ontwerp', Composition: 'Compositie', Testing: 'Testen', Data: 'Data', Operations: 'Planning en uitvoering',
  Scheduling: 'Inplannen', Keywords: 'Zoekwoorden', Community: 'Community', Timing: 'Timing', Strategy: 'Strategie', Decisions: 'Beslissen',
  Analytics: 'Statistieken', Insight: 'Inzicht', 'Outlier Detection': 'Uitschieters vinden', 'Pattern Analysis': 'Patronen zien', 'Market Sizing': 'Marktgrootte',
};

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

  // Geen salaris, niveau, XP, upgrades, training of ontslaan meer: het kantoor is geen spel (niels 2026-11-06).
  return (
    <Drawer open onClose={() => s.selectAgent(null)} title="Teamlid" width={540}>
      <div className="flex items-center gap-4">
        <Avatar agent={a} size={68} ring />
        <div className="min-w-0 flex-1">
          <div className="font-display text-xl font-bold text-white">{a.name}</div>
          <div className="text-sm text-slate-400">{role.title} · <span style={{ color: dept.color }}>{dept.icon} {dept.short}</span></div>
          <div className="mt-1 flex items-center gap-3"><StateDot state={a.state} /></div>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-[13px]">
        <div className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">Performance</div><div className="mb-1 font-semibold text-white">{a.performance}</div><Progress value={a.performance} h={4} color="#22c55e" /></div>
        <div className="rounded-xl bg-white/[.03] p-2.5"><div className="text-slate-500">Morale</div><div className="mb-1 font-semibold text-white">{Math.round(a.morale)}</div><Progress value={a.morale} h={4} color="#f59e0b" /></div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        <button className="btn-ghost text-[13px]" onClick={() => s.openModal('assignTask', { agentId: a.id })}><ClipboardList size={14} />Taak geven</button>
      </div>

      <Section title="About">
        <p className="text-sm text-slate-300">{role.description}</p>
        <p className="mt-1 text-sm italic text-slate-400">“{a.personality}”</p>
      </Section>

      <Section title="Vaardigheden">
        <div className="space-y-2">
          {Object.entries(a.skills).map(([k, v]) => (
            <div key={k} className="flex items-center gap-3">
              <div className="w-36 text-[13px] text-slate-300">{SKILL_NL[k] ?? k}</div>
              <div className="flex-1"><Progress value={v} h={5} color={dept.color} /></div>
              <div className="w-7 text-right text-[13px] text-slate-400">{v}</div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Instructions (system prompt)">
        <textarea className="input min-h-[90px] text-[13px]" value={instr} onChange={(e) => setInstr(e.target.value)} />
        <button className="btn-ghost mt-2 text-[13px]" disabled={instr === a.instructions} onClick={() => { s.updateAgent(a.id, { instructions: instr }); s.toast('Instructions saved.', 'success'); }}>Save instructions</button>
      </Section>

      <Section title="Channel assignment">
        <div className="flex flex-wrap gap-2">
          <button onClick={() => s.updateAgent(a.id, { channelIds: [] })} className={`chip px-3 py-1 ring-1 ${a.channelIds.length === 0 ? 'bg-sky-500/20 text-white ring-sky-400/50' : 'text-slate-400 ring-slate-600'}`}>All channels</button>
          {s.channels.map((c) => {
            const on = a.channelIds.includes(c.id);
            return <button key={c.id} onClick={() => s.updateAgent(a.id, { channelIds: on ? a.channelIds.filter((x) => x !== c.id) : [...a.channelIds, c.id] })} className={`chip px-3 py-1 ring-1 ${on ? 'bg-sky-500/20 text-white ring-sky-400/50' : 'text-slate-400 ring-slate-600'}`}>{c.logo.emoji} {c.name}</button>;
          })}
        </div>
      </Section>

      <Section title={<span className="flex items-center gap-2"><Sparkles size={13} />Werksessie · {llm.name}</span>}>
        <textarea className="input min-h-[60px] text-[13px]" value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder={`Vraag ${a.name.split(' ')[0]} om iets, bv. "10 titelideeën voor de video over teleporteren"`} />
        <div className="mt-2 flex gap-2">
          <button className="btn-primary text-[13px]" onClick={generate} disabled={busy}>{busy ? 'Bezig…' : 'Maken'}</button>
          {out && !out.startsWith('⚠️') && <button className="btn-ghost text-[13px]" onClick={() => { s.createPost(`Verslag van ${a.name}:`, { title: `${role.title}: oplevering`, body: out.slice(0, 1200) }); s.toast('Gedeeld in Berichten.', 'success'); }}><Share2 size={13} />Delen in Berichten</button>}
        </div>
        {llm.status() !== 'connected' && <p className="mt-2 text-[13px] text-slate-500">Geen AI-model gekoppeld, de uitvoer is gesimuleerd. Echte opdrachten lopen via Driftmark HQ.</p>}
        {out && <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-black/40 p-3 text-[13px] text-slate-200">{out}</pre>}
      </Section>

      <Section title="Current task">
        {current ? <div className="flex items-center justify-between gap-2 text-sm"><span className="text-white">{current.title}</span><StatusBadge status={current.status} /></div> : <div className="text-sm text-slate-500">{a.state === 'training' ? 'In training.' : 'Idle — waiting for work.'}</div>}
      </Section>

      <Section title={`Takengeschiedenis · ${a.completed} afgerond`}>
        <div className="space-y-1.5">
          {history.length === 0 && <div className="text-sm text-slate-500">No tasks yet.</div>}
          {history.map((t) => t && (
            <div key={t.id} className="flex items-center justify-between gap-2 rounded-lg bg-white/[.03] px-3 py-1.5 text-[13px]">
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
