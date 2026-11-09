/**
 * Praten met de figuurtjes (niels 2026-11-09). Gedeelde stand tussen het 3D-kantoor (crew.tsx zoekt wie er vlak voor je
 * staat en laat tekstballonnetjes zien) en de schermlaag (TalkPanel.tsx: het gesprek, typen of inspreken).
 * Antwoorden komen van Claude via de sample-capability (zelfde als de coach); in een lokale test vallen ze terug op
 * vaste zinnen. De stem komt van de browser (speechSynthesis), per karakter een eigen toonhoogte en tempo.
 */
import { create } from 'zustand';
import type { CrewMember } from './crew';
import { personaOf, halloZin, type Persona } from './persona';
import { getSample } from '../services/coach';
import { useLive } from '../services/live';
import { walkLock } from './walkState';

export interface TalkMsg { van: 'ik' | 'zij'; tekst: string }
export interface Near { key: string; naam: string; kleur: string; d: number }

interface TalkState {
  /** wie er tijdens het rondlopen vlak voor je staat (E = praten) */
  near: Near | null;
  /** met wie je nu praat */
  open: { key: string; m: CrewMember; p: Persona } | null;
  /** gesprekken per figuurtje (deze sessie) */
  log: Record<string, TalkMsg[]>;
  bezig: boolean;
  /** stem aan of uit (onthouden in de browser) */
  stem: boolean;
  /** tekstballonnetjes boven de hoofden: tekst en tot wanneer (performance.now() / 1000) */
  bubbles: Record<string, { tekst: string; tot: number }>;
  setNear: (n: Near | null) => void;
  zeg: (key: string, tekst: string, sec?: number) => void;
  setStem: (on: boolean) => void;
}

const leesStem = () => { try { return localStorage.getItem('dm-stem') !== 'uit'; } catch { return true; } };

export const useTalk = create<TalkState>((set) => ({
  near: null, open: null, log: {}, bezig: false, stem: leesStem(), bubbles: {},
  setNear: (n) => set((s) => { if (s.near?.key === n?.key) { if (s.near && n) s.near.d = n.d; return {}; } return { near: n }; }),
  zeg: (key, tekst, sec) => set((s) => ({ bubbles: { ...s.bubbles, [key]: { tekst, tot: performance.now() / 1000 + (sec ?? Math.min(9, 2.5 + tekst.length / 14)) } } })),
  setStem: (on) => { try { localStorage.setItem('dm-stem', on ? 'aan' : 'uit'); } catch { /* */ } if (!on) stil(); set({ stem: on }); },
}));

/** alle figuurtjes die nu in het kantoor staan (crew.tsx zet deze lijst) */
export const crewIndex = { members: new Map<string, CrewMember>() };

