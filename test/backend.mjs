import ts from 'typescript';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
await mkdir('.sites-runtime/test',{recursive:true});
let engine=ts.transpileModule(await readFile('lib/recommend.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022},fileName:'recommend.ts'}).outputText;
engine=engine.replace(/import model from ['"]\.\/model.json['"];?/,`const model = ${await readFile('lib/model.json','utf8')};`);
await writeFile('.sites-runtime/test/engine.mjs',engine);
const {recommend,validIds}=await import(pathToFileURL(process.cwd()+'/.sites-runtime/test/engine.mjs'));
function request(overrides={}){
  try{
    const x={a:[],b:[],genre:'',exclude:[],duo:false,...overrides};
    const a=validIds(x.a??[]),b=validIds(x.b??[]);
    if(!Array.isArray(x.exclude)||x.exclude.length>100||x.exclude.some(i=>!Number.isInteger(i)))throw Error('Invalid seen-movie list.');
    if(typeof x.genre!=='string'||typeof x.duo!=='boolean')throw Error('Invalid preferences.');
    return {status:200,data:{movies:recommend(a,b,x.genre,x.exclude,x.duo)}};
  }catch(e){
    return {status:400,data:{error:e instanceof Error?e.message:'Invalid request'}};
  }
}
let tests=0;
const base=await request();assert.equal(base.status,200);assert.equal(base.data.movies.length,8);assert.equal(base.data.movies[0].mode,'community');tests++;
const personal=await request({a:[1,260]});assert.equal(personal.data.movies[0].mode,'personal');assert(personal.data.movies.every(m=>![1,260].includes(m.id)));tests++;
const excluded=await request({exclude:[base.data.movies[0].id]});assert(excluded.data.movies.every(m=>m.id!==base.data.movies[0].id));tests++;
const comedy=await request({a:[1],genre:'Comedy'});assert(comedy.data.movies.every(m=>m.genres.includes('Comedy')));tests++;
const both=await request({a:[1],b:[2571],duo:true}),swapped=await request({a:[2571],b:[1],duo:true});assert.equal(both.data.movies[0].mode,'shared');assert.deepEqual(both.data.movies.map(m=>m.id),swapped.data.movies.map(m=>m.id));tests++;
assert.deepEqual((await request({a:[1,260],b:[356]})).data.movies,personal.data.movies);tests++;
assert.equal((await request({a:[999999]})).status,400);tests++;
assert.equal((await request({a:'wrong'})).status,400);tests++;
assert.equal((await request({a:Array(11).fill(1)})).status,400);tests++;
assert.equal((await request({genre:'No such genre'})).status,400);tests++;
assert.equal((await request({exclude:Array(101).fill(1)})).status,400);tests++;
assert.equal((await request({duo:'true'})).status,400);tests++;
console.log(`${tests} backend checks passed: real learned weights, input rejection, filtering, exclusions, solo isolation and shared-score symmetry.`);
