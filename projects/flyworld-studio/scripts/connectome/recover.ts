/** Offline orchestration: plan bounded curl downloads, then validate/cache their bytes. */
import { mkdir, readFile, writeFile, stat } from 'node:fs/promises';
import { join } from 'node:path';
import { ConnectomeService } from '../../server/connectome.ts';
import { assetCache, assetKey, hash, BUCKET, type GetAsset } from '../../server/assets.ts';
import type { Receipt } from '../../src/connectome/types.ts';

const base=join(process.cwd(),'data/connectome'), recovery=join(base,'recovery'), cache=join(base,'cache');
await mkdir(recovery,{recursive:true});
const queuePath=join(recovery,'requests.json');
type Request={url:string;maxBytes:number;range?:[number,number]};
if(process.argv[2]==='import') {
  const requests:Request[]=JSON.parse(await readFile(queuePath,'utf8'));
  for(const r of requests) {
    const key=assetKey(r.url,r.range), folder=join(cache,key);
    const data=await readFile(join(recovery,key+'.download'));
    const headers=await readFile(join(recovery,key+'.headers'),'utf8');
    const blocks=headers.trim().split(/\r?\n\r?\n/), last=blocks.at(-1)!;
    const status=Number(last.match(/^HTTP\/\S+ (\d+)/)?.[1]);
    if(status!==(r.range?206:200) || data.length>r.maxBytes || (r.range && data.length!==r.range[1]-r.range[0])) throw new Error('Failed/oversized source response: '+r.url);
    if(r.range && !last.toLowerCase().includes(`content-range: bytes ${r.range[0]}-${r.range[1]-1}/`)) throw new Error('Range mismatch');
    const receipt:Receipt={url:r.url,bytes:data.length,sha256:hash(data),retrievedAt:new Date().toISOString(),...(r.range?{range:r.range}:{}),etag:last.match(/etag: (.+)/i)?.[1].trim(),generation:last.match(/x-goog-generation: (.+)/i)?.[1].trim()};
    await mkdir(folder,{recursive:true});
    try {
      const old=await readFile(join(folder,'raw.bin')); if(!old.equals(data)) throw new Error('Refusing to overwrite a different cached source');
    } catch(e) { if((e as NodeJS.ErrnoException).code!=='ENOENT') throw e; await writeFile(join(folder,'raw.bin'),data,{flag:'wx'}); }
    try { await stat(join(folder,'receipt.json')); } catch { await writeFile(join(folder,'receipt.json'),JSON.stringify(receipt,null,2)+'\n',{flag:'wx'}); }
  }
  console.log(`Imported ${requests.length} checked source responses`);
} else {
  const missing=new Map<string,Request>();
  const cached=assetCache(cache);
  const get:GetAsset=async(url,maxBytes=16*1024*1024,range)=>{
    try { await stat(join(cache,assetKey(url,range),'receipt.json')); } catch {
      missing.set(assetKey(url,range),{url,maxBytes,...(range?{range}:{})}); throw new Error('QUEUED');
    }
    return cached(url,maxBytes,range);
  };
  const service=new ConnectomeService(join(base,'index.sqlite'),cache,get);
  const reports:Record<string,unknown>={};
  const record=async(name:string,run:()=>Promise<unknown>)=>{try{reports[name]=await run();}catch(e){reports[name]={error:e instanceof Error?e.message:String(e)};}};
  const expected:Record<string,string>={'71254':'LB3b','72059':'LB3c','15321':'GNG042','28181':'GNG015','18295':'MN4a'};
  for(const [id,type] of Object.entries(expected)) {
    if(service.neuron(id).type!==type) throw new Error('Recovery body/type mismatch');
    await record('body:'+id,async()=>{const s=await service.skeleton(id);return {bodyId:id,type,points:s.points.length,source:s.source,headers:s.headers,units:s.units};});
  }
  await record('scene',async()=>(await get(BUCKET+'v1.0/male-cns-v1.0.json',2*1024*1024)).receipt);
  await record('segmentation',async()=>(await get(BUCKET+'v1.0/segmentation/info',2*1024*1024)).receipt);
  await record('regions',()=>service.regions());
  if(Array.isArray(reports.regions)) for(const r of reports.regions) await record('region:'+r.id,async()=>{const mesh=await service.region(r.id);return {id:r.id,label:r.label,vertices:mesh.vertices.length/3,triangles:mesh.indices.length/3,sources:mesh.sources};});
  // Validate real synapse pairs along the strongest recorded outgoing edge of each test body.
  for(const id of Object.keys(expected)) {
    const partner=service.partners(id,'downstream').partners[0];
    if(partner) await record('synapses:'+id,async()=>{const result=await service.synapses(id,partner.neuron.bodyId);return {...result, synapses:result.synapses.slice(0,2),indexedWeight:partner.edge.weight};});
  }
  service.db.close();
  const requests=[...missing.values()];
  await writeFile(queuePath,JSON.stringify(requests,null,2)+'\n');
  const config=requests.map(r=>{
    const key=assetKey(r.url,r.range);
    return ['fail','silent','show-error','max-time = 25',`url = ${JSON.stringify(r.url)}`,`output = ${JSON.stringify(join(recovery,key+'.download'))}`,`dump-header = ${JSON.stringify(join(recovery,key+'.headers'))}`,`max-filesize = ${r.maxBytes}`,...(r.range?[`range = "${r.range[0]}-${r.range[1]-1}"`]:[]),'next'].join('\n');
  }).join('\n').replace(/\nnext$/,'');
  await writeFile(join(recovery,'requests.curl'),config+'\n');
  await writeFile(join(recovery,'recovery-report.json'),JSON.stringify(reports,null,2)+'\n');
  console.log(JSON.stringify({queued:requests.length,checks:Object.fromEntries(Object.entries(reports).map(([k,v])=>[k,(v as {error?:string}).error??'PASS']))},null,2));
}
