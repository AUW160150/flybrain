import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh } from 'three';
import { usePerformance } from '../state/performance';
import { useStudio } from '../state/store';
import { demoEntities, regionForEntity } from '../circuits/demo';
import { intensityAt } from '../activity/timeline';

export function PerformanceMonitor() {
  const counters = useRef({ seconds: 0, frames: 0 });
  useFrame(({ gl, scene }, dt) => {
    counters.current.seconds += dt; counters.current.frames++;
    if (counters.current.seconds < 1) return;
    let visibleMeshes = 0;
    scene.traverseVisible(object => { if (object instanceof Mesh) visibleMeshes++; });
    const s = useStudio.getState();
    const brainVisible = s.transparentHead || s.cameraMode === 'BRAIN_INSPECTION';
    const activeHighlights = brainVisible ? demoEntities.filter(e => s.layers[regionForEntity(e.id)!.id].visible && intensityAt(s.events, e.id, s.timelineMs, s.reducedMotion) > 0.01).length : 0;
    usePerformance.setState({ fps: counters.current.frames / counters.current.seconds, visibleMeshes, activeHighlights, drawCalls: gl.info.render.calls });
    counters.current.seconds = 0; counters.current.frames = 0;
  });
  return null;
}
