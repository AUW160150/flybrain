import { beforeEach, expect, it } from 'vitest';
import { Euler, Vector3 } from 'three';
import { useStudio } from '../src/state/store';
import { avatarAnimation, wingRotation } from '../src/fly/animation';
import type { AnimationName } from '../src/data/contracts';
import { focus, key } from './support/keyboard';

const state = () => useStudio.getState();
const advance = (ms: number) => { for (let t = 0; t < ms; t += 20) state().tick(0.02); };
beforeEach(() => { useStudio.setState(useStudio.getInitialState(), true); focus(); });

// Measure the actual outer wing-vein endpoint used by ProceduralFly, in body space.
function wingTip(name: AnimationName, ms: number, side: number) {
  return new Vector3(side * 0.46, 0.01, -1.24)
    .applyEuler(new Euler(...wingRotation(name, ms, false, side)));
}

it('courtship visibly extends one wing, then refolds, without moving the physical fly', () => {
  const position = state().pose;
  key('KeyC'); advance(600);
  const animation = avatarAnimation(state());
  expect(animation.name).toBe('COURTSHIP');
  expect(wingTip(animation.name, animation.elapsedMs, 1).x - wingTip('IDLE', 0, 1).x).toBeGreaterThan(0.4);
  expect(wingTip(animation.name, animation.elapsedMs, -1)).toEqual(wingTip('IDLE', 0, -1));
  expect(wingRotation('COURTSHIP', 2400, false, 1)).toEqual(wingRotation('IDLE', 0, false, 1));
  advance(1900);
  expect(avatarAnimation(state()).name).toBe('IDLE');
  expect(state().pose).toEqual(position);
});

it('Space raises the fly, opens both wings, ignores key repeats, and lands on the next press', () => {
  key('Space'); key('Space', { repeat: true }); advance(600);
  expect(state().airborne).toBe(true);
  expect(state().pose.y).toBeGreaterThan(1.5);
  for (const side of [-1, 1]) {
    expect(Math.abs(wingTip('TAKEOFF', 600, side).x)).toBeGreaterThan(Math.abs(wingTip('IDLE', 0, side).x) + 0.2);
  }
  advance(1900);
  expect(avatarAnimation(state()).name).toBe('FLIGHT_IDLE');
  key('Space', { up: true }); key('Space'); advance(2500);
  expect(state().pose.y).toBeLessThan(0.01);
  expect(avatarAnimation(state()).name).toBe('IDLE');
  expect(state().events.map(e => e.behavior)).toEqual(['TAKEOFF', 'LAND']);
});

it('reduced motion retains a distinct static courtship pose and direct altitude control', () => {
  state().setReducedMotion(true);
  key('KeyC'); advance(400);
  expect(wingRotation('COURTSHIP', 400, true, 1)).toEqual(wingRotation('COURTSHIP', 1800, true, 1));
  expect(wingRotation('COURTSHIP', 400, true, 1)).not.toEqual(wingRotation('IDLE', 400, true, 1));
  expect(wingRotation('COURTSHIP', 400, true, -1)).toEqual(wingRotation('IDLE', 400, true, -1));
  key('Space'); advance(1000); expect(state().pose.y).toBeGreaterThan(1.6);
});

it('pausing the activity timeline does not stop takeoff or courtship', () => {
  state().toggleTimeline(); const time = state().timelineMs;
  state().command('COURTSHIP', 'POINTER'); advance(600);
  expect(avatarAnimation(state())).toEqual({ name: 'COURTSHIP', elapsedMs: 600 });
  state().command('TAKEOFF_LAND', 'POINTER'); advance(600);
  expect(state().pose.y).toBeGreaterThan(1.5);
  expect(state().timelineMs).toBe(time); expect(state().events).toEqual([]);
  expect(state().behavior?.sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
});
