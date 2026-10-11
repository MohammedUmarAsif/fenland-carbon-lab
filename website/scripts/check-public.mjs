import {chromium} from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const url=process.env.SITE_URL||'http://127.0.0.1:4174';
const output=fileURLToPath(new URL('../../local/public-review/',import.meta.url));await mkdir(output,{recursive:true});
const root=new URL('../aggregate-public/',import.meta.url);
const manifest=JSON.parse(await readFile(new URL('PACKAGE_MANIFEST.json',root),'utf8'));
assert.equal(manifest.profile,'aggregate');
for(const [file,hash]of Object.entries(manifest.files)){assert(!file.includes('/'));assert.equal(createHash('sha256').update(await readFile(new URL(file,root))).digest('hex'),hash);}
const data=JSON.parse(await readFile(new URL('research.json',root),'utf8'));
for(const key of ['assets','columns','mapping','runs','dissertation','historical'])assert(!(key in data));
for(const file of ['metrics.csv','coverage.csv','diagnostics.csv']){const fields=(await readFile(new URL(file,root),'utf8')).split(/\r?\n/)[0].split(',');assert(!fields.some(f=>f.endsWith('_true')||f.endsWith('_pred')||['key','start','end','tair','sw','pr','wind'].includes(f)));}
const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE||undefined});
const results=[];
for(const [name,size,theme]of [['desktop',{width:1440,height:1000},'light'],['mobile',{width:390,height:844},'light'],['dark',{width:1440,height:1000},'dark']]){
 const context=await browser.newContext({viewport:size,colorScheme:theme});const page=await context.newPage();const errors=[],failed=[];
 page.on('pageerror',e=>errors.push(String(e)));page.on('response',r=>{if(r.status()>=400)failed.push(r.url());});
 await page.goto(url);await page.locator('#headline').waitFor();
 await page.screenshot({path:`${output}/${name}-overview.png`});
 await page.locator('#benchmarks h2').scrollIntoViewIfNeeded();await page.screenshot({path:`${output}/${name}-results.png`});
 const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
 assert.equal(axe.violations.length,0,JSON.stringify(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
 await page.locator('#public-family').selectOption('direct-');await page.locator('#public-target').selectOption('gpp');await page.locator('#public-table').filter({hasText:'No aggregate metrics'}).waitFor();
 await page.locator('#public-target').selectOption('nee');assert.equal(await page.locator('#public-table tbody tr').count(),3);
 await page.reload();await page.locator('#headline').waitFor();assert.equal(await page.locator('#public-family').inputValue(),'direct-');
 for(const link of new Set(await page.locator('a[href]').evaluateAll(as=>as.map(a=>a.href).filter(h=>h.startsWith(location.origin)&&!h.includes('#'))))){const r=await page.request.get(link);assert(r.ok(),link);}
 const [download]=await Promise.all([page.waitForEvent('download'),page.locator('a[download]').click()]);await download.saveAs(`${output}/${name}-metrics.csv`);
 if(name==='desktop'){await page.setViewportSize({width:720,height:500});await page.waitForFunction(()=>document.documentElement.scrollWidth<=innerWidth+1,{},{timeout:5000});await page.screenshot({path:`${output}/zoom-equivalent.png`});}
 assert.equal(errors.length,0);assert.equal(failed.length,0);
 results.push({name,axe_violations:0,overflow:false,errors,failed});await context.close();
}
await browser.close();await writeFile(`${output}/checks.json`,JSON.stringify({profile:'aggregate',results,manifest_files:Object.keys(manifest.files).length},null,2));console.log(JSON.stringify(results,null,2));
