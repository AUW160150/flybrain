# EXP1 continuation: preregistration

Continuation of protocol `f1098ea9857c0053`. Written 2026-10-23 under `../SIGNOFF_EXP1_stage0.md`, which approved Stage 0 and authorized this document. **No Stage 1 run is authorized by it.** Training starts only after a human signs §13.

Protocol hash: `432cb7daac69472c`

The machine-readable protocol is `configs/exp1c_protocol.yaml`; its SHA-256 (first 16 hex digits) is the protocol hash above, and every continuation run, result row and analysis output carries it. `reports/exp1c/registration.json` holds the SHA-256 of every registered file, the fresh-set hashes, the ladder graph hashes and the matched `rho` of every null graph. Where this document and the YAML disagree, the YAML is authoritative and the disagreement is an error to be fixed by amendment. Every deviation after sign-off goes in `amendments.md`, dated, with a reason.

Every table of numbers below is rendered from `reports/exp1c/*.json` by `scripts/exp1c_prereg_tables.py`, and the registration gate fails if any table differs from a fresh rendering.

## 1. Motivation

This is an identifiability and biology question: does the specific wiring of the LC10a → AOTU → steering-DN subgraph carry function that a null graph does not, under a design able to detect it? It is not an engineering question. H3 (engineering benefit) is settled negative and H1 (scaling) is trivially true; neither is re-run.

