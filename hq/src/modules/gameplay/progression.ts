import type { Achievement, Mission, MissionMetric, Upgrade } from '../../types';
import { uid, pick } from '../../lib/util';

export const companyXpForLevel = (lvl: number) => 250 + (lvl - 1) * 200;

export const ACHIEVEMENTS: Achievement[] = [
  { id: 'first_video', title: 'First Upload', description: 'Publish your first video.', icon: '🎬', xp: 100 },
  { id: 'five_videos', title: 'Content Machine', description: 'Publish 5 videos.', icon: '🏭', xp: 200 },
  { id: 'views_100k', title: '100K Views', description: 'Reach 100,000 total views across all channels.', icon: '👀', xp: 300 },
  { id: 'views_1m', title: 'Millionaire Views', description: 'Reach 1,000,000 total views.', icon: '💎', xp: 800 },
  { id: 'monetized', title: 'Monetized!', description: 'Get your first channel monetized (1,000 subscribers).', icon: '💸', xp: 300 },
  { id: 'rev_1000', title: 'First €1,000', description: 'Earn €1,000 in total ad revenue.', icon: '💶', xp: 400 },
  { id: 'team_10', title: 'Growing Team', description: 'Hire your first new AI agent.', icon: '👥', xp: 150 },
  { id: 'team_20', title: 'Full House', description: 'Employ 20 AI agents.', icon: '🏢', xp: 300 },
  { id: 'first_upgrade', title: 'Interior Designer', description: 'Buy your first office upgrade.', icon: '🛋️', xp: 100 },
  { id: 'war_room', title: 'Crisis Manager', description: 'Resolve your first War Room case.', icon: '🛡️', xp: 200 },
  { id: 'level_5', title: 'Rising Company', description: 'Reach company level 5.', icon: '⭐', xp: 300 },
  { id: 'two_channels', title: 'Network Builder', description: 'Launch a new channel of your own.', icon: '📺', xp: 150 },
  { id: 'agent_lvl5', title: 'Elite Employee', description: 'Train an agent to level 5.', icon: '🎓', xp: 200 },
];

export const UPGRADES: Upgrade[] = [
  { id: 'render_farm', name: 'Render Farm', description: 'GPU racks for the edit bay.', icon: '🖥️', cost: 1500, level: 0, maxLevel: 3, effect: '+15% production speed per level' },
  { id: 'coffee_bar', name: 'Coffee Bar', description: 'Espresso for everyone. Morale stays high.', icon: '☕', cost: 600, level: 0, maxLevel: 2, effect: '+8 morale recovery per level' },
  { id: 'expansion', name: 'Office Expansion', description: 'More desks, more agents.', icon: '🏗️', cost: 2000, level: 0, maxLevel: 3, effect: '+6 agent slots per level' },
  { id: 'neon', name: 'Neon Lighting Pack', description: 'Instagrammable office. Boosts reputation.', icon: '🌈', cost: 800, level: 0, maxLevel: 1, effect: '+10 reputation' },
  { id: 'meeting_pods', name: 'Glass Meeting Pods', description: 'Faster reviews, fewer rejections.', icon: '🫧', cost: 1200, level: 0, maxLevel: 2, effect: '+6 review quality per level' },
  { id: 'training_lab', name: 'Training Lab', description: 'VR training stations.', icon: '🧪', cost: 1000, level: 0, maxLevel: 2, effect: '−25% training cost and time per level' },
  { id: 'studio', name: 'Sound Studio', description: 'Acoustic booth for the voice team.', icon: '🎧', cost: 900, level: 0, maxLevel: 2, effect: '+8 voice quality per level' },
];

const MISSION_TEMPLATES: { metric: MissionMetric; title: (n: number) => string; range: [number, number]; xp: number; cash: number }[] = [
  { metric: 'start_video', title: (n) => `Start ${n} nieuwe video${n > 1 ? "'s" : ''}`, range: [1, 2], xp: 40, cash: 100 },
  { metric: 'publish', title: () => `Publish 1 video`, range: [1, 1], xp: 80, cash: 250 },
  { metric: 'approve', title: (n) => `Approve ${n} deliverable${n > 1 ? 's' : ''} as CEO`, range: [1, 2], xp: 50, cash: 120 },
  { metric: 'like', title: (n) => `Like ${n} Threads-berichten`, range: [2, 4], xp: 25, cash: 50 },
  { metric: 'post', title: () => `Post an update on Threads`, range: [1, 1], xp: 25, cash: 50 },
  { metric: 'train', title: () => `Train an agent`, range: [1, 1], xp: 50, cash: 80 },
  { metric: 'complete_tasks', title: (n) => `Rond ${n} taken af`, range: [4, 8], xp: 60, cash: 150 },
];

export function generateMissions(): Mission[] {
  const pool = [...MISSION_TEMPLATES].sort(() => Math.random() - 0.5).slice(0, 3);
  return pool.map((t) => {
    const n = t.range[0] + Math.floor(Math.random() * (t.range[1] - t.range[0] + 1));
    return { id: uid('ms'), title: t.title(n), metric: t.metric, target: n, progress: 0, rewardXp: t.xp, rewardCash: t.cash, claimed: false };
  });
}

export const RANK_TITLES = ['Garage Startup', 'Bedroom Studio', 'Small Agency', 'Content Studio', 'Media House', 'Creator Network', 'Media Empire'];
export const rankTitle = (lvl: number) => RANK_TITLES[Math.min(RANK_TITLES.length - 1, Math.floor((lvl - 1) / 2))];

export const celebration = () => pick(['🔥', '🚀', '🎉', '💪', '✨', '📈']);
