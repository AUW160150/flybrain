# Actual implementation and execution status

Updated 2026-10-06T00:07:00.644886+00:00. This records completed work, not a proposed or unrun result.

## Built

- Separate `fly_connectome_lm/` project; original simulator, scripts, tests, data and workspace files preserved. Full specification read before implementation. Brief project invariants in AGENTS.md.
- Modular authoritative acquisition/provenance, batched canonicalization/exact duplicate auditing, neuron-level extraction, directed matched controls, byte splits/windows/evaluation, five required neural conditions, train-only unigram/bigram references, atomic training/resume, development selection/freeze, explicit final-test evaluation, paired/hierarchical statistics, diagnostics, plots and incomplete-report generation.
- Optional transformer, frozen-fly, count/shuffled-count initialization and fixed-time modes implemented. Alice corpus replication deferred. 1024-node extraction exists, but research training at that size is deliberately a separate follow-up.
- Presets smoke/pilot/confirmation/replication and executable CLI/README commands, installed dependency closure lock, environment/provenance receipts and exact source archives.

## Provenance and preparation actually executed

- Analysis plan recorded before training, SHA-256 `181384189b8fcd4b9c51ba9596549e9d9e94e2650eadd2ed09eb28f542265c15`. Git revision: null because the workspace has no Git repository. This is a timestamped local plan, not public preregistration.
- Python 3.12.13, macOS arm64, 10 logical CPUs, PyTorch 2.14.0. Reused existing isolated workspace virtualenv without installing or modifying packages. CPU float32, two threads, deterministic algorithms. CUDA/MPS reported unavailable. sysctl RAM/model queries denied; RAM capacity is unknown in this sandbox. About 695 GB free disk at inspection.
- Official catalogue and object HTTP metadata fetched with permitted top-level curl. Existing 14,483,314-byte annotations and 1,051,241,946-byte connectivity matched official size/MD5; SHA-256 and actual schema recorded. Cache original acquisition times unknown. Child-process DNS access failed; documented import_cache evidence path avoided redownloading ~1.07 GB.
- Tiny Shakespeare downloaded from pinned revision `6f9487a6fe5b420b7ca9afb0d7c078e37c1d1b4e`, unchanged bytes. Train [0,1003854), validation [1003854,1059624), test [1059624,1115394). No exact cross-split duplicate spans >=256 bytes found. Test bytes were used only for preprocessing hashes/duplicate audit, never model scoring, training or selection.
- Audited all 151,856,684 raw ordered pairs: no duplicates. Retained 165,122 Traced neurons, including 2,605 missing type, and 6,235,649 directed pairs with >=5 contacts after removing 33 self-edges. Full status exclusions recorded. Canonicalization including duplicate audit took 61.123 seconds.
- Extracted real seed-101 graphs: smoke N64/E492; pilot N512/E3061. Both weakly connected. Smoke has 6 strong components (largest 59); pilot has 192 (largest 320). These graphs were kept unchanged. The pilot loses 91.6904% incoming and 91.9036% outgoing filtered edges to outside nodes; this illustrates the restricted neighborhood scope.
- Smoke null: 9,840 accepted directed swaps, 24,677 proposals, original-edge overlap 29.0650%, exact labelled degrees preserved. Pilot controls prepared without training: each completed 61,220 accepted swaps; proposals 115,775 / 116,006 / 117,947. Original-edge overlap about 17.2–17.3%; no claim of perfect mixing.

## Correctness and bounded execution actually run

