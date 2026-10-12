import { describe, it, expect } from 'vitest';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { parseRealPackage, parseRealPackageText, BROWSER_LIMITS, readBoundedResponse } from '../src/realdata/schema';
import { filterGraph, initialFilters, partners, realHighlights } from '../src/realdata/graph';
import { RealInspector, DatasetPanel } from '../src/realdata/RealInspector';
import { RawGraph } from '../src/realdata/RawGraph';
import { morphologySchema } from '../src/realdata/MorphologyView';
import { useStudio } from '../src/state/store';
import { createDisplayEvent } from '../src/activity/timeline';
import mappings from '../config/educational_behavior_mappings.json';

const source = (kind: string) => readFileSync('public/data/malecns/malecns-' + kind + '.json', 'utf8');
const focused = parseRealPackageText(source('focused'));
const paper = parseRealPackageText(source('paper'));
const motors = parseRealPackageText(source('motors'));
const clone = () => structuredClone(focused);
const catalog = JSON.parse(readFileSync('public/data/malecns/manifest.json', 'utf8'));

describe('generated real packages', () => {
  it.each([['focused', 110, 1923], ['paper', 102, 274], ['candidates', 12, 0], ['lb3b', 11, 43], ['lb3c', 23, 221], ['motors', 10, 29], ['sugar-selected', 0, 0], ['anatomy', 3, 0]])('%s preserves verified counts and bounded provenance', (kind, bodies, edges) => {
    const text = source(String(kind)), pkg = parseRealPackageText(text);
    const entry = catalog.packages.find((e: { id: string }) => e.id === pkg.id);
    expect(pkg.neurons).toHaveLength(Number(bodies)); expect(pkg.edges).toHaveLength(Number(edges));
    expect(Buffer.byteLength(text)).toBe(entry.bytes);
    expect(createHash('sha256').update(text).digest('hex')).toBe(entry.sha256);
    expect(entry.bytes).toBeLessThanOrEqual(BROWSER_LIMITS.maxPackageBytes);
    expect(pkg.sourceFiles.some(f => f.path === pkg.sourceRun + '/nodes.csv')).toBe(true);
    expect(pkg.simulation.status).toBe('UNAVAILABLE');
  });
  it('preserves the 957530 missing nerve and M003 disagreement without backfilling', () => {
    const node = focused.neurons.find(n => n.bodyId === '957530')!;
    expect(node.entryNerve).toBeNull();
    expect(node.unresolvedFields).toContain('entry_nerve');
    expect(node.warningIds).toContain('M003');
    expect(focused.warnings.find(w => w.id === 'M003')?.valueA).toBe('MxLbN');
  });
  it('retains divergent transmitter prediction, confidence and consensus', () => {
    const node = focused.neurons.find(n => n.bodyId === '10331')!;
    expect(node.neurotransmitterPrediction).toBe('unclear');
    expect(node.transmitterConsensus).toBe('acetylcholine');
    expect(node.predictionConfidence).toBeCloseTo(0.4896524466871221);
  });
  it('retains paper discrepancy and raw count without converting it into physiology', () => {
    const w = paper.warnings.find(w => w.id === 'M290')!;
    expect([w.valueA, w.valueB]).toEqual(['473', '478']);
    const ids = new Set(paper.neurons.filter(n => n.type === 'GNG015').map(n => n.bodyId));
    const targets = new Set(paper.neurons.filter(n => n.type === 'MN9').map(n => n.bodyId));
    expect(paper.edges.filter(e => ids.has(e.source) && targets.has(e.target)).reduce((s, e) => s + e.rawSynapseCount, 0)).toBe(478);
    expect(JSON.stringify(paper)).not.toContain('SIMULATED_ACTIVITY');
  });
  it('keeps Puddle unassigned and selected sugar empty', () => {
    expect(focused.unresolved.find(u => u.name === 'Puddle')?.bodyId).toBeNull();
    const pkg = parseRealPackageText(source('sugar-selected'));
    expect(pkg.scientificLabel).toBe('UNRESOLVED'); expect(pkg.paths).toEqual([]);
    expect(pkg.selection.validated).toBe(false);
  });
  it('keeps candidate aliases and comparison edges separate', () => {
    const pkg = parseRealPackageText(source('candidates'));
    expect(new Set(pkg.neurons.map(n => n.type))).toEqual(new Set(['GNG021', 'GNG232', 'DNg67', 'DNge080', 'GNG042', 'GNG015']));
    expect(pkg.neurons.find(n => n.type === 'GNG232')?.displayAlias).toBe('G2N-1');
    expect(pkg.edges).toEqual([]);
  });
  it('validates exact native geometry assets and parent references', () => {
    const pkg = parseRealPackageText(source('anatomy'));
    pkg.neurons.forEach(node => {
      if (node.anatomy.status !== 'SOURCE_BACKED_SWC') throw new Error('Missing geometry');
      const data = readFileSync('public' + node.anatomy.asset);
      expect(data.byteLength).toBe(node.anatomy.bytes);
      expect(createHash('sha256').update(data).digest('hex')).toBe(node.anatomy.sha256);
      const geometry = morphologySchema.parse(JSON.parse(data.toString()));
      expect(geometry.bodyId).toBe(node.bodyId);
      expect(geometry.points.length).toBe(node.anatomy.pointCount);
      expect(geometry.transformApplied).toBe(false);
    });
    expect(focused.neurons.every(n => n.anatomy.status === 'UNAVAILABLE')).toBe(true);
  });
});

