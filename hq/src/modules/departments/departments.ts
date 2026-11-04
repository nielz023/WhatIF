import type { DepartmentId } from '../../types';

export interface DepartmentDef {
  id: DepartmentId;
  name: string;
  short: string;
  color: string; // neon accent
  wall: string; // wall paint
  floor: string;
  icon: string;
  grid: [number, number]; // col, row in office layout
  description: string;
}

export const DEPARTMENTS: DepartmentDef[] = [
  { id: 'research', name: 'Research Department', short: 'Research', color: '#3b82f6', wall: '#3d6fd6', floor: '#1b2550', icon: '🔎', grid: [0, 0], description: 'Finds niches, trends, competitor gaps and validated topics.' },
  { id: 'creative', name: 'Creative Department', short: 'Creative', color: '#a855f7', wall: '#7c4dd6', floor: '#231a48', icon: '💡', grid: [1, 0], description: 'Turns research into ideas, titles and scroll-stopping hooks.' },
  { id: 'script', name: 'Script Department', short: 'Script', color: '#fb923c', wall: '#e8735a', floor: '#2a1f33', icon: '✍️', grid: [2, 0], description: 'Writes, structures and fact-checks every script.' },
  { id: 'publishing', name: 'Publishing Department', short: 'Publishing', color: '#22d3ee', wall: '#2f8fb8', floor: '#122a3d', icon: '🚀', grid: [0, 1], description: 'SEO, metadata, scheduling and distribution.' },
  { id: 'ceo', name: 'CEO & Analytics Department', short: 'CEO & Analytics', color: '#facc15', wall: '#e8735a', floor: '#2b2238', icon: '👑', grid: [1, 1], description: 'Executive approvals, finances and performance analytics.' },
  { id: 'voice', name: 'Voice Department', short: 'Voice', color: '#ec4899', wall: '#c2457f', floor: '#2d1735', icon: '🎙️', grid: [2, 1], description: 'Voice direction and AI voice-over generation.' },
  { id: 'thumbnail', name: 'Thumbnail Department', short: 'Thumbnail', color: '#f59e0b', wall: '#f08a4b', floor: '#2d2130', icon: '🖼️', grid: [0, 2], description: 'Designs and A/B tests high-CTR thumbnails.' },
  { id: 'production', name: 'Production Department', short: 'Production', color: '#f43f5e', wall: '#3d6fd6', floor: '#1c1f45', icon: '🎬', grid: [2, 2], description: 'Video editing, b-roll research and supervision.' },
];

export const WAR_ROOM = { name: 'War Room', grid: [1, 2] as [number, number], color: '#ef4444', wall: '#7c1d2e', floor: '#1d1424' };

export const deptById = (id: DepartmentId | 'hq'): DepartmentDef =>
  DEPARTMENTS.find((d) => d.id === id) ?? DEPARTMENTS[4];
