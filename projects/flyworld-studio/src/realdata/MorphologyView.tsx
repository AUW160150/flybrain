import { Component, Suspense, useEffect, useMemo, useState, type ReactNode } from 'react';
import { Canvas } from '@react-three/fiber';
import { Bounds, OrbitControls } from '@react-three/drei';
import { BufferAttribute, BufferGeometry } from 'three';
import { z } from 'zod';
import { BROWSER_LIMITS, readBoundedResponse, sha256Bytes, type RealNode } from './schema';

const point = z.tuple([z.number().int().positive(), z.number().int().nonnegative(), z.number().finite(), z.number().finite(), z.number().finite(), z.number().finite().nonnegative(), z.number().int()]);
export const morphologySchema = z.object({
  format: z.literal('FLYWORLD_NATIVE_SWC'), schemaVersion: z.literal(1), bodyId: z.string().regex(/^[1-9][0-9]*$/),
  dataset: z.literal('male-cns:v1.0'), releaseEvidence: z.literal('OFFICIAL_RELEASE_URL_AND_SHA256_RECEIPT'),
  sourceUrl: z.string(), sourceSha256: z.string().regex(/^[a-f0-9]{64}$/), receiptSha256: z.string().regex(/^[a-f0-9]{64}$/),
  retrievedAt: z.string(), coordinateSpace: z.literal('MaleCNS native EM'), units: z.literal('8 nm'),
  scaleToMicrometers: z.literal(0.008), orientationStatus: z.literal('UNVERIFIED'), transformApplied: z.literal(false),
  sourceHeaders: z.array(z.string()).max(1000), points: z.array(point).min(1).max(BROWSER_LIMITS.maxGeometryPoints),
}).strict().superRefine((value, ctx) => {
  const parents = new Map(value.points.map(p => [p[0], p[6]]));
  const fail = (message: string) => ctx.addIssue({ code: 'custom', message });
  if (parents.size !== value.points.length) fail('Duplicate morphology point ID');
  const complete = new Set<number>();
  for (const id of parents.keys()) {
    const seen = new Set<number>(); let cursor = id;
    while (cursor !== -1 && !complete.has(cursor)) {
      if (!parents.has(cursor)) { fail('Missing morphology parent'); break; }
      if (seen.has(cursor)) { fail('Cyclic morphology parent'); break; }
      seen.add(cursor); cursor = parents.get(cursor)!;
    }
    seen.forEach(v => complete.add(v));
  }
});
type Morphology = z.infer<typeof morphologySchema>;
function Skeleton({ data }: { data: Morphology }) {
  const geometry = useMemo(() => {
    const positions = new Map(data.points.map(p => [p[0], p.slice(2, 5)]));
    const segments: number[] = [];
    for (const p of data.points) if (p[6] !== -1) segments.push(...positions.get(p[6])!, ...positions.get(p[0])!);
    const result = new BufferGeometry();
    result.setAttribute('position', new BufferAttribute(new Float32Array(segments), 3));
    // Translation for framing changes only the render buffer; source coordinates remain intact.
    result.computeBoundingBox(); result.center(); result.computeBoundingSphere();
    return result;
  }, [data]);
  useEffect(() => () => geometry.dispose(), [geometry]);
  return <lineSegments geometry={geometry}><lineBasicMaterial color="#72c9eb" /></lineSegments>;
}
class MorphologyBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <p role="alert">Morphology renderer unavailable. Source metadata remains inspectable.</p> : this.props.children; }
}
export default function MorphologyView({ node }: { node: RealNode | null }) {
  const [data, setData] = useState<Morphology | null>(null);
  const [error, setError] = useState('');
  const [supported] = useState(() => {
    try { const gl = document.createElement('canvas').getContext('webgl2'); gl?.getExtension('WEBGL_lose_context')?.loseContext(); return !!gl; } catch { return false; }
  });
  useEffect(() => {
    const abort = new AbortController(); setData(null); setError('');
    const record = node?.anatomy;
    const expectedBody = node?.bodyId;
    if (record?.status !== 'SOURCE_BACKED_SWC') return;
    void (async () => {
      try {
        const bytes = await readBoundedResponse(await fetch(record.asset.startsWith('/') ? import.meta.env.BASE_URL + record.asset.slice(1) : record.asset, { signal: abort.signal }), BROWSER_LIMITS.maxGeometryBytes);
        if (bytes.byteLength !== record.bytes || await sha256Bytes(bytes.buffer) !== record.sha256) throw new Error('Geometry size/checksum mismatch');
        const parsed = morphologySchema.parse(JSON.parse(new TextDecoder().decode(bytes)));
        if (parsed.bodyId !== expectedBody || parsed.points.length !== record.pointCount || parsed.sourceSha256 !== record.sourceSha256 ||
            parsed.sourceUrl !== record.sourceUrl || parsed.receiptSha256 !== record.receiptSha256) throw new Error('Geometry body/provenance mismatch');
        if (!abort.signal.aborted) setData(parsed);
      } catch (cause) { if (!abort.signal.aborted) setError(cause instanceof Error ? cause.message : 'Geometry load failed'); }
    })();
    return () => abort.abort();
  }, [node]);
  if (!node) return <p>Select a body to inspect its anatomy availability.</p>;
  if (node.anatomy.status === 'UNAVAILABLE') return <div className="real-empty"><strong>ANATOMY UNAVAILABLE FOR THIS BODY</strong><p>Body {node.bodyId} has no verified local morphology. The node-link diagram uses an abstract layout.</p></div>;
  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p role="status">Checking local geometry hash and parent references…</p>;
  return <div className="morphology-view"><div className="real-notice"><strong>SOURCE-BACKED NATIVE SWC · {node.bodyId}</strong><span>{data.points.length.toLocaleString()} original points · 8 nm coordinate units · orientation UNVERIFIED</span></div>
    {supported ? <MorphologyBoundary><div className="morphology-canvas"><Canvas camera={{ position: [0, 0, 100000], near: 1, far: 1000000 }} dpr={[1, 1.5]}>
      <Suspense fallback={null}><Bounds fit clip observe margin={1.2}><Skeleton data={data} /></Bounds><OrbitControls makeDefault enableDamping={false} /></Suspense>
    </Canvas></div></MorphologyBoundary> : <p role="alert">WebGL unavailable. The verified geometry metadata can still be inspected.</p>}
    <p>Native XYZ axes; no anatomical camera names, mirroring, branch repair, or inferred neurites. Lines are skeleton cables, not synaptic edges. This view is centered for display only.</p>
    <details><summary>Original SWC headers and geometry provenance</summary><pre>{data.sourceHeaders.join('\n')}</pre><p>Native SWC header UUIDs are retained as source metadata; they are not substituted for the neuPrint dataset UUID.</p><a href={node.anatomy.asset.startsWith('/') ? import.meta.env.BASE_URL + node.anatomy.asset.slice(1) : node.anatomy.asset} download>Download exact native-coordinate cache</a></details>
  </div>;
}
