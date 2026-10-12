# Run 20261006T180116Z

**STRUCTURAL CONNECTIVITY ONLY** — authenticated male-cns:v1.0 / UUID 4b2087c0fbe046bfaf0d60bc970e3e5d. [Checkpoint](../../../docs/structural_connectivity_checkpoint.md).

The full released Feather is `../../../data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather`. No synapse-count/type/side/status/ROI cutoff was used. Raw CSV and GraphML files are selected views with exact scope/counts in `export_summary.json`; they do not replace the complete retained Feather.

Source selection for B/C changes the starting bodies only. Other sensory and motor bodies may be internal vertices. Simple paths cannot repeat vertices. Counts/memberships are exhaustive up to four hops; CSV examples are capped at 100 per ordered pair and hop. E separately bounds each leg to four hops; it does not enumerate all eight-hop end-to-end paths.

`circuit_membership` means an edge/node occurs on a searched simple path within the bound. `context_circuit_membership` identifies reciprocal or self-loop context that need not itself occur on such a path. `recurrence_status` refers to SCC cycle membership in the exported graph; `recurrent_circuits` refers to the individual bounded path-union graphs. A union graph can contain cycles even though each enumerated path is simple.

`source_subtype_membership` is provenance for sensory-to-motor A–D paths; it does not mean functional input strength. Side relationships use soma/root annotation labels, not anatomical synapse crossings. NT body prediction, confidence, consensus and ground-truth source fields remain distinct. GraphML contains selected display fields; nodes.csv retains all raw annotations. Display classification is derived from the supplied superclass; uncertain/missing annotations remain explicit.

`known_paper_motif` marks mapped type-pair motifs, not an assertion that the paper published each individual body edge. `paper_associated_paths.csv` supplies sensory-inclusive named views after unrestricted extraction. Puddle remains unmapped. `weightHP`/`weightHR` are preserved source variants but do not control topology.

A raw CSV edge references `raw/<query>.json`; the corresponding exact Cypher/request is `queries/<query>.json`. Query logs and manifests store hashes. Start/end Meta agree; all exported edges match the full flat source. IDs are integers, direction is source→target, weights are raw counts. Missing edges in the named matrix are tested absences, not zero-weight graph edges.

## Files