describe('custom-loader scientific and safety boundaries', () => {
  it.each(['name', 'version', 'uuid'] as const)('rejects incompatible dataset %s', field => {
    const pkg = clone(); pkg.dataset[field] = field === 'uuid' ? '0'.repeat(32) : 'another';
    expect(() => parseRealPackage(pkg)).toThrow();
  });
  it.each([
    ['duplicate body', (p: typeof focused) => p.neurons.push(p.neurons[0])],
    ['dangling edge', (p: typeof focused) => { p.edges[0].target = '999999999999'; }],
    ['duplicate edge', (p: typeof focused) => p.edges.push(p.edges[0])],
    ['negative count', (p: typeof focused) => { p.edges[0].rawSynapseCount = -1; }],
    ['fractional count', (p: typeof focused) => { p.edges[0].rawSynapseCount = 1.5; }],
    ['missing source hash', (p: typeof focused) => { p.sourceFiles = []; }],
    ['missing reference', (p: typeof focused) => { p.neurons[0].sourceRefs = ['missing.csv']; }],
    ['unknown scientific label', (p: typeof focused) => { Object.assign(p, { scientificLabel: 'VERIFIED_SIMULATOR' }); }],
    ['premature selection', (p: typeof focused) => { p.scientificLabel = 'SELECTED_EFFECTIVE_CONNECTIVITY'; }],
    ['guessed Puddle', (p: typeof focused) => { p.neurons[0].aliases = ['Puddle']; }],
    ['body budget', (p: typeof focused) => { p.limits.maxNodes = 1; }],
    ['edge budget', (p: typeof focused) => { p.limits.maxEdges = 1; }],
    ['simulation data', (p: typeof focused) => { Object.assign(p.edges[0], { activationStrength: 0.8 }); }],
    ['dangling saved path', (p: typeof focused) => { p.paths[0].bodyIds = ['10331', '999999999']; }],
  ] as const)('rejects %s', (_label, change) => {
    const pkg = clone(); change(pkg); expect(() => parseRealPackage(pkg)).toThrow();
  });
  it('rejects oversized text before parsing', () => expect(() => parseRealPackageText(' '.repeat(BROWSER_LIMITS.maxPackageBytes + 1))).toThrow(/limit/));
  it('rejects bytes beyond a package-specific smaller limit', () => {
    const pkg = clone(); pkg.limits.maxPackageBytes = 100;
    expect(() => parseRealPackageText(JSON.stringify(pkg))).toThrow(/declared byte limit/);
  });
  it('rejects unbounded streamed assets and cancels the reader', async () => {
    let cancelled = false;
    const stream = new ReadableStream({ start(controller) { controller.enqueue(new Uint8Array(20)); }, cancel() { cancelled = true; } });
    await expect(readBoundedResponse(new Response(stream), 10)).rejects.toThrow(/byte limit/);
    expect(cancelled).toBe(true);
  });
  it('rejects altered morphology topology', () => {
    const pkg = parseRealPackageText(source('anatomy')), record = pkg.neurons[0].anatomy;
    if (record.status !== 'SOURCE_BACKED_SWC') throw new Error('Missing geometry');
    const geometry = JSON.parse(readFileSync('public' + record.asset, 'utf8'));
    geometry.points[0][6] = geometry.points[0][0];
    expect(() => morphologySchema.parse(geometry)).toThrow(/Cyclic/);
  });
});

