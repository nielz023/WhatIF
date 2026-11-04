/**
 * Central workflow & task engine — pure mutations on a GameData draft (immer).
 * Handles assignment, progress, reviews, feedback loops, hand-offs, daily economy,
 * Threads chatter, achievements and missions.
 */
import type { Agent, MissionMetric, Project, StageId, Task, ThreadPost } from '../../types';
import type { GameData } from '../../store/state';
import { PIPELINE, nextStage, stageById } from '../workflows/pipeline';
import { simulateDeliverable } from '../workflows/deliverables';
import { agentPower, roleById, xpForLevel } from '../agents/roles';
import { companyXpForLevel, generateMissions, celebration } from '../gameplay/progression';
import { TICKS_PER_DAY, clamp, dayOf, hourOf, pick, rand, randInt, uid, eur } from '../../lib/util';

// ── helpers ─────────────────────────────────────────────────────
/** Share of an agent's nominal salary charged per game day (compute + subscriptions). */
export const SALARY_FACTOR = 0.08;
export const upgradeLevel =(d: GameData, id: string) => d.upgrades.find((u) => u.id === id)?.level ?? 0;
export const agentSlots = (d: GameData) => d.company.baseSlots + upgradeLevel(d, 'expansion') * 6;

export function notify(d: GameData, text: string, kind: GameData['notifications'][number]['kind'] = 'info', link?: GameData['notifications'][number]['link']) {
  d.notifications.unshift({ id: uid('n'), tick: d.tick, text, kind, read: false, link });
  if (d.notifications.length > 80) d.notifications.length = 80;
}

export function post(d: GameData, authorId: string, kind: ThreadPost['kind'], content: string, attachment?: ThreadPost['attachment']) {
  const a = d.agents.find((x) => x.id === authorId);
  d.posts.unshift({ id: uid('po'), authorId, department: a?.department ?? 'hq', kind, content, tick: d.tick, likes: [], comments: [], attachment });
  if (d.posts.length > 150) d.posts.length = 150;
}

export function addCompanyXp(d: GameData, xp: number) {
  d.company.xp += xp;
  while (d.company.xp >= companyXpForLevel(d.company.level)) {
    d.company.xp -= companyXpForLevel(d.company.level);
    d.company.level += 1;
    notify(d, `🏆 Company reached level ${d.company.level}!`, 'achievement');
    d.company.reputation = clamp(d.company.reputation + 3, 0, 100);
  }
}

export function addAgentXp(d: GameData, a: Agent, xp: number) {
  a.xp += xp;
  while (a.xp >= xpForLevel(a.level)) {
    a.xp -= xpForLevel(a.level);
    a.level += 1;
    a.salary += 4;
    Object.keys(a.skills).forEach((k) => (a.skills[k] = clamp(a.skills[k] + 3, 0, 100)));
    notify(d, `⬆️ ${a.name} reached level ${a.level}.`, 'success', 'agents');
  }
}

export function bumpMission(d: GameData, metric: MissionMetric, n = 1) {
  d.missions.forEach((m) => {
    if (m.metric === metric && !m.claimed) m.progress = Math.min(m.target, m.progress + n);
  });
}

export function ledger(d: GameData, category: GameData['ledger'][number]['category'], amount: number, note: string, channelId: string | null = null, day = dayOf(d.tick)) {
  d.ledger.push({ id: uid('le'), day, channelId, category, amount: Math.round(amount * 100) / 100, note });
  d.company.balance += amount;
}

const speedMult = (d: GameData) =>
  1 + upgradeLevel(d, 'render_farm') * 0.15 + (d.modifiers.speedBoostUntil > d.tick ? d.modifiers.speedBoost : 0);

// ── assignment ──────────────────────────────────────────────────
export function findAgentFor(d: GameData, roles: string[], channelId: string | null): Agent | null {
  const candidates = d.agents.filter(
    (a) => roles.includes(a.role) && !a.currentTaskId && a.state !== 'training' &&
      (a.channelIds.length === 0 || !channelId || a.channelIds.includes(channelId)) &&
      !d.warCases.some((w) => w.status === 'Investigating' && w.agentIds.includes(a.id)),
  );
  if (!candidates.length) return null;
  return candidates.sort((x, y) => roles.indexOf(x.role) - roles.indexOf(y.role) || agentPower(y) - agentPower(x))[0];
}

export function assignTask(d: GameData, t: Task, agent: Agent) {
  t.agentId = agent.id;
  t.status = 'Assigned';
  agent.currentTaskId = t.id;
  if (!agent.taskHistory.includes(t.id)) agent.taskHistory.push(t.id);
}

