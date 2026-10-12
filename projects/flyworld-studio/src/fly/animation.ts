import type { AnimationName } from '../data/contracts';
import type { StudioState } from '../state/store';
import { behaviorAt } from '../activity/timeline';

export type LocomotionState = 'IDLE' | 'WALK_FORWARD' | 'WALK_BACKWARD' | 'TURN_LEFT' | 'TURN_RIGHT' | 'WALK_TURN' | 'FLY' | 'COLLISION_BLOCKED' | 'BRAIN_INSPECTION_PAUSED' | 'FLY_INSPECTION_PAUSED' | 'REPLAY_IN_PLACE' | 'RULE_IN_PLACE';
/** Measured movement after collision, distinct from authored behavior/replay gestures. */
export function locomotionState(state: StudioState): LocomotionState {
  if (state.cameraMode === 'BRAIN_INSPECTION') return 'BRAIN_INSPECTION_PAUSED';
  if (state.cameraMode === 'FLY_INSPECTION') return 'FLY_INSPECTION_PAUSED';
  if (state.mode !== 'USER_CONTROL') return state.mode === 'DATA_REPLAY' ? 'REPLAY_IN_PLACE' : 'RULE_IN_PLACE';
  const moving = Math.abs(state.forwardSpeed) > 0.001;
  const turning = Math.abs(state.turnSpeed) > 0.001;
  if (state.collided && !moving && state.motion.FORWARD !== state.motion.BACKWARD) return 'COLLISION_BLOCKED';
  if (state.airborne || state.pose.y > 0.02) return 'FLY';
  if (moving && turning) return 'WALK_TURN';
  if (moving) return state.forwardSpeed > 0 ? 'WALK_FORWARD' : 'WALK_BACKWARD';
  if (turning) return state.turnSpeed > 0 ? 'TURN_LEFT' : 'TURN_RIGHT';
  return 'IDLE';
}

/** Behavior commands and replay gestures are separate from activity intensity. */
export function avatarAnimation(state: StudioState): { name: AnimationName; elapsedMs: number } {
  if (state.mode !== 'USER_CONTROL') return behaviorAt(state.events, state.timelineMs);
  const movement = locomotionState(state);
  // New movement takes visual priority over a still-timed feeding/grooming gesture.
  if (movement === 'WALK_FORWARD' || movement === 'WALK_BACKWARD' || movement === 'WALK_TURN') return { name: 'WALK', elapsedMs: state.animationMs * (state.forwardSpeed < 0 ? -1 : 1) };
  if (movement === 'TURN_LEFT' || movement === 'TURN_RIGHT') return { name: movement, elapsedMs: state.animationMs };
  if (movement === 'COLLISION_BLOCKED') return { name: Math.abs(state.turnSpeed) > 0.001 ? state.turnSpeed > 0 ? 'TURN_LEFT' : 'TURN_RIGHT' : 'IDLE', elapsedMs: state.animationMs };
  if (state.behavior) return { name: state.behavior.name as AnimationName, elapsedMs: state.behaviorElapsedMs };
  const name: AnimationName = movement === 'FLY' ? 'FLIGHT_IDLE' : 'IDLE';
  return { name, elapsedMs: state.animationMs };
}

export function animationPose(name: AnimationName, elapsedMs: number, reducedMotion: boolean) {
  const t = elapsedMs / 1000;
  const progress = Math.min(1, elapsedMs / 2400);
  const walking = name === 'WALK' || name === 'TURN_LEFT' || name === 'TURN_RIGHT';
  const flight = ['TAKEOFF', 'FLIGHT_IDLE', 'LAND'].includes(name);
  return {
    gait: reducedMotion ? 0 : walking ? Math.sin(t * 11) : 0,
    groom: name === 'GROOM' ? reducedMotion ? 0.5 : Math.sin(t * 13) : 0,
    wing: reducedMotion ? flight ? 0.6 : name === 'COURTSHIP' ? 0.8 : 0.12
      : flight ? 0.55 + Math.sin(t * 30) * 0.4 : name === 'COURTSHIP' ? 0.9 + Math.sin(t * 6) * 0.2 : 0.12,
    proboscis: name === 'FEED' ? reducedMotion ? 1.8 : 1.65 + Math.sin(t * 8) * 0.18 : 0.4,
    hop: !reducedMotion && name === 'ESCAPE' ? Math.sin(progress * Math.PI) * 0.7 : 0,
    idleBob: !reducedMotion && name === 'IDLE' ? Math.sin(t * 1.8) * 0.008 : 0,
  };
}

/** Authored placeholder poses, not measured wing kinematics or a biological model. */
export function wingRotation(name: AnimationName, elapsedMs: number, reducedMotion: boolean, side: number): [number, number, number] {
  const pose = animationPose(name, elapsedMs, reducedMotion);
  const flight = name === 'TAKEOFF' || name === 'FLIGHT_IDLE' || name === 'LAND';
  if (flight) return [0, side * -0.95, side * pose.wing];
  if (name === 'COURTSHIP' && side === 1) {
    // Extend one wing laterally; gently unfold/refold within the timed gesture.
    const envelope = reducedMotion ? 1 : Math.max(0, Math.min(1, elapsedMs / 250, (2400 - elapsedMs) / 300));
    return [0, -0.35 - 0.95 * envelope, 0.12 + pose.wing * 0.18 * envelope];
  }
  return [0, side * -0.35, side * 0.12];
}
