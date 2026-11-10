// Cover crop simulation only; does not open or operate Notion.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE);
const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH,headless:true});
try {
  const page = await browser.newPage({viewport:{width:3600,height:600}});
  for (const scene of ['dawn','day','dusk','night']) {
  const source = execFileSync('python3',['-B','-c',`from city import render; print(render(scene='${scene}', cover=True))`]);
  await writeFile(`cover-${scene}.svg`,source);
  await page.setViewportSize({width:3600,height:600});
  await page.goto(pathToFileURL(resolve(`cover-${scene}.svg`)).href);
  const bounds = await page.locator('#heading-text,#year,#taipei-101,#sun,#moon').evaluateAll(els =>
    els.map(el => {const b=el.getBoundingClientRect();return {id:el.id,x:b.x,y:b.y,width:b.width,height:b.height};}));
  const data = `data:image/svg+xml;base64,${(await readFile(`cover-${scene}.svg`)).toString('base64')}`;
  await page.goto('about:blank');
  for (const [width,height] of [[2048,340],[1400,280],[375,180]]) {
    const scale = Math.max(width/3600,height/600);
    const dx = (width-3600*scale)/2, dy = (height-600*scale)/2;
    for (const b of bounds) {
      assert.ok(b.x*scale+dx >= 8 && (b.x+b.width)*scale+dx <= width-8, `${b.id} cropped horizontally`);
      assert.ok(b.y*scale+dy >= 12, `${b.id} cropped at top`);
      if (b.id !== 'taipei-101') assert.ok((b.y+b.height)*scale+dy <= height-12, `${b.id} cropped at bottom`);
    }
    await page.setViewportSize({width,height});
    await page.setContent(`<style>html,body{margin:0;width:100%;height:100%;overflow:hidden}img{width:100%;height:100%;object-fit:cover}</style><img src="${data}" alt="cover">`);
    await page.locator('img').evaluate(el => el.decode());
    await page.screenshot({path:`cover-${scene}-${width}.png`});
  }
  }
  console.log('PASS: four 6:1 covers, full sun/moon, heading/year and 101 top at desktop and phone cover crops');
} finally {await browser.close();}
