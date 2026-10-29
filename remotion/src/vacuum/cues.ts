import {T} from './timing';
import * as E from './events';
import {ROLLUP, SHIP_FALL, SPHERE_CRUNCH, STAMP, UNROLL} from './draw/Parchment';

// Sound-effect cue list: file in public/vacuum/sfx (made by scripts/make_sfx.py), start time in
// seconds, level in dB. Impacts start on their event; whooshes are shifted so their peak (0.34 s
// into the file) lands on the fastest part of the camera move. Big hits sit in pauses.
export type Cue = {f: string; at: number; db: number};

const W = 0.34; // whoosh peak offset

export const CUES: Cue[] = [
  // 1. the balloon is happy, then scared of the pump
  {f: 'squeak', at: T.helium + 0.05, db: -28},
  {f: 'pop', at: T.helium + 0.05, db: -33},
  {f: 'click', at: T.nothing + 0.02, db: -24},
  {f: 'gulp', at: T.nothing + 0.12, db: -22},
  // 2. the thought bubble
  {f: 'pop', at: 3.74, db: -33},
  {f: 'pop', at: 3.8, db: -32},
  {f: 'pop', at: 3.86, db: -31},
  {f: 'pop_low', at: 3.9, db: -25},
  {f: 'pop', at: 4.02, db: -31},
  {f: 'pop', at: 4.08, db: -31},
  {f: 'whoosh_up', at: T.lighter + 0.03, db: -25},
  {f: 'nono', at: T.right + 0.02, db: -25},
  {f: 'pop_low', at: 5.9, db: -24},
  // 3. into the close-up: air puffs, the 15 lb weight
  {f: 'whoosh', at: 6.6 - W, db: -28},
  {f: 'pop', at: 6.5, db: -31},
  {f: 'pop', at: 6.64, db: -31},
  {f: 'pop', at: 6.78, db: -31},
  {f: 'squeak', at: T.pushes + 0.1, db: -29},
  {f: 'tick', at: T.almost, db: -27},
  {f: 'whistle_fall', at: E.KB_DROP - 0.28, db: -31},
  {f: 'thud_heavy', at: E.KB_LAND, db: -16},
  {f: 'tick', at: T.square + 0.1, db: -28},
  {f: 'tick', at: T.inch + 0.1, db: -28},
  // 4. helium pushes back, gets pumped out, crush
  {f: 'pop', at: T.helium2, db: -31},
  {f: 'boing', at: E.KB_LAUNCH, db: -19},
  ...E.STROKES.slice(0, 3).map((s) => ({f: 'pump', at: s - 0.1, db: -22})),
  {f: 'slurp', at: 13.5, db: -25},
  {f: 'squeak_sad', at: T.cant + 0.12, db: -25},
  {f: 'crumple', at: E.CRUSH + 0.03, db: -15},
  // 5. pull back, the crumpled balloon drops, the diamond appears
  {f: 'whoosh', at: 16.9 - W, db: -29},
  {f: 'pop_off', at: E.BAL_FALL, db: -27},
  {f: 'plop', at: E.BAL_LAND, db: -21},
  {f: 'swish', at: T.so2 - 0.1, db: -28},
  {f: 'ting', at: T.hard + 0.03, db: -18},
  {f: 'click', at: E.HOSE_ON_DIA, db: -24},
  // 6. pump the diamond, it caves in, drops on the foot
  ...E.STROKES.slice(3).map((s) => ({f: 'pump', at: s - 0.1, db: -22})),
  {f: 'crack', at: E.CRACK, db: -16},
  {f: 'tinkle', at: E.CRACK + 0.02, db: -23},
  {f: 'crunch', at: E.CRACK2, db: -20},
  {f: 'pop_off', at: E.HOSE_OFF_DIA, db: -27},
  {f: 'whistle_fall', at: E.RELEASE + 0.02, db: -27},
  {f: 'thud', at: E.THUD, db: -11},
  {f: 'plop', at: E.BALL_GROUND, db: -25},
  // 7. the 1670 scroll
  {f: 'paper', at: UNROLL[0], db: -21},
  ...SPHERE_CRUNCH.map((c) => ({f: 'crunch', at: c, db: -21})),
  {f: 'whoosh_down', at: SHIP_FALL - 0.05, db: -25},
  {f: 'stamp', at: STAMP, db: -18},
  {f: 'paper', at: ROLLUP[0], db: -22},
];
