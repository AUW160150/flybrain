import { create } from 'zustand';
import type { AnimationName, BehaviorCommand, BehaviorEvent, CameraMode, ControlEvent, DemoId, DisplayEvent, ExplorationMode, FlyPose, MotionInput, MotionKey, WorldCameraMode } from '../data/contracts';
import { emptyMotion, initialPose, integrateMotion } from '../fly/motion';
import { resolveCollision } from '../world/collision';
import { educationalPackage, entityById, demoIds } from '../circuits/demo';
import { bundledTimeline, closeHeldEvents, createDisplayEvent, EVENT_LIMIT, makeRuleTimeline, recordingForReplay } from '../activity/timeline';
import { parseDisplayEvent } from '../data/demoSchema';
import { aggregateMotion, boosted, isInputKey } from '../controls/input';

export const isInspection = (mode: CameraMode) => mode === 'BRAIN_INSPECTION' || mode === 'FLY_INSPECTION';
type InputOrigin = ControlEvent['input'];
export interface RegionLayer { visible: boolean; opacity: number }
const defaultLayers = () => Object.fromEntries(educationalPackage.regions.map(r => [r.id, { visible: true, opacity: 0.26 }])) as Record<DemoId, RegionLayer>;
export interface StudioState {
  cameraMode: CameraMode;
  returnMode: WorldCameraMode;
  cameraRevision: number;
  brainFocus: DemoId | null;
  transparentHead: boolean;
  pose: FlyPose;
  motion: MotionInput;
  pressedKeys: ReadonlySet<string>;
  padMotion: MotionInput;
  viewportFocused: boolean;
  focusTarget: string;
  forwardSpeed: number;
  turnSpeed: number;
  airborne: boolean;
  collided: boolean;
  behavior: BehaviorEvent | null;
  behaviorElapsedMs: number;
  animationMs: number;
  behaviorHistory: BehaviorEvent[];
  controls: ControlEvent[];
  nextEventId: number;
  mode: ExplorationMode;
  replaySource: 'BUNDLED' | 'SESSION';
  events: DisplayEvent[];
  sessionEvents: DisplayEvent[];
  liveTimeMs: number;
  timelineMs: number;
  timelineDurationMs: number;
  timelinePaused: boolean;
  playbackSpeed: number;
  selectedEntity: DemoId | null;
  hoveredEntity: DemoId | null;
  layers: Record<DemoId, RegionLayer>;
  reducedMotion: boolean;
  showDebug: boolean;
  rendererStatus: 'LOADING' | 'READY' | 'UNAVAILABLE';
  setCamera: (mode: CameraMode, input?: InputOrigin) => void;
  backToWorld: (input?: InputOrigin) => void;
  toggleHead: (input?: InputOrigin) => void;
  setMotion: (key: MotionKey, down: boolean, input?: InputOrigin) => void;
  setPressedKey: (code: string, down: boolean) => void;
  setControlsFocus: (focused: boolean, target: string) => void;
  releaseMotion: () => void;
  command: (command: BehaviorCommand, input?: InputOrigin) => void;
  setMode: (mode: ExplorationMode) => void;
  setReplaySource: (source: 'BUNDLED' | 'SESSION') => void;
  toggleTimeline: (input?: InputOrigin) => void;
  seek: (timeMs: number) => void;
  setPlaybackSpeed: (speed: number) => void;
  clearTimeline: () => void;
  resetTimeline: () => void;
  selectEntity: (id: DemoId | null) => void;
  hoverEntity: (id: DemoId | null) => void;
  focusEntity: (id: DemoId | null) => void;
  setLayer: (id: DemoId, patch: Partial<RegionLayer>) => void;
  isolateRegion: (id: DemoId) => void;
  resetBrain: () => void;
  setReducedMotion: (value: boolean) => void;
  acceptDisplayEvent: (event: unknown) => void;
  tick: (deltaSeconds: number) => void;
}

