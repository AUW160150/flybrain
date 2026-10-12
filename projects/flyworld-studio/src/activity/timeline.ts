import type { AnimationName, DemoId, DemoTimeline, DisplayEvent, ImplementedSourceMode } from '../data/contracts';
import { behaviorTargets, demoIds } from '../circuits/demo';
import { parseDemoTimeline, parseDisplayEvent } from '../data/demoSchema';
import bundled from '../../public/data/demo/timeline.json';

export const EVENT_LIMIT = 120;
export const DEFAULT_EVENT_MS = 2400;
export const bundledTimeline = parseDemoTimeline(bundled, demoIds);

export function createDisplayEvent(
  id: string, behavior: AnimationName, startMs: number,
  sourceMode: ImplementedSourceMode = 'USER_DRIVEN_ILLUSTRATION', endMs: number | null = startMs + DEFAULT_EVENT_MS,
): DisplayEvent {
  return parseDisplayEvent({
    id, name: behavior.replaceAll('_', ' '), behavior, startMs, endMs, sourceMode, evidence: sourceMode,
    origin: sourceMode === 'USER_DRIVEN_ILLUSTRATION' ? 'LIVE_USER' : 'SCRIPTED_RULE',
    values: Object.fromEntries(behaviorTargets[behavior].map(target => [target, 1])),
    notes: 'Explicit educational display mapping. Not measured neural activity, reconstructed anatomy, or a validated functional circuit.',
  }, demoIds);
}

export function makeRuleTimeline(): DemoTimeline {
  const behaviors: AnimationName[] = ['WALK', 'TURN_LEFT', 'TURN_RIGHT', 'FEED', 'GROOM', 'ESCAPE', 'COURTSHIP'];
  return {
    schemaVersion: 1, id: 'demo-rule-tour', label: 'SYNTHETIC_EDUCATIONAL_REPLAY', durationMs: behaviors.length * 2800,
    sourceRefs: ['src/activity/timeline.ts:makeRuleTimeline'],
    events: behaviors.map((behavior, i) => createDisplayEvent(`rule-${i}`, behavior, i * 2800, 'RULE_DRIVEN_EDUCATIONAL')),
  };
}

/** A bounded visual envelope. Reduced motion removes periodic modulation, retaining gentle fades. */
export function eventIntensity(event: DisplayEvent, target: string, timeMs: number, reducedMotion = false): number {
  const value = event.values[target as DemoId] ?? 0;
  if (!value || timeMs < event.startMs || (event.endMs !== null && timeMs >= event.endMs)) return 0;
  const age = timeMs - event.startMs;
  const attack = Math.min(1, age / 240);
  const release = event.endMs === null ? 1 : Math.min(1, (event.endMs - timeMs) / 450);
  const pulse = reducedMotion ? 1 : 0.86 + 0.14 * Math.sin(age * Math.PI * 2 / 1200);
  return Math.max(0, Math.min(1, value * attack * release * pulse));
}

/** Strongest visible event wins; never average or overwrite its provenance. */
export function sampleTarget(events: readonly DisplayEvent[], target: string, timeMs: number, reducedMotion = false) {
  let value = 0;
  let event: DisplayEvent | null = null;
  for (const candidate of events) {
    const next = eventIntensity(candidate, target, timeMs, reducedMotion);
    if (next > value) { value = next; event = candidate; }
  }
  return { value, event };
}

export function latestRelevantEvent(events: readonly DisplayEvent[], target: string, timeMs: number) {
  let latest: DisplayEvent | null = null;
  for (const event of events) if (target in event.values && event.startMs <= timeMs && (!latest || event.startMs >= latest.startMs)) latest = event;
  return latest;
}

export function intensityAt(events: readonly DisplayEvent[], target: string, timeMs: number, reducedMotion = false): number {
  let value = 0;
  for (const event of events) value = Math.max(value, eventIntensity(event, target, timeMs, reducedMotion));
  return value;
}

export function behaviorAt(events: readonly DisplayEvent[], timeMs: number): { name: AnimationName; elapsedMs: number } {
  let selected: DisplayEvent | undefined;
  for (const event of events) if (event.startMs <= timeMs && (event.endMs === null || timeMs < event.endMs) && (!selected || event.startMs >= selected.startMs)) selected = event;
  return selected ? { name: selected.behavior, elapsedMs: timeMs - selected.startMs } : { name: 'IDLE', elapsedMs: 0 };
}

export function closeHeldEvents(events: readonly DisplayEvent[], timeMs: number, heldKey?: string): DisplayEvent[] {
  return events.map(event => event.endMs === null && (!heldKey || event.heldKey === heldKey)
    ? { ...event, endMs: Math.max(event.startMs + 1, timeMs + 450) } : event);
}

export function recordingForReplay(events: readonly DisplayEvent[], timeMs: number): DisplayEvent[] {
  return closeHeldEvents(events, timeMs).map(event => ({ ...event, origin: 'SESSION_RECORDING' }));
}
