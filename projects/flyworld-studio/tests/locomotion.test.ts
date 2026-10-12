import { beforeEach, expect, it } from 'vitest';
import { useStudio } from '../src/state/store';
import { FLY_RADIUS, obstacles, WORLD_LIMIT } from '../src/world/collision';
import { focus, key } from './support/keyboard';
import { avatarAnimation, locomotionState } from '../src/fly/animation';

const state = () => useStudio.getState();
function reset() { useStudio.setState(useStudio.getInitialState(), true); focus(); }
beforeEach(reset);
function down(code: string, shiftKey = false) {
  return key(code, { shiftKey });
}
function advance(seconds = 1, fps = 60) { for (let i = 0; i < seconds * fps; i++) state().tick(1 / fps); }

it('holding W advances continuously from one keydown without browser repeats', () => {
  down('KeyW'); advance(2);
  expect(state().pose.z).toBeCloseTo(4.2, 8);
});
it('ArrowUp moves exactly like W', () => {
  down('KeyW'); advance(); const w = state().pose;
  reset();
  down('ArrowUp'); advance(); expect(state().pose).toEqual(w);
});
it('ArrowDown moves backward', () => {
  down('ArrowDown'); advance(); expect(state().pose.z).toBeCloseTo(-2.1);
});
it('W remains usable with Shift held', () => {
  down('KeyW', true); advance(); expect(state().pose.z).toBeGreaterThan(2);
});
it('world boundary contact is reported, with recovery after turning away', () => {
  useStudio.setState({ pose: { x: 0, y: 0, z: WORLD_LIMIT, heading: 0 } });
  down('KeyW'); advance(); expect(state().collided).toBe(true);
  expect(state().pose.z).toBe(WORLD_LIMIT);
  state().releaseMotion(); down('KeyS'); advance(); expect(state().pose.z).toBeLessThan(WORLD_LIMIT);
});
it('tree blocks penetration but never permanently disables motion', () => {
  const tree = obstacles[0];
  useStudio.setState({ pose: { x: tree.x, y: 0, z: tree.z - tree.radius - FLY_RADIUS - 0.5, heading: 0 } });
  down('KeyW'); advance(1);
  expect(state().collided).toBe(true); expect(state().motion.FORWARD).toBe(true);
  expect(Math.hypot(state().pose.x - tree.x, state().pose.z - tree.z)).toBeGreaterThanOrEqual(tree.radius + FLY_RADIUS);
  state().releaseMotion(); down('KeyS'); const before = state().pose.z; advance();
  expect(state().pose.z).toBeLessThan(before); expect(state().collided).toBe(false);
});

it.each(['KeyS', 'ArrowDown'])('%s moves backward relative to the current heading', code => {
  useStudio.setState({ pose: { x: 0, y: 0, z: 0, heading: Math.PI / 2 } });
  down(code); advance(); expect(state().pose.x).toBeCloseTo(-2.1); expect(state().pose.z).toBeCloseTo(0);
  expect(locomotionState(state())).toBe('WALK_BACKWARD');
});
it.each([['KeyA', 1], ['ArrowLeft', 1], ['KeyD', -1], ['ArrowRight', -1]] as const)('%s turns with the expected yaw sign', (code, sign) => {
  down(code); advance(); expect(state().pose.heading).toBeCloseTo(sign * 2);
  expect(state().pose.x).toBe(0); expect(state().pose.z).toBe(0);
  expect(state().turnSpeed).toBeCloseTo(sign * 2);
  expect(locomotionState(state())).toBe(sign > 0 ? 'TURN_LEFT' : 'TURN_RIGHT');
});
it('W+A curves, releasing A preserves translation, releasing W stops', () => {
  down('KeyW'); down('KeyA'); advance();
  expect(state().pose.x).toBeGreaterThan(0.5); expect(state().pose.z).toBeGreaterThan(0.5); expect(state().pose.heading).toBeCloseTo(2);
  expect(locomotionState(state())).toBe('WALK_TURN');
  key('KeyA', { up: true }); const heading = state().pose.heading; advance(0.5);
  expect(state().pose.heading).toBe(heading); expect(locomotionState(state())).toBe('WALK_FORWARD');
  key('KeyW', { up: true }); const pose = state().pose; advance();
  expect(state().pose).toEqual(pose); expect(locomotionState(state())).toBe('IDLE');
});
it('measures collision blocking and turns away while still holding forward', () => {
  const tree = obstacles[0];
  useStudio.setState({ pose: { x: tree.x, y: 0, z: tree.z - tree.radius - FLY_RADIUS - 0.1, heading: 0 } });
  down('KeyW'); advance(); expect(locomotionState(state())).toBe('COLLISION_BLOCKED');
  expect(state().forwardSpeed).toBeCloseTo(0, 3); expect(avatarAnimation(state()).name).toBe('IDLE');
  down('KeyA'); const blocked = state().pose; advance(1.5);
  expect(state().pose.heading).toBeCloseTo(3); expect(Math.hypot(state().pose.x - blocked.x, state().pose.z - blocked.z)).toBeGreaterThan(0.5);
  expect(state().collided).toBe(false); expect(locomotionState(state())).toBe('WALK_TURN');
});
it('pauses in brain inspection and requires a fresh press after returning', () => {
  down('KeyW'); advance(); state().setCamera('BRAIN_INSPECTION'); const pose = state().pose;
  down('KeyW'); advance(); expect(state().pose).toEqual(pose);
  expect(locomotionState(state())).toBe('BRAIN_INSPECTION_PAUSED'); expect(state().forwardSpeed).toBe(0);
  state().setCamera('WORLD_FOLLOW'); key('KeyW', { repeat: true }); advance(); expect(state().pose).toEqual(pose);
  key('KeyW', { up: true }); down('KeyW'); advance(); expect(state().pose.z).toBeGreaterThan(pose.z);
});
it('applies Shift boost while held and restores normal speed on release', () => {
  down('KeyW'); advance(0.5); expect(state().forwardSpeed).toBeCloseTo(2.1);
  down('ShiftLeft'); advance(0.5); expect(state().forwardSpeed).toBeCloseTo(2.1 * 1.75);
  down('ShiftRight'); key('ShiftLeft', { up: true }); advance(0.1); expect(state().forwardSpeed).toBeCloseTo(2.1 * 1.75);
  key('ShiftRight', { up: true }); advance(0.1); expect(state().forwardSpeed).toBeCloseTo(2.1);
});
it.each([false, true])('agrees at 30, 60, 120 FPS (turning: %s)', turning => {
  const poses = [30, 60, 120].map(fps => {
    reset(); down('KeyW'); if (turning) down('KeyA'); advance(2, fps); return state().pose;
  });
  for (const pose of poses.slice(1)) for (const axis of ['x', 'y', 'z', 'heading'] as const) expect(pose[axis]).toBeCloseTo(poses[0][axis], 9);
});
it('shows movement above a prior gesture, takeoff/flight/landing, and source labels', () => {
  down('KeyF'); down('KeyW'); advance(0.1); expect(avatarAnimation(state()).name).toBe('WALK');
  down('Space'); advance(0.5); expect(locomotionState(state())).toBe('FLY'); expect(avatarAnimation(state()).name).toBe('TAKEOFF');
  down('Space'); advance(3); expect(locomotionState(state())).toBe('IDLE');
  expect(state().controls.every(e => e.sourceMode === 'USER_DRIVEN_ILLUSTRATION')).toBe(true);
  expect(state().events.every(e => e.sourceMode === 'USER_DRIVEN_ILLUSTRATION')).toBe(true);
});
