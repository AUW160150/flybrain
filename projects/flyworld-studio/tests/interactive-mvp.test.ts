import { describe, expect, it } from 'vitest';
import { behaviorTargets, educationalPackage, demoIds, relationsForEntity } from '../src/circuits/demo';
import { parseDemoPackage, parseDemoTimeline, parseDisplayEvent } from '../src/data/demoSchema';
import { bundledTimeline, createDisplayEvent, eventIntensity, sampleTarget, behaviorAt } from '../src/activity/timeline';
import { resolveCollision, obstacles, FLY_RADIUS, WORLD_LIMIT } from '../src/world/collision';
import { initialPose } from '../src/fly/motion';
import { animationPose } from '../src/fly/animation';
import { readFileSync } from 'node:fs';

const pkg = () => structuredClone(educationalPackage);
describe('educational package contracts', () => {
  it.each(['visual', 'taste', 'motor', 'mating', 'central'])('validates the standalone %s demo package', name => {
    const data = JSON.parse(readFileSync(`public/data/demo/circuits/${name}.json`, 'utf8'));
    expect(parseDemoPackage(data).id).toBe(`demo-${name}-package`);
    expect(data.neurons.every((n: { id: string; bodyId?: string }) => n.id.startsWith('demo-') && !n.bodyId)).toBe(true);
  });
  it('ships five placeholder categories and only generic IDs without fabricated biology', () => {
    const demo = parseDemoPackage(pkg()); expect(demo.regions).toHaveLength(5); expect(demo.neurons).toHaveLength(13);
    for (const entity of [...demo.regions, ...demo.neurons]) {
      expect(entity.id).toMatch(/^demo-/); expect(entity.geometryStatus).toBe('PLACEHOLDER_GEOMETRY');
      expect(entity.evidence).toEqual(['UNVERIFIED']); expect(entity).not.toHaveProperty('bodyId');
      expect(entity).not.toHaveProperty('neurotransmitterPrediction');
    }
    expect(demo.relations.every(r => r.kind === 'ILLUSTRATIVE_RELATION')).toBe(true);
  });
  it('rejects decimal body IDs, anatomy claims, and synapse fields in demo records', () => {
    const original = pkg();
    for (const invalid of [{ ...original.neurons[0], id: '12345' }, { ...original.neurons[0], bodyId: '12345' }, { ...original.neurons[0], geometryStatus: 'VERIFIED_ANATOMY' }]) {
      expect(() => parseDemoPackage({ ...original, neurons: [invalid] })).toThrow();
    }
    expect(() => parseDemoPackage({ ...original, relations: [{ ...original.relations[0], rawSynapseCount: 10 }] })).toThrow();
  });
  it('rejects dangling and duplicate demo relationships and identity references', () => {
    const demo = pkg();
    expect(() => parseDemoPackage({ ...demo, neurons: [...demo.neurons, demo.neurons[0]] })).toThrow(/Duplicate/);
    expect(() => parseDemoPackage({ ...demo, relations: [{ ...demo.relations[0], targetId: 'demo-missing' }] })).toThrow(/endpoint/);
    expect(() => parseDemoPackage({ ...demo, relations: [...demo.relations, demo.relations[0]] })).toThrow(/Duplicate/);
    expect(() => parseDemoPackage({ ...demo, circuits: [{ ...demo.circuits[0], entityIds: ['demo-missing'] }] })).toThrow(/Unknown/);
  });
  it('maps user behaviors to explicit educational target sets', () => {
    expect(behaviorTargets.WALK).toContain('demo-motor-system');
    expect(behaviorTargets.TURN_LEFT).toContain('demo-motor-left-01'); expect(behaviorTargets.TURN_LEFT).not.toContain('demo-motor-right-01');
    expect(behaviorTargets.TURN_RIGHT).toContain('demo-motor-right-01');
    expect(behaviorTargets.FEED).toEqual(expect.arrayContaining(['demo-taste-system', 'demo-feed-motor-01']));
    expect(behaviorTargets.ESCAPE).toEqual(expect.arrayContaining(['demo-visual-system', 'demo-escape-motor-01']));
    expect(behaviorTargets.GROOM).toContain('demo-grooming-01'); expect(behaviorTargets.COURTSHIP).toContain('demo-mating-system');
    for (const targets of Object.values(behaviorTargets)) for (const target of targets) expect(demoIds.has(target)).toBe(true);
  });
  it('exposes neuron relations and system-boundary relations separately', () => {
    expect(relationsForEntity('demo-taste-01').downstream).toEqual(['demo-taste-02']);
    expect(relationsForEntity('demo-taste-system').downstream).toEqual(['demo-feed-motor-01']);
    expect(relationsForEntity('demo-taste-system').upstream).toEqual([]);
  });
});

