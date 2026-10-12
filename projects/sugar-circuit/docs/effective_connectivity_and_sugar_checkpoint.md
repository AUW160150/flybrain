# Effective connectivity and sugar checkpoint — source-pack continuation

**Recovered final method sections and implemented a tested mathematical core. Biological circuit selection remains source-gated.** New audit: `results/method_recovery/20261006T220302Z/`.

## Method and validation

The user-supplied source pack enabled independently retrieved indexed final Methods and a full, version-verified bioRxiv v2 XML. The [method diff](final_vs_preprint_method_diff.md) separates final confirmation, preprint wording and unresolved details. Final Cell governs; the preprint is not silently treated as identical. The final supplement/Table S1 remain the earlier verified copies. Full final PDF and publication-specific code remain unavailable in the sources checked.

The new [single core](../src/effective_connectivity.py) implements unsigned body-level synapse fractions using postsynaptic total inputs; exact-hop matrix propagation; explicitly referenced nonzero-mean scaling; strict percentile helpers; original-input AND output filtering of supplied scores; and induced raw adjacency. Body identities and laterality remain separate. 21 new tests and 6 prior weight-audit tests pass. This is not a completed iterative circuit selector or bootstrap/motif implementation.

Remaining selection-critical gaps concern graph/filter/denominator eligibility, body/type/bilateral pooling and normalization grouping, percentile comparison populations/estimator, and iterative candidate/horizon/stopping rules. Three synthetic examples demonstrate changed membership with the 80th percentile held fixed. The [48-row inventory](../results/method_recovery/20261006T220302Z/method_parameters.csv) distinguishes known equations from those gaps.

## Paper reproduction and raw weights

Authenticated metadata again verifies `male-cns:v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`, with unchanged mutation/edit identity. The structural baseline was reused.

Experiment 1R is NOT_RUN. Named-node/edge recovery, motor recovery, extra/missing selected neurons and topology precision/recall are NOT_ASSESSED, not zero. Puddle, Tentacular and the complete published selected inventory remain unresolved.

The [prior raw audit](paper_vs_v1_weight_audit.md) remains4/12 exact mapped motif totals and 8 unexplained differences. None of the 8 paper labels is a subset sum of the mapped current raw body-pair weights. Whole-body/whole-edge pruning alone with unchanged mappings and additive pooling is excluded. Historical adjacency, synapse-level filters and other pooling remain possible but unverified explanations. HP gives 0/12 exact and HR the same 4/12 as raw; no correct selected-weight result exists yet.

## Sugar conditions and candidate branches

LB3b, LB3c and their union remain NOT_RUN_METHOD_BLOCKED. Quasimodo/Clavicle/GNG015 retention, whole-path LB3c dominance, motor rankings, convergence and unique/shared branches remain unknown. Source-only restriction is already configured: change starting sensory bodies while retaining the rest of the graph. No threshold tuning.

GNG021 remains an indirect structural candidate overlapping the Quasimodo/GNG015 network; it has not passed or failed the paper method. GNG232/DNg67 labels in final S16A and DNg67/DNge080 in S19 are panel-specific published support, not confirmed Figure 6G selection. Shiu/FlyWire comparison remains a separate version; no dynamical or experimental evidence was imported.

The seven circuit versions and evidence matrix remain separate readiness/reference records. Empty effective/dynamic fields and NOT_RUN never mean biological absence. No functional effect follows from raw weights or the synthetic tests.

## Next required evidence

Recover the Figure 6G/S16 function/config or equally explicit primary rules resolving B01–B04, then finish the same engine and run Experiment 1R. Freeze only after its scientific checkpoint passes; apply unchanged to the three sugar conditions afterward. Historical figure source tables are needed for complete comparison. The [readiness checkpoint](experiment_01_replication_checkpoint.md) answers all 11 required questions. No simulation or additional permission step is part of this task.


### Follow-up 2026-10-07T22:18:43.582985+00:00
Additional official software and author/lab repository checks did not resolve B01–B04. All four source lists and fixed motor targets are cross-checked and prepared, but no biological selection ran. The existing 27 tests pass. See [sequential checklist](workflow_next_steps.txt), [new audit](../results/workflow/20261007T221035718347Z/report.txt), and [unsent request](tastekin_methods_request.txt). The full method remains unfrozen; generic package defaults were not imported.