**Why the registered H2 null was close to guaranteed (demonstrated from the experiment's own controls).** The encoder gives each LC10a neuron a free 4-vector `B_i` and the decoder is a free 2 × 10 linear readout. Together they absorb any permutation of input-layer or output-layer identity, so rewiring could act only on the mixing among the 158 intermediates. The bypass, which deletes the intermediates and the recurrence, tied `fly_bio` (+1.6 points, 95% interval −3.7 to +6.9). The arrangement of edges inside a module cannot matter more than the module, and the module could be removed without measurable loss.

**Power was also inadequate.** One biological graph against three rewired graphs, with training seeds nested inside graphs, gives a permutation floor of p = 0.25. No smallest effect size of interest was registered.

Hence Stage 1 is a headroom gate, not a larger copy of the original comparison: if a memoryless direct map reaches the recurrent core's converged performance, no topology comparison on this task can show anything.

## 2. What Stage 0 changed

Source: `reports/stage0_diagnostics.md`, accepted in the sign-off. Binding consequences:

1. **Seed variance is not zero.** Every run is scored on the same episodes, so the shared episode-difficulty component cancels in a paired comparison and the right noise floor is the residual, not the binomial SE of an unpaired evaluation. Measured on the registered test results, the between-seed SD of tracked fraction is about 0.025 for bio and bypass and about 0.052 between seeds within a rewired graph. Seeds, not episodes, are the binding sample size. Every power figure below is recomputed from measured components (§4).
2. **Rewired graphs are interchangeable at this endpoint** (graph means 0.711, 0.708, 0.710; between-graph variance estimated at or below zero). This holds for three graphs of the weak parent null and is not assumed for the new rungs: Stage 2 estimates the graph component and the power table spans graph SDs up to 0.03.
3. **The parent's rewired graphs are a weak null.** They preserve edge counts between (role, side) classes, degrees and each presynaptic neuron's synapse counts. They are **not a cell-type-preserving null** and are labelled "parent role × side null" wherever they appear. On the ladder (§8) they are not nested with L2: they keep role-level hemisphere structure that L2 lacks, and lack the cell-type blocks L2 keeps. Nothing in this document or any erratum describes the original experiment as having tested a cell-type-preserving null.
4. **Collisions were post-or-wall.** The parent counter pooled wall and post contacts; the historical 23.2% (fly_bio) and 3.0% (classical) are post-or-wall. Post-only validation estimates are 11.3% for bio and 4.0% for classical, and any shared-failure-mode argument is sized against those. All continuation reporting splits post and wall contacts (§3).
5. **Rewired graphs start far more active than bio**: Stage 0 measured output-neuron rates 43% to 220% above bio before training. That makes the parent's topology comparison a comparison of dynamical regimes. §6 adds a named activity-matching arm.
6. **Encoder identity is consumed** (Test A: permuting `B_i` within a hemisphere keeps hemisphere rate sums within about 11% yet costs fly_bio −0.47 tracked fraction). Per the predeclared reading the retinotopic arm stays, but the bypass is equally dependent: this is a property of jointly training a free encoder with any downstream map and is not evidence about the connectome. Its only legitimate home is the Stage 3 interface × topology interaction, never a main-effect claim, and bypass-under-fixed-interfaces is a required control there.
7. **Test B is confounded and uninformative** (rectification moves summed rates by about 50%). It is reported as attempted and confounded and used as evidence in neither direction.
8. **Mirror invariance passed in all three arms** and is reported as a sanity check. No arm's turn signal is a clean left-minus-right readout (shares 0.66 to 0.73 against an arbitrary 0.9 threshold) and none is purely identity-based either; this neither confirms nor refutes the circularity concern, which rests on Test A. fly_bio's turn signal comes mainly from DNa02 and DNa03.

## 3. Endpoints

- **Primary (every stage): per-episode tracked fraction**, the share of post-warmup steps with |bearing| ≤ 60° and 0.5 ≤ distance ≤ 2.0 m, paired by episode seed. One primary endpoint per stage.
- **Secondary, predeclared:** nominal success (SESOI 0.03); post-collision episode rate and wall-collision episode rate, **each reported separately and never pooled**; target-contact episode rate; success without the collision clause (tracking competence). Collision steps are attributed to a post or a wall by `stage0.contact_kind`, with the nearest-obstacle fallback for contacts resolved within a substep (positive controls in `tests/test_stage0.py`).
- **Episode termination:** none. Episodes always run 300 steps; a collision never ends an episode, so tracked fraction is computed over the same steps for every controller and needs no handling of collision-terminated episodes.
- **Held-out imitation loss** is recorded at every validation point as an early-warning diagnostic only, never as evidence about topology.
- **Statistics:** SESOI 0.03 tracked fraction (and 0.03 success). Intervals are hierarchical percentile bootstraps (graphs, then training seeds within graph, then episodes, the episode draw shared by every arm in a comparison), 10,000 replicates. Equivalence is TOST at α = 0.05: the 90% interval inside ±0.03. Clustering level: graph; a single-graph or non-graph arm has one cluster per training seed.

## 4. Power and sample size

### 4.1 Measured variance components

Seed SD by method of moments on runs × shared episodes (`scripts/exp1c_power.py`). The validation source is shown for completeness, but 100 of its 200 episodes chose the checkpoints, so the pilot-only column and the test results are the unbiased ones. Planning values take the largest seed SD over the three sources.

<!-- BEGIN:seeds -->
| Source | Endpoint | bio seed SD | bypass seed SD | rewired seed SD (within graph) | bio residual var | bypass residual var |
|---|---|---:|---:|---:|---:|---:|
| registered test results (200 ep, read only) | tracked_frac | 0.0249 | 0.0243 | 0.0523 | 0.0497 | 0.0380 |
| registered test results (200 ep, read only) | success | 0.0200 | 0.0268 | 0.0343 | 0.0961 | 0.1008 |
| Stage 0 validation (200 ep) | tracked_frac | 0.0126 | 0.0254 | 0.0503 | 0.0566 | 0.0355 |
| Stage 0 validation (200 ep) | success | 0.0142 | 0.0454 | 0.0489 | 0.1063 | 0.0969 |
| pilot_val only (100 ep, not used for checkpoint selection) | tracked_frac | 0.0000 | 0.0157 | 0.0475 | 0.0631 | 0.0396 |
| pilot_val only (100 ep, not used for checkpoint selection) | success | 0.0071 | 0.0403 | 0.0425 | 0.1149 | 0.0994 |
| **planning value (max over sources)** | tracked_frac | **0.0249** | **0.0254** | **0.0523** | 0.0631 | 0.0396 |
| **planning value (max over sources)** | success | **0.0200** | **0.0454** | **0.0489** | 0.1149 | 0.1008 |

Arm-by-episode interaction variance (bio minus bypass, planning): tracked fraction 0.0063, success 0.0136.

Seed rule: bypass planning SD 0.0254 vs bio 0.0249 (within 20%: yes); P(no-go | true 0) at 10 seeds 31% at 1000 episodes (needs >= 80% to allow 10), so the base is 15. P(no-go | true 0) at 15 seeds: 50%; at 30 seeds: 83%. **Stage 1 seeds per arm: bio 30, bypass 30, rew1001 15, rew1002 15, rew1003 15, two_unit 15.**
<!-- END:seeds -->

The bypass seed SD, measured from the 5 existing bypass checkpoints, is close to bio's, as the sign-off anticipated. With 5 runs per arm each SD estimate has 4 degrees of freedom, so its own uncertainty is large (a 95% interval for an SD from 4 df spans about 0.6× to 2.9× the estimate); the table below therefore also shows every figure at twice the planning SD.

### 4.2 Gate G1: what the sign-off's table measured, and what the gate needs

The sign-off's table reproduces exactly as z · √((0.025² + SD_bypass²) / n), the 95% half-width from the two seed terms alone (bio seed SD 0.025):

<!-- BEGIN:signoff_check -->
| Seeds per arm (n) | Bypass seed SD 0.025 | Bypass seed SD 0.052 |
|---:|---:|---:|
| 5 | 0.0310 | 0.0506 |
| 6 | 0.0283 | 0.0462 |
| 10 | 0.0219 | 0.0358 |
| 15 | 0.0179 | 0.0292 |
| 20 | 0.0155 | 0.0253 |
<!-- END:signoff_check -->

That formula answers "is the half-width below 0.03 when the point estimate is exactly 0". Three things make it optimistic for the registered gate:

1. A half-width just under 0.03 gives about a 50% chance of a no-go when the truth is 0, not near certainty: the estimate itself scatters by one SE.
2. It leaves out the residual episode term and the arm × episode interaction, which do not cancel.
3. **G1's no-go is conjunctive**: the success upper bound must also fall below +0.03. Success is binary and its seed SD for the bypass is larger (planning 0.045), so the success leg, not tracked fraction, limits the gate.

Probabilities of each verdict under the registered rule, at the planning SDs and at twice them:

<!-- BEGIN:g1power -->
| Seeds per arm | Episodes | SD scale | 95% half-width (tracked) | P(no-go \| true 0) | P(ambiguous \| true 0) | P(go \| true +0.03) | P(go \| true +0.05) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 500 | 1x | 0.0343 | 9% | 88% | 40% | 81% |
| 5 | 500 | 2x | 0.0640 | 1% | 96% | 15% | 33% |
| 5 | 1000 | 1x | 0.0328 | 11% | 87% | 43% | 85% |
| 5 | 1000 | 2x | 0.0632 | 1% | 96% | 15% | 34% |
| 5 | 2000 | 1x | 0.0320 | 12% | 86% | 45% | 87% |
| 5 | 2000 | 2x | 0.0628 | 2% | 96% | 15% | 35% |
| 10 | 500 | 1x | 0.0248 | 26% | 73% | 50% | 94% |
| 10 | 500 | 2x | 0.0455 | 4% | 94% | 25% | 58% |
| 10 | 1000 | 1x | 0.0234 | 31% | 69% | 50% | 95% |
| 10 | 1000 | 2x | 0.0448 | 4% | 94% | 26% | 59% |
| 10 | 2000 | 1x | 0.0228 | 33% | 66% | 50% | 96% |
| 10 | 2000 | 2x | 0.0444 | 4% | 93% | 26% | 60% |
| 15 | 500 | 1x | 0.0206 | 43% | 57% | 50% | 97% |
| 15 | 500 | 2x | 0.0374 | 7% | 90% | 35% | 75% |
| 15 | 1000 | 1x | 0.0193 | 50% | 50% | 50% | 98% |
| 15 | 1000 | 2x | 0.0367 | 8% | 90% | 36% | 76% |
| 15 | 2000 | 1x | 0.0187 | 54% | 46% | 50% | 98% |
| 15 | 2000 | 2x | 0.0363 | 8% | 90% | 37% | 77% |
| 20 | 500 | 1x | 0.0182 | 57% | 43% | 50% | 98% |
| 20 | 500 | 2x | 0.0325 | 11% | 86% | 44% | 85% |
| 20 | 1000 | 1x | 0.0169 | 65% | 35% | 50% | 99% |
| 20 | 1000 | 2x | 0.0319 | 12% | 86% | 45% | 87% |
| 20 | 2000 | 1x | 0.0163 | 70% | 30% | 50% | 99% |
| 20 | 2000 | 2x | 0.0315 | 12% | 85% | 46% | 87% |
| 30 | 500 | 1x | 0.0154 | 75% | 25% | 50% | 99% |
| 30 | 500 | 2x | 0.0269 | 20% | 78% | 50% | 93% |
| 30 | 1000 | 1x | 0.0141 | 83% | 17% | 50% | 100% |
| 30 | 1000 | 2x | 0.0262 | 22% | 77% | 50% | 93% |
| 30 | 2000 | 1x | 0.0134 | 87% | 13% | 50% | 100% |
| 30 | 2000 | 2x | 0.0258 | 23% | 76% | 50% | 94% |
| 40 | 500 | 1x | 0.0138 | 84% | 16% | 50% | 100% |
| 40 | 500 | 2x | 0.0235 | 30% | 69% | 50% | 95% |
| 40 | 1000 | 1x | 0.0125 | 91% | 9% | 50% | 100% |
| 40 | 1000 | 2x | 0.0228 | 33% | 66% | 50% | 96% |
| 40 | 2000 | 1x | 0.0118 | 94% | 6% | 50% | 100% |
| 40 | 2000 | 2x | 0.0224 | 35% | 65% | 50% | 96% |
<!-- END:g1power -->

At the sign-off's 15 seeds per arm and 1000 episodes a true zero difference returns "ambiguous" about half the time. That is the failure mode the sign-off forbids, so the registered design spends more seeds where the gate is decided.

**Registered Stage 1 seed counts.** Rule (fixed in `scripts/exp1c_power.py` before the counts were read off): the base count is the sign-off's 15 (10 would be allowed only if the bypass SD is within 20% of bio's and 10 seeds already give P(no-go | 0) ≥ 0.80, which they do not); the two gate-bearing arms, bio and bypass, take the smallest n ≥ 15 in steps of 5 with P(no-go | true 0) ≥ 0.80 at 1000 episodes. The other four arms carry no gate and keep 15. G1 uses 1000 episodes rather than 500 because its success leg needs them (the sign-off allows more than 500 where a specific need is stated). The resulting counts are in the seed table above and in the YAML. **This exceeds the sign-off's "15 per arm" for bio and bypass; it is listed as a decision for sign-off in §13.**

