import React from 'react';
import {C, INK, OUT, ink, ol} from '../style';
import {OFace, ObjFace} from './ObjFace';

// ---------------------------------------------------------------- floor pump
// Origin = middle of the base plate on the ground. ext = how far the rod sticks out.
export const PUMP_TOP = 250;
export const pumpGrips = (ext: number) => {
  const y = -(PUMP_TOP + ext + 12);
  return {left: [-63, y] as [number, number], right: [63, y] as [number, number], y};
};
export const PUMP_PORT: [number, number] = [-44, -46];

export const Pump: React.FC<{ext: number; uid: string}> = ({ext, uid}) => {
  const top = PUMP_TOP;
  const id = `${uid}-cyl`;
  const barY = -(top + ext + 24);
  return (
    <g>
      {/* hose port */}
      <rect x={-46} y={-56} width={20} height={22} rx={5} fill={C.metal} {...ol(OUT * 0.7)} />
      {/* base plate */}
      <rect x={-82} y={-26} width={164} height={26} rx={11} fill={C.base} {...ol()} />
      {/* rod and handle */}
      <rect x={-7} y={-(top + ext + 4)} width={14} height={ext + 12} fill={C.metal} {...ol(OUT * 0.7)} />
      <rect x={-86} y={barY} width={172} height={26} rx={12} fill={C.metal} {...ol()} />
      <rect x={-86} y={barY} width={44} height={26} rx={12} fill={C.grip} />
      <rect x={42} y={barY} width={44} height={26} rx={12} fill={C.grip} />
      <rect x={-86} y={barY} width={172} height={26} rx={12} fill="none" stroke={INK} strokeWidth={OUT} />
      {/* cylinder */}
      <clipPath id={id}>
        <rect x={-31} y={-(top - 14)} width={62} height={top - 36} rx={16} />
      </clipPath>
      <rect x={-31} y={-(top - 14)} width={62} height={top - 36} rx={16} fill={C.pump} {...ol()} />
      <rect x={12} y={-top} width={30} height={top} fill={C.pumpShade} clipPath={`url(#${id})`} />
      <rect x={-20} y={-(top - 30)} width={8} height={top - 80} rx={4} fill={'#7cc6ee'} clipPath={`url(#${id})`} />
      {/* gauge */}
      <circle cx={0} cy={-104} r={21} fill={C.white} {...ol(OUT * 0.7)} />
      <path d="M 0 -104 L 9 -116" {...ink(4)} />
      <circle cx={0} cy={-104} r={3.5} fill={INK} />
      {/* cap */}
      <rect x={-38} y={-top} width={76} height={20} rx={7} fill={C.metal} {...ol()} />
    </g>
  );
};

// ---------------------------------------------------------------- hose
export const Hose: React.FC<{p0: number[]; c1: number[]; c2: number[]; p3: number[]; nozzle?: boolean}> = ({p0, c1, c2, p3, nozzle = true}) => {
  const d = `M ${p0[0]} ${p0[1]} C ${c1[0]} ${c1[1]} ${c2[0]} ${c2[1]} ${p3[0]} ${p3[1]}`;
  const ang = (Math.atan2(p3[1] - c2[1], p3[0] - c2[0]) * 180) / Math.PI;
  return (
    <g>
      <path d={d} stroke={INK} strokeWidth={15 + 2 * OUT} fill="none" strokeLinecap="round" />
      <path d={d} stroke={C.hose} strokeWidth={15} fill="none" strokeLinecap="round" />
      {nozzle && (
        <g transform={`translate(${p3[0]} ${p3[1]}) rotate(${ang})`}>
          <rect x={-22} y={-11} width={26} height={22} rx={5} fill={C.metal} {...ol(OUT * 0.7)} />
        </g>
      )}
    </g>
  );
};

// ---------------------------------------------------------------- kettlebell "15 lb"
export const Kettlebell: React.FC<{uid: string}> = ({uid}) => {
  const id = `${uid}-kb`;
  const body = 'M -25 -6 A 48 48 0 1 1 25 -6 Z';
  const handle = 'M -30 -78 C -34 -150 34 -150 30 -78';
  return (
    <g>
      <path d={handle} stroke={INK} strokeWidth={18 + 2 * OUT} fill="none" strokeLinecap="round" />
      <path d={handle} stroke={C.iron} strokeWidth={18} fill="none" strokeLinecap="round" />
      <clipPath id={id}>
        <path d={body} />
      </clipPath>
      <path d={body} fill={C.iron} {...ol()} />
      <circle cx={24} cy={-36} r={52} fill={C.ironShade} clipPath={`url(#${id})`} />
      <circle cx={-8} cy={-52} r={50} fill={C.iron} clipPath={`url(#${id})`} />
      <text x={0} y={-36} textAnchor="middle" fontFamily="InterBlack" fontSize={29} fill={C.white}>
        15 lb
      </text>
    </g>
  );
};

