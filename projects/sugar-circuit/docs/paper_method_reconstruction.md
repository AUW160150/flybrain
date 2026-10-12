# Paper method reconstruction — initial checkpoint

**PARTIAL; BLOCKED — SOURCE REQUIRED.** The complete final Results and STAR Methods have not been obtained or read. The reconstruction below is limited to retrieved final primary material: Figures 2/6, the final supplemental PDF and Table S1. Equations, defaults and implementation details have not been inferred from search snippets.

The final citation and full author list are in [SOURCES.md](../SOURCES.md) (C001). The associated algorithm repository, paper-used commit and paper's precise MaleCNS snapshot remain UNVERIFIED (C027–C028, C032). The new target release, `male-cns:v1.0`, is independently verified through public and authenticated records (C029).

## Verified parts of the method

| Component | Reconstructed fact / numerical parameter | Primary location | Claim |
|---|---|---|---|
| GRN subtype classification | lbGRN output connectivity; hierarchical clustering; cosine similarity; stated threshold **2 synapses** | P02, S2B–D legend, PDF p.22; figure p.3 | C015 |
| Reconstruction exclusions | **8 right + 9 left** incomplete MaleCNS lbGRNs excluded from this clustering | P02, S2B legend, PDF p.22 | C015 |
| LB3 definitions | LB3a–d are subtypes in the output-connectivity clustering | P02, S2; P03, GRNs sheet | C015 |
| Modality/receptor matching | LB3a: water/ppk28; LB3b: sugar and low salt, Ir56b; LB3b/c: Gr64f; LB3d: high salt/heavy metal association, Ir47a image | P04, Figure 2D–E | C011–C012 |
| Motor cell typing | Input connectivity; cosine similarity; stated threshold **5 synapses**, with morphology comparison | P02, S12A–C legend, PDF p.25; figure p.13 | C016 |
| Motor identity | MN4a corresponds to prior MN4; MN4b is separately identified | P02, S12C legend, PDF p.25; P03 MNs sheet | C014 |
| Baseline circuit populations | LB3a–d to MN4a, MN6, MN8, MN9 | P05, Figure 6G; P02, S16A–E | C013 |
| Effective-connectivity display | S13A heatmap: maximum **7 hops**, Ward clustering | P02, S13A legend, PDF p.25 | C017 |
| Reachability/reference thresholds | S13B plots successive hops against two references: upper **95% confidence limits** from GRN-based and random-neuron bootstrapped distributions | P02, S13B legend, PDF pp.25–26; figure p.14 | C018 |
| Initial downstream selection | LB3 subtype weight to a partner must exceed the **99th percentile** to qualify for S16B–E comparisons | P02, S16 legend, PDF pp.26–27; figure p.17 | C019 |
| Bilateral information in S16 | Ipsilateral and contralateral scores are shown as distinct observations | P02, S16B–E legends, PDF p.27 | C019 |
| Disinhibitory motif | **3 hops from GRNs**; Quasimodo → GNG015 → MN9/MN4a; MN8 branch shown through Puddle | P05, Figure 6I; P02, S17A | C020–C021 |
| Feedforward motif | Clavicle route illustrated at **4 hops from GRNs** | P05, Figure 6J; P02, S17A | C021 |
| Simulation design | **6 conditions**, LB3 drive **200 Hz**, GNG015 drive **100 Hz** in tonic-drive conditions, **30 simulations per condition** | P02, S17A–B legend, PDF p.27 | C022 |
| Simulation comparisons | Wilcoxon rank-sum test; Holm correction | P02, S17B legend, PDF p.27 | C022 |

The figures support morphological/receptor associations; they do not establish exclusive sensory selectivity. The different numerical criteria above belong to different analysis stages. Neither the classification thresholds nor the top-partner percentile should be silently applied to the entire graph.

The illustrated simulation conditions are LB3 drive alone; plus Clavicle silencing; plus GNG015 drive; plus GNG015 drive and Quasimodo silencing; plus GNG015 drive and Clavicle silencing; and plus GNG015 drive and both silenced. These are reported paper conditions, not runs performed here.

## Required method details still unresolved

