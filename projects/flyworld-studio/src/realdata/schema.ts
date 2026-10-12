import { z } from 'zod';
import limits from '../../config/browser_limits.json';
import lock from '../../config/malecns_source_lock.json';

export const BROWSER_LIMITS = limits;
export const DATASET = { name: lock.dataset, version: lock.version, uuid: lock.uuid } as const;
export const SCIENTIFIC_LABELS = ['RAW_STRUCTURAL', 'PAPER_ASSOCIATED', 'CANDIDATE', 'SELECTED_EFFECTIVE_CONNECTIVITY', 'ANATOMY_ONLY', 'UNRESOLVED'] as const;
const text = z.string().min(1).max(20000);
const optionalText = text.nullable();
const bodyId = z.string().regex(/^[1-9][0-9]*$/, 'Body ID must be a positive decimal string');
const hash = z.string().regex(/^[a-f0-9]{64}$/, 'SHA256 must contain 64 lowercase hexadecimal characters');
const count = z.number().int().nonnegative().max(Number.MAX_SAFE_INTEGER);
const confidence = z.number().finite().min(0).max(1).nullable();
const evidence = z.array(z.enum(['RAW_STRUCTURAL', 'LITERATURE_ASSOCIATED', 'SOURCE_BACKED_ANATOMY'])).min(1).max(3);
const refs = z.array(text).min(1).max(32);
const geometry = z.discriminatedUnion('status', [
  z.object({ status: z.literal('UNAVAILABLE') }).strict(),
  z.object({
    status: z.literal('SOURCE_BACKED_SWC'), asset: z.string().regex(/^\/data\/geometry\/[a-f0-9]{64}\.json$/),
    sha256: hash, bytes: count.max(limits.maxGeometryBytes), pointCount: count.min(1).max(limits.maxGeometryPoints),
    sourceSha256: hash, sourceUrl: z.string().regex(/^https:\/\/storage\.googleapis\.com\/flyem-male-cns\/v1\.0\/segmentation\/skeletons-malecns\/skeletons-swc\/[1-9][0-9]*\.swc$/),
    receiptSha256: hash, units: z.literal('8 nm'), coordinateSpace: z.literal('MaleCNS native EM'), orientationStatus: z.literal('UNVERIFIED'),
  }).strict(),
]);
export const realNodeSchema = z.object({
  bodyId, type: optionalText, aliases: z.array(text).max(40), displayAlias: optionalText,
  side: z.enum(['L', 'R', 'M']).nullable(), sideSource: optionalText, rootSide: optionalText, somaSide: optionalText,
  cellClass: optionalText, superclass: optionalText, classification: optionalText, entryNerve: optionalText, exitNerve: optionalText,
  annotationPresent: z.boolean(), neurotransmitterPrediction: optionalText, predictionConfidence: confidence,
  transmitterConsensus: optionalText, cellTypePrediction: optionalText, cellTypePredictionConfidence: confidence,
  evidence, sourceRefs: refs, evidenceSources: z.record(z.string(), text), paperStatus: text,
  annotationProvenance: text, ntProvenance: text, rawSourceMemberships: z.array(text).max(20),
  packageMemberships: z.array(text).max(30), warningIds: z.array(text).max(100), unresolvedFields: z.array(text).max(40), anatomy: geometry,
}).strict();
const edgeSchema = z.object({
  source: bodyId, target: bodyId, rawSynapseCount: count.min(1), neuprintWeightHP: count.nullable(), neuprintWeightHR: count.nullable(),
  sideRelationship: text, evidence, sourceRefs: refs, queryProvenance: refs, flatProvenance: text, verificationStatus: z.literal('VERIFIED'),
}).strict();
const sourceFile = z.object({ path: text, sha256: hash, bytes: count, verification: z.enum(['SHA256_MATCH', 'RECORDED_IN_FROZEN_MANIFEST']) }).strict();
const warning = z.object({
  id: text, status: z.enum(['RESOLVED', 'UNRESOLVED']), message: text, bodyIds: z.array(bodyId).max(limits.maxNodes),
  sourceA: text, valueA: z.string().max(20000), sourceB: text, valueB: z.string().max(20000),
  resolution: z.string().max(20000), sourceRef: text,
}).strict();
const budgetSchema = z.object({
  maxNodes: count.min(1).max(limits.maxNodes), maxEdges: count.min(1).max(limits.maxEdges),
  maxGeometryObjects: count.min(1).max(limits.maxGeometryObjects), maxPackageBytes: count.min(1).max(limits.maxPackageBytes),
  maxPaths: count.min(1).max(limits.maxPaths), maxGeometryPoints: count.min(1).max(limits.maxGeometryPoints),
  maxGeometryBytes: count.min(1).max(limits.maxGeometryBytes), maxRenderedEdges: count.min(1).max(limits.maxRenderedEdges),
}).strict();
export const realPackageSchema = z.object({
  format: z.literal('FLYWORLD_CIRCUIT_PACKAGE'), schemaVersion: z.literal(3), id: text, name: text,
  packageType: z.enum(['focused', 'paper', 'candidates', 'lb3b', 'lb3c', 'motors', 'sugar-selected', 'custom', 'anatomy']),
  scientificLabel: z.enum(SCIENTIFIC_LABELS),
  dataset: z.object({ name: text, version: text, uuid: z.string().regex(/^[a-f0-9]{32}$/) }).strict(),
  generatedAt: z.string().datetime({ offset: true }), sourceRun: text, visualizationRun: text, workflowRun: text,
  preprocessor: z.array(z.object({ path: text, sha256: hash }).strict()).min(1).max(10),
  sourceFiles: z.array(sourceFile).min(1).max(200),
  neurons: z.array(realNodeSchema).max(limits.maxNodes), edges: z.array(edgeSchema).max(limits.maxEdges),
  paths: z.array(z.object({ id: text, bodyIds: z.array(bodyId).min(2).max(100), sourceRef: text, label: z.literal('PAPER_ASSOCIATED') }).strict()).max(limits.maxPaths),
  warnings: z.array(warning).max(2000),
  unresolved: z.array(z.object({ name: text, bodyId: z.null(), status: z.literal('UNRESOLVED'), reason: text }).strict()).max(100),
  selection: z.object({ status: z.literal('UNAVAILABLE'), validated: z.literal(false) }).strict(),
  simulation: z.object({ status: z.literal('UNAVAILABLE') }).strict(),
  anatomyStatus: z.enum(['PARTIAL', 'UNAVAILABLE']), limits: budgetSchema, scope: z.literal('IN-PACKAGE ONLY'),
  inclusionRule: text, neighborhoodScope: optionalText, limitations: z.array(text).min(1).max(30),
}).strict().superRefine((pkg, ctx) => {
  const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
  if (pkg.dataset.name !== DATASET.name || pkg.dataset.version !== DATASET.version || pkg.dataset.uuid !== DATASET.uuid) fail('Incompatible dataset/version/UUID. Comparison mode is unavailable; expected male-cns:v1.0 / ' + DATASET.uuid);
  if (pkg.scientificLabel === 'SELECTED_EFFECTIVE_CONNECTIVITY') fail('Validated selected results are unavailable; selection claims are rejected');
  const ids = new Set(pkg.neurons.map(n => n.bodyId));
  if (ids.size !== pkg.neurons.length) fail('Duplicate body IDs');
  const files = new Set(pkg.sourceFiles.map(f => f.path));
  if (files.size !== pkg.sourceFiles.length) fail('Duplicate source file paths');
  const checkRefs = (values: string[]) => values.forEach(ref => { if (!files.has(ref)) fail('Missing hashed source reference: ' + ref); });
  const warningIds = new Set(pkg.warnings.map(w => w.id));
  if (warningIds.size !== pkg.warnings.length) fail('Duplicate warning IDs');
  pkg.neurons.forEach(node => {
    checkRefs(node.sourceRefs);
    if (node.warningIds.some(id => !warningIds.has(id))) fail('Unresolved warning reference for body ' + node.bodyId);
    if (/\bpuddle\b/i.test([node.type, node.displayAlias, ...node.aliases].join(' '))) fail('Puddle body identity remains unresolved; guessed identities are rejected');
    if (!node.evidence.includes('RAW_STRUCTURAL')) fail('Body identity must retain structural evidence');
    if (node.anatomy.status === 'SOURCE_BACKED_SWC') {
      if (!node.anatomy.sourceUrl.endsWith('/' + node.bodyId + '.swc')) fail('Geometry source/body ID mismatch');
      if (!node.anatomy.asset.endsWith(node.anatomy.sha256 + '.json')) fail('Geometry content hash/path mismatch');
    }
  });
  const pairs = new Set<string>();
  pkg.edges.forEach(edge => {
    if (!ids.has(edge.source) || !ids.has(edge.target)) fail('Edge references a missing source or target body');
    const key = edge.source + ':' + edge.target;
    if (pairs.has(key)) fail('Duplicate directed edge');
    pairs.add(key); checkRefs(edge.sourceRefs);
    if (!edge.evidence.includes('RAW_STRUCTURAL')) fail('Raw edges must retain structural evidence');
  });
  const paths = new Set<string>();
  pkg.paths.forEach(path => {
    if (paths.has(path.id)) fail('Duplicate path ID');
    paths.add(path.id); checkRefs([path.sourceRef]);
    if (path.bodyIds.some(id => !ids.has(id))) fail('Path body missing from package');
    for (let i = 1; i < path.bodyIds.length; i++) if (!pairs.has(path.bodyIds[i - 1] + ':' + path.bodyIds[i])) fail('Path edge missing from package');
  });
  pkg.warnings.forEach(w => { checkRefs([w.sourceRef]); if (w.bodyIds.some(id => !ids.has(id))) fail('Warning body missing from package'); });
  const anatomical = pkg.neurons.filter(n => n.anatomy.status === 'SOURCE_BACKED_SWC').length;
  if (pkg.neurons.length > pkg.limits.maxNodes || pkg.edges.length > pkg.limits.maxEdges || pkg.paths.length > pkg.limits.maxPaths || anatomical > pkg.limits.maxGeometryObjects) fail('Package exceeds its configured browser safety limits');
  if (pkg.anatomyStatus !== (anatomical ? 'PARTIAL' : 'UNAVAILABLE')) fail('Anatomy status disagrees with body records');
  if (pkg.packageType === 'sugar-selected' && (pkg.neurons.length || pkg.edges.length || pkg.paths.length || pkg.scientificLabel !== 'UNRESOLVED')) fail('Sugar-selected placeholder must stay empty and UNRESOLVED');
  if (pkg.packageType === 'candidates' && (pkg.edges.length || pkg.scientificLabel !== 'CANDIDATE')) fail('Independent candidate comparison must not assert a shared pathway');
  if (pkg.packageType === 'paper' && pkg.scientificLabel !== 'PAPER_ASSOCIATED') fail('Paper package must retain PAPER_ASSOCIATED label');
  if (pkg.scientificLabel === 'ANATOMY_ONLY' && pkg.edges.length) fail('Anatomy-only packages cannot claim structural edges');
});
export type RealPackage = z.infer<typeof realPackageSchema>;
export type RealNode = RealPackage['neurons'][number];
export type RealEdge = RealPackage['edges'][number];