// ---------------------------------------------------------------- diamond ball
export const DIA_R = 72;
const dentGeom = (R: number, depth: number) => {
  const a1 = (200 * Math.PI) / 180;
  const a2 = (290 * Math.PI) / 180;
  const p1 = [R * Math.cos(a1), R * Math.sin(a1)];
  const p2 = [R * Math.cos(a2), R * Math.sin(a2)];
  const m = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2];
  const c = [m[0] * depth, m[1] * depth];
  const deep = [0.25 * p1[0] + 0.5 * c[0] + 0.25 * p2[0], 0.25 * p1[1] + 0.5 * c[1] + 0.25 * p2[1]];
  const d = `M ${p2[0].toFixed(1)} ${p2[1].toFixed(1)} A ${R} ${R} 0 1 1 ${p1[0].toFixed(1)} ${p1[1].toFixed(1)} Q ${c[0].toFixed(1)} ${c[1].toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)} Z`;
  return {d, deep};
};

export const Diamond: React.FC<{dent?: number; face?: OFace; uid: string}> = ({dent = 0, face, uid}) => {
  const R = DIA_R;
  const id = `${uid}-dia`;
  const g = dent > 0 ? dentGeom(R, dent === 1 ? 0.5 : 0.18) : null;
  const shape = g ? g.d : `M ${-R} 0 A ${R} ${R} 0 1 1 ${R} 0 A ${R} ${R} 0 1 1 ${-R} 0 Z`;
  // facets: a hexagonal table and lines to the rim
  const hex = Array.from({length: 6}, (_, i) => {
    const a = (i / 6) * Math.PI * 2 + 0.3;
    return [-10 + Math.cos(a) * 30, -16 + Math.sin(a) * 26];
  });
  const rim = hex.map((p) => {
    const a = Math.atan2(p[1] + 16, p[0] + 10);
    return [Math.cos(a) * R, Math.sin(a) * R];
  });
  const facetD = `M ${hex.map((p) => p.join(' ')).join(' L ')} Z ` + hex.map((p, i) => `M ${p[0]} ${p[1]} L ${rim[i][0]} ${rim[i][1]}`).join(' ');
  return (
    <g>
      <clipPath id={id}>
        <path d={shape} />
      </clipPath>
      <path d={shape} fill={C.diamond} {...ol()} />
      <g clipPath={`url(#${id})`}>
        <circle cx={R * 0.35} cy={R * 0.4} r={R * 0.95} fill={C.diamondShade} />
        <circle cx={-R * 0.08} cy={-R * 0.08} r={R * 0.9} fill={C.diamond} />
        <path d={facetD} stroke={C.diamondHi} strokeWidth={5} fill="none" strokeLinejoin="round" />
        <path d={`M ${-R * 0.55} ${R * 0.55} L ${-R * 0.15} ${R * 0.9} M ${R * 0.6} ${R * 0.1} L ${R * 0.95} ${R * 0.25}`} stroke={C.diamondShade} strokeWidth={4} fill="none" />
      </g>
      <ellipse cx={-R * 0.42} cy={-R * 0.4} rx={R * 0.12} ry={R * 0.2} transform={`rotate(35 ${-R * 0.42} ${-R * 0.4})`} fill={C.white} />
      {g && (
        <path
          d={`M ${g.deep[0]} ${g.deep[1]} l 14 10 l -4 12 l 14 8 M ${g.deep[0]} ${g.deep[1]} l -6 16 l 8 10 M ${g.deep[0]} ${g.deep[1]} l 18 -4 l 8 8`}
          {...ink(4.5)}
        />
      )}
      {face && (
        <g transform={`translate(${R * 0.06} ${R * 0.18})`}>
          <ObjFace face={face} r={R * 0.2} sp={R * 0.36} mouthY={R * 0.4} lid={C.diamondShade} uid={uid} lw={6} />
        </g>
      )}
    </g>
  );
};

/** Little glass shard (for the crack). */
export const Shard: React.FC<{s?: number}> = ({s = 1}) => (
  <path d={`M 0 ${-12 * s} L ${10 * s} ${8 * s} L ${-9 * s} ${6 * s} Z`} fill={C.diamond} {...ol(4)} />
);

