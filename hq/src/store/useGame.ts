import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { Channel, DepartmentId, IntegrationSettings, PageId, Priority, RoleId, StageId, Task, ThreadPost, WarIssueType } from '../types';
import type { GameData } from './state';
import { createSeed } from '../data/seed';
import {
  addAgentXp, addCompanyXp, agentSlots, bumpMission, checkAchievements, createStageTask, ledger, notify, post,
  projectQuality, rejectProjectTo, simulateTick, upgradeLevel,
} from '../modules/tasks/engine';
import { createAgent, roleById, xpForLevel } from '../modules/agents/roles';
import { buildAnalysis, ISSUE_META } from '../modules/warroom/warroom';
import { TICKS_PER_DAY, clamp, dayOf, rand, uid } from '../lib/util';
import { localStorageAdapter } from '../services/persistence/storage';

export type ModalId = 'newVideo' | 'assignTask' | 'hireAgent' | 'confirm' | 'newChannel' | null;

export interface ConfirmRequest {
  title: string;
  body: string;
  confirmLabel: string;
  danger?: boolean;
  onConfirm: () => void;
}

interface UIState {
  page: PageId;
  selectedDept: DepartmentId | 'warroom' | null;
  selectedAgentId: string | null;
  selectedProjectId: string | null;
  modal: ModalId;
  modalPayload: Record<string, unknown> | null;
  confirm: ConfirmRequest | null;
  paused: boolean;
  speed: number; // ticks per second
  toasts: { id: string; text: string; kind: 'info' | 'success' | 'warning' }[];
  notifOpen: boolean;
}

interface Actions {
  setPage: (p: PageId) => void;
  selectDept: (d: UIState['selectedDept']) => void;
  selectAgent: (id: string | null) => void;
  selectProject: (id: string | null) => void;
  openModal: (m: ModalId, payload?: Record<string, unknown>) => void;
  closeModal: () => void;
  askConfirm: (c: ConfirmRequest) => void;
  closeConfirm: () => void;
  toast: (text: string, kind?: 'info' | 'success' | 'warning') => void;
  dismissToast: (id: string) => void;
  setNotifOpen: (v: boolean) => void;
  togglePause: () => void;
  setSpeed: (s: number) => void;

  advance: () => void;
  fastForward: (hours: number) => void;

  startVideo: (i: { channelId: string; title: string; topic: string; priority: Priority; deadlineDays: number }) => string;
  assignManualTask: (i: { title: string; description: string; agentId: string | null; role?: RoleId; priority: Priority; deadlineDays: number; projectId: string | null; dependencies: string[] }) => void;
  setTaskPriority: (taskId: string, p: Priority) => void;
  commentTask: (taskId: string, text: string) => void;
  reviewTask: (taskId: string, approve: boolean, note?: string) => void;
  reassignTask: (taskId: string, agentId: string) => void;

  hireAgent: (role: RoleId, channelIds: string[]) => boolean;
  fireAgent: (id: string) => void;
  trainAgent: (id: string, skill: string) => boolean;
  promoteAgent: (id: string) => boolean;
  maxUpgradeAgent: (id: string) => boolean;
  maxUpgradeAll: () => number;
  updateAgent: (id: string, patch: { instructions?: string; channelIds?: string[]; personality?: string }) => void;

  approveProject: (id: string) => void;
  rejectProject: (id: string, to: StageId, reason: string) => void;
  publishProject: (id: string) => void;
  cancelProject: (id: string) => void;

  likePost: (id: string) => void;
  commentPost: (id: string, text: string) => void;
  createPost: (content: string, attachment?: ThreadPost['attachment']) => void;
  sharePost: (id: string) => void;
  markAllRead: () => void;

  buyUpgrade: (id: string) => boolean;
  claimMission: (id: string) => void;

  addChannel: (c: Omit<Channel, 'id' | 'subscribers' | 'views' | 'revenue' | 'monetized' | 'ctrBoost' | 'retentionBoost' | 'createdTick' | 'isDemo'>) => void;
  updateChannel: (id: string, patch: Partial<Channel>) => void;
  assignDeptToChannel: (dept: DepartmentId, channelId: string | null) => void;

  openWarCase: (type: WarIssueType, channelId: string | null) => void;
  approveRecommendation: (caseId: string, recId: string) => void;
  dismissCase: (caseId: string) => void;

