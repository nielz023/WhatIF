// ───────────────────────────────────────────────────────────────
// DEMO DATA — everything in here is fictional seed data for the
// local simulation. It is clearly flagged in the UI as demo data.
// ───────────────────────────────────────────────────────────────
import type { Agent, Channel, DailyStat, LedgerEntry, Project, RoleId, Task, ThreadPost, Video } from '../types';
import { createAgent } from '../modules/agents/roles';
import { ACHIEVEMENTS, UPGRADES, generateMissions } from '../modules/gameplay/progression';
import { PIPELINE } from '../modules/workflows/pipeline';
import { simulateDeliverable } from '../modules/workflows/deliverables';
import { DEFAULT_SETTINGS, type GameData } from '../store/state';
import { TICKS_PER_DAY, uid, rand, randInt, realTick, dayOf } from '../lib/util';

// Geschiedenis vanaf 14 okt 2026 tot vandaag (echte datum).
export const SEED_DAYS = dayOf(realTick());

// Rollen van de Driftmark-studio. De instructies komen uit de echte werkwijze van het project.
const RULES: Partial<Record<RoleId, string>> = {
  hook_specialist: 'Spannendste beeld binnen 5 s, eerste woord op frame 1. Geen uitleg in de eerste minuut. Thumbnail + titel = wat de eerste seconden tonen.',
  scriptwriter: 'Scripts in het Engels, regie in het Nederlands. Spreek de kijker aan met "you". Escalatie: leuk, indrukwekkend, gevaarlijk, schokkend. Elke 60-90 s een nieuw probleem, twist aan het eind, NIET verwijzen naar de volgende video.',
  fact_checker: 'Elke video heeft "this part is real"-momenten met echte wetenschap. Controleer die.',
  voice_generator: 'ElevenLabs v4. Verteller zfc8CJQpe8Kqyl0vvCzo. Genereer op ÉÉN plek, nooit dubbel. Voice-over altijd centraal in de mix.',
  video_editor: 'Blender, glans-look, 30 fps. Shots 3-4 s, max 6 s. -14 LUFS. Eindrender op niels\' pc.',
  quality_controller: 'Kwaliteitscheck: HUD strak, props niet in elkaar, niets zweeft, sets dicht, geen clipping, bestek goed vast, rennen met gebogen knieën.',
  thumbnail_designer: 'Thumbnail toont het beeld uit de eerste seconden. Getal in de titel werkt (2x, 10x).',
  seo_specialist: 'Korte tags met echt zoekvolume; lange titelzinnen scoren 0.',
  upload_manager: 'Shorts koppelen aan de lange video via "Gerelateerde video". Categorie Film & Animation.',
};

const STARTER_ROLES: [RoleId, string][] = [
  ['researcher', 'Ava Quill'], ['topic_finder', 'Kai Vector'], ['niche_analyst', 'Iris Novak'],
  ['title_specialist', 'Luna Prism'], ['hook_specialist', 'Milo Hart'],
  ['scriptwriter', 'Theo Lumen'], ['fact_checker', 'Ines Berg'],
  ['voice_generator', 'Ezra Echo'],
  ['video_editor', 'Zara Pixel'], ['quality_controller', 'Omar Rigor'],
  ['thumbnail_designer', 'Nova Silva'],
  ['upload_manager', 'Finn Atlas'], ['seo_specialist', 'Yuki Kim'],
  ['ceo_agent', 'Sterling Cortex'], ['performance_analyst', 'Ravi Okafor'],
];

