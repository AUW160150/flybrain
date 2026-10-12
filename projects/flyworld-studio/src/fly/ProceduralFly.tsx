import { memo, useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';
import { Group, Quaternion, Vector3 } from 'three';
import { PlaceholderBrain } from '../brain/PlaceholderBrain';
import { useStudio, isInspection } from '../state/store';
import { animationPose, avatarAnimation, wingRotation } from './animation';

type Point = [number, number, number];
function Limb({ from, to, radius = 0.025 }: { from: Point; to: Point; radius?: number }) {
  const shape = useMemo(() => {
    const a = new Vector3(...from), b = new Vector3(...to), delta = b.clone().sub(a);
    return { position: a.add(b).multiplyScalar(0.5), length: delta.length(), quaternion: new Quaternion().setFromUnitVectors(new Vector3(0, 1, 0), delta.normalize()) };
  }, [from[0], from[1], from[2], to[0], to[1], to[2]]);
  return <mesh position={shape.position} quaternion={shape.quaternion} castShadow>
    <cylinderGeometry args={[radius * 0.65, radius, shape.length, 5]} />
    <meshStandardMaterial color="#4f4d36" roughness={0.85} />
  </mesh>;
}

function Leg({ side, index }: { side: number; index: number }) {
  const ref = useRef<Group>(null);
  useFrame(() => {
    const s = useStudio.getState();
    if (!ref.current || isInspection(s.cameraMode)) return;
    const animation = avatarAnimation(s);
    const pose = animationPose(animation.name, animation.elapsedMs + index * 150 + side * 200, s.reducedMotion);
    const grooming = animation.name === 'GROOM' && index === 0;
    ref.current.rotation.x = grooming ? pose.groom * 0.6 : pose.gait * 0.3;
    ref.current.rotation.z = grooming ? -side * 0.65 : ['TAKEOFF', 'FLIGHT_IDLE'].includes(animation.name) ? side * 0.28 : 0;
  });
  const spread = index === 0 ? 0.46 : index === 1 ? 0 : -0.48;
  return <group ref={ref} position={[side * 0.23, 0.18, 0.28 - index * 0.32]}>
    <Limb from={[0, 0, 0]} to={[side * 0.3, -0.08, spread * 0.45]} radius={0.035} />
    <Limb from={[side * 0.3, -0.08, spread * 0.45]} to={[side * 0.53, -0.45, spread]} />
    <Limb from={[side * 0.53, -0.45, spread]} to={[side * 0.7, -0.72, spread + 0.06]} radius={0.018} />
  </group>;
}

function Wing({ side }: { side: number }) {
  const ref = useRef<Group>(null);
  useFrame(() => {
    const s = useStudio.getState();
    const animation = avatarAnimation(s);
    if (ref.current && !isInspection(s.cameraMode)) ref.current.rotation.set(...wingRotation(animation.name, animation.elapsedMs, s.reducedMotion, side));
  });
  return <group ref={ref} name={`placeholder-wing-${side === 1 ? 'right' : 'left'}`} position={[side * 0.16, 0.65, -0.02]} rotation={[0, side * -0.35, side * 0.12]}>
    <mesh position={[side * 0.39, 0, -0.62]} rotation={[0, side * -0.17, 0]} scale={[0.35, 0.018, 0.79]}>
      <sphereGeometry args={[1, 16, 8]} />
      <meshStandardMaterial color="#dce9d8" transparent opacity={0.55} metalness={0.15} roughness={0.32} depthWrite={false} />
    </mesh>
    {[0, 1, 2].map(i => <Line key={i} points={[[0, 0.012, 0], [side * (0.27 + i * 0.1), 0.019, -0.65], [side * (0.3 + i * 0.08), 0.01, -1.24]]} color="#8faaa0" transparent opacity={0.6} lineWidth={0.6} />)}
  </group>;
}

export const ProceduralFly = memo(function ProceduralFly() {
  const root = useRef<Group>(null);
  const proboscis = useRef<Group>(null);
  const transparent = useStudio(s => s.transparentHead);
  const brainMode = useStudio(s => s.cameraMode === 'BRAIN_INSPECTION');
  useFrame(() => {
    const s = useStudio.getState();
    if (!root.current) return;
    const animation = avatarAnimation(s);
    const pose = animationPose(animation.name, animation.elapsedMs, s.reducedMotion);
    const hop = isInspection(s.cameraMode) ? 0 : pose.hop;
    root.current.position.set(s.pose.x, 0.56 + s.pose.y + hop + (isInspection(s.cameraMode) ? 0 : pose.idleBob), s.pose.z);
    root.current.rotation.set(hop * -0.22, s.pose.heading, 0);
    if (proboscis.current && !isInspection(s.cameraMode)) proboscis.current.scale.y = pose.proboscis;
  });
  return <group ref={root} name="procedural-placeholder-avatar">
    <group visible={!brainMode}>
      <mesh position={[0, 0.25, -0.59]} scale={[0.41, 0.37, 0.69]} castShadow>
        <icosahedronGeometry args={[1, 2]} /><meshStandardMaterial color="#746448" roughness={0.8} flatShading />
      </mesh>
      {[-0.33, -0.58, -0.81].map((z, i) => <mesh key={z} position={[0, 0.25, z]} rotation={[Math.PI / 2, 0, 0]} scale={[1, 0.84, 1]}>
        <torusGeometry args={[0.38 - i * 0.022, 0.025, 4, 16]} /><meshStandardMaterial color="#423c2c" />
      </mesh>)}
      <mesh position={[0, 0.37, 0]} scale={[0.39, 0.41, 0.49]} castShadow>
        <icosahedronGeometry args={[1, 2]} /><meshStandardMaterial color="#5a5e45" roughness={0.8} flatShading />
      </mesh>
      {[-1, 1].map(side => <group key={side}>
        {[0, 1, 2].map(index => <Leg key={index} side={side} index={index} />)}
        <Wing side={side} />
        <mesh position={[side * 0.27, 0.51, 0.77]} scale={[0.19, 0.25, 0.22]} castShadow>
          <icosahedronGeometry args={[1, 2]} /><meshStandardMaterial color="#ad573f" roughness={0.43} metalness={0.12} flatShading transparent={transparent} opacity={transparent ? 0.22 : 1} depthWrite={!transparent} />
        </mesh>
        <Limb from={[side * 0.1, 0.65, 0.9]} to={[side * 0.19, 0.9, 1.04]} radius={0.013} />
      </group>)}
      <group ref={proboscis} position={[0, 0.32, 0.91]}>
        <mesh position={[0, -0.16, 0.06]} rotation={[-0.3, 0, 0]}>
          <cylinderGeometry args={[0.025, 0.05, 0.32, 6]} /><meshStandardMaterial color="#897252" />
        </mesh>
      </group>
    </group>
    <mesh position={[0, 0.48, 0.67]} scale={[0.38, 0.34, 0.34]} visible={!brainMode}>
      <icosahedronGeometry args={[1, 2]} />
      <meshStandardMaterial color={transparent ? '#95c9b8' : '#656148'} transparent={transparent} opacity={transparent ? 0.14 : 1} depthWrite={!transparent} roughness={0.7} wireframe={transparent} />
    </mesh>
    {(transparent || brainMode) && <PlaceholderBrain />}
  </group>;
});
