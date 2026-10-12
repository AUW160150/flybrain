import { Component, Suspense, useEffect, useState, type ReactNode } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { ProceduralFly } from '../fly/ProceduralFly';
import { CameraRig } from './CameraRig';
import { Environment } from './Environment';
import { useStudio } from '../state/store';
import { PerformanceMonitor } from './PerformanceMonitor';

/** Rendering boundary. A future backend adapter replaces this Canvas without changing contracts or controls. */
export const rendererDescriptor = { backend: 'WEBGL', implementation: 'React Three Fiber 9', anatomicalCoordinates: false } as const;

function SceneClock() {
  const gl = useThree(s => s.gl);
  useEffect(() => {
    useStudio.setState({ rendererStatus: 'READY' });
    const lost = (event: Event) => { event.preventDefault(); useStudio.setState({ rendererStatus: 'UNAVAILABLE' }); };
    gl.domElement.addEventListener('webglcontextlost', lost);
    return () => { gl.domElement.removeEventListener('webglcontextlost', lost); };
  }, [gl]);
  return null;
}

class RenderBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { useStudio.setState({ rendererStatus: 'UNAVAILABLE' }); }
  render() { return this.state.failed ? <Unavailable /> : this.props.children; }
}
function Unavailable() {
  return <div className="canvas-unavailable" role="alert"><h2>3D rendering unavailable</h2><p>Enable hardware acceleration or open FlyWorld in a WebGL-capable browser. Metadata and scientific boundaries remain available.</p></div>;
}

export function WorldCanvas() {
  const [supported] = useState(() => {
    try {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('webgl2');
      context?.getExtension('WEBGL_lose_context')?.loseContext();
      return !!context;
    } catch { return false; }
  });
  const status = useStudio(s => s.rendererStatus);
  const brain = useStudio(s => s.cameraMode === 'BRAIN_INSPECTION');
  useEffect(() => { if (!supported) useStudio.setState({ rendererStatus: 'UNAVAILABLE' }); }, [supported]);
  if (!supported) return <Unavailable />;
  return <RenderBoundary>
    {status === 'UNAVAILABLE' && <Unavailable />}
    <Canvas shadows dpr={[1, 1.75]} camera={{ position: [5, 4, 7], fov: 42, near: 0.03, far: 120 }}
      gl={{ antialias: true, powerPreference: 'high-performance' }} aria-label="Procedural placeholder fly in a 3D world">
      <color attach="background" args={[brain ? '#192621' : '#29392f']} />
      <fog attach="fog" args={['#29392f', 13, 38]} />
      <ambientLight intensity={1.3} />
      <hemisphereLight args={['#dfefd8', '#647458', 1.4]} />
      <directionalLight position={[4, 8, 5]} intensity={3} color="#fff1cd" castShadow shadow-mapSize={[1024, 1024]} shadow-camera-left={-12} shadow-camera-right={12} shadow-camera-top={12} shadow-camera-bottom={-12} shadow-normalBias={0.025} />
      <directionalLight position={[-3, 3, -4]} intensity={1.6} color="#a2d2c7" />
      <Suspense fallback={null}>
        {!brain && <Environment />}
        <ProceduralFly />
        <CameraRig />
      </Suspense>
      <SceneClock />
      <PerformanceMonitor />
    </Canvas>
  </RenderBoundary>;
}
