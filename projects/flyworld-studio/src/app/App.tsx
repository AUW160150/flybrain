import { lazy, Suspense, useState } from 'react';
import { WorldCanvas } from '../world/WorldCanvas';
import { activateViewport, useKeyboard } from '../controls/keyboard';
import { useStudioClock } from '../controls/useStudioClock';
import { MovementPad } from '../controls/MovementPad';
import { Inspector } from '../inspector/Inspector';
import { ActivityPanel, useTelemetry } from '../activity/ActivityPanel';
import { useStudio, isInspection, controlsActive } from '../state/store';
import { FlyMark } from '../ui/Icons';
import { Dialog } from '../ui/Dialog';
import { DebugOverlay } from '../ui/DebugOverlay';
import type { DialogName } from '../ui/WorkspaceDialog';
import { PLACEHOLDER_LABEL, entityById } from '../circuits/demo';
import { locomotionState } from '../fly/animation';
import type { CameraMode, ExplorationMode } from '../data/contracts';

const WorkspaceDialog = lazy(() => import('../ui/WorkspaceDialog'));
const RealDataWorkspace = lazy(() => import('../realdata/RealDataWorkspace'));
const CircuitExplorer = lazy(() => import('../connectome/CircuitExplorer'));
const cameraNames: Record<CameraMode, string> = { WORLD_FOLLOW: 'Follow', WORLD_ORBIT: 'Orbit', FLY_INSPECTION: 'Fly', BRAIN_INSPECTION: 'Brain' };
const modeNames: Record<ExplorationMode, string> = { USER_CONTROL: 'USER CONTROL', EDUCATIONAL_RULE: 'EDUCATIONAL RULE', DATA_REPLAY: 'DATA REPLAY' };
function WorldTelemetry() {
  const s = useTelemetry();
  return <div className="world-telemetry"><span data-testid="fly-position" data-x={s.pose.x} data-y={s.pose.y} data-z={s.pose.z}>X {s.pose.x.toFixed(2)} <b>·</b> Z {s.pose.z.toFixed(2)}</span><span data-testid="fly-altitude" title="Height above the ground in scene units">Height {s.pose.y.toFixed(2)}</span><span data-testid="fly-heading" data-yaw={s.pose.heading}>{(s.pose.heading * 180 / Math.PI).toFixed(0)}°</span><span data-testid="fly-state" title={locomotionState(s)}>{locomotionState(s)}</span><span data-testid="collision-state">{s.collided ? 'CONTACT' : 'CLEAR'}</span></div>;
}