- Initial pytest run: 21 passed, 2 failed, 2 skipped. Failures were an invalid UTF-8 synthetic test fixture and a tiny-sequence overfit test at lr .025. Corrected the fixture; software-only overfit checks at .003/.01 for 300 updates supported .01 for that test. The main smoke/pilot learning rate remains .001. These are implementation tests, not corpus tuning or scientific results.
- Subsequent suites: 23 passed/2 skipped; expanded graph/provenance tests 29 passed/2 skipped; final-test gate checks 31 passed/2 skipped. Final result: **31 passed, 0 failed, 2 skipped**. Skips: CUDA unavailable, MPS unavailable. CPU float64 dense/scatter/sparse forward/backward, source-target direction, absent edges, learned core, full relabeling, matched degrees/initialization/counts, causality, byte boundaries/tail masking, reset/test isolation, CPU resume and synthetic rejection all covered.
- Bounded CPU forward/backward profile: all five required architectures, one warmup and three measured passes, no optimizer updates. Timing report retained; this does not establish pilot throughput.
- Exactly one real-data neural smoke matrix trained: five required conditions × one seed × 20 updates; 64 nodes, d16, context32, batch2. Each saw 1,280 prediction targets, total 6,400. Deterministic full validation at steps 10/20, 55,769 targets per evaluation. All five best-validation checkpoints were step20, equal to final checkpoints.

| Condition | Active parameters | Final validation BPB | Byte perplexity | Core weight change L2 |
|---|---:|---:|---:|---:|
| FLY-TOPOLOGY | 11052 | 7.771031 | 218.430619 | 0.290734 |
| DEGREE-REWIRED | 11052 | 7.755692 | 216.120429 | 0.269339 |
| RANDOM-DENSITY | 11052 | 7.768305 | 218.018309 | 0.281449 |
| PARAMETER-MATCHED-GRU | 11048 | 7.905474 | 239.764440 | n/a (GRU) |
| NO-CROSS-NODE-RECURRENCE | 10624 | 7.791069 | 221.485558 | 0.083448 |

**This smoke is not evidence that fly wiring helps.** Rewired BPB happens to be lower in this tiny execution check; no statistical inference is made. Train-only smoothed validation sanity references: unigram 4.808269 BPB, bigram 3.585333 BPB. Neural smoke has not converged.
- All five smoke runs completed; no failed scientific seeds or active training processes. Peak process-lifetime RSS across smoke was 466,583,552 bytes, not isolated per-model peak. Per-run training/validation timings, loss/gradient curves, row norms, spectral norm estimates, saturation, exact hashes and checkpoint RNGs are retained.
- Validation-only zero-core/reset-every-byte/10%-edge perturbation diagnostics and fixed prompt byte samples were generated for every smoke arm. They did not select checkpoints or alter the protocol. No cherry-picked text is used as evidence.
- Generated and inspected the honest smoke report and plots. Pilot/confirmation run-matrix dry runs executed. At the initial handoff, the prepared CPU pilot had 15 untrained runs and 15,360,000 prediction-byte exposures; rough tensor/checkpoint estimates are documented, not runtime promises.

## Code revision and artifacts

- Executed smoke code hash: `25220a7f1ba7225708fa8fc6bd6e3c773461eff8fb642c7d1fd79cbafa75afe8`. Exact code archive: `reports/smoke-source-25220a7f1ba7.zip`; reconstructed by reversing the subsequent guard/logging edits and verified byte-for-byte against the logged source digest.
- Current implementation code hash: `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`. Changes after smoke only tightened final-test checkpoint/corpus checks, retained invalid-control failures, and improved report references/commands. The model, data, optimizer, initialization, controls, presets and smoke measurements were not changed or rerun. Updated guard tests passed. Current source archive and checksum are in docs/implementation_receipt.json.
- [Smoke report](../reports/smoke-26a633261d83/report.md), [run bundle](../runs/smoke-26a633261d83.json), [test log](../reports/pytest.txt), [pilot matrix](../reports/pilot-run-matrix.json), [data sources](DATA_SOURCES.md). Every binary/data artifact is local and ignored by Git patterns.

## User-executed pilot — completed and audited

The user ran `./fly_connectome_lm/fly-lm run --config pilot`. Bundle `pilot-f66c5c98ba1e` started 2026-10-05T18:07:02Z and completed all 15 runs. This follow-up inspected outputs and replayed validation, without launching training or test evaluation.

