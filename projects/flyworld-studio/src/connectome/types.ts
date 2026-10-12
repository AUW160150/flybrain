export const DATASET = 'male-cns:v1.0';
export const DATASET_UUID = '4b2087c0fbe046bfaf0d60bc970e3e5d';
export const MAX_BODIES = 24;
export type XYZ = [number, number, number];
export interface Neuron {
  bodyId: string; type: string | null; instance: string | null; synonyms: string | null;
  status: string; superclass: string | null; class: string | null; subclass: string | null;
  somaSide: string | null; rootSide: string | null; somaNeuromere: string | null;
  entryNerve: string | null; exitNerve: string | null; somaLocation: XYZ | null; tosomaLocation: XYZ | null;
}
export interface Edge { source: string; target: string; weight: number }
export interface Receipt { url: string; sha256: string; bytes: number; retrievedAt: string; range?: [number, number]; etag?: string; generation?: string }
export interface Skeleton { bodyId: string; points: number[][]; headers: string[]; source: Receipt; units: '8 nm'; coordinateSpace: 'MaleCNS native EM'; orientationStatus: 'UNVERIFIED' }
export interface Region { id: string; label: string; group: string }
export interface RegionMesh { id: string; vertices: number[]; indices: number[]; sources: Receipt[]; units: 'nm'; simplification:{method:'vertex-clustering';gridNm:number;sourceVertices:number} }
export interface Synapse { id: string; source: string; target: string; pre: XYZ; post: XYZ; confidencePre: number; confidencePost: number; roi: string | null }
export interface SynapseResult { synapses: Synapse[]; total: number; shown: number; minConfidence: number; source: string; target: string; sources: Receipt[]; units: '8 nm' }
export interface IndexManifest {
  dataset: string; uuid: string; neuronCount: number; edgeCount: number; annotationRows: number;
  synapseCount: number; scope: string; synapseConfidence: number; createdAt: string;
  sources: Record<string, { name: string; url: string; sha256: string; bytes: number }>;
}
