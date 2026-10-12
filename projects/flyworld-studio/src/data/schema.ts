import { z } from 'zod';
import type { CircuitPackage, ActivityFrame } from './contracts';

const text = z.string().trim().min(1).max(1000);
const bodyId = z.string().regex(/^[1-9]\d*$/, 'Body IDs must be positive decimal strings');
const evidence = z.array(z.enum([
  'ANATOMY_VERIFIED', 'LITERATURE_SUPPORTED', 'STRUCTURAL_CANDIDATE',
  'USER_DRIVEN_ILLUSTRATION', 'RULE_DRIVEN_EDUCATIONAL', 'DATA_REPLAY', 'SIMULATED', 'UNVERIFIED',
])).min(1).max(8);
const sourceRefs = z.array(text).max(100);
const region = z.strictObject({
  id: text, name: text, role: text.optional(), evidence, sourceRefs,
  geometryStatus: z.enum(['VERIFIED_ANATOMY', 'PLACEHOLDER_GEOMETRY', 'UNAVAILABLE']),
});
const neuron = z.strictObject({
  bodyId, type: text.optional(), aliases: z.array(text).max(100),
  side: z.enum(['L', 'R', 'M', 'UNKNOWN']).optional(), role: text.optional(),
  regionIds: z.array(text).max(100), neurotransmitterPrediction: text.optional(),
  neurotransmitterConsensus: text.optional(), evidence, sourceRefs,
});
const edge = z.strictObject({
  sourceBodyId: bodyId, targetBodyId: bodyId,
  rawSynapseCount: z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER).optional(),
  evidence, sourceRefs,
});

export const circuitPackageSchema = z.strictObject({
  schemaVersion: z.literal(1), id: text, name: text, dataset: text,
  datasetVersion: text, datasetUuid: text.optional(),
  label: z.enum(['RAW_STRUCTURAL', 'PAPER_ASSOCIATED', 'CANDIDATE', 'SELECTED_EFFECTIVE_CONNECTIVITY', 'EDUCATIONAL_DEMO']),
  neurons: z.array(neuron).max(500), edges: z.array(edge).max(5000), regions: z.array(region).max(100),
  metadata: z.record(z.string(), z.unknown()),
}).superRefine((pkg, ctx) => {
  const issue = (message: string) => ctx.addIssue({ code: 'custom', message });
  const ids = new Set(pkg.neurons.map(n => n.bodyId));
  const regions = new Set(pkg.regions.map(r => r.id));
  if (ids.size !== pkg.neurons.length) issue('Duplicate neuron body ID');
  if (regions.size !== pkg.regions.length) issue('Duplicate region ID');
  const pairs = new Set<string>();
  pkg.edges.forEach(e => {
    if (!ids.has(e.sourceBodyId) || !ids.has(e.targetBodyId)) issue('Edge endpoint is missing from the package');
    const pair = `${e.sourceBodyId}:${e.targetBodyId}`;
    if (pairs.has(pair)) issue('Duplicate directed edge');
    pairs.add(pair);
  });
  pkg.neurons.forEach(n => n.regionIds.forEach(id => {
    if (!regions.has(id)) issue('Neuron references an unknown region');
  }));
  [...pkg.neurons, ...pkg.edges, ...pkg.regions].forEach(record => {
    if (record.evidence.some(e => ['ANATOMY_VERIFIED', 'LITERATURE_SUPPORTED'].includes(e)) && !record.sourceRefs.length) {
      issue('Verified anatomy and literature annotations require source references');
    }
  });
  pkg.regions.forEach(r => {
    if (r.geometryStatus === 'VERIFIED_ANATOMY' && (!r.evidence.includes('ANATOMY_VERIFIED') || !r.sourceRefs.length)) {
      issue('Verified geometry requires anatomy evidence and sources');
    }
  });
  if (pkg.label === 'EDUCATIONAL_DEMO' && (pkg.neurons.length || pkg.edges.length)) {
    issue('Foundation demos use display regions only; never fabricated body IDs or synapse counts');
  }
  if (pkg.label !== 'EDUCATIONAL_DEMO' && [...pkg.neurons, ...pkg.edges].some(r => !r.sourceRefs.length)) {
    issue('Biological records require source references; schema validation does not verify their claims');
  }
});

export const MAX_PACKAGE_BYTES = 2 * 1024 * 1024;
export function parseCircuitPackage(input: unknown): CircuitPackage {
  return circuitPackageSchema.parse(input);
}
export function parseCircuitText(json: string): CircuitPackage {
  if (new TextEncoder().encode(json).byteLength > MAX_PACKAGE_BYTES) throw new Error('Package exceeds the 2 MiB foundation limit');
  return parseCircuitPackage(JSON.parse(json));
}

/** Reserved simulator/replay modes are intentionally rejected at this MVP boundary. */
export const activityFrameSchema = z.strictObject({
  timeMs: z.number().finite().nonnegative(),
  sourceMode: z.enum(['USER_DRIVEN_ILLUSTRATION', 'RULE_DRIVEN_EDUCATIONAL']),
  values: z.record(text, z.number().finite().min(0).max(1)),
  notes: text.optional(),
});
export function parseActivityFrame(input: unknown): ActivityFrame {
  return activityFrameSchema.parse(input);
}
