// Render stills of the Short at given times (seconds) into a folder, bundling once.
// node scripts/stills.mjs <outDir> <scale> t1 t2 ...
import path from 'path';
import fs from 'fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const [outDir, scaleArg, ...times] = process.argv.slice(2);
const scale = Number(scaleArg || 0.5);
const browser = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const browserExecutable = fs.existsSync(browser) ? browser : undefined;
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), outDir: path.resolve('build/bundle')});
const composition = await selectComposition({serveUrl, id: 'VacuumBalloon', browserExecutable});
for (const ts of times) {
  const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(ts) * composition.fps));
  const output = path.join(outDir, `t${Number(ts).toFixed(2).padStart(5, '0')}.png`);
  await renderStill({serveUrl, composition, frame, output, scale, browserExecutable, chromiumOptions: {gl: 'angle'}});
  console.log('rendered', output);
}
