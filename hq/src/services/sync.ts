/**
 * SYNC: zet de echte stand (status.json) om naar het kantoor.
 * - medewerkers = echte threads (activity[])
 * - projecten = echte video's met hun echte stap
 * - geen nepvoortgang: de simulatie draait niet meer
 * - meldingen + geluid bij nieuws
 */
import type { Agent, DepartmentId, LedgerEntry, Project, RoleId, StageId, Task, ThreadPost, Video } from '../types';
import { createAgent } from '../modules/agents/roles';
import { useGame } from '../store/useGame';
import { realTick, uid } from '../lib/util';
import type { Live, Activity } from './live';
import { prefs } from '../lib/prefs';

const ROLE_BY_KEY: [RegExp, RoleId][] = [
  [/thumbnail|banner|branding/i, 'thumbnail_designer'],
  [/titel|beschrijving|tags/i, 'seo_specialist'],
  [/stem|voice/i, 'voice_generator'],
  [/animeer|render|montage/i, 'video_editor'],
  [/cast|sets|personage|bouw/i, 'visual_researcher'],
  [/short/i, 'social_media_manager'],
  [/script|schrijf|verloop/i, 'scriptwriter'],
  [/idee|bedenk/i, 'idea_generator'],
  [/analyse|kijkers|weergaven|groei/i, 'performance_analyst'],
  [/hq|werkwijze|koppel/i, 'ceo_agent'],
];
const roleFor = (t: string): RoleId => (ROLE_BY_KEY.find(([re]) => re.test(t))?.[1] ?? 'researcher');
const STATE: Record<string, Agent['state']> = { working: 'working', blocked: 'meeting', review_ready: 'meeting', done: 'idle' };

// stap → pipeline-stage
const STEP_STAGE: Record<string, StageId> = {
  Idee: 'research', Verloop: 'topic', Script: 'script', Stemmen: 'voice', Cast: 'editing', Sets: 'editing',
  Animatie: 'editing', Render: 'editing', Montage: 'qc', 'Upload-tekst': 'thumbnail', Shorts: 'approval', Online: 'publishing',
};
const ORDER: StageId[] = ['research', 'topic', 'titles', 'script', 'factcheck', 'voice', 'editing', 'thumbnail', 'qc', 'approval', 'publishing'];

// Vorige echte stand, bewaard in deze browser: meldingen gaan alleen over wat er echt veranderd is
// sinds de vorige keer, nooit over de ingebouwde reservestand (verbeterpunt 6 nov).
const SIG_KEY = 'dm-lastsig';
let lastSig = (() => { try { return localStorage.getItem(SIG_KEY) ?? ''; } catch { return ''; } })();
let audioCtx: AudioContext | null = null;
function beep() {
  try {
    audioCtx = audioCtx ?? new AudioContext();
    if (audioCtx.state !== 'running') return; // alleen na een klik van de kijker
    const o = audioCtx.createOscillator(); const g = audioCtx.createGain();
    o.frequency.value = 880; g.gain.setValueAtTime(0.06, audioCtx.currentTime); g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.35);
    o.connect(g).connect(audioCtx.destination); o.start(); o.stop(audioCtx.currentTime + 0.35);
  } catch { /* geen geluid */ }
}
if (typeof window !== 'undefined') window.addEventListener('pointerdown', () => { try { audioCtx = audioCtx ?? new AudioContext(); void audioCtx.resume(); } catch { /* */ } }, { once: true });