| File | Purpose |
| --- | --- |
| [README.md](README.md) | Derived structural table/configuration; see checkpoint and column names. |
| [bounded_circuit_growth.csv](bounded_circuit_growth.csv) | Exact simple-path union membership at bounds 1–4. |
| [circuit_graph.graphml](circuit_graph.graphml) | Visualization graph; directed, numeric raw weights, node and edge metadata. |
| [circuit_summary.csv](circuit_summary.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [combined_only_convergence_motifs.csv](combined_only_convergence_motifs.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [convergence_divergence.csv](convergence_divergence.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [dataset_identity.json](dataset_identity.json) | Derived structural table/configuration; see checkpoint and column names. |
| [edge_source_comparison.csv](edge_source_comparison.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [export_summary.json](export_summary.json) | Counts outside each exported view; no weight-based removal. |
| [full_lb3_component_origins.csv](full_lb3_component_origins.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [gng021_candidate_paths.csv](gng021_candidate_paths.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [gng021_end_to_end_path_counts.csv](gng021_end_to_end_path_counts.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [gng021_overlap_examples.csv](gng021_overlap_examples.csv) | 3,264 exact named-pattern paths, explicitly candidate extensions rather than paper claims. |
| [gng021_partners.csv](gng021_partners.csv) | Complete raw incoming and outgoing partners, not a top-partner cutoff. |
| [gng021_three_edge_cycles.csv](gng021_three_edge_cycles.csv) | Candidate-anchored length-3 cycles in export; not full-connectome cycle enumeration. |
| [graph_growth_by_depth.csv](graph_growth_by_depth.csv) | Prebound full-graph growth (0–7), including lower-bound walk corridors. |
| [important_intermediates.csv](important_intermediates.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [lb3b_lb3c_combined_paths.csv](lb3b_lb3c_combined_paths.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [lb3b_paths.csv](lb3b_paths.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [lb3c_paths.csv](lb3c_paths.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [left_right_comparison.csv](left_right_comparison.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [manifest.json](manifest.json) | Input/output/script hashes, environment and audit snapshot. |
| [motor_origin_edges_in_circuit_A.csv](motor_origin_edges_in_circuit_A.csv) | 997 verified motor-origin edges retained by the nonabsorbing-target definition. |
| [named_neuron_edge_validation.csv](named_neuron_edge_validation.csv) | Positive edges and tested absences for sensory/named/motor queries. |
| [named_overlap_path_counts.csv](named_overlap_path_counts.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [nodes.csv](nodes.csv) | All extracted body/segment metadata, annotation JSON, side source, NT fields and exact bounded memberships. |
| [nt_field_distinctions.csv](nt_field_distinctions.csv) | 1,009 distinct nonempty NT field pairs; no sign assignment. |
| [paper_associated_paths.csv](paper_associated_paths.csv) | Post hoc named view, 3,564 paths; not an input restriction on A–D. |
| [paper_motif_comparison.csv](paper_motif_comparison.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [path_counts_by_side.csv](path_counts_by_side.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [path_edge_source_comparison.csv](path_edge_source_comparison.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [path_enumeration_counts.csv](path_enumeration_counts.csv) | Exact path counts and saved counts per ordered pair/depth. |
| [quasimodo_mn8_unassigned_bridges.csv](quasimodo_mn8_unassigned_bridges.csv) | All targeted two-edge bridges; no Puddle identity assigned. |
| [raw_edges.csv](raw_edges.csv) | All extracted edges; every weight checked against live neuPrint. Full unfiltered release retained in data/raw Feather. |
| [raw_validation_summary.json](raw_validation_summary.json) | Derived structural table/configuration; see checkpoint and column names. |
| [reciprocal_pairs.csv](reciprocal_pairs.csv) | Each distinct two-body reciprocal pair once; self-loops separate. |
| [recurrent_edges.csv](recurrent_edges.csv) | Cycle edges in export graph; separate from vertex-simple path records. |
| [search_config.json](search_config.json) | Explicit bounds, caps, no-filter rules, rationale and exclusions from scientific scope. |
| [shortest_paths.csv](shortest_paths.csv) | All 33,851 shortest paths; no truncation. |
| [simple_paths.csv](simple_paths.csv) | 195,120 deterministic examples; cap 100 per pair/hop; not a complete path listing. |
| [source_target_reachability.csv](source_target_reachability.csv) | 944 individually identified ordered pairs; full-graph directed distances and exact per-depth path counts. |
| [structural_comparison_summary.json](structural_comparison_summary.json) | Derived structural table/configuration; see checkpoint and column names. |
| [structural_edge_comparison.csv](structural_edge_comparison.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [structural_node_comparison.csv](structural_node_comparison.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [supplemental_summary.json](supplemental_summary.json) | Derived structural table/configuration; see checkpoint and column names. |
| [validation_checks.json](validation_checks.json) | Export/path/GraphML checks. |
| [visualization_edges.csv](visualization_edges.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [visualization_nodes.csv](visualization_nodes.csv) | Derived structural table/configuration; see checkpoint and column names. |
| [visualization_views.json](visualization_views.json) | Six view definitions; E leg bounds differ from A–D end-to-end bounds. |

`queries/` and `raw/` preserve requests/responses, including a failed DNS-only batch transport attempt and successful standard requests. `analysis/export_attempt1.log` records an interrupted export with a redundant set-intersection computation; moving that computation outside the loop changed execution cost, not graph selection or results. `audit_snapshot/` preserves the final ledgers/status.

## Reproducibility

Python 3.12 with requirements-structural.txt. Scripts 05–07 build the complete sparse graph, inspect growth and enumerate bounded simple paths. Script 06 compares complete boundary queries. Script 08 plans pair checks and reciprocal context. After authenticated responses are saved, scripts 09–12 export, summarize and validate. Script 13 writes this report. They use config/current_structural_run.txt and saved source/response files. Exact request JSON is retained; network retrieval uses the user credential only in a temporary ignored curl config, removed after the run. To reproduce, create a fresh timestamped directory and update that pointer; do not overwrite the baseline. No paper-method defaults, signs, simulation or random sampling are implemented.
