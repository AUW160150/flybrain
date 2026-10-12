import mappings from '../../config/educational_behavior_mappings.json';
import { eventIntensity } from '../activity/timeline';
import type { StudioState } from '../state/store';
import type { RealPackage } from './schema';

export type Isolation = 'ALL' | 'INCOMING' | 'OUTGOING' | 'ONE_HOP' | 'PATH';
export interface GraphFilters { side: string; evidence: string; type: string; isolation: Isolation; selected: string | null; pathIndex: number }
export const initialFilters: GraphFilters = { side: 'ALL', evidence: 'ALL', type: 'ALL', isolation: 'ALL', selected: null, pathIndex: 0 };
export function filterGraph(pkg: RealPackage, filters: GraphFilters) {
  let allowed: Set<string> | null = null;
  let pathPairs: Set<string> | null = null;
  if (filters.isolation === 'PATH') {
    const path = pkg.paths[filters.pathIndex];
    allowed = new Set(path?.bodyIds ?? []);
    pathPairs = new Set(path?.bodyIds.slice(1).map((id, i) => path.bodyIds[i] + ':' + id) ?? []);
  } else if (filters.isolation !== 'ALL' && filters.selected) {
    allowed = new Set([filters.selected]);
    pkg.edges.forEach(edge => {
      if (filters.isolation !== 'OUTGOING' && edge.target === filters.selected) allowed!.add(edge.source);
      if (filters.isolation !== 'INCOMING' && edge.source === filters.selected) allowed!.add(edge.target);
    });
  }
  const neurons = pkg.neurons.filter(n =>
    (!allowed || allowed.has(n.bodyId)) && (filters.side === 'ALL' || (n.side ?? 'UNKNOWN') === filters.side) &&
    (filters.evidence === 'ALL' || n.evidence.includes(filters.evidence as typeof n.evidence[number])) &&
    (filters.type === 'ALL' || (n.type ?? 'UNKNOWN') === filters.type));
  const ids = new Set(neurons.map(n => n.bodyId));
  const edges = pkg.edges.filter(e => ids.has(e.source) && ids.has(e.target) &&
    (!pathPairs || pathPairs.has(e.source + ':' + e.target)) &&
    (filters.isolation !== 'INCOMING' || e.target === filters.selected) &&
    (filters.isolation !== 'OUTGOING' || e.source === filters.selected) &&
    (filters.isolation !== 'ONE_HOP' || e.source === filters.selected || e.target === filters.selected));
  return { neurons, edges };
}
export function partners(pkg: RealPackage, id: string) {
  return { incoming: pkg.edges.filter(e => e.target === id), outgoing: pkg.edges.filter(e => e.source === id) };
}
export function realHighlights(pkg: RealPackage, state: StudioState) {
  if (state.mode !== 'USER_CONTROL') return { bodyIds: new Set<string>(), value: 0, mapping: null };
  const mapping = mappings.mappings[0];
  const event = state.events.filter(e => e.behavior === mapping.behavior && e.sourceMode === 'USER_DRIVEN_ILLUSTRATION' && e.origin === 'LIVE_USER').at(-1);
  const value = event && mapping.enabled ? Math.max(0, ...Object.keys(event.values).map(target => eventIntensity(event, target, state.timelineMs, state.reducedMotion))) : 0;
  return { bodyIds: new Set(value > 0 ? pkg.neurons.filter(n => mapping.types.includes(n.type ?? '') && n.packageMemberships.includes(mapping.circuitPackage)).map(n => n.bodyId) : []),
    value, mapping: value > 0 ? mapping : null };
}
export function graphPositions(pkg: Pick<RealPackage, 'neurons'>) {
  const positions = new Map<string, { x: number; y: number }>();
  const types = [...new Set(pkg.neurons.map(n => n.type ?? 'UNKNOWN'))].sort();
  const columns = Math.max(1, Math.ceil(Math.sqrt(types.length * 1.4)));
  const rows = Math.max(1, Math.ceil(types.length / columns));
  types.forEach((type, index) => {
    const members = pkg.neurons.filter(n => (n.type ?? 'UNKNOWN') === type);
    const cx = (index % columns + 0.5) * 1000 / columns, cy = (Math.floor(index / columns) + 0.5) * 700 / rows;
    members.forEach((node, i) => {
      const angle = i * Math.PI * 2 / members.length - Math.PI / 2;
      const radius = members.length === 1 ? 0 : Math.min(1000 / columns, 700 / rows) * 0.33;
      positions.set(node.bodyId, { x: cx + Math.cos(angle) * radius, y: cy + Math.sin(angle) * radius });
    });
  });
  return positions;
}
