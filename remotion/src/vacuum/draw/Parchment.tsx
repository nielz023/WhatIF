import React from 'react';
import {C, INK, OUT, ol} from '../style';
import {easeInCubic, easeOutCubic, inv, rnd, wobble} from '../anim';

// Screen-space scroll that unrolls over the camera and shows Lana de Terzi's 1670
// "flying ship" with four emptied copper spheres. Drawn in sepia on parchment.

const SEP = C.sepia;
const sep = (w: number) => ({stroke: SEP, strokeWidth: w, fill: 'none', strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const});

const CRUMPLE = Array.from({length: 16}, (_, i) => {
  const a = (i / 16) * Math.PI * 2 - Math.PI / 2;
  const r = (i % 2 === 0 ? 1 : 0.74) + (rnd(i + 31) - 0.5) * 0.2;
  return [Math.cos(a) * r, Math.sin(a) * r * 0.8] as const;
});

const Sphere: React.FC<{r: number; crumpled: boolean; id: string}> = ({r, crumpled, id}) => {
  if (crumpled) {
    const d = `M ${CRUMPLE.map(([x, y]) => `${(x * r * 0.8).toFixed(1)} ${(y * r * 0.8 + r * 0.15).toFixed(1)}`).join(' L ')} Z`;
    return (
      <g>
        <path d={d} fill={C.copperShade} stroke={SEP} strokeWidth={6} strokeLinejoin="round" />
        <path d={`M ${-r * 0.4} ${-r * 0.1} L 0 ${r * 0.15} L ${-r * 0.1} ${r * 0.5} M ${r * 0.35} ${-r * 0.3} L ${r * 0.05} 0`} {...sep(3.5)} />
      </g>
    );
  }
  return (
    <g>
      <clipPath id={id}>
        <circle r={r} />
      </clipPath>
      <circle r={r} fill={C.copper} stroke={SEP} strokeWidth={6} />
      <g clipPath={`url(#${id})`}>
        <circle cx={r * 0.3} cy={r * 0.35} r={r} fill={C.copperShade} />
        <circle cx={-r * 0.08} cy={-r * 0.08} r={r * 0.9} fill={C.copper} />
      </g>
      <ellipse cx={-r * 0.38} cy={-r * 0.38} rx={r * 0.14} ry={r * 0.24} transform={`rotate(40 ${-r * 0.38} ${-r * 0.38})`} fill={C.copperHi} />
      <path d={`M ${-r} 0 Q 0 ${r * 0.35} ${r} 0`} {...sep(2.5)} />
    </g>
  );
};

export const SPHERE_CRUNCH = [23.4, 23.6, 23.8, 24.0];
export const SHIP_FALL = 24.08;
export const STAMP = 24.46;
export const UNROLL = [22.68, 23.06];
export const ROLLUP = [25.3, 25.62];

