import { useEffect, useRef } from 'react';
import { useStudio } from '../state/store';
import { educationalPackage, entityById, regionForEntity, relationsForEntity, PLACEHOLDER_LABEL } from '../circuits/demo';
import { Crosshair } from '../ui/Icons';
import { useTelemetry } from '../activity/ActivityPanel';
import { latestRelevantEvent, sampleTarget } from '../activity/timeline';
import { avatarAnimation } from '../fly/animation';
import type { DemoId } from '../data/contracts';

export function Inspector() {
  const panel = useRef<HTMLElement>(null);
  const selected = useStudio(s => s.selectedEntity);
  useEffect(() => { panel.current?.scrollTo({ top: 0 }); }, [selected]);
  const transparent = useStudio(s => s.transparentHead);
  const layers = useStudio(s => s.layers);
  const brainMode = useStudio(s => s.cameraMode === 'BRAIN_INSPECTION');
  const sample = useTelemetry();
  const entity = selected ? entityById.get(selected) : null;
  const region = selected ? regionForEntity(selected) : null;
  const activity = selected ? sampleTarget(sample.events, selected, sample.timelineMs, sample.reducedMotion) : { value: 0, event: null };
  const event = activity.event ?? (selected ? latestRelevantEvent(sample.events, selected, sample.timelineMs) : sample.events.slice().reverse().find(e => e.startMs <= sample.timelineMs));
  const { upstream, downstream } = selected ? relationsForEntity(selected) : { upstream: [], downstream: [] };
  const choose = (id: DemoId) => { useStudio.getState().selectEntity(id); useStudio.getState().setCamera('BRAIN_INSPECTION'); };
  const relationList = (ids: DemoId[]) => ids.length ? ids.map(id => <button key={id} onClick={() => choose(id)}>{entityById.get(id)?.name} ↗</button>) : <span>None in this demo</span>;
  return <aside ref={panel} className="inspector" aria-label="Inspector">
    <div className="panel-heading"><span className="eyebrow">INSPECTOR / EDUCATIONAL</span><Crosshair /></div>
    <div className="specimen-title"><span className="specimen-index">02</span><div><h2>{entity?.name ?? 'Drosophila avatar'}</h2><p>{entity ? 'Selected educational placeholder' : 'PROCEDURAL PLACEHOLDER AVATAR'}</p></div></div>
    <div className="geometry-note"><span className="tiny-dot" /><div><strong>No anatomical data loaded</strong><p>Systems and nodes are teaching categories. Shapes, placement, and relations are arbitrary.</p></div></div>
    <section className="inspector-section">
      <label className="toggle-row"><span>Transparent head<small>Reveal the educational brain</small></span><input type="checkbox" role="switch" checked={transparent} onChange={() => useStudio.getState().toggleHead()} aria-label="Transparent head" /><span className="switch-track" aria-hidden="true" /></label>
      <div className="inspector-actions"><button onClick={() => useStudio.getState().setCamera(brainMode ? 'FLY_INSPECTION' : 'BRAIN_INSPECTION')}>{brainMode ? 'Inspect fly' : 'Inspect brain'}</button><button onClick={() => useStudio.getState().resetBrain()}>Reset brain view</button></div>
    </section>
    {entity && <section className="inspector-section selected-details" data-testid="entity-record">
      <div className="section-title"><h3>Selected {entity.kind === 'REGION' ? 'system' : 'demo neuron'}</h3><span>UNVERIFIED</span></div>
      <code className="entity-id">{entity.id}</code>
      <dl className="metadata-grid"><dt>Role category</dt><dd>{entity.roleCategory}<small>Educational category only</small></dd><dt>Anatomy</dt><dd>PLACEHOLDER_GEOMETRY</dd><dt>Biological body ID</dt><dd>None</dd><dt>Current behavior</dt><dd>{avatarAnimation(sample).name}</dd><dt>Current activity</dt><dd data-testid="selected-activity">{activity.value.toFixed(3)} / 1</dd></dl>
      <div className="source-label" data-testid="activation-source">{event?.sourceMode ?? 'UNVERIFIED'}</div>
      <dl className="metadata-grid"><dt>Caused by</dt><dd>{event?.name ?? 'No event'}</dd><dt>Event ID</dt><dd>{event?.id ?? '—'}</dd><dt>Start / end</dt><dd>{event ? `${(event.startMs / 1000).toFixed(2)} s / ${event.endMs === null ? 'on key release' : `${(event.endMs / 1000).toFixed(2)} s`}` : '—'}</dd><dt>Activity evidence</dt><dd>{event?.evidence ?? 'UNVERIFIED'}</dd></dl>
      <p className="small muted">{event?.notes ?? entity.description}</p>
      <div className="inspector-actions"><button onClick={() => useStudio.getState().focusEntity(entity.id)}>Focus selection</button><button onClick={() => useStudio.getState().focusEntity(null)}>Whole brain</button>{region && <button onClick={() => useStudio.getState().isolateRegion(region.id)}>Isolate system</button>}</div>
      <div className="relations"><h4>Upstream demo relations</h4>{relationList(upstream)}<h4>Downstream demo relations</h4>{relationList(downstream)}<p>Illustrative relations; not synaptic connections. {entity.kind === 'REGION' && 'Only relations across this demo system’s boundary are listed.'}</p></div>
      <div className="source-references"><strong>Source references</strong>{entity.sourceRefs.map(ref => <a key={ref} href={ref} target="_blank" rel="noreferrer">Local demo design JSON ↗</a>)}<span>Design source only; no biological evidence.</span></div>
    </section>}
    <section className="inspector-section"><div className="section-title"><h3>Brain layers</h3><span>5 SYSTEMS</span></div>
      <p className="small muted">Select a system or node. Use the checkbox to hide a layer.</p>
      <div className="region-layers">{educationalPackage.regions.map(r => <div key={r.id} className="region-layer">
        <div className="region-layer-heading"><input type="checkbox" checked={layers[r.id].visible} onChange={e => useStudio.getState().setLayer(r.id, { visible: e.target.checked })} aria-label={`Show ${r.name}`} /><button aria-pressed={selected === r.id} onClick={() => choose(r.id)} title={`${r.name} — educational placeholder`}><span className="system-symbol" style={{ borderColor: r.color }}>{r.symbol}</span>{r.name}</button></div>
        <label className="opacity-row">Opacity<input type="range" min={8} max={85} value={Math.round(layers[r.id].opacity * 100)} onChange={e => useStudio.getState().setLayer(r.id, { opacity: Number(e.target.value) / 100 })} aria-label={`${r.name} opacity`} /><span>{Math.round(layers[r.id].opacity * 100)}%</span></label>
        <details><summary>{educationalPackage.neurons.filter(n => n.regionId === r.id).length} generic demo nodes</summary><div className="neuron-list">{educationalPackage.neurons.filter(n => n.regionId === r.id).map(n => <button key={n.id} aria-pressed={selected === n.id} onClick={() => choose(n.id)}>{n.name}</button>)}</div></details>
      </div>)}</div>
    </section>
    {!entity && <section className="inspector-section"><div className="section-title"><h3>Latest display event</h3><span>PROVENANCE</span></div><div className="source-label" data-testid="activation-source">{event?.sourceMode ?? 'UNVERIFIED'}</div><p className="small muted">{event?.name ?? 'Use a control or start the educational tour.'}</p></section>}
    <div className="inspector-footer"><span className="tiny-dot" /><span>13 generic nodes · 0 biological records<br /><small>{PLACEHOLDER_LABEL}</small></span></div>
  </aside>;
}
