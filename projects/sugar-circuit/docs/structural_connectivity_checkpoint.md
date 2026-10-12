# Structural connectivity checkpoint — Gates 2 and 3

6 October 2026. Run `results/structural/20261006T180116Z`.

**STRUCTURAL CONNECTIVITY ONLY.** Gates 2 and 3 are finished within the bounds below. Gate 1 identities were reused. The structural searches, body-level edge checks, comparisons and visualization exports are complete; Puddle's identity and the paper's exact computational methods remain unresolved. No effective-connectivity calculation, statistical replication, physiological simulation or polished biological figure was produced. No strict computational replication is claimed.

The graph supports many alternative routes, including routes through GNG021. Structural reachability does not establish activation, inhibition, physiological importance or a sugar-specific pathway. In particular, a neuron appearing in these dense unthresholded graphs is not evidence that the paper's selection algorithm would retain it.

## Dataset and raw-edge validation

**VERIFIED:** authenticated `male-cns:v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`. Start and end Meta records agree on family/tag, UUID, last database edit and latest mutation ID `1006591300`. Last edit: `2026-03-28 11:56:30.222612573-04:00 / 2026-06-08T01:31:39-04:00 (segment property update)`. See [raw/meta_start.json](../results/structural/20261006T180116Z/raw/meta_start.json) and [raw/meta_end.json](../results/structural/20261006T180116Z/raw/meta_end.json).