| Requested item | Status and missing evidence |
|---|---|
| Complete GRN identification procedure | PARTIALLY SUPPORTED by annotations, Table S1 and S2; full tracing/seeding and cross-dataset matching Methods required |
| Fine LB3 definitions and exact receptor-matching procedure | PARTIALLY SUPPORTED by Figure 2/S2; full anatomical matching Methods and limitations required |
| Motor-neuron identification pipeline | PARTIALLY SUPPORTED by S12/Table S1; complete tracing and validation procedure required |
| Synapse filtering and cleft-score thresholds | BLOCKED — SOURCE REQUIRED. The v1.0 filename's minconf-0.5 and database metadata are not automatically the paper settings |
| Adjacency construction and edge weighting | BLOCKED — SOURCE REQUIRED. Need included neurons, ROI policy, handling of untyped/untraced fragments and raw-versus-aggregated weights |
| Effective-connectivity equation | BLOCKED — SOURCE REQUIRED. No verified equation entered |
| Normalization | BLOCKED — SOURCE REQUIRED. Need denominators, zero handling, population aggregation and normalization timing |
| Multi-hop propagation | PARTIALLY SUPPORTED by S13/S17; matrix orientation, recurrence, cumulative versus exact-hop interpretation and cycles require Methods/code |
| Bootstrapping, nulls and random sampling | PARTIALLY SUPPORTED by S13B; resample count, sample size, replacement, sampling universe, CI estimator and seeds unverified |
| Significant-path selection and pruning | PARTIALLY SUPPORTED by S16 initial selection; later percentile rules, iteration and stopping logic unverified |
| Bilateral pooling | PARTIALLY SUPPORTED by separate ipsi/contra points; aggregation and population averaging unverified |
| Neurotransmitter handling | PARTIALLY SUPPORTED by Figure 6's predicted signs; source/version, confidence rule and inclusion in effective connectivity unverified |
| Disinhibition enrichment analysis | Motif is supported; enrichment denominator, null model and statistical implementation require full Results/Methods |
| Network simulation implementation | S17 design supported; integration parameters, defaults, basal rates, simulation duration, input mapping and exact code version unverified |

No code file/function can yet be assigned as the paper's implementation. These gaps prevent a faithful implementation. The final article's accessibility is the stop condition; independent annotation checks were completed because the user explicitly requested them at this checkpoint.

## Body identity evidence

The [resolved-body file](../results/validation/20261006T171922Z/resolved_bodies.csv) includes all 95 targets, each with raw identity fields, side provenance, nerve fields, NT predictions, confidence and consensus. The [Table S1 comparison](../results/validation/20261006T171922Z/table_s1_comparison.csv) verifies 87 sensory/motor records. The eight interneuron identities and aliases are supported directly by v1.0 annotation and neuPrint records, not fabricated Table S1 mappings.

The annotation agreement does not verify connectivity weights, pathway selection or snapshot equivalence with the paper. Refer to C006–C010, C025–C030.


## 2026-10-06T21:56:23.667556+00:00 — Independent method recovery for prompt_1.md

**Still PARTIAL; main replication blocked.** Live v1.0 identity passed again. The final supplement and Table S1 were re-fetched and are byte-identical to the earlier copies. Main final paper/STAR Methods requests returned 403; full API 401. Author-linked PDF also returned 403. Search-index excerpts were treated as discovery leads, not a substitute for the missing source. No exact algorithm or numerical assumption was adopted.

Full parameter records with the requested ten fields, plus a criticality flag, are in [results/method_recovery/20261006T214639Z/method_parameters.csv](../results/method_recovery/20261006T214639Z/method_parameters.csv). Blank code/function fields mean no paper-specific implementation was recovered. VERIFIED values have narrow figure/stage scopes and do not imply a verified complete method.

