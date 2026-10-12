/** Dataset identity and evidence remain separate from display state. IDs are strings. */
export type EvidenceStatus =
  | 'ANATOMY_VERIFIED' | 'LITERATURE_SUPPORTED' | 'STRUCTURAL_CANDIDATE'
  | 'USER_DRIVEN_ILLUSTRATION' | 'RULE_DRIVEN_EDUCATIONAL'
  | 'DATA_REPLAY' | 'SIMULATED' | 'UNVERIFIED';

export type SourceMode =
  | 'USER_DRIVEN_ILLUSTRATION' | 'RULE_DRIVEN_EDUCATIONAL' | 'DATA_REPLAY'
  | 'REDUCED_CIRCUIT_SIMULATION' | 'FULL_CONNECTOME_SIMULATION' | 'UNVERIFIED';
export type ImplementedSourceMode = Extract<SourceMode, 'USER_DRIVEN_ILLUSTRATION' | 'RULE_DRIVEN_EDUCATIONAL'>;

export interface BrainRegionRecord {
  id: string;
  name: string;
  role?: string;
  evidence: EvidenceStatus[];
  sourceRefs: string[];
  geometryStatus: 'VERIFIED_ANATOMY' | 'PLACEHOLDER_GEOMETRY' | 'UNAVAILABLE';
}

export interface NeuronRecord {
  bodyId: string;
  type?: string;
  aliases: string[];
  side?: 'L' | 'R' | 'M' | 'UNKNOWN';
  role?: string;
  regionIds: string[];
  neurotransmitterPrediction?: string;
  neurotransmitterConsensus?: string;
  evidence: EvidenceStatus[];
  sourceRefs: string[];
}

export interface EdgeRecord {
  sourceBodyId: string;
  targetBodyId: string;
  rawSynapseCount?: number;
  evidence: EvidenceStatus[];
  sourceRefs: string[];
}

export interface CircuitPackage {
  schemaVersion: 1;
  id: string;
  name: string;
  dataset: string;
  datasetVersion: string;
  datasetUuid?: string;
  label: 'RAW_STRUCTURAL' | 'PAPER_ASSOCIATED' | 'CANDIDATE' | 'SELECTED_EFFECTIVE_CONNECTIVITY' | 'EDUCATIONAL_DEMO';
  neurons: NeuronRecord[];
  edges: EdgeRecord[];
  regions: BrainRegionRecord[];
  metadata: Record<string, unknown>;
}

export interface ActivityFrame {
  timeMs: number;
  sourceMode: Exclude<SourceMode, 'UNVERIFIED'>;
  values: Record<string, number>;
  notes?: string;
}

export interface BehaviorEvent {
  id: string;
  name: string;
  startedAtMs: number;
  endedAtMs?: number;
  sourceMode: ActivityFrame['sourceMode'];
  circuitIds: string[];
}

export type CameraMode = 'WORLD_FOLLOW' | 'WORLD_ORBIT' | 'FLY_INSPECTION' | 'BRAIN_INSPECTION';
export type WorldCameraMode = Extract<CameraMode, 'WORLD_FOLLOW' | 'WORLD_ORBIT'>;
export type BehaviorCommand = 'TAKEOFF_LAND' | 'FEED' | 'GROOM' | 'ESCAPE' | 'COURTSHIP' | 'STOP';
export type MotionKey = 'FORWARD' | 'BACKWARD' | 'LEFT' | 'RIGHT';
export interface ControlEvent {
  id: string;
  timeMs: number;
  controlMode: 'USER';
  sourceMode: 'USER_DRIVEN_ILLUSTRATION';
  command: string;
  phase: 'PRESS' | 'RELEASE';
  input: 'KEYBOARD' | 'POINTER';
}

export interface FlyPose { x: number; y: number; z: number; heading: number }
export type MotionInput = Record<MotionKey, boolean>;

// Educational identities deliberately cannot be mistaken for dataset body IDs.
export type DemoId = `demo-${string}`;
export type ExplorationMode = 'USER_CONTROL' | 'EDUCATIONAL_RULE' | 'DATA_REPLAY';
export type RoleCategory = 'VISUAL' | 'TASTE' | 'MOTOR' | 'COURTSHIP' | 'INTEGRATION';
export type AnimationName = 'IDLE' | 'WALK' | 'TURN_LEFT' | 'TURN_RIGHT' | 'FEED' | 'GROOM' | 'TAKEOFF' | 'FLIGHT_IDLE' | 'LAND' | 'ESCAPE' | 'COURTSHIP' | 'STOP';
export type Point3 = [number, number, number];
export interface DemoEntity {
  id: DemoId;
  name: string;
  kind: 'REGION' | 'DEMO_NEURON';
  roleCategory: RoleCategory;
  description: string;
  geometryStatus: 'PLACEHOLDER_GEOMETRY';
  evidence: ['UNVERIFIED'];
  sourceRefs: string[];
  position: Point3;
}
export interface DemoRegion extends DemoEntity {
  kind: 'REGION';
  color: string;
  symbol: string;
  scale: Point3;
}
export interface DemoNeuron extends DemoEntity {
  kind: 'DEMO_NEURON';
  regionId: DemoId;
}
export interface DemoRelation {
  sourceId: DemoId;
  targetId: DemoId;
  kind: 'ILLUSTRATIVE_RELATION';
  evidence: ['UNVERIFIED'];
}
export interface DemoCircuitPackage {
  schemaVersion: 1;
  format: 'FLYWORLD_EDUCATIONAL_DEMO';
  id: DemoId;
  label: 'EDUCATIONAL_DEMO';
  name: string;
  regions: DemoRegion[];
  neurons: DemoNeuron[];
  relations: DemoRelation[];
  circuits: { id: DemoId; name: string; entityIds: DemoId[] }[];
  sourceRefs: string[];
  disclaimer: string;
}

export interface DisplayEvent {
  id: string;
  name: string;
  startMs: number;
  endMs: number | null;
  sourceMode: ImplementedSourceMode;
  evidence: ImplementedSourceMode;
  origin: 'LIVE_USER' | 'SCRIPTED_RULE' | 'BUNDLED_DEMO' | 'SESSION_RECORDING';
  values: Record<DemoId, number>;
  behavior: AnimationName;
  heldKey?: MotionKey;
  notes: string;
}
export interface DemoTimeline {
  schemaVersion: 1;
  id: DemoId;
  label: 'SYNTHETIC_EDUCATIONAL_REPLAY';
  durationMs: number;
  events: DisplayEvent[];
  sourceRefs: string[];
}
