import React from 'react';
import {AbsoluteFill, getInputProps, useCurrentFrame} from 'remotion';
import {
  FPS,
  activeAt,
  bez,
  bump,
  clamp,
  easeInCubic,
  easeInOutCubic,
  easeInOutSine,
  easeOutBack,
  easeOutCubic,
  inv,
  lerp,
  popIn,
  popOut,
  rnd,
  shake,
  squashAll,
  wobble,
} from './anim';
import {DURATION, T} from './timing';
import {C} from './style';
import {Guy, HEAD_Y, Vec} from './draw/Guy';
import {POSES, PoseName} from './poses';
import {Balloon, CrumpledBalloon, GlassBalloon, HeDot, PushArrow} from './draw/Balloon';
import {
  DIA_R,
  Diamond,
  Dust,
  Hose,
  Kettlebell,
  PUMP_PORT,
  Patch,
  Puff,
  Pump,
  Shadow,
  Shard,
  Sparkle,
  SweatDrop,
  ShadowGradient,
  ThoughtBubble,
  bubbleClip,
  pumpGrips,
} from './draw/Props';
import {Clouds, Hills, MidGround, NearGround} from './draw/Scenery';
import {Parchment, SPHERE_CRUNCH, STAMP} from './draw/Parchment';
import {OFace} from './draw/ObjFace';
import {useFonts} from './fonts';
import {
  BAL,
  BALL_GROUND,
  BALL_IN_HAND,
  BAL_FALL,
  BAL_LAND,
  BOUNCE,
  BRX,
  BRY,
  CRACK,
  CRACK2,
  CRUSH,
  CR_G,
  CR_GROUND_Y,
  CR_START_Y,
  DROP,
  GROUND_BALL_Y,
  GUY,
  HOSE_OFF_DIA,
  HOSE_ON_DIA,
  KB_DROP,
  KB_LAND,
  KB_LAUNCH,
  PUMP,
  RELEASE,
  RESET,
  STROKES,
  THUD,
  FOOT_TOP,
  ballStart,
  hitX,
  tGround,
  tHit,
} from './events';
import {Sound} from './Sound';


// ------------------------------------------------------------------ camera (2.5D multiplane)
type Cam = {x: number; y: number; z: number};
type Key = {t: number; x: number; y: number; k: number; ease?: (u: number) => number};
const K0 = {x: 455, y: 1030, k: 1.5};
const KEYS: Key[] = [
  {t: 0, ...K0},
  {t: 0.5, ...K0},
  {t: 3.2, x: 455, y: 1015, k: 1.58, ease: easeInOutSine},
  {t: 3.65, x: 455, y: 1015, k: 1.58},
  {t: 4.3, x: 492, y: 995, k: 1.54, ease: easeInOutCubic},
  {t: 6.0, x: 492, y: 995, k: 1.54},
  {t: 7.2, x: 330, y: 700, k: 2.15, ease: easeInOutCubic},
  {t: 7.85, x: 330, y: 702, k: 2.17, ease: easeInOutSine},
  {t: 9.05, x: 335, y: 655, k: 2.1, ease: easeInOutCubic},
  {t: 11.2, x: 335, y: 662, k: 2.14, ease: easeInOutSine},
  {t: 12.25, x: 330, y: 700, k: 2.2, ease: easeInOutCubic},
  {t: 15.85, x: 330, y: 712, k: 2.32, ease: easeInOutSine},
  {t: 16.05, x: 330, y: 718, k: 2.45, ease: easeOutCubic},
  {t: 16.35, x: 330, y: 718, k: 2.45},
  {t: 17.45, x: 505, y: 1035, k: 1.45, ease: easeInOutCubic},
  {t: 18.9, x: 505, y: 1035, k: 1.45},
  {t: 20.0, x: 560, y: 1030, k: 1.58, ease: easeInOutSine},
  {t: 20.18, x: 562, y: 1032, k: 1.64, ease: easeOutCubic},
  {t: 21.55, x: 562, y: 1020, k: 1.6, ease: easeInOutSine},
  {t: 22.5, x: 560, y: 1075, k: 1.55, ease: easeInOutCubic},
  {t: RESET - 0.05, x: 560, y: 1075, k: 1.55},
  {t: RESET, ...K0},
  {t: DURATION, ...K0},
];
const step = (u: number) => (u >= 1 ? 1 : 0);
function camAt(t: number): Cam {
  let a = KEYS[KEYS.length - 1];
  let b = a;
  for (let i = 0; i < KEYS.length - 1; i++) {
    if (t >= KEYS[i].t && t < KEYS[i + 1].t) {
      a = KEYS[i];
      b = KEYS[i + 1];
      break;
    }
  }
  const u = (b.ease ?? step)(inv(a.t, b.t, t));
  const k = Math.exp(lerp(Math.log(a.k), Math.log(b.k), u));
  return {x: lerp(a.x, b.x, u), y: lerp(a.y, b.y, u), z: 1000 - 1000 / k};
}

