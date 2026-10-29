import React from 'react';
import {C, INK, OUT, ol} from '../style';

// Set pieces, each drawn in the coordinates of its own depth layer.

const CloudShape: React.FC<{s?: number}> = ({s = 1}) => {
  const cs: [number, number, number][] = [
    [0, -10, 62],
    [-72, 14, 46],
    [74, 14, 50],
    [-34, 26, 44],
    [38, 28, 44],
  ];
  return (
    <g transform={`scale(${s})`}>
      {cs.map(([x, y, r], i) => (
        <circle key={`o${i}`} cx={x} cy={y} r={r + OUT * 1.6} fill={INK} />
      ))}
      {cs.map(([x, y, r], i) => (
        <circle key={`f${i}`} cx={x} cy={y} r={r} fill={C.cloud} />
      ))}
      <ellipse cx={8} cy={52} rx={92} ry={16} fill={C.cloudShade} />
      <rect x={-130} y={52} width={260} height={60} fill="none" />
    </g>
  );
};

/** Z 4200. drift = horizontal offset in layer units. */
export const Clouds: React.FC<{drift: number}> = ({drift}) => (
  <g>
    <g transform={`translate(${-900 + drift} -1250)`}>
      <CloudShape s={1.5} />
    </g>
    <g transform={`translate(${650 - drift * 0.7} -1500)`}>
      <CloudShape s={1.9} />
    </g>
    <g transform={`translate(${1750 + drift * 0.5} -900)`}>
      <CloudShape s={1.3} />
    </g>
    <g transform={`translate(${-250 - drift * 0.4} -300)`}>
      <CloudShape s={1.1} />
    </g>
    <g transform={`translate(${1250 + drift * 0.8} 50)`}>
      <CloudShape s={1.0} />
    </g>
  </g>
);

/** Z 3000: rolling hills; the outline of their tops is the horizon line. */
export const Hills: React.FC = () => (
  <g>
    <rect x={-2600} y={1600} width={6000} height={4000} fill={C.ground} />
    <path
      d="M -2600 1700 L -2600 1420 C -2100 1180 -1500 1200 -1000 1430 C -650 1260 -150 1250 250 1450 C 700 1220 1300 1230 1750 1440 C 2150 1270 2700 1260 3400 1450 L 3400 1700 Z"
      fill={C.hillShade}
      {...ol(OUT * 2.2)}
    />
    <path
      d="M -2600 1760 L -2600 1560 C -2000 1390 -1300 1420 -700 1600 C -150 1420 600 1400 1150 1590 C 1700 1420 2600 1430 3400 1620 L 3400 1760 Z"
      fill={C.hill}
      {...ol(OUT * 2.2)}
    />
    <rect x={-2600} y={1690} width={6000} height={4000} fill={C.ground} />
    <path d="M -2600 1690 L 3400 1690" stroke={INK} strokeWidth={OUT * 2.2} />
  </g>
);

const Tree: React.FC<{s?: number}> = ({s = 1}) => {
  const cs: [number, number, number][] = [
    [0, -330, 120],
    [-95, -250, 95],
    [95, -250, 98],
    [-40, -190, 90],
    [55, -185, 92],
  ];
  return (
    <g transform={`scale(${s})`}>
      <path d="M -26 0 L -18 -200 L 18 -200 L 26 0 Z" fill={C.trunk} {...ol(OUT * 1.5)} />
      {cs.map(([x, y, r], i) => (
        <circle key={`o${i}`} cx={x} cy={y} r={r + OUT * 1.5} fill={INK} />
      ))}
      {cs.map(([x, y, r], i) => (
        <circle key={`f${i}`} cx={x} cy={y} r={r} fill={i >= 3 ? C.treeShade : C.tree} />
      ))}
      <circle cx={-30} cy={-345} r={70} fill={C.tree} />
      <ellipse cx={-50} cy={-380} rx={28} ry={18} fill={'#78c46f'} />
    </g>
  );
};

const Bush: React.FC<{s?: number}> = ({s = 1}) => {
  const cs: [number, number, number][] = [
    [0, -70, 70],
    [-70, -40, 52],
    [70, -40, 56],
  ];
  return (
    <g transform={`scale(${s})`}>
      {cs.map(([x, y, r], i) => (
        <circle key={`o${i}`} cx={x} cy={y} r={r + OUT * 1.5} fill={INK} />
      ))}
      {cs.map(([x, y, r], i) => (
        <circle key={`f${i}`} cx={x} cy={y} r={r} fill={i === 0 ? C.tree : C.treeShade} />
      ))}
      <rect x={-150} y={-6} width={300} height={90} fill={C.ground} />
    </g>
  );
};

/** Z 1800: a tree on the right, bushes, and the middle ground band. */
export const MidGround: React.FC = () => (
  <g>
    <rect x={-2400} y={1585} width={6000} height={4000} fill={C.ground} />
    <g transform="translate(1110 1600)">
      <Tree s={1.15} />
    </g>
    <g transform="translate(-260 1600)">
      <Bush s={1.25} />
    </g>
    <g transform="translate(1700 1600)">
      <Bush s={1.1} />
    </g>
  </g>
);

const Tuft: React.FC<{s?: number; flip?: boolean; flower?: string}> = ({s = 1, flip, flower}) => (
  <g transform={`scale(${flip ? -s : s} ${s})`}>
    <path d="M -40 0 Q -46 -60 -60 -96 Q -22 -54 -12 0 Z" fill={C.groundDark} {...ol(OUT * 0.8)} />
    <path d="M -16 0 Q -12 -80 6 -130 Q 16 -70 12 0 Z" fill={C.tree} {...ol(OUT * 0.8)} />
    <path d="M 6 0 Q 30 -50 66 -84 Q 40 -40 36 0 Z" fill={C.groundDark} {...ol(OUT * 0.8)} />
    {flower && (
      <g transform="translate(-58 -100)">
        {[0, 72, 144, 216, 288].map((a) => (
          <ellipse key={a} cx={0} cy={-14} rx={9} ry={14} transform={`rotate(${a})`} fill={flower} {...ol(4)} />
        ))}
        <circle r={8} fill={'#ffb03b'} {...ol(4)} />
      </g>
    )}
  </g>
);

/** Z 650: blades of grass in the bottom corners. */
export const Foreground: React.FC = () => (
  <g>
    <g transform="translate(250 1380)">
      <Tuft s={1.1} flower={C.flower} />
    </g>
    <g transform="translate(700 1392)">
      <Tuft s={1.0} flip flower={C.flower2} />
    </g>
  </g>
);

/** Z 1000 ground under the characters, with a few small details. */
export const NearGround: React.FC = () => (
  <g>
    <rect x={-1600} y={1440} width={4000} height={3000} fill={C.ground} />
    {[
      [-60, 1560],
      [150, 1650],
      [820, 1600],
      [980, 1720],
      [430, 1740],
    ].map(([x, y], i) => (
      <path key={i} d={`M ${x - 14} ${y} q 6 -16 12 0 q 6 -20 12 0`} stroke={C.groundDark} strokeWidth={7} fill="none" strokeLinecap="round" />
    ))}
    <g transform="translate(150 1700)">
      <Tuft s={0.55} flower={C.flower} />
    </g>
    <g transform="translate(860 1690)">
      <Tuft s={0.5} flip flower={C.flower2} />
    </g>
    <g transform="translate(-40 1640)">
      <Tuft s={0.42} flip />
    </g>
  </g>
);