// ---------------------------------------------------------------- air puff (comes alive)
export const Puff: React.FC<{face?: OFace; uid: string; squash?: number}> = ({face, uid, squash = 1}) => {
  const circles: [number, number, number][] = [
    [0, -10, 25],
    [-22, 4, 18],
    [22, 4, 18],
    [-9, 11, 17],
    [10, 11, 17],
  ];
  return (
    <g transform={`scale(${1 / squash} ${squash})`}>
      {circles.map(([x, y, r], i) => (
        <circle key={`o${i}`} cx={x} cy={y} r={r + OUT * 0.85} fill={INK} />
      ))}
      {circles.map(([x, y, r], i) => (
        <circle key={`f${i}`} cx={x} cy={y} r={r} fill={i >= 3 ? C.puffShade : C.puff} />
      ))}
      <circle cx={0} cy={-6} r={21} fill={C.puff} />
      {face && (
        <g transform="translate(0 -3)">
          <ObjFace face={face} r={7.5} sp={11} mouthY={12} lid={C.puffShade} uid={uid} lw={4} />
        </g>
      )}
    </g>
  );
};

// ---------------------------------------------------------------- thought bubble
export const ThoughtBubble: React.FC<{w: number; h: number}> = ({w, h}) => {
  const n = 10;
  const circles = Array.from({length: n}, (_, i) => {
    const a = (i / n) * Math.PI * 2;
    return [Math.cos(a) * w * 0.38, Math.sin(a) * h * 0.36, Math.min(w, h) * (i % 2 ? 0.2 : 0.24)] as const;
  });
  return (
    <g>
      {circles.map(([x, y, r], i) => (
        <circle key={`o${i}`} cx={x} cy={y} r={r + OUT} fill={INK} />
      ))}
      <ellipse cx={0} cy={0} rx={w * 0.42 + OUT} ry={h * 0.4 + OUT} fill={INK} />
      {circles.map(([x, y, r], i) => (
        <circle key={`f${i}`} cx={x} cy={y} r={r} fill={C.white} />
      ))}
      <ellipse cx={0} cy={0} rx={w * 0.42} ry={h * 0.4} fill={C.white} />
    </g>
  );
};

export const bubbleClip = (w: number, h: number) => `M ${-w * 0.42} 0 A ${w * 0.42} ${h * 0.4} 0 1 1 ${w * 0.42} 0 A ${w * 0.42} ${h * 0.4} 0 1 1 ${-w * 0.42} 0 Z`;

// ---------------------------------------------------------------- small effects
export const SweatDrop: React.FC<{s?: number}> = ({s = 1}) => (
  <g transform={`scale(${s})`}>
    <path d="M 0 -24 C 9 -10 16 0 16 9 A 16 16 0 1 1 -16 9 C -16 0 -9 -10 0 -24 Z" fill={C.sweat} {...ol(5)} />
    <ellipse cx={-6} cy={7} rx={4} ry={6} fill={C.white} />
  </g>
);

export const Sparkle: React.FC<{s?: number}> = ({s = 22}) => (
  <path
    d={`M 0 ${-s} Q ${s * 0.16} ${-s * 0.16} ${s} 0 Q ${s * 0.16} ${s * 0.16} 0 ${s} Q ${-s * 0.16} ${s * 0.16} ${-s} 0 Q ${-s * 0.16} ${-s * 0.16} 0 ${-s} Z`}
    fill={C.white}
    {...ol(4.5)}
  />
);

/** Dashed square patch ("per square inch"). */
export const Patch: React.FC<{s?: number}> = ({s = 46}) => (
  <rect x={-s / 2} y={-s / 2} width={s} height={s} rx={4} fill="rgba(255,255,255,0.45)" stroke={INK} strokeWidth={5} strokeDasharray="10 7" />
);

/** Dust cloud for landings: circles with one merged outline. */
export const Dust: React.FC<{s: number}> = ({s}) => {
  const cs: [number, number, number][] = [
    [-26, -6, 14],
    [0, -12, 18],
    [26, -6, 14],
  ];
  if (s <= 0.01) return null;
  return (
    <g transform={`scale(${s})`}>
      {cs.map(([x, y, r], i) => (
        <circle key={`o${i}`} cx={x} cy={y} r={r + 6} fill={INK} />
      ))}
      {cs.map(([x, y, r], i) => (
        <circle key={`f${i}`} cx={x} cy={y} r={r} fill={'#f3efe6'} />
      ))}
    </g>
  );
};

/** Soft contact shadow: a radial gradient (cheap to render), soft edge like a 3 px blur. */
export const Shadow: React.FC<{rx: number; ry?: number; gradId: string; opacity?: number}> = ({rx, ry = 14, gradId, opacity = 1}) => (
  <ellipse cx={0} cy={0} rx={rx + 6} ry={ry + 4} fill={`url(#${gradId})`} opacity={opacity} />
);

export const ShadowGradient: React.FC<{id: string}> = ({id}) => (
  <radialGradient id={id}>
    <stop offset="0%" stopColor={C.shadow} />
    <stop offset="70%" stopColor={C.shadow} />
    <stop offset="100%" stopColor="rgba(52, 68, 36, 0)" />
  </radialGradient>
);