const Layer: React.FC<{cam: Cam; z: number; blur?: number; children: React.ReactNode}> = ({cam, z, blur = 0, children}) => {
  const d = z - cam.z;
  if (d < 300) return null;
  const k = 1000 / d;
  return (
    <AbsoluteFill style={{filter: blur > 0.05 ? `blur(${blur.toFixed(2)}px)` : undefined}}>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{overflow: 'visible'}}>
        <g transform={`translate(540 960) scale(${k.toFixed(5)}) translate(${(-cam.x).toFixed(3)} ${(-cam.y).toFixed(3)})`}>{children}</g>
      </svg>
    </AbsoluteFill>
  );
};

// ------------------------------------------------------------------ pump strokes
const pumpExt = (t: number) => 80 - 58 * Math.max(0, ...STROKES.map((s) => bump(t, s, 0.15)));

// ------------------------------------------------------------------ the character
type Swap = {t: number; name: PoseName; kind?: 'action' | 'turn' | 'soft'};

const SWAPS: Swap[] = [
  {t: 0, name: 'p0'},
  {t: T.when, name: 'idea', kind: 'turn'},
  {t: T.nothing, name: 'grin', kind: 'action'},
  {t: T.an, name: 'think', kind: 'soft'},
  {t: T.right, name: 'thumb', kind: 'action'},
  {t: T.but, name: 'pump', kind: 'action'},
  {t: 16.42, name: 'shock', kind: 'action'},
  {t: T.so2, name: 'behind', kind: 'turn'},
  {t: T.hard, name: 'diamond', kind: 'action'},
  {t: T.even, name: 'pumpDiamond', kind: 'soft'},
  {t: T.caves, name: 'wince', kind: 'action'},
  {t: T.ifIts, name: 'hopeful', kind: 'action'},
  {t: RELEASE, name: 'release', kind: 'soft'},
  {t: THUD, name: 'ouch', kind: 'action'},
  {t: RESET, name: 'p0'},
];
const SQUASHES = SWAPS.filter((s) => s.kind).map((s) => ({t: s.t, kind: s.kind}));
const BLINKS = [1.62, 25.72];

function guyAt(t: number) {
  const cur = activeAt(SWAPS, t);
  const e = pumpExt(t);
  const gr = pumpGrips(e).right;
  const grip: Vec = [PUMP[0] + gr[0] - GUY[0], gr[1]];
  const pose = POSES[cur.name](grip);
  const sq = squashAll(t, SQUASHES);
  const breath = 1 + 0.009 * Math.sin(2 * Math.PI * (16 / DURATION) * t);
  let hop = 0;
  if (cur.name === 'ouch') {
    const x = t - THUD;
    hop = -46 * Math.abs(Math.sin((Math.PI * x) / 0.3)) * Math.exp(-1.4 * x);
  }
  // little talk bounce of the open hand in frame 0
  if (cur.name === 'p0') {
    const b = bump(t, T.fill + 0.1, 0.16) + bump(t, T.helium + 0.12, 0.2);
    pose.armR = {...pose.armR, to: [pose.armR.to[0] + 4 * b, pose.armR.to[1] - 12 * b]};
  }
  const blink = Math.max(0, ...BLINKS.map((b) => bump(t, b, 0.07)));
  pose.face = {...pose.face, blink};
  return {name: cur.name, pose, sx: sq.sx, sy: sq.sy * breath, hop};
}
const toWorld = (g: ReturnType<typeof guyAt>, p: Vec): Vec => [GUY[0] + p[0] * g.sx, GUY[1] + p[1] * g.sy + g.hop];

// ------------------------------------------------------------------ balloon
const bob = (t: number) => 7 * Math.sin(2 * Math.PI * (14 / DURATION) * t);
const sway = (t: number) => 2.5 * Math.sin(2 * Math.PI * (10 / DURATION) * t + 0.6);
const PUSHES = Array.from({length: 9}, (_, i) => T.pushes + i * 0.55).filter((x) => x < 11.4);
const pushPulse = (t: number) => Math.max(0, ...PUSHES.map((p) => bump(t, p + 0.12, 0.14)));
const backBump = (t: number) => (t < T.pushesBack ? 0 : easeOutCubic(inv(T.pushesBack, T.pushesBack + 0.18, t)) * (1 - easeInOutSine(inv(12.6, 13.3, t))));

