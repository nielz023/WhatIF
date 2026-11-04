import type {
  Achievement, Agent, Channel, DailyStat, IntegrationSettings, LedgerEntry, Mission, Notification,
  Project, Task, ThreadPost, Upgrade, Video, WarCase,
} from '../types';

export interface Company {
  name: string;
  level: number;
  xp: number;
  balance: number;
  reputation: number; // 0-100
  baseSlots: number;
}

export interface Modifiers {
  speedBoostUntil: number; // tick
  speedBoost: number;
}

export interface GameData {
  version: number;
  tick: number;
  company: Company;
  agents: Agent[];
  tasks: Task[];
  projects: Project[];
  videos: Video[];
  channels: Channel[];
  stats: DailyStat[];
  ledger: LedgerEntry[];
  posts: ThreadPost[];
  notifications: Notification[];
  achievements: Achievement[];
  missions: Mission[];
  missionDay: number;
  upgrades: Upgrade[];
  warCases: WarCase[];
  modifiers: Modifiers;
  settings: IntegrationSettings;
  demoMode: boolean;
}

export const DEFAULT_SETTINGS: IntegrationSettings = {
  anthropicKey: '',
  anthropicModel: 'claude-sonnet-5-5',
  openaiKey: '',
  openaiModel: 'gpt-4o-mini',
  llmProvider: 'simulation',
  youtubeApiKey: '',
  threadsToken: '',
  elevenLabsKey: '',
  imageProvider: '',
  supabaseUrl: '',
  supabaseAnonKey: '',
};