The go rule requires a point estimate of at least +0.03, so a true difference of exactly +0.03 returns "go" only about half the time at any sample size; a true +0.05 returns it with high probability.

**The single G1 extension** (only if G1 is ambiguous): 10 more seeds for bio and bypass and all 2000 F1 episodes, after which the verdict is final.

<!-- BEGIN:extension -->
| Seeds per gate arm | SE before (1000 ep) | SE after (+10 seeds, 2000 ep) | Ratio | P(no-go \| true 0) before | after |
|---:|---:|---:|---:|---:|---:|
| 15 | 0.0099 | 0.0075 | 0.76 | 50% | 80% |
| 30 | 0.0072 | 0.0060 | 0.83 | 83% | 94% |
<!-- END:extension -->

### 4.3 Bootstrap coverage

The frozen interval (`exp1c_analysis.boot_diff`) was run on data simulated from the planning components at a true difference of 0. Small-cluster percentile bootstraps can under-cover. Here coverage is within one Monte Carlo SE of 0.95 at both seed counts, so no correction is applied:

<!-- BEGIN:coverage -->
| Seeds per arm | Episodes | Simulated data sets | Bootstrap replicates | Coverage of the 95% interval at true 0 |
|---:|---:|---:|---:|---:|
| 15 | 1000 | 400 | 2000 | 0.945 (MC SE 0.011) |
| 30 | 1000 | 400 | 2000 | 0.943 (MC SE 0.011) |
<!-- END:coverage -->

