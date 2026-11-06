/**
 * RUSTIGE INTERFACE-GELUIDJES (niels 2026-11-06: "satisfying kalmerende sound effects
 * wanneer je wat aanklikt of naar beneden scrolt, en waar het nog meer toepasselijk is").
 * Alles wordt live gemaakt met de Web Audio API (geen bestanden): zachte sinus-tikjes,
 * glazen klokjes in een pentatonische toonladder, een zacht "whoosh" bij panelen.
 * Aan/uit staat in localStorage (dm-geluid). Volume bewust laag.
 */
type Kind = 'click' | 'hover' | 'scroll' | 'open' | 'close' | 'zoom' | 'send' | 'success' | 'tab' | 'notify' | 'applause' | 'alarm' | 'ping';

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let verb: ConvolverNode | null = null;
let on = (() => { try { return localStorage.getItem('dm-geluid') !== 'uit'; } catch { return true; } })();
const listeners = new Set<(v: boolean) => void>();
const PENTA = [523.25, 587.33, 659.25, 783.99, 880, 1046.5, 1174.66]; // C-pentatonisch, rustig en altijd "goed"

function ac(): AudioContext | null {
  if (!on) return null;
  try {
    if (!ctx) {
      const C = window.AudioContext ?? (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (!C) return null;
      ctx = new C();
      master = ctx.createGain(); master.gain.value = 0.32;
      // kleine galm: korte ruis-impuls die uitsterft
      verb = ctx.createConvolver();
      const len = ctx.sampleRate * 1.4, buf = ctx.createBuffer(2, len, ctx.sampleRate);
      for (let ch = 0; ch < 2; ch++) { const d = buf.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / len, 3.2); }
      verb.buffer = buf;
      const wet = ctx.createGain(); wet.gain.value = 0.22;
      verb.connect(wet).connect(master);
      master.connect(ctx.destination);
    }
    if (ctx.state === 'suspended') void ctx.resume();
    return ctx;
  } catch { return null; }
}

function tone(freq: number, { t = 0, dur = 0.18, vol = 0.12, type = 'sine' as OscillatorType, glide = 0, wet = true, attack = 0.006 } = {}) {
  const c = ac(); if (!c || !master) return;
  const t0 = c.currentTime + t;
  const o = c.createOscillator(); o.type = type; o.frequency.setValueAtTime(freq, t0);
  if (glide) o.frequency.exponentialRampToValueAtTime(Math.max(40, freq * glide), t0 + dur);
  const g = c.createGain();
  g.gain.setValueAtTime(0.0001, t0);
  g.gain.exponentialRampToValueAtTime(vol, t0 + attack);
  g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  o.connect(g); g.connect(master); if (wet && verb) g.connect(verb);
  o.start(t0); o.stop(t0 + dur + 0.05);
}

function noise({ dur = 0.45, vol = 0.05, from = 300, to = 2400, t = 0 } = {}) {
  const c = ac(); if (!c || !master) return;
  const t0 = c.currentTime + t;
  const len = Math.floor(c.sampleRate * dur), buf = c.createBuffer(1, len, c.sampleRate), d = buf.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
  const src = c.createBufferSource(); src.buffer = buf;
  const f = c.createBiquadFilter(); f.type = 'bandpass'; f.Q.value = 1.4;
  f.frequency.setValueAtTime(from, t0); f.frequency.exponentialRampToValueAtTime(to, t0 + dur);
  const g = c.createGain(); g.gain.setValueAtTime(0.0001, t0); g.gain.exponentialRampToValueAtTime(vol, t0 + dur * 0.35); g.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
  src.connect(f).connect(g); g.connect(master); if (verb) g.connect(verb);
  src.start(t0); src.stop(t0 + dur + 0.05);
}