/* ---------- stem van de browser ---------- */
let stemmen: SpeechSynthesisVoice[] = [];
function laadStemmen() { try { stemmen = window.speechSynthesis?.getVoices() ?? []; } catch { stemmen = []; } }
if (typeof window !== 'undefined' && 'speechSynthesis' in window) { laadStemmen(); window.speechSynthesis.onvoiceschanged = laadStemmen; }
export function stil() { try { window.speechSynthesis?.cancel(); } catch { /* */ } }
export function spreek(p: Persona, tekst: string) {
  if (!useTalk.getState().stem || !('speechSynthesis' in window)) return;
  try {
    const u = new SpeechSynthesisUtterance(tekst.replace(/[*_#>`]/g, ''));
    const nl = stemmen.filter((v) => /^nl/i.test(v.lang));
    u.lang = 'nl-NL'; if (nl.length) u.voice = nl[Math.floor((p.stem.pitch * 7) % nl.length)];
    u.pitch = Math.max(0, Math.min(2, p.stem.pitch)); u.rate = Math.max(0.5, Math.min(1.6, p.stem.rate));
    window.speechSynthesis.cancel(); window.speechSynthesis.speak(u);
  } catch { /* geen stem */ }
}

/* ---------- gesprek ---------- */
export function begin(m: CrewMember) {
  const p = personaOf(m);
  walkLock.on = true;
  try { if (document.pointerLockElement) document.exitPointerLock(); } catch { /* */ }
  const s = useTalk.getState(); const oud = s.log[m.key] ?? [];
  const hallo = halloZin(p);
  useTalk.setState({ open: { key: m.key, m, p }, log: { ...s.log, [m.key]: oud.length ? oud : [{ van: 'zij', tekst: hallo }] } });
  if (!oud.length) { s.zeg(m.key, hallo); spreek(p, hallo); }
}
export function sluit() { stil(); if (useTalk.getState().open) walkLock.on = false; useTalk.setState({ open: null }); }

function kantoor(): string {
  const d = useLive.getState().data; if (!d) return '';
  const st = d.channel?.stats?.map((x) => `${x.label}: ${x.value}`).join(', ');
  const vids = d.videos?.map((v) => { const a = v.steps?.find((x) => x.active); return `video ${v.nr} "${v.title}" (${v.status}${a ? `, nu: ${a.label}` : ''})`; }).join('; ');
  const act = d.activity?.filter((a) => a.state === 'working' || a.state === 'blocked' || a.state === 'review_ready').slice(0, 6).map((a) => `${a.title} (${a.state === 'working' ? 'bezig' : 'wacht op niels'})`).join('; ');
  return [st && `Kanaal Driftmark: ${st}.`, vids && `Video's: ${vids}.`, act && `Lopende taken: ${act}.`].filter(Boolean).join('\n');
}

function prompt(p: Persona, m: CrewMember, msgs: TalkMsg[]) {
  const regels = [
    `Je speelt een figuurtje in Driftmark HQ, het digitale 3D-kantoor van het YouTube-kanaal Driftmark (3D "What If"-video's, @driftmark3d).`,
    `Wie je bent: ${p.naam}. ${p.karakter}`,
    p.uitVideo?.length ? `Echte zinnen en momenten uit de video's (Engels, mag je naar verwijzen): ${p.uitVideo.join(' · ')}` : '',
    m.doing ? `Wat je nu doet in het kantoor (in de derde persoon): ${m.doing}.` : '',
    `Je praat met niels, de maker van het kanaal en de echte baas. Hij loopt rond in het kantoor.`,
    `Wat er nu echt speelt:\n${kantoor()}`,
    `Regels: antwoord in het Nederlands, in karakter, kort (1 tot 3 zinnen, als in een gesprek, geen opsommingen of kopjes). Verzin geen cijfers of feiten over het kanaal die hierboven niet staan; weet je iets niet, zeg dat dan in karakter. Nooit grof of gemeen.`,
  ].filter(Boolean).join('\n\n');
  const gesprek = msgs.slice(-12).map((x) => ({ role: x.van === 'ik' ? 'user' as const : 'assistant' as const, content: x.tekst }));
  // de eerste beurt moet van de gebruiker zijn: de regels gaan voor de eerste vraag
  const eerste = gesprek.findIndex((x) => x.role === 'user');
  const rest = gesprek.slice(eerste);
  if (rest.length) rest[0] = { role: 'user', content: `${regels}\n\n---\nniels zegt: ${rest[0].content}` };
  return rest;
}

const REserve = ['Haha, goeie vraag. Daar moet ik even over nadenken.', 'Zeg dat nog eens? Het is hier best druk.', 'Daar weet ik eigenlijk niks van. Vraag het de coach eens!'];

export async function stuur(tekst: string) {
  const s = useTalk.getState(); const o = s.open; if (!o || !tekst.trim() || s.bezig) return;
  const msgs: TalkMsg[] = [...(s.log[o.key] ?? []), { van: 'ik', tekst: tekst.trim() }];
  useTalk.setState({ log: { ...s.log, [o.key]: [...msgs, { van: 'zij', tekst: '…' }] }, bezig: true });
  const zet = (t: string) => useTalk.setState((st) => ({ log: { ...st.log, [o.key]: [...msgs, { van: 'zij', tekst: t }] } }));
  let antwoord = '';
  const sample = getSample();
  try {
    if (!sample) throw new Error('geen sample');
    const r = await sample(prompt(o.p, o.m, msgs), { cache: false, modelTier: 'quick', onText: ({ text }: { text: string }) => { antwoord = text; zet(text || '…'); } });
    antwoord = (r?.text ?? antwoord).trim();
  } catch {
    antwoord = REserve[Math.floor(Math.random() * REserve.length)];
  }
  if (!antwoord) antwoord = '…';
  zet(antwoord); useTalk.setState({ bezig: false });
  useTalk.getState().zeg(o.key, antwoord); spreek(o.p, antwoord);
}