function balloonFace(t: number): OFace {
  const blink = Math.max(bump(t, 0.95, 0.07), bump(t, 2.3, 0.07), bump(t, 25.5, 0.07));
  if (t >= RESET || t < T.nothing + 0.05) return {eyes: 'open', brows: 'relaxed', mouth: 'smile', look: [0, 0.1], blink};
  if (t < T.an) return {eyes: 'wide', brows: 'worried', mouth: 'o', look: [0.75, 0.55]};
  if (t < T.right) return {eyes: 'open', brows: 'worried', mouth: 'flat', look: [1, -0.15]};
  if (t < T.but) return {eyes: 'closed', brows: 'angry', mouth: 'frown'};
  if (t < T.pushes) return {eyes: 'wide', brows: 'worried', mouth: 'o', look: [Math.sin(t * 9) * 0.8, 0]};
  if (t < T.helium2) return {eyes: 'angry', brows: 'angry', mouth: 'teeth'};
  if (t < T.vacuum) return {eyes: 'half', brows: 'relaxed', mouth: 'grin', look: [0.2, 0]};
  if (t < T.cant) return {eyes: 'wide', brows: 'worried', mouth: 'wavy', look: [0, 0.9]};
  return {eyes: 'wide', brows: 'worried', mouth: 'wide', look: [0, 0]};
}

function balloonAt(t: number) {
  const by = bob(t);
  let x = BAL[0];
  let y = BAL[1] + by;
  let rot = sway(t);
  let sx = 1;
  let sy = 1;
  if (t >= RESET) return {mode: 'alive' as const, x, y, rot, sx, sy};
  // happy float on "helium"
  const hf = wobble(t, T.helium, 3, 4);
  sy *= 1 + 0.06 * hf;
  sx *= 1 - 0.04 * hf;
  y -= 14 * bump(t, T.helium + 0.25, 0.35);
  // nervous tremble
  if (t > T.nothing && t < T.an) x += 1.8 * Math.sin(2 * Math.PI * 17 * t);
  // "no no" head shake
  if (t >= T.right && t < T.but) rot += 11 * Math.sin(2 * Math.PI * 3.2 * (t - T.right)) * Math.exp(-2.2 * (t - T.right));
  // squeezed by the air puffs
  const pp = pushPulse(t);
  sx *= 1 - 0.035 * pp;
  sy *= 1 - 0.03 * pp;
  // kettlebell on top
  if (t >= KB_LAND && t < KB_LAUNCH) {
    sy *= 0.965 - 0.03 * Math.max(0, wobble(t, KB_LAND, 4, 6));
    y += 5;
  }
  // helium pushes back
  const bb = backBump(t);
  sx *= 1 + 0.06 * bb;
  sy *= 1 + 0.06 * bb;
  // emptied: trembles and shrinks
  if (t >= T.so && t < CRUSH) {
    const u = easeInCubic(inv(T.so, CRUSH, t));
    sx *= 1 - 0.1 * u;
    sy *= 1 - 0.08 * u;
    x += 3.2 * Math.sin(2 * Math.PI * 23 * t) * (0.4 + u);
  } else if (t >= T.cant && t < T.so) x += 1.5 * Math.sin(2 * Math.PI * 19 * t);
  if (t < CRUSH) return {mode: 'alive' as const, x, y, rot, sx, sy};
  // crumpled: hangs on the hose, then drops to the ground
  if (t < BAL_FALL) {
    const w = wobble(t, CRUSH, 4, 6);
    return {mode: 'crumpled' as const, x: BAL[0], y: CR_START_Y + bob(t), rot: 8 * w, sx: 1 + 0.25 * Math.max(0, -w) - 0.1 * w, sy: 1 + 0.2 * w};
  }
  if (t < BAL_LAND) {
    const tau = t - BAL_FALL;
    const u = tau / (BAL_LAND - BAL_FALL);
    return {mode: 'crumpled' as const, x: lerp(BAL[0], 262, u), y: CR_START_Y + 0.5 * CR_G * tau * tau, rot: -40 * u, sx: 1, sy: 1};
  }
  const w = wobble(t, BAL_LAND, 4, 7);
  return {mode: 'crumpled' as const, x: 262, y: CR_GROUND_Y, rot: -40, sx: 1 + 0.25 * w, sy: 1 - 0.25 * w};
}