The complete [official released graph](https://male-cns.janelia.org/download/) is retained at `data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather`: **88,384,522 segment endpoints and 151,856,684 directed body pairs**. These are segments, not 88 million identified neurons. The raw weight sum is **311,833,243**, matching live Meta `totalPostCount`. Weights range from 1 to 2,591; no duplicate body pair or nonpositive weight was found. The download's GCS MD5 and local checksum agree; SHA256 is `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1`. [raw/flat_weights_provenance.json](../results/structural/20261006T180116Z/raw/flat_weights_provenance.json); [analysis/graph_summary.json](../results/structural/20261006T180116Z/analysis/graph_summary.json).

All **746,910 unique exported edges** were checked against authenticated `ConnectsTo.weight`; **zero neuPrint/flat-file disagreements** were found. This comprises 118,272 complete targeted-query comparisons, containing overlaps, and 628,729 additional pair checks. Raw responses also retain `weightHP` and `weightHR`; neither variant controls this search. Every exported edge has query provenance. Agreement compares two representations of the same reconstruction, not independent biological measurements. [edge_source_comparison.csv](../results/structural/20261006T180116Z/edge_source_comparison.csv); [path_edge_source_comparison.csv](../results/structural/20261006T180116Z/path_edge_source_comparison.csv); [raw_edges.csv](../results/structural/20261006T180116Z/raw_edges.csv).

## Search definition, bounds and preservation

The starting bodies remain LB3a 17 (9 L/8 R), LB3b 11 (5 L/6 R), LB3c 23 (12 L/11 R), and LB3d 26 (11 L/15 R). Targets are four MN4a bodies and two each of MN6, MN8 and MN9. MN4b is excluded from the **target list**, not silently removed as a possible graph intermediate. Missing `entryNerve` for LB3c 957530 remains missing; the body is retained.

Reachability and shortest directed distances use the entire released graph with **no hop cutoff**. All edge costs are one for this purpose; synapse counts remain raw annotations. No synapse-count, ROI, annotation, tracing-status, hemisphere or intermediate-type filter was applied. The filename's `minconf-0.5` is release preprocessing, not a new filter or a verified paper-method parameter.

Before choosing a bound, forward expansion and motor-compatible lower-bound corridors were measured at depths 0–7. For A, the corridor grows from 1,854 nodes/40,533 edges at depth 3, to 23,960/358,931 at depth 4, to 89,113/4,490,174 at depth 5. Corridor counts may include bounded walks and therefore exceed exact simple-path membership. This sharp expansion motivated the uniform **maximum of four edges** for simple paths, with smaller bounds retained. This is an analysis choice, not the paper's pruning algorithm. [graph_growth_by_depth.csv](../results/structural/20261006T180116Z/graph_growth_by_depth.csv); [search_config.json](../results/structural/20261006T180116Z/search_config.json).

Every directed **vertex-simple** path within four hops was visited for A–D and for each of E's two separate legs. A path cannot revisit a body. Other sensory bodies and motor bodies may occur internally; targets are not made absorbing, and no cell class is removed from the graph. Thus “LB3b only” describes the starting population, not a ban on other sensory intermediates. At four hops, B and C each contain all 77 LB3 bodies somewhere in their path unions. This matters when defining a later sugar-restricted experiment.

Counts and node/edge memberships are exhaustive **within these bounds**. Saved simple-path examples are capped at **100 per ordered body pair and exact hop count**, in ascending-body-ID traversal order, without weight ranking. The cap did not affect membership or counting. **195,120 examples** are saved from 364,457,645 paths counted across the three query scopes (A, sensory→GNG021 and GNG021→motor). All **33,851 shortest paths** for all 944 tested ordered pairs were saved; the 10,000-per-pair safety cap was never reached. Exact omitted-example counts are in [path_enumeration_counts.csv](../results/structural/20261006T180116Z/path_enumeration_counts.csv). No completeness beyond four-hop simple paths is asserted.

## Paper-associated named edges

**VERIFIED current raw structure:** all four Quasimodo/GNG042→GNG015 body pairs exist:

| Source | GNG015 L 523590 | GNG015 R 28181 |
| --- | --- | --- |
| Quasimodo L 15321 | 73 | 88 |
| Quasimodo R 15734 | 87 | 81 |

All eight GNG015→MN4a pairs and all four GNG015→MN9 pairs exist:

| Source | MN9 L 10331 | MN9 R 16949 | MN4a L 18295 | MN4a L 36368 | MN4a R 27938 | MN4a R 522704 |
| --- | --- | --- | --- | --- | --- | --- |
| GNG015 L 523590 | 266 | 16 | 49 | 31 | 10 | 13 |
| GNG015 R 28181 | 177 | 19 | 19 | 18 | 7 | 41 |

These are synapse counts, not activation strengths. GNG042 and GNG015 have supplied GABA prediction/consensus labels; their physiological effects were not tested. [named_neuron_edge_validation.csv](../results/structural/20261006T180116Z/named_neuron_edge_validation.csv); [nodes.csv](../results/structural/20261006T180116Z/nodes.csv).

Clavicle/ANXXX462a connects to Sternum/GNG585: **514625 L→10961 L:59**, **514625 L→13611 L:39**, **19480 R→12402 R:80**. Sternum has two listed left bodies and one right body; none was collapsed. Its branches through Roundup/GNG108 (523040 L, 26764 R), Roundtree/GNG120 (513162 L, 10881 R), and GNG472 (46013 L, 524254 R) reach the illustrated motor classes. Alias/type/side checks for these additional records match live neuPrint in all 54 compared fields. [analysis/additional_alias_crosscheck.json](../results/structural/20261006T180116Z/analysis/additional_alias_crosscheck.json); [paper_associated_paths.csv](../results/structural/20261006T180116Z/paper_associated_paths.csv).

**SOURCE CONFLICT — descriptive paper/current comparison:** all 12 mapped type-pair motifs have current structural edges, but eight pooled raw totals differ from [Figure 6I/J](../paper/primary/figure6.jpg):

| Source type | Target type | Figure label | Current all-body sum | Difference |
| --- | --- | --- | --- | --- |
| GNG042 | GNG015 | 329 | 329 | 0 |
| GNG015 | MN9 | 473 | 478 | 5 |
| GNG015 | MN4a | 188 | 188 | 0 |
| ANXXX462a | GNG585 | 179 | 178 | -1 |
| GNG585 | GNG108 | 835 | 835 | 0 |
| GNG585 | GNG120 | 359 | 350 | -9 |
| GNG108 | MN9 | 376 | 381 | 5 |
| GNG108 | MN4a | 98 | 135 | 37 |
| GNG120 | MN9 | 441 | 443 | 2 |
| GNG120 | MN4a | 89 | 98 | 9 |
| GNG585 | GNG472 | 244 | 244 | 0 |
| GNG472 | MN8 | 205 | 221 | 16 |

The figure's exact pooling, snapshot and selection rules are unresolved. These discrepancies do not identify their cause, and are **not neuPrint/flat-file disagreements**. Four equal totals also do not establish strict replication. [paper_motif_comparison.csv](../results/structural/20261006T180116Z/paper_motif_comparison.csv).

The illustration is not a complete raw adjacency list. Current direct motor totals also include:

| Source type | MN4a | MN6 | MN8 | MN9 |
| --- | --- | --- | --- | --- |
| GNG042 | 0 | 0 | 1 | 0 |
| ANXXX462a | 0 | 0 | 0 | 0 |
| GNG015 | 188 | 2 | 155 | 478 |
| GNG021 | 4 | 167 | 25 | 3 |

For example, GNG015→MN8 totals 155, while Quasimodo→MN8 has a single weight-1 edge; Clavicle has no direct edge to any requested motor. Tested absent individual pairs are recorded with `present=False` in the named validation matrix, not inserted as zero-weight edges into the graph.

**BLOCKED — SOURCE REQUIRED:** Puddle has no match in the six searched flat annotation fields or the live synonym/instance query. Figure 6 names Puddle but does not establish its MaleCNS body IDs. Its claimed identity cannot be validated here. All current two-edge Quasimodo→intermediate→MN8 bridges are preserved in [quasimodo_mn8_unassigned_bridges.csv](../results/structural/20261006T180116Z/quasimodo_mn8_unassigned_bridges.csv), without renaming any intermediate Puddle. A paper source-data/curator mapping is needed. [analysis/puddle_identity_audit.json](../results/structural/20261006T180116Z/analysis/puddle_identity_audit.json).

## Circuits A–D and routes to individual motors

**VERIFIED:** no starting LB3 body directly connects to a requested motor. All 770 body pairs are reachable: 718 shortest distances are two hops and 52 are three. Each circuit independently uses its specified starting bodies; named neurons are not required in route selection. Shared graph preparation does not change the separate per-source searches. [source_target_reachability.csv](../results/structural/20261006T180116Z/source_target_reachability.csv); [shortest_paths.csv](../results/structural/20261006T180116Z/shortest_paths.csv).

| Circuit | Starting population | Nodes ≤4 | Edges ≤4 | Simple paths ≤4 |
| --- | --- | --- | --- | --- |
| A | all 77 LB3a–d | 23207 | 354639 | 223,674,804 |
| B | 11 LB3b | 16252 | 257482 | 32,967,386 |
| C | 23 LB3c | 16156 | 274236 | 73,630,850 |
| D | 34 LB3b+LB3c | 19833 | 311760 | 106,598,236 |

Shortest-distance ranges across individual starting bodies, preserving each motor ID:

| Motor body | LB3a | LB3b | LB3c | LB3d |
| --- | --- | --- | --- | --- |
| MN9 L 10331 | 2–3 | 2–3 | 2–3 | 2–3 |
| MN8 L 16827 | 2 | 2 | 2–3 | 2–3 |
| MN9 R 16949 | 2–3 | 2–3 | 2–3 | 2–3 |
| MN4a L 18295 | 2–3 | 2–3 | 2 | 2–3 |
| MN8 R 20173 | 2 | 2–3 | 2 | 2 |
| MN4a R 27938 | 2–3 | 2–3 | 2 | 2 |
| MN4a L 36368 | 2 | 2 | 2–3 | 2–3 |
| MN6 R 519667 | 2–3 | 2–3 | 2–3 | 2–3 |
| MN4a R 522704 | 2–3 | 2 | 2 | 2 |
| MN6 L 924612 | 2–3 | 2–3 | 2–3 | 2–3 |

A, B, C and D retain all ten motors. Individual body paths and their raw edge weights are in [simple_paths.csv](../results/structural/20261006T180116Z/simple_paths.csv), [lb3b_paths.csv](../results/structural/20261006T180116Z/lb3b_paths.csv), [lb3c_paths.csv](../results/structural/20261006T180116Z/lb3c_paths.csv) and [lb3b_lb3c_combined_paths.csv](../results/structural/20261006T180116Z/lb3b_lb3c_combined_paths.csv). The latter three contain capped examples; the table above and [circuit_summary.csv](../results/structural/20261006T180116Z/circuit_summary.csv) use exhaustive memberships/counts. Path-count differences are not tests of whole-path dominance and are affected by unequal numbers of starting bodies.

Full-LB3 component origins, including overlap:

| Origin | Starting bodies | Nodes supported | Edges supported | Nodes unique among a–d | Edges unique among a–d |
| --- | --- | --- | --- | --- | --- |
| LB3a | 17 | 16272 | 259692 | 958 | 10868 |
| LB3b | 11 | 16252 | 257482 | 727 | 8316 |
| LB3c | 23 | 16156 | 274236 | 1044 | 19157 |
| LB3d | 26 | 19878 | 307086 | 1715 | 22394 |

Membership for every body/edge is retained in `source_subtype_membership`. [full_lb3_component_origins.csv](../results/structural/20261006T180116Z/full_lb3_component_origins.csv).

## Shared structure, convergence and divergence

At the four-hop bound, B and C share **12,575 nodes and 219,958 edges**. B has **3,677 nodes/37,524 edges** absent from C; C has **3,581 nodes/54,278 edges** absent from B. Excluding the fixed 77 sensory and ten motor endpoints leaves **12,488 shared intermediate segments**, with the same unique-segment counts. “Intermediate” does not imply a fully annotated interneuron. [structural_node_comparison.csv](../results/structural/20261006T180116Z/structural_node_comparison.csv); [structural_edge_comparison.csv](../results/structural/20261006T180116Z/structural_edge_comparison.csv).

**INTERPRETATION:** there are **zero combined-only nodes, edges or paths** under identical static graph bounds: paths from a union of source sets equal the union of their separate paths. Combination can reveal convergence motifs without creating new routes. There are **663 nodes** with at least two incoming partners in D but at most one in each separate B/C graph. [combined_only_convergence_motifs.csv](../results/structural/20261006T180116Z/combined_only_convergence_motifs.csv); [structural_comparison_summary.json](../results/structural/20261006T180116Z/structural_comparison_summary.json).

| Circuit | Convergence nodes (in-degree >1) | Divergence nodes (out-degree >1) | Opposite-side endpoint edges | Unknown-side edges |
| --- | --- | --- | --- | --- |
| A | 13214 | 15060 | 134755 | 49647 |
| B | 8481 | 10646 | 101723 | 28240 |
| C | 8635 | 10635 | 107237 | 32835 |
| D | 11024 | 12937 | 120457 | 38954 |
| E | 19579 | 23287 | 186884 | 88641 |

Per-body partners, degrees, source-subtype support and shared incoming branches are available in [convergence_divergence.csv](../results/structural/20261006T180116Z/convergence_divergence.csv). Convergence/divergence are graph properties, not evidence of simultaneous activation or summation.

The search discovers numerous intermediates beyond the requested names. Examples ranked by the number of distinct sensory–motor body pairs whose **shortest** paths contain the body are:

| Body/type/side | Body pairs | Body NT prediction | Consensus |
| --- | --- | --- | --- |
| 12230 GNG043 L | 380 | unclear | histamine |
| 12808 GNG043 R | 256 | serotonin | histamine |
| 556512 GNG089 R | 241 | acetylcholine | acetylcholine |
| 15030 GNG467 R | 126 | acetylcholine | acetylcholine |
| 21828 GNG215 R | 122 | acetylcholine | acetylcholine |
| 15450 DNge057 L | 114 | acetylcholine | acetylcholine |
| 512730 GNG089 L | 113 | acetylcholine | acetylcholine |
| 31018 GNG232 R | 109 | acetylcholine | acetylcholine |

This is descriptive route occurrence, not functional importance. All 900 bodies appearing as shortest-path intermediates are listed in [important_intermediates.csv](../results/structural/20261006T180116Z/important_intermediates.csv); all other bounded-path intermediates remain in the node/edge tables. The histamine consensus versus unclear/serotonin body predictions for GNG043 illustrate why the two NT fields cannot be silently substituted.

## Circuit E — GNG021 hypothesis

**VERIFIED:** neither GNG021 body—27203 L or 521222 R—receives a direct edge from any of the 77 LB3 bodies. All **154** LB3→GNG021 ordered pairs have shortest length **2**, including every subtype and source side. This is an indirect structural candidate, not a direct LB3 recipient or a paper-selected neuron. [named_neuron_edge_validation.csv](../results/structural/20261006T180116Z/named_neuron_edge_validation.csv); [source_target_reachability.csv](../results/structural/20261006T180116Z/source_target_reachability.csv).

Both bodies structurally reach all ten motor bodies. Direct counts and unbounded shortest lengths are:

| Motor | 27203 L direct count | Hops | 521222 R direct count | Hops |
| --- | --- | --- | --- | --- |
| MN9 L 10331 | 2 | 1 | 1 | 1 |
| MN8 L 16827 | 16 | 1 | 9 | 1 |
| MN9 R 16949 | 0 | 2 | 0 | 2 |
| MN4a L 18295 | 3 | 1 | 0 | 2 |
| MN8 R 20173 | 0 | 2 | 0 | 2 |
| MN4a R 27938 | 0 | 2 | 1 | 1 |
| MN4a L 36368 | 0 | 2 | 0 | 2 |
| MN6 R 519667 | 50 | 1 | 12 | 1 |
| MN4a R 522704 | 0 | 2 | 0 | 2 |
| MN6 L 924612 | 42 | 1 | 63 | 1 |

Zero means no direct record in the release, not no indirect route. Shortest motor distances are one or two hops. Direct MN8 and MN9 outputs occur only to the left target bodies, whereas both MN6 bodies receive direct edges; this is not left/right weight symmetry. All four LB3 source populations have symmetric two-hop *reachability* to both candidates, which does not imply symmetric edge weights.

Strongest raw upstream/downstream partners for each candidate (top five by synapse count, complete unfiltered lists retained separately):

| GNG021 body | Direction | Partner body/type/side | Synapses |
| --- | --- | --- | --- |
| 27203 | upstream | 520669 GNG028 L | 269 |
| 27203 | upstream | 12582 GNG025 L | 231 |
| 27203 | upstream | 12664 GNG140 L | 231 |
| 27203 | upstream | 12474 GNG025 R | 214 |
| 27203 | upstream | 11506 GNG028 R | 161 |
| 27203 | downstream | 12851 GNG095 L | 264 |
| 27203 | downstream | 28181 GNG015 R | 228 |
| 27203 | downstream | 523590 GNG015 L | 216 |
| 27203 | downstream | 555256 GNG017 L | 175 |
| 27203 | downstream | 11844 GNG142 L | 138 |
| 521222 | upstream | 11506 GNG028 R | 271 |
| 521222 | upstream | 12474 GNG025 R | 232 |
| 521222 | upstream | 12582 GNG025 L | 206 |
| 521222 | upstream | 13528 GNG169 R | 196 |
| 521222 | upstream | 523993 GNG069 R | 195 |
| 521222 | downstream | 43765 GNG095 R | 270 |
| 521222 | downstream | 28181 GNG015 R | 182 |
| 521222 | downstream | 523590 GNG015 L | 157 |
| 521222 | downstream | 519661 GNG142 R | 131 |
| 521222 | downstream | 555270 GNG017 R | 123 |

[gng021_partners.csv](../results/structural/20261006T180116Z/gng021_partners.csv) retains every partner, ranks, NT fields, membership and reciprocal status. The upstream lists establish convergence from multiple distinct bodies, including GNG028, GNG025 and GNG140, as well as Quasimodo. Intermediate paths from each sensory subtype are preserved in [gng021_candidate_paths.csv](../results/structural/20261006T180116Z/gng021_candidate_paths.csv) and the complete shortest-path file.

GNG021 overlaps directly with the Quasimodo/GNG015 network:

- Quasimodo **15321→27203:98; 15321→521222:82; 15734→27203:79; 15734→521222:120**.
- GNG021 **27203→523590:216; 27203→28181:228; 521222→523590:157; 521222→28181:182**, where the targets are GNG015 L/R.
- Reverse GNG021→Quasimodo edges are **27203→15321:9; 27203→15734:6; 521222→15321:3; 521222→15734:6**.
- GNG015 **523590→27203:1** and **28181→521222:1** provide additional reciprocal motifs. The GNG021 pair itself has **27203→521222:9** and **521222→27203:7**.

Every number joins to [named_neuron_edge_validation.csv](../results/structural/20261006T180116Z/named_neuron_edge_validation.csv). Opposite-side body pairs are explicit; the crossing neurite has not been identified anatomically. These feedback motifs do not establish physiological recurrence or sign.

**INTERPRETATION:** GNG021 survives the structural search as an indirectly reachable, motor-connected candidate. Its neighborhood overlaps the known network, so it is not a structurally disjoint replacement for Quasimodo/GNG015. A distinct functional role and paper membership remain unverified. Post hoc examples containing Quasimodo→GNG021→GNG015 are kept separately in [gng021_overlap_examples.csv](../results/structural/20261006T180116Z/gng021_overlap_examples.csv), explicitly not claimed as a paper motif.

E's **34,576 nodes/536,440 edges** are the union of **LB3→GNG021 paths up to four hops** and **GNG021→motor paths up to four hops**, traced independently. These counts are not directly comparable with A's single end-to-end four-hop bound and do not claim exhaustive eight-hop sensory–motor paths. Independently, the unrestricted A search contains **3,641,392 actual simple sensory–motor paths through GNG021 within four hops**, covering all 770 sensory–motor body pairs. [gng021_end_to_end_path_counts.csv](../results/structural/20261006T180116Z/gng021_end_to_end_path_counts.csv).

## Recurrence and left/right interpretation

Every A–E bounded path-union graph forms one strongly connected component at four hops; accordingly all of its path-union edges lie on a directed cycle **in that union graph**. The cycle may be longer than an individual four-hop path. No repeated-vertex walk was enumerated as a simple path. The export plus explicitly added reciprocal/self-loop context contains **643,924 cycle edges**, **145,594 distinct reciprocal pairs**, and **78 self-loops**. [recurrent_edges.csv](../results/structural/20261006T180116Z/recurrent_edges.csv); [reciprocal_pairs.csv](../results/structural/20261006T180116Z/reciprocal_pairs.csv); [circuit_summary.csv](../results/structural/20261006T180116Z/circuit_summary.csv).

There are **55,599 three-edge cycle records around GNG021 in the exported graph**, indexed by the candidate body at which the cycle starts; cycles containing both candidates can therefore appear twice. This is not an enumeration of every full-connectome cycle. [gng021_three_edge_cycles.csv](../results/structural/20261006T180116Z/gng021_three_edge_cycles.csv).

The A path union includes **997 motor-origin edges**, 524 of weight one. Examples include MN4a 27938→GNG108 26764 (33) and MN8 16827→GNG120 513162 (17), both independently query-checked. These records explain why an absorbing-motor interpretation cannot be silently substituted for the actual search. Presynaptic placement/segmentation and functional interpretation need separate manual review. [motor_origin_edges_in_circuit_A.csv](../results/structural/20261006T180116Z/motor_origin_edges_in_circuit_A.csv).

All four endpoint-side combinations are preserved before bilateral summaries: **185 L→L**, **185 L→R**, **200 R→R**, **200 R→L** sensory–motor body pairs, all reachable. The graph uses sensory `rootSide` and other bodies' available `somaSide`/`rootSide`, retaining the original fields and provenance. [left_right_comparison.csv](../results/structural/20261006T180116Z/left_right_comparison.csv); [path_counts_by_side.csv](../results/structural/20261006T180116Z/path_counts_by_side.csv).

The raw export contains **221,159 opposite-side endpoint edges** and **210,710 edges with undetermined side relation**. Sample paths retain their full side sequence, opposite-side steps and unknown-side steps, including same-side endpoints whose path switches side internally. A side label is not a synapse coordinate: anatomical midline crossing and which neurite crosses remain **UNVERIFIED**, requiring morphology or synapse locations. Do not relabel every opposite-soma edge as an anatomically localized midline crossing.

Weight asymmetries are concrete: GNG015→MN9 totals **443 to left body 10331 versus 35 to right body 16949**; GNG021 has direct MN8/MN9 edges only to their left bodies; Sternum has two left bodies and one right. These are raw structural observations, without normalization or statistical testing.

## Uncertainties, audit and experiment design

- **BLOCKED — SOURCE REQUIRED:** Puddle's MaleCNS type/body mapping; full final main paper/STAR Methods; paper implementation/commit; exact effective-connectivity equation, normalization, bootstrap, pruning and simulation algorithm. These did not block the authorized structural phase.
- **UNVERIFIED:** the paper's exact dataset snapshot/pooling, causes of eight figure-total discrepancies, GNG021's paper membership, physiological interpretation of raw motor-origin edges and weak fragment connections, and anatomical crossing locations.
- **VERIFIED field distinctions, physiological policy unresolved:** 1,009 exported bodies have different nonempty body-NT prediction and consensus fields (509 unclear predictions; 500 differing named predictions). Thirty-three were already logged; all 976 newly encountered distinctions are retained in the mismatch ledger and [nt_field_distinctions.csv](../results/structural/20261006T180116Z/nt_field_distinctions.csv). Neither field was used to assign physiological sign.
- **Scope limitation:** 7,547 A nodes and 14,392 visualization nodes lack curated annotations; unknown type/side/class remain explicit. Weight-one edges are retained (146,675 in A). A later display or robustness filter must create a separately labeled derivative and retain this baseline.
- **Still not tested:** H1 whole-path dominance, physiological activation, paper algorithm selection and statistical/strict computational replication. A high path count is not evidence for any of them.

The three-experiment scaffold can remain. Its definitions need these clarifications before execution: experiment 1 must reconcile the paper snapshot/weight differences and missing method; experiment 2 must specify whether “restricted” means only starting inputs (as B–D do here) or additionally removing other sensory intermediates; experiment 3 should test GNG021 as an **indirect, overlapping candidate**, not a direct LB3 recipient or an already independent circuit. Puddle identity and an explicit NT interpretation policy remain prerequisites for any claims that rely on them. Experiment configurations remain drafts with `execution_allowed: false`.

## Files, validation and visualization readiness

The full raw graph is retained unchanged. `raw_edges.csv` is a **documented extracted view**, comprising unfiltered targeted-query neighborhoods, all bounded-path edges and reciprocal/self-loop context; it is not a CSV conversion of all 151 million graph edges. It contains 129,125 nodes/746,910 edges, leaving 88,255,397 nodes/151,109,774 edges outside that view. No nodes or edges were removed by a synapse threshold. [export_summary.json](../results/structural/20261006T180116Z/export_summary.json) records exact selection counts.

The visualization view has **37,246 nodes and 643,834 edges**. It omits 91,879 raw-context nodes and 103,076 raw-context edges that are outside bounded paths, feedback context and mapped paper motifs; they remain in the raw tables. [visualization_views.json](../results/structural/20261006T180116Z/visualization_views.json) defines A/B/C/D/E and the paper-associated view. The paper-associated route file contains 3,564 explicitly labeled routes, selected only after the unrestricted searches; it does not define A–D.

Required outputs: [nodes.csv](../results/structural/20261006T180116Z/nodes.csv), [raw_edges.csv](../results/structural/20261006T180116Z/raw_edges.csv), [source_target_reachability.csv](../results/structural/20261006T180116Z/source_target_reachability.csv), [shortest_paths.csv](../results/structural/20261006T180116Z/shortest_paths.csv), [simple_paths.csv](../results/structural/20261006T180116Z/simple_paths.csv), [recurrent_edges.csv](../results/structural/20261006T180116Z/recurrent_edges.csv), [left_right_comparison.csv](../results/structural/20261006T180116Z/left_right_comparison.csv), [lb3b_paths.csv](../results/structural/20261006T180116Z/lb3b_paths.csv), [lb3c_paths.csv](../results/structural/20261006T180116Z/lb3c_paths.csv), [lb3b_lb3c_combined_paths.csv](../results/structural/20261006T180116Z/lb3b_lb3c_combined_paths.csv), [gng021_candidate_paths.csv](../results/structural/20261006T180116Z/gng021_candidate_paths.csv), [named_neuron_edge_validation.csv](../results/structural/20261006T180116Z/named_neuron_edge_validation.csv).

Graph export: [circuit_graph.graphml](../results/structural/20261006T180116Z/circuit_graph.graphml), plus [visualization_nodes.csv](../results/structural/20261006T180116Z/visualization_nodes.csv) and [visualization_edges.csv](../results/structural/20261006T180116Z/visualization_edges.csv). Metadata support body IDs, types/classes, raw annotations, both NT fields, side provenance, edge weight/direction, recurrence, shared/unique membership and source-subtype contribution. Raw responses and exact query files live under `raw/` and `queries/`; full-graph caches/distances and processing logs are under `analysis/`. Additional named, comparison, convergence, growth, NT and provenance tables are indexed in [README.md](../results/structural/20261006T180116Z/README.md); scientific artifacts and requests/responses are hashed in [manifest.json](../results/structural/20261006T180116Z/manifest.json).

**Validation:** four synthetic behavior tests pass, including cycles, bounds, multiple targets, source-set union, unreachable vertices, SCC direction and annotation grouping. Export checks join every saved path weight and side sequence to the verified body-edge tables, verify shortest-path completeness and path-example caps, check recurrence certificates, and parse GraphML with exact weight/referential-integrity checks. All required files pass. [validation_checks.json](../results/structural/20261006T180116Z/validation_checks.json); [analysis/search_tests.log](../results/structural/20261006T180116Z/analysis/search_tests.log).

**Ready for side-by-side structural visualization:** yes, using the declared view definitions and preserving unknown annotations, raw strengths and predicted NT labels. The graph is dense; a readable final figure will need explicit display choices. Puddle cannot yet be given a verified body label, and the figures must not imply physiology or strict replication.

**Stop point:** Gates 2 and 3 only. No effective-connectivity, statistical replication or simulation is authorized by this checkpoint. See [STATUS](../STATUS.md), [claim ledger](../logs/claim_ledger.csv), [mismatch ledger](../logs/mismatch_ledger.csv), [query log](../logs/query_log.jsonl), [decisions](../logs/decision_log.md) and [unresolved questions](../logs/unresolved_questions.md).

