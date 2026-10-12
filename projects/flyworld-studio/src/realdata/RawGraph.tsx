import { useId, useMemo, useState } from 'react';
import { graphPositions } from './graph';
import type { RealPackage, RealNode, RealEdge } from './schema';

export const nodeColor = (node: RealNode) => node.type === 'LB3b' ? '#56b4e9' : node.type === 'LB3c' ? '#009e73' : node.superclass === 'cb_motor' ? '#e69f00' : '#cc79a7';
export function RawGraph({ pkg, neurons, edges, selected, highlights, select }: {
  pkg: RealPackage; neurons: RealNode[]; edges: RealEdge[]; selected: string | null;
  highlights: Set<string>; select: (id: string) => void;
}) {
  const marker = 'edge-arrow-' + useId().replace(/[^a-zA-Z0-9]/g, '');
  const positions = useMemo(() => graphPositions(pkg), [pkg]);
  const [zoom, setZoom] = useState(1);
  const shown = edges.slice(0, pkg.limits.maxRenderedEdges);
  const maxCount = Math.max(1, ...shown.map(edge => edge.rawSynapseCount));
  return <div className="raw-graph">
    <div className="graph-toolbar"><span>{neurons.length} bodies · {edges.length} raw directed edges</span><div><button onClick={() => setZoom(z => Math.max(1, z - 0.5))} aria-label="Zoom out graph">−</button><button onClick={() => setZoom(1)}>Fit diagram</button><button onClick={() => setZoom(z => Math.min(4, z + 0.5))} aria-label="Zoom in graph">+</button></div></div>
    <p className="graph-limit">{shown.length < edges.length ? 'Display cap: first ' + shown.length + ' of ' + edges.length + ' edges in source-ID order. Narrow to a body, path, or filter to inspect the rest.' : 'All filtered edges shown.'} Arrows show source → target. Width uses √(raw count / visible maximum), not activation strength.</p>
    <div className="graph-scroll"><svg viewBox="0 0 1000 730" style={{ width: zoom * 100 + '%', minWidth: 720 }} role="group" aria-label="Abstract body-level raw structural diagram; positions are not anatomical">
      <defs><marker id={marker} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#9fb4ab" /></marker></defs>
      {shown.map(edge => {
        const a = positions.get(edge.source)!, b = positions.get(edge.target)!;
        const dx = b.x - a.x, dy = b.y - a.y, distance = Math.hypot(dx, dy) || 1;
        const endX = b.x - dx / distance * 11, endY = b.y - dy / distance * 11;
        const bend = 14;
        const path = edge.source === edge.target ? 'M ' + a.x + ' ' + (a.y - 9) + ' C ' + (a.x + 35) + ' ' + (a.y - 48) + ', ' + (a.x - 35) + ' ' + (a.y - 48) + ', ' + (a.x - 5) + ' ' + (a.y - 10)
          : 'M ' + a.x + ' ' + a.y + ' Q ' + ((a.x + b.x) / 2 - dy / distance * bend) + ' ' + ((a.y + b.y) / 2 + dx / distance * bend) + ' ' + endX + ' ' + endY;
        return <path key={edge.source + ':' + edge.target} d={path} fill="none" stroke="#9fb4ab" opacity={selected && (edge.source === selected || edge.target === selected) ? 0.95 : 0.3}
          strokeWidth={0.7 + 2.8 * Math.sqrt(edge.rawSynapseCount / maxCount)} markerEnd={'url(#' + marker + ')'}>
          <title>{edge.source + ' → ' + edge.target + ': ' + edge.rawSynapseCount + ' raw synapses · IN-PACKAGE ONLY'}</title></path>;
      })}
      {neurons.map(node => {
        const p = positions.get(node.bodyId)!; const active = highlights.has(node.bodyId);
        return <g key={node.bodyId} transform={'translate(' + p.x + ',' + p.y + ')'} role="button" tabIndex={0} aria-label={(node.type ?? 'Unknown') + ' body ' + node.bodyId} aria-pressed={selected === node.bodyId}
          onClick={() => select(node.bodyId)} onKeyDown={event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); event.stopPropagation(); select(node.bodyId); } }}>
          <title>{(node.type ?? 'Unknown') + ' · ' + node.bodyId + ' · ' + node.evidence.join(' / ') + ' · ' + (node.anatomy.status === 'UNAVAILABLE' ? 'ANATOMY UNAVAILABLE FOR THIS BODY' : 'SOURCE-BACKED SWC')}</title>
          <circle r={active ? 12 : 9} fill={nodeColor(node)} stroke={selected === node.bodyId || active ? '#fff' : '#162820'} strokeWidth={selected === node.bodyId || active ? 3 : 1.5} />
          <text y={-14} textAnchor="middle" fill="#f1f4e9" fontSize="10">{node.type ?? '?'}</text>
          <text y={23} textAnchor="middle" fill="#d0ddd4" fontSize="9">{node.bodyId}{node.side ? ' ' + node.side : ''}{active ? ' · USER' : ''}</text>
        </g>;
      })}
    </svg></div><p className="real-notice">ABSTRACT LAYOUT — NOT ANATOMICAL COORDINATES. Grouping by type is a display choice.</p>
  </div>;
}
