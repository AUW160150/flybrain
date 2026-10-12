import { usePerformance } from '../state/performance';
import { controlsActive } from '../state/store';
import { useTelemetry } from '../activity/ActivityPanel';
import { avatarAnimation, locomotionState } from '../fly/animation';

export function DebugOverlay() {
  const metrics = usePerformance();
  const s = useTelemetry();
  return <div className="debug-overlay" tabIndex={0} aria-label="Performance overlay"><strong>MOVEMENT · GAME UNITS</strong><dl>
    <dt>Pressed keys</dt><dd data-testid="pressed-keys">{[...s.pressedKeys].sort().join(' + ') || 'None'}</dd>
    <dt>Movement pad</dt><dd>{Object.entries(s.padMotion).filter(([, down]) => down).map(([key]) => key).join(' + ') || 'None'}</dd>
    <dt>Position X / Y / Z</dt><dd>{[s.pose.x, s.pose.y, s.pose.z].map(n => n.toFixed(2)).join(' / ')}</dd>
    <dt>Heading / yaw</dt><dd>{(s.pose.heading * 180 / Math.PI).toFixed(1)}°</dd>
    <dt>Forward speed</dt><dd data-testid="forward-speed">{s.forwardSpeed.toFixed(3)} units/s</dd>
    <dt>Turn speed</dt><dd>{s.turnSpeed.toFixed(3)} rad/s</dd>
    <dt>Movement state</dt><dd>{locomotionState(s)}</dd>
    <dt>Avatar gesture</dt><dd>{avatarAnimation(s).name}</dd>
    <dt>Collision</dt><dd>{s.collided ? 'CONTACT' : 'CLEAR'}</dd>
    <dt>Controls</dt><dd>{controlsActive(s) ? 'ACTIVE' : 'INACTIVE'}</dd>
    <dt>Focus target</dt><dd>{s.focusTarget}</dd>
    <dt>Camera</dt><dd>{s.cameraMode}</dd><dt>Brain target</dt><dd>{s.brainFocus ?? 'Whole brain'}</dd>
    <dt>Control mode</dt><dd>{s.mode}</dd>
  </dl><strong>LIVE RENDER METRICS</strong><dl>
    <dt>FPS</dt><dd>{metrics.fps === null ? 'Awaiting WebGL' : metrics.fps.toFixed(0)}</dd>
    <dt>Visible meshes</dt><dd>{metrics.visibleMeshes}</dd><dt>Draw calls</dt><dd>{metrics.drawCalls}</dd>
    <dt>Active highlights</dt><dd>{metrics.activeHighlights}</dd>
  </dl><span>Motion: 100 ms sample, measured after collision.<br />Render: 1 s sample · instances count as one mesh.<br />Controls badge describes viewport keyboard focus; the movement pad works separately.</span></div>;
}