let last: Record<string, number> = {};
let step = 0;
export function play(kind: Kind) {
  if (!on) return;
  const now = performance.now();
  const gap = { hover: 70, scroll: 85, click: 40, tab: 60 }[kind as 'hover'] ?? 0;
  if (gap && now - (last[kind] ?? 0) < gap) return;
  last[kind] = now;
  switch (kind) {
    case 'click': { const f = PENTA[(step++ % 3) + 2]; tone(f, { dur: 0.16, vol: 0.09 }); tone(f * 2, { dur: 0.08, vol: 0.025, wet: false }); break; }
    case 'tab': tone(PENTA[4], { dur: 0.14, vol: 0.07 }); tone(PENTA[6], { t: 0.05, dur: 0.16, vol: 0.05 }); break;
    case 'hover': tone(1567.98, { dur: 0.05, vol: 0.012, wet: false }); break;
    case 'scroll': { const f = PENTA[step++ % PENTA.length] * 1.5; tone(f, { dur: 0.06, vol: 0.016, wet: false, type: 'triangle' }); break; }
    case 'open': noise({ dur: 0.5, vol: 0.035, from: 260, to: 2600 }); tone(PENTA[2], { t: 0.18, dur: 0.5, vol: 0.06 }); tone(PENTA[4], { t: 0.26, dur: 0.6, vol: 0.05 }); break;
    case 'close': noise({ dur: 0.35, vol: 0.025, from: 2200, to: 300 }); tone(PENTA[3], { dur: 0.3, vol: 0.05, glide: 0.75 }); break;
    case 'zoom': noise({ dur: 0.7, vol: 0.03, from: 200, to: 1400 }); tone(PENTA[0], { t: 0.1, dur: 0.9, vol: 0.05, attack: 0.15 }); tone(PENTA[3], { t: 0.25, dur: 0.9, vol: 0.04, attack: 0.15 }); break;
    case 'send': [0, 2, 4, 5].forEach((n, i) => tone(PENTA[n], { t: i * 0.07, dur: 0.5, vol: 0.06 })); break;
    case 'success': tone(PENTA[3], { dur: 0.6, vol: 0.06 }); tone(PENTA[5], { t: 0.09, dur: 0.8, vol: 0.05 }); break;
    case 'notify': tone(PENTA[5], { dur: 0.4, vol: 0.05 }); tone(PENTA[3], { t: 0.12, dur: 0.6, vol: 0.045 }); break;
    case 'ping': tone(1318.5, { dur: 0.25, vol: 0.05 }); tone(1975.5, { t: 0.08, dur: 0.4, vol: 0.04 }); break;
    case 'applause': { // klappende collega's: veel korte ruisstootjes, eerst aanzwellend dan uitstervend
      for (let i = 0; i < 70; i++) { const t = Math.pow(Math.random(), 1.4) * 2.8; clap(t, 0.02 + Math.random() * 0.03 * (1 - t / 3.2)); }
      [0, 2, 4, 6].forEach((n, i) => tone(PENTA[n % PENTA.length] * (n > 4 ? 1 : 1), { t: 0.1 + i * 0.09, dur: 0.7, vol: 0.04 }));
      break;
    }
    case 'alarm': { // zachte tweetonige sirene, één keer
      for (let k = 0; k < 3; k++) { tone(660, { t: k * 0.55, dur: 0.26, vol: 0.05, type: 'triangle', glide: 1.35, wet: false }); tone(880, { t: k * 0.55 + 0.27, dur: 0.26, vol: 0.045, type: 'triangle', glide: 0.75, wet: false }); }
      break;
    }
  }
}

function clap(t: number, vol: number) {
  const c = ac(); if (!c || !master) return;
  const t0 = c.currentTime + t; const len = Math.floor(c.sampleRate * 0.05);
  const buf = c.createBuffer(1, len, c.sampleRate); const d = buf.getChannelData(0);
  for (let i = 0; i < len; i++) d[i] = (Math.random() * 2 - 1) * Math.exp(-i / (len * 0.18));
  const src = c.createBufferSource(); src.buffer = buf;
  const f = c.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 900 + Math.random() * 1800; f.Q.value = 0.9;
  const g = c.createGain(); g.gain.value = vol;
  src.connect(f).connect(g); g.connect(master); if (verb) g.connect(verb);
  src.start(t0);
}

