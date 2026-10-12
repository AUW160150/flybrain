import { DatabaseSync } from 'node:sqlite';
import { join } from 'node:path';
import type { IncomingMessage, ServerResponse } from 'node:http';
import type { Plugin } from 'vite';
import { assetCache, BUCKET, type GetAsset } from './assets.ts';
import { parseSwc, parseMesh, simplifyReference, decodeGzip, minishardEntry, parseSynapses, type AnnotationInfo } from './formats.ts';
import { murmurHash3_x86_128Hash64Bits_Bigint } from './murmur.ts';
import { DATASET, DATASET_UUID, MAX_BODIES, type Neuron, type Edge, type IndexManifest, type Skeleton, type Region, type RegionMesh, type SynapseResult } from '../src/connectome/types.ts';

export const SWC_BASE = BUCKET+'v1.0/segmentation/skeletons-malecns/skeletons-swc/';
export const SYN_BASE = BUCKET+'v1.0/male-cns-v1.0-synapses-precomputed/';
export const REGIONS = [
  { group:'brain', path:'rois/fullbrain-major-shells' },
  { group:'vnc', path:'rois/vnc-neuropil-shell-v2' },
] as const;

export function bodyId(value: string) {
  if (!/^[1-9][0-9]{0,9}$/.test(value) || Number(value)>0xffffffff) throw new Error('Invalid MaleCNS body ID');
  return value;
}
function integer(value: string | null, fallback: number, min: number, max: number) {
  const n = value === null ? fallback : Number(value);
  if (!Number.isSafeInteger(n) || n<min || n>max) throw new Error(`Expected an integer from ${min} to ${max}`);
  return n;
}
function encodeNode(row: unknown): Neuron { return JSON.parse((row as {record:string}).record); }
function encodeEdge(row: unknown): Edge { const e = row as {source:number;target:number;weight:number}; return {source:String(e.source),target:String(e.target),weight:e.weight}; }

