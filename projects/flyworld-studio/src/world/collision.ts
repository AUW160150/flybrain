import type { FlyPose } from '../data/contracts';

export interface WorldObstacle { id: string; name: string; x: number; z: number; radius: number; height: number }
// Mesh placement and collision use the same definitions. Units are arbitrary game units.
export const WORLD_LIMIT = 11;
export const FLY_RADIUS = 0.78;
export const obstacles: readonly WorldObstacle[] = [
  { id: 'tree', name: 'Tree obstacle', x: -3.2, z: 2.6, radius: 0.95, height: 4.1 },
  { id: 'food', name: 'Flower / food marker', x: 2.8, z: 3.1, radius: 0.65, height: 1.55 },
  { id: 'landmark', name: 'Neutral landmark', x: 3.7, z: -2.8, radius: 0.65, height: 1.3 },
];

export function resolveCollision(previous: FlyPose, desired: FlyPose, world: readonly WorldObstacle[] = obstacles): { pose: FlyPose; collided: boolean } {
  const pose = { ...desired, x: Math.max(-WORLD_LIMIT, Math.min(WORLD_LIMIT, desired.x)), z: Math.max(-WORLD_LIMIT, Math.min(WORLD_LIMIT, desired.z)) };
  let collided = pose.x !== desired.x || pose.z !== desired.z;
  // A swept horizontal check prevents crossing an obstacle even on a large proposed step.
  for (const object of world) {
    if (Math.min(previous.y, pose.y) > object.height + 0.1) continue;
    const radius = object.radius + FLY_RADIUS;
    const dx = pose.x - previous.x, dz = pose.z - previous.z;
    const lengthSquared = dx * dx + dz * dz;
    const t = lengthSquared ? Math.max(0, Math.min(1, ((object.x - previous.x) * dx + (object.z - previous.z) * dz) / lengthSquared)) : 0;
    const cx = previous.x + t * dx - object.x, cz = previous.z + t * dz - object.z;
    const endX = pose.x - object.x, endZ = pose.z - object.z;
    const distance = Math.hypot(endX, endZ);
    const startDistance = Math.hypot(previous.x - object.x, previous.z - object.z);
    if (lengthSquared > 0 && startDistance >= radius && cx * cx + cz * cz < radius * radius) {
      // First contact on the swept segment; never project a large step through to the far side.
      const fx = previous.x - object.x, fz = previous.z - object.z;
      const b = 2 * (fx * dx + fz * dz);
      const c = fx * fx + fz * fz - radius * radius;
      const enter = Math.max(0, (-b - Math.sqrt(Math.max(0, b * b - 4 * lengthSquared * c))) / (2 * lengthSquared) - 0.001);
      pose.x = previous.x + enter * dx; pose.z = previous.z + enter * dz;
      collided = true;
    } else if (distance < radius) {
      const normalX = distance > 1e-8 ? endX / distance : 1;
      const normalZ = distance > 1e-8 ? endZ / distance : 0;
      pose.x = object.x + normalX * (radius + 0.001);
      pose.z = object.z + normalZ * (radius + 0.001);
      collided = true;
    }
  }
  return { pose, collided };
}