export function createStageTask(d: GameData, p: Project, stage: StageId, note?: string): Task {
  const s = stageById(stage);
  const prev = d.tasks.filter((t) => t.projectId === p.id && t.stage === stage);
  const prevTaskOfPrevStage = d.tasks.filter((t) => t.projectId === p.id && t.status === 'Completed').slice(-1)[0];
  const t: Task = {
    id: uid('tk'),
    title: `${s.label}: ${p.title}`,
    description: `Produce the ${s.deliverableName} for "${p.title}".${note ? ` Feedback to address: ${note}` : ''}`,
    agentId: null, projectId: p.id, stage, kind: 'pipeline', priority: p.priority,
    status: 'Pending', progress: 0, createdTick: d.tick,
    deadlineTick: d.tick + Math.max(6, Math.round(s.effort / 6)),
    dependencies: prevTaskOfPrevStage ? [prevTaskOfPrevStage.id] : [],
    comments: note ? [{ id: uid('c'), authorId: 'system', text: `Returned with feedback: ${note}`, tick: d.tick }] : [],
    documents: [], result: null, quality: null, revision: prev.length,
  };
  d.tasks.push(t);
  p.taskIds.push(t.id);
  return t;
}

// ── project transitions ─────────────────────────────────────────
function advanceProject(d: GameData, p: Project, fromTask: Task) {
  const nxt = nextStage(p.stage);
  const s = stageById(p.stage);
  p.cost += s.cost;
  ledger(d, 'Production', -s.cost, `${s.label} · ${p.title}`, p.channelId);
  p.history.push({ tick: d.tick, text: `${s.label} completed (quality ${fromTask.quality})` });
  addCompanyXp(d, 6);
  if (!nxt) return;
  p.stage = nxt;
  const nt = createStageTask(d, p, nxt);
  const fromAgent = d.agents.find((a) => a.id === fromTask.agentId);
  const ns = stageById(nxt);
  // hand-off message
  fromTask.comments.push({ id: uid('c'), authorId: fromTask.agentId ?? 'system', text: `Submitted ${s.deliverableName}. Handing off to ${ns.label}.`, tick: d.tick });
  if (nxt === 'approval') {
    p.status = 'Awaiting Approval';
    nt.status = 'Review';
    const ceo = d.agents.find((a) => a.role === 'ceo_agent');
    if (ceo) { nt.agentId = ceo.id; }
    nt.documents.push({ id: uid('doc'), name: 'Approval Memo', kind: 'analysis', content: simulateDeliverable('approval', p, d.channels.find((c) => c.id === p.channelId), projectQuality(p)) });
    notify(d, `🧾 "${p.title}" is waiting for your CEO approval.`, 'approval', 'projects');
    if (ceo) post(d, ceo.id, 'update', `"${p.title}" passed QC and is on the CEO's desk for final approval. Quality score ${projectQuality(p)}/100.`);
  } else if (fromAgent && Math.random() < 0.35) {
    post(d, fromAgent.id, 'handoff', `Just handed the ${s.deliverableName} for "${p.title}" to the ${ns.label} team ${celebration()}`);
  }
}

export const projectQuality = (p: Project) => {
  const v = Object.values(p.stageQuality) as number[];
  return v.length ? Math.round(v.reduce((s, x) => s + x, 0) / v.length) : 0;
};

/** Feedback loop — send project back to an earlier stage. */
export function rejectProjectTo(d: GameData, p: Project, to: StageId, reason: string, byAgentId: string | null) {
  // close any open tasks for this project
  d.tasks.filter((t) => t.projectId === p.id && !['Completed', 'Rejected'].includes(t.status)).forEach((t) => {
    t.status = 'Rejected';
    const a = d.agents.find((x) => x.id === t.agentId);
    if (a && a.currentTaskId === t.id) { a.currentTaskId = null; a.state = 'idle'; }
  });
  const last = [...d.tasks].reverse().find((t) => t.projectId === p.id && t.stage === to && t.status === 'Completed');
  if (last) {
    last.status = 'Rejected';
    last.comments.push({ id: uid('c'), authorId: byAgentId ?? 'player', text: `Rejected: ${reason}`, tick: d.tick });
  }
  p.rejections += 1;
  p.stage = to;
  p.status = 'Active';
  delete p.stageQuality[to];
  p.history.push({ tick: d.tick, text: `Returned to ${stageById(to).label}: ${reason}` });
  createStageTask(d, p, to, reason);
  notify(d, `↩️ "${p.title}" was sent back to ${stageById(to).label}.`, 'warning', 'projects');
}