  updateSettings: (patch: Partial<IntegrationSettings>) => void;
  resetGame: () => void;
  importSave: (data: GameData) => void;
}

export type GameStore = GameData & UIState & Actions;

const uiDefaults: UIState = {
  page: 'driftmark', selectedDept: null, selectedAgentId: null, selectedProjectId: null, modal: null, modalPayload: null,
  confirm: null, paused: false, speed: 1, toasts: [], notifOpen: false,
};

export const useGame = create<GameStore>()(
  persist(
    immer((set, get) => ({
      ...createSeed(),
      ...uiDefaults,

      // ── UI ───────────────────────────────────────────
      setPage: (p) => set((s) => { s.page = p; s.selectedDept = null; }),
      selectDept: (d) => set((s) => { s.selectedDept = d; }),
      selectAgent: (id) => set((s) => { s.selectedAgentId = id; }),
      selectProject: (id) => set((s) => { s.selectedProjectId = id; }),
      openModal: (m, payload) => set((s) => { s.modal = m; s.modalPayload = payload ?? null; }),
      closeModal: () => set((s) => { s.modal = null; s.modalPayload = null; }),
      askConfirm: (c) => set((s) => { s.confirm = c as never; }),
      closeConfirm: () => set((s) => { s.confirm = null; }),
      toast: (text, kind = 'info') => {
        const id = uid('t');
        set((s) => { s.toasts.push({ id, text, kind }); });
        setTimeout(() => get().dismissToast(id), 3800);
      },
      dismissToast: (id) => set((s) => { s.toasts = s.toasts.filter((t) => t.id !== id); }),
      setNotifOpen: (v) => set((s) => { s.notifOpen = v; }),
      togglePause: () => set((s) => { s.paused = !s.paused; }),
      setSpeed: (v) => set((s) => { s.speed = v; s.paused = false; }),

      // ── simulation ───────────────────────────────────
      advance: () => set((s) => { simulateTick(s as unknown as GameData); }),
      fastForward: (hours) => set((s) => { for (let i = 0; i < hours; i++) simulateTick(s as unknown as GameData); }),

      // ── projects & tasks ─────────────────────────────
      startVideo: ({ channelId, title, topic, priority, deadlineDays }) => {
        const id = uid('pr');
        set((s) => {
          const d = s as unknown as GameData;
          d.projects.unshift({
            id, title, topic, channelId, stage: 'research', status: 'Active', createdTick: d.tick,
            deadlineTick: d.tick + deadlineDays * TICKS_PER_DAY, priority, taskIds: [], stageQuality: {}, rejections: 0, cost: 0,
            history: [{ tick: d.tick, text: 'Project gestart door niels' }],
          });
          createStageTask(d, d.projects[0], 'research');
          bumpMission(d, 'start_video');
          addCompanyXp(d, 10);
          const ceo = d.agents.find((a) => a.role === 'ceo_agent');
          if (ceo) post(d, ceo.id, 'update', `Nieuwe video gestart: "${title}" 🎬 Onderzoek, aan jullie.`);
        });
        get().toast(`"${title}" gestart. Onderzoek heeft de opdracht.`, 'success');
        return id;
      },
      assignManualTask: (i) => {
        set((s) => {
          const d = s as unknown as GameData;
          let agentId = i.agentId;
          if (!agentId && i.role) agentId = d.agents.find((a) => a.role === i.role)?.id ?? null;
          const t: Task = {
            id: uid('tk'), title: i.title, description: i.description, agentId, projectId: i.projectId, stage: null, kind: 'manual',
            priority: i.priority, status: 'Pending', progress: 0, createdTick: d.tick, deadlineTick: d.tick + i.deadlineDays * TICKS_PER_DAY,
            dependencies: i.dependencies, comments: [{ id: uid('c'), authorId: 'player', text: 'Assigned by CEO.', tick: d.tick }], documents: [{ id: uid('doc'), name: 'Task Brief', kind: 'brief', content: i.description || i.title }],
            result: null, quality: null, revision: 0,
          };
          d.tasks.push(t);
          if (i.projectId) d.projects.find((p) => p.id === i.projectId)?.taskIds.push(t.id);
        });
        get().toast('Taak gemaakt en klaargezet voor de agent.', 'success');
      },
      setTaskPriority: (taskId, p) => set((s) => { const t = s.tasks.find((x) => x.id === taskId); if (t) t.priority = p; }),
      commentTask: (taskId, text) => set((s) => {
        const t = s.tasks.find((x) => x.id === taskId);
        if (!t) return;
        t.comments.push({ id: uid('c'), authorId: 'player', text, tick: s.tick });
        const a = s.agents.find((x) => x.id === t.agentId);
        if (a) t.comments.push({ id: uid('c'), authorId: a.id, text: `Thanks — noted. I'll factor that in. (${a.personality.split(' ')[0]} response)`, tick: s.tick });
      }),
      reviewTask: (taskId, approve, note) => set((s) => {
        const d = s as unknown as GameData;
        const t = d.tasks.find((x) => x.id === taskId);
        if (!t) return;
        if (approve) {
          t.status = 'Approved';
          t.comments.push({ id: uid('c'), authorId: 'player', text: note || 'Approved by CEO.', tick: d.tick });
          bumpMission(d, 'approve');
        } else {
          t.status = 'In Progress';
          t.progress = 55;
          t.revision += 1;
          t.comments.push({ id: uid('c'), authorId: 'player', text: `Aanpassingen gevraagd: ${note || 'Please improve quality.'}`, tick: d.tick });
        }
      }),
      reassignTask: (taskId, agentId) => set((s) => {
        const t = s.tasks.find((x) => x.id === taskId);
        if (!t) return;
        const old = s.agents.find((a) => a.id === t.agentId);
        if (old && old.currentTaskId === t.id) { old.currentTaskId = null; old.state = 'idle'; }
        t.agentId = agentId;
        t.status = 'Pending';
        t.comments.push({ id: uid('c'), authorId: 'player', text: 'Reassigned by CEO.', tick: s.tick });
      }),

      // ── agents ───────────────────────────────────────
      hireAgent: (role, channelIds) => {
        const d = get() as unknown as GameData;
        const def = roleById(role);
        if (d.agents.length >= agentSlots(d)) { get().toast('Geen vrij bureau. Koop de upgrade Kantooruitbreiding.', 'warning'); return false; }
        if (d.company.balance < def.hireCost) { get().toast('Niet genoeg saldo om aan te nemen.', 'warning'); return false; }
        let name = '';
        set((s) => {
          const g = s as unknown as GameData;
          const a = createAgent(role, dayOf(g.tick), { channelIds });
          name = a.name;
          g.agents.push(a);
          ledger(g, 'Hiring', -def.hireCost, `Hired ${a.name} (${def.title})`);
          bumpMission(g, 'hire');
          post(g, a.id, 'celebration', `Hoi allemaal 👋 Ik ben ${a.name}, de nieuwe ${def.title}. Zin in het team ${def.department}!`);
          notify(g, `👋 ${a.name} is begonnen als ${def.title}.`, 'success', 'agents');
          checkAchievements(g);
        });
        get().toast(`Hired ${name} as ${def.title}.`, 'success');
        return true;
      },
      fireAgent: (id) => set((s) => {
        const a = s.agents.find((x) => x.id === id);
        if (!a) return;
        s.tasks.filter((t) => t.agentId === id && !['Completed', 'Rejected'].includes(t.status)).forEach((t) => { t.agentId = null; t.status = 'Pending'; });
        s.agents = s.agents.filter((x) => x.id !== id);
        notify(s as unknown as GameData, `${a.name} heeft het bedrijf verlaten.`, 'info', 'agents');
        if (s.selectedAgentId === id) s.selectedAgentId = null;
      }),
      trainAgent: (id, skill) => {
        const d = get() as unknown as GameData;
        const a = d.agents.find((x) => x.id === id);
        if (!a) return false;
        const lab = upgradeLevel(d, 'training_lab');
        const cost = Math.round(120 * a.level * (1 - lab * 0.25));
        if (a.currentTaskId) { get().toast(`${a.name} is bezig met een taak. Probeer het als hij vrij is.`, 'warning'); return false; }
        if (a.state === 'training') { get().toast(`${a.name} zit al in een training.`, 'warning'); return false; }
        if (d.company.balance < cost) { get().toast('Niet genoeg saldo voor de training.', 'warning'); return false; }
        set((s) => {
          const g = s as unknown as GameData;
          const ag = g.agents.find((x) => x.id === id)!;
          ag.state = 'training';
          ag.trainingUntil = g.tick + Math.round(10 * (1 - lab * 0.25));
          ag.skills[skill] = clamp((ag.skills[skill] ?? 40) + 8, 0, 100);
          addAgentXp(g, ag, 40);
          ag.morale = clamp(ag.morale + 6, 0, 100);
          ledger(g, 'Training', -cost, `Training ${ag.name}: ${skill}`);
          bumpMission(g, 'train');
        });
        get().toast(`${a.name} started ${skill} training (−€${cost}).`, 'success');
        return true;
      },
      promoteAgent: (id) => {
        const d = get() as unknown as GameData;
        const a = d.agents.find((x) => x.id === id);
        if (!a) return false;
        const cost = 250 * a.level;
        if (d.company.balance < cost) { get().toast('Niet genoeg saldo voor deze upgrade.', 'warning'); return false; }
        set((s) => {
          const g = s as unknown as GameData;
          const ag = g.agents.find((x) => x.id === id)!;
          ledger(g, 'Training', -cost, `${ag.name} naar niveau ${ag.level + 1}`);
          addAgentXp(g, ag, xpForLevel(ag.level) - ag.xp);
          checkAchievements(g);
        });
        return true;
      },
      // Max upgraden in één keer (niels 2026-11-05): niveau 10, alle vaardigheden 100
      maxUpgradeAgent: (id) => {
        const d = get() as unknown as GameData;
        const a = d.agents.find((x) => x.id === id);
        if (!a) return false;
        if (a.level >= MAX_LEVEL && Object.values(a.skills).every((v) => v >= 100)) { get().toast(`${a.name} is al maximaal.`, 'info'); return false; }
        const cost = maxUpgradeCost(a);
        if (d.company.balance < cost) { get().toast('Niet genoeg saldo om maximaal te upgraden.', 'warning'); return false; }
        set((s) => {
          const g = s as unknown as GameData;
          const ag = g.agents.find((x) => x.id === id)!;
          ledger(g, 'Training', -cost, `${ag.name} maximaal geüpgraded (niveau ${MAX_LEVEL})`);
          ag.salary += 4 * Math.max(0, MAX_LEVEL - ag.level);
          ag.level = Math.max(ag.level, MAX_LEVEL); ag.xp = 0;
          Object.keys(ag.skills).forEach((k) => (ag.skills[k] = 100));
          ag.morale = 100; ag.performance = 100;
          notify(g, `🚀 ${ag.name} is maximaal geüpgraded.`, 'success', 'agents');
          checkAchievements(g);
        });
        return true;
      },
      maxUpgradeAll: () => {
        let n = 0;
        for (const a of (get() as unknown as GameData).agents) {
          if (a.level >= MAX_LEVEL && Object.values(a.skills).every((v) => v >= 100)) continue;
          if (get().maxUpgradeAgent(a.id)) n++;
        }
        get().toast(n ? `${n} agents maximaal geüpgraded.` : 'Iedereen is al maximaal.', n ? 'success' : 'info');
        return n;
      },
      updateAgent: (id, patch) => set((s) => { const a = s.agents.find((x) => x.id === id); if (a) Object.assign(a, patch); }),

      // ── approvals & publishing ───────────────────────
      approveProject: (id) => set((s) => {
        const d = s as unknown as GameData;
        const p = d.projects.find((x) => x.id === id);
        if (!p || p.status !== 'Awaiting Approval') return;
        const t = d.tasks.find((x) => x.projectId === id && x.stage === 'approval' && x.status === 'Review');
        if (t) { t.status = 'Completed'; t.quality = projectQuality(p); t.result = 'Goedgekeurd door niels.'; }
        p.stageQuality.approval = projectQuality(p);
        p.stage = 'publishing';
        p.status = 'Awaiting Publish';
        p.history.push({ tick: d.tick, text: 'Goedgekeurd door niels' });
        const pt = createStageTask(d, p, 'publishing');
        pt.status = 'Review';
        pt.agentId = d.agents.find((a) => a.role === 'upload_manager')?.id ?? null;
        pt.documents.push({ id: uid('doc'), name: 'Upload Package', kind: 'metadata', content: `UPLOADPAKKET\nTitel: ${p.title}\nWacht op bevestiging van niels.` });
        bumpMission(d, 'approve');
        addCompanyXp(d, 15);
        notify(d, `✅ "${p.title}" goedgekeurd, klaar om te publiceren (jij bevestigt).`, 'approval', 'projects');
      }),
      rejectProject: (id, to, reason) => set((s) => {
        const d = s as unknown as GameData;
        const p = d.projects.find((x) => x.id === id);
        if (!p) return;
        rejectProjectTo(d, p, to, reason, null);
      }),
      publishProject: (id) => {
        set((s) => {
          const d = s as unknown as GameData;
          const p = d.projects.find((x) => x.id === id);
          if (!p || p.status !== 'Awaiting Publish') return;
          const ch = d.channels.find((c) => c.id === p.channelId)!;
          const q = projectQuality(p);
          const thumbQ = p.stageQuality.thumbnail ?? 60;
          const hookQ = p.stageQuality.titles ?? 60;
          const vid = {
            id: uid('vid'), projectId: p.id, channelId: p.channelId, title: p.title, publishedTick: d.tick, quality: q,
            ctr: +clamp(2.2 + thumbQ / 25 + hookQ / 60 + ch.ctrBoost + rand(-0.5, 0.5), 1, 14).toFixed(1),
            avd: +clamp(26 + q / 4.5 + ch.retentionBoost + rand(-3, 3), 15, 75).toFixed(1),
            views: 0, revenue: 0, likes: 0,
          };
          d.videos.push(vid);
          d.tasks.filter((t) => t.projectId === id && t.stage === 'publishing').forEach((t) => { t.status = 'Completed'; t.result = 'Gepubliceerd.'; t.quality = q; });
          p.status = 'Published';
          p.publishedTick = d.tick;
          p.videoId = vid.id;
          p.history.push({ tick: d.tick, text: 'Gepubliceerd (uploaden doet niels in Studio)' });
          // first-hour views
          const first = Math.round((q * 8 + ch.subscribers * 0.05) * (vid.ctr / 5));
          vid.views += first; ch.views += first;
          bumpMission(d, 'publish');
          addCompanyXp(d, 60);
          d.company.reputation = clamp(d.company.reputation + 1.5, 0, 100);
          const smm = d.agents.find((a) => a.role === 'social_media_manager' || a.role === 'upload_manager');
          if (smm) post(d, smm.id, 'celebration', `🚀 "${p.title}" is LIVE on ${ch.name} (simulated). Predicted CTR ${vid.ctr}% · AVD ${vid.avd}%`);
          d.agents.filter((a) => d.tasks.some((t) => t.projectId === id && t.agentId === a.id)).forEach((a) => addAgentXp(d, a, 15));
          notify(d, `🚀 "${p.title}" gepubliceerd.`, 'success', 'analytics');
          checkAchievements(d);
        });
        get().toast('Video gepubliceerd. Claude maakt het uploadpakket klaar.', 'success');
      },
      cancelProject: (id) => set((s) => {
        const p = s.projects.find((x) => x.id === id);
        if (!p) return;
        p.status = 'Cancelled';
        s.tasks.filter((t) => t.projectId === id && !['Completed', 'Rejected'].includes(t.status)).forEach((t) => {
          t.status = 'Rejected';
          const a = s.agents.find((x) => x.id === t.agentId);
          if (a && a.currentTaskId === t.id) { a.currentTaskId = null; a.state = 'idle'; }
        });
      }),

      // ── threads ──────────────────────────────────────
      likePost: (id) => set((s) => {
        const p = s.posts.find((x) => x.id === id);
        if (!p) return;
        if (p.likes.includes('player')) p.likes = p.likes.filter((l) => l !== 'player');
        else { p.likes.push('player'); bumpMission(s as unknown as GameData, 'like'); }
      }),
      commentPost: (id, text) => set((s) => {
        const p = s.posts.find((x) => x.id === id);
        if (!p) return;
        p.comments.push({ id: uid('c'), authorId: 'player', text, tick: s.tick });
        const a = s.agents.find((x) => x.id === p.authorId);
        if (a) p.comments.push({ id: uid('c'), authorId: a.id, text: 'Thanks boss! 🙌', tick: s.tick });
      }),
      createPost: (content, attachment) => set((s) => {
        const d = s as unknown as GameData;
        d.posts.unshift({ id: uid('po'), authorId: 'player', department: 'hq', kind: attachment ? 'report' : 'update', content, tick: d.tick, likes: [], comments: [], attachment });
        bumpMission(d, 'post');
        // a few agents react
        d.agents.slice().sort(() => Math.random() - 0.5).slice(0, 3).forEach((a) => d.posts[0].likes.push(a.id));
      }),
      sharePost: (id) => set((s) => {
        const d = s as unknown as GameData;
        const p = d.posts.find((x) => x.id === id);
        if (!p) return;
        const author = d.agents.find((a) => a.id === p.authorId)?.name ?? 'CEO';
        d.posts.unshift({ id: uid('po'), authorId: 'player', department: 'hq', kind: 'report', content: `Sharing ${author}'s post with the whole company 👇`, tick: d.tick, likes: [], comments: [], attachment: { title: `${author} wrote`, body: p.content } });
        bumpMission(d, 'post');
      }),
      markAllRead: () => set((s) => { s.notifications.forEach((n) => (n.read = true)); }),

      // ── game mechanics ───────────────────────────────
      buyUpgrade: (id) => {
        const d = get() as unknown as GameData;
        const u = d.upgrades.find((x) => x.id === id);
        if (!u || u.level >= u.maxLevel) return false;
        const cost = Math.round(u.cost * (1 + u.level * 0.6));
        if (d.company.balance < cost) { get().toast('Niet genoeg saldo voor deze upgrade.', 'warning'); return false; }
        set((s) => {
          const g = s as unknown as GameData;
          const up = g.upgrades.find((x) => x.id === id)!;
          up.level += 1;
          ledger(g, 'Upgrades', -cost, `Kantoor-upgrade: ${up.name} N${up.level}`);
          if (id === 'neon') g.company.reputation = clamp(g.company.reputation + 10, 0, 100);
          addCompanyXp(g, 40);
          notify(g, `🛠️ ${up.name} naar niveau ${up.level}.`, 'success', 'upgrades');
          checkAchievements(g);
        });
        get().toast(`${u.name} installed!`, 'success');
        return true;
      },
      claimMission: (id) => set((s) => {
        const d = s as unknown as GameData;
        const m = d.missions.find((x) => x.id === id);
        if (!m || m.claimed || m.progress < m.target) return;
        m.claimed = true;
        addCompanyXp(d, m.rewardXp);
        ledger(d, 'Rewards', m.rewardCash, `Missiebeloning: ${m.title}`);
      }),

      // ── channels ─────────────────────────────────────
      addChannel: (c) => set((s) => {
        const d = s as unknown as GameData;
        d.channels.push({ ...c, id: uid('ch'), subscribers: 0, views: 0, revenue: 0, monetized: false, ctrBoost: 0, retentionBoost: 0, createdTick: d.tick, isDemo: false });
        addCompanyXp(d, 30);
        notify(d, `📺 Nieuw kanaal gestart: ${c.name}`, 'success', 'channels');
        checkAchievements(d);
      }),
      updateChannel: (id, patch) => set((s) => { const c = s.channels.find((x) => x.id === id); if (c) Object.assign(c, patch); }),
      assignDeptToChannel: (dept, channelId) => set((s) => {
        s.agents.filter((a) => a.department === dept).forEach((a) => { a.channelIds = channelId ? [channelId] : []; });
      }),

      // ── war room ─────────────────────────────────────
      openWarCase: (type, channelId) => set((s) => {
        const d = s as unknown as GameData;
        const ch = d.channels.find((c) => c.id === channelId);
        const { analysis, recs } = buildAnalysis(type, ch?.name ?? 'alle kanalen');
        const mgmt = d.agents.filter((a) => ['ceo_agent', 'performance_analyst', 'financial_manager', 'ctr_specialist', 'editing_supervisor'].includes(a.role)).slice(0, 4);
        d.warCases.unshift({
          id: uid('war'), type, channelId, title: `${ISSUE_META[type].label}${ch ? ` · ${ch.name}` : ''}`,
          evidence: evidenceFor(d, type, channelId), status: 'Investigating', openedTick: d.tick, readyTick: d.tick + 6,
          agentIds: mgmt.map((a) => a.id), analysis, recommendations: recs,
        });
        mgmt.forEach((a) => { if (!a.currentTaskId) a.state = 'meeting'; });
        notify(d, `🛡️ Crisiskamer bijeengeroepen: ${ISSUE_META[type].label}`, 'info', 'warroom');
      }),
      approveRecommendation: (caseId, recId) => {
        const d = get() as unknown as GameData;
        const w = d.warCases.find((x) => x.id === caseId);
        const r = w?.recommendations.find((x) => x.id === recId);
        if (!w || !r) return;
        if (d.company.balance < r.cost) { get().toast('Niet genoeg saldo voor dit plan.', 'warning'); return; }
        set((s) => {
          const g = s as unknown as GameData;
          const wc = g.warCases.find((x) => x.id === caseId)!;
          wc.status = 'Resolved'; wc.chosen = recId;
          const targets = wc.channelId ? g.channels.filter((c) => c.id === wc.channelId) : g.channels;
          if (r.effect === 'ctr') targets.forEach((c) => (c.ctrBoost += r.magnitude));
          if (r.effect === 'retention') targets.forEach((c) => (c.retentionBoost += r.magnitude));
          if (r.effect === 'rpm') targets.forEach((c) => (c.rpm = +(c.rpm + r.magnitude).toFixed(2)));
          if (r.effect === 'schedule') targets.forEach((c) => { c.uploadsPerWeek += 1; c.uploadSchedule = `${c.uploadsPerWeek}x / week`; });
          if (r.effect === 'speed') { g.modifiers.speedBoost = r.magnitude; g.modifiers.speedBoostUntil = g.tick + 14 * TICKS_PER_DAY; }
          ledger(g, r.effect === 'speed' ? 'Freelancers' : 'Production', -r.cost, `Plan crisiskamer: ${r.title}`, wc.channelId);
          addCompanyXp(g, 50);
          const ceo = g.agents.find((a) => a.role === 'ceo_agent');
          if (ceo) post(g, ceo.id, 'update', `niels keurde het plan "${r.title}" goed. We voeren het nu uit.`);
          checkAchievements(g);
        });
        get().toast(`Plan goedgekeurd: ${r.title}`, 'success');
      },
      dismissCase: (caseId) => set((s) => { const w = s.warCases.find((x) => x.id === caseId); if (w) w.status = 'Dismissed'; }),

      // ── settings ─────────────────────────────────────
      updateSettings: (patch) => set((s) => { Object.assign(s.settings, patch); }),
      resetGame: () => set(() => ({ ...createSeed(), ...uiDefaults })),
      importSave: (data) => set(() => ({ ...data, ...uiDefaults })),
    })),
    {
      name: 'driftmark-hq',
      version: 1,
      storage: createJSONStorage(() => localStorageAdapter),
      partialize: (s) => {
        // persist only game data (+ speed)
        const { page, selectedDept, selectedAgentId, selectedProjectId, modal, modalPayload, confirm, toasts, notifOpen, paused, ...rest } = s;
        void page; void selectedDept; void selectedAgentId; void selectedProjectId; void modal; void modalPayload; void confirm; void toasts; void notifOpen; void paused;
        return Object.fromEntries(Object.entries(rest).filter(([, v]) => typeof v !== 'function')) as unknown as GameStore;
      },
    },
  ),
);

