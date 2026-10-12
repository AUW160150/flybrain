import { beforeEach, describe, expect, it } from 'vitest';
import { useStudio } from '../src/state/store';
import { emptyMotion, initialPose, integrateMotion } from '../src/fly/motion';
import { createDisplayEvent, intensityAt } from '../src/activity/timeline';
import { avatarAnimation } from '../src/fly/animation';
import type { BehaviorCommand, CameraMode, DemoId } from '../src/data/contracts';
import { resolveCollision } from '../src/world/collision';

beforeEach(() => useStudio.setState(useStudio.getInitialState(), true));
const state = () => useStudio.getState();
function advance(ms: number) { for (let i = 0; i < ms / 20; i++) state().tick(0.02); }

describe('explicit user controls', () => {
  it('records motion press/release with provenance and a held display span', () => {
    state().setMotion('FORWARD', true); advance(100); state().setMotion('FORWARD', false);
    expect(state().pose.z).toBeGreaterThan(0);
    expect(state().controls.map(e => e.phase)).toEqual(['PRESS', 'RELEASE']);
    expect(state().controls.every(e => e.controlMode === 'USER' && e.sourceMode === 'USER_DRIVEN_ILLUSTRATION')).toBe(true);
    expect(state().events[0].sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
    expect(state().events[0].endMs).toBe(550);
  });
  it.each<BehaviorCommand>(['FEED', 'GROOM', 'ESCAPE', 'COURTSHIP', 'TAKEOFF_LAND', 'STOP'])('never applies a simulation label to %s', command => {
    state().command(command, 'KEYBOARD');
    expect(state().behavior?.sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
    expect(state().behavior?.circuitIds).toEqual([]);
    expect(state().events.at(-1)?.sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
    advance(2500); expect(state().behavior).toBeNull(); expect(state().behaviorHistory[0].endedAtMs).toBeDefined();
  });
  it('separates takeoff, flight idle, landing, and idle transitions', () => {
    state().command('TAKEOFF_LAND'); expect(avatarAnimation(state()).name).toBe('TAKEOFF');
    advance(2500); expect(avatarAnimation(state()).name).toBe('FLIGHT_IDLE'); expect(state().pose.y).toBeGreaterThan(1.6);
    state().command('TAKEOFF_LAND'); expect(avatarAnimation(state()).name).toBe('LAND');
    advance(2500); expect(avatarAnimation(state()).name).toBe('IDLE'); expect(state().pose.y).toBeLessThan(0.01);
  });
  it('stop closes held display spans and releases locomotion', () => {
    state().setMotion('FORWARD', true); advance(100); state().command('STOP');
    expect(state().motion).toEqual(emptyMotion()); expect(state().events[0].endMs).toBe(550);
  });
  it('releases held controls on focus loss', () => {
    state().setMotion('FORWARD', true); state().setMotion('LEFT', true); state().releaseMotion();
    const before = state().pose; advance(100); expect(state().pose).toEqual(before);
  });
  it('pauses activity independently from physical motion and suppresses paused overlays', () => {
    state().setMotion('FORWARD', true); advance(300); state().toggleTimeline();
    const time = state().timelineMs, z = state().pose.z;
    const intensity = intensityAt(state().events, 'demo-motor-system', time);
    advance(500); expect(state().timelineMs).toBe(time); expect(state().pose.z).toBeGreaterThan(z);
    expect(intensityAt(state().events, 'demo-motor-system', state().timelineMs)).toBe(intensity);
    const count = state().events.length; state().command('GROOM'); expect(state().events).toHaveLength(count);
  });
  it('rejects unsupported provenance, unknown targets, and future/duplicate live events', () => {
    const event = createDisplayEvent('accepted', 'FEED', 0);
    for (const bad of [{ ...event, sourceMode: 'FULL_CONNECTOME_SIMULATION' }, { ...event, values: { 'demo-unknown': 1 } }, { ...event, startMs: 100 }, { ...event, sourceMode: 'RULE_DRIVEN_EDUCATIONAL', evidence: 'RULE_DRIVEN_EDUCATIONAL' }]) expect(() => state().acceptDisplayEvent(bad)).toThrow();
    state().acceptDisplayEvent(event);
    expect(() => state().acceptDisplayEvent(event)).toThrow(/Duplicate/);
  });
  it('bounds event and behavior history', () => {
    for (let i = 0; i < 180; i++) state().command('FEED');
    expect(state().controls).toHaveLength(40); expect(state().events).toHaveLength(120); expect(state().behaviorHistory).toHaveLength(30);
    expect(new Set(state().events.map(e => e.id)).size).toBe(120);
  });
});

describe('mode switching and replay', () => {
  it('runs educational rules without moving the physical fly or accepting user gestures', () => {
    state().setMode('EDUCATIONAL_RULE'); const pose = state().pose;
    state().setMotion('FORWARD', true); state().command('FEED'); advance(500);
    expect(state().pose).toEqual(pose); expect(state().behavior).toBeNull();
    expect(state().events.every(e => e.sourceMode === 'RULE_DRIVEN_EDUCATIONAL')).toBe(true);
    expect(avatarAnimation(state()).name).toBe('WALK');
  });
  it('closes active keys before switching mode and does not resume stale inputs', () => {
    state().setMotion('FORWARD', true); advance(300); state().setMode('EDUCATIONAL_RULE'); state().setMode('USER_CONTROL');
    expect(state().motion).toEqual(emptyMotion()); expect(state().events[0].endMs).not.toBeNull();
  });
  it('scrubbing a user session selects its replay and preserves user origin labels', () => {
    state().command('FEED'); advance(1000); const pose = state().pose;
    state().seek(500);
    expect(state().mode).toBe('DATA_REPLAY'); expect(state().replaySource).toBe('SESSION'); expect(state().timelinePaused).toBe(true);
    expect(state().events[0].sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
    expect(state().events[0].origin).toBe('SESSION_RECORDING');
    expect(avatarAnimation(state()).name).toBe('FEED'); expect(state().pose).toEqual(pose);
    state().setMode('USER_CONTROL'); expect(state().timelineMs).toBe(1000);
  });
  it('replays bundled synthetic data, scrubs in both directions, and applies speed', () => {
    state().setMode('DATA_REPLAY'); expect(state().timelinePaused).toBe(true);
    state().seek(6000); expect(avatarAnimation(state()).name).toBe('FEED');
    state().seek(500); expect(avatarAnimation(state()).name).toBe('WALK');
    state().setPlaybackSpeed(2); state().toggleTimeline(); advance(500); expect(state().timelineMs).toBe(1500);
    expect(state().events.every(e => e.origin === 'BUNDLED_DEMO' && e.sourceMode === 'RULE_DRIVEN_EDUCATIONAL')).toBe(true);
  });
  it('clamps scrubbing, ignores invalid speed, and stops at replay end', () => {
    state().setMode('DATA_REPLAY'); state().seek(Infinity); expect(state().timelineMs).toBe(0);
    state().seek(-100); expect(state().timelineMs).toBe(0);
    state().setPlaybackSpeed(999); expect(state().playbackSpeed).toBe(1);
    state().seek(state().timelineDurationMs - 10); state().toggleTimeline(); advance(100);
    expect(state().timelineMs).toBe(state().timelineDurationMs); expect(state().timelinePaused).toBe(true);
  });
  it('loops a fixed rule tour with bounded event count', () => {
    state().setMode('EDUCATIONAL_RULE'); const count = state().events.length; const duration = state().timelineDurationMs;
    advance(duration + 300); expect(state().timelineMs).toBeCloseTo(300); expect(state().events).toHaveLength(count);
  });
  it('clears and resets replay without deleting the session recording', () => {
    state().command('GROOM'); state().setMode('DATA_REPLAY'); state().clearTimeline();
    expect(state().events).toHaveLength(0); expect(state().sessionEvents).toHaveLength(1); expect(state().timelinePaused).toBe(true);
    state().resetTimeline(); expect(state().events.length).toBeGreaterThan(0); expect(state().timelineMs).toBe(0);
    state().setMode('USER_CONTROL'); state().resetTimeline(); expect(state().sessionEvents).toHaveLength(0); expect(state().timelinePaused).toBe(false);
  });
});

describe('camera and layers', () => {
  it.each<CameraMode>(['WORLD_FOLLOW', 'WORLD_ORBIT'])('returns through inspection to the previous %s', world => {
    state().setCamera(world); state().setCamera('BRAIN_INSPECTION'); state().setCamera('FLY_INSPECTION'); state().backToWorld();
    expect(state().cameraMode).toBe(world);
  });
  it.each<CameraMode>(['BRAIN_INSPECTION', 'FLY_INSPECTION'])('pauses locomotion in %s', mode => {
    state().setMotion('FORWARD', true); state().setCamera(mode); const pose = state().pose;
    state().setMotion('FORWARD', true); state().command('ESCAPE'); advance(500);
    expect(state().pose).toEqual(pose); expect(state().motion).toEqual(emptyMotion());
  });
  it('preserves the transparent-head preference', () => {
    state().setCamera('BRAIN_INSPECTION'); state().backToWorld(); expect(state().transparentHead).toBe(false);
    state().toggleHead(); state().setCamera('BRAIN_INSPECTION'); state().backToWorld(); expect(state().transparentHead).toBe(true);
  });
  it('selects/focuses a generic node, isolates its region, and restores the whole brain', () => {
    state().selectEntity('demo-taste-01'); state().focusEntity('demo-taste-01');
    expect(state().cameraMode).toBe('BRAIN_INSPECTION'); expect(state().brainFocus).toBe('demo-taste-01');
    state().isolateRegion('demo-taste-system'); expect(Object.values(state().layers).filter(l => l.visible)).toHaveLength(1);
    state().setLayer('demo-taste-system', { opacity: 0.7 }); expect(state().layers['demo-taste-system'].opacity).toBe(0.7);
    state().resetBrain(); expect(Object.values(state().layers).every(l => l.visible)).toBe(true); expect(state().brainFocus).toBeNull();
  });
  it('bounds opacity and ignores unknown selections/layers', () => {
    state().setLayer('demo-taste-system', { opacity: 2 }); expect(state().layers['demo-taste-system'].opacity).toBe(0.85);
    state().selectEntity('demo-unknown' as DemoId); expect(state().selectedEntity).toBeNull();
    state().setLayer('demo-unknown', { visible: false }); expect(state().layers['demo-unknown']).toBeUndefined();
  });
  it('reduced motion preserves event provenance and uses a stable visible envelope', () => {
    state().command('FEED'); state().setReducedMotion(true); advance(500);
    expect(intensityAt(state().events, 'demo-taste-system', state().timelineMs, true)).toBe(1);
    expect(state().events[0].sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
  });
});

describe('physical motion', () => {
  it('opposing inputs cancel and turning changes heading', () => {
    expect(integrateMotion(initialPose(), { ...emptyMotion(), FORWARD: true, BACKWARD: true }, 0.02, false, false)).toEqual(initialPose());
    expect(integrateMotion(initialPose(), { ...emptyMotion(), LEFT: true }, 0.02, false, false).heading).toBeGreaterThan(0);
  });
  it('caps time jumps and bounds the world', () => {
    expect(integrateMotion(initialPose(), { ...emptyMotion(), FORWARD: true }, 100, false, false).z).toBeLessThan(0.2);
    const edge = { ...initialPose(), z: 11 };
    expect(resolveCollision(edge, integrateMotion(edge, { ...emptyMotion(), FORWARD: true }, 0.05, false, false)).pose.z).toBe(11);
  });
});
