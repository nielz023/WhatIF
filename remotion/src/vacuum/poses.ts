import {Pose, Vec} from './draw/Guy';

// Every pose of the main character as its own drawing. g = where the pump handle is,
// relative to the character's feet (the hands on the handle follow it while pumping).
export type PoseName =
  | 'p0'
  | 'idea'
  | 'grin'
  | 'think'
  | 'thumb'
  | 'pump'
  | 'shock'
  | 'behind'
  | 'diamond'
  | 'pumpDiamond'
  | 'wince'
  | 'hopeful'
  | 'release'
  | 'ouch';

export const POSES: Record<PoseName, (g: Vec) => Pose> = {
  // frame 0: hand on the pump, the other hand open: "why?"
  p0: (g) => ({
    facing: -0.28,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [122, -236], bend: 34, hand: 'open', rot: -32},
    face: {eyes: 'open', look: [0.15, 0.05], brows: 'raise1', mouth: 'smile'},
  }),
  idea: (g) => ({
    facing: -0.55,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [92, -318], bend: 38, hand: 'point', rot: -90},
    face: {eyes: 'open', look: [-0.6, -0.8], brows: 'up', mouth: 'open'},
  }),
  grin: (g) => ({
    facing: -0.25,
    lean: -5,
    armL: {to: [g[0] - 30, g[1]], bend: -10, hand: 'fist', front: false},
    armR: {to: [g[0] + 6, g[1] + 2], bend: -34, hand: 'fist'},
    face: {eyes: 'half', look: [0.1, 0.1], brows: 'angry', mouth: 'grin'},
  }),
  think: (g) => ({
    facing: 0.1,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [26, -300], bend: -52, hand: 'fist', rot: -100},
    face: {eyes: 'open', look: [0.7, -0.75], brows: 'up', mouth: 'smile'},
  }),
  thumb: (g) => ({
    facing: 0.12,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [128, -300], bend: 26, hand: 'thumb', rot: -10},
    face: {eyes: 'happy', brows: 'up', mouth: 'grin'},
  }),
  pump: (g) => ({
    facing: -0.45,
    lean: -6,
    armL: {to: [g[0] - 28, g[1]], bend: -10, hand: 'fist', front: false},
    armR: {to: [g[0] + 8, g[1]], bend: -34, hand: 'fist'},
    face: {eyes: 'open', look: [-0.45, -0.9], brows: 'angry', mouth: 'teeth'},
  }),
  shock: (g) => ({
    facing: -0.4,
    lean: 4,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [112, -334], bend: 22, hand: 'open', rot: -64},
    face: {eyes: 'wide', look: [-0.65, -0.55], brows: 'worried', mouth: 'o'},
  }),
  behind: (g) => ({
    facing: 0.25,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [-30, -200], bend: -30, hand: 'fist', front: false},
    face: {eyes: 'half', look: [0.3, 0], brows: 'raise1', mouth: 'smirk'},
  }),
  diamond: (g) => ({
    facing: 0.12,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [150, -322], bend: 42, hand: 'fist', rot: -80},
    face: {eyes: 'happy', brows: 'up', mouth: 'grin'},
  }),
  pumpDiamond: (g) => ({
    facing: -0.05,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [158, -300], bend: 42, hand: 'fist', rot: -80},
    face: {eyes: 'open', look: [0.85, -0.2], brows: 'angry', mouth: 'teeth'},
  }),
  wince: (g) => ({
    facing: 0.1,
    lean: 6,
    armL: {to: [g[0], g[1]], bend: -16, hand: 'fist', front: false},
    armR: {to: [168, -292], bend: 46, hand: 'fist', rot: -80},
    face: {eyes: 'wide', look: [0.8, -0.3], brows: 'worried', mouth: 'wavy'},
  }),
  hopeful: () => ({
    facing: 0.15,
    armL: {to: [-92, -172], bend: -10, hand: 'fist', front: false},
    armR: {to: [140, -468], bend: 34, hand: 'fist', rot: -90},
    face: {eyes: 'open', look: [0.3, -1], brows: 'up', mouth: 'smile'},
  }),
  release: () => ({
    facing: 0.15,
    armL: {to: [-92, -172], bend: -10, hand: 'fist', front: false},
    armR: {to: [140, -464], bend: 34, hand: 'open', rot: -90},
    face: {eyes: 'wide', look: [0.3, 0.6], brows: 'worried', mouth: 'o'},
  }),
  ouch: () => ({
    facing: 0,
    footR: [58, -80],
    armL: {to: [-118, -372], bend: -22, hand: 'open', rot: -122},
    armR: {to: [124, -380], bend: 22, hand: 'open', rot: -58},
    face: {eyes: 'squeeze', brows: 'worried', mouth: 'wide'},
  }),
};