// ------------------------------------------------------------------ air puffs
const PUFF_N = 12;
function puffsAt(t: number, bal: ReturnType<typeof balloonAt>) {
  if (t < T.air || t > 16.6 || t >= RESET) return [];
  const pp = pushPulse(t);
  const out: {x: number; y: number; s: number; face: OFace; squash: number; key: number}[] = [];
  for (let i = 0; i < PUFF_N; i++) {
    const a0 = (i / PUFF_N) * Math.PI * 2 + 0.26;
    // the two top puffs step aside while the kettlebell sits on the balloon
    const kbOn = easeInOutSine(inv(KB_DROP - 0.1, KB_DROP + 0.15, t)) * (1 - easeInOutSine(inv(KB_LAUNCH, KB_LAUNCH + 0.3, t)));
    // open a gap at the top for the weight: spread all puffs evenly over the rest of the circle
    const TOP = -Math.PI / 2;
    let rel = Math.atan2(Math.sin(a0 - TOP), Math.cos(a0 - TOP));
    const gap = 0.5 * kbOn;
    rel = Math.sign(rel) * (gap + Math.abs(rel) * ((Math.PI - gap) / Math.PI));
    const a = TOP + rel;
    const sIn = popIn(t, T.air + 0.035 * i, 0.22);
    const sOut = popOut(t, 16.12 + 0.025 * i, 0.2);
    const s = sIn * sOut;
    if (s <= 0.001) continue;
    let ring = 66 - 16 * pp + 56 * backBump(t) - 22 * easeInCubic(inv(T.so, CRUSH, t)) + 4 * Math.sin(t * 7 + i);
    let rx = BRX * bal.sx + ring;
    let ry = BRY * bal.sy + ring;
    let cy = bal.y;
    if (t >= CRUSH) {
      const u = easeOutCubic(inv(CRUSH, CRUSH + 0.1, t));
      rx = lerp(rx, 100, u);
      ry = lerp(ry, 86, u);
      cy = lerp(bal.y, CR_START_Y + bob(t), u);
    }
    let x = bal.x + Math.cos(a) * rx;
    let y = cy + Math.sin(a) * ry;
    if (t >= CRUSH) y -= 18 * bump(t, CRUSH + 0.14 + 0.012 * i, 0.07);
    let face: OFace = {eyes: 'angry', brows: 'angry', mouth: pp > 0.3 ? 'teeth' : 'flat', look: [-Math.cos(a), -Math.sin(a)]};
    if (t >= T.pushesBack && t < 12.9) face = {eyes: 'wide', brows: 'worried', mouth: 'o'};
    else if (t >= 12.9 && t < CRUSH) face = {eyes: 'angry', brows: 'angry', mouth: 'teeth', look: [-Math.cos(a), -Math.sin(a)]};
    else if (t >= CRUSH) face = {eyes: 'closed', brows: 'up', mouth: 'smile'};
    out.push({x, y, s, face, squash: 1 - 0.1 * pp, key: i});
  }
  return out;
}

// ------------------------------------------------------------------ helium dots
const DOTS = Array.from({length: 14}, (_, i) => ({a: (i / 14) * Math.PI * 2 + rnd(i) * 0.25, r: 0.7 + rnd(i + 20) * 0.15}));
function dotsAt(t: number, bal: ReturnType<typeof balloonAt>) {
  if (t < T.helium2 || t > 14.4 || t >= RESET) return [];
  const knot: Vec = [bal.x, bal.y + BRY * bal.sy + 4];
  const bb = backBump(t);
  return DOTS.map((d, i) => {
    const s = popIn(t, T.helium2 + 0.025 * i, 0.2);
    const r = d.r + 0.09 * bb;
    let x = bal.x + Math.cos(d.a) * BRX * bal.sx * r + 5 * Math.sin(2 * Math.PI * 1.4 * t + i);
    let y = bal.y + Math.sin(d.a) * BRY * bal.sy * r + 5 * Math.cos(2 * Math.PI * 1.1 * t + 2 * i);
    const leave = 13.5 + 0.05 * i;
    const u = easeInCubic(inv(leave, leave + 0.14, t));
    x = lerp(x, knot[0], u);
    y = lerp(y, knot[1], u);
    const arrow = t >= 12.2 ? popIn(t, 12.2 + 0.01 * i, 0.15) * popOut(t, 12.72, 0.15) : 0;
    return {x, y, s: t > leave + 0.14 ? 0 : s, a: d.a, arrow, key: i};
  });
}

// ------------------------------------------------------------------ diamond
function diamondAt(t: number, g: ReturnType<typeof guyAt>) {
  if (t < T.hard || t >= RESET) return null;
  const dent = t >= CRACK2 ? 2 : t >= CRACK ? 1 : 0;
  let face: OFace;
  if (t < T.even) face = {eyes: 'half', brows: 'relaxed', mouth: 'smirk', look: [0.2, -0.1], blink: bump(t, 18.62, 0.07)};
  else if (t < CRACK) face = {eyes: 'wide', brows: 'worried', mouth: 'o', look: [-0.75, 0.5]};
  else face = {eyes: 'squeeze', mouth: t >= CRACK2 && t < 21.0 ? 'wide' : 'wavy'};
  let x: number;
  let y: number;
  let rot = 0;
  let sx = 1;
  let sy = 1;
  if (t < RELEASE) {
    const hand = g.pose.armR.to;
    [x, y] = toWorld(g, [hand[0], hand[1] + BALL_IN_HAND]);
    if (t >= T.even && t < CRACK) x += 1.6 * Math.sin(2 * Math.PI * 21 * t);
    const w = wobble(t, CRACK, 5, 6) + 0.6 * wobble(t, CRACK2, 5, 7);
    sx = 1 + 0.12 * w;
    sy = 1 - 0.12 * w;
  } else if (t < THUD) {
    const tau = t - RELEASE;
    x = ballStart[0] + DROP.vx * tau;
    y = ballStart[1] + DROP.vy * tau + 0.5 * DROP.g * tau * tau;
    rot = -60 * tau;
  } else if (t < BALL_GROUND) {
    const tau = t - THUD;
    x = hitX + BOUNCE.vx * tau;
    y = FOOT_TOP - DIA_R + BOUNCE.vy * tau + 0.5 * DROP.g * tau * tau;
    rot = -60 * tHit + 200 * tau;
  } else {
    const tau = t - BALL_GROUND;
    const roll = 110 * (1 - Math.exp(-3.5 * tau));
    x = hitX + BOUNCE.vx * tGround + roll;
    y = GROUND_BALL_Y;
    rot = -60 * tHit + 200 * tGround + (roll / DIA_R) * (180 / Math.PI);
    const w = wobble(t, BALL_GROUND, 5, 8);
    sx = 1 + 0.12 * w;
    sy = 1 - 0.12 * w;
  }
  return {x, y, rot, sx, sy, dent, face};
}