function evidenceFor(d: GameData, type: WarIssueType, channelId: string | null): string {
  const day = dayOf(d.tick);
  const st = d.stats.filter((x) => (!channelId || x.channelId === channelId) && x.day > day - 8);
  const views = st.reduce((s, x) => s + x.views, 0);
  const ctr = st.length ? st.reduce((s, x) => s + x.ctr, 0) / st.length : 0;
  const avd = st.length ? st.reduce((s, x) => s + x.avd, 0) / st.length : 0;
  switch (type) {
    case 'declining_views': return `Laatste 7 dagen: ${views.toLocaleString('nl-NL')} weergaven.`;
    case 'low_ctr': return `Gem. CTR laatste 7 dagen: ${ctr.toFixed(2)}%.`;
    case 'poor_retention': return `Gem. kijkduur laatste 7 dagen: ${avd.toFixed(1)}%.`;
    case 'production_delays': return `${d.projects.filter((p) => p.status === 'Active' && p.deadlineTick < d.tick).length} projecten te laat · ${d.tasks.filter((t) => t.status === 'Pending').length} taken wachten op een agent.`;
    case 'falling_revenue': return `Inkomsten laatste 7 dagen: €${st.reduce((s, x) => s + x.revenue, 0).toFixed(2)}.`;
  }
}

