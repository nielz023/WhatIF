import React, {useId} from 'react';
import {C, INK, OUT, ink, ol} from '../style';

// The main character: white round head, small soft body, noodle arms, four-finger hands,
// short legs with rounded feet, thick even outlines. Origin = middle between the feet.
// Every pose is a full drawing (a set of parameters); the scene swaps poses inside motion.

export type Vec = [number, number];
export type HandKind = 'fist' | 'open' | 'thumb' | 'point';
export type Arm = {to: Vec; bend?: number; hand?: HandKind; rot?: number; front?: boolean; mirror?: boolean};
export type Eyes = 'open' | 'wide' | 'happy' | 'squeeze' | 'closed' | 'half';
export type Brows = 'neutral' | 'up' | 'worried' | 'angry' | 'raise1';
export type Mouth = 'smile' | 'grin' | 'open' | 'o' | 'wide' | 'flat' | 'wavy' | 'smirk' | 'teeth' | 'frown';
export type Face = {eyes: Eyes; look?: Vec; brows: Brows; mouth: Mouth; blink?: number};
export type Pose = {facing: number; lean?: number; armL: Arm; armR: Arm; footL?: Vec; footR?: Vec; face: Face};

export const HEAD_R = 112;
export const HEAD_Y = -402;
export const SHOULDER_L: Vec = [-40, -262];
export const SHOULDER_R: Vec = [40, -262];
const HIP_C: Vec = [0, -150];
const HIP_L: Vec = [-26, -150];
const HIP_R: Vec = [26, -150];
const ARM_W = 22;
const LEG_W = 26;

const BODY_D =
  'M -44 -294 C -58 -262 -70 -204 -68 -170 Q -66 -138 -40 -134 L 40 -134 Q 66 -138 68 -170 C 70 -204 58 -262 44 -294 Z';
const BODY_SHADE_D = 'M 30 -300 C 44 -250 48 -190 40 -128 L 96 -128 L 96 -300 Z';

const rotP = (p: Vec, c: Vec, deg: number): Vec => {
  const a = (deg * Math.PI) / 180;
  const x = p[0] - c[0];
  const y = p[1] - c[1];
  return [c[0] + x * Math.cos(a) - y * Math.sin(a), c[1] + x * Math.sin(a) + y * Math.cos(a)];
};

export function curve(s: Vec, h: Vec, bend: number) {
  const mx = (s[0] + h[0]) / 2;
  const my = (s[1] + h[1]) / 2;
  const dx = h[0] - s[0];
  const dy = h[1] - s[1];
  const len = Math.hypot(dx, dy) || 1;
  const c: Vec = [mx + (-dy / len) * bend, my + (dx / len) * bend];
  return {
    d: `M ${s[0].toFixed(1)} ${s[1].toFixed(1)} Q ${c[0].toFixed(1)} ${c[1].toFixed(1)} ${h[0].toFixed(1)} ${h[1].toFixed(1)}`,
    ang: (Math.atan2(h[1] - c[1], h[0] - c[0]) * 180) / Math.PI,
  };
}

export const Noodle: React.FC<{from: Vec; to: Vec; bend: number; w: number; fill?: string}> = ({from, to, bend, w, fill = C.white}) => {
  const {d} = curve(from, to, bend);
  return (
    <g>
      <path d={d} stroke={INK} strokeWidth={w + 2 * OUT} fill="none" strokeLinecap="round" />
      <path d={d} stroke={fill} strokeWidth={w} fill="none" strokeLinecap="round" />
    </g>
  );
};

type Shp = {c?: [number, number, number]; cap?: [number, number, number, number, number]};
function handShapes(kind: HandKind): Shp[] {
  switch (kind) {
    case 'fist':
      return [{c: [13, 0, 20]}, {cap: [9, -13, 20, -17, 12]}];
    case 'open':
      return [
        {c: [10, 0, 17]},
        {cap: [12, -8, 35, -19, 10]},
        {cap: [14, -3, 40, -7, 10]},
        {cap: [14, 3, 40, 6, 10]},
        {cap: [12, 8, 34, 18, 10]},
        {cap: [3, -11, -2, -31, 11]},
      ];
    case 'thumb':
      return [{c: [13, 0, 20]}, {cap: [10, -10, 10, -40, 13]}];
    case 'point':
      return [{c: [13, 0, 20]}, {cap: [18, -7, 52, -7, 11]}];
  }
}

/** Hand at a wrist point; local x points away from the wrist, thumb on local -y. */
export const Hand: React.FC<{kind: HandKind; at: Vec; ang: number; mirror?: boolean}> = ({kind, at, ang, mirror}) => {
  const shapes = handShapes(kind);
  const draw = (pass: 'ink' | 'fill') =>
    shapes.map((s, i) =>
      s.c ? (
        <circle key={i} cx={s.c[0]} cy={s.c[1]} r={s.c[2] + (pass === 'ink' ? OUT : 0)} fill={pass === 'ink' ? INK : C.white} />
      ) : (
        <line
          key={i}
          x1={s.cap![0]}
          y1={s.cap![1]}
          x2={s.cap![2]}
          y2={s.cap![3]}
          stroke={pass === 'ink' ? INK : C.white}
          strokeWidth={s.cap![4] + (pass === 'ink' ? 2 * OUT : 0)}
          strokeLinecap="round"
        />
      ),
    );
  return (
    <g transform={`translate(${at[0].toFixed(1)} ${at[1].toFixed(1)}) rotate(${ang.toFixed(1)}) scale(1 ${mirror ? -1 : 1})`}>
      {draw('ink')}
      {draw('fill')}
    </g>
  );
};

