// ───────────────────────────────────────────────────────────────
// FACELESS YOUTUBE HQ — domain types
// ───────────────────────────────────────────────────────────────

export type DepartmentId =
  | 'research'
  | 'creative'
  | 'script'
  | 'voice'
  | 'production'
  | 'thumbnail'
  | 'publishing'
  | 'ceo';

export type RoleId =
  | 'researcher' | 'niche_analyst' | 'competitor_analyst' | 'topic_finder'
  | 'idea_generator' | 'title_specialist' | 'hook_specialist'
  | 'scriptwriter' | 'storytelling_expert' | 'fact_checker' | 'quality_controller'
  | 'voice_director' | 'voice_generator'
  | 'video_editor' | 'visual_researcher' | 'editing_supervisor'
  | 'thumbnail_designer' | 'ctr_specialist'
  | 'upload_manager' | 'seo_specialist' | 'social_media_manager'
  | 'ceo_agent' | 'financial_manager' | 'performance_analyst';

export type AgentState = 'idle' | 'working' | 'meeting' | 'training';

export interface RoleDef {
  id: RoleId;
  title: string;
  department: DepartmentId;
  description: string;
  skills: string[];
  baseSalary: number; // € per game day
  hireCost: number;
}

export interface Agent {
  id: string;
  name: string;
  role: RoleId;
  department: DepartmentId;
  avatar: { skin: string; hair: string; shirt: string; initials: string };
  personality: string;
  instructions: string;
  skills: Record<string, number>; // 0-100
  level: number;
  xp: number;
  performance: number; // 0-100
  morale: number; // 0-100
  salary: number;
  state: AgentState;
  currentTaskId: string | null;
  taskHistory: string[];
  channelIds: string[]; // empty = all channels
  hiredDay: number;
  trainingUntil?: number; // tick
  completed: number;
}

export type TaskStatus =
  | 'Pending' | 'Assigned' | 'In Progress' | 'Review' | 'Approved' | 'Rejected' | 'Completed';

export type Priority = 'Low' | 'Medium' | 'High' | 'Critical';

export interface TaskComment {
  id: string;
  authorId: string; // agent id or 'player'
  text: string;
  tick: number;
}

export interface TaskDocument {
  id: string;
  name: string;
  kind: 'brief' | 'report' | 'script' | 'audio' | 'video' | 'image' | 'metadata' | 'analysis';
  content: string;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  agentId: string | null;
  projectId: string | null;
  stage: StageId | null;
  kind: 'pipeline' | 'manual' | 'warroom' | 'training';
  priority: Priority;
  status: TaskStatus;
  progress: number; // 0-100
  createdTick: number;
  deadlineTick: number;
  dependencies: string[];
  comments: TaskComment[];
  documents: TaskDocument[];
  result: string | null;
  quality: number | null; // 0-100 once produced
  revision: number;
}

export type StageId =
  | 'research' | 'topic' | 'titles' | 'script' | 'factcheck' | 'voice'
  | 'editing' | 'thumbnail' | 'qc' | 'approval' | 'publishing';

export interface StageDef {
  id: StageId;
  label: string;
  department: DepartmentId;
  roles: RoleId[];
  effort: number; // work units
  deliverable: TaskDocument['kind'];
  deliverableName: string;
  reviewer?: RoleId; // role that reviews output
  rejectTo?: StageId; // where rejected work goes
  manual?: boolean; // requires player
  cost: number; // production cost €
}

export type ProjectStatus = 'Active' | 'Awaiting Approval' | 'Awaiting Publish' | 'Published' | 'Cancelled';

export interface Project {
  id: string;
  title: string;
  topic: string;
  channelId: string;
  stage: StageId;
  status: ProjectStatus;
  createdTick: number;
  deadlineTick: number;
  priority: Priority;
  taskIds: string[];
  stageQuality: Partial<Record<StageId, number>>;
  rejections: number;
  cost: number;
  publishedTick?: number;
  videoId?: string;
  history: { tick: number; text: string }[];
}

