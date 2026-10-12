import { useEffect, useRef } from 'react';
import { partners, type Isolation } from './graph';
import type { RealNode, RealPackage } from './schema';

const value = (input: string | number | null) => input === null ? 'UNRESOLVED / not supplied' : String(input);
export function RealInspector({ pkg, node, select, isolate }: {
  pkg: RealPackage; node: RealNode | null; select: (id: string) => void; isolate: (mode: Isolation) => void;
}) {
  const ref = useRef<HTMLElement>(null);
  useEffect(() => { if (ref.current) ref.current.scrollTop = 0; }, [node?.bodyId]);
  if (!node) return <aside className="real-inspector" ref={ref}><h2>Body inspector</h2><p>Select a node, population member, or body in the list.</p><strong>IN-PACKAGE ONLY</strong><p>Partner summaries do not represent whole-connectome totals.</p></aside>;
  const { incoming, outgoing } = partners(pkg, node.bodyId);
  const byId = new Map(pkg.neurons.map(n => [n.bodyId, n]));
  const warnings = pkg.warnings.filter(w => node.warningIds.includes(w.id));
  const fields: [string, string | number | null][] = [
    ['Body ID', node.bodyId], ['Type', node.type], ['Aliases (source)', node.aliases.join('; ') || null],
    ['Display alias', node.displayAlias], ['Side', node.side], ['Side source', node.sideSource],
    ['Root side', node.rootSide], ['Soma side', node.somaSide], ['Class', node.cellClass], ['Superclass', node.superclass],
    ['Source classification', node.classification], ['Entry nerve', node.entryNerve], ['Exit nerve', node.exitNerve],
    ['NT body prediction', node.neurotransmitterPrediction], ['Prediction confidence', node.predictionConfidence],
    ['Transmitter consensus', node.transmitterConsensus], ['Cell-type prediction', node.cellTypePrediction],
    ['Cell-type confidence', node.cellTypePredictionConfidence],
  ];
  return <aside className="real-inspector" ref={ref} aria-label="Real neuron inspector" data-testid="real-inspector">
    <div className="eyebrow">SOURCE RECORD / BODY</div><h2>{node.type ?? 'Unannotated body'} <small>{node.bodyId}</small></h2>
    <div className="real-badges">{node.evidence.map(e => <span key={e}>{e}</span>)}</div>
    <p className="real-notice">{node.anatomy.status === 'UNAVAILABLE' ? 'ANATOMY UNAVAILABLE FOR THIS BODY' : 'SOURCE-BACKED SWC · native orientation UNVERIFIED'}</p>
    <dl className="real-metadata">{fields.map(([label, content]) => <div key={label}><dt>{label}</dt><dd>{value(content)}</dd></div>)}</dl>
    <p className="real-notice">PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION</p>
    <h3>Package membership</h3><ul>{node.packageMemberships.map(id => <li key={id}>{id}</li>)}</ul>
    <p>Source search memberships: {node.rawSourceMemberships.join(', ') || 'none supplied'}. These are bounded raw-search sets, not effective selection.</p>
    <h3>Inspect raw partners <small>IN-PACKAGE ONLY</small></h3>
    <div className="real-actions">{(['INCOMING', 'OUTGOING', 'ONE_HOP', 'ALL'] as Isolation[]).map(mode => <button key={mode} onClick={() => isolate(mode)}>{({ INCOMING: 'Incoming', OUTGOING: 'Outgoing', ONE_HOP: 'One hop', ALL: 'Full package', PATH: 'Path' })[mode]}</button>)}</div>
    {([['Incoming', incoming], ['Outgoing', outgoing]] as const).map(([direction, edges]) => <details key={direction} open>
      <summary>{direction}: {edges.length} partners · {edges.reduce((sum, e) => sum + e.rawSynapseCount, 0).toLocaleString()} raw synapses</summary>
      <div className="partner-list">{edges.map(edge => {
        const id = direction === 'Incoming' ? edge.source : edge.target;
        return <button key={edge.source + ':' + edge.target} onClick={() => select(id)}><span>{byId.get(id)?.type ?? 'Unknown'} · {id}</span><b>{edge.rawSynapseCount}</b></button>;
      })}{!edges.length && <p>No records in this package. This does not establish absence from the connectome.</p>}</div>
    </details>)}
    <h3>Mismatch warnings</h3>{warnings.length ? warnings.map(w => <details key={w.id}><summary>{w.id} · {w.message} ({w.status})</summary><p>{w.sourceA}: {w.valueA}</p><p>{w.sourceB}: {w.valueB}</p><p>{w.resolution}</p></details>) : <p>No body-specific ledger warning supplied. Package-wide limitations still apply.</p>}
    <h3>Unresolved fields</h3><p>{node.unresolvedFields.join(', ') || 'No missing fields among the tracked metadata columns.'}</p>
    <h3>Evidence and sources</h3><p>{node.paperStatus}</p>
    <ul className="source-paths">{node.sourceRefs.map(path => <li key={path}>{path}</li>)}</ul>
    <details><summary>Original evidence and annotation references</summary><pre>{JSON.stringify({ evidence: node.evidenceSources, annotation: node.annotationProvenance, neurotransmitter: node.ntProvenance }, null, 2)}</pre></details>
  </aside>;
}
export function DatasetPanel({ pkg, bytes, origin }: { pkg: RealPackage; bytes: number; origin: string }) {
  const anatomical = pkg.neurons.filter(n => n.anatomy.status === 'SOURCE_BACKED_SWC').length;
  return <details className="dataset-panel" open data-testid="dataset-panel"><summary>Dataset and package provenance</summary>
    <dl className="dataset-grid">
      <div><dt>Loaded package</dt><dd>{pkg.name}</dd></div><div><dt>Scientific label</dt><dd>{pkg.scientificLabel}</dd></div>
      <div><dt>Dataset / version</dt><dd>{pkg.dataset.name} / {pkg.dataset.version}</dd></div><div><dt>UUID</dt><dd>{pkg.dataset.uuid}</dd></div>
      <div><dt>Bodies / edges</dt><dd>{pkg.neurons.length} / {pkg.edges.length}</dd></div><div><dt>Package size</dt><dd>{bytes.toLocaleString()} bytes</dd></div>
      <div><dt>Source run</dt><dd>{pkg.sourceRun}</dd></div><div><dt>Visualization run</dt><dd>{pkg.visualizationRun}</dd></div>
      <div><dt>Anatomy</dt><dd>{anatomical}/{pkg.neurons.length} source-backed local SWCs</dd></div>
      <div><dt>Effective selection</dt><dd>UNAVAILABLE — no validated result</dd></div><div><dt>Simulation</dt><dd>UNAVAILABLE</dd></div>
      <div><dt>Import assurance</dt><dd>{origin}</dd></div>
    </dl><p>{pkg.inclusionRule}</p><p>Generated {pkg.generatedAt}. Partner scope: <strong>IN-PACKAGE ONLY</strong>.</p>
    <details><summary>Source hashes and preprocessing scripts</summary><div className="source-hashes">{pkg.sourceFiles.map(f => <p key={f.path}><strong>{f.path}</strong><code>{f.sha256}</code><small>{f.verification} · {f.bytes.toLocaleString()} bytes</small></p>)}{pkg.preprocessor.map(f => <p key={f.path}><strong>{f.path}</strong><code>{f.sha256}</code></p>)}</div></details>
    <details><summary>Unresolved warnings and scientific limits ({pkg.warnings.filter(w => w.status === 'UNRESOLVED').length})</summary>
      {pkg.unresolved.map(u => <p key={u.name}><strong>{u.name}: {u.status}</strong> — {u.reason}</p>)}
      <ul>{pkg.limitations.map(item => <li key={item}>{item}</li>)}</ul>
      <div className="source-hashes">{pkg.warnings.filter(w => w.status === 'UNRESOLVED' && !w.bodyIds.length).map(w => <p key={w.id}><strong>{w.id}: {w.message}</strong><span>{w.valueA} / {w.valueB}</span><small>{w.resolution}</small></p>)}</div>
    </details>
  </details>;
}
