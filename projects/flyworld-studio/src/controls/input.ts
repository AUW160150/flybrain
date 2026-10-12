import type { MotionInput, MotionKey } from '../data/contracts';

export const motionKeys: Readonly<Record<string, MotionKey>> = {
  KeyW: 'FORWARD', ArrowUp: 'FORWARD', KeyS: 'BACKWARD', ArrowDown: 'BACKWARD',
  KeyA: 'LEFT', ArrowLeft: 'LEFT', KeyD: 'RIGHT', ArrowRight: 'RIGHT',
};
export const isBoostKey = (code: string) => code === 'ShiftLeft' || code === 'ShiftRight';
export const isInputKey = (code: string) => !!motionKeys[code] || isBoostKey(code);
export const boosted = (keys: ReadonlySet<string>) => keys.has('ShiftLeft') || keys.has('ShiftRight');

/** Keep physical aliases and the movement pad independent until aggregation. */
export function aggregateMotion(keys: ReadonlySet<string>, pad: MotionInput): MotionInput {
  const motion = { ...pad };
  for (const code of keys) if (motionKeys[code]) motion[motionKeys[code]] = true;
  return motion;
}