const logControl = (state: StudioState, command: string, input: InputOrigin, phase: ControlEvent['phase'] = 'PRESS') => ({
  controls: [...state.controls, {
    id: `control-${state.nextEventId}`, timeMs: state.timelineMs, controlMode: 'USER' as const,
    sourceMode: 'USER_DRIVEN_ILLUSTRATION' as const, command, phase, input,
  }].slice(-40), nextEventId: state.nextEventId + 1,
});
const durationOf = (events: readonly DisplayEvent[], now = 0) => Math.max(1000, now, ...events.map(e => e.endMs ?? now));
const closedUserEvents = (s: StudioState) => s.mode === 'USER_CONTROL' ? closeHeldEvents(s.events, s.timelineMs) : s.sessionEvents;
const motionAnimation = (key: MotionKey): AnimationName => key === 'LEFT' ? 'TURN_LEFT' : key === 'RIGHT' ? 'TURN_RIGHT' : 'WALK';
export const controlsActive = (s: Pick<StudioState, 'viewportFocused' | 'cameraMode' | 'mode'>) => s.viewportFocused && s.mode === 'USER_CONTROL' && !isInspection(s.cameraMode);
const clearedInput = () => ({ motion: emptyMotion(), padMotion: emptyMotion(), pressedKeys: new Set<string>(), forwardSpeed: 0, turnSpeed: 0, collided: false });
function updateMotion(s: StudioState, motion: MotionInput, input: InputOrigin) {
  let next = s;
  for (const key of Object.keys(motion) as MotionKey[]) {
    if (s.motion[key] === motion[key]) continue;
    let events = next.events;
    if (motion[key] && !s.timelinePaused) {
      const event = { ...createDisplayEvent(`user-${next.nextEventId}`, motionAnimation(key), s.timelineMs, 'USER_DRIVEN_ILLUSTRATION', null), heldKey: key };
      events = [...events, event].slice(-EVENT_LIMIT);
    } else if (!motion[key]) events = closeHeldEvents(events, s.timelineMs, key);
    next = { ...next, events, sessionEvents: events, ...logControl(next, key, input, motion[key] ? 'PRESS' : 'RELEASE') };
  }
  return { ...next, motion,
    forwardSpeed: motion.FORWARD === motion.BACKWARD ? 0 : next.forwardSpeed,
    turnSpeed: motion.LEFT === motion.RIGHT ? 0 : next.turnSpeed,
    collided: Object.values(motion).some(Boolean) && next.collided,
  };
}

