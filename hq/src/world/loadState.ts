/** Laadstand van het 3D-kantoor (voor het laadscherm). Klein bestand, zodat het hoofdscherm het kan lezen zonder three.js te laden. */
import { create } from 'zustand';

export const useOfficeLoad = create<{ p: number; stap: string; done: boolean; failed: boolean }>(() => ({ p: 0, stap: 'Kantoor openen…', done: false, failed: false }));
export const setLoad = (p: number, stap?: string) => useOfficeLoad.setState((s) => ({ p: Math.max(s.p, Math.min(1, p)), ...(stap ? { stap } : {}) }));
