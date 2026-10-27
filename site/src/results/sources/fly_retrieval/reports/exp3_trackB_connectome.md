# EXP3 Track B: does the MaleCNS wiring help the fly hash, and where do fly methods sit on the ANN frontier

**Load-bearing source:** Senge, S. (2026), "A Connectome Test of the Fly Hashing Algorithm", arXiv:2610.09114 v1. It is a **single-author preprint, not peer reviewed**, and it carries the negative claim that this whole question rests on. B1 is an independent reimplementation: his code was read for specification but never executed. B2 fills a gap in the literature: no fly-derived method had been placed on an ANN-Benchmarks recall–QPS frontier.

**Hardware.** Apple M5 (10 cores, 32 GB), macOS 26.6.2, Python 3.12.13, numpy 2.5.4. B1 workers run single-threaded BLAS, 8 processes. During B1 the machine was shared with another session's `fly_track` EXP2 pilot runs; this changes wall time only. B1 measures retrieval accuracy, not time. B2 runs in the ANN-Benchmarks harness in linux/arm64 Docker on colima (8 vCPUs, 24 GiB), one pinned CPU per container. The machine load during B2 is recorded below.

## B1. MaleCNS olfactory wiring against a graded null ladder

**Extraction** (`configs/olfactory_extraction.yaml`; Senge's PN rule as an explicit whitelist; traced-only, LC10a discipline).
- **Matrix:** binary glomerulus × KC, per hemisphere, with PNs and KCs on the same side.
- **Threshold:** w ≥ 5 synapses per PN→KC pair is primary, a **modelling choice, not a measurement**. w ≥ 1 is the Senge-fidelity arm; w ≥ 10 and the synapse-weighted matrix are sensitivity arms.
- **Positive control:** at w ≥ 1 our rule reproduces Senge's MaleCNS-R matrix exactly: d = 51, m = 1,886, maximum fan-out 473 on DC1.

**Null ladder.**
- **N0:** Erdős–Rényi. A weak null that only anchors the scale.
- **N1:** degree-preserving curveball. This is Senge's null.
- **N2:** equal to N1 by construction on the binary matrix, because a KC's claw count is its column sum. N2 is a distinct ensemble only on the weighted arm, where each KC keeps its claw-weight multiset.
- **N3:** N1 plus glomerulus × KC-class block counts.
- **NQ:** N3 plus per-glomerulus co-convergence Q_g held within 0.5 N1-null SD of BIO. NQ was added at sign-off (A1) so that the ladder grades.

**Odour benchmark** (Senge's primary; A2, A8).
- **Data:** DoOR 2.0 @ db323a4, with his filter reproduced exactly: 35 glomeruli, 172 odorants, 28.7% unmeasured.
- **Items and ground truth:** 4,000 Dirichlet mixtures of 2–5 profiles. Each mixture queries the other 3,999, and ground truth is its 10 Euclidean nearest neighbours on the raw responses.
- **Hash and metric:** the hash input is unit-mean normalised and M is aligned to the DoOR glomeruli. k = 5% of the aligned KCs, with random tie priority. The metric is AP@10.
- **Draws:** 200 null draws per level.
- **Arms:**
  - zero-filled: primary;
  - **mean imputation:** reported beside the primary, because Senge's deficit disappears under it;
  - our own DoOR filter (37 / 178 / 30.3%): sensitivity;
  - w ≥ 10 and synapse-weighted: sensitivity.

**2017-style protocol** (secondary).
- **Datasets:** SIFT, GloVe and MNIST.
- **Inputs:** PCA to 51 components, assigned to glomeruli by a fresh random permutation per trial.
- **Scale:** 10,000 database items, 1,000 queries, ground truth the top 2% by Euclidean distance, metric AP@200.
- **Repetition:** 20 trials × 50 null draws per level.

**Statistics.**
- **Effect:** Δ = AP(BIO) / mean AP(null) − 1.
- **Intervals:** 95% CI by two-stage bootstrap over queries (odours) or trials (protocol), then null draws, with 10,000 resamples.
- **Tests:** two-sided Monte Carlo p-values, with Holm correction over 12 tests: 2 hemispheres × 2 thresholds × {N1, N3, NQ}.
- **Margin:** SESOI = 2.5%.

### B1 result: Senge replicated

**Senge replicated.** The predeclared verdict is **REPLICATES SENGE**. In both hemispheres and at both w ≥ 5 and w ≥ 1, the upper 95% CI bound of Δ against N1 and against N3 is below +2.5% (largest: +0.20%, w5_L vs N1). This replicates MaleCNS only, **2 of Senge's 7 hemispheres**; hemibrain, FlyWire and BANC were not re-extracted. Senge 2026 is a single-author preprint, not peer reviewed. This is the first independent reimplementation we know of, and it agrees with him.

**The size of his number.** On the matrix he used (MaleCNS R, w ≥ 1), we measure Δ = −2.09% [−2.88%, −1.30%] against N1, raw p = 0.030. His odour primary is **−2.06%**, p = 0.020. On our primary threshold (w ≥ 5, R) the deficit is −2.38% [−3.16%, −1.60%].
- **Left hemisphere:** the deficit is smaller and not distinguishable from zero (w5_L −0.55% [−1.30%, +0.20%]; w1_L −0.87%).
- **Inside ±2.5% (equivalence):** the L CIs are; the R CIs are not, because their lower bounds reach −2.9% to −3.3%. R is a small, consistent *deficit*, not equivalence.
- **After Holm correction over the 12-test family:** no comparison stays significant (smallest adjusted p = 0.119, w5_R vs N1). In the table, "(nan)" in the Holm column marks N0, which is outside the family by design.

So the wiring is worse than its degree-preserving shuffle on R and indistinguishable from it on L. In neither hemisphere is it better by as much as the 2.5% margin. That is **evidence of no benefit**, bounded by the CI, not an absence of evidence: the experiment could have detected a +2.5% benefit and the CIs rule it out.

**Mean imputation, reported next to the primary.** Senge noted that his deficit disappears under mean imputation of unmeasured DoOR entries. We find more than that:
- **R:** the deficit shrinks, to −0.63% [−1.43%, +0.19%] at w ≥ 5 and −1.12% at w ≥ 1.
- **L:** it reverses, to **+3.38% [+2.61%, +4.15%]** at w ≥ 5. The CI lies entirely above the margin; w ≥ 1 gives +2.17%.

On the imputed inputs, therefore, the left-hemisphere wiring beats its degree-preserving null by more than the SESOI. This is a **robustness finding about Senge's conclusion**: its sign depends on how missing DoOR data are filled and on which hemisphere is used. It does not overturn the replication verdict, which was predeclared on the zero-filled primary. It does mean "the wiring adds nothing" is conditional on the zero-fill. Neither imputation is a measurement of the fly's real input; both are modelling choices about 28.7% unmeasured entries.

**Our own DoOR filter (sensitivity, 37 glomeruli / 178 odorants / 30.3% missing)** gives the same picture with slightly smaller deficits. N1 results:
- w5_R −1.75%, w5_L +0.00%;
- w1_R −1.32%, w1_L −0.45%.
- No upper bound reaches +2.5%.

The two filters agree on the endpoint.

**NQ: the localization result.**
- **Predeclared reading:** "no effect to localize" in both hemispheres, because Δ against N1 never has a lower bound above +2.5%. NQ is therefore reported descriptively only.
- **What NQ shows descriptively:**
  - In every arm, the nulls that hold co-convergence Q fixed score *lower* than N1 and N3, and the gap between BIO and NQ is close to zero: w5_R −1.08%, w5_L +0.87%, w1_R −0.88%, w1_L +0.37%.
  - In the protocol arm, BIO's deficit against NQ is 29–55% of its deficit against N1 in every cell.
  - Read descriptively, the per-glomerulus co-convergence structure accounts for much of what makes the real wiring score below a degree-preserving shuffle. This is **not** a predeclared reading and is labelled plausible but untested below.
- **Fidelity:**
  - Every NQ draw in every odour matrix stayed within tolerance (max |Q dev| 0.500 N1-null SD, acceptance 0.49–0.60) and kept all N3 invariants.
  - Its BIO Jaccard (0.080–0.098) is only slightly above N1's and N3's, so NQ did not collapse onto BIO (criterion ii).
  - On the aligned odour matrices (d = 35) actually used, N3 draws drift a mean 1.66–1.98 N1-null SD from BIO's Q (20 draws each, seeds 730000+; minimum per-draw value 1.34), so N3 does not already preserve Q and criterion (iii) holds (`scripts/check_nq_aligned.py`, output in `reports/checks/nq_aligned_criterion3.txt`). NQ is informative at every rung; it did not collapse.

**Synapse-weighted arm (sensitivity).**
- **Effect:** weighting the hash input by synapse count makes the real wiring markedly worse than its weighted nulls on L (−6.94% vs N1w, −6.72% vs N2w) and slightly worse on R (−0.98%, −0.75%, CIs reaching zero).
- **Ensemble:** N2w keeps each KC's own claw-weight multiset, unlike N1w, so it is the null that differs from N1 in this arm. It does not change the picture.
- **Scope:** this arm was not part of Senge's analysis.

**2017-style protocol (secondary).**
- **Cells:** BIO scores below N1 and N3 in all 12 cells (SIFT, GloVe and MNIST × 4 matrices). Every 95% CI excludes 0, with Δ against N1 between −2.07% and −3.81%.
- **Median:** the secondary median Δ against N1 over dataset × hemisphere × threshold × k (60 combinations) is **−1.96%** (IQR −2.85% to −1.35%). Senge reports −1.6% (IQR −3.2% to −0.3%) over 168 combinations.
- **Agreement and scope:** the two agree in sign and roughly in size. Our IQR is narrower and lies wholly below zero. The protocol arm feeds PCA components to glomeruli by random assignment, so it says nothing about olfactory coding. It tests whether the wiring's statistics help a generic hash.
- **Departure:** GloVe here is `glove-100-angular`, not Senge's GloVe 6B 300d.

**How this relates to Track A and to the 2017 result.** B1 tests the wiring, not the fly-hash algorithm itself. It is silent on Senge's separate arithmetic-matching claim, which is labelled **contradicted under matched-arithmetic conditions — against real-valued Gaussian projections only; against one-bit codes the fly hash leads from k = 32**. That claim is cited from Senge (unreviewed) and was not re-measured here. Dasgupta et al. 2017 (Science 358:793) used random sparse wiring. B1 asks whether the measured wiring improves on that randomness, and finds that it does not.

**Run details.**
- **Machine and code:** Apple M5, float64 hashing and float32 overlap scoring, single-threaded BLAS per worker, 8 workers. numpy 2.5.4, DoOR.data @ db323a4, MaleCNS v1.0 (checksums in `data/DATASETS.json`).
- **Draws and sizes:** 200 null draws per level for odours; 20 trials × 50 draws per level for the protocol arm. "Batch size" is the whole 4,000-item odour set or the 1,000-query protocol set per evaluation.
- **Wall time:** the protocol arm took 14,488 s for 80 trial files on a shared machine (load 30–50). This does not affect the accuracy numbers.
- **Code change during the run:** A12 sped up `b1.tags`, verified bit-identical in 40 cases before use.

## Labels

- **The MaleCNS olfactory wiring improves fly-hash retrieval over a degree-preserving null (odours, zero-filled, both hemispheres and thresholds): contradicted under specified conditions.** The upper CI bounds are < +2.5% everywhere, and R is significantly negative before Holm correction.
- **Senge's MaleCNS-R deficit of −2.06%: demonstrated** (replicated at −2.09% on his matrix), with the caveat that it does not survive Holm correction over our 12-test family. The left hemisphere does not show it.
- **"The wiring adds nothing" holds regardless of how missing odour data are filled: contradicted under specified conditions.** Under mean imputation the left hemisphere's wiring beats N1 by +3.38%, with a CI above the margin.
- **Per-glomerulus co-convergence Q carries the wiring's deficit: plausible but untested.** The pattern is consistent and descriptive only; the predeclared localization reading is "no effect to localize".
- **The wiring hurts a generic hash on SIFT, GloVe and MNIST (2017-style protocol): weakly supported.** All 12 cells are negative with CIs excluding 0, but it is a secondary analysis, and the input-to-glomerulus assignment is arbitrary.
- **Synapse weighting helps: contradicted under specified conditions** (L −6.9% vs N1w; R not distinguishable).
- **The same result on hemibrain, FlyWire and BANC: unknown.** Not re-extracted here; for these connectomes it is an absence of evidence, not a negative.
- **Whether a learned or plastic MBON readout benefits from the wiring: unknown.** B1 tests a fixed tag-overlap readout only.

<!-- BEGIN GENERATED B1 (scripts/trackB1_analyze.py) -->

**Predeclared replication verdict (odours, primary k, N1 and N3, both hemispheres, w ≥ 5 and w ≥ 1): REPLICATES SENGE.**
**Localization (NQ, w ≥ 5):** L: no effect to localize; R: no effect to localize.

Senge 2026 (single-author preprint, not peer reviewed), odour primary for MaleCNS R at all synapses: AP 0.4063 vs null 0.4148, Δ = −2.06%, p = 0.020.

### Odours: BIO against each null, with zero-filled primary and mean-imputation shown together (A2)

| matrix | filter | level | AP BIO | AP null (mean ± sd) | Δ zero-filled [95% CI] | p (Holm-12) | Δ mean-imputed [95% CI] | BIO Jaccard of level |
|---|---|---|---|---|---|---|---|---|
| w5_L | Senge | N0 | 0.4015 | 0.4190 ± 0.0039 | -4.16% [-4.97%, -3.37%] | 0.010 (nan) | +0.45% [-0.33%, +1.22%] | 0.053 |
| w5_L | Senge | N1 | 0.4015 | 0.4038 ± 0.0033 | -0.55% [-1.30%, +0.20%] | 0.557 (1.000) | +3.38% [+2.61%, +4.15%] | 0.080 |
| w5_L | Senge | N3 | 0.4015 | 0.4043 ± 0.0034 | -0.69% [-1.42%, +0.04%] | 0.458 (1.000) | +2.70% [+1.94%, +3.48%] | 0.087 |
| w5_L | Senge | NQ | 0.4015 | 0.3981 ± 0.0035 | +0.87% [+0.12%, +1.62%] | 0.348 (1.000) | +4.07% [+3.31%, +4.85%] | 0.089 |
| w5_R | Senge | N0 | 0.3950 | 0.4198 ± 0.0037 | -5.91% [-6.73%, -5.10%] | 0.010 (nan) | -2.91% [-3.69%, -2.12%] | 0.053 |
| w5_R | Senge | N1 | 0.3950 | 0.4046 ± 0.0035 | -2.38% [-3.16%, -1.60%] | 0.010 (0.119) | -0.63% [-1.43%, +0.19%] | 0.079 |
| w5_R | Senge | N3 | 0.3950 | 0.4053 ± 0.0036 | -2.54% [-3.31%, -1.76%] | 0.020 (0.219) | -1.24% [-2.01%, -0.45%] | 0.086 |
| w5_R | Senge | NQ | 0.3950 | 0.3993 ± 0.0039 | -1.08% [-1.85%, -0.35%] | 0.328 (1.000) | +1.02% [+0.24%, +1.80%] | 0.089 |
| w1_L | Senge | N0 | 0.4072 | 0.4228 ± 0.0040 | -3.69% [-4.49%, -2.91%] | 0.010 (nan) | -0.28% [-1.10%, +0.51%] | 0.058 |
| w1_L | Senge | N1 | 0.4072 | 0.4108 ± 0.0035 | -0.87% [-1.64%, -0.12%] | 0.299 (1.000) | +2.17% [+1.37%, +2.98%] | 0.086 |
| w1_L | Senge | N3 | 0.4072 | 0.4108 ± 0.0035 | -0.89% [-1.61%, -0.15%] | 0.259 (1.000) | +1.64% [+0.86%, +2.44%] | 0.093 |
| w1_L | Senge | NQ | 0.4072 | 0.4057 ± 0.0036 | +0.37% [-0.37%, +1.14%] | 0.677 (1.000) | +3.31% [+2.51%, +4.13%] | 0.096 |
| w1_R | Senge | N0 | 0.4010 | 0.4245 ± 0.0036 | -5.53% [-6.33%, -4.75%] | 0.010 (nan) | -3.73% [-4.54%, -2.93%] | 0.058 |
| w1_R | Senge | N1 | 0.4010 | 0.4096 ± 0.0036 | -2.09% [-2.88%, -1.30%] | 0.030 (0.299) | -1.12% [-1.94%, -0.29%] | 0.088 |
| w1_R | Senge | N3 | 0.4010 | 0.4104 ± 0.0040 | -2.28% [-3.03%, -1.51%] | 0.030 (0.299) | -1.73% [-2.54%, -0.94%] | 0.095 |
| w1_R | Senge | NQ | 0.4010 | 0.4046 ± 0.0038 | -0.88% [-1.63%, -0.13%] | 0.358 (1.000) | +0.37% [-0.41%, +1.20%] | 0.098 |

### Odour sensitivity arms (zero-filled)

| arm | level | Δ [95% CI] | p |
|---|---|---|---|
| w10_L_senge | N0 | -4.84% [-5.66%, -4.01%] | 0.010 |
| w10_L_senge | N1 | -0.12% [-0.92%, +0.67%] | 0.935 |
| w10_L_senge | N3 | -0.39% [-1.18%, +0.40%] | 0.716 |
| w10_L_senge | NQ | +1.15% [+0.38%, +1.94%] | 0.199 |
| w10_R_senge | N0 | -5.80% [-6.65%, -4.94%] | 0.010 |
| w10_R_senge | N1 | -1.89% [-2.70%, -1.07%] | 0.040 |
| w10_R_senge | N3 | -2.03% [-2.82%, -1.21%] | 0.040 |
| w10_R_senge | NQ | -0.16% [-0.97%, +0.63%] | 0.826 |
| w1_L_ours | N0 | -2.77% [-3.53%, -2.01%] | 0.010 |
| w1_L_ours | N1 | -0.45% [-1.17%, +0.29%] | 0.567 |
| w1_L_ours | N3 | -0.82% [-1.53%, -0.10%] | 0.229 |
| w1_L_ours | NQ | +0.25% [-0.48%, +0.96%] | 0.746 |
| w1_R_ours | N0 | -3.76% [-4.52%, -2.98%] | 0.010 |
| w1_R_ours | N1 | -1.32% [-2.09%, -0.56%] | 0.080 |
| w1_R_ours | N3 | -1.68% [-2.41%, -0.94%] | 0.050 |
| w1_R_ours | NQ | -0.35% [-1.08%, +0.40%] | 0.617 |
| w5_L_ours | N0 | -3.08% [-3.84%, -2.30%] | 0.010 |
| w5_L_ours | N1 | +0.00% [-0.73%, +0.76%] | 0.995 |
| w5_L_ours | N3 | -0.42% [-1.15%, +0.31%] | 0.567 |
| w5_L_ours | NQ | +0.80% [+0.09%, +1.54%] | 0.328 |
| w5_L_senge_weighted | N0 | -12.18% [-13.05%, -11.30%] | 0.010 |
| w5_L_senge_weighted | N1w | -6.94% [-7.78%, -6.12%] | 0.010 |
| w5_L_senge_weighted | N2w | -6.72% [-7.56%, -5.89%] | 0.010 |
| w5_L_senge_weighted | N3 | -7.55% [-8.38%, -6.74%] | 0.010 |
| w5_R_ours | N0 | -4.47% [-5.26%, -3.66%] | 0.010 |
| w5_R_ours | N1 | -1.75% [-2.50%, -0.99%] | 0.060 |
| w5_R_ours | N3 | -2.08% [-2.82%, -1.36%] | 0.010 |
| w5_R_ours | NQ | -0.63% [-1.38%, +0.11%] | 0.418 |
| w5_R_senge_weighted | N0 | -6.51% [-7.42%, -5.64%] | 0.010 |
| w5_R_senge_weighted | N1w | -0.98% [-1.84%, -0.13%] | 0.358 |
| w5_R_senge_weighted | N2w | -0.75% [-1.61%, +0.11%] | 0.527 |
| w5_R_senge_weighted | N3 | -2.08% [-2.92%, -1.22%] | 0.060 |

### NQ fidelity per odour matrix (achieved Q deviation in N1-null SD; acceptance; BIO Jaccard)

| matrix | draws | max \|Q dev\| | acceptance | Jaccard NQ | Jaccard N1 | Jaccard N3 | all invariants |
|---|---|---|---|---|---|---|---|
| w10_L_senge | 200 | 0.500 | 0.60 | 0.081 | 0.071 | 0.078 | True |
| w10_R_senge | 200 | 0.500 | 0.58 | 0.080 | 0.071 | 0.078 | True |
| w1_L_ours | 200 | 0.500 | 0.49 | 0.093 | 0.083 | 0.091 | True |
| w1_L_senge | 200 | 0.500 | 0.51 | 0.096 | 0.086 | 0.093 | True |
| w1_R_ours | 200 | 0.500 | 0.49 | 0.097 | 0.086 | 0.093 | True |
| w1_R_senge | 200 | 0.500 | 0.51 | 0.098 | 0.088 | 0.095 | True |
| w5_L_ours | 200 | 0.500 | 0.52 | 0.086 | 0.077 | 0.084 | True |
| w5_L_senge | 200 | 0.500 | 0.55 | 0.089 | 0.080 | 0.087 | True |
| w5_R_ours | 200 | 0.500 | 0.51 | 0.087 | 0.077 | 0.084 | True |
| w5_R_senge | 200 | 0.500 | 0.53 | 0.089 | 0.079 | 0.086 | True |

### 2017-style protocol (PCA to d = 51, 20 trials × 50 draws, AP@200)

| matrix | dataset | AP BIO | Δ vs N0 | Δ vs N1 [95% CI] | Δ vs N3 [95% CI] | Δ vs NQ [95% CI] |
|---|---|---|---|---|---|---|
| w5_L | sift | 0.3517 | -18.03% | -3.16% [-4.58%, -1.70%] | -3.22% [-4.32%, -2.12%] | -1.35% [-2.40%, -0.34%] |
| w5_L | glove | 0.0559 | -17.64% | -3.32% [-4.14%, -2.44%] | -3.19% [-3.98%, -2.26%] | -0.96% [-1.69%, -0.12%] |
| w5_L | mnist | 0.4524 | -9.23% | -2.22% [-2.87%, -1.56%] | -2.30% [-2.78%, -1.79%] | -0.95% [-1.43%, -0.43%] |
| w5_R | sift | 0.3574 | -16.44% | -3.64% [-4.79%, -2.48%] | -3.43% [-4.35%, -2.51%] | -1.57% [-2.45%, -0.73%] |
| w5_R | glove | 0.0563 | -16.94% | -3.60% [-4.49%, -2.70%] | -3.48% [-4.22%, -2.72%] | -1.48% [-2.15%, -0.79%] |
| w5_R | mnist | 0.4523 | -8.93% | -2.42% [-3.34%, -1.47%] | -2.43% [-3.17%, -1.67%] | -1.17% [-1.90%, -0.40%] |
| w1_L | sift | 0.3685 | -16.94% | -2.64% [-4.06%, -1.24%] | -2.58% [-3.71%, -1.45%] | -1.23% [-2.25%, -0.22%] |
| w1_L | glove | 0.0580 | -16.30% | -3.34% [-4.05%, -2.64%] | -3.31% [-4.00%, -2.65%] | -1.58% [-2.19%, -0.95%] |
| w1_L | mnist | 0.4707 | -8.22% | -2.07% [-2.69%, -1.43%] | -2.19% [-2.63%, -1.74%] | -1.09% [-1.58%, -0.58%] |
| w1_R | sift | 0.3734 | -15.99% | -3.54% [-4.83%, -2.28%] | -3.35% [-4.34%, -2.41%] | -1.68% [-2.61%, -0.83%] |
| w1_R | glove | 0.0583 | -16.08% | -3.81% [-4.71%, -2.89%] | -3.71% [-4.44%, -2.96%] | -1.87% [-2.59%, -1.21%] |
| w1_R | mnist | 0.4710 | -8.17% | -2.26% [-3.14%, -1.38%] | -2.22% [-2.92%, -1.51%] | -1.24% [-1.90%, -0.56%] |

**Secondary (protocol median Δ vs N1 over dataset × hemisphere × threshold × k, 60 combinations):** -1.96% (IQR -2.85% to -1.35%); Senge's protocol median −1.6% (IQR −3.2% to −0.3%, 168 combinations).

<!-- END GENERATED B1 -->

## B2. The ANN-Benchmarks frontier (reduced and gated on B1, A4)

**Scope.** B1 replicated Senge, so B2 ran in its reduced form, as predeclared (A4). The real-wiring hash is known to be no better than a null, so **ConnectomeHash was dropped**. B2 places the two published fly-derived methods on the frontier: FlyHash, the Dasgupta 2017 construction (Science 358:793), and DenseFly (Sharma & Navlakha 2018). They are compared against hnswlib, FAISS IVF-PQ (plain, added), FAISS IVF-PQ fast-scan (published) and ScaNN, on `sift-128-euclidean` and `glove-100-angular`, full splits. To our knowledge this is the first such placement.

**Result: inside the frontier on both datasets, as predicted in advance.** Both datasets get the predeclared verdict **INSIDE THE FRONTIER**. No fly method is competitive at any recall ≥ 0.8.
- **FlyHash on SIFT:** reaches recall@10 0.9 at 92 QPS. The best baseline there is ScaNN at 21,131 QPS, so FlyHash runs at 0.43% of it. It also reaches 0.95, at 0.61% of the best baseline.
- **FlyHash on GloVe:** reaches 0.9 at 54 QPS against ScaNN's 10,556 (0.52%). It does not reach 0.95; its maximum recall is 0.906.
- **DenseFly:** **not reached** at every level ≥ 0.8 on both datasets. Its maximum recall is 0.525 on SIFT and 0.420 on GloVe, within its full 36-configuration budget. "Not reached" is a reportable result here, not missing data.
- **Tuning budgets:** every fly method had at most hnswlib's 81 configurations (FlyHash 54, DenseFly 36). Every baseline ran its published or registered grid in full, so no comparison is against an under-tuned baseline.

**Against published numbers, with hnswlib as the shared anchor.** QPS here is comparable within this run. It can be compared with the ann-benchmarks.com plots only through relative positions, because the hardware differs: one pinned core of an Apple M5 in a linux/arm64 VM. The hnswlib build also differs: PyPI `hnswlib` 0.8.0, not the plots' fork (A11).
- At recall 0.9, FlyHash runs at 1.5% of hnswlib's QPS on SIFT (92 vs 6,038) and 4.5% on GloVe (54 vs 1,187).
- ScaNN and FAISS fast-scan lead hnswlib on both datasets at every level. Whether the published plots show the same ordering was not re-checked in this run.
- VIBE, the harness's successor, was not used (section 5 B2).

**Why the fly methods are slow: language-independent evidence.** The fly modules are numpy, with Python per-query overhead, while every baseline is C++. QPS therefore mixes the algorithm with the implementation language. To separate them, the fly modules record **candidates touched** and exact distances per query, and these do not depend on the language:
- **FlyHash:**
  - Its recall-0.9 configuration touches 1,278,276 inverted-list entries per query on SIFT, 1.28× the database, and 4,884,445 on GloVe, 4.1× the database.
  - Every query then counts overlaps over all n items and computes 5,000 exact distances.
  - Across all FlyHash configurations, candidates touched range from 465,384 to 5,280,664 per query on SIFT and from 157,347 to 4,884,445 on GloVe.
  - The cause is that a k-of-m winner-take-all tag puts each item in k lists of average length n·k/m. A query's k lists would then hold k²·n/m entries if list lengths were uniform: for m = 20d and k = 32 on SIFT, 1,024 × 10⁶ / 2,560 ≈ 400,000. The measured 1,278,276 is 3.2× that, because the KCs a query activates tend to be the popular ones, with long lists.
  - Per-query work in this index therefore grows linearly with n, whatever the implementation language.
- **DenseFly:** touches 47,740–242,406 candidates per query on SIFT and 45,957–278,885 on GloVe, but its pseudo-hash buckets do not hold the true neighbours often enough to pass recall 0.53.
- **The baselines:** the harness does not record per-query distance counts for their modules (`distcomps` = 0 in the export), so this comparison is one-sided and descriptive.
- **Would a C++ port reach the frontier?** It would have to be about 230× faster than the numpy version on SIFT and about 195× on GloVe just to match the best baseline at recall 0.9, while still touching more entries than the database holds. That it would remain inside the frontier is **plausible but untested**.

**Build time and index size.**
- **Build time:** fly builds are fast (FlyHash 22–67 s, DenseFly 11–34 s) and far quicker than hnswlib's (691–6,561 s, efConstruction = 500). They are comparable to ScaNN (7–83 s) and FAISS fast-scan (7–193 s). Build speed is therefore not a fly advantage over the strongest baselines.
- **Index size is not comparable for the fly modules.** The harness measures it as resident memory after the build minus before. On SIFT, which is float32 Euclidean, the fly modules keep a reference to the harness's training array rather than a copy, so their 71–281 MB (FlyHash) and 373–680 MB (DenseFly) exclude the 512 MB of vectors that every baseline counts. On GloVe the modules normalise into a new array, so the vectors are counted.

**Additional costs, measured after the frontier numbers (A15, descriptive).** One configuration per method and dataset, chosen by a rule fixed in A15 before measurement: the fastest point with recall ≥ 0.9, or the maximum-recall point if 0.9 is never reached.
- **Method:** build on all but the last 10,000 training points; insert those 10,000 one at a time; encode them in one batch; delete 100 items that the index returns for their own vectors.
- **Conditions:** one pinned CPU, one thread, in each method's own image.
- **Deletion:** every method supports it, and 0 of 100 deleted items were returned afterwards in every case. FlyHash's own query fills its top C with zero-overlap items when too few items share a KC, so the fly methods need a tombstone mask in addition to list removal. Their reimplementations for this measurement matched the frozen modules on 50 of 50 queries.
- **Insertion:** FlyHash inserts at 62–268 µs per item, against hnswlib's 3,161–4,410 µs per item (efConstruction 500) and 22–53 µs for FAISS fast-scan and ScaNN.
- **Encoding arithmetic:** the fly projection uses no multiplications, m·⌈0.1d⌉ additions, but that is 10,000–33,280 additions per item. FAISS fast-scan needs 67,584 (SIFT) and 122,000 (GloVe) multiply-adds. Measured encoding time per item is 2.7× (GloVe) to 9.3× (SIFT) higher for FlyHash than for fast-scan, with the numpy-vs-C++ caveat.

| dataset | method | configuration (A15 rule) | recall@10 | QPS | insert µs/item | encode µs/item | encoding arithmetic | deletion | delete µs/item |
|---|---|---|---|---|---|---|---|---|---|
| SIFT | flyhash | `euclidean_20_32_5000` | 0.966 | 92 | 268 | 112.0 | m*ceil(0.1d) = 2560*13 = 33,280 additions, 0 multiplications; top-32 of 2560 | supported (list/bucket removal + tombstone); 0/100 returned after | 5,324 |
| SIFT | densefly | `euclidean_20_16_5000` (0.9 not reached: max-recall point) | 0.525 | 30 | 89 | 30.1 | m*ceil(0.1d) = 2560*13 = 33,280 additions, 0 multiplications; sign + 16 block sums | supported (list/bucket removal + tombstone); 0/100 returned after | 525 |
| SIFT | faiss-ivfpqfs | `euclidean_512_10_10` | 0.913 | 14,662 | 53 | 12.0 | coarse nlist*d = 65,536 + PQ 16*d = 2,048 multiply-adds (4-bit fast scan) | supported (remove_ids); 0/100 returned after | 2,462 |
| SIFT | scann | `600_NaN_2_squared_l2_10_82` | 0.903 | 21,131 | 48 | — | not exposed by the API; included in insertion | supported (delete); 0/100 returned after | 117 |
| SIFT | faiss-ivfpq | `euclidean_16384_32_200` (0.9 not reached: max-recall point) | 0.752 | 1,786 | 167 | 86.8 | coarse nlist*d = 2,097,152 + PQ 256*d = 32,768 multiply-adds | supported (remove_ids); 0/100 returned after | 1,435 |
| SIFT | hnswlib | `euclidean_M_48_efConstruction_500_20` | 0.919 | 6,038 | 3,161 | — | n/a: stores raw vectors, no encoding step | supported (mark_deleted); 0/100 returned after | 3 |
| GloVe | flyhash | `angular_10_64_5000` | 0.906 | 54 | 62 | 16.3 | m*ceil(0.1d) = 1000*10 = 10,000 additions, 0 multiplications; top-64 of 1000 | supported (list/bucket removal + tombstone); 0/100 returned after | 8,533 |
| GloVe | densefly | `angular_20_16_5000` (0.9 not reached: max-recall point) | 0.420 | 34 | 122 | 28.9 | m*ceil(0.1d) = 2000*10 = 20,000 additions, 0 multiplications; sign + 16 block sums | supported (list/bucket removal + tombstone); 0/100 returned after | 1,121 |
| GloVe | faiss-ivfpqfs | `angular_1204_100_10` | 0.908 | 4,653 | 22 | 6.0 | coarse nlist*d = 120,400 + PQ 16*d = 1,600 multiply-adds (4-bit fast scan) | supported (remove_ids); 0/100 returned after | 1,331 |
| GloVe | scann | `2000_0_2_2_dot_product_55_95` | 0.907 | 10,556 | 32 | — | not exposed by the API; included in insertion | supported (delete); 0/100 returned after | 31 |
| GloVe | faiss-ivfpq | `angular_1024_25_200` (0.9 not reached: max-recall point) | 0.624 | 702 | 27 | 18.2 | coarse nlist*d = 102,400 + PQ 256*d = 25,600 multiply-adds | supported (remove_ids); 0/100 returned after | 1,454 |
| GloVe | hnswlib | `angular_M_64_efConstruction_500_80` | 0.920 | 1,187 | 4,410 | — | n/a: stores raw vectors, no encoding step | supported (mark_deleted); 0/100 returned after | 3 |

Source: `reports/trackB2_costs.json` (from `scripts/trackB2_costs.py` and `b2/costs/inner.py`; raw results in `raw_results/b2_costs/`).

**Plain IVF-PQ.** The added plain IVF-PQ baseline does not reach recall 0.8 on either dataset with its registered grid: maximum 0.752 on SIFT and 0.624 on GloVe. That is consistent with its having no exact re-ranking step. It is therefore not the "best baseline" anywhere at recall ≥ 0.8. The fast-scan variant with refinement carries the FAISS family there.

**Run conditions and incidents.**
- **Hardware and software:** Apple M5 host, colima linux/arm64 VM (8 vCPU, 24 GiB), one pinned vCPU per container.
- **Harness methodology:** single-query mode, k = 10, 10,000 test queries, QPS from the best of 5 runs, float32 data. Harness commit `2e081ad3`. Dataset files are as distributed, with hashes in the preregistration's dataset table. Images: faiss-cpu 1.15.1, hnswlib 0.8.0, scann 1.4.0, numpy 2.2.4 in the fly image.
- **Machine load:** at every algorithm boundary, the host's 1-minute load was 2.7–4.8 on 10 cores, after the other sessions' EXP1/EXP2 jobs had finished.
- **Two passes (A14, A16):**
  - The first pass, at parallelism 7, lost 26 containers to out-of-memory kills, while the harness still reported success.
  - The re-run, at parallelism 3 and then 1 for the GloVe FlyHash k = 64 builds, completed every registered grid. The pass that produced each result is listed in A16.
  - Every container had its own core, so the mixed parallelism affects only shared memory bandwidth.
- **Correction:** a faiss-ivfpq padding fault (A14) was fixed before its missing builds ran.
- **Sleep:** the host slept for 12 h during the GloVe densefly m = 20d query runs.
  - One query setting has an anomalous timing: m = 20d, p = 32, C = 20 records 31.5 ms against 15.4–17.0 ms for its neighbours.
  - It is flagged and cannot change any readout, because DenseFly never reaches 0.5 on GloVe.
  - Build times were not affected (A16 corrects A14 on this).
- **Timeouts:** no container hit the 12 h timeout.

## B2 Labels

- **FlyHash and DenseFly have never been placed on a modern ANN frontier.** Before: absence of evidence. After: **demonstrated.** Both are **inside the frontier** on SIFT 1M and GloVe 1.2M.
  - FlyHash runs at 0.4–0.6% of the best baseline's QPS at recall 0.8–0.95, and does not reach 0.95 on GloVe.
  - DenseFly does **not reach** recall 0.8 on either dataset. This is a measured negative against tuned production baselines (hnswlib, ScaNN, FAISS IVF-PQ fast-scan), not an absence of evidence.
- **The QPS gap is mostly implementation language (numpy vs C++): contradicted as the main explanation for FlyHash, descriptively.**
  - FlyHash's recall-0.9 configurations touch 1.3–4.1× the database size in list entries per query, and count overlaps over all n items, so their per-query work grows linearly with n.
  - That a compiled FlyHash would remain inside the frontier is **plausible but untested**.
- **Fly indexes support cheap insertion and deletion: weakly supported.** Insertion is about 10–70× faster than hnswlib's at efConstruction 500, but slower than ScaNN's and FAISS fast-scan's. Deletion needs a tombstone. Measured once per configuration (A15), descriptive.
- **ConnectomeHash on the frontier: not tested.** It was dropped as predeclared because B1 replicated Senge. Given B1, it would be no better than its null, and its d = 51 bottleneck is a design limit.
- **Fashion-MNIST, MNIST and NYTimes on the frontier: unknown.** Not run (A4: only if SIFT and GloVe were unexpected, and they were not).

<!-- BEGIN GENERATED B2 (scripts/trackB2_analyze.py) -->

#### glove-100-angular: **INSIDE THE FRONTIER**

| method | configs | max recall@10 | QPS @0.5 | QPS @0.8 | QPS @0.9 | QPS @0.95 | build s (min–max) | index size MB (min–max) |
|---|---|---|---|---|---|---|---|---|
| densefly | 36 | 0.420 | — | — | — | — | 11–20 | 812–1,098 |
| faiss-ivfpq | 21 | 0.624 | 13,332 | — | — | — | 34–563 | 101–492 |
| faiss-ivfpqfs | 96 | 0.996 | 24,408 | 9,203 | 4,653 | 2,906 | 7–127 | 523–532 |
| flyhash | 54 | 0.906 | 93 | 72 | 54 | — | 22–43 | 553–777 |
| hnswlib | 81 | 0.999 | 9,692 | 3,159 | 1,187 | 572 | 704–6,561 | 652–1,476 |
| scann | 84 | 0.998 | 41,591 | 21,018 | 10,556 | 5,402 | 58–83 | 516–542 |

| recall level | best baseline QPS | densefly (status, ratio) | flyhash (status, ratio) |
|---|---|---|---|
| 0.5 | 41,591 | not reached, — | inside, 0.0022 |
| 0.8 | 21,018 | not reached, — | inside, 0.0034 |
| 0.9 | 10,556 | not reached, — | inside, 0.0052 |
| 0.95 | 5,402 | not reached, — | not reached, — |

#### sift-128-euclidean: **INSIDE THE FRONTIER**

| method | configs | max recall@10 | QPS @0.5 | QPS @0.8 | QPS @0.9 | QPS @0.95 | build s (min–max) | index size MB (min–max) |
|---|---|---|---|---|---|---|---|---|
| densefly | 36 | 0.525 | 33 | — | — | — | 17–34 | 373–680 |
| faiss-ivfpq | 21 | 0.752 | 13,802 | — | — | — | 38–707 | 113–609 |
| faiss-ivfpqfs | 96 | 1.000 | 35,969 | 20,533 | 14,662 | 8,295 | 9–193 | 562–570 |
| flyhash | 54 | 0.994 | 101 | 92 | 92 | 92 | 30–67 | 71–281 |
| hnswlib | 81 | 1.000 | 16,195 | 9,303 | 6,038 | 4,194 | 691–2,511 | 661–1,358 |
| scann | 33 | 0.997 | 42,985 | 28,464 | 21,131 | 15,000 | 7–77 | 568–627 |

| recall level | best baseline QPS | densefly (status, ratio) | flyhash (status, ratio) |
|---|---|---|---|
| 0.5 | 42,985 | inside, 0.0008 | inside, 0.0024 |
| 0.8 | 28,464 | not reached, — | inside, 0.0032 |
| 0.9 | 21,131 | not reached, — | inside, 0.0043 |
| 0.95 | 15,000 | not reached, — | inside, 0.0061 |

<!-- END GENERATED B2 -->