// convenience selectors
export const useData = useGame;

// ── ECHT-MODUS ─────────────────────────────────────────────
// Acties van de speler worden echte opdrachten voor Claude (zie services/real.ts).
export const MAX_LEVEL = 10;
export const maxUpgradeCost = (a: { level: number }) => { let c = 0; for (let l = a.level; l < MAX_LEVEL; l++) c += 250 * l; return Math.max(c, 500); };
import { order } from '../services/real';
import { stageById } from '../modules/workflows/pipeline';
{
  const g = useGame.getState();
  const toast = (t: string, k?: 'success' | 'info' | 'warning') => useGame.getState().toast(t, k);
  const proj = (id: string | null | undefined) => useGame.getState().projects.find((p) => p.id === id);
  const task = (id: string) => useGame.getState().tasks.find((t) => t.id === id);
  const agent = (id: string | null | undefined) => useGame.getState().agents.find((a) => a.id === id);
  const chan = (id: string) => useGame.getState().channels.find((c) => c.id === id)?.name ?? id;
  const wrap = <K extends keyof Actions>(k: K, describe: (...a: Parameters<Actions[K]>) => string | null) => {
    const orig = g[k] as unknown as (...a: unknown[]) => unknown;
    useGame.setState({ [k]: (...a: unknown[]) => {
      const text = describe(...(a as Parameters<Actions[K]>));
      const r = orig(...a);
      if (text) order(text, toast);
      return r;
    } } as unknown as Partial<GameStore>);
  };
  wrap('startVideo', (i) => `Start een nieuwe video voor ${chan(i.channelId)}.\nTitel: ${i.title}\nOnderwerp: ${i.topic}\nPrioriteit: ${i.priority} · deadline over ${i.deadlineDays} dagen.\nBegin met het verloop (zoals bij video 3) volgens het productiehandboek.`);
  wrap('assignManualTask', (i) => `Nieuwe taak: ${i.title}\n${i.description}\nRol: ${i.role ? roleById(i.role).title : agent(i.agentId) ? roleById(agent(i.agentId)!.role).title : 'vrij'} · prioriteit ${i.priority} · deadline ${i.deadlineDays} dagen${proj(i.projectId) ? ` · project: ${proj(i.projectId)!.title}` : ''}.`);
  wrap('commentTask', (id, text) => `Opmerking bij taak "${task(id)?.title ?? id}": ${text}`);
  wrap('reviewTask', (id, ok, note) => `${ok ? 'Goedgekeurd' : 'Afgekeurd'}: taak "${task(id)?.title ?? id}"${note ? `. Opmerking: ${note}` : ''}.`);
  wrap('setTaskPriority', (id, p) => `Prioriteit van taak "${task(id)?.title ?? id}" naar ${p}.`);
  wrap('approveProject', (id) => `Goedkeuring niels: "${proj(id)?.title}" is goed, ga door naar de volgende stap (klaarmaken voor upload).`);
  wrap('rejectProject', (id, to, reason) => `Afgekeurd: "${proj(id)?.title}" moet terug naar ${stageById(to).label}. Reden: ${reason}`);
  wrap('publishProject', (id) => `Publiceren: "${proj(id)?.title}". Maak titel, beschrijving, tags en thumbnail klaar. (Uploaden naar YouTube doet niels zelf in Studio.)`);
  wrap('cancelProject', (id) => `Stop project: "${proj(id)?.title}". Niet verder aan werken.`);
  wrap('updateAgent', (id, patch) => patch.instructions ? `Nieuwe werkregel voor ${roleById(agent(id)!.role).title}: ${patch.instructions}\nVoeg dit toe aan de werkwijze en het projectgeheugen.` : null);
  wrap('createPost', (content) => `Bericht van niels aan het team: ${content}`);
  wrap('commentPost', (_id, text) => `Reactie van niels: ${text}`);
  wrap('updateChannel', (id, patch) => `Kanaal ${chan(id)} aanpassen: ${Object.entries(patch).map(([k, v]) => `${k} = ${v}`).join(', ')}.`);
  wrap('approveRecommendation', (caseId, recId) => {
    const c = useGame.getState().warCases.find((w) => w.id === caseId);
    const r = c?.recommendations.find((x) => x.id === recId);
    return r ? `War Room: voer deze aanbeveling echt uit voor Driftmark: ${r.title}. ${r.detail}` : null;
  });
}
