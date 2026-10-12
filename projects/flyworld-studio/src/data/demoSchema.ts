import { z } from 'zod';
import type { DemoCircuitPackage, DemoTimeline, DisplayEvent } from './contracts';

const id = z.string().regex(/^demo-[a-z0-9-]+$/);
const text = z.string().min(1).max(1000);
const point = z.tuple([z.number().finite(), z.number().finite(), z.number().finite()]);
const educationalSource = z.enum(['USER_DRIVEN_ILLUSTRATION', 'RULE_DRIVEN_EDUCATIONAL']);
const entity = {
  id, name: text, roleCategory: z.enum(['VISUAL', 'TASTE', 'MOTOR', 'COURTSHIP', 'INTEGRATION']),
  description: text, geometryStatus: z.literal('PLACEHOLDER_GEOMETRY'),
  evidence: z.tuple([z.literal('UNVERIFIED')]), sourceRefs: z.array(text).min(1), position: point,
};
export const demoPackageSchema = z.strictObject({
  schemaVersion: z.literal(1), format: z.literal('FLYWORLD_EDUCATIONAL_DEMO'),
  id, label: z.literal('EDUCATIONAL_DEMO'), name: text,
  regions: z.array(z.strictObject({ ...entity, kind: z.literal('REGION'), color: z.string().regex(/^#[0-9a-fA-F]{6}$/), symbol: text, scale: point.refine(p => p.every(v => v > 0)) })).min(1).max(10),
  neurons: z.array(z.strictObject({ ...entity, kind: z.literal('DEMO_NEURON'), regionId: id })).max(64),
  relations: z.array(z.strictObject({ sourceId: id, targetId: id, kind: z.literal('ILLUSTRATIVE_RELATION'), evidence: z.tuple([z.literal('UNVERIFIED')]) })).max(128),
  circuits: z.array(z.strictObject({ id, name: text, entityIds: z.array(id).min(1) })).max(10),
  sourceRefs: z.array(text).min(1), disclaimer: text,
}).superRefine((pkg, ctx) => {
  const issue = (message: string) => ctx.addIssue({ code: 'custom', message });
  const entities = [...pkg.regions, ...pkg.neurons];
  const ids = new Set(entities.map(e => e.id));
  const regions = new Set(pkg.regions.map(e => e.id));
  const neurons = new Set(pkg.neurons.map(e => e.id));
  if (ids.size !== entities.length) issue('Duplicate demo entity ID');
  if (new Set(pkg.circuits.map(c => c.id)).size !== pkg.circuits.length) issue('Duplicate demo circuit ID');
  if (pkg.neurons.some(n => !regions.has(n.regionId))) issue('Unknown demo region');
  const pairs = new Set<string>();
  for (const relation of pkg.relations) {
    if (!neurons.has(relation.sourceId) || !neurons.has(relation.targetId)) issue('Unknown demo relation endpoint');
    const pair = `${relation.sourceId}:${relation.targetId}`;
    if (pairs.has(pair)) issue('Duplicate illustrative relation');
    pairs.add(pair);
  }
  for (const circuit of pkg.circuits) if (circuit.entityIds.some(id => !ids.has(id))) issue('Unknown circuit display entity');
});

export const displayEventSchema = z.strictObject({
  id: text, name: text, startMs: z.number().finite().nonnegative(),
  endMs: z.number().finite().nonnegative().nullable(),
  sourceMode: educationalSource, evidence: educationalSource,
  origin: z.enum(['LIVE_USER', 'SCRIPTED_RULE', 'BUNDLED_DEMO', 'SESSION_RECORDING']),
  values: z.record(id, z.number().finite().min(0).max(1)),
  behavior: z.enum(['IDLE', 'WALK', 'TURN_LEFT', 'TURN_RIGHT', 'FEED', 'GROOM', 'TAKEOFF', 'FLIGHT_IDLE', 'LAND', 'ESCAPE', 'COURTSHIP', 'STOP']),
  heldKey: z.enum(['FORWARD', 'BACKWARD', 'LEFT', 'RIGHT']).optional(), notes: text,
}).superRefine((event, ctx) => {
  if (event.endMs !== null && event.endMs <= event.startMs) ctx.addIssue({ code: 'custom', message: 'Event must end after its start' });
  if (event.evidence !== event.sourceMode) ctx.addIssue({ code: 'custom', message: 'Evidence must preserve activity provenance' });
  if (event.endMs === null && event.origin !== 'LIVE_USER') ctx.addIssue({ code: 'custom', message: 'Replay events must have finite end times' });
});

export function parseDemoPackage(input: unknown): DemoCircuitPackage { return demoPackageSchema.parse(input) as DemoCircuitPackage; }
export function parseDisplayEvent(input: unknown, allowedIds: ReadonlySet<string>): DisplayEvent {
  const event = displayEventSchema.parse(input) as DisplayEvent;
  if (Object.keys(event.values).some(id => !allowedIds.has(id))) throw new Error('Unknown activity target');
  return event;
}
export function parseDemoTimeline(input: unknown, allowedIds: ReadonlySet<string>): DemoTimeline {
  const parsed = z.strictObject({
    schemaVersion: z.literal(1), id, label: z.literal('SYNTHETIC_EDUCATIONAL_REPLAY'),
    durationMs: z.number().positive().max(120000), events: z.array(displayEventSchema).max(120), sourceRefs: z.array(text).min(1),
  }).parse(input);
  const seen = new Set<string>();
  for (const event of parsed.events) {
    parseDisplayEvent(event, allowedIds);
    if (event.endMs === null || event.endMs > parsed.durationMs) throw new Error('Replay event extends outside timeline');
    if (seen.has(event.id)) throw new Error('Duplicate replay event ID');
    seen.add(event.id);
  }
  return parsed as DemoTimeline;
}