describe('real data interaction adapters and rendered labels', () => {
  it('filters side and evidence while keeping edges referentially complete', () => {
    const graph = filterGraph(focused, { ...initialFilters, side: 'L', evidence: 'LITERATURE_ASSOCIATED' });
    const ids = new Set(graph.neurons.map(n => n.bodyId));
    expect(graph.neurons.every(n => n.side === 'L' && n.evidence.includes('LITERATURE_ASSOCIATED'))).toBe(true);
    expect(graph.edges.every(e => ids.has(e.source) && ids.has(e.target))).toBe(true);
  });
  it('isolates incoming, outgoing and one-hop edges without adding graph-inferred paths', () => {
    for (const isolation of ['INCOMING', 'OUTGOING', 'ONE_HOP'] as const) {
      const graph = filterGraph(focused, { ...initialFilters, selected: '15321', isolation });
      expect(graph.edges.length).toBeGreaterThan(0);
      expect(graph.edges.every(e => isolation === 'INCOMING' ? e.target === '15321' : isolation === 'OUTGOING' ? e.source === '15321' : [e.source, e.target].includes('15321'))).toBe(true);
    }
  });
  it('isolates exactly an already saved paper path', () => {
    const graph = filterGraph(paper, { ...initialFilters, isolation: 'PATH', pathIndex: 0 });
    expect(graph.neurons).toHaveLength(paper.paths[0].bodyIds.length);
    expect(graph.edges).toHaveLength(paper.paths[0].bodyIds.length - 1);
  });
  it('labels raw partners as in-package counts in the inspector', () => {
    const node = focused.neurons.find(n => n.bodyId === '957530')!;
    const html = renderToStaticMarkup(createElement(RealInspector, { pkg: focused, node, select: () => {}, isolate: () => {} }));
    for (const label of ['IN-PACKAGE ONLY', '957530', 'M003', 'UNRESOLVED', 'ANATOMY UNAVAILABLE FOR THIS BODY', 'NT body prediction', 'Transmitter consensus']) expect(html).toContain(label);
    expect(partners(focused, node.bodyId).outgoing.length).toBeGreaterThan(0);
  });
  it('shows source identity, hashes, blocked selection and simulation in dataset panel', () => {
    const html = renderToStaticMarkup(createElement(DatasetPanel, { pkg: focused, bytes: 1723513, origin: 'Test' }));
    for (const label of ['male-cns:v1.0', focused.dataset.uuid, focused.sourceFiles[0].sha256, 'UNAVAILABLE', 'Puddle']) expect(html).toContain(label);
  });
  it('keeps directional arrows, readable counts and an explicit edge cap in the graph', () => {
    const html = renderToStaticMarkup(createElement(RawGraph, { pkg: focused, neurons: focused.neurons, edges: focused.edges, selected: null, highlights: new Set<string>(), select: () => {} }));
    expect(html.match(/marker-end=/g)).toHaveLength(BROWSER_LIMITS.maxRenderedEdges);
    expect(html).toContain('300 of 1923');
    expect(html).toContain('NOT ANATOMICAL COORDINATES');
  });
  it('makes real highlights user-driven, independent of structural count and disabled for scripted playback', () => {
    const event = createDisplayEvent('test-feed', 'FEED', 0);
    const state = { ...useStudio.getInitialState(), events: [event], timelineMs: 700 };
    const before = JSON.stringify(motors);
    const result = realHighlights(motors, state);
    expect(result.bodyIds.size).toBe(10);
    expect(result.mapping?.evidence).toBe('USER_DRIVEN_ILLUSTRATION');
    expect(realHighlights(motors, { ...state, mode: 'EDUCATIONAL_RULE' }).bodyIds.size).toBe(0);
    expect(realHighlights(motors, { ...state, mode: 'DATA_REPLAY' }).bodyIds.size).toBe(0);
    expect(realHighlights(motors, { ...state, events: [createDisplayEvent('walk', 'WALK', 0)] }).bodyIds.size).toBe(0);
    expect(JSON.stringify(motors)).toBe(before);
    for (const key of ['behavior', 'circuitPackage', 'bodyIds', 'types', 'source', 'evidence', 'disclaimer', 'confidence', 'author', 'date', 'reviewStatus']) expect(mappings.mappings[0]).toHaveProperty(key);
  });
});