// ── reviews (fact check & QC gatekeepers) ──────────────────────
function runGateReview(d: GameData, p: Project, t: Task): boolean {
  const s = stageById(t.stage!);
  if (!s.rejectTo) return true;
  const targetQ = p.stageQuality[s.rejectTo] ?? 60;
  const reviewBonus = upgradeLevel(d, 'meeting_pods') * 6;
  const passChance = clamp((targetQ + reviewBonus - 30) / 50, 0.25, 0.97);
  if (Math.random() < passChance || p.rejections >= 3) return true;
  const reason = s.id === 'factcheck' ? `${randInt(2, 5)} claims need stronger sources` : pick(['pacing dips in act 2', 'audio levels inconsistent', 'b-roll does not match narration']);
  t.result = `Rejected — ${reason}`;
  t.status = 'Completed';
  const reviewer = d.agents.find((a) => a.id === t.agentId);
  if (reviewer) post(d, reviewer.id, 'alert', `Sent "${p.title}" back to ${stageById(s.rejectTo).label}: ${reason}. Let's tighten it up 🔁`);
  rejectProjectTo(d, p, s.rejectTo, reason, t.agentId);
  return false;
}

// ── main tick ───────────────────────────────────────────────────
export function simulateTick(d: GameData) {
  const prevDay = dayOf(d.tick);
  d.tick += 1;
  const day = dayOf(d.tick);

  // 1. ensure active projects have a live stage task
  d.projects.filter((p) => p.status === 'Active').forEach((p) => {
    const live = d.tasks.find((t) => t.projectId === p.id && t.stage === p.stage && !['Completed', 'Rejected'].includes(t.status));
    if (!live) createStageTask(d, p, p.stage);
  });

  // 2. assignment of pending tasks (pipeline + manual)
  d.tasks.filter((t) => t.status === 'Pending').forEach((t) => {
    if (t.dependencies.some((dep) => { const x = d.tasks.find((y) => y.id === dep); return x && x.status !== 'Completed' && x.status !== 'Approved'; })) return;
    if (t.agentId) {
      const a = d.agents.find((x) => x.id === t.agentId);
      if (a && !a.currentTaskId && a.state !== 'training') assignTask(d, t, a);
      return;
    }
    if (t.stage) {
      const p = d.projects.find((x) => x.id === t.projectId);
      const a = findAgentFor(d, stageById(t.stage).roles, p?.channelId ?? null);
      if (a) {
        assignTask(d, t, a);
        if (Math.random() < 0.2) post(d, a.id, 'update', `Picked up "${t.title}". ${pick(['Let’s go!', 'Coffee first ☕', 'This one looks fun.', 'Deadline noted.'])}`);
      }
    }
  });

  // 3. progress
  const mult = speedMult(d);
  d.tasks.forEach((t) => {
    if (t.status === 'Assigned') { t.status = 'In Progress'; return; }
    const a = d.agents.find((x) => x.id === t.agentId);
    if (t.status === 'In Progress' && a) {
      const effort = t.stage ? stageById(t.stage).effort : 50;
      const prioBoost = { Low: 0.9, Medium: 1, High: 1.12, Critical: 1.25 }[t.priority];
      t.progress = Math.min(100, t.progress + (agentPower(a) / effort) * 6 * mult * prioBoost);
      a.state = 'working';
      if (t.progress >= 100) {
        // produce result → review (request feedback)
        let q = agentPower(a) * rand(0.85, 1.2) + (t.revision * 6);
        if (t.stage === 'voice') q += upgradeLevel(d, 'studio') * 8;
        t.quality = Math.round(clamp(q, 20, 99));
        const p = d.projects.find((x) => x.id === t.projectId);
        if (t.stage && p) {
          const s = stageById(t.stage);
          t.documents.push({ id: uid('doc'), name: `${s.deliverableName}${t.revision ? ` (rev ${t.revision + 1})` : ''}`, kind: s.deliverable, content: simulateDeliverable(t.stage, p, d.channels.find((c) => c.id === p.channelId), t.quality) });
        } else {
          t.documents.push({ id: uid('doc'), name: 'Deliverable', kind: 'report', content: `${t.title}\nCompleted by ${a.name} (${roleById(a.role).title}).\nQuality ${t.quality}/100.\n(Local simulation output)` });
        }
        t.status = 'Review';
        t.comments.push({ id: uid('c'), authorId: a.id, text: 'Deliverable submitted — requesting feedback.', tick: d.tick });
        a.state = 'meeting';
      }
    } else if (t.status === 'Review' && t.stage !== 'approval' && t.stage !== 'publishing') {
      // a review meeting lasts ~2 ticks
      if (a) a.state = 'meeting';
      if (d.tick - t.createdTick > 0 && Math.random() < 0.55) {
        t.status = 'Approved';
        t.comments.push({ id: uid('c'), authorId: 'system', text: 'Peer review approved.', tick: d.tick });
      }
    } else if (t.status === 'Approved' && t.kind !== 'warroom') {
      t.status = 'Completed';
      t.result = t.result ?? `${t.documents.at(-1)?.name ?? 'Deliverable'} delivered (quality ${t.quality}).`;
      if (a) {
        a.currentTaskId = null; a.state = 'idle'; a.completed += 1;
        a.performance = Math.round(clamp(a.performance * 0.85 + (t.quality ?? 60) * 0.15, 0, 100));
        a.morale = clamp(a.morale - 2, 0, 100);
        addAgentXp(d, a, Math.round((t.stage ? stageById(t.stage).effort : 50) / 3));
      }
      bumpMission(d, 'complete_tasks');
      const p = d.projects.find((x) => x.id === t.projectId);
      if (p && t.stage && p.stage === t.stage && p.status === 'Active') {
        p.stageQuality[t.stage] = t.quality ?? 60;
        if (runGateReview(d, p, t)) advanceProject(d, p, t);
      }
    }
  });

  // 4. idle agents / training
  d.agents.forEach((a) => {
    if (a.state === 'training' && a.trainingUntil && d.tick >= a.trainingUntil) {
      a.state = 'idle'; a.trainingUntil = undefined;
      notify(d, `🎓 ${a.name} finished training.`, 'success', 'agents');
    }
    if (a.state !== 'training' && !a.currentTaskId) {
      const inWar = d.warCases.some((w) => w.status === 'Investigating' && w.agentIds.includes(a.id));
      a.state = inWar ? 'meeting' : (a.state === 'meeting' && Math.random() < 0.5 ? 'meeting' : 'idle');
      a.morale = clamp(a.morale + 0.4 + upgradeLevel(d, 'coffee_bar') * 0.3, 0, 100);
    }
  });

  // 5. war room
  d.warCases.forEach((w) => {
    if (w.status === 'Investigating' && d.tick >= w.readyTick) {
      w.status = 'Ready';
      notify(d, `🛡️ War Room analysis ready: ${w.title}`, 'approval', 'warroom');
      const ceo = d.agents.find((a) => a.role === 'ceo_agent');
      if (ceo) post(d, ceo.id, 'report', `War Room finished investigating "${w.title}". Recommendations are on the CEO's desk.`, { title: w.title, body: w.analysis.join('\n') });
    }
  });

  // 6. Threads chatter
  if (Math.random() < 0.12) {
    const a = pick(d.agents);
    if (a) {
      const lines = [
        `Reminder: hooks under 15 seconds. Our retention data doesn't lie 📊`,
        `Found a great reference channel for our ${pick(d.channels)?.niche ?? 'niche'} content — sharing in the research folder.`,
        `Productive morning in the ${roleById(a.role).department} room ${celebration()}`,
        `Anyone free for a quick feedback session on my latest deliverable?`,
        `New personal best: ${randInt(3, 6)} tasks shipped this week.`,
      ];
      post(d, a.id, pick(['update', 'update', 'question']) as ThreadPost['kind'], pick(lines));
    }
  }
  if (Math.random() < 0.25 && d.posts.length) {
    const p = pick(d.posts.slice(0, 10));
    const a = pick(d.agents);
    if (a && !p.likes.includes(a.id) && p.authorId !== a.id) p.likes.push(a.id);
  }

  // 7. daily rollover
  if (day !== prevDay) dailyRollover(d, prevDay);

  checkAchievements(d);
}

