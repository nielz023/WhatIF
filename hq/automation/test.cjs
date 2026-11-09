#!/usr/bin/env node
/**
 * AUTOMATISCHE TEST VAN HET HQ (verbeterlijst punt 69).
 * Draai dit na `npm run build && sh automation/pagina.sh` en vóór elke publicatie:
 *
 *   node automation/test.cjs            (pc en telefoon)
 *   node automation/test.cjs --snel     (alleen pc, zonder screenshots)
 *
 * Opent elke pagina en elk tabblad op pc- (1440x900) en telefoonformaat (iPhone 13), en zoekt naar:
 *   - een crash ("Dit scherm liep vast" of "kon niet laden"),
 *   - JavaScript-fouten op de pagina,
 *   - oude Engelse spelteksten (Reset game, Greenlight project, enz.).
 * Projectbestanden worden nagebootst vanuit /mnt/project-files, zodat de echte stand te zien is.
 * Screenshots komen in automation/test-uit/. Stopt met code 1 als er iets mis is.
 */
const { chromium, devices } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const HQ = path.resolve(__dirname, '..');
const DIST = path.join(HQ, 'dist');
const UIT = path.join(__dirname, 'test-uit');
const PROJ = '/mnt/project-files';
const PORT = 4199;
const SNEL = process.argv.includes('--snel');

const PAGINAS = ['overzicht', 'videos', 'kanaal', 'kennis', 'driftmark', 'coach', 'settings', 'hq', 'projects', 'agents', 'warroom'];
const ENGELS = /\b(Reset game|Greenlight project|Import save|Export save|Supabase|Danger zone|Assign task|All channels|Approve deliverable|Request changes|Send back|Ready to publish|Production pipeline|Live on Threads|Performance|Morale|Working title|Target audience|Save settings|Cancel project|No projects yet|Pipeline board|Task engine|Create channel|Channel name|Waiting for you|CEO approval required|Recently delivered|Assigned tasks|Open agent|Reassign to)\b/;

function zelfTestPagina() {
  const page = fs.readFileSync(path.join(DIST, 'page.html'), 'utf8');
  fs.writeFileSync(path.join(DIST, 't.html'), '<meta name="viewport" content="width=device-width,initial-scale=1">' + page);
}

/** window.claude nabootsen: files leest uit /mnt/project-files, de rest is er niet */
const MOCK = `(() => {
  const files = {
    read: async (p) => { const r = await fetch('/__files/' + String(p).replace(/^\\/+/, '')); if (!r.ok) { const e = new Error('not_found'); e.code = 'not_found'; throw e; } return { bytes: new Uint8Array(await r.arrayBuffer()), size: 0, revision: '1' }; },
    list: async () => ({ entries: [] }),
  };
  window.claude = { use: async (n) => (n === 'files' ? files : null) };
  try { localStorage.setItem('dm-tour', 'gezien'); } catch (e) {}
})();`;

async function testViewport(browser, naam, opts, fouten) {
  const ctx = await browser.newContext(opts);
  const p = await ctx.newPage();
  await p.addInitScript(MOCK);
  await p.route('**/__files/**', async (route) => {
    const rel = decodeURIComponent(new URL(route.request().url()).pathname.replace(/^\/__files\//, ''));
    const f = path.join(PROJ, rel);
    if (!f.startsWith(PROJ) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) return route.fulfill({ status: 404, body: '' });
    return route.fulfill({ status: 200, body: fs.readFileSync(f) });
  });
  const err = [];
  p.on('pageerror', (e) => err.push(e.message.slice(0, 200)));
  p.on('console', (m) => { if (m.type() === 'error' && !/favicon|fonts\.g|net::ERR|Failed to load resource|WebGL|GPU stall/i.test(m.text())) err.push('console: ' + m.text().slice(0, 200)); });
  await p.goto(`http://localhost:${PORT}/t.html`);
  await p.waitForFunction(() => !!window.__dmGame, null, { timeout: 20000 });
  await p.waitForTimeout(2500);
  // zo licht mogelijk renderen, anders duurt een screenshot met software-WebGL te lang
  await p.evaluate(() => { try { window.__dmWorld?.getState().setQuality('snel'); } catch (e) {} });
  for (const id of PAGINAS) {
    await p.evaluate((x) => window.__dmGame.getState().setPage(x), id);
    await p.waitForTimeout(id === 'driftmark' ? 3000 : 2500);
    // alle tabbladen langs (knoppen in de tabbalk)
    const SEL = '[role="tab"], .sticky button.rounded-full';
    const aantal = await p.evaluate((sel) => document.querySelectorAll(sel).length, SEL);
    let n = 0;
    for (let i = 0; i < Math.min(aantal, 12); i++) {
      const ok = await p.evaluate(([sel, k]) => { const b = document.querySelectorAll(sel)[k]; if (!b || !b.offsetParent) return false; b.click(); return true; }, [SEL, i]);
      if (!ok) continue;
      await p.waitForTimeout(700); n++;
      await controle(p, `${naam}/${id}/tab${n}`, fouten);
    }
    await controle(p, `${naam}/${id}`, fouten);
    if (!SNEL) { try { await p.screenshot({ path: path.join(UIT, `${naam}_${id}.png`), timeout: 90000 }); } catch { fouten.push(`${naam}/${id}: screenshot lukte niet (te traag)`); } }
    console.log(`  ${naam.padEnd(8)} ${id.padEnd(10)} ${n} tabbladen`);
  }
  for (const e of [...new Set(err)]) fouten.push(`${naam}: JS-fout: ${e}`);
  await ctx.close();
}

async function controle(p, waar, fouten) {
  const tekst = await p.evaluate(() => document.body.innerText);
  if (/Dit scherm liep vast|kon niet laden\. De rest werkt/.test(tekst)) fouten.push(`${waar}: crash: ${(tekst.match(/(Dit scherm liep vast|kon niet laden)[\s\S]{0,160}/) || [''])[0].replace(/\s+/g, ' ')}`);
  const m = tekst.match(ENGELS);
  if (m) fouten.push(`${waar}: Engelse tekst "${m[0]}"`);
}

(async () => {
  zelfTestPagina();
  fs.mkdirSync(UIT, { recursive: true });
  const srv = spawn('python3', ['-m', 'http.server', String(PORT)], { cwd: DIST, stdio: 'ignore' });
  await new Promise((r) => setTimeout(r, 800));
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader'] });
  const fouten = [];
  try {
    console.log('HQ-test: pc');
    await testViewport(browser, 'pc', { viewport: { width: 1440, height: 900 } }, fouten);
    if (!SNEL) { console.log('HQ-test: telefoon'); await testViewport(browser, 'telefoon', { ...devices['iPhone 13'] }, fouten); }
  } finally { await browser.close(); srv.kill(); }
  const uniek = [...new Set(fouten)];
  if (uniek.length) { console.log(`\n✗ ${uniek.length} probleem/problemen:`); uniek.forEach((f) => console.log('  - ' + f)); process.exit(1); }
  console.log('\n✓ Alles in orde' + (SNEL ? '' : `, screenshots in ${path.relative(process.cwd(), UIT)}/`));
})().catch((e) => { console.error(e); process.exit(1); });
