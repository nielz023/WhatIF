import React from 'react';
import {C, INK, ink} from '../style';

// Faces for things that come alive (balloon, diamond, air puffs): white eyes with black
// pupils and a glint, grey lids clipped to the eye with an ink lid line, thick round brows.

export type OEyes = 'open' | 'wide' | 'half' | 'angry' | 'squeeze' | 'closed';
export type OBrows = 'none' | 'angry' | 'worried' | 'up' | 'relaxed';
export type OMouth = 'none' | 'smile' | 'o' | 'flat' | 'wavy' | 'grin' | 'frown' | 'teeth' | 'smirk' | 'wide';
export type OFace = {eyes: OEyes; look?: [number, number]; brows?: OBrows; mouth?: OMouth; blink?: number; open?: number};

const OEye: React.FC<{
  x: number;
  r: number;
  kind: OEyes;
  look: [number, number];
  side: -1 | 1;
  blink: number;
  open: number;
  lid: string;
  id: string;
  lw: number;
}> = ({x, r, kind, look, side, blink, open, lid, id, lw}) => {
  if (kind === 'squeeze') {
    const d =
      side < 0
        ? `M ${x - r * 0.75} ${-r * 0.7} L ${x + r * 0.6} 0 L ${x - r * 0.75} ${r * 0.7}`
        : `M ${x + r * 0.75} ${-r * 0.7} L ${x - r * 0.6} 0 L ${x + r * 0.75} ${r * 0.7}`;
    return <path d={d} {...ink(lw * 1.1)} />;
  }
  if (kind === 'closed') return <path d={`M ${x - r * 0.8} ${-r * 0.15} Q ${x} ${r * 0.55} ${x + r * 0.8} ${-r * 0.15}`} {...ink(lw)} />;
  const big = kind === 'wide' ? 1.14 : 1;
  const rx = r * 0.84 * big;
  const ry = r * big * Math.max(0.05, open);
  const pr = r * (kind === 'wide' ? 0.38 : 0.48);
  const px = x + look[0] * (rx - pr) * 0.62;
  const py = look[1] * (ry - pr) * 0.62;
  // lid: covers from the top down to lidY (angry = tilted, inner side lower)
  let lidD: string | null = null;
  const inner = side < 0 ? 1 : -1;
  const b = Math.max(blink, kind === 'half' ? 0.45 : kind === 'angry' ? 0.3 : 0);
  if (b > 0.01) {
    const yMid = -ry + 2 * ry * b;
    const tilt = kind === 'angry' ? r * 0.35 : 0;
    const yIn = yMid + tilt;
    const yOut = yMid - tilt;
    const xIn = x + inner * (rx + 4);
    const xOut = x - inner * (rx + 4);
    lidD = `M ${xOut} ${-ry - 6} L ${xIn} ${-ry - 6} L ${xIn} ${yIn} L ${xOut} ${yOut} Z`;
  }
  return (
    <g>
      <clipPath id={id}>
        <ellipse cx={x} cy={0} rx={rx} ry={ry} />
      </clipPath>
      <ellipse cx={x} cy={0} rx={rx} ry={ry} fill={C.white} stroke={INK} strokeWidth={lw} />
      <g clipPath={`url(#${id})`}>
        <circle cx={px} cy={py} r={pr} fill={INK} />
        <circle cx={px + pr * 0.32} cy={py - pr * 0.38} r={pr * 0.34} fill={C.white} />
        {lidD && <path d={lidD} fill={lid} />}
      </g>
      {lidD && (
        <path
          d={(() => {
            const tilt = kind === 'angry' ? r * 0.35 : 0;
            const yMid = -ry + 2 * ry * b;
            return `M ${x - inner * rx} ${yMid - tilt} L ${x + inner * rx} ${yMid + tilt}`;
          })()}
          {...ink(lw * 0.9)}
        />
      )}
      <ellipse cx={x} cy={0} rx={rx} ry={ry} fill="none" stroke={INK} strokeWidth={lw} />
    </g>
  );
};

