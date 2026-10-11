import {chromium} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {mkdir,writeFile} from 'node:fs/promises';
const url=process.env.SITE_URL||'http://127.0.0.1:4173';
const output=process.env.REVIEW_OUTPUT||'../local/ui-review';
await mkdir(output,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined});
const results=[];
const errors=[];
for(const [name,size,theme] of [['desktop',{width:1440,height:1000},'light'],['mobile',{width:390,height:844},'light'],['dark',{width:1440,height:1000},'dark']]){
 const context=await browser.newContext({viewport:size,colorScheme:theme,reducedMotion:'reduce'});
 const page=await context.newPage();
 page.on('pageerror',e=>errors.push(String(e)));
 const failed=[];page.on('response',r=>{if(r.status()>=400)failed.push({url:r.url(),status:r.status()});});
 await page.goto(url);await page.locator('#headline').waitFor();await page.locator('#explorer-status').filter({hasText:'daily intervals'}).waitFor();
 await page.screenshot({path:`${output}/${name}-overview.png`});
 await page.locator('#explore').scrollIntoViewIfNeeded();await page.screenshot({path:`${output}/${name}-explorer.png`});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
 const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 if(name==='desktop'){
  await page.locator('#target').selectOption('rs');await page.locator('#aggregation').selectOption('budget');
  await page.locator('#explorer-status').filter({hasText:'daily intervals'}).waitFor();
  await page.locator('#split').selectOption('train');await page.locator('#explorer-status').filter({hasText:'Training fit'}).waitFor();
  await page.locator('#task').selectOption('direct');await page.locator('#explorer-status').filter({hasText:'No predictions'}).waitFor();
  await page.locator('#target').selectOption('nee');await page.locator('#explorer-status').filter({hasText:'daily intervals'}).waitFor();
  const [download]=await Promise.all([page.waitForEvent('download'),page.locator('#download').click()]);
  await download.saveAs(`${output}/selected-download.csv`);
  await page.locator('#bench-family').selectOption('spatial-');await page.locator('#bench-split').selectOption('validation');
  if(await page.locator('#bench-table tbody tr').count()!==6)throw new Error('Spatial fold table should have six held cells for one seed.');
  await page.keyboard.press('Tab');
  const state=page.url();const reload=await browser.newPage();await reload.goto(state);await reload.locator('#headline').waitFor();
  if(await reload.locator('#task').inputValue()!=='direct')throw new Error('Query state lost');await reload.close();
  // Check every same-site resource link and historical reading edition.
  const links=await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.href).filter(h=>h.startsWith(location.origin)&&!h.includes('#')));
  for(const link of new Set(links)){const response=await page.request.get(link);if(!response.ok())throw new Error(`Broken local link ${link}: ${response.status()}`);}
  const thesis=await browser.newPage();await thesis.goto(url+'/thesis/index.html');await thesis.locator('h1').waitFor();
  const chapters=await thesis.locator('nav a').allTextContents();
  if(!chapters.some(t=>t==='7. Conclusion')||chapters.length<11)throw new Error('Historical chapter navigation incomplete');
  for(const src of await thesis.locator('img').evaluateAll(images=>images.map(i=>i.src))){const r=await thesis.request.get(src);if(!r.ok())throw new Error('Missing dissertation figure '+src);}
  const broken=await thesis.locator('img').evaluateAll(images=>images.filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.src));
  if(broken.length)throw new Error('Broken dissertation images: '+broken.join(','));await thesis.close();
  // Browser zoom halves the effective CSS viewport. CSS `zoom` does not update
  // media queries, so test the 200% equivalent layout at 720x500 CSS pixels.
  await page.setViewportSize({width:720,height:500});await page.screenshot({path:`${output}/desktop-zoom200.png`});
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw new Error('Overflow at 200% zoom');
 }
 results.push({name,overflow,failed,violations:axe.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(n=>n.target)}))});
 await context.close();
}
// Missing-asset error state must remain actionable.
const error=await browser.newPage();await error.route('**/research.json',r=>r.fulfill({status:404,body:'missing'}));await error.goto(url);await error.locator('[role=alert]').waitFor();await error.close();
await browser.close();
await writeFile(`${output}/checks.json`,JSON.stringify({results,errors},null,2));
console.log(JSON.stringify({results,errors},null,2));
if(errors.length||results.some(r=>r.overflow||r.failed.length||r.violations.length))process.exitCode=1;