// ------------------------------------------------------------------ hose
type HoseGeom = {p0: number[]; c1: number[]; c2: number[]; p3: number[]};
const PORT: Vec = [PUMP[0] + PUMP_PORT[0], PUMP[1] + PUMP_PORT[1]];
const HOSE_REST: HoseGeom = {p0: PORT, c1: [270, 1500], c2: [236, 1486], p3: [196, 1480]};
const hoseToBalloon = (knot: Vec): HoseGeom => ({p0: PORT, c1: [150, 1430], c2: [knot[0] - 8, knot[1] + 250], p3: [knot[0], knot[1] + 12]});
const hoseToDiamond = (c: Vec): HoseGeom => ({p0: PORT, c1: [420, 1560], c2: [800, 1430], p3: [c[0] - 30, c[1] + DIA_R - 6]});
const mixHose = (a: HoseGeom, b: HoseGeom, u: number): HoseGeom => ({
  p0: a.p0,
  c1: [lerp(a.c1[0], b.c1[0], u), lerp(a.c1[1], b.c1[1], u)],
  c2: [lerp(a.c2[0], b.c2[0], u), lerp(a.c2[1], b.c2[1], u)],
  p3: [lerp(a.p3[0], b.p3[0], u), lerp(a.p3[1], b.p3[1], u)],
});
const settle = (u: number) => (u >= 1 ? 1 : 1 - Math.cos(u * Math.PI * 2.5) * Math.pow(1 - u, 2.2));

function hoseAt(t: number, bal: ReturnType<typeof balloonAt>, dia: ReturnType<typeof diamondAt>): HoseGeom {
  const knotOf = (x: number, y: number, sy: number): Vec => [x, y + BRY * sy + 8];
  if (t >= RESET || t < CRUSH) return hoseToBalloon(knotOf(bal.x, bal.y, bal.sy));
  const hang: Vec = [BAL[0], BAL[1] + BRY + 8 + bob(t)];
  if (t < BAL_FALL) return hoseToBalloon(hang);
  if (t < HOSE_ON_DIA - 0.12) return mixHose(hoseToBalloon(hang), HOSE_REST, settle(inv(BAL_FALL, BAL_FALL + 0.55, t)));
  if (dia && t < HOSE_ON_DIA) return mixHose(HOSE_REST, hoseToDiamond([dia.x, dia.y]), easeOutBack(inv(HOSE_ON_DIA - 0.12, HOSE_ON_DIA, t), 1.4));
  if (dia && t < HOSE_OFF_DIA) return hoseToDiamond([dia.x, dia.y]);
  if (dia && t < HOSE_OFF_DIA + 0.6) return mixHose(hoseToDiamond([dia.x, dia.y]), HOSE_REST, settle(inv(HOSE_OFF_DIA, HOSE_OFF_DIA + 0.55, t)));
  return HOSE_REST;
}

// ------------------------------------------------------------------ the kettlebell
function kettlebellAt(t: number, bal: ReturnType<typeof balloonAt>) {
  if (t < KB_DROP || t > 13.6 || t >= RESET) return null;
  const top = bal.y - BRY * bal.sy + 10;
  if (t < KB_LAND) {
    const u = (t - KB_DROP) / (KB_LAND - KB_DROP);
    return {x: bal.x, y: top - 520 + 520 * u * u, rot: 0, sx: 1, sy: 1};
  }
  if (t < KB_LAUNCH) {
    const w = wobble(t, KB_LAND, 4, 6);
    return {x: bal.x, y: top, rot: 6 * wobble(t, KB_LAND + 0.05, 3, 5), sx: 1 + 0.12 * w, sy: 1 - 0.12 * w};
  }
  const tau = t - KB_LAUNCH;
  return {x: bal.x + 420 * tau, y: top - 1150 * tau + 0.5 * 2600 * tau * tau, rot: 700 * tau, sx: 1, sy: 1};
}

