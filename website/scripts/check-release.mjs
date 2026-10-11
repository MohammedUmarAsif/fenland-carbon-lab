import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const approval=JSON.parse(await readFile(new URL('../../config/public-release.json',import.meta.url),'utf8'));
assert.equal(approval.approved,true,'Scoped public release not approved');
assert.equal(approval.profile,'aggregate');
assert.equal(approval.aggregate_findings_publication_allowed,true,'Original access terms not checked');
assert(approval.approval_reference&&approval.access_agreement_publication_check);
const root=new URL('../aggregate-public/',import.meta.url);
const manifest=JSON.parse(await readFile(new URL('PACKAGE_MANIFEST.json',root),'utf8'));
assert.equal(manifest.profile,'aggregate');
const files=await readdir(root,{withFileTypes:true});
assert(files.every(f=>f.isFile()),'Folders/series/thesis media prohibited in aggregate package');
assert.deepEqual(files.map(f=>f.name).sort(),[...Object.keys(manifest.files),'PACKAGE_MANIFEST.json'].sort());
for(const [name,hash]of Object.entries(manifest.files)){
 assert(!name.includes('/')&&!name.includes('\\'));
 assert(!/\.(nc|pkl|joblib|pt|pdf|docx|png|zip)$/i.test(name));
 assert.equal(createHash('sha256').update(await readFile(new URL(name,root))).digest('hex'),hash);
}
const data=JSON.parse(await readFile(new URL('research.json',root),'utf8'));
assert.equal(data.publication_mode,'aggregate');
for(const key of ['assets','columns','mapping','runs','dissertation','historical'])assert(!(key in data));
console.log('Scoped aggregate release approval and exact package verified');
