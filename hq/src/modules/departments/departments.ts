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
  { id: 'research', name: 'Onderzoek', short: 'Onderzoek', color: '#3b82f6', wall: '#3d6fd6', floor: '#1b2550', icon: '🔎', grid: [0, 0], description: 'Zoekt niches, trends, gaten bij concurrenten en goede onderwerpen.' },
  { id: 'creative', name: 'Creatief', short: 'Creatief', color: '#a855f7', wall: '#7c4dd6', floor: '#231a48', icon: '💡', grid: [1, 0], description: 'Maakt van onderzoek ideeën, titels en hooks die blijven hangen.' },
  { id: 'script', name: 'Script', short: 'Script', color: '#fb923c', wall: '#e8735a', floor: '#2a1f33', icon: '✍️', grid: [2, 0], description: 'Schrijft en controleert elk script.' },
  { id: 'publishing', name: 'Publicatie', short: 'Publicatie', color: '#22d3ee', wall: '#2f8fb8', floor: '#122a3d', icon: '🚀', grid: [0, 1], description: 'Titels, beschrijving, tags, planning en shorts.' },
  { id: 'ceo', name: 'CEO & Statistieken', short: 'CEO & Statistieken', color: '#facc15', wall: '#e8735a', floor: '#2b2238', icon: '👑', grid: [1, 1], description: 'Jouw akkoord, cijfers en strategie.' },
  { id: 'voice', name: 'Stem', short: 'Stem', color: '#ec4899', wall: '#c2457f', floor: '#2d1735', icon: '🎙️', grid: [2, 1], description: 'Stemregie en voice-overs in ElevenLabs.' },
  { id: 'thumbnail', name: 'Thumbnail', short: 'Thumbnail', color: '#f59e0b', wall: '#f08a4b', floor: '#2d2130', icon: '🖼️', grid: [0, 2], description: 'Ontwerpt thumbnails en test varianten.' },
  { id: 'production', name: 'Productie', short: 'Productie', color: '#f43f5e', wall: '#3d6fd6', floor: '#1c1f45', icon: '🎬', grid: [2, 2], description: 'Cast, sets, animatie, renders en montage.' },
];

export const WAR_ROOM = { name: 'Crisiskamer', grid: [1, 2] as [number, number], color: '#ef4444', wall: '#7c1d2e', floor: '#1d1424' };

export const deptById = (id: DepartmentId | 'hq'): DepartmentDef =>
  DEPARTMENTS.find((d) => d.id === id) ?? DEPARTMENTS[4];