export const Parchment: React.FC<{t: number; uid: string}> = ({t, uid}) => {
  if (t < UNROLL[0] || t > ROLLUP[1] + 0.25) return null;
  const top = 110;
  const full = 1810;
  let bottom: number;
  let lift = 0;
  if (t < UNROLL[1]) bottom = top + (full - top) * easeOutCubic(inv(UNROLL[0], UNROLL[1], t));
  else if (t < ROLLUP[0]) bottom = full;
  else {
    bottom = full - (full - top) * easeInCubic(inv(ROLLUP[0], ROLLUP[1], t));
    lift = 380 * easeInCubic(inv(ROLLUP[1] - 0.08, ROLLUP[1] + 0.22, t));
  }
  // ship: sinks a little at every crumpled sphere, then drops out of the frame
  const crunched = SPHERE_CRUNCH.map((c) => t >= c);
  let sink = 0;
  SPHERE_CRUNCH.forEach((c) => {
    if (t >= c) sink += 18 + 10 * wobble(t, c, 4, 7);
  });
  let fall = 0;
  let tilt = 0;
  if (t >= SHIP_FALL) {
    const x = t - SHIP_FALL;
    fall = 0.5 * 12000 * x * x;
    tilt = 26 * x;
  }
  // after landing the stamp keeps a gentle pulse, so the hold is never a frozen picture
  const stampS =
    t < STAMP
      ? 0
      : 1 + 0.55 * (1 - easeOutCubic(inv(STAMP, STAMP + 0.14, t))) - 0.06 * wobble(t, STAMP + 0.14, 5, 9) + 0.014 * Math.sin(2 * Math.PI * 1.4 * (t - STAMP));
  const cloudDrift = 10 * Math.sin(2 * Math.PI * 0.35 * t);
  const clipPaper = `${uid}-paper`;
  const clipFrame = `${uid}-frame`;
  const spheres: [number, number][] = [
    [-232, -470],
    [-128, -548],
    [128, -548],
    [232, -470],
  ];
  return (
    <svg width={1080} height={1920} viewBox="0 0 1080 1920" style={{position: 'absolute', inset: 0, overflow: 'visible'}}>
      <g transform={`translate(0 ${-lift})`}>
        <clipPath id={clipPaper}>
          <rect x={-60} y={top} width={1200} height={Math.max(0, bottom - top)} />
        </clipPath>
        <clipPath id={clipFrame}>
          <rect x={92} y={262} width={896} height={1426} />
        </clipPath>
        <g clipPath={`url(#${clipPaper})`}>
          <rect x={-60} y={top} width={1200} height={full - top + 40} fill={C.parch} />
          {Array.from({length: 26}, (_, i) => (
            <circle key={i} cx={60 + rnd(i) * 960} cy={180 + rnd(i + 50) * 1560} r={3 + rnd(i + 90) * 6} fill={C.parchDark} opacity={0.55} />
          ))}
          <rect x={80} y={250} width={920} height={1450} {...sep(6)} />
          <rect x={98} y={268} width={884} height={1414} {...sep(2.5)} />
          <g clipPath={`url(#${clipFrame})`}>
            {/* sky hatching and clouds */}
            {Array.from({length: 7}, (_, i) => (
              <path key={i} d={`M ${150 + (i % 3) * 40} ${330 + i * 34} l ${120 + (i % 2) * 60} 0`} {...sep(2.5)} />
            ))}
            <g transform={`translate(${cloudDrift} 0)`}>
              <path d="M 700 420 q 20 -40 60 -20 q 30 -40 70 -6 q 40 -6 36 30 q -10 22 -40 18 l -110 0 q -36 -4 -16 -22 Z" {...sep(3.5)} />
            </g>
            <g transform={`translate(${-cloudDrift * 0.8} 0)`}>
              <path d="M 160 780 q 16 -30 46 -14 q 24 -30 54 -4 q 30 -4 28 22 q -8 16 -30 14 l -84 0 q -28 -4 -14 -18 Z" {...sep(3)} />
            </g>
            <path d="M 760 760 q 10 -10 20 0 q 10 -10 20 0 M 820 700 q 8 -8 16 0 q 8 -8 16 0" {...sep(3)} />
            {/* the flying ship */}
            <g transform={`translate(540 ${1075 + sink + fall}) rotate(${tilt}) scale(1.2)`}>
              {spheres.map(([x, y], i) => (
                <g key={`rope${i}`}>
                  <path d={`M ${x} ${y + 50} L ${x * 0.95} 0`} {...sep(5)} />
                  <path d={`M ${x} ${y} L ${x < 0 ? -268 : 268} 2 M ${x} ${y} L ${x * 0.35} -4`} {...sep(2.2)} />
                </g>
              ))}
              <path d="M 0 0 L 0 -350" {...sep(8)} />
              <path d="M -96 -322 Q 0 -294 96 -322 L 86 -118 Q 0 -94 -86 -118 Z" {...sep(5)} fill="#f8edd3" />
              <path d="M -90 -250 Q 0 -226 90 -250 M -88 -186 Q 0 -162 88 -186" {...sep(2.5)} />
              <path d="M -272 0 Q -252 102 -150 118 L 150 118 Q 252 102 272 0 Z" {...sep(6)} fill="#e2c38c" />
              <path d="M -256 40 Q 0 62 256 40 M -222 82 Q 0 100 222 82" {...sep(3)} />
              <path d="M -272 0 q -34 -12 -26 -46 q 18 -14 30 4 M 272 0 q 34 -12 26 -46 q -18 -14 -30 4" {...sep(4)} />
              <circle cx={-58} cy={-28} r={15} {...sep(4)} fill="#f3e3bd" />
              <circle cx={44} cy={-30} r={15} {...sep(4)} fill="#f3e3bd" />
              <path d="M -72 -14 L -44 -14 M 30 -16 L 58 -16" {...sep(4)} />
              {spheres.map(([x, y], i) => (
                <g key={`sph${i}`} transform={`translate(${x} ${y}) scale(${crunched[i] ? 1 + 0.18 * wobble(t, SPHERE_CRUNCH[i], 5, 8) : 1})`}>
                  <Sphere r={58} crumpled={crunched[i]} id={`${uid}-s${i}`} />
                </g>
              ))}
            </g>
            {stampS > 0 && (
              <g transform={`translate(540 1060) rotate(-4) scale(${stampS})`}>
                <text x={0} y={80} textAnchor="middle" fontFamily="SerifBI" fontSize={250} fill={SEP}>
                  1670
                </text>
              </g>
            )}
          </g>
        </g>
        {/* the two rolls */}
        {[top, bottom].map((y, i) => (
          <g key={i} transform={`translate(0 ${y})`}>
            <rect x={-60} y={-38} width={1200} height={76} rx={38} fill={C.parchDark} {...ol(OUT)} />
            <path d="M -60 -12 L 1140 -12" stroke={C.parch} strokeWidth={8} />
            <path d="M -60 16 L 1140 16" stroke={C.parchEdge} strokeWidth={6} />
          </g>
        ))}
      </g>
      <rect x={0} y={0} width={0} height={0} fill={INK} />
    </svg>
  );
};