export interface Video {
  id: string;
  projectId: string;
  channelId: string;
  title: string;
  publishedTick: number;
  quality: number;
  ctr: number; // %
  avd: number; // average view duration %
  views: number;
  revenue: number;
  likes: number;
}

export interface Channel {
  id: string;
  name: string;
  logo: { emoji: string; color: string };
  niche: string;
  audience: string;
  subscribers: number;
  views: number;
  revenue: number;
  rpm: number;
  uploadSchedule: string; // e.g. "3x / week"
  uploadsPerWeek: number;
  monetized: boolean;
  ctrBoost: number; // temporary modifiers from war room
  retentionBoost: number;
  createdTick: number;
  isDemo: boolean;
}

export interface DailyStat {
  day: number;
  channelId: string;
  views: number;
  subs: number;
  revenue: number;
  ctr: number;
  avd: number;
}

export type LedgerCategory =
  | 'Ad Revenue' | 'Production' | 'Salaries' | 'Freelancers'
  | 'AI Subscriptions' | 'Software' | 'Upgrades' | 'Hiring' | 'Training' | 'Rewards';

export interface LedgerEntry {
  id: string;
  day: number;
  channelId: string | null;
  category: LedgerCategory;
  amount: number; // positive income / negative expense
  note: string;
}

export interface ThreadComment {
  id: string;
  authorId: string;
  text: string;
  tick: number;
}

export interface ThreadPost {
  id: string;
  authorId: string; // agent id or 'player'
  department: DepartmentId | 'hq';
  kind: 'update' | 'report' | 'handoff' | 'celebration' | 'question' | 'alert';
  content: string;
  tick: number;
  likes: string[]; // agent ids or 'player'
  comments: ThreadComment[];
  attachment?: { title: string; body: string };
  isDemo?: boolean;
}

export interface Notification {
  id: string;
  tick: number;
  text: string;
  kind: 'info' | 'success' | 'warning' | 'approval' | 'achievement';
  read: boolean;
  link?: PageId;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  xp: number;
  unlockedTick?: number;
}

export interface Mission {
  id: string;
  title: string;
  metric: MissionMetric;
  target: number;
  progress: number;
  rewardXp: number;
  rewardCash: number;
  claimed: boolean;
}

export type MissionMetric =
  | 'publish' | 'approve' | 'like' | 'train' | 'start_video' | 'hire' | 'post' | 'complete_tasks';

export interface Upgrade {
  id: string;
  name: string;
  description: string;
  cost: number;
  icon: string;
  level: number;
  maxLevel: number;
  effect: string;
}

export type WarIssueType =
  | 'declining_views' | 'low_ctr' | 'poor_retention' | 'production_delays' | 'falling_revenue';

export interface WarRecommendation {
  id: string;
  title: string;
  detail: string;
  cost: number;
  effect: 'ctr' | 'retention' | 'speed' | 'schedule' | 'rpm';
  magnitude: number;
}

export interface WarCase {
  id: string;
  type: WarIssueType;
  channelId: string | null;
  title: string;
  evidence: string;
  status: 'Investigating' | 'Ready' | 'Resolved' | 'Dismissed';
  openedTick: number;
  readyTick: number;
  agentIds: string[];
  analysis: string[];
  recommendations: WarRecommendation[];
  chosen?: string;
}

export type PageId =
  | 'driftmark' | 'hq' | 'projects' | 'agents' | 'channels' | 'analytics' | 'threads'
  | 'finances' | 'upgrades' | 'achievements' | 'settings' | 'warroom' | 'videos' | 'kanaal' | 'meer' | 'coach';

export interface IntegrationSettings {
  anthropicKey: string;
  anthropicModel: string;
  openaiKey: string;
  openaiModel: string;
  llmProvider: 'simulation' | 'anthropic' | 'openai';
  youtubeApiKey: string;
  threadsToken: string;
  elevenLabsKey: string;
  imageProvider: string;
  supabaseUrl: string;
  supabaseAnonKey: string;
}