### 4.4 Stage 2

Bio is the Stage 1 bio arm (re-evaluated on F2); nulls are L3 activity-matched graphs × seeds, 500 episodes; the within-graph seed SD is the measured rewired value; the graph SD is unknown, so it is varied.

<!-- BEGIN:stage2power -->
| Graphs x seeds | Graph SD | SE | MDE (80%, two-sided) | P(CI > 0 \| +0.03) | P(informative null \| 0) | SD of a null-graph mean | P(bio > 95th pct \| +0.03) | \| +0.05 | \| +0.10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20 x 3 | 0.00 | 0.0085 | 0.024 | 94% | 94% | 0.0308 | 14% | 68% | 100% |
| 20 x 3 | 0.01 | 0.0088 | 0.025 | 93% | 92% | 0.0324 | 11% | 62% | 100% |
| 20 x 3 | 0.02 | 0.0096 | 0.027 | 88% | 86% | 0.0367 | 6% | 45% | 100% |
| 20 x 3 | 0.03 | 0.0108 | 0.030 | 79% | 74% | 0.0430 | 3% | 27% | 98% |
| 20 x 5 | 0.00 | 0.0073 | 0.020 | 98% | 99% | 0.0239 | 36% | 93% | 100% |
| 20 x 5 | 0.01 | 0.0076 | 0.021 | 98% | 98% | 0.0259 | 28% | 87% | 100% |
| 20 x 5 | 0.02 | 0.0086 | 0.024 | 94% | 94% | 0.0311 | 13% | 67% | 100% |
| 20 x 5 | 0.03 | 0.0099 | 0.028 | 86% | 83% | 0.0383 | 5% | 40% | 99% |
| 30 x 3 | 0.00 | 0.0075 | 0.021 | 98% | 98% | 0.0308 | 7% | 64% | 100% |
| 30 x 3 | 0.01 | 0.0077 | 0.022 | 97% | 97% | 0.0324 | 5% | 55% | 100% |
| 30 x 3 | 0.02 | 0.0084 | 0.023 | 95% | 95% | 0.0367 | 2% | 35% | 100% |
| 30 x 3 | 0.03 | 0.0093 | 0.026 | 90% | 89% | 0.0430 | 1% | 17% | 99% |
<!-- END:stage2power -->

The interval and TOST parts of the Stage 2 rule are adequately powered at 20 × 3. **The percentile part is not**: a null-graph mean from 3 seeds carries the full seed SD (about 0.052) divided by √3, so bio must sit roughly 0.05 above the null mean before it clears the 95th percentile of 20 such means, and an effect at the SESOI rarely does (about one time in seven even with no graph variance). The brief's conjunctive "topology effect" definition is kept as written; its consequence, that only effects well above the SESOI can earn that verdict while a SESOI-sized effect will read "inconclusive", is stated here in advance. Raising seeds per graph to 5 is the efficient remedy (see the 20 × 5 rows) and is listed as a decision for sign-off in §13.

## 5. Stage 1: the headroom gate

**Question.** At convergence, does the full recurrent connectome core beat a memoryless direct map?

**The one factor changed:** training to convergence by the rule below instead of a fixed 4000 steps. Everything else is held at the parent's values: simulator and nominal condition, demonstrations (600 DART episodes, σ ~ U[0, 0.4]), loss, Adam, batch 32, window 64 + 16 burn-in, gradient clip 1.0, two torch threads, dynamics K = 4, α = 0.5, rank 4, ρ = 0.9, and the parent's tuned learning rates (fly_bio 0.003, rewired 0.003, bypass 0.001).

**Arms** (`configs/exp1c_protocol.yaml` `stages.stage1`):

| Arm | Model | Graph | Seeds |
|---|---|---|---|
| bio | FlyRNN, trainable edges | bio, ρ 0.9 | gate arm |
| bypass | FlyRNN bypass: LC10a rates → dense trainable map → output rates, memoryless | none | gate arm |
| rew1001, rew1002, rew1003 | FlyRNN, trainable edges | parent role × side null, ρ 0.9 (un-normalized) | base |
| two_unit | two-unit capacity null (below) | none | base |

**Two-unit core** (`exp1c.TwoUnitCore`): the same free encoder and per-LC10a bias, LC10a rates `r_i = max(0, tanh(u_i + b_i))`, two units `h_s = max(0, tanh(g_s Σ_{i∈s} r_i / √n_s + c_s))` for s ∈ {left, right}, action `tanh(D h + d)` with a 2 × 2 `D`. Memoryless and graph-free. Its learning rate is tuned once like the parent's groups: lr ∈ {0.001, 0.003} on tuning seed 97 under the convergence rule, chosen by validation tracked fraction.

**Training seeds:** 3101 upward, the arm's count of them; the extension adds the next 10 for each gate arm.

