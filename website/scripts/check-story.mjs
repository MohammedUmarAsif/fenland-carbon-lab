import {chromium} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const url=process.env.SITE_URL||'http://127.0.0.1:4174/';
const output=fileURLToPath(new URL('../../local/story-review/',import.meta.url));await mkdir(output,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined});
const results=[];
const chapters=['problem','question','data','carbon','learning','models','insights','reliability','dissertation','future'];
for(const [name,viewport,theme,motion]of [
 ['desktop',{width:1440,height:1000},'light','no-preference'],
 ['mobile',{width:390,height:844},'light','no-preference'],
 ['dark',{width:1440,height:1000},'dark','no-preference'],
 ['reduced-motion',{width:390,height:844},'light','reduce'],
 ['zoom',{width:720,height:500},'light','reduce']
]){
 const context=await browser.newContext({viewport,colorScheme:theme,reducedMotion:motion});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(url);await page.locator('.chapter').last().waitFor();
 assert.equal(new URL(page.url()).search,'','Clean root URL must stay clean');
 assert.equal(await page.locator('.chapter').count(),10);
 assert.equal(await page.locator('.chapter-nav a').count(),10);
 await page.screenshot({path:`${output}/${name}-hero.png`});
 for(const id of chapters){
  await page.locator(`#${id}`).scrollIntoViewIfNeeded();
  const intro=await page.locator(`#${id} .chapter-intro`).innerText();
  const words=intro.split(/\s+/).length;assert(words>=40&&words<=80,`${id} explanation has ${words} words`);
  await page.locator(`#${id} > details`).evaluate(el=>el.open=true);
  for(const c of await page.locator(`#${id} .chart`).all()){
   await c.scrollIntoViewIfNeeded();await c.locator('canvas').waitFor();
   const size=await c.locator('canvas').first().boundingBox();assert(size.width>100&&size.height>200,id);
   await c.locator('..').screenshot({path:`${output}/${name}-${await c.getAttribute('id')}.png`});
  }
  await page.locator(`#${id}`).evaluate(el=>window.scrollTo(0,el.getBoundingClientRect().top+window.scrollY-90));
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false,id+' overflow');
  const axe=await new AxeBuilder({page}).include(`#${id}`).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  assert.equal(axe.violations.length,0,JSON.stringify({name,id,violations:axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))}));
  await page.screenshot({path:`${output}/${name}-${id}.png`});
  await page.locator(`#${id} > details`).evaluate(el=>el.open=false);
 }
 await page.locator('#data').scrollIntoViewIfNeeded();
 await page.locator('.map-figure details').evaluate(el=>el.open=true);
 await page.locator('.full-map').scrollIntoViewIfNeeded();
 await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
 assert(await page.locator('img').evaluateAll(imgs=>imgs.every(i=>i.hasAttribute('width')&&i.hasAttribute('height')&&i.alt.length>10)));
 const data=await (await page.request.get(new URL('research.json',url).href)).json();
 const selected=data.metrics.find(r=>r.run_id===data.selected.run_id&&r.target==='nee'&&r.split==='test');
 assert((await page.locator('#headline').innerText()).includes(selected.rmse.toFixed(3)));
 assert((await page.locator('#reliability').innerText()).includes(String(data.story.support.rows.find(r=>r.run_id===data.selected.run_id&&r.split==='test'&&r.group==='unusual').n)));
 for(const href of await page.locator('a[href^="#"]').evaluateAll(as=>as.map(a=>a.getAttribute('href'))))assert(await page.locator(href).count(),href);
 await page.goto(new URL('?public-family=direct-&public-target=nee&public-split=test&public-seed=17#benchmarks',url).href);
 await page.locator('#public-table tbody tr').first().waitFor();assert.equal(await page.locator('#public-table tbody tr').count(),3);
 for(const anchor of ['methods','dissertation','reproduce']){await page.goto(new URL('#'+anchor,url).href);await page.locator('#'+anchor).waitFor();}
 await page.goto(url);await page.keyboard.press('Tab');assert.equal(await page.locator('.skip').evaluate(el=>el===document.activeElement),true);
 await page.keyboard.press('Enter');assert.equal(new URL(page.url()).hash,'#main');
 assert.equal(errors.length,0,JSON.stringify(errors));
 results.push({name,chapters:10,charts:10,axe_violations:0,overflow:false,clean_url:true,legacy_links:true,keyboard:true,errors});
 await context.close();
}
await browser.close();await writeFile(`${output}/checks.json`,JSON.stringify(results,null,2));console.log(JSON.stringify(results,null,2));
