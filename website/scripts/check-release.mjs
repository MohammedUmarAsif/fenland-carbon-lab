import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const approval=JSON.parse(await readFile(new URL('../../config/public-release.json',import.meta.url),'utf8'));
assert.equal(approval.approved,true,'Scoped public release not approved');
assert.equal(approval.profile,'aggregate');
assert.equal(approval.aggregate_findings_publication_allowed,true,'Author aggregate-results approval missing');
assert(approval.approval_reference&&approval.access_agreement_publication_check);
const root=new URL('../aggregate-public/',import.meta.url);
const media=new Set(['fen-landscape.jpg','fen-soil.jpg','england-peat-map.png']);
const allowed=new Set(['research.json','metrics.csv','coverage.csv','diagnostics.csv','paired_comparisons.json','robots.txt','RESEARCH_REPORT.md','PROTOCOL.md','CORRECTIONS.md','DATA_CARD.md','MODEL_CARD.md','OBSERVATIONAL_FEASIBILITY.md','INTERVIEW.md','CLAIM_LEDGER.csv','EXPERIMENT_LINEAGE.csv','BIBLIOGRAPHY.json','EXPERIMENT_STATUS.json','VALIDATION.md','PUBLICATION.md','SUPPLEMENTARY_PROTOCOL.md','REVISED_DISSERTATION_AUDIT.json','REVISED_DISSERTATION_AUDIT.md','PUBLICATION_PATHWAY.md','ASSET_REGISTER.json',...media]);
const manifest=JSON.parse(await readFile(new URL('PACKAGE_MANIFEST.json',root),'utf8'));
assert.equal(manifest.profile,'aggregate');
assert.equal(manifest.public_release_approved,true,'Package remains an unapproved candidate');
const files=await readdir(root,{withFileTypes:true});
assert(files.every(f=>f.isFile()),'Folders/series/thesis media prohibited in aggregate package');
assert.deepEqual(files.map(f=>f.name).sort(),[...Object.keys(manifest.files),'PACKAGE_MANIFEST.json'].sort());
for(const [name,hash]of Object.entries(manifest.files)){
 assert(allowed.has(name),'Non-allowlisted summary or asset: '+name);
 assert(!name.includes('/')&&!name.includes('\\'));
 assert(!/\.(nc|pkl|joblib|pt|pdf|docx|zip)$/i.test(name));
 if(/\.(png|jpe?g|webp|svg)$/i.test(name))assert(media.has(name),'Unreviewed media asset');
 const bytes=await readFile(new URL(name,root));
 if(name.endsWith('.jpg'))assert.equal(bytes.subarray(0,3).toString('hex'),'ffd8ff');
 if(name.endsWith('.png'))assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
 assert.equal(createHash('sha256').update(bytes).digest('hex'),hash);
}
assert.deepEqual(Object.keys(manifest.files).sort(),[...allowed].sort());
const data=JSON.parse(await readFile(new URL('research.json',root),'utf8'));
assert.equal(data.publication_mode,'aggregate');
for(const key of ['assets','columns','mapping','runs','dissertation','historical'])assert(!(key in data));
assert.equal(data.schema_version,2);
assert.equal(data.story.version,2);
const register=JSON.parse(await readFile(new URL('ASSET_REGISTER.json',root),'utf8'));
assert.deepEqual(register.map(a=>a.file).sort(),[...media].sort());
for(const a of register){
 assert(a.creator&&a.source.startsWith('https://')&&a.licence&&a.licence_url.startsWith('https://')&&a.alt&&a.changes);
 assert.equal(a.sha256,manifest.files[a.file]);
}
const privateKeys=new Set(['feature_mean','feature_scale','target_mean','target_scale','threshold','distance','flagged','nee_true','nee_pred','key','start','end']);
function safe(value){if(Array.isArray(value))value.forEach(safe);else if(value&&typeof value==='object')for(const [k,v]of Object.entries(value)){assert(!privateKeys.has(k),'Private field: '+k);safe(v);}}
safe(data.story);
for(const r of data.story.support.rows)if(r.n<30)for(const k of ['rmse','mae','bias','coverage95','mean_width95'])assert.equal(r[k],null);
console.log('Scoped aggregate release approval and exact package verified');
