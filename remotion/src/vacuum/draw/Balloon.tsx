import React from 'react';
import {C, INK, OUT, ink, ol} from '../style';
import {rnd} from '../anim';
import {OFace, ObjFace} from './ObjFace';

// Red party balloon that comes alive, its crumpled version, and a glass "empty" balloon
// for the thought bubble. Origin = balloon centre; the knot hangs below at y = ry.

export const balloonPath = (rx: number, ry: number) =>
  `M 0 ${-ry} C ${rx * 0.56} ${-ry} ${rx} ${-ry * 0.55} ${rx} ${-ry * 0.05} ` +
  `C ${rx} ${ry * 0.45} ${rx * 0.45} ${ry * 0.92} 0 ${ry} ` +
  `C ${-rx * 0.45} ${ry * 0.92} ${-rx} ${ry * 0.45} ${-rx} ${-ry * 0.05} ` +
  `C ${-rx} ${-ry * 0.55} ${-rx * 0.56} ${-ry} 0 ${-ry} Z`;

const Knot: React.FC<{y: number; color: string}> = ({y, color}) => (
  <path d={`M -12 ${y + 17} Q 0 ${y + 10} 12 ${y + 17} L 2 ${y - 3} L -2 ${y - 3} Z`} fill={color} {...ol(OUT * 0.8)} />
);

export const Balloon: React.FC<{rx?: number; ry?: number; face?: OFace; uid: string; topFlat?: number}> = ({
  rx = 118,
  ry = 138,
  face,
  uid,
  topFlat = 0,
}) => {
  const d = balloonPath(rx, ry);
  const id = `${uid}-bal`;
  return (
    <g>
      <Knot y={ry} color={C.red} />
      <clipPath id={id}>
        <path d={d} />
      </clipPath>
      <path d={d} fill={C.red} {...ol()} />
      <g clipPath={`url(#${id})`}>
        <path d={d} fill={C.redShade} />
        <ellipse cx={-rx * 0.12} cy={-ry * 0.1} rx={rx * 0.93} ry={ry * 0.92} fill={C.red} />
        {topFlat > 0 && <ellipse cx={0} cy={-ry} rx={rx * 0.5} ry={topFlat} fill={C.redShade} opacity={0.6} />}
      </g>
      <ellipse cx={-rx * 0.45} cy={-ry * 0.47} rx={rx * 0.12} ry={ry * 0.22} transform={`rotate(32 ${-rx * 0.45} ${-ry * 0.47})`} fill={C.redHi} />
      <circle cx={-rx * 0.62} cy={-ry * 0.12} r={rx * 0.05} fill={C.redHi} />
      {face && (
        <g transform={`translate(0 ${-ry * 0.06})`}>
          <ObjFace face={face} r={rx * 0.19} sp={rx * 0.36} mouthY={ry * 0.34} lid={C.redShade} uid={uid} lw={6.5} />
        </g>
      )}
    </g>
  );
};

// Crumpled balloon: a jagged squashed outline with folds.
const CRUMPLE = Array.from({length: 18}, (_, i) => {
  const a = (i / 18) * Math.PI * 2 - Math.PI / 2;
  const r = (i % 2 === 0 ? 1.0 : 0.8) + (rnd(i + 7) - 0.5) * 0.18;
  return [Math.cos(a) * r, Math.sin(a) * r * 0.72] as const;
});

export const CrumpledBalloon: React.FC<{s?: number; face?: OFace; uid: string}> = ({s = 1, face, uid}) => {
  const rx = 74 * s;
  const ry = 64 * s;
  const pts = CRUMPLE.map(([x, y]) => `${(x * rx).toFixed(1)} ${(y * ry + 6).toFixed(1)}`);
  const d = `M ${pts.join(' L ')} Z`;
  return (
    <g>
      <Knot y={ry * 0.62} color={C.red} />
      <path d={d} fill={C.red} {...ol()} />
      <path
        d={`M ${-rx * 0.6} ${-ry * 0.2} L ${-rx * 0.2} ${ry * 0.05} L ${-rx * 0.35} ${ry * 0.4} M ${rx * 0.55} ${-ry * 0.35} L ${rx * 0.15} ${-ry * 0.05} L ${rx * 0.5} ${ry * 0.3} M ${-rx * 0.1} ${-ry * 0.55} L ${rx * 0.05} ${-ry * 0.25}`}
        stroke={C.redFold}
        strokeWidth={6}
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {face && <ObjFace face={face} r={rx * 0.17} sp={rx * 0.34} mouthY={ry * 0.32} lid={C.redShade} uid={uid} lw={6} />}
    </g>
  );
};

/** A see-through balloon with "nothing" inside, for the thought bubble. */
export const GlassBalloon: React.FC<{rx?: number; ry?: number; face?: OFace; uid: string}> = ({rx = 118, ry = 138, face, uid}) => {
  const d = balloonPath(rx, ry);
  return (
    <g>
      <Knot y={ry} color={'#e9f6ff'} />
      <path d={d} fill={'#eef8ff'} {...ol()} />
      <path d={`M ${-rx * 0.62} ${-ry * 0.25} Q ${-rx * 0.55} ${-ry * 0.7} ${-rx * 0.15} ${-ry * 0.8}`} stroke={C.white} strokeWidth={rx * 0.1} fill="none" strokeLinecap="round" />
      <path d={`M ${rx * 0.55} ${ry * 0.2} Q ${rx * 0.5} ${ry * 0.45} ${rx * 0.3} ${ry * 0.6}`} stroke={'#d4ecfb'} strokeWidth={rx * 0.08} fill="none" strokeLinecap="round" />
      {face && (
        <g transform={`translate(0 ${-ry * 0.06})`}>
          <ObjFace face={face} r={rx * 0.19} sp={rx * 0.36} mouthY={ry * 0.34} lid={'#cfe4f2'} uid={uid} lw={6.5} />
        </g>
      )}
    </g>
  );
};

/** Little helium particle. */
export const HeDot: React.FC<{r?: number}> = ({r = 11}) => (
  <g>
    <circle r={r} fill={C.helium} stroke={INK} strokeWidth={5} />
    <circle cx={-r * 0.3} cy={-r * 0.35} r={r * 0.28} fill={C.white} />
  </g>
);

/** Short outward arrow (for "pushes back"). */
export const PushArrow: React.FC<{len?: number}> = ({len = 30}) => (
  <g>
    <path d={`M 0 0 L ${len} 0 M ${len - 10} -9 L ${len} 0 L ${len - 10} 9`} {...ink(6)} />
  </g>
);
