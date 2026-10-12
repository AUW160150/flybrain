# Protocol versus paper audit — initial checkpoint

6 October 2026. This audit uses the final primary sources actually retrieved. “CONFIRMED BY PAPER” below means supported by the named figure, supplement or Table S1; it does not mean the full main paper/Methods were read. No item is classified CONFIRMED BY CODE because no paper-specific implementation was identified.

| Protocol assumption or question | Classification | Evidence and consequence | Claims |
|---|---|---|---|
| Paper circuit starts with LB3a–d | CONFIRMED BY PAPER | Figure 6G and S16A contain all four; restricting replication to b/c would change the input | C013 |
| LB3b/c are the sugar-associated labellar populations of interest | CONFIRMED BY PAPER | Figure 2D–E maps them to Gr64f; association is morphological/receptor-based | C011 |
| LB3b overlaps other modalities | CONFIRMED BY PAPER | Figure 2 labels LB3b sugar/low salt and relates it to Ir56b | C011 |
| LB3b/c are exclusively sugar-sensing | UNSUPPORTED for c; CONTRADICTED for b | Exclusivity does not follow from receptor-image matching; b also has low-salt association | C011 |
| All LB3 subtypes are sugar-sensing | CONTRADICTED | Figure 2 labels a as water and d as high salt/heavy metal-associated | C012 |
| Quasimodo is GNG042 | PARTIALLY SUPPORTED by retrieved paper material; VERIFIED in v1.0 | Paper panels name Quasimodo; P09/P12 synonyms explicitly map GNG042 to Quasimodo | C008, C020 |
| Clavicle is ANXXX462a | PARTIALLY SUPPORTED by retrieved paper material; VERIFIED in v1.0 | P09/P12 explicitly provide the alias; paper Figure 6 and S17 name Clavicle | C008, C021 |
| GNG015 participates in the Quasimodo disinhibitory route | CONFIRMED BY PAPER | Figure 6I and S17; specifically illustrated for MN9/MN4a; MN8's illustrated branch uses Puddle | C020 |
| GNG021 is in / absent from the paper | UNCLEAR | No exact match in extracted supplement and not named in inspected relevant panels; inaccessible text and unnamed nodes prevent an absence claim | C024 |
| GNG021 route is already paper-confirmed or selected | UNSUPPORTED | v1.0 existence and NT prediction do not establish its edges or algorithmic selection | C009–C010, C024 |
| Motor targets are MN4a, MN6, MN8, MN9 | CONFIRMED BY PAPER | Figure 6G/S16 and Table S1; IDs corroborate in v1.0 | C007, C013 |
| MN4 is an interchangeable query name for MN4a/MN4b | CONTRADICTED | S12C distinguishes types; exact MN4 query finds none | C014 |
| Effective-connectivity equation and normalization are settled | UNCLEAR | Full STAR Methods and code are missing; no equation accepted from snippets | C028 |
| Percentile rules are settled | PARTIALLY SUPPORTED | S16 verifies the 99th-percentile initial criterion; later pruning rule and percentile universe need Methods/code | C019, C028 |
| Hop rules are settled | PARTIALLY SUPPORTED | Seven-hop heatmaps and 3/4-hop motifs are supported; general iteration/termination is not | C017, C021 |
| Bootstrap procedure is settled | PARTIALLY SUPPORTED | S13 identifies two bootstrapped reference distributions and upper 95% CI limits; exact sampling settings unknown | C018 |
| Paper used male-cns:v1.0 | UNCLEAR | Do not substitute present-day access verification for paper provenance | C027, C029 |
| H1: LB3c contributes more strongly to the complete Quasimodo route | PARTIALLY SUPPORTED for the published first-edge plot; UNSUPPORTED for whole-path/v1.0 dominance | S16A visually supports c > b at the first edge; raw v1.0 edges and full paths have not been assessed | C023 |
| Structural presence means functional significance | UNSUPPORTED | No functional validation or new circuit experiments performed at this checkpoint | C010, C028 |
| Raw NT and consensus can be used interchangeably | CONTRADICTED by v1.0 records | 22 unclear and 11 named body predictions differ from consensus; preserve both | C026 |

The protocol already cautions against exclusive sugar labeling and forcing GNG021 into results. Those are appropriate safeguards, not errors attributed to the user. The corrections above identify interpretations that must not enter the future implementation.

## Structural-only follow-up

[Gate 2/3 findings](structural_connectivity_checkpoint.md) establish current raw structural routes, not the unresolved paper algorithm. GNG021 is an indirect overlapping candidate; Puddle identity remains unmapped. Eight pooled figure/current counts differ. The original paper-method audit remains partial; no strict replication or physiological inference is added.


## 2026-10-06T21:56:23.667556+00:00 — prompt_1.md follow-up

- The 80th-percentile rule remains UNVERIFIED; prompt text alone is not a method source.
- S16A explicitly labels GNG232 and DNg67; S19 labels DNg67/Fudog and DNge080/Rounddown. Preserve Tastekin structural-panel evidence alongside the separate, future Shiu comparison. This is not proof of Figure 6G selection. C061/M1283.
- The eight mismatched Figure 6 labels cannot be reproduced by whole-body/whole-raw-edge deletion plus additive pooling using the current mapped counts. Snapshot, synapse filtering and other mapping/pooling remain unresolved. C059.
- The prompt supplies no numeric acceptable-recall threshold. Do not invent one, tune weights, or treat four matching raw totals as a passed method gate.
- Experiment 2 is explicitly source-only restriction. This resolves Q-016 without deleting other GRN relays. The final continuation instruction permits Experiment 2 only after a trustworthy Experiment 1R; that prerequisite is unmet.


## 2026-10-06T22:16:22.713335+00:00 — Final-text cross-check

Postsynaptic normalization, matrix propagation, both 80th-percentile criteria and unsigned effective connectivity are now CONFIRMED BY FINAL PAPER. Bootstrap constants are recovered from the final Methods; the preprint lacks that dedicated section. The source-pack anchors are independently confirmed, but source-pack text alone is not used as evidence. Complete significant-path execution rules remain PARTIALLY SUPPORTED. Seven-hop heatmaps do not establish a seven-hop Figure 6G iterator. Simulation-only proofread/sign settings do not establish EC graph filters. See [diff and implementation limits](final_vs_preprint_method_diff.md), C075–C083.
