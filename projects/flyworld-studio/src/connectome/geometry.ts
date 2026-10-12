import type { Skeleton, RegionMesh, Synapse, XYZ } from './types';

// One native origin for every object. Never center individual neurons or infer branches.
export function inMicrometers(point: readonly number[], units: '8 nm' | 'nm'): XYZ {
  const scale = units === '8 nm' ? 0.008 : 0.001;
  return [point[0]*scale,point[1]*scale,point[2]*scale];
}
export function skeletonSegments(skeleton: Skeleton) {
  const points=new Map(skeleton.points.map(p=>[p[0],inMicrometers(p.slice(2,5),skeleton.units)]));
  const positions:number[]=[];
  for(const p of skeleton.points) if(p[6]!==-1) positions.push(...points.get(p[6])!,...points.get(p[0])!);
  return new Float32Array(positions);
}
export function regionVertices(mesh: RegionMesh) { return Float32Array.from(mesh.vertices,v=>v*0.001); }
export function synapsePositions(synapses: Synapse[], endpoint:'pre'|'post') { return new Float32Array(synapses.flatMap(s=>inMicrometers(s[endpoint],'8 nm'))); }
const colors=['#56b4e9','#e69f00','#009e73','#cc79a7','#f0e442','#d55e00','#a4b6ff','#f6bf9b'];
export function bodyColor(id: string) { return colors[Number(BigInt(id)%BigInt(colors.length))]; }