export const useStudio = create<StudioState>((set, get) => ({
  cameraMode: 'WORLD_FOLLOW', returnMode: 'WORLD_FOLLOW', cameraRevision: 0, brainFocus: null, transparentHead: false,
  pose: initialPose(), ...clearedInput(), viewportFocused: false, focusTarget: 'No world focus', airborne: false,
  behavior: null, behaviorElapsedMs: 0, animationMs: 0, behaviorHistory: [], controls: [], nextEventId: 1,
  mode: 'USER_CONTROL', replaySource: 'BUNDLED', events: [], sessionEvents: [], liveTimeMs: 0,
  timelineMs: 0, timelineDurationMs: 10000, timelinePaused: false, playbackSpeed: 1,
  selectedEntity: null, hoveredEntity: null, layers: defaultLayers(), reducedMotion: false, showDebug: false,
  rendererStatus: 'LOADING',
  setCamera: (mode, input = 'POINTER') => set(s => {
    const sessionEvents = closedUserEvents(s);
    return {
      cameraMode: mode, cameraRevision: s.cameraRevision + 1, hoveredEntity: null,
      brainFocus: mode === 'BRAIN_INSPECTION' ? s.brainFocus : null,
      returnMode: !isInspection(mode) ? mode : !isInspection(s.cameraMode) ? s.cameraMode : s.returnMode,
      ...clearedInput(), sessionEvents,
      events: s.mode === 'USER_CONTROL' ? sessionEvents : s.events,
      ...logControl(s, `CAMERA:${mode}`, input),
    };
  }),
  backToWorld: (input = 'POINTER') => get().setCamera(get().returnMode, input),
  toggleHead: (input = 'POINTER') => set(s => ({ transparentHead: !s.transparentHead, hoveredEntity: null, ...logControl(s, 'TRANSPARENT_HEAD', input) })),
  setMotion: (key, down, input = 'KEYBOARD') => set(s => {
    if (s.mode !== 'USER_CONTROL' || (down && isInspection(s.cameraMode)) || s.padMotion[key] === down) return s;
    const padMotion = { ...s.padMotion, [key]: down };
    return { ...updateMotion(s, aggregateMotion(s.pressedKeys, padMotion), input), padMotion };
  }),
  setPressedKey: (code, down) => set(s => {
    if (!isInputKey(code) || (down && !controlsActive(s)) || s.pressedKeys.has(code) === down) return s;
    const pressedKeys = new Set(s.pressedKeys);
    if (down) pressedKeys.add(code); else pressedKeys.delete(code);
    return { ...updateMotion(s, aggregateMotion(pressedKeys, s.padMotion), 'KEYBOARD'), pressedKeys };
  }),
  setControlsFocus: (viewportFocused, focusTarget) => {
    if (!viewportFocused && get().viewportFocused) get().releaseMotion();
    set({ viewportFocused, focusTarget });
  },
  releaseMotion: () => set(s => ({ ...updateMotion(s, emptyMotion(), 'KEYBOARD'), ...clearedInput() })),
  command: (command, input = 'POINTER') => set(s => {
    if (s.mode !== 'USER_CONTROL' || isInspection(s.cameraMode)) return s;
    const name: AnimationName = command === 'TAKEOFF_LAND' ? (s.airborne ? 'LAND' : 'TAKEOFF') : command;
    const event: BehaviorEvent = { id: `behavior-${s.nextEventId}`, name, startedAtMs: s.timelineMs, sourceMode: 'USER_DRIVEN_ILLUSTRATION', circuitIds: [] };
    const history = s.behavior ? [...s.behaviorHistory, { ...s.behavior, endedAtMs: s.timelineMs }].slice(-30) : s.behaviorHistory;
    let events = closeHeldEvents(s.events, s.timelineMs);
    if (!s.timelinePaused) events = [...events, createDisplayEvent(`user-${s.nextEventId}`, name, s.timelineMs)].slice(-EVENT_LIMIT);
    return {
      airborne: command === 'TAKEOFF_LAND' ? !s.airborne : s.airborne, ...clearedInput(),
      behavior: event, behaviorHistory: history, behaviorElapsedMs: 0, events, sessionEvents: events,
      timelineDurationMs: Math.max(s.timelineDurationMs, durationOf(events)), ...logControl(s, command, input),
    };
  }),
  setMode: mode => set(s => {
    const sessionEvents = closedUserEvents(s);
    const script = mode === 'EDUCATIONAL_RULE' ? makeRuleTimeline() : bundledTimeline;
    const events = mode === 'USER_CONTROL' ? sessionEvents : mode === 'DATA_REPLAY' && s.replaySource === 'SESSION' ? recordingForReplay(sessionEvents, s.liveTimeMs) : script.events;
    return {
      mode, ...clearedInput(), behavior: null, behaviorElapsedMs: 0, sessionEvents, events,
      timelineMs: mode === 'USER_CONTROL' ? s.liveTimeMs : 0,
      timelineDurationMs: mode === 'USER_CONTROL' || (mode === 'DATA_REPLAY' && s.replaySource === 'SESSION') ? durationOf(events, s.liveTimeMs) : script.durationMs,
      timelinePaused: mode === 'DATA_REPLAY', playbackSpeed: 1,
      ...logControl(s, `MODE:${mode}`, 'POINTER'),
    };
  }),
  setReplaySource: replaySource => { set({ replaySource }); get().setMode('DATA_REPLAY'); },
  toggleTimeline: (input = 'POINTER') => set(s => ({
    timelinePaused: !s.timelinePaused,
    timelineMs: s.mode !== 'USER_CONTROL' && s.timelineMs >= s.timelineDurationMs && s.timelinePaused ? 0 : s.timelineMs,
    ...logControl(s, 'PAUSE_TIMELINE', input),
  })),
  seek: timeMs => {
    if (!Number.isFinite(timeMs)) return;
    if (get().mode === 'USER_CONTROL') { set({ replaySource: 'SESSION' }); get().setMode('DATA_REPLAY'); }
    set(s => ({ timelineMs: Math.max(0, Math.min(s.timelineDurationMs, timeMs)), timelinePaused: true, ...clearedInput() }));
  },
  setPlaybackSpeed: speed => { if ([0.25, 0.5, 1, 1.5, 2].includes(speed)) set({ playbackSpeed: speed }); },
  clearTimeline: () => set(s => ({
    events: [], timelineMs: 0, timelineDurationMs: 10000, timelinePaused: true, ...clearedInput(), behavior: null,
    ...(s.mode === 'USER_CONTROL' ? { sessionEvents: [], liveTimeMs: 0, controls: [] } : {}),
  })),
  resetTimeline: () => {
    if (get().mode === 'USER_CONTROL') { get().clearTimeline(); set({ timelinePaused: false }); }
    else { const mode = get().mode; get().setMode(mode); set({ timelinePaused: true }); }
  },
  selectEntity: id => { if (id === null || entityById.has(id)) set({ selectedEntity: id }); },
  hoverEntity: id => { if (id === null || entityById.has(id)) set({ hoveredEntity: id }); },
  focusEntity: id => {
    if (id !== null && !entityById.has(id)) return;
    get().setCamera('BRAIN_INSPECTION');
    const entity = id ? entityById.get(id) : null;
    const regionId = entity?.kind === 'REGION' ? id : educationalPackage.neurons.find(n => n.id === id)?.regionId;
    if (regionId) get().setLayer(regionId, { visible: true });
    set(s => ({ brainFocus: id, selectedEntity: id ?? s.selectedEntity, cameraRevision: s.cameraRevision + 1 }));
  },
  setLayer: (id, patch) => set(s => {
    if (!s.layers[id]) return s;
    const opacity = patch.opacity === undefined ? s.layers[id].opacity : Number.isFinite(patch.opacity) ? Math.max(0.08, Math.min(0.85, patch.opacity)) : s.layers[id].opacity;
    return { layers: { ...s.layers, [id]: { visible: patch.visible ?? s.layers[id].visible, opacity } }, hoveredEntity: null };
  }),
  isolateRegion: id => set(s => !s.layers[id] ? s : ({ layers: Object.fromEntries(Object.entries(s.layers).map(([key, value]) => [key, { ...value, visible: key === id }])) as Record<DemoId, RegionLayer>, hoveredEntity: null })),
  resetBrain: () => { set({ layers: defaultLayers(), brainFocus: null, hoveredEntity: null }); get().focusEntity(null); },
  setReducedMotion: reducedMotion => set({ reducedMotion }),
  acceptDisplayEvent: input => {
    const event = parseDisplayEvent(input, demoIds);
    if (event.startMs > get().timelineMs) throw new Error('Future live event is not allowed');
    if (get().mode !== 'USER_CONTROL' || event.sourceMode !== 'USER_DRIVEN_ILLUSTRATION' || event.origin !== 'LIVE_USER') throw new Error('Live event provenance must remain user driven');
    set(s => {
      if (s.events.some(e => e.id === event.id)) throw new Error('Duplicate event ID');
      const events = [...s.events, event].slice(-EVENT_LIMIT);
      return { events, sessionEvents: events };
    });
  },
  tick: deltaSeconds => set(s => {
    if (!Number.isFinite(deltaSeconds)) return s;
    const dt = Math.min(Math.max(deltaSeconds, 0), 0.05);
    let timelineMs = s.timelineMs + (s.timelinePaused ? 0 : dt * 1000 * s.playbackSpeed);
    let timelinePaused = s.timelinePaused;
    if (s.mode === 'EDUCATIONAL_RULE' && s.events.length) timelineMs %= s.timelineDurationMs;
    else if (s.mode !== 'USER_CONTROL' && timelineMs >= s.timelineDurationMs) { timelineMs = s.timelineDurationMs; timelinePaused = true; }
    const physicalPaused = isInspection(s.cameraMode) || s.mode !== 'USER_CONTROL';
    const elapsed = s.behaviorElapsedMs + (physicalPaused ? 0 : dt * 1000);
    const finished = !!s.behavior && elapsed >= (s.behavior.name === 'STOP' ? 100 : 2400);
    const desired = integrateMotion(s.pose, s.motion, dt, s.airborne, physicalPaused, boosted(s.pressedKeys));
    const collision = physicalPaused ? { pose: s.pose, collided: false } : resolveCollision(s.pose, desired);
    const middleHeading = (s.pose.heading + collision.pose.heading) / 2;
    const forwardSpeed = dt > 0 ? ((collision.pose.x - s.pose.x) * Math.sin(middleHeading) + (collision.pose.z - s.pose.z) * Math.cos(middleHeading)) / dt : 0;
    return {
      pose: collision.pose, collided: collision.collided, timelineMs, timelinePaused,
      forwardSpeed, turnSpeed: dt > 0 ? (collision.pose.heading - s.pose.heading) / dt : 0,
      liveTimeMs: s.mode === 'USER_CONTROL' ? timelineMs : s.liveTimeMs,
      timelineDurationMs: s.mode === 'USER_CONTROL' ? Math.max(s.timelineDurationMs, timelineMs) : s.timelineDurationMs,
      animationMs: s.animationMs + (physicalPaused ? 0 : dt * 1000),
      behaviorElapsedMs: elapsed, behavior: finished ? null : s.behavior,
      behaviorHistory: finished ? [...s.behaviorHistory, { ...s.behavior!, endedAtMs: timelineMs }].slice(-30) : s.behaviorHistory,
    };
  }),
}));
