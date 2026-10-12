import { describe, expect, it } from 'vitest';
import { demoPackage } from '../src/circuits/demo';
import { parseActivityFrame, parseCircuitPackage, parseCircuitText, MAX_PACKAGE_BYTES } from '../src/data/schema';

const demo = () => structuredClone(demoPackage);
// Parser fixtures only. These synthetic decimal strings are never exported as biological records.
function structuralFixture() {
  return { ...demo(), label: 'RAW_STRUCTURAL', dataset: 'TEST FIXTURE ONLY', neurons: [
    { bodyId: '90000000000000001', aliases: [], regionIds: ['display-a'], evidence: ['UNVERIFIED'], sourceRefs: ['test:fixture'] },
    { bodyId: '90000000000000002', aliases: [], regionIds: [], evidence: ['UNVERIFIED'], sourceRefs: ['test:fixture'] },
  ], edges: [{ sourceBodyId: '90000000000000001', targetBodyId: '90000000000000002', rawSynapseCount: 3, evidence: ['UNVERIFIED'], sourceRefs: ['test:fixture'] }] };
}

describe('compact circuit package boundary', () => {
  it('validates the shipped demo without manufacturing neurons or edges', () => {
    const parsed = parseCircuitPackage(demo());
    expect(parsed.neurons).toEqual([]); expect(parsed.edges).toEqual([]);
    expect(parsed.regions.every(r => r.geometryStatus === 'PLACEHOLDER_GEOMETRY')).toBe(true);
  });
  it('preserves string IDs beyond the JavaScript integer precision limit', () => {
    expect(parseCircuitPackage(structuralFixture()).neurons[0].bodyId).toBe('90000000000000001');
  });
  it.each([null, {}, { ...demo(), schemaVersion: 2 }, { ...demo(), label: 'FULL_CONNECTOME_SIMULATION' }, { ...demo(), unknown: 'silently discarded?' }])('rejects an invalid package: %j', pkg => {
    expect(() => parseCircuitPackage(pkg)).toThrow();
  });
  it('rejects malformed JSON and oversized text before parsing', () => {
    expect(() => parseCircuitText('{')).toThrow();
    expect(() => parseCircuitText(' '.repeat(MAX_PACKAGE_BYTES + 1))).toThrow(/2 MiB/);
  });
  it('rejects dangling endpoints', () => {
    const pkg = structuralFixture(); pkg.edges[0].targetBodyId = '99';
    expect(() => parseCircuitPackage(pkg)).toThrow(/endpoint/);
  });
  it('rejects duplicate body IDs and duplicate directed edges', () => {
    const pkg = structuralFixture(); pkg.neurons.push(pkg.neurons[0]);
    expect(() => parseCircuitPackage(pkg)).toThrow(/Duplicate/);
    const other = structuralFixture(); other.edges.push(other.edges[0]);
    expect(() => parseCircuitPackage(other)).toThrow(/Duplicate directed/);
  });
  it('rejects numeric IDs, negative counts, fractional counts and unknown regions', () => {
    const pkg = structuralFixture();
    expect(() => parseCircuitPackage({ ...pkg, neurons: [{ ...pkg.neurons[0], bodyId: 1 }] })).toThrow();
    for (const rawSynapseCount of [-1, 1.5, Infinity]) expect(() => parseCircuitPackage({ ...pkg, edges: [{ ...pkg.edges[0], rawSynapseCount }] })).toThrow();
    pkg.neurons[0].regionIds = ['not-in-package'];
    expect(() => parseCircuitPackage(pkg)).toThrow(/unknown region/);
  });
  it('requires sources for verified anatomy or literature annotations', () => {
    const pkg = demo(); pkg.regions[0].geometryStatus = 'VERIFIED_ANATOMY';
    expect(() => parseCircuitPackage(pkg)).toThrow(/Verified geometry/);
    pkg.regions[0].evidence = ['ANATOMY_VERIFIED'];
    expect(() => parseCircuitPackage(pkg)).toThrow(/source/);
  });
  it('rejects invented biological IDs in an educational demo', () => {
    expect(() => parseCircuitPackage({ ...structuralFixture(), label: 'EDUCATIONAL_DEMO' })).toThrow(/fabricated body IDs/);
  });
  it('keeps transmitter prediction and consensus independent', () => {
    const pkg = structuralFixture();
    const parsed = parseCircuitPackage({ ...pkg, neurons: [{ ...pkg.neurons[0], neurotransmitterPrediction: 'test-prediction', neurotransmitterConsensus: 'test-consensus' }, pkg.neurons[1]] });
    expect(parsed.neurons[0].neurotransmitterPrediction).not.toBe(parsed.neurons[0].neurotransmitterConsensus);
  });
  it('rejects complete-connectome-sized packages', () => {
    expect(() => parseCircuitPackage({ ...demo(), neurons: Array(501).fill(structuralFixture().neurons[0]) })).toThrow();
  });
});

describe('activity provenance boundary', () => {
  const frame = { timeMs: 0, sourceMode: 'USER_DRIVEN_ILLUSTRATION', values: { 'display-a': 0.7 } };
  it('preserves user provenance', () => expect(parseActivityFrame(frame).sourceMode).toBe('USER_DRIVEN_ILLUSTRATION'));
  it('supports explicitly educational frames', () => expect(parseActivityFrame({ ...frame, sourceMode: 'RULE_DRIVEN_EDUCATIONAL' }).sourceMode).toBe('RULE_DRIVEN_EDUCATIONAL'));
  it.each(['REDUCED_CIRCUIT_SIMULATION', 'FULL_CONNECTOME_SIMULATION', 'SIMULATED', 'DATA_REPLAY', 'UNVERIFIED', undefined])('refuses unsupported or missing provenance: %s', sourceMode => {
    expect(() => parseActivityFrame({ ...frame, sourceMode })).toThrow();
  });
  it.each([-0.1, 1.1, NaN, Infinity])('rejects invalid display intensity: %s', value => {
    expect(() => parseActivityFrame({ ...frame, values: { a: value } })).toThrow();
  });
});