export function createSeed(): GameData {
  const now = realTick();
  const agents: Agent[] = STARTER_ROLES.map(([role, name], i) =>
    createAgent(role, 0, { name, level: 1 + (i % 3), xp: randInt(0, 60), ...(RULES[role] ? { instructions: `Driftmark-studio. ${RULES[role]}` } : {}) }),
  );

  const channels: Channel[] = [
    { id: 'ch_history', name: 'Driftmark', logo: { emoji: '🌀', color: '#f97316' }, niche: '3D What If animations', audience: '13–34 global, curious about superpowers & science', subscribers: 13, views: 0, revenue: 0, rpm: 4.5, uploadSchedule: '1x / week', uploadsPerWeek: 1, monetized: false, ctrBoost: 0, retentionBoost: 0, createdTick: 0, isDemo: true },
    { id: 'ch_science', name: 'Driftmark Shorts', logo: { emoji: '⚡', color: '#8b5cf6' }, niche: '3D What If shorts', audience: 'Shorts feed, 13–24', subscribers: 0, views: 0, revenue: 0, rpm: 0.1, uploadSchedule: '7x / week', uploadsPerWeek: 7, monetized: false, ctrBoost: 0, retentionBoost: 0, createdTick: 0, isDemo: true },
  ];

  // Demo published videos & stats history
  const videos: Video[] = [];
  const stats: DailyStat[] = [];
  const ledger: LedgerEntry[] = [];
  const demoTitles: [string, string, number][] = [
    // dag 0 = 14 okt 2026
    ['ch_science', 'Teaser-short SH1: 10x sneller per dag', 13],
    ['ch_science', 'Teaser-short SH2: tijd stopt', 13],
    ['ch_history', 'What IF You Got 2x STRONGER Every Day for 40 Days?', 14],
    ['ch_science', 'Short uit video 1: Titan', 15],
    ['ch_science', 'Short uit video 1: Sneeze', 16],
    ['ch_science', 'Teaser-short SH4: word wat je aanraakt', 17],
  ];
  demoTitles.forEach(([ch, title, day]) => {
    videos.push({ id: uid('vid'), projectId: 'demo', channelId: ch, title, publishedTick: day * TICKS_PER_DAY + 15, quality: randInt(55, 78), ctr: +rand(3.6, 6.2).toFixed(1), avd: +rand(34, 48).toFixed(1), views: 0, revenue: 0, likes: 0 });
  });
  for (let d = 0; d < SEED_DAYS; d++) {
    channels.forEach((c) => {
      let views = 0;
      videos.filter((v) => v.channelId === c.id && v.publishedTick / TICKS_PER_DAY <= d).forEach((v) => {
        const age = d - Math.floor(v.publishedTick / TICKS_PER_DAY);
        const vv = Math.round((v.quality * 28) * Math.exp(-age / 9) * rand(0.8, 1.2) + 40);
        v.views += vv; v.likes += Math.round(vv * 0.035); views += vv;
      });
      views += randInt(20, 60); // back catalogue
      const subs = Math.round(views * rand(0.006, 0.011));
      c.subscribers += subs; c.views += views;
      stats.push({ day: d, channelId: c.id, views, subs, revenue: 0, ctr: +rand(3.8, 5.8).toFixed(2), avd: +rand(35, 47).toFixed(1) });
    });
    ledger.push({ id: uid('le'), day: d, channelId: null, category: 'Salaries', amount: -Math.round(agents.reduce((s, a) => s + a.salary, 0) * 0.08), note: 'Daily agent compute & salaries (demo)' });
    if (d % 30 === 0) {
      ledger.push({ id: uid('le'), day: d, channelId: null, category: 'AI Subscriptions', amount: -120, note: 'LLM & voice plans (demo)' });
      ledger.push({ id: uid('le'), day: d, channelId: null, category: 'Software', amount: -65, note: 'Editing suite & stock library (demo)' });
    }
  }
  videos.forEach((v) => ledger.push({ id: uid('le'), day: Math.floor(v.publishedTick / TICKS_PER_DAY), channelId: v.channelId, category: 'Production', amount: -124, note: `Production: ${v.title} (demo)` }));
  ledger.push({ id: uid('le'), day: 10, channelId: 'ch_history', category: 'Freelancers', amount: -180, note: 'Freelance motion designer (demo)' });

  // Active demo projects at different stages
  const tasks: Task[] = [];
  const projects: Project[] = [];
  const mkProject = (ch: string, title: string, stageIdx: number): Project => {
    const p: Project = {
      id: uid('pr'), title, topic: title, channelId: ch, stage: PIPELINE[stageIdx].id, status: 'Active',
      createdTick: now - 40, deadlineTick: now + TICKS_PER_DAY * 5, priority: 'Medium', taskIds: [], stageQuality: {}, rejections: 0, cost: 0,
      history: [{ tick: now - 40, text: 'Project created (demo)' }],
    };
    for (let i = 0; i < stageIdx; i++) {
      const s = PIPELINE[i];
      const q = randInt(58, 82);
      p.stageQuality[s.id] = q;
      p.cost += s.cost;
      const agent = agents.find((a) => s.roles.includes(a.role));
      const t: Task = {
        id: uid('tk'), title: `${s.label}: ${title}`, description: `Produce the ${s.deliverableName}.`, agentId: agent?.id ?? null,
        projectId: p.id, stage: s.id, kind: 'pipeline', priority: 'Medium', status: 'Completed', progress: 100,
        createdTick: now - 40 + i * 4, deadlineTick: now, dependencies: [], comments: [], quality: q, revision: 0,
        documents: [{ id: uid('doc'), name: s.deliverableName, kind: s.deliverable, content: simulateDeliverable(s.id, p, channels.find((c) => c.id === ch), q) }],
        result: `${s.deliverableName} delivered.`,
      };
      tasks.push(t); p.taskIds.push(t.id);
      agent?.taskHistory.push(t.id);
    }
    projects.push(p);
    return p;
  };
  mkProject('ch_history', 'What IF There Were NO RULES?', 6);
  mkProject('ch_science', 'Shorts uit video 3 (No Rules)', 3);
  mkProject('ch_history', 'Video 4: kies uit de ideeënlijst', 1);

  const by = (role: RoleId) => agents.find((a) => a.role === role)!.id;
  const posts: ThreadPost[] = [
    { id: uid('po'), authorId: by('ceo_agent'), department: 'ceo', kind: 'update', content: 'Goedemorgen team ☀️ Focus: video 3 (No Rules) afmaken. Spannendste beeld binnen 5 seconden, geen uitleg in de eerste minuut.', tick: now - 30, likes: [by('hook_specialist'), by('scriptwriter')], comments: [{ id: uid('c'), authorId: by('hook_specialist'), text: 'On it — new hook framework drops today.', tick: now - 28 }], isDemo: true },
    { id: uid('po'), authorId: by('performance_analyst'), department: 'ceo', kind: 'report', content: 'Rapport: 10,4K weergaven in 28 dagen, +16 abonnees. Shorts doen elk 1,1-1,5K, maar sturen weinig door naar de lange video.', tick: now - 20, likes: [by('ceo_agent')], comments: [], attachment: { title: 'Retentie video 1', body: 'Gem. kijkduur 6:40 (26,3%) · ~2/3 haakt af in de eerste 30-60 s · daarna vlak 25-35%' }, isDemo: true },
    { id: uid('po'), authorId: by('video_editor'), department: 'production', kind: 'update', content: 'Renderwachtrij op de pc: scène 1 en 3-9 van No Rules staan erin. Nu bezig met scène 10, de stroom valt uit 🔦', tick: now - 12, likes: [], comments: [], isDemo: true },
    { id: uid('po'), authorId: by('researcher'), department: 'research', kind: 'question', content: 'Wie checkt de "this part is real"-momenten van No Rules? Er zijn er 8.', tick: now - 8, likes: [by('fact_checker')], comments: [{ id: uid('c'), authorId: by('fact_checker'), text: 'Doe ik, ze staan in bijlage D van het script.', tick: now - 7 }], isDemo: true },
    { id: uid('po'), authorId: by('thumbnail_designer'), department: 'thumbnail', kind: 'celebration', content: 'Video 2 is af en niels vindt hem echt top 🎉 7 shorts staan klaar voor upload.', tick: now - 4, likes: [by('ceo_agent'), by('upload_manager'), by('title_specialist')], comments: [], isDemo: true },
  ];

  return {
    version: 1,
    tick: now,
    company: { name: 'Driftmark Studio', level: 2, xp: 120, balance: 6000, reputation: 32, baseSlots: 18 },
    agents, tasks, projects, videos, channels, stats, ledger, posts,
    notifications: [{ id: uid('n'), tick: now, text: 'Welkom in Driftmark HQ! Het hoofdscherm toont de echte stand; het kantoor is een simulatie die met jouw kanaal speelt.', kind: 'info', read: false }],
    achievements: ACHIEVEMENTS.map((a) => ({ ...a })),
    missions: generateMissions(),
    missionDay: SEED_DAYS,
    upgrades: UPGRADES.map((u) => ({ ...u })),
    warCases: [],
    modifiers: { speedBoost: 0, speedBoostUntil: 0 },
    settings: { ...DEFAULT_SETTINGS },
    demoMode: true,
  };
}