export function App() {
  useKeyboard(); useStudioClock();
  const [dialog, setDialog] = useState<DialogName | null>(null);
  const [dataOpen, setDataOpen] = useState(false);
  const [atlasOpen, setAtlasOpen] = useState(false);
  const showWorld = () => { setDataOpen(false); setAtlasOpen(false); useStudio.getState().backToWorld(); };
  const showAtlas = () => { useStudio.getState().setControlsFocus(false, 'Real circuit anatomy'); setDataOpen(false); setAtlasOpen(true); };
  const showData = () => {
    useStudio.getState().setControlsFocus(false, 'MaleCNS data workspace');
    useStudio.getState().backToWorld(); setAtlasOpen(false); setDataOpen(true);
  };
  const camera = useStudio(s => s.cameraMode);
  const mode = useStudio(s => s.mode);
  const reduced = useStudio(s => s.reducedMotion);
  const debug = useStudio(s => s.showDebug);
  const focus = useStudio(s => s.brainFocus);
  const status = useStudio(s => s.rendererStatus);
  const active = useStudio(controlsActive);
  return <main className={`studio${reduced ? ' reduced-motion' : ''}`}>
    <header className="topbar"><a className="brand" href="#" onClick={e => { e.preventDefault(); showWorld(); }}><FlyMark /><span>FlyWorld<span className="brand-dot">.</span></span></a>
      <nav aria-label="Main navigation"><button className={!dataOpen ? 'nav-active' : ''} onClick={showWorld}>Explore</button><button className={dataOpen ? 'nav-active' : ''} onClick={showData}>MaleCNS data</button><button onClick={() => setDialog('data')}>Circuit packages</button><button onClick={() => setDialog('experiments')}>Experiments <span className="soon">LATER</span></button></nav>
      <div className="topbar-right"><a className="portfolio-link" href="/" title="Back to the Flybrain portfolio">Flybrain ↖</a><span className="local-status"><span className="tiny-dot mint" />LOCAL WORKSPACE</span><button className="help-button" onClick={() => setDialog('help')} aria-label="Controls and help">?</button></div>
    </header>
    <div className="workspace-heading"><div><div className="eyebrow">EXPLORATION STUDIO <span>/</span> DATA INTEGRATION 03</div><h1>A small world. A closer look.</h1></div><button className="science-badge" onClick={() => setDialog('science')}><span className="tiny-dot" /><span>EDUCATIONAL + STRUCTURAL<small>Explicit sources · no neural dynamics</small></span><span>↗</span></button></div>
    <div className="mode-toolbar"><div className="mode-switch" aria-label="Exploration modes">{(Object.keys(modeNames) as ExplorationMode[]).map(value => <button key={value} aria-pressed={mode === value} onClick={() => useStudio.getState().setMode(value)}>{modeNames[value]}</button>)}</div><span className="simulation-badge">SIMULATION UNAVAILABLE</span><div className="display-options"><label><input type="checkbox" checked={reduced} onChange={e => useStudio.getState().setReducedMotion(e.target.checked)} />Reduced motion</label><button aria-pressed={debug} onClick={() => useStudio.setState({ showDebug: !debug })}>Performance</button></div></div>
    {atlasOpen ? <Suspense fallback={<p role="status">Loading real circuit anatomy…</p>}><CircuitExplorer showWorld={showWorld}/></Suspense> : dataOpen ? <Suspense fallback={<p role="status">Loading MaleCNS data workspace…</p>}><RealDataWorkspace showWorld={showWorld} showAtlas={showAtlas} /></Suspense> : <div className="workspace">
      <section className="world" aria-label="World workspace">
        <div className="viewport" data-world-viewport tabIndex={0} aria-label="3D viewport. Click to focus keyboard controls. Tab inspects the brain. Escape returns to the world." onPointerDownCapture={e => activateViewport(e.currentTarget)}>
          <WorldCanvas />
        </div>
        <div className={`controls-focus ${active ? 'controls-focused' : ''}`}><strong data-testid="controls-active">{active ? 'CONTROLS ACTIVE' : 'CONTROLS INACTIVE'}</strong><span>{isInspection(camera) ? 'Inspection pauses locomotion' : mode !== 'USER_CONTROL' ? 'Choose USER CONTROL to move' : active ? 'WASD / arrows · Shift boost · X stop' : 'Click the viewport to move'}</span><small>USER_DRIVEN_ILLUSTRATION</small></div>
        <div className="world-top"><div className="breadcrumb" aria-label="Current camera mode"><span>World</span>{isInspection(camera) && <><b>/</b><span>Fly</span></>}{camera === 'BRAIN_INSPECTION' && <><b>/</b><span>Brain</span></>}<span className="mode-code" data-testid="camera-mode">{camera}</span></div><span className="control-badge" data-testid="control-mode">{mode === 'USER_CONTROL' ? 'CONTROL MODE: USER' : `${modeNames[mode]} · SYNTHETIC DEMO`}</span></div>
        <div className="scene-label"><span className="eyebrow">{camera === 'BRAIN_INSPECTION' ? 'LAYERED EDUCATIONAL BRAIN' : 'GARDEN / 001'}</span><p>{camera === 'BRAIN_INSPECTION' ? 'Five teaching categories · 13 generic demo nodes' : 'Tree obstacle · flower / food marker · neutral landmark'}</p><span className="physics-badge">COLLISION HANDLING: GAME PHYSICS</span></div>
        {debug && <DebugOverlay />}
        <div className="world-bottom"><div className="movement-block"><MovementPad /><span>{isInspection(camera) ? 'Orbit to look closer' : mode !== 'USER_CONTROL' ? 'Gestures replay in place' : 'Hold to move · A / D turn'}<small>{camera === 'WORLD_FOLLOW' ? 'Choose Orbit to rotate with your mouse' : 'Drag to orbit · scroll to zoom'}</small></span></div>
          <div className="camera-controls" aria-label="Camera controls">{(Object.keys(cameraNames) as CameraMode[]).map(value => <button key={value} aria-pressed={camera === value} onClick={() => useStudio.getState().setCamera(value)}>{cameraNames[value]}</button>)}</div>
        </div>
        {isInspection(camera) && <div className="brain-navigation"><button onClick={() => useStudio.getState().backToWorld()}>← Back to world <kbd>ESC</kbd></button>{camera === 'BRAIN_INSPECTION' && <><button onClick={() => useStudio.getState().focusEntity(null)}>Whole brain</button><button onClick={showAtlas}>Real circuit anatomy</button></>}{focus && <span>{entityById.get(focus)?.name}</span>}</div>}
        <div className="world-status"><span className="placeholder-caption">{PLACEHOLDER_LABEL}</span><span data-testid="renderer-status">{status === 'READY' ? 'WEBGL · READY' : status === 'LOADING' ? 'INITIALIZING 3D' : '3D UNAVAILABLE'}</span></div>
        <WorldTelemetry />
      </section>
      <Inspector />
    </div>}
    <ActivityPanel worldVisible={!dataOpen && !atlasOpen} showWorld={showWorld} />
    <footer className="footer"><span>FLYWORLD <b> / </b> v0.3.0</span><span>Explore the interface. Keep the evidence visible.</span><button onClick={() => setDialog('science')}>Scientific boundaries ↗</button></footer>
    {dialog && <Dialog title={{ science: 'Scientific boundaries', data: 'Circuit packages', experiments: 'Future experiment workspace', help: 'Explore with your keyboard' }[dialog]} onClose={() => setDialog(null)}><Suspense fallback={<p>Loading panel…</p>}><WorkspaceDialog name={dialog} /></Suspense></Dialog>}
  </main>;
}
