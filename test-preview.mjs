// Run from a disposable /private/tmp/codex-builds copy; isolated Chromium only.
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE);
const browser = await chromium.launch({executablePath: process.env.CHROMIUM_PATH, headless: true});
try {
  const page = await browser.newPage({viewport: {width: 1500, height: 600}});
  for (const scene of ['day', 'dusk', 'night']) {
    await page.goto(pathToFileURL(resolve(`${scene}.svg`)).href);
    assert.equal(await page.locator('svg').getAttribute('data-scene'), scene);
    assert.equal(await page.locator('#heading-text').getAttribute('aria-label'), 'PAI任務管理');
    assert.equal(await page.locator('text').count(), 0, 'Heading must use fixed pixels, not device fonts');
    const headingTop = await page.locator('#heading-text').evaluate(el => el.getBBox().y);
    for (const selector of ['.cloud', '.plane']) {
      const bottoms = await page.locator(selector).evaluateAll(els => els.map(el => {const b=el.getBBox();return b.y+b.height;}));
      assert.ok(bottoms.every(bottom => bottom <= headingTop-16), 'Moving sky elements must leave clear space above lettering');
    }
    assert.equal(await page.locator('#year').getAttribute('aria-label'), '2026');
    const bounds = await page.locator('svg').evaluate(svg => {
      const box = id => {const b = svg.querySelector(id).getBBox(); return {x:b.x,y:b.y,width:b.width,height:b.height};};
      return {date:box('#date'), tower:box('#taipei-101'), skyline:box('#skyline'),
        groups:[...svg.querySelectorAll('#city > g')].map(el => box(`#${el.id}`))};
    });
    assert.ok(bounds.tower.height >= 360, '101 must tower over the city');
    assert.ok(bounds.tower.y <= bounds.skyline.y - 140, '101 must rise clearly above other buildings');
    for (const b of bounds.groups) {
      const d = bounds.date;
      assert.ok(b.x >= d.x+d.width+24 || b.x+b.width+24 <= d.x || b.y >= d.y+d.height+24,
        'Buildings must leave at least 24px beside or below date/year');
    }
    for (const landmark of ['taipei-101', 'north-gate', 'taipei-station']) {
      assert.equal(await page.locator(`#${landmark}`).count(), 1);
    }
    const before = await page.locator('.plane').evaluate(el => getComputedStyle(el).transform);
    await page.waitForTimeout(300);
    const after = await page.locator('.plane').evaluate(el => getComputedStyle(el).transform);
    assert.notEqual(before, after, 'Plane must move');
    await page.screenshot({path: `${scene}.png`});
    await page.emulateMedia({reducedMotion: 'reduce'});
    assert.deepEqual(await page.locator('.cloud,.plane,.beacon').evaluateAll(els =>
      [...new Set(els.map(el => getComputedStyle(el).animationName))]), ['none']);
    await page.emulateMedia({reducedMotion: 'no-preference'});
  }
  await page.goto(pathToFileURL(resolve('index.html')).href);
  for (const colorScheme of ['light', 'dark']) {
    await page.emulateMedia({colorScheme});
    for (const width of [1440, 375]) {
      await page.setViewportSize({width, height: 1000});
      assert.equal(await page.locator('img').evaluateAll(els => els.every(el => el.complete && el.naturalWidth > 0)), true);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      await page.screenshot({path: `preview-${colorScheme}-${width}.png`, fullPage: true});
    }
  }
  console.log('PASS: skyline/date clearance, Taipei landmarks, 3 SVG animations, reduced motion, responsive light/dark preview');
} finally {
  await browser.close();
}