| Parameter | Value / equation | Source and location | Verification | Missing detail / scope |
| --- | --- | --- | --- | --- |
| replication_input_types | LB3a;LB3b;LB3c;LB3d | paper/primary/figure6.jpg; paper/supplement/supplemental_information.pdf; LB3 circuit; Figure 6G; S16A / PDF p17 | VERIFIED_FROM_FINAL_PAPER | Current full body membership was validated earlier; exact paper graph/body filtering is still unresolved. |
| requested_motor_types | MN4a;MN6;MN8;MN9 | paper/primary/figure6.jpg; paper/supplement/supplemental_information.pdf; Proboscis positioning; Figure 6G; S16B-E / PDF p17 | VERIFIED_FROM_FINAL_PAPER |  |
| grn_clustering_synapse_threshold | 2 | paper/supplement/supplemental_information.pdf; S2 legend; PDF p22 | VERIFIED_FROM_SUPPLEMENT | Typing only; not a graph-wide replication edge cutoff. |
| incomplete_lbgrn_exclusion_for_typing | 8 right; 9 left | paper/supplement/supplemental_information.pdf; S2B legend; PDF p22 | VERIFIED_FROM_SUPPLEMENT | Not established as the effective-connectivity graph rule. |
| motor_clustering_synapse_threshold | 5 | paper/supplement/supplemental_information.pdf; S12 legend; PDF p25 | VERIFIED_FROM_SUPPLEMENT | Typing only. |
| effective_heatmap_max_hops | 7 | paper/supplement/supplemental_information.pdf; S13A legend; PDF p25 | VERIFIED_FROM_SUPPLEMENT | Does not establish exact/cumulative propagation or the significant-path hop limit. |
| heatmap_clustering | Ward | paper/supplement/supplemental_information.pdf; S13A legend; PDF p25 | VERIFIED_FROM_SUPPLEMENT | Display-stage rule. |
| hop_plateau_termination | not recovered | paper/supplement/supplemental_information.pdf; S13B legend; PDF pp25-26 | PARTIAL | Plateau equation, tolerance and implementation missing. |
| grn_bootstrap_reference | upper 95% confidence limit | paper/supplement/supplemental_information.pdf; S13B legend; PDF pp25-26 | VERIFIED_FROM_SUPPLEMENT | Estimator, sampling and comparison rule unresolved. |
| random_neuron_reference | upper 95% confidence limit | paper/supplement/supplemental_information.pdf; S13B legend; PDF pp25-26 | VERIFIED_FROM_SUPPLEMENT | Sampling universe and estimator unresolved. |
| s16_partner_percentile | exceeds 99th percentile | paper/supplement/supplemental_information.pdf; S16A-E legend; PDF pp26-27 | VERIFIED_FROM_SUPPLEMENT | Percentile denominator/population, aggregation, and estimator are not specified here. |
| s16_laterality | ipsilateral and contralateral scores displayed separately | paper/supplement/supplemental_information.pdf; S16B-E legend; PDF p27 | VERIFIED_FROM_SUPPLEMENT | Does not define bilateral pooling for Figure 6 weights. |
| display_normalization_per_motor | not recovered | paper/supplement/supplemental_information.pdf; S15 legend; S18C legend; PDF pp26-27 | PARTIAL | Do not substitute this display rule for the unknown edge/layer normalization. |
| disinhibitory_motif_depth | 3 hops from GRNs | paper/primary/figure6.jpg; Disinhibition; Figure 6I | VERIFIED_FROM_FINAL_PAPER | Not the general path-search limit. |
| feedforward_motif_depth | 4 hops from GRNs | paper/primary/figure6.jpg; Feedforward excitation; Figure 6J | VERIFIED_FROM_FINAL_PAPER | Not the general path-search limit. |
| graph_neuron_universe | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Typed/untyped fragments, brain/VNC, ROI and status inclusions unknown. |
| connectivity_matrix_orientation | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Body-level directed records available; paper matrix orientation and construction unknown. |
| cleft_score_filter | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Search-index text mentions 50, but full final Methods were not obtained; scale and mapping to v1 minconf-0.5 are unverified. |
| replication_synapse_weight_filter | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Do not import the typing thresholds or released filename as paper rules. |
| edge_weight_equation | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Raw anatomical counts available; paper normalized-weight equation missing. |
| edge_normalization_denominator | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Total postsynaptic input versus presynaptic output versus included-network sums unresolved. |
| effective_connectivity_equation | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | No verified equation; do not infer ordinary matrix powers. |
| multi_hop_aggregation | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Exact hop versus cumulative hop, route aggregation and population aggregation unresolved. |
| layer_hop_normalization | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Equation, denominator and timing unresolved. |
| significant_path_hop_limit | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Cannot infer from seven-hop heatmaps or 3/4-hop illustrations. |
| significant_path_percentile_80 | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | 80th percentile is requested in prompt_1.md but not independently verified. |
| percentile_population | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Zeros, body/type pooling, per-layer or whole-network comparison unresolved. |
| percentile_estimator_and_ties | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Quantile interpolation and equality handling unresolved. |
| selection_direction | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Input-to-output versus output-to-input scoring/combination unresolved. |
| pruning_iteration | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Rules, iteration order and stopping condition unresolved. |
| recurrence_handling | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Self-loops, revisits, sensory relays and absorbing motors unresolved. |
| bootstrap_replicates | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | No verified replicate count. |
| bootstrap_grn_sample_size | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Current 77 LB3 bodies do not establish paper null sample size. |
| bootstrap_random_neuron_sample_size | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | No verified control sample size. |
| bootstrap_sampling_universe_replacement | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Eligible neurons and replacement policy missing. |
| bootstrap_ci_estimator_seed | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | Estimator and random seed missing. |
| paper_body_vs_type_bilateral_pooling | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | No verified summation/averaging or selected-body inventory. |
| paper_motif_extraction_rule | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | 99th-percentile S16 partner rule cannot automatically be assigned to every Fig6 motif. |
| neurotransmitter_in_metric | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | No explicit paper metric sign policy recovered; preserve metadata, do not insert signs. |
| paper_snapshot | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | MaleCNS family known; analysis release/mutation/adjacency hash unknown. |
| official_analysis_code_version | not recovered | Final Results/STAR Methods and publication-linked implementation required; Not retrieved;  | UNVERIFIED | No publication-specific implementation identified in checked repositories. |

