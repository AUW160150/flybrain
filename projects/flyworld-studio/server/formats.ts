import { gunzipSync } from 'node:zlib';
import type { Synapse, XYZ } from '../src/connectome/types';

export function parseSwc(text: string, maxPoints = 250000) {
  const points: number[][] = [], headers: string[] = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.trim(); if (!line) continue;
    if (line.startsWith('#')) { headers.push(line); continue; }
    const p = line.split(/\s+/).map(Number);
    if (p.length !== 7 || !p.every(Number.isFinite) || ![p[0],p[1],p[6]].every(Number.isSafeInteger) || p[0] <= 0 || p[1] < 0 || p[5] < 0) throw new Error('Invalid source SWC row');
    points.push(p); if (points.length > maxPoints) throw new Error('Skeleton exceeds geometry budget; no branches were truncated');
  }
  const parents = new Map(points.map(p => [p[0],p[6]]));
  if (!points.length || parents.size !== points.length) throw new Error('Empty or duplicate SWC points');
  const complete = new Set<number>();
  for (const id of parents.keys()) {
    const visit = new Set<number>(); let cursor = id;
    while (cursor !== -1 && !complete.has(cursor)) {
      if (!parents.has(cursor) || visit.has(cursor)) throw new Error('Missing or cyclic SWC parent; no repair was attempted');
      visit.add(cursor); cursor = parents.get(cursor)!;
    }
    visit.forEach(p => complete.add(p));
  }
  return { points, headers };
}

export function parseMesh(data: Buffer) {
  if (data.length < 4) throw new Error('Empty mesh');
  const count = data.readUInt32LE(0), end = 4+count*12;
  if (!count || count > 2000000 || end > data.length || (data.length-end)%12) throw new Error('Invalid mesh dimensions');
  const vertices = Array.from({ length: count*3 }, (_,i) => data.readFloatLE(4+i*4));
  const indices = Array.from({ length: (data.length-end)/4 }, (_,i) => data.readUInt32LE(end+i*4));
  if (!vertices.every(Number.isFinite) || indices.some(i => i >= count)) throw new Error('Invalid mesh vertex or triangle');
  return { vertices, indices };
}

/** Deterministic reference-surface LOD only. Skeleton and synapse coordinates are untouched. */
export function simplifyReference(mesh:{vertices:number[];indices:number[]},gridNm=1000) {
  const groups=new Map<string,number>(),sums:number[][]=[],mapping:number[]=[];
  for(let i=0;i<mesh.vertices.length;i+=3){
    const p=mesh.vertices.slice(i,i+3),key=p.map(v=>Math.floor(v/gridNm)).join(',');
    let target=groups.get(key);
    if(target===undefined){target=sums.length;groups.set(key,target);sums.push([0,0,0,0]);}
    const sum=sums[target];for(let j=0;j<3;j++)sum[j]+=p[j];sum[3]++;mapping.push(target);
  }
  const vertices=sums.flatMap(s=>s.slice(0,3).map(v=>v/s[3])),indices:number[]=[],seen=new Set<string>();
  for(let i=0;i<mesh.indices.length;i+=3){
    const triangle=mesh.indices.slice(i,i+3).map(v=>mapping[v]);
    if(new Set(triangle).size<3)continue;
    const key=[...triangle].sort((a,b)=>a-b).join(',');
    if(!seen.has(key)){seen.add(key);indices.push(...triangle);}
  }
  return {vertices,indices};
}

export function decodeGzip(data: Buffer) { return gunzipSync(data, { maxOutputLength: 32*1024*1024 }); }
export function minishardEntry(data: Buffer, id: bigint, indexEnd: number) {
  if (data.length%24) throw new Error('Invalid minishard index length');
  const count = data.length/24; let body = 0n, end = BigInt(indexEnd);
  for (let i=0;i<count;i++) {
    body += data.readBigUInt64LE(i*8);
    const start = end + data.readBigUInt64LE((count+i)*8), size = data.readBigUInt64LE((2*count+i)*8);
    end = start+size;
    if (body === id) {
      if (end > BigInt(Number.MAX_SAFE_INTEGER)) throw new Error('Unsafe shard offset');
      return [Number(start),Number(end)] as [number,number];
    }
  }
  return null;
}