// ------------------------------------------------------------------ thought bubble
const BUB: Vec = [662, 772];
const TRAIL: [number, number, number][] = [
  [586, 958, 12],
  [606, 914, 17],
  [630, 866, 22],
];

// ------------------------------------------------------------------ helpers for one-off effects
const sweatDrops = (t: number, bal: ReturnType<typeof balloonAt>, dia: ReturnType<typeof diamondAt>, g: ReturnType<typeof guyAt>) => {
  const list: {x: number; y: number; s: number; key: string}[] = [];
  const add = (key: string, t0: number, t1: number, at: Vec, slide = 36) => {
    if (t < t0 || t > t1 + 0.2) return;
    const s = popIn(t, t0, 0.2) * popOut(t, t1, 0.18);
    list.push({key, x: at[0], y: at[1] + slide * easeInOutSine(inv(t0 + 0.1, t1, t)), s});
  };
  if (t < RESET) {
    add('b1', T.nothing + 0.08, T.an + 0.05, [bal.x + BRX * 0.82, bal.y - BRY * 0.45]);
    if (bal.mode === 'alive') add('b2', T.cant + 0.06, CRUSH - 0.05, [bal.x + BRX * 0.82, bal.y - BRY * 0.45]);
    if (dia) add('d1', 19.5, CRACK - 0.04, [dia.x + DIA_R * 0.8, dia.y - DIA_R * 0.55], 22);
    const head = toWorld(g, [0, HEAD_Y]);
    add('g1', THUD + 0.04, 23.3, [head[0] + 108, head[1] - 70], 40);
  }
  return list;
};

const SHAKES = [
  {t: KB_LAND, amp: 9, decay: 9},
  {t: KB_LAUNCH, amp: 5, decay: 10},
  {t: CRUSH, amp: 24, decay: 6},
  {t: 17.09, amp: 4, decay: 10},
  {t: CRACK, amp: 16, decay: 7},
  {t: CRACK2, amp: 7, decay: 9},
  {t: THUD, amp: 22, decay: 6},
  ...SPHERE_CRUNCH.map((c) => ({t: c, amp: 4, decay: 12})),
  {t: STAMP, amp: 9, decay: 9},
];