export class ConnectomeService {
  db: DatabaseSync;
  manifest: IndexManifest;
  get: GetAsset;
  regionCache = new Map<string,Promise<RegionMesh>>();
  constructor(database: string, cache: string, getter?: GetAsset) {
    this.db = new DatabaseSync(database, { readOnly:true });
    this.manifest = JSON.parse((this.db.prepare('SELECT value FROM metadata WHERE key=?').get('manifest') as {value:string}).value);
    if (this.manifest.dataset!==DATASET || this.manifest.uuid!==DATASET_UUID) { this.db.close(); throw new Error('Index dataset identity mismatch'); }
    this.get = getter ?? assetCache(cache);
  }
  neuron(id: string) {
    const row = this.db.prepare('SELECT record FROM neurons WHERE body=?').get(bodyId(id));
    if (!row) throw new Error('Body is not in the pinned Traced-neuron catalogue');
    return encodeNode(row);
  }
  search(query: string, offset = 0) {
    if (query.length>100 || offset<0 || offset>200000 || !Number.isSafeInteger(offset)) throw new Error('Search exceeds limits');
    const q = query.trim().toLowerCase();
    const pattern = '%'+q.replace(/[\\%_]/g,'\\$&')+'%';
    const total = (this.db.prepare("SELECT count(*) AS n FROM neurons WHERE search LIKE ? ESCAPE '\\'").get(pattern) as {n:number}).n;
    const rows = this.db.prepare("SELECT record FROM neurons WHERE search LIKE ? ESCAPE '\\' ORDER BY CASE WHEN lower(type)=? THEN 0 WHEN CAST(body AS TEXT)=? THEN 0 ELSE 1 END,type,body LIMIT 50 OFFSET ?").all(pattern,q,q,offset);
    return { neurons:rows.map(encodeNode),total,offset,limit:50,query:q,scope:this.manifest.scope };
  }
  graph(ids: string[], minWeight = 1) {
    if (!ids.length || ids.length>MAX_BODIES || new Set(ids).size!==ids.length) throw new Error(`Select 1–${MAX_BODIES} distinct bodies`);
    const neurons = ids.map(id=>this.neuron(id));
    const marks = ids.map(()=>'?').join(',');
    const edges = this.db.prepare(`SELECT source,target,weight FROM edges WHERE source IN (${marks}) AND target IN (${marks}) AND weight>=? ORDER BY weight DESC,source,target`).all(...ids,...ids,minWeight).map(encodeEdge);
    const total = (this.db.prepare(`SELECT count(*) AS n FROM edges WHERE source IN (${marks}) AND target IN (${marks})`).get(...ids,...ids) as {n:number}).n;
    return { neurons,edges,total,filteredOut:total-edges.length,minWeight,scope:'Induced connections among selected Traced neurons',scientificLabel:'RAW_STRUCTURAL',dataset:DATASET };
  }
  partners(id: string, direction: string, minWeight = 1, offset = 0) {
    this.neuron(id);
    if (direction!=='upstream' && direction!=='downstream') throw new Error('Invalid direction');
    const fixed = direction==='upstream'?'target':'source', partner = direction==='upstream'?'source':'target';
    const total = (this.db.prepare(`SELECT count(*) AS n FROM edges WHERE ${fixed}=? AND weight>=?`).get(id,minWeight) as {n:number}).n;
    const rows = this.db.prepare(`SELECT n.record,e.source,e.target,e.weight FROM edges e JOIN neurons n ON n.body=e.${partner} WHERE e.${fixed}=? AND e.weight>=? ORDER BY e.weight DESC,n.body LIMIT 50 OFFSET ?`).all(id,minWeight,offset);
    return { partners:rows.map(r=>({neuron:encodeNode(r),edge:encodeEdge(r)})),total,offset,limit:50,direction,minWeight,scope:this.manifest.scope };
  }
  async skeleton(id: string): Promise<Skeleton> {
    this.neuron(id);
    const asset = await this.get(SWC_BASE+id+'.swc');
    return { bodyId:id,...parseSwc(asset.data.toString('utf8')),source:asset.receipt,units:'8 nm',coordinateSpace:'MaleCNS native EM',orientationStatus:'UNVERIFIED' };
  }
  async regions(): Promise<Region[]> {
    const groups = await Promise.all(REGIONS.map(async group=>{
      const asset = await this.get(BUCKET+group.path+'/segment_properties/info',1024*1024);
      const data = JSON.parse(asset.data.toString());
      const labels = data.inline?.properties?.find((p:{type:string})=>p.type==='label')?.values;
      if (data['@type']!=='neuroglancer_segment_properties' || !Array.isArray(labels) || labels.length!==data.inline.ids.length || labels.length>150) throw new Error('Invalid region catalogue');
      return data.inline.ids.map((id:string,i:number)=>({id:group.group+':'+bodyId(id),label:String(labels[i]),group:group.group}));
    }));
    return groups.flat();
  }
  region(id: string): Promise<RegionMesh> {
    if(!this.regionCache.has(id)) {
      const pending=this.loadRegion(id);this.regionCache.set(id,pending);
      void pending.catch(()=>this.regionCache.delete(id));
    }
    return this.regionCache.get(id)!;
  }
  private async loadRegion(id: string): Promise<RegionMesh> {
    const [groupName,segment] = id.split(':');
    const group = REGIONS.find(g=>g.group===groupName); if (!group) throw new Error('Unknown reference group');
    bodyId(segment ?? '');
    if (!(await this.regions()).some(r=>r.id===id)) throw new Error('Unknown reference region');
    const base = BUCKET+group.path+'/mesh/';
    const info = await this.get(base+'info',1024*1024);
    if (JSON.parse(info.data.toString())['@type']!=='neuroglancer_legacy_mesh') throw new Error('Unsupported reference mesh format');
    const manifest = await this.get(base+segment+':0',1024*1024);
    const fragments: string[] = JSON.parse(manifest.data.toString()).fragments;
    if (!Array.isArray(fragments) || !fragments.length || fragments.length>8 || fragments.some(p=>!/^[-a-zA-Z0-9_().]+$/.test(p) || p.includes('..'))) throw new Error('Invalid mesh fragments');
    const vertices:number[]=[],indices:number[]=[],sources=[info.receipt,manifest.receipt];let sourceVertices=0;
    for (const fragment of fragments) {
      const asset = await this.get(base+fragment,64*1024*1024), original = parseMesh(asset.data);
      sourceVertices+=original.vertices.length/3;
      const mesh=simplifyReference(original,2000);
      const offset = vertices.length/3;
      if (offset+mesh.vertices.length/3>300000) throw new Error('Reference mesh exceeds geometry budget');
      for (const v of mesh.vertices) vertices.push(v);
      for (const i of mesh.indices) indices.push(i+offset);
      sources.push(asset.receipt);
    }
    return {id,vertices,indices,sources,units:'nm',simplification:{method:'vertex-clustering',gridNm:2000,sourceVertices}};
  }
  async synapses(source: string, target: string, minConfidence = 0.5): Promise<SynapseResult> {
    this.neuron(source); this.neuron(target);
    if (!Number.isFinite(minConfidence) || minConfidence<0.5 || minConfidence>1) throw new Error('Confidence must be between 0.5 and 1');
    const metadata = await this.get(SYN_BASE+'info',1024*1024), info:AnnotationInfo=JSON.parse(metadata.data.toString());
    const rel = info.relationships.find(r=>r.id==='body_pre');
    if (!rel || rel.key!=='by_rel_body_pre') throw new Error('Unsupported synapse relationship');
    const s = rel.sharding;
    if (s.hash!=='murmurhash3_x86_128' || s.data_encoding!=='gzip' || s.minishard_index_encoding!=='gzip' || s.preshift_bits!==10 || s.shard_bits!==9 || s.minishard_bits!==2) throw new Error('Synapse sharding changed; review metadata before loading');
    const hashed=murmurHash3_x86_128Hash64Bits_Bigint(0,BigInt(source)>>BigInt(s.preshift_bits));
    const mini=Number(hashed&((1n<<BigInt(s.minishard_bits))-1n));
    const shard=Number((hashed>>BigInt(s.minishard_bits))&((1n<<BigInt(s.shard_bits))-1n));
    const url=SYN_BASE+rel.key+'/'+shard.toString(16).padStart(Math.ceil(s.shard_bits/4),'0')+'.shard';
    const indexEnd=2**s.minishard_bits*16;
    const index=await this.get(url,16,[mini*16,mini*16+16]);
    const begin=indexEnd+Number(index.data.readBigUInt64LE(0)),end=indexEnd+Number(index.data.readBigUInt64LE(8));
    const sources=[metadata.receipt,index.receipt];
    const empty = ():SynapseResult=>({source,target,synapses:[],total:0,shown:0,minConfidence,sources,units:'8 nm'});
    if (begin===end) return empty();
    const miniIndex=await this.get(url,4*1024*1024,[begin,end]); sources.push(miniIndex.receipt);
    const range=minishardEntry(decodeGzip(miniIndex.data),BigInt(source),indexEnd);
    if (!range) return empty();
    const content=await this.get(url,16*1024*1024,range); sources.push(content.receipt);
    if(sources.slice(1).some(r=>!r.etag || r.etag!==index.receipt.etag)) throw new Error('Synapse shard changed between ranges; source refresh requires review');
    const synapses=parseSynapses(decodeGzip(content.data),info,source,target,minConfidence).sort((a,b)=>Number(BigInt(a.id)-BigInt(b.id)));
    return {source,target,synapses:synapses.slice(0,5000),total:synapses.length,shown:Math.min(5000,synapses.length),minConfidence,sources,units:'8 nm'};
  }
}

