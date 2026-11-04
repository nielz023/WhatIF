import type { Agent, RoleDef, RoleId, DepartmentId } from '../../types';
import { uid, pick, rand } from '../../lib/util';

export const ROLES: RoleDef[] = [
  { id: 'researcher', title: 'Researcher', department: 'research', description: 'Verzamelt trends, zoekvolume en vragen van kijkers.', skills: ['Data Mining', 'Trend Spotting', 'Accuracy'], baseSalary: 38, hireCost: 400 },
  { id: 'niche_analyst', title: 'Niche Analyst', department: 'research', description: 'Beoordeelt onderwerpen op RPM, concurrentie en blijvende waarde.', skills: ['Market Sizing', 'RPM Analysis', 'Strategy'], baseSalary: 42, hireCost: 450 },
  { id: 'competitor_analyst', title: 'Competitor Analyst', department: 'research', description: 'Ontleedt uitschieters van kanalen zoals IFOLOGY.', skills: ['Outlier Detection', 'Pattern Analysis', 'Speed'], baseSalary: 40, hireCost: 430 },
  { id: 'topic_finder', title: 'Topic Finder', department: 'research', description: 'Maakt van onderzoek een shortlist van What If-onderwerpen.', skills: ['Curiosity', 'Search Intent', 'Speed'], baseSalary: 36, hireCost: 380 },
  { id: 'idea_generator', title: 'Idea Generator', department: 'creative', description: 'Bedenkt invalshoeken en twists die opvallen.', skills: ['Creativity', 'Formats', 'Speed'], baseSalary: 36, hireCost: 380 },
  { id: 'title_specialist', title: 'Title Specialist', department: 'creative', description: 'Schrijft titels met een getal en nieuwsgierigheid.', skills: ['Copywriting', 'CTR Psychology', 'SEO'], baseSalary: 44, hireCost: 480 },
  { id: 'hook_specialist', title: 'Hook Specialist', department: 'creative', description: 'Maakt de eerste 5 seconden zo spannend mogelijk.', skills: ['Hooks', 'Retention', 'Pacing'], baseSalary: 44, hireCost: 480 },
  { id: 'scriptwriter', title: 'Scriptwriter', department: 'script', description: 'Schrijft het hele script (Engels, regie in het Nederlands).', skills: ['Writing', 'Structure', 'Speed'], baseSalary: 48, hireCost: 520 },
  { id: 'storytelling_expert', title: 'Storytelling Expert', department: 'script', description: 'Zorgt voor escalatie, open vragen en emotie.', skills: ['Narrative', 'Emotion', 'Retention'], baseSalary: 50, hireCost: 560 },
  { id: 'fact_checker', title: 'Fact Checker', department: 'script', description: 'Checkt de “this part is real”-momenten.', skills: ['Accuracy', 'Research', 'Rigor'], baseSalary: 38, hireCost: 400 },
  { id: 'quality_controller', title: 'Quality Controller', department: 'production', description: 'Laatste check op geluid, beeld, tempo en clipping.', skills: ['Attention to Detail', 'Policy', 'Rigor'], baseSalary: 46, hireCost: 500 },
  { id: 'voice_director', title: 'Voice Director', department: 'voice', description: 'Kiest stem en toon per personage in ElevenLabs.', skills: ['Direction', 'Tone', 'Audio'], baseSalary: 44, hireCost: 480 },
  { id: 'voice_generator', title: 'Voice Generator', department: 'voice', description: 'Maakt de voice-overs in ElevenLabs v4.', skills: ['Audio', 'Speed', 'Clarity'], baseSalary: 34, hireCost: 360 },
  { id: 'video_editor', title: 'Video Editor', department: 'production', description: 'Animeert in Blender en monteert de video.', skills: ['Editing', 'Pacing', 'Motion'], baseSalary: 52, hireCost: 600 },
  { id: 'visual_researcher', title: 'Visual Researcher', department: 'production', description: 'Verzorgt sets, props en beeldmateriaal.', skills: ['Sourcing', 'Licensing', 'Speed'], baseSalary: 36, hireCost: 380 },
  { id: 'editing_supervisor', title: 'Editing Supervisor', department: 'production', description: 'Bewaakt de montage en de renderwachtrij.', skills: ['Leadership', 'Editing', 'Rigor'], baseSalary: 56, hireCost: 650 },
  { id: 'thumbnail_designer', title: 'Thumbnail Designer', department: 'thumbnail', description: 'Ontwerpt opvallende, leesbare thumbnails.', skills: ['Design', 'Composition', 'Speed'], baseSalary: 44, hireCost: 480 },
  { id: 'ctr_specialist', title: 'CTR Specialist', department: 'thumbnail', description: 'Test thumbnails en titels op klikken.', skills: ['CTR Psychology', 'Testing', 'Data'], baseSalary: 48, hireCost: 520 },
  { id: 'upload_manager', title: 'Upload Manager', department: 'publishing', description: 'Maakt uploads, planning en eindschermen klaar.', skills: ['Operations', 'Scheduling', 'Accuracy'], baseSalary: 34, hireCost: 360 },
  { id: 'seo_specialist', title: 'SEO Specialist', department: 'publishing', description: 'Schrijft beschrijving, tags en hoofdstukken.', skills: ['SEO', 'Keywords', 'Copywriting'], baseSalary: 40, hireCost: 430 },
  { id: 'social_media_manager', title: 'Social Media Manager', department: 'publishing', description: 'Promoot uploads en shorts.', skills: ['Community', 'Copywriting', 'Timing'], baseSalary: 38, hireCost: 400 },
  { id: 'ceo_agent', title: 'CEO Agent', department: 'ceo', description: 'Bepaalt de koers, bereidt goedkeuringen voor en leidt de crisiskamer.', skills: ['Strategy', 'Leadership', 'Decisions'], baseSalary: 80, hireCost: 1200 },
  { id: 'financial_manager', title: 'Financial Manager', department: 'ceo', description: 'Houdt kosten en opbrengst bij.', skills: ['Finance', 'Forecasting', 'Rigor'], baseSalary: 60, hireCost: 800 },
  { id: 'performance_analyst', title: 'Performance Analyst', department: 'ceo', description: 'Analyseert CTR, kijkduur en kanaaltrends.', skills: ['Analytics', 'Data', 'Insight'], baseSalary: 56, hireCost: 700 },
];

