# Data and evidence contract

## Source records

The three Feather inputs are content-pinned in config/sources.json. The graph uses only bodies with the source status exactly equal to Traced. The complete annotation status distribution is retained in atlas_summary.json. This is a technical inclusion rule, not a declaration that every excluded fragment is biologically irrelevant.

Every original annotation field is preserved. NT fields acquire the prefix nt_ to avoid conflating source identity and cell-type predictions. Source nulls remain null. Body IDs stay int64 internally and decimal strings in candidate exports. A contiguous node_index is assigned after sorting source IDs. It has meaning only with this run's atlas.

The derived sensory_modality_annotation copies the source class only for ol_sensory, cb_sensory, and vnc_sensory superclasses. Other neurons remain unassigned by this particular rule; they are not declared irrelevant to sensation. visual_superclass_annotation covers ol_sensory, ol_intrinsic, visual_projection, and visual_centrifugal. This set is a starting population, not the complete visual circuit.

## Raw edges

edges.parquet contains pre_index, post_index, synapse_count, and source_row. Source-row indices are zero-based across the Feather record batches. Counts are positive integers, including one-synapse edges. Rows are not collapsed, thresholded, signed, or interpreted as effective connectivity. The original source table uses the column name weight; this project names its contents synapse_count to distinguish them from model weights.

Synapses crossing the Traced boundary are counted for each included endpoint. In/out totals therefore distinguish the included graph from contributions of excluded partners. A runtime subgraph will require the same accounting plus an explicit treatment of omitted activity.

## Coordinates and side hints

has_source_hex_pair requires two finite integral coordinate values. source_column_usable additionally requires a visual superclass and an unconflicted L/R annotation hint. The side grouping uses somaSide where it is L/R, otherwise rootSide where it is L/R. When both are L/R and disagree, the hint is missing. The original side fields and the chosen basis remain available.

This grouping does not establish eye of origin, crossed projections, viewing direction, or anatomical orientation. The coordinate frame is the source's assignedOlHex1/2 frame. No universal pixel spacing, angular spacing, visual field of view, or transform between left and right eyes is assumed.

## Candidate support

An anchor is a neuron with a usable source column pair. For photoreceptor-labelled bodies, the method collects outgoing synapse counts onto anchors. For other neurons in the visual population, it collects incoming counts from anchors. Only matching nonmissing side hints contribute. Self loops are excluded. Counts from all anchors at the same column are summed, and all supported columns are retained in column_support.npz.

The top column is only a summary statistic. Ties are flagged; the first column index is used as a deterministic tie-break. A broad distribution may reflect a wide receptive field, uncertainty, partner coverage, or a failure of this simple method. Entropy and top-support fraction cannot distinguish those explanations and are not calibrated probabilities of correctness.

anchor_coverage_fraction uses all source partners, including excluded bodies, in its denominator. It measures the fraction of relevant-direction raw synapses captured by the anchors, not the fraction of physiological input explained.

All candidate records retain physiologically_validated=false, angular_calibration_status=UNAVAILABLE, and stimulus_binding_status=UNMAPPED. No candidate replaces an original annotation. The method is a local baseline, not a reproduction of the published MaleCNS visual-pathway algorithm.

## Holdout interpretation

Within each type/side stratum, approximately 20% of usable source coordinate pairs are withheld from the anchor set, with seed 20261008. Predictions are made without those neuron-coordinate assignments or target self loops. The source column vocabulary is retained; this is transductive within-animal evaluation. Predictions are scored against the withheld pairs, with coverage, exact match, and top-candidate ties reported separately.

The coordinates are source annotations that may themselves have used connectivity. This test measures internal consistency and prevents direct label copying. It supplies neither independent physiological validation nor evidence that an inferred R1-R6 or T4/T5 field is correct. Those target populations lack local source column annotations and are not represented by this holdout score.