export function connectomePlugin(): Plugin {
  let service:ConnectomeService|undefined;
  const directory=join(process.cwd(),'data/connectome');
  const middleware=async(req:IncomingMessage,res:ServerResponse,next:()=>void)=>{
    const url=new URL(req.url??'/', 'http://localhost');
    if (!url.pathname.startsWith('/api/connectome/')) return next();
    res.setHeader('Content-Type','application/json'); res.setHeader('Cache-Control','no-store');
    const origin=req.headers.origin;
    let sameOrigin=!origin;
    try { if(origin) sameOrigin=new URL(origin).host===req.headers.host; } catch { sameOrigin=false; }
    if (req.method!=='GET' || !sameOrigin) { res.statusCode=403; res.end(JSON.stringify({error:'Local same-origin GET requests only'})); return; }
    try {
      if (!service) service=new ConnectomeService(join(directory,'index.sqlite'),join(directory,'cache'));
      const p=url.searchParams, route=url.pathname.slice('/api/connectome/'.length);
      let result:unknown;
      if(route==='status') result={...service.manifest,maxBodies:MAX_BODIES};
      else if(route==='search') result=service.search(p.get('q')??'',integer(p.get('offset'),0,0,200000));
      else if(route==='graph') result=service.graph((p.get('ids')??'').split(','),integer(p.get('minWeight'),1,1,1000000));
      else if(route==='partners') result=service.partners(p.get('id')??'',p.get('direction')??'',integer(p.get('minWeight'),1,1,1000000),integer(p.get('offset'),0,0,200000));
      else if(route==='skeleton') result=await service.skeleton(p.get('id')??'');
      else if(route==='regions') result=await service.regions();
      else if(route==='region') result=await service.region(p.get('id')??'');
      else if(route==='synapses') result=await service.synapses(p.get('source')??'',p.get('target')??'',Number(p.get('confidence')??0.5));
      else { res.statusCode=404; result={error:'Unknown connectome request'}; }
      res.end(JSON.stringify(result));
    } catch(error) {
      res.statusCode=service?400:503;
      res.end(JSON.stringify({error:service?(error instanceof Error?error.message:'Source unavailable'):'Connectome index unavailable. Run npm run index:connectome; see the setup documentation.'}));
    }
  };
  return {name:'flyworld-local-connectome',configureServer(server){server.middlewares.use(middleware); server.httpServer?.once('close',()=>service?.db.close());},configurePreviewServer(server){server.middlewares.use(middleware); server.httpServer.once('close',()=>service?.db.close());}};
}