- Real male-cns:v1.0 sample 101, N512/E3061; required five conditions × seeds 1/2/3; one independent degree-rewired control per seed. CPU float32, batch4/context128/d32, lr .001, 2,000 updates per run. All declared budgets completed: 1,024,000 prediction-byte exposures per run, 15,360,000 total.
- Integrity audit passed for all 15 runs and 30 best/final checkpoint identities. Verified code/config/graph/corpus/plan hashes, exact validation schedules, logged selected minima, finite losses/gradients, active parameter counts, identical final training-window RNG states, matched initial fly/null edge slots, exact labelled degrees, and changed recurrent-core weights.
- All saved best-checkpoint validation BPBs were independently replayed and matched logs within 1e-6 BPB. Final checkpoint replay was also verified; 14 runs selected step2000. RANDOM-DENSITY seed3 selected step1900 and its final checkpoint was separately scored. No test loader was used; no test result files exist.

| Condition | Active parameters | Mean best-validation BPB | Mean final-validation BPB |
|---|---:|---:|---:|
| FLY-TOPOLOGY | 52981 | 3.187733 | 3.187733 |
| DEGREE-REWIRED | 52981 | 3.190773 | 3.190773 |
| RANDOM-DENSITY | 52981 | 3.166654 | 3.167465 |
| PARAMETER-MATCHED-GRU | 53000 | 2.914926 | 2.914926 |
| NO-CROSS-NODE-RECURRENCE | 50432 | 3.270516 | 3.270516 |

Primary pilot contrast (rewired minus fly): seed1 +0.008538, seed2 +0.001960, seed3 −0.001380 BPB; mean **+0.003039 BPB**. Descriptive paired 10,000-resample interval: [−0.001380, +0.008538]. Only three training seeds, one graph sample and validation-selected checkpoints: this is not a confirmatory test interval or proof of equality. The observed mean is below the predeclared 0.02 BPB practical threshold. This pilot establishes no practically meaningful fly-wiring advantage. GRU and random-density have lower mean validation BPB; all conditions are retained and reported.

Nearly every run selected the last evaluated checkpoint, so convergence has not been established. Keep the predeclared development/confirmation design; do not change anatomy, node count, seeds or choose extra fly variants from these results.

Logged training time across the matrix: 526.774 seconds; validation time: 40.418 seconds. Equal parameter count/bytes do not imply equal compute: GRU mean training time was about 12.87s versus 40.62s for fly recurrence on this CPU implementation.

[Pilot report](../reports/pilot-f66c5c98ba1e/report.md), [integrity audit](../reports/pilot-f66c5c98ba1e/audit.json), [review summary](../reports/pilot-f66c5c98ba1e/review-summary.json), and [paired effects](../reports/pilot-f66c5c98ba1e/paired-effects.json). The audit script is saved with the report. No experiment source, checkpoints, analysis plan, presets or corpus were changed. Code hash remains `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`.

Pilot diagnostics/text-generation interventions were not run in this follow-up. The implementation test suite was not rerun because experiment code did not change; the previous 31-pass/2-skip result is retained, and the new artifact/checkpoint/validation audit passed.

## User-executed development grid — completed, audited and frozen

The user ran `./fly_connectome_lm/fly-lm tune --config pilot`. All 30 development trials completed; selection written 2026-10-05T18:46:52Z. Seeds 901/902 and rates .0003/.001/.003 were used exactly as planned. Every arm trained to 2,000 updates (1,024,000 prediction bytes per run); 30,720,000 exposures total. No failed/missing trial was dropped.

| Learning rate | Pooled fly + rewired validation BPB | GRU validation BPB |
|---|---:|---:|
| 0.0003 | 3.478438 | 3.344572 |
| 0.001 | 3.186370 | 2.924730 |
| 0.003 | 2.933066 | 2.698202 |

