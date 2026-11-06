import type { Achievement, Mission, MissionMetric, Upgrade } from '../../types';
import { uid, pick } from '../../lib/util';

export const companyXpForLevel = (lvl: number) => 250 + (lvl - 1) * 200;

export const ACHIEVEMENTS: Achievement[] = [
  // geen prestaties meer voor geld, aannemen, upgrades of niveaus (niels 2026-11-06)
  { id: 'first_video', title: 'Eerste upload', description: 'Publiceer je eerste video.', icon: '🎬', xp: 100 },
  { id: 'five_videos', title: 'Contentmachine', description: "Publiceer 5 video's.", icon: '🏭', xp: 200 },
  { id: 'views_100k', title: '100K weergaven', description: 'Haal samen 100.000 weergaven.', icon: '👀', xp: 300 },
  { id: 'views_1m', title: 'Een miljoen weergaven', description: 'Haal samen 1.000.000 weergaven.', icon: '💎', xp: 800 },
  { id: 'war_room', title: 'Crisismanager', description: 'Los je eerste zaak in de crisiskamer op.', icon: '🛡️', xp: 200 },
  { id: 'two_channels', title: 'Netwerkbouwer', description: 'Start een eigen nieuw kanaal.', icon: '📺', xp: 150 },
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
  { metric: 'start_video', title: (n) => `Start ${n} nieuwe ${n > 1 ? "video's" : 'video'}`, range: [1, 2], xp: 40, cash: 100 },
  { metric: 'publish', title: (n) => `Publiceer ${n} ${n > 1 ? "video's" : 'video'}`, range: [1, 1], xp: 80, cash: 250 },
  { metric: 'approve', title: (n) => `Keur ${n} ${n > 1 ? 'opleveringen' : 'oplevering'} goed`, range: [1, 2], xp: 50, cash: 120 },
  { metric: 'like', title: (n) => `Like ${n} berichten van het team`, range: [2, 4], xp: 25, cash: 50 },
  { metric: 'post', title: () => 'Plaats een bericht voor het team', range: [1, 1], xp: 25, cash: 50 },
  // geen trainingsmissie meer: training kostte speelgeld (niels 2026-11-06)
  { metric: 'complete_tasks', title: (n) => `Rond ${n} taken af`, range: [4, 8], xp: 60, cash: 150 },
];

/** De titel van een missie in het Nederlands (ook voor missies die nog met een Engelse titel bewaard zijn). */
export const missionTitle = (m: Mission) => MISSION_TEMPLATES.find((t) => t.metric === m.metric)?.title(m.target) ?? m.title;

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
