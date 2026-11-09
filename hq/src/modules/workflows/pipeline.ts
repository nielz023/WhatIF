import type { StageDef, StageId } from '../../types';

/**
 * The production pipeline. Order matters.
 * Research → Topic → Titles & Hooks → Script → Fact Check → Voice → Editing → Thumbnail → QC → CEO Approval → Publishing
 */
export const PIPELINE: StageDef[] = [
  { id: 'research', label: 'Onderzoek', department: 'research', roles: ['researcher', 'niche_analyst', 'competitor_analyst'], effort: 60, deliverable: 'report', deliverableName: 'Onderzoeksverslag', cost: 6 },
  { id: 'topic', label: 'Onderwerp kiezen', department: 'research', roles: ['topic_finder', 'niche_analyst', 'researcher'], effort: 40, deliverable: 'brief', deliverableName: 'Onderwerpenlijst', cost: 4 },
  { id: 'titles', label: 'Titels & hooks', department: 'creative', roles: ['title_specialist', 'hook_specialist', 'idea_generator'], effort: 50, deliverable: 'brief', deliverableName: 'Titels en hooks', cost: 5 },
  { id: 'script', label: 'Script schrijven', department: 'script', roles: ['scriptwriter', 'storytelling_expert'], effort: 110, deliverable: 'script', deliverableName: 'Volledig script', cost: 18 },
  { id: 'factcheck', label: 'Feiten checken', department: 'script', roles: ['fact_checker'], effort: 45, deliverable: 'report', deliverableName: 'Feitencheck', reviewer: 'fact_checker', rejectTo: 'script', cost: 5 },
  { id: 'voice', label: 'Voice-over', department: 'voice', roles: ['voice_generator', 'voice_director'], effort: 60, deliverable: 'audio', deliverableName: 'Voice-over', cost: 22 },
  { id: 'editing', label: 'Animatie & montage', department: 'production', roles: ['video_editor', 'visual_researcher', 'editing_supervisor'], effort: 140, deliverable: 'video', deliverableName: 'Montage', cost: 45 },
  { id: 'thumbnail', label: 'Thumbnail', department: 'thumbnail', roles: ['thumbnail_designer', 'ctr_specialist'], effort: 55, deliverable: 'image', deliverableName: 'Thumbnailvarianten', cost: 12 },
  { id: 'qc', label: 'Kwaliteitscheck', department: 'production', roles: ['quality_controller', 'editing_supervisor'], effort: 40, deliverable: 'report', deliverableName: 'Afvinklijst kwaliteit', reviewer: 'quality_controller', rejectTo: 'editing', cost: 4 },
  { id: 'approval', label: 'Akkoord niels', department: 'ceo', roles: ['ceo_agent'], effort: 20, deliverable: 'analysis', deliverableName: 'Akkoord', manual: true, cost: 0 },
  { id: 'publishing', label: 'Upload', department: 'publishing', roles: ['upload_manager', 'seo_specialist', 'social_media_manager'], effort: 35, deliverable: 'metadata', deliverableName: 'Uploadpakket', manual: true, cost: 3 },
];

export const stageById = (id: StageId) => PIPELINE.find((s) => s.id === id)!;
export const stageIndex = (id: StageId) => PIPELINE.findIndex((s) => s.id === id);
export const nextStage = (id: StageId): StageId | null => PIPELINE[stageIndex(id) + 1]?.id ?? null;
export const stageProgress = (id: StageId) => (stageIndex(id) / (PIPELINE.length - 1)) * 100;
