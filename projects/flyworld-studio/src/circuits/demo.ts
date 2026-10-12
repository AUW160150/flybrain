import source from '../../public/data/demo/foundation.json';
import educational from '../../public/data/demo/educational-circuits.json';
import { parseCircuitPackage } from '../data/schema';
import { parseDemoPackage } from '../data/demoSchema';
import type { AnimationName, DemoEntity, DemoId } from '../data/contracts';

export const demoPackage = parseCircuitPackage(source);
export const PLACEHOLDER_LABEL = 'PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA';
export const educationalPackage = parseDemoPackage(educational);
export const demoEntities: DemoEntity[] = [...educationalPackage.regions, ...educationalPackage.neurons];
export const entityById = new Map(demoEntities.map(e => [e.id, e]));
export const demoIds: ReadonlySet<string> = new Set(entityById.keys());
export const regionForEntity = (id: string) => educationalPackage.regions.find(r => r.id === id || educationalPackage.neurons.some(n => n.id === id && n.regionId === r.id));

export function relationsForEntity(id: DemoId) {
  const entity = entityById.get(id);
  const members = new Set(entity?.kind === 'REGION' ? educationalPackage.neurons.filter(n => n.regionId === id).map(n => n.id) : [id]);
  return {
    upstream: [...new Set(educationalPackage.relations.filter(r => members.has(r.targetId) && !members.has(r.sourceId)).map(r => r.sourceId))],
    downstream: [...new Set(educationalPackage.relations.filter(r => members.has(r.sourceId) && !members.has(r.targetId)).map(r => r.targetId))],
  };
}

/** Explicit UI associations requested for this demo, never biological connectivity. */
export const behaviorTargets: Record<AnimationName, DemoId[]> = {
  IDLE: [], STOP: [],
  WALK: ['demo-motor-system', 'demo-motor-left-01', 'demo-motor-right-01'],
  TURN_LEFT: ['demo-motor-system', 'demo-motor-left-01'],
  TURN_RIGHT: ['demo-motor-system', 'demo-motor-right-01'],
  FEED: ['demo-taste-system', 'demo-taste-01', 'demo-taste-02', 'demo-feed-motor-01'],
  ESCAPE: ['demo-visual-system', 'demo-visual-01', 'demo-visual-02', 'demo-escape-motor-01'],
  GROOM: ['demo-central-system', 'demo-grooming-01'],
  COURTSHIP: ['demo-mating-system', 'demo-mating-01', 'demo-mating-02'],
  TAKEOFF: ['demo-motor-system', 'demo-flight-motor-01'],
  FLIGHT_IDLE: ['demo-motor-system', 'demo-flight-motor-01'],
  LAND: ['demo-motor-system', 'demo-flight-motor-01'],
};
