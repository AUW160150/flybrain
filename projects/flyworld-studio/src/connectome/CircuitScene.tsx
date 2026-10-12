import { Component, Suspense, useEffect, useMemo, type ReactNode } from 'react';
import { Canvas } from '@react-three/fiber';
import { Bounds, OrbitControls, useBounds } from '@react-three/drei';
import { BufferAttribute, BufferGeometry, DoubleSide } from 'three';
import type { RegionMesh, Skeleton, Synapse } from './types';
import { bodyColor, inMicrometers, regionVertices, skeletonSegments, synapsePositions } from './geometry';

function useGeometry(positions:Float32Array,indices?:number[]) {
  const geometry=useMemo(()=>{
    const g=new BufferGeometry(); g.setAttribute('position',new BufferAttribute(positions,3));
    if(indices){g.setIndex(indices);g.computeVertexNormals();}
    return g;
  },[positions,indices]);
  useEffect(()=>()=>geometry.dispose(),[geometry]); return geometry;
}
function SkeletonLines({data,selected,onSelect}:{data:Skeleton;selected:boolean;onSelect:()=>void}) {
  const positions=useMemo(()=>skeletonSegments(data),[data]), geometry=useGeometry(positions);
  return <lineSegments geometry={geometry} name={`native-neuron-${data.bodyId}`} onClick={e=>{e.stopPropagation();onSelect();}}>
    <lineBasicMaterial color={selected?'#ffffff':bodyColor(data.bodyId)} transparent opacity={selected?1:0.85} />
  </lineSegments>;
}
function RegionSurface({data}:{data:RegionMesh}) {
  const positions=useMemo(()=>regionVertices(data),[data]),geometry=useGeometry(positions,data.indices);
  return <mesh geometry={geometry} name={`native-region-${data.id}`}><meshBasicMaterial color={data.id.startsWith('brain')?'#6fa6b0':'#a3af84'} transparent opacity={0.055} depthWrite={false} side={DoubleSide} /></mesh>;
}
function SynapsePoints({data,endpoint}:{data:Synapse[];endpoint:'pre'|'post'}) {
  const positions=useMemo(()=>synapsePositions(data,endpoint),[data,endpoint]),geometry=useGeometry(positions);
  return <points geometry={geometry} name={`recorded-${endpoint}-synapses`}><pointsMaterial color={endpoint==='pre'?'#ffb347':'#58d8ff'} size={5} sizeAttenuation={false} depthTest={false} /></points>;
}
function SynapseContacts({data}:{data:Synapse[]}) {
  const positions=useMemo(()=>new Float32Array(data.flatMap(s=>[...inMicrometers(s.pre,'8 nm'),...inMicrometers(s.post,'8 nm')])),[data]);
  const geometry=useGeometry(positions);
  return <lineSegments geometry={geometry} name="recorded-synaptic-contacts"><lineBasicMaterial color="#d6ded5" depthTest={false}/></lineSegments>;
}
function Reframe({revision}:{revision:string}) {
  const bounds=useBounds();
  useEffect(()=>{bounds.refresh().clip().fit();},[bounds,revision]); return null;
}
class SceneBoundary extends Component<{children:ReactNode},{error:boolean}> {
  state={error:false}; static getDerivedStateFromError(){return {error:true};}
  render(){return this.state.error?<p role="alert">3D rendering unavailable. Neuron records and connection counts remain available.</p>:this.props.children;}
}
export default function CircuitScene({skeletons,regions,synapses,selected,onSelect,frame}:{skeletons:Skeleton[];regions:RegionMesh[];synapses:Synapse[];selected:string|null;onSelect:(id:string)=>void;frame:number}) {
  const revision=skeletons.map(s=>s.bodyId).join(',')+'|'+regions.map(r=>r.id).join(',')+'|'+frame;
  return <SceneBoundary><div className="circuit-canvas" data-testid="circuit-canvas">
    <Canvas camera={{position:[500,300,1100],near:0.05,far:20000,fov:45}} dpr={[1,1.5]} gl={{antialias:true}} aria-label="Source-backed neurons in shared MaleCNS coordinates">
      <color attach="background" args={['#111e23']} />
      <Suspense fallback={null}><Bounds margin={1.15} maxDuration={0}>
        <group>{regions.map(r=><RegionSurface key={r.id} data={r}/>)}
          {skeletons.map(s=><SkeletonLines key={s.bodyId} data={s} selected={selected===s.bodyId} onSelect={()=>onSelect(s.bodyId)}/>)}
          {!!synapses.length && <><SynapseContacts data={synapses}/><SynapsePoints data={synapses} endpoint="pre"/><SynapsePoints data={synapses} endpoint="post"/></>}
        </group><Reframe revision={revision}/>
      </Bounds></Suspense>
      <OrbitControls makeDefault enableDamping={false}/>
    </Canvas>
    {!skeletons.length && <p className="circuit-canvas-hint">Search for neurons, then add them to this view.<br/>Region surfaces provide anatomical context.</p>}
  </div></SceneBoundary>;
}
