import { useEffect, useState } from 'react';
import { ClipboardList } from 'lucide-react';
import { useGame } from '../../store/useGame';
import { Avatar, Drawer, Progress, StateDot, StatusBadge } from '../ui';
import { roleById } from '../../modules/agents/roles';
import { deptById } from '../../modules/departments/departments';

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
  useEffect(() => { if (a) setInstr(a.instructions); }, [a?.id]); // eslint-disable-line
  if (!a) return <Drawer open={false} onClose={() => s.selectAgent(null)}>{null}</Drawer>;

  const role = roleById(a.role);
  const dept = deptById(a.department);
  const current = s.tasks.find((t) => t.id === a.currentTaskId);
  const history = a.taskHistory.map((id) => s.tasks.find((t) => t.id === id)).filter(Boolean).reverse().slice(0, 12);
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

      <div className="mt-4 flex flex-wrap gap-2">
        <button className="btn-ghost text-[13px]" onClick={() => s.openModal('assignTask', { agentId: a.id })}><ClipboardList size={14} />Taak geven</button>
      </div>

      <Section title="Wat doet dit teamlid">
        <p className="text-sm text-slate-300">{role.description}</p>
      </Section>

      {/* geen werksessie meer: die gaf gesimuleerde uitvoer (niels 2026-11-06) */}
      <Section title="Huidige taak">
        {current ? <div className="flex items-center justify-between gap-2 text-sm"><span className="text-white">{current.title}</span><StatusBadge status={current.status} /></div> : <div className="text-sm text-slate-500">Geen lopende taak.</div>}
      </Section>

      <Section title={`Takengeschiedenis · ${a.completed} afgerond`}>
        <div className="space-y-1.5">
          {history.length === 0 && <div className="text-sm text-slate-500">Nog geen taken.</div>}
          {history.map((t) => t && (
            <div key={t.id} className="flex items-center justify-between gap-2 rounded-lg bg-white/[.03] px-3 py-1.5 text-[13px]">
              <span className="truncate text-slate-300">{t.title}</span>
              <span className="flex shrink-0 items-center gap-2"><StatusBadge status={t.status} /></span>
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