**Convergence rule (committed; identical for every arm).** Validate every 250 steps on the 200 validation-role episodes (seeds 300000–300099 and 920000–920099) and record the mean tracked fraction. Let M(s) be the mean of the last 4 evaluations ending at step s. Stop at the first s ≥ 4000 with M(s) − M(s − 2000) < 0.005; otherwise stop at the cap, 16,000 steps. A run that reaches the cap with M(cap) − M(cap − 2000) ≥ 0.005 is recorded as **"cap, still rising"**, a reportable outcome and not a failure. The minimum of 4000 steps means no arm trains less than in the parent. Learning curves for every run are reported. The rule is `exp1c.convergence_stop`; the loop is `src/flytrack/exp1c_train.py`, tested end to end on a shrunken rule.

**Checkpoint rule:** the evaluation with the highest validation tracked fraction up to the stop; ties go to lower mean |bearing|. A run with a non-finite loss or gradient stops, is recorded as failed and stays in the accounting.

**Evaluation:** the first 1000 episodes of fresh set F1, nominal, through `scripts/exp1c_evaluate.py` only.

**Gate G1, on bio minus bypass:**

- **No-go** if the 95% upper bound is below +0.03 tracked fraction **and** below +0.03 success.
- **Go** if the 95% lower bound (tracked fraction) is above 0 **and** the point estimate is at least +0.03.
- **Ambiguous** otherwise; this permits the single extension in §4.2, after which the verdict is final.

The rewired and two-unit arms are reported descriptively against bio (intervals, no gate). The methodologist's stated prior that G1 fails (0.65 to 0.75) is recorded and has no role in the decision.

**Cost** (measured; `reports/exp1c/power.json`):

<!-- BEGIN:cost -->
| Arm timing source | Parent wall per run (4000 steps, 5 concurrent) | Validation, 100 ep (shared machine) | 200 ep | Run at 4000 steps | Run at 16000 steps |
|---|---:|---:|---:|---:|---:|
| fly_bio (5 parent runs) | 456 s | 2.5 s | 4.4 s | 486 s | 1945 s |
| fly_bypass (5 parent runs) | 174 s | 1.8 s | 3.2 s | 195 s | 781 s |
| fly_rewired (15 parent runs) | 461 s | 2.3 s | 3.9 s | 487 s | 1948 s |

Stage 1: 120 runs (+2 two-unit learning-rate tuning runs). Training run-time 12.6 h if every run stops at 4000 steps, 50.3 h if every run reaches the 16000-step cap; at the parent's 5 concurrent runs that is 2.5 to 10.1 h wall-clock. Fresh-set evaluation at 1000 episodes: 0.63 h single-process. Two-unit timing uses fly_bypass (two_unit has fewer operations; no two_unit run exists yet).
<!-- END:cost -->

The validation and evaluation timings were measured while another session was loading the machine (load average about 20), so they are upper bounds; training rates come from the parent's run manifests. The sign-off's estimate (90 runs, 11.4 h) assumed every run stops at 4000 steps and ran serially. Under the convergence rule each fly run can take up to four times as long; the range above covers both ends.

## 6. Activity matching

This arm addresses Stage 0 finding 7 and is the most important addition to the brief.

**Mechanism.** FlyRNN initialises each edge's magnitude from its synapse count and then scales all of them so the spectral radius of |W| equals ρ = 0.9. The parent experiment therefore already matched every graph by spectral radius, which is the alternative the sign-off names, and the activity offsets persisted under it. That condition is kept as the **un-normalized (retained) control**. Because the spectral normalisation absorbs any scalar on the counts, one scalar `c` on every weight magnitude is exactly ρ → 0.9 c.

**Frozen rule (applied identically to every null graph on every rung).**

- **Target statistic:** the mean output-neuron rate over post-warmup steps on 50 calibration episodes (seeds 29,000,000–29,000,049, teacher-driven retina, identical for every graph), averaged over 10 calibration initialisations (torch seeds 7001–7010).
- **Reference:** bio at ρ 0.9.
- **Rule:** one scalar `c_g` per null graph, found by bisection in log c over [1/16, 16], stopping within 0.25% and accepted within the **1% tolerance**. A graph that cannot reach the tolerance keeps its best `c` on a 65-point grid and is flagged; analyses are then reported with and without flagged graphs, primary with. The matched graph trains with ρ = 0.9 c_g; nothing else changes.
- **Code:** `exp1c.activity_statistic`, `exp1c.match_activity`; the values are in `reports/exp1c/activity.json` and `registration.json`.

Measured before registration, for every graph Stage 1 or 2 can use:

<!-- BEGIN:activity -->
Reference: bio at rho 0.9, mean output rate 0.0780 (intermediate 0.0859). Tolerance 1%. Graphs flagged: 0.

| Graph set | Output-rate offset vs bio, un-normalized (min / max) | Matched scalar c (min / max) | Matched rho (min / max) | Largest matched offset | Intermediate-rate offset after matching (min / max) |
|---|---|---|---|---:|---|
| parent rew1001-1003 (3) | +108.8% / +186.0% | 0.528 / 0.640 | 0.475 / 0.576 | 0.21% | -21.5% / -14.1% |
| parent rewU2001 (1) | +40.0% / +40.0% | 0.746 / 0.746 | 0.672 / 0.672 | 0.06% | -18.4% / -18.4% |
| L0 (10) | +8.8% / +91.9% | 0.732 / 0.964 | 0.659 / 0.868 | 0.21% | -21.5% / +26.8% |
| L1 (10) | +20.2% / +108.1% | 0.478 / 0.841 | 0.430 / 0.757 | 0.23% | -30.9% / +24.6% |
| L2 (10) | +69.7% / +121.2% | 0.641 / 0.755 | 0.577 / 0.679 | 0.24% | +3.4% / +20.2% |
| L3 (20) | +3.0% / +102.5% | 0.685 / 0.984 | 0.616 / 0.885 | 0.25% | +0.3% / +35.4% |
| L4 (10) | +0.2% / +8.2% | 0.952 / 1.000 | 0.857 / 0.900 | 0.23% | -1.8% / +1.6% |
| bypass (descriptive; not matched) | -29.0% | - | - | - | - |
<!-- END:activity -->