/* ---------- KANTOORGELUID (verbeterpunt: geroezemoes, toetsenborden, eigen volume) ---------- */
let amb: { gain: GainNode; murmur: GainNode; timer: number } | null = null;
let ambVol = (() => { try { const v = parseFloat(localStorage.getItem('dm-kantoor') ?? ''); return isNaN(v) ? 0.35 : v; } catch { return 0.35; } })();
let ambLevel = { typing: 3, people: 0.5 };
const ambListeners = new Set<(v: number) => void>();
export const officeVolume = () => ambVol;
export function setOfficeVolume(v: number) {
  ambVol = Math.max(0, Math.min(1, v)); try { localStorage.setItem('dm-kantoor', String(ambVol)); } catch { /* */ }
  if (amb && ctx) amb.gain.gain.setTargetAtTime(ambVol * 0.5, ctx.currentTime, 0.2);
  ambListeners.forEach((f) => f(ambVol));
}
export function onOfficeVolume(f: (v: number) => void) { ambListeners.add(f); return () => { ambListeners.delete(f); }; }
/** door het kantoor bijgewerkt: hoeveel mensen typen en hoe druk het is (0..1) */
export function setAmbience(typing: number, people: number) { ambLevel = { typing, people }; if (amb && ctx) amb.murmur.gain.setTargetAtTime(0.04 + people * 0.1, ctx.currentTime, 1.5); }
function startAmbience() {
  const c = ac(); if (!c || !master || amb) return;
  const gain = c.createGain(); gain.gain.value = ambVol * 0.5; gain.connect(master);
  // geroezemoes: zachte ruis door een laagdoorlaatfilter, langzaam golvend
  const len = c.sampleRate * 4; const buf = c.createBuffer(1, len, c.sampleRate); const d = buf.getChannelData(0);
  let b0 = 0, b1 = 0; for (let i = 0; i < len; i++) { const w = Math.random() * 2 - 1; b0 = 0.99 * b0 + w * 0.06; b1 = 0.6 * b1 + w * 0.2; d[i] = b0 + b1 * 0.25; }
  const src = c.createBufferSource(); src.buffer = buf; src.loop = true;
  const lp = c.createBiquadFilter(); lp.type = 'lowpass'; lp.frequency.value = 520; lp.Q.value = 0.4;
  const murmur = c.createGain(); murmur.gain.value = 0.04 + ambLevel.people * 0.1;
  const lfo = c.createOscillator(); lfo.frequency.value = 0.13; const lfoG = c.createGain(); lfoG.gain.value = 0.025; lfo.connect(lfoG).connect(murmur.gain); lfo.start();
  src.connect(lp).connect(murmur).connect(gain); src.start();
  // toetsenborden: losse zachte tikjes, meer als er meer mensen typen
  const timer = window.setInterval(() => {
    if (!on || !ctx || ctx.state !== 'running' || ambVol <= 0.01 || document.hidden) return;
    const p = Math.min(0.85, ambLevel.typing * 0.07);
    if (Math.random() > p) return;
    const n = 1 + Math.floor(Math.random() * 3);
    for (let k = 0; k < n; k++) {
      const t0 = ctx.currentTime + k * (0.06 + Math.random() * 0.07); const L = Math.floor(ctx.sampleRate * 0.012);
      const bb = ctx.createBuffer(1, L, ctx.sampleRate); const dd = bb.getChannelData(0);
      for (let i = 0; i < L; i++) dd[i] = (Math.random() * 2 - 1) * Math.exp(-i / (L * 0.25));
      const s2 = ctx.createBufferSource(); s2.buffer = bb; const hp = ctx.createBiquadFilter(); hp.type = 'highpass'; hp.frequency.value = 1800 + Math.random() * 1500;
      const g2 = ctx.createGain(); g2.gain.value = 0.05 + Math.random() * 0.05; s2.connect(hp).connect(g2).connect(gain); s2.start(t0);
    }
  }, 140);
  amb = { gain, murmur, timer };
}

export const soundOn = () => on;
export function setSound(v: boolean) {
  on = v; try { localStorage.setItem('dm-geluid', v ? 'aan' : 'uit'); } catch { /* */ }
  listeners.forEach((f) => f(v));
  if (v) play('success');
}
export function onSoundChange(f: (v: boolean) => void) { listeners.add(f); return () => { listeners.delete(f); }; }

/** Eén keer aanroepen: luistert naar klikken, hover op knoppen en scrollen in de hele app. */
export function startSounds() {
  window.addEventListener('pointerdown', () => { if (on) startAmbience(); }, { capture: true });
  onSoundChange((v) => { if (v) startAmbience(); });
  const isUi = (el: EventTarget | null) => (el as HTMLElement | null)?.closest?.('button, a, [role="button"], [role="tab"], summary, select, input[type="checkbox"], input[type="radio"]');
  window.addEventListener('pointerdown', (e) => {
    const el = isUi(e.target) as HTMLElement | null;
    if (el) { if (el.closest('[role="tab"]') || /rounded-full/.test(el.className ?? '')) play('tab'); else play('click'); }
  }, true);
  let hovered: Element | null = null;
  window.addEventListener('pointerover', (e) => {
    if ((e as PointerEvent).pointerType !== 'mouse') return;
    const el = isUi(e.target); if (el && el !== hovered) { hovered = el; play('hover'); }
    if (!el) hovered = null;
  }, true);
  let acc = 0;
  window.addEventListener('wheel', (e) => { acc += Math.abs(e.deltaY); if (acc > 90) { acc = 0; play('scroll'); } }, { passive: true, capture: true });
  let lastY = new WeakMap<Element, number>();
  window.addEventListener('scroll', (e) => {
    const t = e.target as Element; if (!t || !(t as HTMLElement).scrollTop && t !== document.documentElement) return;
    const y = (t as HTMLElement).scrollTop ?? 0; const p = lastY.get(t) ?? y;
    if (Math.abs(y - p) > 110) { lastY.set(t, y); play('scroll'); }
  }, { passive: true, capture: true });
  void lastY;
}