// ── economy ─────────────────────────────────────────────────────
export function dailyRollover(d: GameData, closedDay: number) {
  const totalSubs = d.channels.reduce((s, c) => s + c.subscribers, 0);
  d.channels.forEach((c) => {
    let views = 0;
    let ctrSum = 0; let avdSum = 0; let n = 0;
    d.videos.filter((v) => v.channelId === c.id).forEach((v) => {
      const age = closedDay - dayOf(v.publishedTick);
      if (age < 0) return;
      const reach = (v.quality * 40 + c.subscribers * 0.15 + d.company.reputation * 6) * (v.ctr / 5) * (v.avd / 42);
      const vv = Math.round(reach * Math.exp(-age / 10) * rand(0.75, 1.25) + 15);
      v.views += vv; v.likes += Math.round(vv * 0.035);
      const rev = c.monetized ? (vv / 1000) * c.rpm : 0;
      v.revenue += rev;
      views += vv; ctrSum += v.ctr; avdSum += v.avd; n++;
    });
    views += Math.round(c.subscribers * 0.02);
    const subs = Math.round(views * rand(0.006, 0.012));
    const revenue = c.monetized ? (views / 1000) * c.rpm : 0;
    c.views += views; c.subscribers += subs; c.revenue += revenue;
    d.stats.push({ day: closedDay, channelId: c.id, views, subs, revenue: Math.round(revenue * 100) / 100, ctr: n ? +(ctrSum / n).toFixed(2) : 0, avd: n ? +(avdSum / n).toFixed(1) : 0 });
    if (revenue > 0) ledger(d, 'Ad Revenue', revenue, `Ad revenue · ${c.name}`, c.id, closedDay);
    if (!c.monetized && c.subscribers >= 1000) {
      c.monetized = true;
      notify(d, `💸 ${c.name} is now monetized! Ad revenue starts flowing.`, 'achievement', 'channels');
      const fm = d.agents.find((a) => a.role === 'financial_manager' || a.role === 'ceo_agent');
      if (fm) post(d, fm.id, 'celebration', `${c.name} just crossed 1,000 subscribers and is MONETIZED 💸 Huge work, team!`);
    }
  });
  void totalSubs;
  const salaries = d.agents.reduce((s, a) => s + a.salary, 0) * SALARY_FACTOR;
  ledger(d, 'Salaries', -salaries, `Daily agent compute & salaries (${d.agents.length} agents)`, null, closedDay);
  if (closedDay % 30 === 0) {
    ledger(d, 'AI Subscriptions', -(80 + d.agents.length * 4), 'Monthly LLM & voice plans');
    ledger(d, 'Software', -65, 'Editing suite & stock footage library');
  }
  // missions refresh
  d.missions = generateMissions();
  d.missionDay = closedDay + 1;
  // reputation drift
  d.company.reputation = clamp(d.company.reputation + (d.videos.length ? 0.2 : -0.1), 0, 100);
  // expire war-room boosts gradually
  d.channels.forEach((c) => { c.ctrBoost *= 0.97; c.retentionBoost *= 0.97; });
  if (closedDay % 3 === 0) detectIssues(d);
}

