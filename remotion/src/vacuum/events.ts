import {T} from './timing';
import {DIA_R} from './draw/Props';

// World layout (Z 1000 plane) and every physics event time, shared by the picture and the sound.
export type V2 = [number, number];
export const PUMP: V2 = [360, 1500];
export const GUY: V2 = [540, 1500];
export const BAL: V2 = [330, 705];
export const BRX = 118;
export const BRY = 138;
export const RESET = 23.55; // the scroll covers the screen: everything goes back to frame 0

// pump strokes (handle at its lowest point)
export const STROKES = [13.42, 13.78, 14.14, 19.02, 19.38, 19.74];

// kettlebell
export const KB_DROP = 9.0;
export const KB_LAND = 9.3;
export const KB_LAUNCH = 12.3;

// balloon crushed, hangs, drops (gravity 3600 px/s^2)
export const CRUSH = T.crushed;
export const BAL_FALL = 16.48;
export const CR_START_Y = BAL[1] + BRY - 46;
export const CR_GROUND_Y = PUMP[1] - 40;
export const CR_G = 3600;
export const BAL_LAND = BAL_FALL + Math.sqrt((2 * (CR_GROUND_Y - CR_START_Y)) / CR_G);

// diamond
export const CRACK = T.caves;
export const CRACK2 = T.inWord;
export const HOSE_ON_DIA = 18.66;
export const HOSE_OFF_DIA = 20.92;

// the dropped ball: let go on "float", thrown slightly toward the foot, gravity 3000 px/s^2
export const RELEASE = T.float;
export const DROP = {vx: -150, vy: -60, g: 3000};
export const HAND_HOPE: V2 = [140, -468];
export const BALL_IN_HAND = -96;
export const ballStart: V2 = [GUY[0] + HAND_HOPE[0], GUY[1] + HAND_HOPE[1] + BALL_IN_HAND];
export const FOOT_TOP = GUY[1] - 34;
export const tHit = (() => {
  const dy = FOOT_TOP - DIA_R - ballStart[1];
  return (-DROP.vy + Math.sqrt(DROP.vy * DROP.vy + 2 * DROP.g * dy)) / DROP.g;
})();
export const THUD = +(RELEASE + tHit).toFixed(3);
export const hitX = ballStart[0] + DROP.vx * tHit;
export const BOUNCE = {vx: 220, vy: -520};
export const GROUND_BALL_Y = GUY[1] - DIA_R + 6;
export const tGround = (() => {
  const dy = GROUND_BALL_Y - (FOOT_TOP - DIA_R);
  return (-BOUNCE.vy + Math.sqrt(BOUNCE.vy * BOUNCE.vy + 2 * DROP.g * dy)) / DROP.g;
})();
export const BALL_GROUND = THUD + tGround;
