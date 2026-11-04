import type { StageDef, StageId } from '../../types';

/**
 * The production pipeline. Order matters.
 * Research → Topic → Titles & Hooks → Script → Fact Check → Voice → Editing → Thumbnail → QC → CEO Approval → Publishing
 */
export const PIPELINE: StageDef[] = [
  { id: 'research', label: 'Research', department: 'research', roles: ['researcher', 'niche_analyst', 'competitor_analyst'], effort: 60, deliverable: 'report', deliverableName: 'Research Brief', cost: 6 },
  { id: 'topic', label: 'Topic Selection', department: 'research', roles: ['topic_finder', 'niche_analyst', 'researcher'], effort: 40, deliverable: 'brief', deliverableName: 'Topic Shortlist', cost: 4 },
  { id: 'titles', label: 'Titles & Hooks', department: 'creative', roles: ['title_specialist', 'hook_specialist', 'idea_generator'], effort: 50, deliverable: 'brief', deliverableName: 'Title & Hook Pack', cost: 5 },
  { id: 'script', label: 'Scriptwriting', department: 'script', roles: ['scriptwriter', 'storytelling_expert'], effort: 110, deliverable: 'script', deliverableName: 'Full Script', cost: 18 },
  { id: 'factcheck', label: 'Fact Checking', department: 'script', roles: ['fact_checker'], effort: 45, deliverable: 'report', deliverableName: 'Fact-Check Report', reviewer: 'fact_checker', rejectTo: 'script', cost: 5 },
  { id: 'voice', label: 'Voice-over', department: 'voice', roles: ['voice_generator', 'voice_director'], effort: 60, deliverable: 'audio', deliverableName: 'Voice-over Track (simulated)', cost: 22 },
  { id: 'editing', label: 'Video Editing', department: 'production', roles: ['video_editor', 'visual_researcher', 'editing_supervisor'], effort: 140, deliverable: 'video', deliverableName: 'Edited Cut (simulated)', cost: 45 },
  { id: 'thumbnail', label: 'Thumbnail', department: 'thumbnail', roles: ['thumbnail_designer', 'ctr_specialist'], effort: 55, deliverable: 'image', deliverableName: 'Thumbnail Variants (simulated)', cost: 12 },
  { id: 'qc', label: 'Quality Control', department: 'production', roles: ['quality_controller', 'editing_supervisor'], effort: 40, deliverable: 'report', deliverableName: 'QC Checklist', reviewer: 'quality_controller', rejectTo: 'editing', cost: 4 },
  { id: 'approval', label: 'CEO Approval', department: 'ceo', roles: ['ceo_agent'], effort: 20, deliverable: 'analysis', deliverableName: 'Approval Memo', manual: true, cost: 0 },
  { id: 'publishing', label: 'Publishing', department: 'publishing', roles: ['upload_manager', 'seo_specialist', 'social_media_manager'], effort: 35, deliverable: 'metadata', deliverableName: 'Upload Package', manual: true, cost: 3 },
];

export const stageById = (id: StageId) => PIPELINE.find((s) => s.id === id)!;
export const stageIndex = (id: StageId) => PIPELINE.findIndex((s) => s.id === id);
export const nextStage = (id: StageId): StageId | null => PIPELINE[stageIndex(id) + 1]?.id ?? null;
export const stageProgress = (id: StageId) => (stageIndex(id) / (PIPELINE.length - 1)) * 100;