**Selected common graph rate: .003; independently selected GRU rate: .003.** All A/B/C/E share the selected common rate. The fixed grid was not expanded. These are development selection values, not confirmatory topology evidence.

Post-run audit passed for all 30 runs/60 best-final checkpoint identities. Replayed saved validation scores, matched histories and selection summaries, checked full budgets/schedules, active parameter counts, exact degree preservation, null policy, initial fly/null slot weights, learned-core changes, shared window RNG states, and hashes. No test loader used. No training launched by this review. The previous 31-pass/2-skip unit suite remains the latest suite result; code was unchanged, so it was not rerun.

Logged training time 1054.927s and validation 80.543s. Optional secondary fixed-time budget derived from development is 35.164231s; that protocol has not run.

Created `configs/confirmation-frozen.json` and validated the exact confirmation dry run. All 35 runs resolve lr .003 and remain untrained. Seeds11/22/33/44/55, three nulls per seed, 20,000 updates, batch8/context128; 716,800,000 prediction-byte exposures total. No default preset/source/analysis-plan changes. Test data remains sealed.

Freeze SHA-256 `ffb133aefbbdcfba44463ba1303d2834c7d449332aaca4358516bca15d6b52e5`. Code remains `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`. [Development report](../reports/development-review/report.md), [audit](../reports/development-review/audit.json), [selection](../configs/development-selection.json), [freeze](../configs/confirmation-frozen.json), [resolved confirmation matrix](../reports/confirmation-frozen-run-matrix.json).

## Confirmation observed in progress

At 2026-10-05T19:13:51.502075+00:00, user-started bundle `confirmation-211428f1ca1f` was observed with statuses `{'complete': 2, 'running': 1, 'not_started': 32}`. These counts are a timestamped progress snapshot, not a completion claim. The frozen recipe was left unchanged. No interim confirmation BPBs were analyzed in this fairness review, no training process was launched/stopped, and no test evaluation was performed.

At 2026-10-05T21:00:54.922319+00:00, a read-only progress check found 16/35 confirmation runs complete, 1 marked running and 18 not started. The active saved history was at step 16000/20,000 (confirmation-g101-s11-degree-rewired-k3-287ca1ae66b9); its file timestamp showed continued progress. Median completed wall times were 8.57 minutes for graph models and 2.43 minutes for GRU. Estimated remaining time was approximately 144 minutes assuming unchanged throughput and no sleep; this is an estimate, not a completion claim. Process listing was denied by the environment, so this check used saved histories and manifests. No training was launched/stopped, no recipe changed, and no model test evaluation was performed.

## User-executed confirmation training — completed and audited

Bundle `confirmation-211428f1ca1f` completed all 35 runs on 2026-10-05T23:22:44.835351Z (7:22 p.m. Eastern), after 4.462 hours wall time. Five training seeds, three independent rewired controls per seed, real sample101 N512/E3061; every run completed 20,000 updates at batch8/context128, selected lr .003. Total prediction-byte exposures: 716,800,000.

This review passed the frozen-matrix integrity audit and validation replay for all 35 runs and 70 best/final checkpoint identities. Verified code/plan/corpus/graph hashes, checkpoint selection, full budgets, finite losses, exact labelled degrees and accepted-swap policy, initial edge-slot and interface matching, optimizer settings, identical per-seed final data-window RNG states, and changed recurrent weights. All replayed validation metrics matched logged values within 1e-6. No model test bytes were loaded; no new training was launched.

| Condition | Runs | Mean best-validation BPB | Mean final-validation BPB |
|---|---:|---:|---:|
| FLY-TOPOLOGY | 5 | 2.496182 | 2.504713 |
| DEGREE-REWIRED | 15 | 2.481610 | 2.492190 |
| RANDOM-DENSITY | 5 | 2.446179 | 2.454212 |
| PARAMETER-MATCHED-GRU | 5 | 2.359059 | 2.367948 |
| NO-CROSS-NODE-RECURRENCE | 5 | 2.531805 | 2.548355 |

