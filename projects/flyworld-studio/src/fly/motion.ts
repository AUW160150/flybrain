import type { FlyPose, MotionInput } from '../data/contracts';

export const emptyMotion = (): MotionInput => ({ FORWARD: false, BACKWARD: false, LEFT: false, RIGHT: false });
export const initialPose = (): FlyPose => ({ x: 0, y: 0, z: 0, heading: 0 });

/** Display-world units only: neither calibrated kinematics nor neural output. */
export function integrateMotion(pose: FlyPose, input: MotionInput, dt: number, airborne: boolean, paused: boolean, boost = false): FlyPose {
  if (paused || !Number.isFinite(dt)) return pose;
  const step = Math.min(Math.max(dt, 0), 0.05);
  const turn = (Number(input.LEFT) - Number(input.RIGHT)) * step * 2;
  const heading = pose.heading + turn;
  const speed = (Number(input.FORWARD) - Number(input.BACKWARD)) * (airborne ? 3.6 : 2.1) * (boost ? 1.75 : 1);
  // Exact constant-speed arc: combined walking/turning agrees across frame rates.
  const halfTurn = turn / 2;
  const distance = speed * step * (Math.abs(halfTurn) < 1e-8 ? 1 : Math.sin(halfTurn) / halfTurn);
  return {
    heading,
    // Collision owns all clamping so boundary contact remains observable.
    x: pose.x + Math.sin(pose.heading + halfTurn) * distance,
    z: pose.z + Math.cos(pose.heading + halfTurn) * distance,
    y: pose.y + ((airborne ? 1.65 : 0) - pose.y) * (1 - Math.exp(-step * 5)),
  };
}
