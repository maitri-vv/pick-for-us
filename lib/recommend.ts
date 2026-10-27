import model from './model.json';
export type Movie = typeof model.movies[number];
const catalog=model.movies;const index=new Map(catalog.map((m,i)=>[m.id,i]));
export const genres=Array.from(new Set(catalog.flatMap(m=>m.genres))).filter(g=>g!=='(no genres listed)').sort();
export function searchCatalog(q=''){const query=q.toLowerCase().trim();return catalog.filter(m=>!query||m.title.toLowerCase().includes(query)).sort((a,b)=>b.count-a.count).slice(0,query?30:24);}
export function validIds(x:unknown):number[]{if(!Array.isArray(x)||x.length>10||x.some(i=>!Number.isInteger(i)||!index.has(i)))throw Error('Choose up to 10 valid movies per person.');return [...new Set(x)];}
function affinity(ids:number[]){const scores=new Float64Array(catalog.length);for(const id of ids){for(const [j,w] of model.weights[index.get(id)!])scores[j]+=w;}const max=Math.max(...scores);if(max>0)for(let i=0;i<scores.length;i++)scores[i]/=max;return scores;}
export function recommend(a:number[],b:number[],genre:string,exclude:number[],duo:boolean){
 b=duo?b:[];
 if(genre&& !genres.includes(genre))throw Error('Unknown genre.');
 const sa=affinity(a),sb=affinity(b),blocked=new Set([...a,...b,...exclude]);const seeded=a.length>0||duo&&b.length>0;
 const result=catalog.map((m,i)=>{const quality=(m.quality-2)/3;let fit=0;
 if(duo&&a.length&&b.length)fit=.65*Math.min(sa[i],sb[i])+.35*(sa[i]+sb[i])/2;
 else fit=a.length?sa[i]:duo&&b.length?sb[i]:0;
 const score=seeded?.9*fit+.1*quality:quality;
 const related=(ids:number[])=>ids.map(id=>({id,weight:model.weights[index.get(id)!].find(([j])=>j===i)?.[1]||0})).sort((x,y)=>y.weight-x.weight).filter(x=>x.weight>0).slice(0,2).map(x=>catalog[index.get(x.id)!].title);
 return {...m,score,fitA:sa[i],fitB:sb[i],becauseA:related(a),becauseB:related(b),mode:!seeded?'community':duo&&a.length&&b.length?'shared':'personal'};
 }).filter(m=>!blocked.has(m.id)&&(!genre||m.genres.includes(genre))).sort((a,b)=>b.score-a.score||b.count-a.count);
 return result.slice(0,8).map(({score,...m})=>m);
}
export const catalogSize=catalog.length;
