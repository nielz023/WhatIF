// Time single 4K stills with different settings: node scripts/timing.mjs
import path from 'path';
import fs from 'fs';
import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';

const browserExecutable = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), outDir: path.resolve('build/bundle')});
fs.mkdirSync('out/timing', {recursive: true});
for (const gl of ['angle']) {
  let browser;
  try {
    browser = await openBrowser('chrome', {browserExecutable, chromiumOptions: {gl}});
  } catch (e) {
    console.log(gl, 'cannot open:', e.message.split('\n')[0]);
    continue;
  }
  for (const [label, t, props] of [
    ['wide', 0.5, {}],
    ['close+blur', 7.5, {}],
    ['close-noblur', 7.5, {noBlur: true}],
  ]) {
    const composition = await selectComposition({serveUrl, id: 'VacuumBalloon', inputProps: props, puppeteerInstance: browser});
    const frame = Math.round(t * 60);
    const t0 = Date.now();
    for (let r = 0; r < 2; r++) {
      await renderStill({serveUrl, composition, frame, output: `out/timing/${gl}-${label}.jpeg`, imageFormat: 'jpeg', scale: 2, inputProps: props, puppeteerInstance: browser});
    }
    console.log(`${String(gl).padEnd(12)} ${label.padEnd(14)} ${((Date.now() - t0) / 2000).toFixed(2)} s/frame`);
  }
  await browser.close({silent: true});
}