export function detectIssues(d: GameData) {
  const day = dayOf(d.tick);
  const overdue = d.projects.filter((p) => p.status === 'Active' && p.deadlineTick < d.tick).length;
  if (overdue >= 2 && !d.warCases.some((w) => w.type === 'production_delays' && ['Investigating', 'Ready'].includes(w.status)))
    notify(d, `⚠️ ${overdue} projects are overdue. Consider convening the War Room.`, 'warning', 'warroom');
  d.channels.forEach((c) => {
    const s = d.stats.filter((x) => x.channelId === c.id && x.day > day - 15);
    if (s.length < 14) return;
    const a = s.slice(-7).reduce((t, x) => t + x.views, 0);
    const b = s.slice(-14, -7).reduce((t, x) => t + x.views, 0);
    if (b > 0 && a < b * 0.85) notify(d, `📉 ${c.name}: views down ${Math.round((1 - a / b) * 100)}% week-over-week.`, 'warning', 'warroom');
  });
}

// ── achievements ────────────────────────────────────────────────
export function checkAchievements(d: GameData) {
  const totalViews = d.channels.reduce((s, c) => s + c.views, 0);
  const totalRev = d.ledger.filter((l) => l.category === 'Ad Revenue').reduce((s, l) => s + l.amount, 0);
  const published = d.projects.filter((p) => p.status === 'Published').length;
  const checks: Record<string, boolean> = {
    first_video: published >= 1,
    five_videos: published >= 5,
    views_100k: totalViews >= 100_000,
    views_1m: totalViews >= 1_000_000,
    monetized: d.channels.some((c) => c.monetized),
    rev_1000: totalRev >= 1000,
    team_10: d.agents.some((a) => a.hiredDay > 0),
    team_20: d.agents.length >= 20,
    first_upgrade: d.upgrades.some((u) => u.level > 0),
    war_room: d.warCases.some((w) => w.status === 'Resolved'),
    level_5: d.company.level >= 5,
    two_channels: d.channels.some((c) => !c.isDemo),
    agent_lvl5: d.agents.some((a) => a.level >= 5),
  };
  d.achievements.forEach((a) => {
    if (!a.unlockedTick && checks[a.id]) {
      a.unlockedTick = d.tick;
      addCompanyXp(d, a.xp);
      notify(d, `🏅 Achievement unlocked: ${a.title}`, 'achievement', 'achievements');
    }
  });
}

export { eur, TICKS_PER_DAY, hourOf, PIPELINE };