const ArmG: React.FC<{arm: Arm; shoulder: Vec; side: -1 | 1}> = ({arm, shoulder, side}) => {
  const bend = arm.bend ?? 18 * side;
  const {ang} = curve(shoulder, arm.to, bend);
  return (
    <g>
      <Noodle from={shoulder} to={arm.to} bend={bend} w={ARM_W} />
      <Hand kind={arm.hand ?? 'fist'} at={arm.to} ang={arm.rot ?? ang} mirror={arm.mirror ?? side < 0} />
    </g>
  );
};

// ---------------------------------------------------------------- face
const Eye: React.FC<{x: number; y: number; kind: Eyes; look: Vec; side: -1 | 1; blink: number}> = ({x, y, kind, look, side, blink}) => {
  const lx = x + look[0] * 6;
  const ly = y + look[1] * 6;
  if (kind === 'happy') return <path d={`M ${x - 12} ${y + 5} Q ${x} ${y - 12} ${x + 12} ${y + 5}`} {...ink(7)} />;
  if (kind === 'closed' || (blink >= 0.85 && kind !== 'squeeze'))
    return <path d={`M ${x - 12} ${y - 1} Q ${x} ${y + 9} ${x + 12} ${y - 1}`} {...ink(6)} />;
  if (kind === 'squeeze') {
    const d =
      side < 0
        ? `M ${x - 11} ${y - 11} L ${x + 9} ${y} L ${x - 11} ${y + 11}`
        : `M ${x + 11} ${y - 11} L ${x - 9} ${y} L ${x + 11} ${y + 11}`;
    return <path d={d} {...ink(7)} />;
  }
  const big = kind === 'wide';
  const rx = big ? 12.5 : 10;
  const ry = (big ? 18 : 14) * (1 - blink);
  return (
    <g>
      <ellipse cx={lx} cy={ly} rx={rx} ry={Math.max(ry, 1)} fill={INK} />
      {ry > 6 && <circle cx={lx + 3.5} cy={ly - ry * 0.38} r={big ? 4.2 : 3.4} fill={C.white} />}
      {kind === 'half' && (
        <g>
          <rect x={lx - 16} y={ly - 22} width={32} height={20} fill={C.white} />
          <line x1={lx - 14} y1={ly - 2} x2={lx + 14} y2={ly - 2} {...ink(5)} />
        </g>
      )}
    </g>
  );
};

const Brow: React.FC<{x: number; y: number; kind: Brows; side: -1 | 1}> = ({x, y, kind, side}) => {
  let d: string;
  // "inner" end = the end nearer the middle of the face
  const inner = side < 0 ? 1 : -1;
  const p = (dxIn: number, dyIn: number, dyOut: number, lift: number) => {
    const xi = x + inner * 14;
    const xo = x - inner * 14;
    return `M ${xo} ${y + dyOut - lift} Q ${x} ${y - 7 - lift} ${xi + dxIn} ${y + dyIn - lift}`;
  };
  switch (kind) {
    case 'up':
      d = p(0, 2, 2, 12);
      break;
    case 'worried':
      d = p(0, -9, 4, 2);
      break;
    case 'angry':
      d = p(0, 7, -8, 0);
      break;
    case 'raise1':
      d = side < 0 ? p(0, 2, 2, 15) : p(0, 3, 1, -2);
      break;
    default:
      d = p(0, 2, 2, 0);
  }
  return <path d={d} {...ink(8)} />;
};

