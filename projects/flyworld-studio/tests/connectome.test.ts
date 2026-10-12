import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { existsSync } from 'node:fs';
import { mkdtemp, readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { ConnectomeService, bodyId, connectomePlugin } from '../server/connectome';
import { assetCache, assetKey, hash, BUCKET } from '../server/assets';
import { parseSwc, parseMesh, simplifyReference, minishardEntry, parseSynapses, type AnnotationInfo } from '../server/formats';
import { inMicrometers, skeletonSegments, regionVertices } from '../src/connectome/geometry';
import type { Skeleton, RegionMesh } from '../src/connectome/types';

describe('native format and source guards',()=>{
  it('rejects malformed origins, foreign origins and writes before opening the index',async()=>{
    let handler!: (request:unknown,response:unknown,next:()=>void)=>Promise<void>;
    const plugin=connectomePlugin();
    (plugin.configureServer as (server:unknown)=>void)({middlewares:{use:(fn:typeof handler)=>{handler=fn;}}});
    for(const [method,origin] of [['GET','not a URL'],['GET','https://example.com'],['POST','http://localhost:5173']]){
      let body='';const response={statusCode:200,setHeader:()=>{},end:(text:string)=>{body=text;}};
      await handler({url:'/api/connectome/status',method,headers:{origin,host:'localhost:5173'}},response,()=>{throw new Error('Unexpected fallthrough');});
      expect(response.statusCode).toBe(403);expect(JSON.parse(body).error).toContain('same-origin GET');
    }
  });
  it.each(['-1','0','1.2','../71254','1 OR 1=1','4294967296'])('rejects invalid source identity %s',id=>expect(()=>bodyId(id)).toThrow());
  it('preserves source SWC points without repairing missing parents or cycles',()=>{
    expect(parseSwc('# native\n1 0 10 20 30 2 -1\n2 3 11 25 32 1 1').points[1]).toEqual([2,3,11,25,32,1,1]);
    for(const text of ['1 0 NaN 1 2 0 -1','1 0 1 2 3 0 2','1 0 1 2 3 0 2\n2 0 1 2 3 0 1','1 0 1 2 3 0 -1\n1 0 4 5 6 0 -1'])expect(()=>parseSwc(text)).toThrow();
    expect(()=>parseSwc('1 0 1 2 3 0 -1\n2 0 4 5 6 0 1',1)).toThrow(/budget/);
  });
  it('preserves separation between neurons and aligns nm surfaces with 8-nm data',()=>{
    const a={points:[[1,0,100,200,300,1,-1],[2,0,110,210,310,1,1]],units:'8 nm'} as Skeleton;
    const b={...a,points:a.points.map(p=>p.map((v,i)=>i===2?v+1000:v))};
    expect(skeletonSegments(b)[0]-skeletonSegments(a)[0]).toBeCloseTo(8,5);
    expect(inMicrometers([100,200,300],'8 nm')).toEqual(inMicrometers([800,1600,2400],'nm'));
    expect(Array.from(regionVertices({vertices:[800,1600,2400],units:'nm'} as RegionMesh))[0]).toBeCloseTo(0.8);
  });
  it('validates triangle indices and labels a separate surface-only simplification',()=>{
    const bytes=Buffer.alloc(4+36+12);bytes.writeUInt32LE(3,0);
    [0,0,0,3000,0,0,0,3000,0].forEach((v,i)=>bytes.writeFloatLE(v,4+i*4));
    [0,1,2].forEach((v,i)=>bytes.writeUInt32LE(v,40+i*4));
    const original=parseMesh(bytes),copy=structuredClone(original);
    expect(simplifyReference(original,2000).indices).toEqual([0,1,2]);expect(original).toEqual(copy);
    bytes.writeUInt32LE(9,40);expect(()=>parseMesh(bytes)).toThrow();
  });
  it('decodes delta offsets relative to the prior chunk end',()=>{
    const index=Buffer.alloc(48);[10n,5n,100n,20n,30n,40n].forEach((n,i)=>index.writeBigUInt64LE(n,i*8));
    expect(minishardEntry(index,10n,64)).toEqual([164,194]);
    expect(minishardEntry(index,15n,64)).toEqual([214,254]);expect(minishardEntry(index,99n,64)).toBeNull();
    expect(()=>minishardEntry(Buffer.alloc(3),1n,64)).toThrow();
  });
  it('rejects damaged or mismatched cached bytes without a network fallback',async()=>{
    const path=await mkdtemp(join(tmpdir(),'flyworld-cache-'));
    try{
      const url=BUCKET+'v1.0/test',folder=join(path,assetKey(url));await mkdir(folder);
      await writeFile(join(folder,'receipt.json'),JSON.stringify({url,bytes:3,sha256:hash('abc')}));
      await writeFile(join(folder,'raw.bin'),'bad');await expect(assetCache(path)(url)).rejects.toThrow(/integrity/);
      await expect(assetCache(path)('https://example.com/private')).rejects.toThrow(/Unsupported/);
    }finally{await rm(path,{recursive:true,force:true});}
  });
});

describe.skipIf(!existsSync('data/connectome/index.sqlite'))('pinned real catalogue and recovered official anatomy',()=>{
  let service:ConnectomeService;
  beforeAll(()=>{service=new ConnectomeService('data/connectome/index.sqlite','data/connectome/cache');});
  afterAll(()=>service?.db.close());
  it('indexes the exact Traced population and keeps whole-source exclusions explicit',()=>{
    expect(service.manifest.neuronCount).toBe(165122);expect(service.manifest.annotationRows).toBe(211577);
    expect(service.manifest.edgeCount).toBe(25563197);expect(service.manifest.synapseConfidence).toBe(0.5);
    expect(service.search('LB3b').total).toBe(11);expect(service.search('LB3c').total).toBe(23);
    expect(service.search('71254').neurons[0].bodyId).toBe('71254');
    expect(service.search('Quasimodo').neurons.every(n=>n.type==='GNG042')).toBe(true);
    expect(service.search("%' OR 1=1 --").total).toBe(0);
  });
  it('respects graph direction, filtering, expansion and identity budgets',()=>{
    const edge=service.partners('71254','downstream').partners[0].edge;
    expect(edge).toEqual({source:'71254',target:'21763',weight:86});
    expect(service.partners('21763','upstream').partners.some(p=>p.neuron.bodyId==='71254')).toBe(true);
    expect(service.graph(['71254','21763']).edges).toContainEqual(edge);
    expect(service.graph(['71254','21763'],87).edges).not.toContainEqual(edge);
    expect(()=>service.graph(Array.from({length:25},(_,i)=>String(i+1)))).toThrow(/24/);
    expect(()=>service.graph(['71254','71254'])).toThrow();expect(()=>service.neuron('999999999')).toThrow();
  });
  it.each(['71254','72059','15321','28181','18295'])('retrieves exact source cables and synapse counts for %s',async id=>{
    const skeleton=await service.skeleton(id);expect(skeleton.points.length).toBeGreaterThan(300);
    expect(skeleton.source.url).toContain('/skeletons-malecns/skeletons-swc/'+id+'.swc');
    expect(skeleton.orientationStatus).toBe('UNVERIFIED');
    const partner=service.partners(id,'downstream').partners[0];const sites=await service.synapses(id,partner.neuron.bodyId);
    expect(sites.total).toBe(partner.edge.weight);expect(sites.shown).toBe(sites.total);
    expect(new Set(sites.synapses.map(s=>s.id)).size).toBe(sites.total);
    expect(sites.synapses.every(s=>s.source===id&&s.target===partner.neuron.bodyId&&s.confidencePre>=0.5&&s.confidencePost>=0.5)).toBe(true);
    expect(sites.sources.slice(1).every(s=>s.etag===sites.sources[1].etag)).toBe(true);
    const higher=await service.synapses(id,partner.neuron.bodyId,0.95);expect(higher.total).toBeLessThanOrEqual(sites.total);
  });
  it('rejects corrupted synapse lists and coordinate frame substitutions',async()=>{
    const metadata=await service.get(BUCKET+'v1.0/male-cns-v1.0-synapses-precomputed/info');
    const info:AnnotationInfo=JSON.parse(metadata.data.toString());
    expect(()=>parseSynapses(Buffer.alloc(7),info,'1','2',0.5)).toThrow();
    info.dimensions.x[0]=1e-9;expect(()=>parseSynapses(Buffer.alloc(8),info,'1','2',0.5)).toThrow(/coordinate/);
  });
  it('validates all four official reference surfaces in the same native frame',async()=>{
    const regions=await service.regions();expect(regions.map(r=>r.id)).toEqual(['brain:1','brain:2','brain:3','vnc:1']);
    for(const r of regions){const mesh=await service.region(r.id);expect(mesh.vertices.length).toBeGreaterThan(0);expect(mesh.units).toBe('nm');expect(mesh.simplification.gridNm).toBe(2000);expect(mesh.simplification.sourceVertices).toBeGreaterThan(mesh.vertices.length/3);}
  },30000);
  it('keeps the saved scientific packages byte-identical',async()=>{
    const baseline=JSON.parse(await readFile('data/anatomy/manifests/source-baseline.json','utf8')) as Record<string,string>;
    for(const [path,digest] of Object.entries(baseline).filter(([p])=>p.includes('/flyworld/public/')))expect(hash(await readFile(path))).toBe(digest);
  });
});