All graphs reach the tolerance. Matching on output rate leaves intermediate rates unmatched; their offsets after matching are shown and reported, not corrected.

**Finding reported in its own right:** bio is quieter before training than every one of the 64 null graphs measured, though the L4 margins are small. The ladder localises much of it. Graphs that keep each (type, side) block's synapse-count magnitudes (L4) sit within a few percent of bio, while graphs that keep the same blocks but permute the counts (L3) and the parent's role × side null start far more active. So the quietness tracks which edges carry the large synapse counts, not edge placement as such. This is descriptive, measured with an untrained encoder on one input distribution.

**Where the arm enters.** Stage 1's gate compares bio with the bypass, which has no graph to rescale; its rewired arms stay un-normalized, as in the parent, and are descriptive (the bypass's own pre-training output-rate offset is reported above). From Stage 2 on, every null graph runs in both conditions: **activity-matched (primary)** and **un-normalized (retained control)**, so the size of the confound stays visible.

**Predeclared readings** (`exp1c_analysis.activity_reading`, from the Stage 2 primary comparison and its un-normalized counterpart):

- If bio beats the nulls only in the un-normalized condition: "bio beats the nulls only in the un-normalized condition: the advantage is activity scale, not topology".
- If bio beats the activity-matched nulls: "bio beats the activity-matched nulls: topology is the better explanation".
- Otherwise: "bio does not beat the nulls in either condition".

"Beats" means the 95% lower bound of bio minus the null is above 0.

## 7. Stage 1b: occlusion (only if G1 is no-go)

The one factor changed from Stage 1 is the distribution: demonstrations, validation and the convergence rule use the occlusion condition (two occlusion windows of 1–2 s), and evaluation uses fresh set F1b (first 1000 episodes; extension 2000). Same arms, seeds, rule and gate (G1b). Occlusion is the one condition where memory gives a recurrent core a mechanistic reason to beat a memoryless map. Changing the distribution also changes the teacher's behaviour, so this is a **headroom gate and not a topology test**.

**Stopping rule:** if G1 and G1b are both no-go, H2 stops on this task family and the write-up is the structural explanation: a memoryless direct map reaches the recurrent core's converged performance, so the task has no headroom in which topology could express itself, and the registered null is explained by construction rather than by absence of a topology effect.

## 8. Stage 2: the graded null ladder (only after a go at G1 or G1b)

**The one factor changed:** graph topology, under the Stage 1 (or 1b) training rule.

**Rungs** (`src/flytrack/ladder.py`). Node identities and attributes (role, side, cell type, sign) never change; each rung keeps everything below it and adds one property.

| Rung | Adds | Construction |
|---|---|---|
| L0 | signs | directed Erdős–Rényi: edge count per presynaptic sign class kept, presynaptic end uniform within its sign class, postsynaptic end uniform; synapse-count multiset kept, assigned at random |
| L1 | degrees | every neuron's in- and out-degree (double edge swaps from bio, unconstrained, 10 accepted swaps per edge) |
| L2 | cell-type blocks | edge count between every ordered pair of cell types (types pool both hemispheres); swap accepted if the two postsynaptic types or the two presynaptic types match |
| L3 | hemisphere | edge count between every ordered pair of (cell type, side) classes; same swap condition on (type, side) |
| L4 | per-block synapse magnitudes | L3 edges, with each block's synapse counts drawn from that block's biological counts |

In L0–L3 synapse counts are permuted over all edges, so in- and out-strength are not kept; allowing either swap condition stops the chain from also freezing each neuron's per-class profile. Every generated graph was checked against its rung before registration, and none keeps the next rung's property:

<!-- BEGIN:ladder -->
| Rung | Graphs | Claimed properties (all hold on every graph) | Next rung's property kept by | Edges shared with bio (min / mean / max) |
|---|---:|---|---:|---|
| L0 | 10 | node_attributes, edge_count, simple, syn_multiset, sign_edge_counts (yes) | 0 of 10 (degrees) | 0.031 / 0.034 / 0.038 |
| L1 | 10 | node_attributes, edge_count, simple, syn_multiset, sign_edge_counts, degrees (yes) | 0 of 10 (type_blocks) | 0.114 / 0.119 / 0.125 |
| L2 | 10 | node_attributes, edge_count, simple, syn_multiset, sign_edge_counts, degrees, type_blocks (yes) | 0 of 10 (typeside_blocks) | 0.227 / 0.233 / 0.239 |
| L3 | 20 | node_attributes, edge_count, simple, syn_multiset, sign_edge_counts, degrees, type_blocks, typeside_blocks (yes) | 0 of 20 (typeside_block_syn) | 0.354 / 0.359 / 0.366 |
| L4 | 10 | node_attributes, edge_count, simple, syn_multiset, sign_edge_counts, degrees, type_blocks, typeside_blocks, typeside_block_syn (yes) | n/a | 0.351 / 0.357 / 0.362 |