export const roleById = (id: RoleId) => ROLES.find((r) => r.id === id)!;
export const rolesForDept = (d: DepartmentId) => ROLES.filter((r) => r.department === d);

const FIRST = ['Ava', 'Leo', 'Mia', 'Noah', 'Zara', 'Kai', 'Luna', 'Omar', 'Iris', 'Finn', 'Nova', 'Ezra', 'Yuki', 'Ravi', 'Lena', 'Milo', 'Sara', 'Theo', 'Ines', 'Jonas', 'Aria', 'Sami', 'Elio', 'Freya', 'Hugo', 'Nia', 'Otto', 'Pia', 'Rex', 'Vera'];
const LAST = ['Byte', 'Vector', 'Pixel', 'Quill', 'Nimbus', 'Cortex', 'Echo', 'Prism', 'Atlas', 'Vale', 'Sterling', 'Lumen', 'Hart', 'Novak', 'Reyes', 'Kim', 'Okafor', 'Silva', 'Berg', 'Moreau'];
const PERSONALITIES = [
  'Analytisch en rustig, houdt van spreadsheets.',
  'Energieke optimist die elk succesje viert.',
  'Perfectionist, zegt nee tegen haastwerk.',
  'Snel en praktisch, eerst af, dan mooi.',
  'Nieuwsgierige verteller die drie keer “waarom?” vraagt.',
  'Stille expert, post weinig maar altijd raak.',
  'Competitief, vergelijkt alles met de concurrentie.',
  'Teamspeler die graag om feedback vraagt.',
];
const SKIN = ['#f1c7a5', '#d9a07a', '#a86b48', '#7a4a2e', '#f5d6bf', '#c58c64'];
const HAIR = ['#1f1a17', '#4a2f1d', '#b5651d', '#e8c26a', '#2b2b2b', '#7c3aed', '#ef4444', '#94a3b8'];

export function createAgent(role: RoleId, day: number, opts: Partial<Agent> = {}): Agent {
  const def = roleById(role);
  const name = opts.name ?? `${pick(FIRST)} ${pick(LAST)}`;
  const deptColor: Record<DepartmentId, string> = {
    research: '#3b82f6', creative: '#a855f7', script: '#fb923c', voice: '#ec4899',
    production: '#f43f5e', thumbnail: '#f59e0b', publishing: '#22d3ee', ceo: '#facc15',
  };
  const skills: Record<string, number> = {};
  def.skills.forEach((s) => (skills[s] = Math.round(rand(42, 72))));
  return {
    id: uid('ag'),
    name,
    role,
    department: def.department,
    avatar: {
      skin: pick(SKIN),
      hair: pick(HAIR),
      shirt: deptColor[def.department],
      initials: name.split(' ').map((p) => p[0]).join(''),
    },
    personality: pick(PERSONALITIES),
    instructions: `Jij bent de ${def.title} bij Driftmark Studio (3D What If-kanaal). ${def.description} Lever kort en duidelijk werk op en geef het door aan de volgende afdeling.`,
    skills,
    level: 1,
    xp: 0,
    performance: Math.round(rand(60, 80)),
    morale: 80,
    salary: def.baseSalary,
    state: 'idle',
    currentTaskId: null,
    taskHistory: [],
    channelIds: [],
    hiredDay: day,
    completed: 0,
    ...opts,
  };
}

export const agentPower = (a: Agent) => {
  const vals = Object.values(a.skills);
  const avg = vals.reduce((s, v) => s + v, 0) / Math.max(1, vals.length);
  return avg * (0.85 + a.level * 0.05) * (0.7 + a.morale / 333);
};

export const xpForLevel = (lvl: number) => 100 + (lvl - 1) * 80;
