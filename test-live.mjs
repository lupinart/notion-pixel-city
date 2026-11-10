// Isolated test copy only. SITE_BASE_URL optionally verifies the deployed website.
import assert from 'node:assert/strict';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE);
const files = new Set(['embed.html', 'embed.mjs', 'time.mjs', 'day.svg', 'dusk.svg', 'night.svg', 'today.svg']);
const server = createServer(async (req, res) => {
  const file = new URL(req.url, 'http://localhost').pathname.slice(1);
  if (!files.has(file)) {res.writeHead(404).end(); return;}
  try {
    const mime = file.endsWith('.mjs') ? 'text/javascript' : file.endsWith('.svg') ? 'image/svg+xml' : 'text/html';
    res.writeHead(200, {'Content-Type':mime}); res.end(await readFile(file));
  } catch {res.writeHead(404).end();}
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const base = process.env.SITE_BASE_URL || `http://127.0.0.1:${server.address().port}/`;
const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH, headless:true});
try {
  const context = await browser.newContext({timezoneId:'America/Los_Angeles', viewport:{width:1500,height:600}});
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.clock.install({time:new Date('2026-11-10T08:59:50Z')}); // Taipei 16:59:50
  await page.goto(new URL('embed.html', base).href);
  const scene = async expected => page.waitForFunction(e => document.querySelector('#city').dataset.scene === e, expected);
  await scene('day');
  // A stalled request must expire and retry; late responses must not replace a newer scene.
  let stalled;
  let intercepted = false;
  await page.route('**/dusk.svg*', route => {
    if (!intercepted) {intercepted = true; stalled = route; return;}
    return route.continue();
  });
  await page.clock.fastForward(15_000);
  assert.equal(await page.locator('#city').getAttribute('data-scene'), 'day');
  assert.equal(await page.locator('#city').evaluate(el => el.complete && el.naturalWidth > 0), true);
  await page.clock.fastForward(15_000);
  await scene('dusk');
  await page.clock.setSystemTime(new Date('2026-11-10T10:59:55Z'));
  await page.clock.fastForward(15_000);
  await scene('night');
  await stalled.fulfill({contentType:'image/svg+xml', body:'<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"/>'});
  await page.waitForTimeout(50);
  assert.equal(await page.locator('#city').getAttribute('data-scene'), 'night');
  await page.clock.setSystemTime(new Date('2026-12-31T15:59:55Z'));
  await page.clock.fastForward(15_000);
  await page.waitForFunction(() => document.querySelector('#city').dataset.day === '2027-01-01');
  await page.clock.setSystemTime(new Date('2027-01-01T00:00:00Z'));
  await page.reload();
  await scene('day'); // Taipei 08:00, despite America/Los_Angeles context.
  for (const colorScheme of ['light','dark']) {
    await page.emulateMedia({colorScheme});
    await page.setViewportSize({width:375,height:150});
    assert.equal(await page.locator('#city').evaluate(el => el.complete && el.naturalWidth > 0), true);
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    await page.screenshot({path:`live-${colorScheme}-375.png`});
  }
  assert.deepEqual(errors, []);
  console.log(`PASS ${base}: Taipei day→dusk→night, stalled/late requests, midnight, reload, other timezone, narrow light/dark`);
} finally {
  await browser.close();
  await new Promise(resolve => server.close(resolve));
}
