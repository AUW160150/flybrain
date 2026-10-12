import type { SourceMode } from '../data/contracts';

/** Complete vocabulary; reserved labels do not imply an attached simulator. */
export const SOURCE_LABELS: Record<SourceMode, string> = {
  USER_DRIVEN_ILLUSTRATION: 'USER_DRIVEN_ILLUSTRATION',
  RULE_DRIVEN_EDUCATIONAL: 'RULE_DRIVEN_EDUCATIONAL',
  DATA_REPLAY: 'DATA_REPLAY',
  REDUCED_CIRCUIT_SIMULATION: 'REDUCED_CIRCUIT_SIMULATION',
  FULL_CONNECTOME_SIMULATION: 'FULL_CONNECTOME_SIMULATION',
  UNVERIFIED: 'UNVERIFIED',
};