/** Face centred between the eyes. r = eye radius, sp = half distance between eyes. */
export const ObjFace: React.FC<{
  face: OFace;
  r: number;
  sp: number;
  mouthY: number;
  lid: string;
  uid: string;
  lw?: number;
}> = ({face, r, sp, mouthY, lid, uid, lw = 6}) => {
  const look = face.look ?? [0, 0];
  const blink = face.blink ?? 0;
  const open = face.open ?? 1;
  const brows = face.brows ?? 'none';
  const by = -r * 1.42;
  const brow = (side: -1 | 1) => {
    const x = side * sp;
    const inner = side < 0 ? 1 : -1;
    const xi = x + inner * r * 0.8;
    const xo = x - inner * r * 0.8;
    let yi = by;
    let yo = by;
    let lift = 0;
    if (brows === 'angry') {
      yi = by + r * 0.45;
      yo = by - r * 0.2;
    } else if (brows === 'worried') {
      yi = by - r * 0.45;
      yo = by + r * 0.15;
    } else if (brows === 'up') lift = r * 0.35;
    else if (brows === 'relaxed') {
      yi = by + r * 0.12;
      yo = by + r * 0.12;
    }
    return <path d={`M ${xo} ${yo - lift} Q ${x} ${Math.min(yi, yo) - r * 0.28 - lift} ${xi} ${yi - lift}`} {...ink(lw * 1.25)} />;
  };
  const m = face.mouth ?? 'none';
  const mw = sp * 0.62;
  let mouth: React.ReactNode = null;
  switch (m) {
    case 'smile':
      mouth = <path d={`M ${-mw} ${mouthY} Q 0 ${mouthY + mw * 0.75} ${mw} ${mouthY}`} {...ink(lw)} />;
      break;
    case 'grin':
      mouth = (
        <path
          d={`M ${-mw * 1.1} ${mouthY - 2} Q 0 ${mouthY + 2} ${mw * 1.1} ${mouthY - 2} Q ${mw} ${mouthY + mw * 1.1} 0 ${mouthY + mw * 1.15} Q ${-mw} ${mouthY + mw * 1.1} ${-mw * 1.1} ${mouthY - 2} Z`}
          fill={INK}
          stroke={INK}
          strokeWidth={lw * 0.6}
          strokeLinejoin="round"
        />
      );
      break;
    case 'smirk':
      mouth = <path d={`M ${-mw} ${mouthY + mw * 0.15} Q ${mw * 0.1} ${mouthY + mw * 0.5} ${mw} ${mouthY - mw * 0.35}`} {...ink(lw)} />;
      break;
    case 'frown':
      mouth = <path d={`M ${-mw} ${mouthY + mw * 0.45} Q 0 ${mouthY - mw * 0.3} ${mw} ${mouthY + mw * 0.45}`} {...ink(lw)} />;
      break;
    case 'flat':
      mouth = <path d={`M ${-mw * 0.7} ${mouthY} L ${mw * 0.7} ${mouthY}`} {...ink(lw)} />;
      break;
    case 'o':
      mouth = <ellipse cx={0} cy={mouthY + mw * 0.2} rx={mw * 0.42} ry={mw * 0.55} fill={INK} />;
      break;
    case 'wide':
      mouth = <ellipse cx={0} cy={mouthY + mw * 0.35} rx={mw * 0.75} ry={mw * 0.85} fill={INK} />;
      break;
    case 'wavy': {
      const s = (mw * 2) / 4;
      mouth = (
        <path d={`M ${-mw} ${mouthY} q ${s / 2} ${-s * 0.6} ${s} 0 t ${s} 0 t ${s} 0 t ${s} 0`} {...ink(lw * 0.9)} />
      );
      break;
    }
    case 'teeth':
      mouth = (
        <g>
          <rect x={-mw} y={mouthY - mw * 0.3} width={mw * 2} height={mw * 0.85} rx={mw * 0.3} fill={C.white} stroke={INK} strokeWidth={lw * 0.85} />
          <path
            d={`M ${-mw} ${mouthY + mw * 0.12} L ${mw} ${mouthY + mw * 0.12} M ${-mw * 0.33} ${mouthY - mw * 0.3} L ${-mw * 0.33} ${mouthY + mw * 0.55} M ${mw * 0.33} ${mouthY - mw * 0.3} L ${mw * 0.33} ${mouthY + mw * 0.55}`}
            {...ink(lw * 0.6)}
          />
        </g>
      );
      break;
  }
  return (
    <g>
      <OEye x={-sp} r={r} kind={face.eyes} look={look} side={-1} blink={blink} open={open} lid={lid} id={`${uid}-el`} lw={lw} />
      <OEye x={sp} r={r} kind={face.eyes} look={look} side={1} blink={blink} open={open} lid={lid} id={`${uid}-er`} lw={lw} />
      {brows !== 'none' && brow(-1)}
      {brows !== 'none' && brow(1)}
      {mouth}
    </g>
  );
};
