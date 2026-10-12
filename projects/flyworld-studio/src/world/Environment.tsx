import { memo } from 'react';
import { Grid } from '@react-three/drei';
import { obstacles, WORLD_LIMIT } from './collision';

/** All props and colliders share definitions; decoration has no neural function. */
export const Environment = memo(function Environment() {
  const [tree, food, landmark] = obstacles;
  return <group name="educational-world">
    <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.015, 0]}>
      <planeGeometry args={[100, 100]} /><meshStandardMaterial color="#26352e" roughness={1} />
    </mesh>
    <Grid position={[0, 0.003, 0]} args={[24, 24]} cellSize={1} cellThickness={0.5} cellColor="#425148"
      sectionSize={4} sectionThickness={0.8} sectionColor="#667564" fadeDistance={25} fadeStrength={2} />
    {[-1, 1].flatMap(side => [
      <mesh key={`x${side}`} position={[side * (WORLD_LIMIT + 0.8), 0.13, 0]}><boxGeometry args={[0.1, 0.26, 24]} /><meshStandardMaterial color="#687a5e" /></mesh>,
      <mesh key={`z${side}`} position={[0, 0.13, side * (WORLD_LIMIT + 0.8)]}><boxGeometry args={[24, 0.26, 0.1]} /><meshStandardMaterial color="#687a5e" /></mesh>,
    ])}
    <group position={[tree.x, 0, tree.z]} name="tree-obstacle">
      <mesh position={[0, 1, 0]} castShadow><cylinderGeometry args={[0.28, 0.36, 2, 7]} /><meshStandardMaterial color="#7b694e" flatShading /></mesh>
      <mesh position={[0, 2.6, 0]} scale={[0.95, 1.5, 0.95]} castShadow><icosahedronGeometry args={[1, 1]} /><meshStandardMaterial color="#66835e" flatShading /></mesh>
      <mesh position={[0, 0.015, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[tree.radius - 0.03, tree.radius, 32]} /><meshBasicMaterial color="#a4b684" transparent opacity={0.6} /></mesh>
    </group>
    <group position={[food.x, 0, food.z]} name="flower-food-marker">
      <mesh position={[0, 0.15, 0]} castShadow><cylinderGeometry args={[0.58, 0.4, 0.3, 12]} /><meshStandardMaterial color="#98694f" /></mesh>
      <mesh position={[0, 0.8, 0]} castShadow><cylinderGeometry args={[0.045, 0.07, 1.3, 6]} /><meshStandardMaterial color="#89a462" /></mesh>
      <mesh position={[0, 1.45, 0]} castShadow><sphereGeometry args={[0.19, 10, 6]} /><meshStandardMaterial color="#edc45c" /></mesh>
      {Array.from({ length: 6 }, (_, i) => <mesh key={i} position={[Math.cos(i * Math.PI / 3) * 0.28, 1.4, Math.sin(i * Math.PI / 3) * 0.28]} scale={[0.29, 0.12, 0.22]} rotation={[0, -i * Math.PI / 3, 0]} castShadow>
        <icosahedronGeometry args={[1, 1]} /><meshStandardMaterial color="#d7a5ba" flatShading />
      </mesh>)}
    </group>
    <group position={[landmark.x, 0, landmark.z]} name="neutral-landmark">
      <mesh position={[0, 0.08, 0]} receiveShadow><cylinderGeometry args={[0.6, 0.6, 0.16, 24]} /><meshStandardMaterial color="#9caaa1" /></mesh>
      <mesh position={[0, 0.68, 0]} castShadow><boxGeometry args={[0.7, 1.2, 0.7]} /><meshStandardMaterial color="#a8b6b7" roughness={0.5} /></mesh>
      <mesh position={[0, 0.72, 0.356]}><boxGeometry args={[0.35, 0.075, 0.01]} /><meshBasicMaterial color="#445b60" /></mesh>
    </group>
  </group>;
});
