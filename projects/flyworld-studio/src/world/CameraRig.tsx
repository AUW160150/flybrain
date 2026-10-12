import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import type { OrbitControls as OrbitControlsImpl } from 'three-stdlib';
import { Vector3 } from 'three';
import { useStudio } from '../state/store';
import type { CameraMode } from '../data/contracts';
import { entityById } from '../circuits/demo';

const target = new Vector3();
const destination = new Vector3();
const up = new Vector3(0, 1, 0);
const origin = new Vector3();
const shift = new Vector3();

export function CameraRig() {
  const controls = useRef<OrbitControlsImpl>(null);
  const mode = useStudio(s => s.cameraMode);
  const previous = useRef<CameraMode | null>(null);
  const revision = useRef(-1);
  const transitioning = useRef(true);
  const transitionTime = useRef(0);
  useFrame(({ camera }, dt) => {
    const s = useStudio.getState();
    const orbit = controls.current;
    if (!orbit) return;
    if (previous.current !== s.cameraMode || revision.current !== s.cameraRevision) {
      previous.current = s.cameraMode; transitioning.current = true; transitionTime.current = 0;
      revision.current = s.cameraRevision;
    }
    const brain = s.cameraMode === 'BRAIN_INSPECTION';
    const fly = s.cameraMode === 'FLY_INSPECTION';
    const entity = brain && s.brainFocus ? entityById.get(s.brainFocus) : null;
    target.set(entity?.position[0] ?? 0, (brain ? 1.04 : 0.75) + (entity?.position[1] ?? 0), (brain ? 0.67 : 0) + (entity?.position[2] ?? 0));
    // Keep a ground reference in world views so takeoff visibly raises the fly.
    // Inspection still centers the actual body at its current altitude.
    target.applyAxisAngle(up, s.pose.heading).add(origin.set(s.pose.x, brain || fly ? s.pose.y : 0, s.pose.z));
    destination.set(...(brain ? entity ? [0.38, 0.23, 0.72] : [0.8, 0.45, 1.2] : fly ? [2.6, 1.6, 3.1] : [4.5, 3.2, 5.8]) as [number, number, number]);
    destination.applyAxisAngle(up, s.pose.heading).add(target);
    const follow = s.cameraMode === 'WORLD_FOLLOW';
    orbit.enabled = !transitioning.current && !follow;
    // Do not clamp the old world distance before the eased approach has finished.
    orbit.minDistance = transitioning.current ? 0.03 : brain ? 0.5 : 2.1;
    orbit.maxDistance = transitioning.current ? Infinity : brain ? 4 : 20;
    if (transitioning.current || follow) {
      const alpha = s.reducedMotion ? 1 : 1 - Math.exp(-Math.min(dt, 0.05) * 6);
      camera.position.lerp(destination, alpha);
      orbit.target.lerp(target, alpha);
      transitionTime.current += dt;
      if (s.reducedMotion || transitionTime.current > 1.5) transitioning.current = false;
    } else if (s.cameraMode === 'WORLD_ORBIT') {
      // Preserve the user's orbit offset as the controlled fly moves.
      shift.copy(target).sub(orbit.target);
      camera.position.add(shift); orbit.target.copy(target);
    }
    orbit.update();
  });
  return <OrbitControls ref={controls} makeDefault enablePan={false} enableDamping dampingFactor={0.09}
    maxPolarAngle={mode === 'BRAIN_INSPECTION' ? Math.PI : Math.PI * 0.48} />;
}