export interface AnnotationInfo {
  annotation_type: string; dimensions: Record<string,[number,string]>;
  properties: { id: string; type: string; enum_values?: number[]; enum_labels?: string[] }[];
  relationships: { id: string; key: string; sharding: { hash: string; preshift_bits: number; minishard_bits: number; shard_bits: number; minishard_index_encoding: string; data_encoding: string } }[];
}
export function parseSynapses(data: Buffer, info: AnnotationInfo, source: string, target: string, confidence: number) {
  if (info.annotation_type.toLowerCase() !== 'line' || Object.keys(info.dimensions).join(',') !== 'x,y,z' || !Object.values(info.dimensions).every(v=>v[0]===8e-9 && v[1]==='m')) throw new Error('Unsupported synapse coordinate frame');
  const widths: Record<string,number> = { float32:4,uint32:4,int32:4,uint16:2,int16:2,uint8:1,int8:1 };
  if (info.properties.some(p=>!widths[p.type])) throw new Error('Unsupported annotation property');
  const properties = info.properties.map((p,i)=>({...p,order:i})).sort((a,b)=>widths[b.type]-widths[a.type] || a.order-b.order);
  const offsets = new Map<string,number>(); let size = 24;
  for (const p of properties) { offsets.set(p.id,size); size += widths[p.type]; }
  size = Math.ceil(size/4)*4;
  for (const id of ['conf_pre','conf_post','body_pre_u32','body_post_u32','primary_roi']) if (!offsets.has(id)) throw new Error('Missing synapse property '+id);
  for(const [id,type] of Object.entries({conf_pre:'float32',conf_post:'float32',body_pre_u32:'uint32',body_post_u32:'uint32',primary_roi:'int16'})) if(properties.find(p=>p.id===id)?.type!==type) throw new Error('Changed synapse property type: '+id);
  if (data.length < 8) throw new Error('Truncated annotation list');
  const count = Number(data.readBigUInt64LE(0));
  if (!Number.isSafeInteger(count) || count > 400000 || 8+count*(size+8)!==data.length) throw new Error('Annotation count or byte length mismatch');
  const roi = properties.find(p=>p.id==='primary_roi')!;
  const synapses: Synapse[] = [];
  for (let i=0;i<count;i++) {
    const base = 8+i*size;
    const preBody = String(data.readUInt32LE(base+offsets.get('body_pre_u32')!));
    if (preBody !== source) throw new Error('Body-to-synapse relationship mismatch');
    if (String(data.readUInt32LE(base+offsets.get('body_post_u32')!)) !== target) continue;
    const confidencePre = data.readFloatLE(base+offsets.get('conf_pre')!), confidencePost = data.readFloatLE(base+offsets.get('conf_post')!);
    const xyz = Array.from({length:6},(_,j)=>data.readFloatLE(base+j*4));
    if (!xyz.every(Number.isFinite) || ![confidencePre,confidencePost].every(c=>Number.isFinite(c)&&c>=0&&c<=1)) throw new Error('Invalid synapse position/confidence');
    if (confidencePre < confidence || confidencePost < confidence) continue;
    const code = data.readInt16LE(base+offsets.get('primary_roi')!);
    synapses.push({ id:data.readBigUInt64LE(8+count*size+i*8).toString(),source,target,pre:xyz.slice(0,3) as XYZ,post:xyz.slice(3) as XYZ,confidencePre,confidencePost,roi:roi.enum_labels?.[roi.enum_values?.indexOf(code) ?? -1] ?? null });
  }
  return synapses;
}