describe('timed activity and replay provenance', () => {
  it('validates the bundled replay as synthetic with original educational source labels', () => {
    expect(parseDemoTimeline(bundledTimeline, demoIds).label).toBe('SYNTHETIC_EDUCATIONAL_REPLAY');
    expect(bundledTimeline.events.every(e => e.origin === 'BUNDLED_DEMO' && e.sourceMode === 'RULE_DRIVEN_EDUCATIONAL')).toBe(true);
  });
  it.each(['FULL_CONNECTOME_SIMULATION', 'REDUCED_CIRCUIT_SIMULATION', 'DATA_REPLAY', undefined])('refuses %s as an educational activation origin', sourceMode => {
    expect(() => parseDisplayEvent({ ...createDisplayEvent('test', 'FEED', 0), sourceMode }, demoIds)).toThrow();
  });
  it('rejects mismatched evidence, inverted time, unbounded replay, and unknown targets', () => {
    const event = createDisplayEvent('test', 'FEED', 100);
    for (const bad of [{ ...event, evidence: 'RULE_DRIVEN_EDUCATIONAL' }, { ...event, endMs: 50 }, { ...event, endMs: null, origin: 'BUNDLED_DEMO' }, { ...event, values: { 'demo-missing': 1 } }]) expect(() => parseDisplayEvent(bad, demoIds)).toThrow();
    expect(() => parseDemoTimeline({ ...bundledTimeline, durationMs: 100 }, demoIds)).toThrow(/outside/);
  });
  it.each([-1, 1.01, Infinity, NaN])('rejects normalized activity value %s', value => {
    expect(() => parseDisplayEvent({ ...createDisplayEvent('test', 'FEED', 0), values: { 'demo-taste-01': value } }, demoIds)).toThrow();
  });
  it('fades from zero, has a bounded pulse, fades out, and produces no future activity', () => {
    const event = createDisplayEvent('test', 'FEED', 1000);
    expect(eventIntensity(event, 'demo-taste-system', 999)).toBe(0);
    expect(eventIntensity(event, 'demo-taste-system', 1000)).toBe(0);
    expect(eventIntensity(event, 'demo-taste-system', 1120, true)).toBeCloseTo(0.5);
    expect(eventIntensity(event, 'demo-taste-system', 1500, true)).toBe(1);
    expect(eventIntensity(event, 'demo-taste-system', 3175, true)).toBeCloseTo(0.5);
    expect(eventIntensity(event, 'demo-taste-system', 3400)).toBe(0);
    for (let t = 0; t < 5000; t += 13) { const value = eventIntensity(event, 'demo-taste-system', t); expect(value).toBeGreaterThanOrEqual(0); expect(value).toBeLessThanOrEqual(1); }
  });
  it('retains the winning event provenance when activity overlaps', () => {
    const user = createDisplayEvent('user', 'FEED', 0);
    const rule = { ...createDisplayEvent('rule', 'FEED', 0, 'RULE_DRIVEN_EDUCATIONAL'), values: { 'demo-taste-system': 0.25 } };
    expect(sampleTarget([rule, user], 'demo-taste-system', 600, true).event?.sourceMode).toBe('USER_DRIVEN_ILLUSTRATION');
    expect(behaviorAt([user], 2500).name).toBe('IDLE');
  });
  it('reconstructs gestures deterministically when scrubbing backward', () => {
    expect(behaviorAt(bundledTimeline.events, 6100).name).toBe('FEED');
    const a = sampleTarget(bundledTimeline.events, 'demo-taste-system', 6100);
    sampleTarget(bundledTimeline.events, 'demo-taste-system', 15000);
    expect(sampleTarget(bundledTimeline.events, 'demo-taste-system', 6100)).toEqual(a);
  });
  it('reduces optional movement without removing gesture states', () => {
    for (const t of [500, 750, 1000]) {
      expect(animationPose('WALK', t, true).gait).toBe(0); expect(animationPose('ESCAPE', t, true).hop).toBe(0);
      expect(animationPose('FEED', t, true).proboscis).toBe(1.8); expect(animationPose('COURTSHIP', t, true).wing).toBe(0.8);
    }
  });
});

describe('game physics collision', () => {
  it.each(obstacles)('blocks movement through $name, including large swept steps', object => {
    const before = { ...initialPose(), x: object.x - 4, z: object.z };
    const after = { ...before, x: object.x + 4 };
    const result = resolveCollision(before, after, [object]);
    expect(result.collided).toBe(true); expect(result.pose.x).toBeLessThan(object.x);
    expect(Math.hypot(result.pose.x - object.x, result.pose.z - object.z)).toBeGreaterThanOrEqual(object.radius + FLY_RADIUS);
  });
  it('resolves a landing overlap and allows flight above a short object', () => {
    const object = obstacles[2];
    const above = { ...initialPose(), x: object.x, z: object.z, y: 2 };
    const landing = resolveCollision(above, { ...above, y: 0 }, [object]);
    expect(landing.collided).toBe(true);
    expect(Math.hypot(landing.pose.x - object.x, landing.pose.z - object.z)).toBeGreaterThan(object.radius);
    expect(resolveCollision({ ...above, x: object.x - 4 }, { ...above, x: object.x + 4 }, [object]).collided).toBe(false);
  });
  it('keeps world boundaries and free-space motion deterministic', () => {
    expect(resolveCollision(initialPose(), { ...initialPose(), x: 99 }, []).pose.x).toBe(WORLD_LIMIT);
    expect(resolveCollision(initialPose(), { ...initialPose(), z: 1 }, []).pose.z).toBe(1);
  });
});