| Parent graph | degrees | type blocks | (type, side) blocks | out-strength | Edges shared with bio |
|---|---|---|---|---|---:|
| rew1001 | yes | no | no | yes | 0.256 |
| rew1002 | yes | no | no | yes | 0.251 |
| rew1003 | yes | no | no | yes | 0.250 |
| rewU2001 | yes | no | no | yes | 0.122 |
<!-- END:ladder -->

L5 (spatial embedding) is not registered: no independently validated spatial assignment exists. Rewired graphs share a third of their edges with bio at L3 and L4, because the (type, side) blocks are small; this is a property of the null, reported with it.

**Primary comparison:** bio minus L3 activity-matched, 20 graphs × 3 seeds (graphs `L3_g01`–`L3_g20`), first 500 F2 episodes. L3 rather than L4: Stage 0 did not show that synapse-count magnitudes matter for the trained endpoint (edge weights are trainable, so counts set only the initial weights), so the brief's default stands. **Retained control:** the same 20 graphs × 3 seeds un-normalized. Bio, the bypass and the two-unit core are the Stage 1 checkpoints re-evaluated on F2, so a graph effect can be told apart from a capacity effect. The graph variance component is estimated and reported; nothing assumes it is zero.

**Data-budget sweep** (sensitive secondary): 25% and 50% of the demonstrations (the first 150 and 300 episodes), bio × 15 seeds (3101–3115) and L3 matched graphs 1–10 × 3 seeds.

**Predeclared outcomes** (`exp1c_analysis.stage2_verdict`):

- **Topology effect:** bio's mean above the 95th percentile of the 20 L3-matched graph means, **and** the 95% lower bound of bio minus L3-matched above 0, **and** the gap at 25% data at least the gap at full data (point estimates; both gaps on graphs 1–10).
- **Informative null:** the 90% interval of bio minus L3-matched inside [−0.03, +0.03]. This is a real result and is written as one.
- **Inconclusive:** otherwise. No extension.

**Full ladder** (only after a topology effect): L0, L1, L2 and L4 at 10 graphs × 3 seeds each, activity-matched, to attribute the effect to the property a rung adds.

**Runs:** 120 for the primary and retained control, 90 for the data-budget sweep, and 120 more for the full ladder if triggered. Bio and the capacity nulls reuse Stage 1 checkpoints.

## 9. Stage 3: interfaces × topology (optional)

Stage 3 is not registered in operational detail here. What is fixed now:

- **Design:** interfaces {free encoder and decoder; fixed retinotopic encoder with a fixed push-pull two-cell decoder} × cores {bio, L3 activity-matched at 10 graphs, bypass}. Task and training rule frozen at their Stage 1 values. Fresh set F3.
- **Primary statistic:** the interface × topology interaction, (core − bypass | fixed) − (core − bypass | free) (`exp1c_analysis.interaction`). The claim it can support is an interaction, never a main effect.
- **Required control:** bypass under fixed interfaces. Without it, a topology effect under constrained interfaces could just be the constrained interfaces being worse for everything.
- **Encoder caveat**, carried with the arm every time: Stage 0 Test A showed the trained circuits consume LC10a identity, but the bypass is equally dependent, so this is a property of jointly training a free encoder with any downstream map and is not evidence about the connectome.
- **Prerequisite gate G3:** the retinotopic assignment must pass ordinal validation against independent anatomy (the central-versus-peripheral sampling split between the two relay cell types, and the lobula-to-tubercle axis ordering). Its operational criteria, with sources and a rejection rule, are registered by amendment **before any retinotopic data is inspected**, and Stage 3 needs its own sign-off.

## 10. Fresh evaluation sets

Generated from episode seeds used nowhere before: above every parent range and EXP2's fixed sets, and below EXP2's open-ended training namespace (30,000,000 upward). Each hash covers the seed list and every array of the generated initial scenes under the nominal and the occlusion configuration; building the scenes runs no controller.

<!-- BEGIN:evalsets -->
| Set | Episode seeds | SHA-256 (seed list + generated initial scenes) | Disjoint from earlier ranges | Disjoint from observed seeds |
|---|---|---|---|---|
| F1_stage1_nominal | 25,000,000-25,001,999 | `be98e457bb2de18e0c25c213b4b6df852a055aea5b6e70aabbea5f95a409fcbe` | yes | yes |
| F1b_stage1b_occlusion | 26,000,000-26,001,999 | `e75f70a0d4e0b212ad6693b873e5691efa7dee5091f6d4dad9302cf07b9512f7` | yes | yes |
| F2_stage2_nominal | 27,000,000-27,000,999 | `0a3bd3eba614258324de54b574b6cbf0dc86cf0b70659acf22f70b6394873846` | yes | yes |
| F3_stage3_nominal | 28,000,000-28,000,999 | `3ada08269d9696d5675d08bb9432dcc3ee5cadc418e12d7fd32a5f3f8962a948` | yes | yes |
| activity_calibration | 29,000,000-29,000,049 | `not an evaluation set` | yes | yes |