// ------------------------------------------------------------------ composition
export const VacuumScene: React.FC = () => {
  useFonts();
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const cam = camAt(t);
  const k = 1000 / (1000 - cam.z);
  const noBlur = Boolean((getInputProps() as {noBlur?: boolean}).noBlur);
  const dof = noBlur ? 0 : clamp((k - 1.7) / 0.5) * 3.4;
  const sh = shake(t, SHAKES);
  const g = guyAt(t);
  const bal = balloonAt(t);
  const dia = diamondAt(t, g);
  const hose = hoseAt(t, bal, dia);
  const kb = kettlebellAt(t, bal);
  const puffs = puffsAt(t, bal);
  const dots = dotsAt(t, bal);
  const ext = pumpExt(t);
  const drift = 30 * Math.sin((2 * Math.PI * t) / DURATION);

  // look at the falling ball while releasing it
  if (g.name === 'release' && dia) {
    const head = toWorld(g, [0, HEAD_Y]);
    const dx = dia.x - head[0];
    const dy = dia.y - head[1];
    const n = Math.hypot(dx, dy) || 1;
    g.pose.face = {...g.pose.face, look: [dx / n, dy / n]};
  }

  // thought bubble
  const bubS = t >= RESET ? 0 : popIn(t, 3.9, 0.26) * popOut(t, 5.9, 0.2);
  const trailS = TRAIL.map((_, i) => (t >= RESET ? 0 : popIn(t, 3.74 + 0.06 * i, 0.2) * popOut(t, 5.86 - 0.04 * i, 0.16)));
  const redUp = 26 * easeInOutSine(inv(4.1, 5.8, t));
  const glassUp = 46 * easeInOutSine(inv(4.1, 4.9, t)) + 900 * easeInCubic(inv(T.lighter + 0.05, T.lighter + 0.4, t));

  // hose bulges while the helium is sucked out
  const bulges: Vec[] = [];
  if (t > 13.5 && t < 14.45 && t < RESET) {
    for (let j = 0; j < 3; j++) {
      const s = 1 - (((t - 13.5) / 0.32 + j / 3) % 1);
      bulges.push(bez(hose.p0, hose.c1, hose.c2, hose.p3, s));
    }
  }

  // shards from the crack
  const shards =
    dia && t >= CRACK && t < CRACK + 0.7
      ? Array.from({length: 7}, (_, i) => {
          const a = -Math.PI * (0.18 + 0.75 * rnd(i + 3));
          const v = 320 + 320 * rnd(i + 9);
          const tau = t - CRACK;
          const ox = dia.x - 30;
          const oy = dia.y - 50;
          return {x: ox + Math.cos(a) * v * tau, y: oy + Math.sin(a) * v * tau + 0.5 * 2400 * tau * tau, r: 600 * tau * (i % 2 ? 1 : -1), s: popOut(t, CRACK + 0.45, 0.2), key: i};
        })
      : [];

  // sparkles around the diamond
  const sparkles: {x: number; y: number; s: number; key: string}[] = [];
  if (dia && t < RELEASE) {
    const spots: [number, number, number, number][] = [
      [-92, -66, 17.97, 18.48],
      [96, -44, 18.03, 18.54],
      [62, 84, 18.09, 18.6],
      [-70, 64, T.shell + 0.02, T.shell + 0.36],
    ];
    spots.forEach(([dx, dy, a, b], i) => {
      const s = popIn(t, a, 0.2) * popOut(t, b, 0.16);
      if (s > 0.001) sparkles.push({x: dia.x + dx, y: dia.y + dy, s, key: `s${i}`});
    });
  }
  if (t >= T.helium && t < T.helium + 0.8) {
    [
      [BAL[0] + 150, BAL[1] - 110, T.helium + 0.05],
      [BAL[0] - 150, BAL[1] - 60, T.helium + 0.15],
    ].forEach(([x, y, a], i) => sparkles.push({x, y: y + bob(t), s: 0.7 * popIn(t, a, 0.2) * popOut(t, a + 0.45, 0.16), key: `h${i}`}));
  }

  // dust on landings
  const dusts: {x: number; y: number; s: number; key: string}[] = [];
  const dustAt = (key: string, t0: number, x: number) => {
    if (t < t0 || t > t0 + 0.5) return;
    const u = inv(t0, t0 + 0.5, t);
    const s = Math.sin(Math.PI * Math.min(1, u * 1.2)) * 0.9;
    dusts.push({key: key + 'l', x: x - 50 - 50 * u, y: 1500, s});
    dusts.push({key: key + 'r', x: x + 50 + 50 * u, y: 1500, s});
  };
  if (t < RESET) {
    dustAt('bal', BAL_LAND, 262);
    dustAt('dia', BALL_GROUND, hitX + BOUNCE.vx * tGround);
  }

  const drops = sweatDrops(t, bal, dia, g);
  const guyShadowS = 1 - clamp(-g.hop / 120) * 0.5;

  return (
    <AbsoluteFill style={{backgroundColor: C.sky2}}>
      <AbsoluteFill style={{transform: `translate(${sh.x.toFixed(2)}px, ${sh.y.toFixed(2)}px)`}}>
        <div style={{position: 'absolute', inset: -80, background: `linear-gradient(180deg, ${C.sky1} 0%, ${C.sky2} 62%)`}} />
        {/* far layers: depth-of-field blur on close-ups, done once for all three */}
        <AbsoluteFill style={{filter: dof > 0.05 ? `blur(${dof.toFixed(2)}px)` : undefined}}>
          <Layer cam={cam} z={4200}>
            <Clouds drift={drift} />
          </Layer>
          <Layer cam={cam} z={3000}>
            <Hills />
          </Layer>
          <Layer cam={cam} z={1800}>
            <MidGround />
          </Layer>
        </AbsoluteFill>
        <Layer cam={cam} z={1000}>
          <defs>
            <ShadowGradient id="softShadow" />
            <clipPath id="bubClip">
              <path d={bubbleClip(300, 230)} />
            </clipPath>
          </defs>
          <NearGround />
          {/* contact shadows */}
          <g transform={`translate(${PUMP[0]} ${PUMP[1]})`}>
            <Shadow rx={96} gradId="softShadow" />
          </g>
          <g transform={`translate(${GUY[0]} ${GUY[1]}) scale(${guyShadowS} 1)`}>
            <Shadow rx={84} gradId="softShadow" />
          </g>
          {bal.mode === 'crumpled' && t >= BAL_LAND && (
            <g transform={`translate(262 1500)`}>
              <Shadow rx={70} gradId="softShadow" />
            </g>
          )}
          {dia && t >= THUD && (
            <g transform={`translate(${dia.x} 1500) scale(${clamp(1 - (GROUND_BALL_Y - dia.y) / 300, 0.4, 1)} 1)`}>
              <Shadow rx={58} gradId="softShadow" />
            </g>
          )}
          {/* hose (behind the pump and the character) */}
          <Hose p0={hose.p0} c1={hose.c1} c2={hose.c2} p3={hose.p3} />
          {bulges.map(([x, y], i) => (
            <g key={`bu${i}`} transform={`translate(${x} ${y})`}>
              <circle r={13 + 9} fill="#1c1a20" />
              <circle r={13} fill={C.hose} />
            </g>
          ))}
          <g transform={`translate(${PUMP[0]} ${PUMP[1]})`}>
            <Pump ext={ext} uid="pump" />
          </g>
          {/* crumpled balloon on the ground (behind the character) */}
          {bal.mode === 'crumpled' && (
            <g transform={`translate(${bal.x} ${bal.y}) rotate(${bal.rot}) scale(${bal.sx} ${bal.sy})`}>
              <CrumpledBalloon uid="crumpled" face={{eyes: 'squeeze', mouth: 'wavy'}} />
            </g>
          )}
          {/* balloon, helium, kettlebell */}
          {bal.mode === 'alive' && (
            <g transform={`translate(${bal.x} ${bal.y}) rotate(${bal.rot}) scale(${bal.sx} ${bal.sy})`}>
              <Balloon uid="balloon" face={balloonFace(t)} topFlat={kb && t >= KB_LAND && t < KB_LAUNCH ? 10 : 0} />
            </g>
          )}
          {dots.map((d) =>
            d.s > 0.001 ? (
              <g key={`d${d.key}`} transform={`translate(${d.x} ${d.y})`}>
                <g transform={`scale(${d.s})`}>
                  <HeDot />
                </g>
                {d.arrow > 0.001 && (
                  <g transform={`rotate(${(d.a * 180) / Math.PI}) translate(16 0) scale(${d.arrow})`}>
                    <PushArrow len={30} />
                  </g>
                )}
              </g>
            ) : null,
          )}
          {/* the character */}
          <g transform={`translate(${GUY[0]} ${GUY[1] + g.hop}) scale(${g.sx} ${g.sy})`}>
            <Guy pose={g.pose} uid="guy" />
          </g>
          {/* the diamond ball, in front of the hand */}
          {dia && (
            <g transform={`translate(${dia.x} ${dia.y}) rotate(${dia.rot}) scale(${dia.sx} ${dia.sy})`}>
              <Diamond uid="diamond" dent={dia.dent} face={dia.face} />
            </g>
          )}
          {shards.map((s) => (
            <g key={`sh${s.key}`} transform={`translate(${s.x} ${s.y}) rotate(${s.r}) scale(${s.s})`}>
              <Shard s={1.3} />
            </g>
          ))}
          {/* air puffs in front of the balloon */}
          {puffs.map((p) => (
            <g key={`p${p.key}`} transform={`translate(${p.x} ${p.y}) scale(${p.s})`}>
              <Puff uid={`puff${p.key}`} face={p.face} squash={p.squash} />
            </g>
          ))}
          {t >= 8.66 && t < KB_LAUNCH + 0.25 && t < RESET && (
            <g
              transform={`translate(${bal.x} ${bal.y - BRY * bal.sy + 30}) scale(${popIn(t, 8.66, 0.22) * popOut(t, KB_LAUNCH, 0.18) * (1 + 0.25 * bump(t, T.square + 0.1, 0.12) + 0.25 * bump(t, T.inch + 0.1, 0.12))})`}
            >
              <Patch />
            </g>
          )}
          {kb && (
            <g transform={`translate(${kb.x} ${kb.y}) rotate(${kb.rot}) scale(${kb.sx} ${kb.sy})`}>
              <Kettlebell uid="kb" />
            </g>
          )}
          {/* thought bubble */}
          {TRAIL.map(([x, y, r], i) =>
            trailS[i] > 0.001 ? (
              <g key={`tr${i}`} transform={`translate(${x} ${y}) scale(${trailS[i]})`}>
                <circle r={r + 9} fill="#1c1a20" />
                <circle r={r} fill={C.white} />
              </g>
            ) : null,
          )}
          {bubS > 0.001 && (
            <g transform={`translate(${BUB[0]} ${BUB[1]}) scale(${bubS})`}>
              <ThoughtBubble w={300} h={230} />
              <g clipPath="url(#bubClip)">
                <g transform={`translate(-62 ${50 - redUp}) scale(${0.4 * popIn(t, 4.02, 0.2)})`}>
                  <Balloon uid="mini-red" face={{eyes: 'open', brows: 'worried', mouth: 'flat', look: [1, -0.5]}} />
                </g>
                <g transform={`translate(60 ${50 - glassUp}) scale(${0.4 * popIn(t, 4.08, 0.2)})`}>
                  <GlassBalloon uid="mini-glass" face={{eyes: 'half', brows: 'relaxed', mouth: 'smirk'}} />
                </g>
              </g>
            </g>
          )}
          {sparkles.map((s) => (
            <g key={s.key} transform={`translate(${s.x} ${s.y}) scale(${s.s})`}>
              <Sparkle />
            </g>
          ))}
          {drops.map((d) => (
            <g key={d.key} transform={`translate(${d.x} ${d.y}) scale(${d.s})`}>
              <SweatDrop s={1.1} />
            </g>
          ))}
          {dusts.map((d) => (
            <g key={d.key} transform={`translate(${d.x} ${d.y})`}>
              <Dust s={d.s} />
            </g>
          ))}
        </Layer>
        <Parchment t={t} uid="scroll" />
      </AbsoluteFill>
      <Sound />
    </AbsoluteFill>
  );
};