Descriptive paired validation delta (mean of three rewired controls minus fly): −0.014572 BPB; 10,000-resample seed-level percentile interval [−0.024581, −0.006182]. All five seed-level means favored rewiring. This is validation-only analysis of validation-selected checkpoints, not the predeclared primary test outcome. It establishes no fly-wiring advantage; no recipe or checkpoint rule was revised in response.

Selected checkpoint steps: 16,000 (1 run), 17,000 (5), 18,000 (19), 19,000 (3), 20,000 (7). All consumed the full budget. Training time 15,901.594s; validation 98.067s. Equal byte/parameter budgets do not imply equal compute; GRU was faster in this implementation.

[Validation review](../reports/confirmation-211428f1ca1f/validation-review.md), [full run report](../reports/confirmation-211428f1ca1f/report.md), [audit](../reports/confirmation-211428f1ca1f/audit.json), [audit source](../reports/confirmation-211428f1ca1f/audit_confirmation.py), [machine-readable summary](../reports/confirmation-211428f1ca1f/review-summary.json). Added audit/review scripts and generated plots. Corrected AGENTS.md's specification path to its current location `Experiment/CODEX_EXPERIMENT_PROMPT.md`; the frozen analysis plan's historical reference and bytes were preserved.

Experiment source, presets, plan, corpus, graphs, checkpoints and freeze were unchanged. Code remains `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`. The latest unit-test suite remains 31 passed / 2 unavailable-accelerator skips; it was not rerun because experiment source did not change. The new post-run audit passed.

## User-executed final test — complete, frozen and audited

The user explicitly ran `./fly_connectome_lm/fly-lm final-evaluate --freeze fly_connectome_lm/configs/confirmation-frozen.json`. All 35 runs were scored on the held-out test split between 2026-10-05T23:41:07.467106Z and 2026-10-05T23:41:17.766877Z. Both the preselected best-validation and final-step checkpoints were evaluated: 70 checkpoint scores, each over the same 55,769 byte prediction positions. Test data has now been used; it must not be treated as unseen for later study revisions.

The post-test artifact audit passed: complete frozen run matrix; all 70 checkpoint hashes match the audit recorded before test access; validation-selected steps and identities unchanged; per-run results match the final summary; BPB/perplexity/accuracy arithmetic verified; paired analysis independently recalculated. This audit did not load raw test bytes or repeat test inference. No training, checkpoint reselection, hyperparameter changes or graph changes were performed.

| Condition | Runs | Mean primary test BPB | Mean final-step test BPB |
|---|---:|---:|---:|
| FLY-TOPOLOGY | 5 | 2.638847 | 2.643372 |
| DEGREE-REWIRED | 15 | 2.628560 | 2.633725 |
| RANDOM-DENSITY | 5 | 2.582685 | 2.588465 |
| PARAMETER-MATCHED-GRU | 5 | 2.557536 | 2.570289 |
| NO-CROSS-NODE-RECURRENCE | 5 | 2.673807 | 2.682296 |

**Primary test contrast, mean rewired BPB minus fly BPB: −0.010287 BPB; 95% paired bootstrap interval [−0.020626, +0.001733].** Three rewired controls were averaged per training seed, then the five paired differences were resampled 10,000 times (seed1729). Four seeds favor rewiring and one favors fly. No practical fly-wiring advantage is established. The interval includes zero, so a clear disadvantage is also not established; this is not proof of equality. Five seeds provide limited uncertainty, and this single graph from one specimen does not support population-level conclusions.

Secondary final-step contrast: −0.009647 BPB, interval [−0.018598, +0.000245]. The predeclared best-validation selection remains primary. GRU has the lowest mean test BPB among the five conditions; this is a secondary architecture comparison, not an isolated wiring effect. Train-only unigram/bigram test references: 4.850567 / 3.608388 BPB.

