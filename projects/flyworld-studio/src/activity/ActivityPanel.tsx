import { useEffect, useState } from 'react';
import { useShallow } from 'zustand/react/shallow';
import { useStudio, isInspection } from '../state/store';
import { educationalPackage } from '../circuits/demo';
import { intensityAt } from './timeline';
import type { BehaviorCommand } from '../data/contracts';

const behaviors: { command: BehaviorCommand; name: string; key: string }[] = [
  { command: 'TAKEOFF_LAND', name: 'Take off', key: 'SPACE' },
  { command: 'FEED', name: 'Feed', key: 'F' }, { command: 'GROOM', name: 'Groom', key: 'G' },
  { command: 'ESCAPE', name: 'Escape animation', key: 'E' },
  { command: 'COURTSHIP', name: 'Courtship', key: 'C' }, { command: 'STOP', name: 'Stop', key: 'X' },
];
const gestureLabels: Record<string, string> = {
  TAKEOFF: 'Taking off', LAND: 'Landing', COURTSHIP: 'Courtship wing display',
  FEED: 'Feeding gesture', GROOM: 'Grooming gesture', ESCAPE: 'Escape gesture', STOP: 'Stopped',
};
export function useTelemetry() {
  const [sample, setSample] = useState(() => useStudio.getState());
  useEffect(() => { const timer = window.setInterval(() => setSample(useStudio.getState()), 100); return () => clearInterval(timer); }, []);
  return sample;
}

export function ActivityPanel({ worldVisible = true, showWorld }: { worldVisible?: boolean; showWorld?: () => void }) {
  const sample = useTelemetry();
  // Sample advancing display time, but never use an old sample to control inputs.
  // Mode switches, paused seeks and transport edits must render synchronously.
  const transport = useStudio(useShallow(state => ({
    mode: state.mode, timelinePaused: state.timelinePaused, playbackSpeed: state.playbackSpeed,
    cameraMode: state.cameraMode, airborne: state.airborne, behavior: state.behavior, reducedMotion: state.reducedMotion,
    replaySource: state.replaySource, events: state.events,
    timelineMs: state.timelinePaused ? state.timelineMs : null,
    timelineDurationMs: state.mode === 'USER_CONTROL' ? null : state.timelineDurationMs,
  })));
  const s = { ...sample, ...transport, timelineMs: transport.timelineMs ?? sample.timelineMs,
    timelineDurationMs: transport.timelineDurationMs ?? sample.timelineDurationMs };
  const paused = s.timelinePaused;
  const last = s.controls.at(-1);
  const blocked = !worldVisible ? 'Open the world to see and control the fly.'
    : isInspection(s.cameraMode) ? 'Inspection pauses behavior commands.'
    : s.mode !== 'USER_CONTROL' ? 'Replay and rule modes pause user behavior commands.' : null;
  const gesture = s.behavior ? gestureLabels[s.behavior.name] : s.airborne ? 'Hovering' : 'Ready';
  const enableBehaviors = () => {
    if (showWorld) showWorld();
    else useStudio.getState().backToWorld();
    useStudio.getState().setMode('USER_CONTROL');
  };
  return <section className="activity-panel" aria-label="Activity and behavior controls">
    <div className="behavior-row"><span className="eyebrow">BEHAVIORS</span><div className="behavior-buttons">{behaviors.map(b => <button key={b.command} disabled={!!blocked} aria-describedby="behavior-guidance" data-active={b.command === 'TAKEOFF_LAND' ? s.airborne : s.behavior?.name === b.command} onClick={() => useStudio.getState().command(b.command)}>
      {b.command === 'TAKEOFF_LAND' && s.airborne ? 'Land' : b.name}<kbd>{b.key}</kbd>
    </button>)}</div><span className="animation-note">Scripted educational gestures</span></div>
    <div className="behavior-feedback">
      <span id="behavior-guidance">{blocked ?? 'Click the viewport for shortcuts: Space takes off / lands; C plays courtship.'}</span>
      {blocked ? <button onClick={enableBehaviors}>Enable behavior controls</button> : <span data-testid="behavior-status" aria-live="polite">{gesture} · USER_DRIVEN_ILLUSTRATION{s.reducedMotion ? ' · Reduced motion: static wing poses' : ''}</span>}
    </div>
    <div className="timeline-row">
      <button className="pause-button" onClick={() => useStudio.getState().toggleTimeline()} aria-label={paused ? 'Play activity timeline' : 'Pause activity timeline'}>{paused ? '▶' : 'Ⅱ'}</button>
      <div className="timeline-clock"><span className="eyebrow">{s.mode === 'USER_CONTROL' ? 'SESSION RECORDING' : s.mode === 'DATA_REPLAY' ? 'DATA REPLAY · DEMO' : 'EDUCATIONAL RULE'}</span><strong data-testid="timeline-time">{(s.timelineMs / 1000).toFixed(1)}<small> / {(s.timelineDurationMs / 1000).toFixed(1)} s</small></strong></div>
      <div className="scrubber"><div className="timeline-events" aria-hidden="true">{s.events.map(event => <span key={event.id} style={{ left: `${event.startMs / s.timelineDurationMs * 100}%`, width: `${Math.max(0.3, ((event.endMs ?? s.timelineMs) - event.startMs) / s.timelineDurationMs * 100)}%` }} />)}</div>
        <input type="range" min={0} max={s.timelineDurationMs} step={20} value={s.timelineMs} onInput={e => useStudio.getState().seek(e.currentTarget.valueAsNumber)} aria-label="Activity timeline position" aria-valuetext={`${(s.timelineMs / 1000).toFixed(1)} seconds`} />
        <span>{s.mode === 'USER_CONTROL' ? 'Scrub to review this session; physical controls pause during review.' : 'Synthetic demo events · gestures replay in place'}</span>
      </div>
      <label className="speed-control">Speed<select aria-label="Playback speed" value={s.playbackSpeed} onChange={e => useStudio.getState().setPlaybackSpeed(Number(e.target.value))}>{[0.25, 0.5, 1, 1.5, 2].map(speed => <option key={speed} value={speed}>{speed}×</option>)}</select></label>
      <div className="timeline-actions"><button onClick={() => useStudio.getState().resetTimeline()}>Reset</button><button onClick={() => useStudio.getState().clearTimeline()}>Clear</button></div>
    </div>
    <div className="timeline-details"><div className="system-meters">{educationalPackage.regions.map(r => <div key={r.id} title={`${r.name}: illustrative intensity`}><span>{r.symbol}</span><meter min={0} max={1} value={intensityAt(s.events, r.id, s.timelineMs, s.reducedMotion)} aria-label={`${r.name} intensity`} /></div>)}</div>
      <span className="small muted">Normalized display intensity [0, 1] · never a firing rate</span>
      {s.mode === 'DATA_REPLAY' && <label className="replay-source">Replay source<select aria-label="Replay source" value={s.replaySource} onChange={e => useStudio.getState().setReplaySource(e.target.value as 'BUNDLED' | 'SESSION')}><option value="BUNDLED">Bundled synthetic demo</option><option value="SESSION">My session recording</option></select></label>}
    </div>
    <div className="activity-footer"><span data-testid="last-control">{last ? `${last.command} / ${last.phase} · ${last.sourceMode}` : 'Ready for input · CONTROL MODE: USER'}</span><span>{s.events.length} / 120 events · original provenance retained</span></div>
  </section>;
}