RECONSTRUCTED_METHOD_ASSUMPTION: **none adopted**. The gaps concern selection-changing definitions, so a sensitivity analysis around guessed equations would not establish replication. Keep the mathematics implementation and biological execution gated. The six new arithmetic tests exercise only the raw pooling audit.


## 2026-10-06T22:16:22.713335+00:00 — Source-pack recovery and verified algebra core

Current status: **FINAL_METHOD_SECTIONS_RECOVERED_SELECTION_DETAILS_UNRESOLVED**. Earlier source-access statements above describe their dated checkpoints. The user source pack authorized indexed final text, which exposed the relevant Methods; the full preprint v2 XML was also recovered and compared. See [final/preprint audit](final_vs_preprint_method_diff.md) and `results/method_recovery/20261006T220302Z/`.

The unsigned postsynaptic-normalized matrix core and explicit-reference threshold/pruning helpers are implemented. **27 tests pass: 21 new mathematical/helper tests plus six weight-audit tests.** Three synthetic comparisons establish that remaining reference-population, pooling and hop choices change candidate membership. These are not biological results.

Figure 6G graph eligibility/filter/denominator scope, score grouping/pooling, percentile reference populations/estimator and iterative hop/candidate policy still need primary definitions. Experiment 1R, all sugar conditions and simulation remain unrun. No method freeze, selected circuit or functional inference is claimed. The prior raw audit remains 4/12 exact and eight unexplained discrepancies. Live v1.0 UUID is unchanged. Claims C074–C085; mismatches M1287–M1289.

Current detailed parameter inventory: [48 parameter rows](../results/method_recovery/20261006T220302Z/method_parameters.csv). Recovered values and unresolved implementation fields are separated. Earlier tables remain historical.


### Follow-up 2026-10-07T22:18:43.582985+00:00
Additional official software and author/lab repository checks did not resolve B01–B04. All four source lists and fixed motor targets are cross-checked and prepared, but no biological selection ran. The existing 27 tests pass. See [sequential checklist](workflow_next_steps.txt), [new audit](../results/workflow/20261007T221035718347Z/report.txt), and [unsent request](tastekin_methods_request.txt). The full method remains unfrozen; generic package defaults were not imported.