## Post-confirmation validation diagnostics — actually executed

After test artifact verification, ran the predeclared validation-only baseline/zero-core/reset-every-byte/fixed-10%-coefficient interventions for all applicable arms across all 35 runs. Generated all 35 fixed training-prompt samples (first32 training bytes; 128 generated bytes; temperature .8; same generation seed within each training seed). Baseline validation scores matched prior logged scores within 1e-6. Best checkpoint hashes remained unchanged, and immutable test artifact hashes remained unchanged. These are artificial-model dependence checks and illustrations, not evidence of a special connectome benefit. No training or test-based selection occurred.

[Final readable report](../reports/confirmation-211428f1ca1f/final-review.md), [full per-run scores/curves](../reports/confirmation-211428f1ca1f/report.md), [final audit](../reports/confirmation-211428f1ca1f/final-audit.json), [audit source](../reports/confirmation-211428f1ca1f/audit_final.py), [paired effects](../reports/confirmation-211428f1ca1f/final-test-effects.json), [final summary](../reports/confirmation-211428f1ca1f/final-review-summary.json), [all validation diagnostics/samples](../reports/confirmation-211428f1ca1f/validation-diagnostics-review.json). The earlier validation review remains as a timestamped pre-test artifact.

Frozen source/plan/config/data/checkpoints are unchanged: code SHA-256 `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`; freeze file SHA-256 `ffb133aefbbdcfba44463ba1303d2834c7d449332aaca4358516bca15d6b52e5`. New report/audit scripts live outside frozen experiment source. Latest unit suite remains 31 passed / 2 unavailable-accelerator skips; no source change required rerunning it. Both post-run audits passed.

## Completed scope and remaining unexecuted studies

The initial one-subgraph confirmation is complete: implementation, real-data smoke, pilot, development tuning, frozen confirmation training, held-out test evaluation, integrity review, prescribed validation diagnostics and reporting. No integrity blocker remains. No further command is required to finish this scope.

Multi-subgraph replication, fixed-time research, independent Alice retraining and 1024-node research training remain unrun and separately scoped. Existing hardware/network/Git limitations remain documented above. No additional training, paid compute, uploads or background jobs were launched during final review. The held-out test results cannot be used to retune this frozen experiment.

## Presentation figures — generated from saved results

Created seven figures from the completed confirmation artifacts: final test overview, all paired seed comparisons, validation curves versus training bytes, validation curves versus measured training time, parameter allocation/runtime, recurrence-intervention heatmap, and actual fly/rewired wiring with directed adjacency matrices. Used the real 512-node graph and the control identified by training seed11/null1, with identical abstract node positions (not anatomical coordinates).

Each figure has a 220-DPI PNG, editable-text SVG and PDF. Added a seven-page PDF collection, a local HTML gallery, ZIP bundle, exact plot-data JSON, provenance hashes and a reproducible rendering script outside frozen experiment source. Shaded learning-curve bands are explicitly seed min/max, not confidence intervals; rewired controls are averaged within seed for trajectories and paired analysis. Only the predeclared primary comparison uses its audited seed-bootstrap interval.

Verified all saved-input/output hashes, agreement of plotted test means with the audited results, all gallery links, all SVG XML files, the seven PDF pages and ZIP integrity. Inspected all seven PNG figures and corrected label overlaps/font fallback. No training, model inference, new test scoring, data changes or frozen-code changes occurred. The existing anatomical visualization project was preserved.

[Open figure gallery](../reports/confirmation-211428f1ca1f/figures/index.html) · [PDF collection](../reports/confirmation-211428f1ca1f/figures/experiment-figures.pdf) · [ZIP collection](../reports/confirmation-211428f1ca1f/figures/experiment-figures.zip) · [verification](../reports/confirmation-211428f1ca1f/figures/verification.json).
