// Beat times in composition seconds. The voice starts at VO_START; word times come from
// ElevenLabs Scribe, the pause edges from loudness (RMS < -42 dB for >= 0.18 s).
export const VO_START = 0.1;
export const DURATION = 26.0;

const w = (scribe: number) => +(scribe + VO_START).toFixed(2);

export const T = {
  // 1. "Why fill a balloon with helium, when you could fill it with nothing?"
  fill: w(0.32),
  helium: w(1.12),
  when: w(2.0),
  nothing: w(2.8),
  nothingEnd: w(3.1),
  // 2. "An empty one would be even lighter, right?"
  an: w(3.68),
  empty: w(3.92),
  lighter: w(4.88),
  right: w(5.28),
  rightEnd: w(5.56),
  // 3. "But air pushes from all sides, almost 15 pounds per square inch."
  but: w(6.16),
  air: w(6.4),
  pushes: w(6.8),
  sides: w(7.76),
  almost: w(8.56),
  fifteen: w(9.04),
  pounds: w(9.6),
  square: w(10.24),
  inch: w(10.56),
  inchEnd: w(10.92),
  // 4. "Helium pushes back. A vacuum can't, so the balloon just gets crushed."
  helium2: w(11.44),
  pushesBack: w(12.08),
  back: w(12.48),
  vacuum: w(13.36),
  cant: w(14.04),
  so: w(14.8),
  crushed: w(15.84),
  crushedEnd: w(16.36),
  // 5. "So what about a hard shell?"
  so2: w(17.04),
  hard: w(17.84),
  shell: w(18.16),
  shellEnd: w(18.42),
  // 6. "Even a diamond one caves in, if it's light enough to float."
  even: w(18.88),
  diamond: w(19.48),
  caves: w(20.0),
  inWord: w(20.4),
  ifIts: w(20.88),
  float: w(21.76),
  floatEnd: w(21.98),
  // 7. "That's why nobody's pulled it off since 1670."
  thats: w(22.64),
  nobody: w(23.04),
  pulled: w(23.48),
  since: w(24.12),
  y1670: w(24.32),
  voEnd: w(25.16),
};
