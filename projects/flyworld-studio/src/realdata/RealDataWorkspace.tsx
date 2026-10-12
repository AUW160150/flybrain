import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { catalogSchema, type CatalogEntry } from './catalog';
import { BROWSER_LIMITS, parseRealPackageText, readBoundedResponse, sha256Bytes, type RealPackage } from './schema';
import { filterGraph, initialFilters, realHighlights, type GraphFilters, type Isolation } from './graph';
import { DatasetPanel, RealInspector } from './RealInspector';
import { RawGraph, nodeColor } from './RawGraph';
import { useStudio } from '../state/store';
import { useTelemetry } from '../activity/ActivityPanel';
import { educationalPackage, PLACEHOLDER_LABEL } from '../circuits/demo';

const MorphologyView = lazy(() => import('./MorphologyView'));
type View = 'BODY' | 'POPULATION' | 'REGION' | 'EDGES' | 'MORPHOLOGY';
const views: [View, string][] = [['BODY', 'Body diagram'], ['POPULATION', 'Populations'], ['REGION', 'Region context'], ['EDGES', 'Raw edges'], ['MORPHOLOGY', 'Morphology']];

export default function RealDataWorkspace({ showWorld, showAtlas }: { showWorld: () => void; showAtlas?: () => void }) {
  const [catalog, setCatalog] = useState<CatalogEntry[]>([]);
  const [pkg, setPackage] = useState<RealPackage | null>(null);
  const [bytes, setBytes] = useState(0);
  const [origin, setOrigin] = useState('');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<GraphFilters>(initialFilters);
  const [view, setView] = useState<View>('BODY');
  const [page, setPage] = useState(0);
  const request = useRef(0);
  const abort = useRef<AbortController | null>(null);
  const telemetry = useTelemetry();
  function install(next: RealPackage, size: number, assurance: string) {
    setPackage(next); setBytes(size); setOrigin(assurance); setFilters({ ...initialFilters, selected: next.neurons[0]?.bodyId ?? null }); setPage(0);
    setView(next.packageType === 'anatomy' ? 'MORPHOLOGY' : next.packageType === 'candidates' ? 'POPULATION' : 'BODY');
  }
  async function load(entry: CatalogEntry) {
    const key = ++request.current; abort.current?.abort(); abort.current = new AbortController();
    setPending(true); setError('');
    try {
      const data = await readBoundedResponse(await fetch(import.meta.env.BASE_URL + 'data/malecns/' + entry.file, { signal: abort.current.signal }), BROWSER_LIMITS.maxPackageBytes);
      if (data.byteLength !== entry.bytes || await sha256Bytes(data.buffer) !== entry.sha256) throw new Error('Package checksum/size mismatch; regenerate the local catalog and packages together.');
      const next = parseRealPackageText(new TextDecoder().decode(data));
      if (next.id !== entry.id || next.neurons.length !== entry.nodes || next.edges.length !== entry.edges || next.scientificLabel !== entry.scientificLabel) throw new Error('Catalog/package identity or count mismatch');
      if (key === request.current) install(next, data.byteLength, 'Bundled package checksum verified; source hashes checked offline');
    } catch (cause) { if (key === request.current) setError(cause instanceof Error ? cause.message : 'Package load failed'); }
    finally { if (key === request.current) setPending(false); }
  }
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    void (async () => {
      try {
        const data = await readBoundedResponse(await fetch(import.meta.env.BASE_URL + 'data/malecns/manifest.json', { signal: controller.signal }), 65536);
        const next = catalogSchema.parse(JSON.parse(new TextDecoder().decode(data)));
        if (active) { setCatalog(next.packages); if (next.packages[0]) void load(next.packages[0]); }
      } catch (cause) { if (active) setError(cause instanceof Error ? cause.message : 'Catalog unavailable'); }
    })();
    return () => { active = false; controller.abort(); request.current++; abort.current?.abort(); };
  }, []);
  const graph = useMemo(() => pkg ? filterGraph(pkg, filters) : null, [pkg, filters]);
  const selected = pkg?.neurons.find(n => n.bodyId === filters.selected) ?? null;
  const highlight = pkg ? realHighlights(pkg, telemetry) : { bodyIds: new Set<string>(), value: 0, mapping: null };
  const update = (patch: Partial<GraphFilters>) => { setFilters(current => ({ ...current, ...patch })); setPage(0); };
  const select = (id: string) => update({ selected: id });
  const isolate = (isolation: Isolation) => update({ isolation, side: 'ALL', type: 'ALL', evidence: 'ALL' });
  return <section className="real-workspace" aria-label="MaleCNS data workspace">
    <div className="real-heading"><div><div className="eyebrow">MALECNS / LOCAL VERIFIED SOURCE FILES</div><h2>Inspect the records. Keep the limits visible.</h2></div>{showAtlas&&<button onClick={showAtlas}>Real circuit anatomy</button>}<button onClick={showWorld}>← World & educational brain</button></div>
    <div className="package-toolbar">
      <label>Scientific package<select aria-label="Scientific package" value={pkg && catalog.some(e => e.id === pkg.id) && !origin.startsWith('Custom') ? pkg.id : ''} disabled={pending} onChange={event => { const entry = catalog.find(e => e.id === event.target.value); if (entry) void load(entry); }}>
        <option value="" disabled>{pkg ? 'Custom local package' : 'Loading catalog…'}</option>{catalog.map(entry => <option key={entry.id} value={entry.id}>{entry.name} · {entry.nodes} bodies</option>)}</select></label>
      <label className="file-label">Import small local package<input aria-label="Import real circuit package" type="file" accept=".json,application/json" onChange={async event => {
        const file = event.target.files?.[0]; if (!file) return;
        const key = ++request.current; abort.current?.abort(); setPending(true); setError('');
        try {
          if (file.size > BROWSER_LIMITS.maxPackageBytes) throw new Error('File exceeds the 4 MiB safety limit. Use offline preprocessing.');
          const next = parseRealPackageText(await file.text());
          if (key === request.current) install(next, file.size, 'Custom file: schema valid; supplied scientific provenance has not been independently reverified');
        } catch (cause) { if (key === request.current) setError(cause instanceof Error ? cause.message : 'Invalid local package'); }
        finally { if (key === request.current) setPending(false); event.target.value = ''; }
      }} /></label>
    </div>
    {pending && <p role="status">Loading bounded package and verifying its checksum…</p>}
    {error && <p className="real-error" role="alert">Rejected: {error}</p>}
    {pkg && graph && <>
      <div className="real-badges"><strong data-testid="real-scientific-label">{pkg.scientificLabel}</strong><span>{pkg.dataset.name}</span><span>IN-PACKAGE ONLY</span><span>SIMULATION UNAVAILABLE</span></div>
      {telemetry.showDebug && <div className="real-notice" aria-label="Data display statistics"><span>View: {view} · {graph.neurons.length} filtered bodies · {graph.edges.length} filtered edges</span><span>{view === 'BODY' ? Math.min(graph.edges.length, pkg.limits.maxRenderedEdges) + ' arrows drawn' : view === 'MORPHOLOGY' && selected?.anatomy.status === 'SOURCE_BACKED_SWC' ? selected.anatomy.pointCount.toLocaleString() + ' source geometry points' : 'Bounded package view'} · {bytes.toLocaleString()} package bytes</span><span>Browser FPS is not sampled in this data view.</span></div>}
      <div className="real-notice"><span>Raw counts describe saved structure. No connectome activity or autonomous behavior is calculated.</span>
        <button disabled={telemetry.mode !== 'USER_CONTROL'} onClick={() => useStudio.getState().command('FEED')}>Illustrate feeding</button>
      </div>
      {highlight.mapping ? <div className="real-highlight-status" data-testid="real-highlight-source"><strong>USER_DRIVEN_ILLUSTRATION</strong> · FEED · {highlight.bodyIds.size} mapped bodies in this package · display intensity {highlight.value.toFixed(2)}<p>{highlight.mapping.disclaimer} Review: {highlight.mapping.reviewStatus}.</p></div>
        : <p className="real-muted">Feeding can illustrate source-labelled motor records where they are package members. Other behavior keys have no real-body mapping. No highlight is inferred from raw edge counts.</p>}
      <div className="real-filters">
        <label>Side<select aria-label="Body side filter" value={filters.side} onChange={e => update({ side: e.target.value })}>{['ALL', 'L', 'R', 'M', 'UNKNOWN'].map(v => <option key={v}>{v}</option>)}</select></label>
        <label>Evidence<select aria-label="Body evidence filter" value={filters.evidence} onChange={e => update({ evidence: e.target.value })}>{['ALL', 'RAW_STRUCTURAL', 'LITERATURE_ASSOCIATED', 'SOURCE_BACKED_ANATOMY'].map(v => <option key={v}>{v}</option>)}</select></label>
        <label>Type<select aria-label="Body type filter" value={filters.type} onChange={e => update({ type: e.target.value })}><option>ALL</option>{[...new Set(pkg.neurons.map(n => n.type ?? 'UNKNOWN'))].sort().map(v => <option key={v}>{v}</option>)}</select></label>
        <label>Body<select aria-label="Inspect real body" value={filters.selected ?? ''} onChange={e => select(e.target.value)}><option value="" disabled>Select body</option>{pkg.neurons.map(n => <option key={n.bodyId} value={n.bodyId}>{n.type ?? 'Unknown'} · {n.bodyId} · {n.side ?? '?'}</option>)}</select></label>
        <button onClick={() => { setFilters({ ...initialFilters, selected: filters.selected }); setPage(0); }}>Reset filters</button>
      </div>
      <div className="real-view-tabs" aria-label="Scientific data views">{views.map(([id, label]) => <button key={id} aria-pressed={view === id} disabled={id === 'MORPHOLOGY' && !pkg.neurons.some(n => n.anatomy.status === 'SOURCE_BACKED_SWC')} onClick={() => setView(id)}>{label}</button>)}</div>
      <div className="path-controls"><span>Isolation: {filters.isolation} · {graph.neurons.length}/{pkg.neurons.length} visible bodies</span>
        <button onClick={() => isolate('ALL')}>Full package membership</button>
        <label>Saved paper path ({pkg.paths.length})<input aria-label="Saved package path number" type="number" min="1" max={Math.max(1, pkg.paths.length)} value={filters.pathIndex + 1} disabled={!pkg.paths.length}
          onChange={e => { const index = Number(e.target.value) - 1; if (Number.isInteger(index)) update({ pathIndex: Math.max(0, Math.min(pkg.paths.length - 1, index)) }); }} /></label>
        <button disabled={!pkg.paths.length} onClick={() => isolate('PATH')}>Isolate saved path</button>
      </div>
      {filters.isolation === 'PATH' && pkg.paths[filters.pathIndex] && <p className="real-notice">{pkg.paths[filters.pathIndex].id}: {pkg.paths[filters.pathIndex].bodyIds.join(' → ')} · PAPER_ASSOCIATED · not effective selection</p>}
      <div className="real-content">
        <div className="real-visualization">
          {pkg.packageType === 'sugar-selected' ? <div className="real-empty"><strong>VALIDATED SUGAR SELECTION UNAVAILABLE</strong><p>0 bodies · 0 edges. No raw structural path has been substituted for an effective-connectivity result.</p></div>
            : view === 'BODY' ? <RawGraph pkg={pkg} neurons={graph.neurons} edges={graph.edges} selected={filters.selected} highlights={highlight.bodyIds} select={select} />
            : view === 'MORPHOLOGY' ? <Suspense fallback={<p>Loading morphology viewer…</p>}><MorphologyView node={selected} /></Suspense>
            : view === 'REGION' ? <div className="region-context"><h3>Educational region context</h3><p>{PLACEHOLDER_LABEL}</p><div className="region-context-grid">{educationalPackage.regions.map(region => <div key={region.id} style={{ borderColor: region.color }}><strong>{region.name}</strong><small>Educational placeholder</small></div>)}</div><p>No verified body-to-region assignment was imported. None of this package's {pkg.neurons.length} bodies is assigned to these arbitrary shapes.</p><button onClick={() => { showWorld(); useStudio.getState().setCamera('BRAIN_INSPECTION'); }}>Inspect placeholder brain in 3D</button></div>
            : view === 'POPULATION' ? <div className="population-grid">{[...new Set(graph.neurons.map(n => n.type ?? 'UNKNOWN'))].sort().map(type => {
              const nodes = graph.neurons.filter(n => (n.type ?? 'UNKNOWN') === type);
              return <article key={type}><h3 style={{ borderColor: nodeColor(nodes[0]) }}>{type}<small>{nodes.length} bodies in this filtered package</small></h3>
                {nodes.map(n => <button key={n.bodyId} aria-pressed={filters.selected === n.bodyId} onClick={() => select(n.bodyId)}>{n.bodyId} · {n.side ?? 'side unknown'}{n.displayAlias ? ' · ' + n.displayAlias : ''}{highlight.bodyIds.has(n.bodyId) ? ' · USER' : ''}</button>)}</article>;
            })}{!graph.neurons.length && <p>No bodies match these filters.</p>}</div>
            : <div className="raw-table"><p>Raw synapse counts · source → target · IN-PACKAGE ONLY. HP/HR are preserved source fields; neither is activation.</p><table><thead><tr><th>Source</th><th>Target</th><th>Raw count</th><th>HP</th><th>HR</th></tr></thead><tbody>{graph.edges.slice(page * 50, (page + 1) * 50).map(edge => <tr key={edge.source + ':' + edge.target}><td><button onClick={() => select(edge.source)}>{edge.source}</button></td><td><button onClick={() => select(edge.target)}>{edge.target}</button></td><td>{edge.rawSynapseCount}</td><td>{edge.neuprintWeightHP ?? 'Unknown'}</td><td>{edge.neuprintWeightHR ?? 'Unknown'}</td></tr>)}</tbody></table>
              {!graph.edges.length && <p>No raw edges in this filtered package.</p>}<div className="real-actions"><button disabled={page === 0} onClick={() => setPage(p => p - 1)}>Previous 50</button><span>Page {page + 1} / {Math.max(1, Math.ceil(graph.edges.length / 50))} · {graph.edges.length} edges</span><button disabled={(page + 1) * 50 >= graph.edges.length} onClick={() => setPage(p => p + 1)}>Next 50</button></div></div>}
        </div>
        <RealInspector pkg={pkg} node={selected} select={select} isolate={isolate} />
      </div>
      <DatasetPanel pkg={pkg} bytes={bytes} origin={origin} />
      <p className="real-muted">Safety limits: {BROWSER_LIMITS.maxNodes} bodies · {BROWSER_LIMITS.maxEdges} edges · {BROWSER_LIMITS.maxGeometryObjects} geometry objects · 4 MiB/package. Anatomy loads one selected body at a time. No full raw graph enters this browser.</p>
      <div className="real-actions"><a href={import.meta.env.BASE_URL + 'data/malecns/SHA256SUMS'} download>Download package checksums</a>
      <a href={import.meta.env.BASE_URL + 'data/custom-example/malecns-custom.json'} download>Download a generated two-body custom example</a></div>
    </>}
  </section>;
}