export function applyReal(live: Live, echt = true) {
  const st = useGame.getState();
  const now = realTick();

  // ── meldingen bij nieuws ─────────────────────
  const sig = JSON.stringify(live.activity.map((a) => [a.id, a.state, a.doing]));
  const prev = lastSig ? (JSON.parse(lastSig) as [string, string, string][]) : null;
  const news: string[] = [];
  if (prev && echt) {
    for (const a of live.activity) {
      const p = prev.find((x) => x[0] === a.id);
      if (!p) news.push(`🆕 Nieuw aan het werk: ${a.title}`);
      else if (p[1] !== a.state) news.push(a.state === 'blocked' ? `⏳ ${a.title} wacht op jou` : a.state === 'review_ready' ? `👀 ${a.title} is klaar voor controle` : a.state === 'done' ? `✅ ${a.title} is klaar` : `▶️ ${a.title} is weer aan het werk`);
      else if (p[2] !== a.doing && a.doing) news.push(`📌 ${a.title}: ${a.doing}`);
    }
  }
  if (echt) { lastSig = sig; try { localStorage.setItem(SIG_KEY, sig); } catch { /* geen opslag */ } }

  // ── medewerkers = threads ────────────────────
  const agents: Agent[] = live.activity.map((a: Activity) => {
    const old = st.agents.find((x) => x.id === a.id);
    const role = roleFor(a.title);
    const base = old ?? createAgent(role, 0, { name: a.title });
    return { ...base, id: a.id, name: a.title, role, department: createAgent(role, 0).department, state: STATE[a.state] ?? 'idle', currentTaskId: a.state === 'done' ? null : `task_${a.id}`, personality: a.doing ?? '', instructions: `Echte thread in het project. Laatst actief ${a.last}.`, avatar: { ...base.avatar, initials: a.title.split(' ').slice(0, 2).map((w) => w[0]?.toUpperCase() ?? '').join('') } };
  });
  const realTasks: Task[] = live.activity.map((a) => ({
    id: `task_${a.id}`, title: a.doing || a.title, description: `${a.title} · laatst actief ${a.last}`, agentId: a.id, projectId: null, stage: null, kind: 'manual',
    priority: a.state === 'blocked' ? 'High' : 'Medium', status: a.state === 'done' ? 'Completed' : a.state === 'working' ? 'In Progress' : 'Review',
    progress: a.state === 'done' ? 100 : a.state === 'working' ? 50 : 90, createdTick: now, deadlineTick: now + 24, dependencies: [], comments: [], documents: [], result: null, quality: null, revision: 0,
  }));

  // ── projecten = echte video's ────────────────
  const realProjects: Project[] = live.videos.map((v) => {
    const firstOpen = v.steps.find((s) => !s.done);
    const stage = firstOpen ? STEP_STAGE[firstOpen.label] ?? 'editing' : 'publishing';
    const idx = ORDER.indexOf(stage);
    const status: Project['status'] = v.status === 'Online' ? 'Published' : v.status === 'Klaar' ? 'Awaiting Publish' : 'Active';
    return {
      id: `real_v${v.nr}`, title: v.title, topic: v.werktitel, channelId: 'ch_history', stage, status, createdTick: 0, deadlineTick: now + 24 * 7, priority: v.status === 'In productie' ? 'High' : 'Medium',
      taskIds: [], stageQuality: Object.fromEntries(ORDER.slice(0, Math.max(0, idx)).map((s) => [s, 80])), rejections: 0, cost: 0,
      history: v.notes.map((n) => ({ tick: now, text: n })),
    };
  });
  const ownProjects = st.projects.filter((p) => !p.id.startsWith('real_') && !p.history.some((h) => h.text.includes('(demo)')));

  // ── feed = wat de threads doen ───────────────
  const posts: ThreadPost[] = live.activity.filter((a) => a.doing).map((a) => ({ id: `post_${a.id}`, authorId: a.id, department: agents.find((x) => x.id === a.id)?.department as DepartmentId, kind: a.state === 'blocked' ? 'question' : a.state === 'done' ? 'celebration' : 'update', content: a.doing!, tick: now, likes: [], comments: [] }));
  const ownPosts = st.posts.filter((p) => p.authorId === 'player');

  // ── video's en kosten = echt (geen speelgeld meer, niels 2026-11-06) ──
  const yt = live.youtube;
  const videos: Video[] = (yt?.videos?.length ? yt.videos.map((v, i) => ({ id: `ytv_${i}`, projectId: 'real', channelId: 'ch_history', title: v.title, publishedTick: now, quality: 0, ctr: 0, avd: v.avp ?? 0, views: v.views ?? 0, revenue: 0, likes: v.likes ?? 0 }))
    : live.videos.filter((v) => v.status === 'Online').map((v) => ({ id: `real_vid${v.nr}`, projectId: `real_v${v.nr}`, channelId: 'ch_history', title: v.title, publishedTick: now, quality: 0, ctr: 0, avd: v.nr === 1 ? 26.3 : 0, views: v.nr === 1 ? 48 : 0, revenue: 0, likes: 0 })));
  const ledger: LedgerEntry[] = (live.costs ?? []).filter((c) => typeof c.bedrag === 'number').map((c, i) => ({ id: `cost_${i}`, day: Math.floor(now / 24), channelId: null, category: 'AI Subscriptions', amount: -(c.bedrag as number), note: `${c.wat}${c.notitie ? ` · ${c.notitie}` : ''} (${c.datum})` }));
  const subs = yt?.subscribers;

  useGame.setState({
    videos, ledger, stats: [], company: { ...st.company, name: 'Driftmark', balance: -ledger.reduce((s, l) => s - l.amount, 0) },
    channels: st.channels.map((c) => (c.id === 'ch_history' ? { ...c, isDemo: false, subscribers: subs ?? c.subscribers, views: yt?.views ?? c.views } : { ...c, isDemo: false })),
    tick: now, agents, tasks: [...realTasks, ...st.tasks.filter((t) => !t.id.startsWith('task_') && ownProjects.some((p) => p.id === t.projectId))],
    projects: [...realProjects, ...ownProjects], posts: [...ownPosts, ...posts], demoMode: false,
    notifications: [...news.map((text) => ({ id: uid('n'), tick: now, text, kind: 'info' as const, read: false })), ...st.notifications].slice(0, 60),
  });
  if (news.length && prefs().meldingen) { news.slice(0, 3).forEach((n) => st.toast(n, 'info')); if (prefs().meldingGeluid) beep(); }
}
