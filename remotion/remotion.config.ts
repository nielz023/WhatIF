import {Config} from '@remotion/cli/config';
import fs from 'fs';

// In the cloud container there is no browser download; use the pre-installed headless shell
// when it exists. On a normal machine Remotion picks its own browser.
const HEADLESS = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
if (fs.existsSync(HEADLESS)) Config.setBrowserExecutable(HEADLESS);

// 'angle' uses the graphics card when there is one and was also 3-4x faster than 'swangle'
// on the CPU-only cloud machine.
Config.setChromiumOpenGlRenderer('angle');

Config.setVideoImageFormat('png');
Config.setPixelFormat('yuv420p');