const MouthG: React.FC<{x: number; y: number; kind: Mouth; uid: string}> = ({x, y, kind, uid}) => {
  const id = `${uid}-m`;
  const filled = (shape: string, tongue?: string) => (
    <g transform={`translate(${x} ${y})`}>
      <clipPath id={id}>
        <path d={shape} />
      </clipPath>
      <path d={shape} fill={INK} stroke={INK} strokeWidth={4} strokeLinejoin="round" />
      {tongue && <path d={tongue} fill={C.tongue} clipPath={`url(#${id})`} />}
    </g>
  );
  switch (kind) {
    case 'smile':
      return <path d={`M ${x - 22} ${y - 4} Q ${x} ${y + 16} ${x + 22} ${y - 4}`} {...ink(7)} />;
    case 'frown':
      return <path d={`M ${x - 20} ${y + 10} Q ${x} ${y - 6} ${x + 20} ${y + 10}`} {...ink(7)} />;
    case 'smirk':
      return <path d={`M ${x - 20} ${y + 4} Q ${x + 2} ${y + 12} ${x + 22} ${y - 8}`} {...ink(7)} />;
    case 'flat':
      return <path d={`M ${x - 16} ${y + 4} L ${x + 16} ${y + 4}`} {...ink(7)} />;
    case 'wavy':
      return <path d={`M ${x - 24} ${y + 4} q 6 -7 12 0 t 12 0 t 12 0 t 12 0`} {...ink(6)} />;
    case 'o':
      return <ellipse cx={x} cy={y + 6} rx={10} ry={13} fill={INK} />;
    case 'teeth':
      return (
        <g transform={`translate(${x} ${y})`}>
          <rect x={-24} y={-6} width={48} height={22} rx={8} {...ink(6)} fill={C.white} />
          <path d="M -22 5 L 22 5 M -8 -5 L -8 15 M 8 -5 L 8 15" {...ink(4)} />
        </g>
      );
    case 'grin':
      return filled('M -30 -6 Q 0 0 30 -6 Q 27 30 0 33 Q -27 30 -30 -6 Z', 'M -18 24 Q 0 10 18 24 L 18 40 L -18 40 Z');
    case 'open':
      return filled('M -15 0 A 15 17 0 1 0 15 0 A 15 17 0 1 0 -15 0 Z', 'M -14 10 Q 0 2 14 10 L 14 30 L -14 30 Z');
    case 'wide':
      return filled('M -25 -8 Q 0 -14 25 -8 Q 27 34 0 38 Q -27 34 -25 -8 Z', 'M -18 26 Q 0 12 18 26 L 18 44 L -18 44 Z');
  }
};

export const FaceG: React.FC<{face: Face; facing: number; uid: string}> = ({face, facing, uid}) => {
  const fx = facing * 44;
  const sp = 32 * (1 - 0.22 * Math.abs(facing));
  const look = face.look ?? [0, 0];
  const blink = face.blink ?? 0;
  return (
    <g>
      <Eye x={fx - sp} y={-8} kind={face.eyes} look={look} side={-1} blink={blink} />
      <Eye x={fx + sp} y={-8} kind={face.eyes} look={look} side={1} blink={blink} />
      <Brow x={fx - sp} y={-46} kind={face.brows} side={-1} />
      <Brow x={fx + sp} y={-46} kind={face.brows} side={1} />
      <MouthG x={fx + facing * 6} y={46} kind={face.mouth} uid={uid} />
    </g>
  );
};

export const Head: React.FC<{face: Face; facing: number; uid: string}> = ({face, facing, uid}) => {
  const hid = `${uid}-head`;
  return (
    <g transform={`translate(0 ${HEAD_Y})`}>
      <clipPath id={hid}>
        <circle r={HEAD_R} />
      </clipPath>
      <circle r={HEAD_R} fill={C.white} {...ol()} />
      <g clipPath={`url(#${hid})`}>
        <circle r={HEAD_R} fill={C.shade} />
        <circle cx={-HEAD_R * 0.1} cy={-HEAD_R * 0.08} r={HEAD_R * 0.93} fill={C.white} />
      </g>
      <FaceG face={face} facing={facing} uid={uid} />
    </g>
  );
};

// ---------------------------------------------------------------- whole body
export const Guy: React.FC<{pose: Pose; uid?: string}> = ({pose, uid: uidIn}) => {
  const auto = useId().replace(/:/g, '');
  const uid = uidIn ?? `guy${auto}`;
  const lean = pose.lean ?? 0;
  const f = pose.facing;
  const sL = rotP(SHOULDER_L, HIP_C, lean);
  const sR = rotP(SHOULDER_R, HIP_C, lean);
  const footL = pose.footL ?? [-38, 0];
  const footR = pose.footR ?? [38, 0];
  const dirL = f > 0.15 ? 1 : -1;
  const dirR = f < -0.15 ? -1 : 1;
  const armL = <ArmG arm={pose.armL} shoulder={sL} side={-1} />;
  const armR = <ArmG arm={pose.armR} shoulder={sR} side={1} />;
  const bid = `${uid}-body`;
  const leg = (hip: Vec, foot: Vec, dir: number, key: string) => (
    <g key={key}>
      <Noodle from={hip} to={[foot[0], foot[1] - 14]} bend={-dir * 6} w={LEG_W} />
      <ellipse cx={foot[0] + dir * 11} cy={foot[1] - 15} rx={34} ry={19} fill={C.white} {...ol()} />
    </g>
  );
  return (
    <g>
      {pose.armL.front === false && armL}
      {pose.armR.front === false && armR}
      {leg(HIP_L, footL, dirL, 'l')}
      {leg(HIP_R, footR, dirR, 'r')}
      <g transform={`rotate(${lean} ${HIP_C[0]} ${HIP_C[1]})`}>
        <clipPath id={bid}>
          <path d={BODY_D} />
        </clipPath>
        <path d={BODY_D} fill={C.white} {...ol()} />
        <path d={BODY_SHADE_D} fill={C.shade} clipPath={`url(#${bid})`} />
        <Head face={pose.face} facing={f} uid={uid} />
      </g>
      {pose.armL.front !== false && armL}
      {pose.armR.front !== false && armR}
    </g>
  );
};