Ranges checked: parent:pilot_demos 910,000+300; parent:pilot_val 920,000+100; parent:train_demos 100,000+600; parent:val_demos 200,000+50; parent:val_closed_loop 300,000+100; parent:test 400,000+200; parent:pilot_900000_block (preregistration.md names 900000+; denied as a whole block) 900,000+100,000; exp2:diagnostic 21,000,000+100; exp2:tuning_validation 22,000,000+2,000; exp2:validation 23,000,000+2,000; exp2:test 24,000,000+2,000; exp2:cl_training_namespace (open-ended upward) 30,000,000 upward; plus 400 seeds observed in raw_results and Stage 0.
<!-- END:evalsets -->

**Access rule.** `exp1c.FreshSetGuard` is the only source of fresh-set seeds. It refuses unless the named gate has an authorization record containing `AUTHORIZED <gate>`, and the protocol hash and the set's hash both match the registration. Each access is appended to `reports/exp1c/fresh_access.jsonl`. `scripts/exp1c_evaluate.py` is the only caller. Each set is evaluated only at its gate. No access has occurred at registration (checked by the registration gate).

## 11. Frozen analysis

`src/flytrack/exp1c_analysis.py` with the entry point `scripts/exp1c_analyze.py`, written before the training code and registered by hash, regenerates every gate number from the raw per-episode files. It refuses rows that carry a different protocol hash, come from another evaluation set, or do not cover exactly the registered first-N episodes. Tests (`tests/test_exp1c.py`) exercise every verdict branch on synthetic data with known answers: go, no-go, ambiguous, topology effect, informative null, inconclusive when the low-data gap does not grow, both activity readings, and a known interaction. `exp1c_analyze.py synthetic` runs the whole pipeline on synthetic data and labels its output `SYNTHETIC_DATA_NOT_A_RESULT`.

Multiple comparisons: each stage has one primary endpoint and one primary comparison; everything else is labelled secondary or descriptive and reported with intervals but no decision.

## 12. Threats to validity

1. **Convergence-rule gaming or non-convergence.** The rule and cap are committed; curves are reported; "cap, still rising" is reportable. Validation is noisy (200 episodes); the 4-evaluation smoothing and 2000-step window are the guard, and an early stop on a noisy plateau is a known risk that falls on every arm alike.
2. **Fresh-set contamination.** Hashes at registration, access only through the guard, an access log, evaluation only at gates.
3. **Between-graph variance may be near zero**, which makes the Stage 2 percentile statistic seed-noise-dominated (§4.4). It is reported with that limitation stated in advance.
4. **The null definition carries the result.** Rungs are defined and verified in code before registration (§8).
5. **Multiple comparisons.** One primary endpoint and comparison per stage.
6. **Tracked fraction's own failure modes.** No episode terminates early; nominal success and separate post and wall collision rates are kept as secondaries.
7. **Seed variance under the new training rule.** The planning SDs come from 5-seed estimates at 4000 fixed steps; longer, convergence-matched training may change them. Every stage reports its measured components, and the power tables show twice the planning SD.
8. **Stage 1b changes teacher behaviour** as well as difficulty, so it is a headroom gate, not a topology test.
9. **Stage 3's fixed interfaces may simply be wrong.** The DNa03 role rests on an unreviewed preprint; the retinotopic mapping rests on about 1.2% of LC10a input synapses with known channel and layer bias. Bypass-under-fixed-interfaces catches the gross version; a mediocre mapping depresses all cores equally, and there is no fix beyond stating it.
10. **External validity to real robots or real flies is low** regardless of outcome.
11. **Activity matching is on one statistic.** Matching mean output rate leaves intermediate rates and the rate distribution unmatched; a bio advantage that survives matching could still reflect another activity property. Both conditions are reported, and the readings say "better explanation", not "proof".
12. **Calibration inputs.** The matching uses a teacher-driven retina on nominal episodes and an untrained encoder; matched graphs may drift apart during training. Pre-training matching is what the confound concerns; post-training rates are reported descriptively.
13. **Validation reuse.** The 200 convergence-rule episodes were also used for Stage 0 diagnostics and the parent's checkpoint selection. They select nothing that is analysed; all gate numbers come from fresh sets.
14. **Planning conservatism.** Planning SDs are the largest over three sources and include a validation source whose checkpoints were selected on half its episodes. If the true SDs are smaller, the gate is more decisive than stated, not less.

## 13. Registration

Registered artifacts and their SHA-256: `reports/exp1c/registration.json`, produced by `scripts/exp1c_register.py`. Ledger: `GATES_prereg.md`. Inputs measured before registration: `reports/exp1c/{power,ladder,activity,evalsets}.json`.

No training, tuning or fresh-set evaluation has been run under this protocol. The parent experiment's registered results, checkpoints and configs are unchanged (Stage 0 snapshot check).

**Decisions for sign-off:**

1. **Stage 1 seed counts above the sign-off's 15 for bio and bypass** (§4.2). The alternative is 15 for every arm, with P(no-go | true 0) of about one half at 15 × 1000.
2. **G1 at 1000 episodes and the extension at 2000** (§4.2), instead of 500.
3. **Stage 2 seeds per graph**: registered at the brief's 3; 5 would make the percentile criterion able to detect effects near +0.05 (§4.4).
4. **L3 as the Stage 2 primary rung** rather than L4 (§8).
5. **Stage 3 left at design level**, with G3's criteria to be registered by amendment before any retinotopic data is seen (§9).

- [ ] Preregistration approved by: ____________________  Date: __________
- [ ] Stage 1 training authorized (write `AUTHORIZED G1` into the sign-off record): ____________________

## Stop here

Work stops at this document. Stage 1 begins only after the boxes above are signed.
