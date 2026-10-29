// One outline weight and one flat palette for every drawing and every code effect.
export const OUT = 9;
export const INK = '#1c1a20';

export const C = {
  white: '#ffffff',
  shade: '#e3e7ee',
  tongue: '#ff7f95',
  red: '#ff5264',
  redShade: '#dc394c',
  redHi: '#ffc2c9',
  redFold: '#c22f41',
  pump: '#39a1da',
  pumpShade: '#2a7fb2',
  metal: '#d3d9e1',
  metalShade: '#aab4c0',
  grip: '#2c2c32',
  base: '#5b6574',
  hose: '#424852',
  diamond: '#bff2ff',
  diamondShade: '#8bd5ea',
  diamondHi: '#f4fdff',
  iron: '#4d525b',
  ironShade: '#3b3f46',
  puff: '#ffffff',
  puffShade: '#dce8f6',
  helium: '#fff0a0',
  heliumShade: '#efcf5e',
  sweat: '#8ed3ff',
  sky1: '#72bff2',
  sky2: '#d4f0ff',
  hill: '#a9dc90',
  hillShade: '#93cf7b',
  ground: '#87ca6c',
  groundDark: '#74b95b',
  tree: '#5aae56',
  treeShade: '#48984a',
  trunk: '#9c6a42',
  cloud: '#ffffff',
  cloudShade: '#e3eefa',
  flower: '#ffd84d',
  flower2: '#ff8fb1',
  parch: '#f1ddb0',
  parchDark: '#dcc08a',
  parchEdge: '#c49f63',
  sepia: '#5a3a1f',
  sepiaLight: '#8a6a45',
  copper: '#cd8249',
  copperShade: '#a65f2b',
  copperHi: '#ecb37e',
  shadow: 'rgba(52, 68, 36, 0.24)',
};

/** Outline drawn under the fill (paint-order), so the visible ink is OUT wide outside. */
export const ol = (w = OUT) => ({
  stroke: INK,
  strokeWidth: 2 * w,
  paintOrder: 'stroke' as const,
  strokeLinejoin: 'round' as const,
  strokeLinecap: 'round' as const,
});

/** A plain ink line. */
export const ink = (w = 7) => ({
  stroke: INK,
  strokeWidth: w,
  fill: 'none',
  strokeLinejoin: 'round' as const,
  strokeLinecap: 'round' as const,
});
