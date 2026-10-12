import { memo, useLayoutEffect, useMemo, useRef } from 'react';
import { useFrame, type ThreeEvent } from '@react-three/fiber';
import { Html, Line } from '@react-three/drei';
import { Color, InstancedMesh, MeshStandardMaterial, Object3D } from 'three';
import { useStudio } from '../state/store';
import { intensityAt } from '../activity/timeline';
import { educationalPackage, entityById, regionForEntity } from '../circuits/demo';
import type { DemoId, DemoRegion } from '../data/contracts';

function select(event: ThreeEvent<MouseEvent>, id: DemoId) {
  event.stopPropagation();
  const state = useStudio.getState();
  state.selectEntity(id);
  if (state.cameraMode !== 'BRAIN_INSPECTION') state.setCamera('BRAIN_INSPECTION');
}
const RegionVolume = memo(function RegionVolume({ region, opacity }: { region: DemoRegion; opacity: number }) {
  const material = useRef<MeshStandardMaterial>(null);
  const selected = useStudio(s => s.selectedEntity === region.id);
  useFrame(() => {
    const s = useStudio.getState();
    if (material.current) material.current.emissiveIntensity = 0.07 + intensityAt(s.events, region.id, s.timelineMs, s.reducedMotion) * 1.5;
  });
  return <group position={region.position} name={region.id}>
    <mesh scale={region.scale}
      onClick={event => { if (!event.intersections.some(hit => hit.object.name === 'demo-neurons')) select(event, region.id); }}
      onPointerMove={event => { if (!event.intersections.some(hit => hit.object.name === 'demo-neurons')) { event.stopPropagation(); useStudio.getState().hoverEntity(region.id); } }}
      onPointerOut={() => useStudio.getState().hoverEntity(null)}>
      <icosahedronGeometry args={[1, 2]} />
      <meshStandardMaterial ref={material} color={region.color} emissive={region.color} roughness={0.5} transparent opacity={opacity} depthWrite={false} flatShading />
    </mesh>
    <mesh scale={region.scale} raycast={() => undefined}>
      <icosahedronGeometry args={[selected ? 1.035 : 1.005, 1]} />
      <meshBasicMaterial color={selected ? '#ffffff' : region.color} wireframe transparent opacity={selected ? 0.75 : 0.2} depthWrite={false} />
    </mesh>
  </group>;
});

function DemoNeurons() {
  const mesh = useRef<InstancedMesh>(null);
  const layers = useStudio(s => s.layers);
  const nodes = useMemo(() => educationalPackage.neurons.filter(n => layers[n.regionId].visible), [layers]);
  const scratch = useMemo(() => ({ object: new Object3D(), color: new Color(), white: new Color('#ffffff') }), []);
  useLayoutEffect(() => {
    if (!mesh.current) return;
    for (let i = 0; i < nodes.length; i++) {
      scratch.object.position.set(...nodes[i].position);
      scratch.object.scale.setScalar(0.026); scratch.object.updateMatrix();
      mesh.current.setMatrixAt(i, scratch.object.matrix);
    }
    mesh.current.instanceMatrix.needsUpdate = true;
    mesh.current.computeBoundingSphere();
    if (mesh.current.boundingSphere) mesh.current.boundingSphere.radius += 0.01;
  }, [nodes, scratch]);
  useFrame(() => {
    const s = useStudio.getState();
    if (!mesh.current) return;
    nodes.forEach((node, i) => {
      const value = intensityAt(s.events, node.id, s.timelineMs, s.reducedMotion);
      scratch.color.set(regionForEntity(node.id)!.color).lerp(scratch.white, s.selectedEntity === node.id ? 0.85 : value * 0.65);
      mesh.current!.setColorAt(i, scratch.color);
      scratch.object.position.set(...node.position);
      scratch.object.scale.setScalar(0.026 * (s.reducedMotion ? 1 : 1 + value * 0.15));
      scratch.object.updateMatrix(); mesh.current!.setMatrixAt(i, scratch.object.matrix);
    });
    if (mesh.current.instanceColor) mesh.current.instanceColor.needsUpdate = true;
    mesh.current.instanceMatrix.needsUpdate = true;
  });
  return <instancedMesh ref={mesh} name="demo-neurons" args={[undefined, undefined, nodes.length]} frustumCulled={false}
    onClick={event => { if (event.instanceId !== undefined && nodes[event.instanceId]) select(event, nodes[event.instanceId].id); }}
    onPointerMove={event => { if (event.instanceId !== undefined && nodes[event.instanceId]) { event.stopPropagation(); useStudio.getState().hoverEntity(nodes[event.instanceId].id); } }}
    onPointerOut={() => useStudio.getState().hoverEntity(null)}>
    <icosahedronGeometry args={[1, 1]} />
    <meshBasicMaterial toneMapped={false} />
  </instancedMesh>;
}

export function PlaceholderBrain() {
  const layers = useStudio(s => s.layers);
  const hovered = useStudio(s => s.hoveredEntity);
  const tooltip = hovered ? entityById.get(hovered) : null;
  return <group position={[0, 0.48, 0.67]} name="educational-placeholder-brain">
    {educationalPackage.regions.filter(r => layers[r.id].visible).map(region => <RegionVolume key={region.id} region={region} opacity={layers[region.id].opacity} />)}
    {educationalPackage.relations.map(relation => {
      const source = educationalPackage.neurons.find(n => n.id === relation.sourceId)!;
      const target = educationalPackage.neurons.find(n => n.id === relation.targetId)!;
      return layers[source.regionId].visible && layers[target.regionId].visible
        ? <Line key={`${source.id}:${target.id}`} points={[source.position, target.position]} color="#bac8bf" lineWidth={0.8} dashed dashSize={0.01} gapSize={0.008} transparent opacity={0.42} raycast={() => undefined} /> : null;
    })}
    <DemoNeurons />
    {tooltip && <Html position={[tooltip.position[0], tooltip.position[1] + 0.06, tooltip.position[2]]} center style={{ pointerEvents: 'none' }}>
      <div className="brain-tooltip"><strong>{tooltip.name}</strong><code>{tooltip.id}</code><span>UNVERIFIED · educational placeholder</span></div>
    </Html>}
  </group>;
}
