// Validate approved exports without requiring private training checkpoints.
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const root=new URL('../public/',import.meta.url);
const data=JSON.parse(await readFile(new URL('research.json',root),'utf8'));
const fields=data.columns;
let rowsChecked=0;
for(const asset of data.assets){
 const bytes=await readFile(new URL(asset.path,root));
 assert.equal(createHash('sha256').update(bytes).digest('hex'),asset.sha256);
 const full=JSON.parse(bytes);
 assert.equal(full.length,asset.rows);
 assert.equal(new Set(full.map(r=>r[0])).size,full.length);
 const rebuilt=new Map();
 for(const [identity,path] of Object.entries(asset.partitions)){
  const [cell,split]=identity.split('|');
  for(const row of JSON.parse(await readFile(new URL(path,root),'utf8'))){
   assert.equal(row[fields.indexOf('cell')],cell);
   assert.equal(row[fields.indexOf('split')],split);
   assert(!rebuilt.has(row[0]));rebuilt.set(row[0],row);
  }
 }
 assert.equal(rebuilt.size,full.length);
 for(const row of full){assert.deepEqual(row,rebuilt.get(row[0]));rowsChecked++;}
 const test=full.filter(r=>r[fields.indexOf('split')]==='test');
 if(asset.run_id.startsWith('weather-')){
  const residual=test.map(r=>r[fields.indexOf('nee_pred')]-r[fields.indexOf('nee_true')]);
  const rmse=Math.sqrt(residual.reduce((s,e)=>s+e*e,0)/residual.length);
  const expected=data.metrics.find(r=>r.run_id===asset.run_id&&r.target==='nee'&&r.split==='test');
  assert(Math.abs(rmse-expected.rmse)<2e-6);
 }
 for(const row of full){
  const value=f=>row[fields.indexOf(f)];
  // Float32 component arithmetic and six-decimal export have bounded rounding.
  if(value('gpp_pred')!==null)assert(Math.abs(value('nee_pred')-(value('rp_pred')+value('rs_pred')-value('gpp_pred')))<=2e-6+1e-7*Math.abs(value('nee_pred')));
  if(value('nee_lo95')!==null)assert(value('nee_lo95')<=value('nee_hi95'));
 }
}
console.log(`Verified ${data.assets.length} authentic exports and ${rowsChecked} keyed rows; partitions, hashes, accounting and test metrics agree.`);