export function parseRealPackage(input: unknown) { return realPackageSchema.parse(input); }
export function parseRealPackageText(input: string) {
  const bytes = new TextEncoder().encode(input).byteLength;
  if (bytes > limits.maxPackageBytes) throw new Error('Package exceeds the configured 4 MiB limit. Preprocess a smaller subset.');
  const pkg = parseRealPackage(JSON.parse(input));
  if (bytes > pkg.limits.maxPackageBytes) throw new Error('Package exceeds its declared byte limit');
  return pkg;
}
export async function sha256Bytes(bytes: ArrayBuffer) {
  return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes)), v => v.toString(16).padStart(2, '0')).join('');
}
export async function readBoundedResponse(response: Response, maxBytes: number) {
  if (!response.ok) throw new Error('Local asset request failed: HTTP ' + response.status);
  const reader = response.body?.getReader();
  if (!reader) throw new Error('Local asset body is unavailable');
  const chunks: Uint8Array[] = []; let length = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      length += value.byteLength;
      if (length > maxBytes) throw new Error('Local asset exceeds browser byte limit');
      chunks.push(value);
    }
  } catch (error) { await reader.cancel(); throw error; }
  const buffer = new Uint8Array(length); let offset = 0;
  chunks.forEach(chunk => { buffer.set(chunk, offset); offset += chunk.length; });
  return buffer;
}
