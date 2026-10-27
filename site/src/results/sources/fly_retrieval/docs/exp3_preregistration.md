# EXP3 preregistration: does fly-brain structure help memory retrieval, and if so where

**Status: SIGNED 2026-10-23** (`../SIGNOFF_EXP3_signed.md`). The amendments requested at sign-off (A1–A5) are logged in `docs/exp3_amendments.md` and incorporated below, before any result exists. At the time of signing, no retrieval, novelty or ANN number had been measured. What exists so far is connectome extraction, null-sampler invariant checks, the connectome-only Track C ranking, dataset downloads and checksums. None of these touches a query.

Brief: `../EXP3_retrieval_prompt.md` (the experiment author's prompt). Project root: `fly_retrieval/`. This is a new sibling of `fly_track/` and reuses its extraction discipline. Every later change is logged in `docs/exp3_amendments.md` before it takes effect.

## 0. Framing (read first)

Most of this question is already answered, and the answer is mostly no. This experiment is a **falsification exercise with one open niche attached** (Track A). It also includes one replication (Track B) and one speculative hypothesis (Track C). It must not be written up as "we tested whether the fly brain improves retrieval".

Of the four meanings of "better data fetching":

1. **Similarity search (ANN retrieval).** Tracks B and C test this.
2. **Choosing what to inspect next under a budget.** This is open and has no fly-derived work. It is not attempted here (section 10).
3. **Semantic document retrieval / RAG.** Out of scope. The one real system is BioVSS (ICDE 2025), and its baselines are FAISS IVF variants on vector-set Hausdorff search, never HNSW. It is not a RAG result.
4. **Database, API and network fetching.** This is a **category error**, not an absence of evidence. Its bottlenecks are I/O, indexes, query plans, permissions and rate limits, and there is no fly mechanism for any of them. It is not tested.

Track A (novelty detection) is a fifth, adjacent reading: distance-sensitive membership.

## 1. Settled starting points (not re-litigated) and their verification status

Verdicts come from `docs/exp3_sources.md`, which holds full-text checks done on 2026-10-23. Every Senge 2026 number is from a **single-author preprint that has not been peer reviewed** (arXiv:2610.09114 v1).

| Settled point | Label carried into the write-up | Verification (see `docs/exp3_sources.md`) |
|---|---|---|
| The fly hash's advantage is per active cell, not per operation. Under matched projection arithmetic, a Gaussian baseline beats it everywhere (Senge). The 2017 advantage (MNIST k=4, 16.0% → 44.8%) was measured against a single-table dense Gaussian LSH at matched operation count. | **contradicted under matched-arithmetic conditions — against real-valued Gaussian projections only; against one-bit codes the fly hash leads from k = 32** (Senge, unreviewed). This qualifier travels with the label every time it appears (A5). | S1, S2 verified. S3 verified with a qualifier: it holds against real-valued Gaussian projections. Against one-bit sign codes on odours, the fly hash leads from k = 32. |
| Connectome wiring adds nothing to the hash (4 connectomes, 7 hemispheres; median −1.6%) | **plausible but untested at a trustworthy level**: one unreviewed preprint. B1 replicates it. | S4 verified (MaleCNS R −2.06%, p = 0.020). S5's −1.6% is the median over 168 protocol combinations, not the odour primary. |
| FlyHash has never been benchmarked against a modern ANN index | **absence of evidence**, not a measured defeat | S6 verified directly against the harness's algorithm list |
| FlyVec is contradicted on its own terms | **contradicted** | S7 verified (it beats word2vec on WiC and 20NG only) |
| Removing the biology improves performance (DenseFly 0.395 vs 0.212; BioHash 26% → 55%; block codes per bit) | **demonstrated**, as a repeated pattern | S8 verified. S9 holds at k = 16 against FlyHash with label ground truth. S10 holds per bit only. |
| PN→KC connectivity is non-random (Zheng), and the non-randomness does not help general discrimination | **demonstrated** (non-random); **demonstrated** (does not improve general discrimination) | S11 **corrected**: the main text gives z = 13.8, not 14.3. S12 and S13 verified; Caron's average is 7 claws. |
| Two of the four meanings of "better data fetching" are out of scope | RAG: no fly work beyond BioVSS. DB/API/network: **category error** | S15 verified |
| The 2018 FBF is the best fly-derived result (SIFT 0.535 / 0.345 / 0.002) and has never met production baselines | open, which is what Track A tests | S14 **corrected**: the values are correlations with true novelty, not AUCs |

## 2. Hardware, software and data (applies to every number)

- **Machine:** Apple M5, 10 cores, 32 GB RAM, macOS 26.6.2 (build 25G83).
- **Python and libraries:** Python 3.12.13 in `fly_retrieval/.venv`, locked in `requirements.lock` (numpy 2.5.4, scipy 1.18.1, faiss-cpu 1.15.1, hnswlib 0.8.0, datasketch 2.0.0, h5py 3.16.0).
- **Precision:** float32 for all vectors, projections and indexes. Ground-truth distances are float64.
- **Threads:** timing is single-threaded, with `OMP_NUM_THREADS=1`, `faiss.omp_set_num_threads(1)`, and hnswlib `num_threads=1`.
- **Batch size:** 1 query per call for every QPS number. Batch-mode numbers, if reported, are labelled as such and kept separate.
- **Track B2:** runs inside the ANN-Benchmarks harness in a linux/arm64 Docker container on colima, native and not emulated. ScaNN has no macOS wheel (it ships only `manylinux_2_27_aarch64`/`x86_64` wheels), so this is the only native route. The harness pins one CPU per container. The VM's CPU count and memory are recorded in every B2 result file. B2 QPS is comparable *within* this run. It is comparable to the published ann-benchmarks.com plots (AWS r6i.16xlarge, April 2025) only through relative positions, with hnswlib as the shared anchor.
- **Connectome:** MaleCNS v1.0 flat tables, minconf-0.5 (CC-BY 4.0). SHA-256 values are in `graphs/extraction_summary.json` and match `fly_track/data_manifest.json`.
- **Benchmark data:** ANN-Benchmarks HDF5 files, `http://ann-benchmarks.com/<name>.hdf5`, downloaded 2026-10-23. SHA-256 values are in `data/DATASETS.json`. Any further dataset is checksummed into the same file before its first use, and that is logged as an amendment.

| Dataset | Train × dim | Test | Distance | SHA-256 (first 16) | Used in |
|---|---|---|---|---|---|
| `fashion-mnist-784-euclidean` | 60,000 × 784 | 10,000 | euclidean | `7f24e5122b713463` | B2 |
| `glove-100-angular` | 1,183,514 × 100 | 10,000 | angular | `544af1d5e84e112c` | B1, B2 |
| `mnist-784-euclidean` | 60,000 × 784 | 10,000 | euclidean | `35ff29594d96d1c5` | A, B1, B2 |
| `nytimes-256-angular` | 290,000 × 256 | 10,000 | angular | `6ad5d2cde6d6a6f2` | A (text), B2 |
| `sift-128-euclidean` | 1,000,000 × 128 | 10,000 | euclidean | `dd6f0a6ed6b7ebb8` | A (5k subset), B1 (10k subsets), B2 |
| DoOR.data (ropensci) | commit `db323a496577` (Senge's db323a4) | | | `bc2aa5414ff54d3a` (consensus matrix) | B1 odours; A fly odours (Hallem 2006 columns) |

## 3. Common definitions

- **SESOI (smallest effect size of interest):** a relative difference of **2.5%** in the track's primary accuracy metric. This is the stricter of Senge's two margins: he reports 80% power at 2.5% and an equivalence margin of ±5%. It is fixed here and not derived from this experiment's data.
- **Labels used in every conclusion:** demonstrated / plausible but untested / weakly supported / contradicted under specified conditions / unknown. Absence of evidence is always kept distinct from evidence of no benefit.
- **Confidence intervals:** 95%, by two-stage bootstrap with 10,000 resamples. Stage one resamples trials (or odorants or queries, as named per track). Stage two resamples null draws within each resample. **Monte Carlo randomization p-values** use the BIO rank among null draws, with the floor 1/(n+1). Holm correction is applied within each declared family.
- **Seeds:** every seed range is listed per track. Validation seeds and test seeds never overlap. Test sets are evaluated once.
- **Hash (shared by B1, B2-fly and C):**
  1. y = Mᵀx, where M is binary d × m.
  2. Top-k winner-take-all with **random tie priority**, seeded per trial. This is Senge's code baseline; index order is the sensitivity arm.
  3. The tag is binary, and ranking is by tag overlap with random tie-breaking.
  4. APL is modelled only as this global k-WTA inhibition. That is a stated modelling choice: the extraction records both APL neurons and their roughly 196k APL→KC synapses but does not wire them.

## 4. Track A: distance-sensitive novelty detection (the one untested niche; run first)

**The gap, verified.** Dasgupta et al. 2018 (PNAS) compared the fly Bloom filter (FBF) only against a traditional Bloom filter and the locality-sensitive Bloom filter (LSBF; Kirsch & Mitzenmacher 2006). It never compared it against SimHash, MinHash with banded LSH, or count-min sketch. **Correction to the brief:** its headline numbers are **correlations** between true and predicted novelty, not AUCs. On SIFT they are 0.535 ± 0.03 (FBF), 0.345 ± 0.03 (LSBF) and 0.002 ± 0.02 (Bloom filter). Ground truth is the continuous f(x, S) = min_{s∈S} d(x, s), with no novelty threshold. Memory was m = 30n bits, with k varied over [5, 50] under 10-fold cross-validation. Its SI (distance d, LSBF parameters, Pearson or Spearman, the k behind the SIFT numbers) could not be accessed, so those details are re-specified here and labelled as our choices.

**Datasets.** These are the 2018 paper's five, at its sizes, plus text:

| Dataset | n | d | Source | Status |
|---|---|---|---|---|
| Fly odours (Hallem & Carlson 2006) | 110 | 24 | DoOR.data @ db323a4, `Hallem.2006.EN` columns | available: the `Hallem.2006.EN` columns across DoOR receptor files give exactly 110 odorants × 24 receptors with no missing values (checked 2026-10-23); the spontaneous-firing row `SFR` is excluded |
| Primate faces (face-patch responses; refs Chang & Tsao 2017 / Stevens 2018) | 2,000 | 99 | no public deposit found | **ABANDONED (A6)**, handed off to the owner, never substituted |
| SIFT | 5,000 | 128 | `sift-128-euclidean` train, seeded subset | downloaded |
| MNIST | 5,000 | 784 | `mnist-784-euclidean` train, seeded subset | downloaded |
| Random exponential | 1,000 | 20 | i.i.d. Exp(1), seed 800000 | generated |
| **Text embeddings (primary)** | 5,000 | 256 | `nytimes-256-angular` train, seeded subset. TF-IDF + random projection of NYT articles (CC BY 4.0), not a neural embedding. | downloaded |
| ~~Text embeddings (secondary, A3)~~ | — | — | VIBE `yahoo-minilm-384-normalized`: **dropped (A6)**, because the source-text licence could not be resolved. The Track A report states that the text result does not speak to neural-embedding practice. | dropped |

Subset seeds are 810000 + dataset index. Distance d is Euclidean, except angular datasets, which use cosine distance on L2-normalised vectors. f is rescaled to [0, 1] per dataset by dividing by the maximum over the test fold. Spearman ρ is unaffected by that rescaling.

**Protocol (2018-faithful, extended).**

- 10-fold cross-validation, with fold assignment seeded at 830000 + dataset index. Folds 0–7 are test folds. Folds 8–9 are the **validation pair**, used only for tuning.
- **Validation:** the stored set is folds 0–7, and the queries are folds 8–9 plus their near-duplicates.
- **Test fold f ∈ {0, …, 7}:** the stored set S is the other seven test folds, and every item of fold f is queried. Validation items are never stored or queried at test time. Tuning sees items that are stored at test time, but never a test query.
- **Near-duplicate augmentation**, so that familiar queries exist, which is the production use case: each test fold also queries an equal number of perturbed copies of random stored items, x' = s + ε. Here ε ~ N(0, σ²I) with σ chosen so that E‖ε‖ = 0.25 × the median nearest-neighbour distance within S. The noise seed is 820000 + fold.
- **Ground truth:** continuous f(x, S), plus a binary label "familiar" iff f(x, S) ≤ τ, where τ = 0.5 × the median within-S nearest-neighbour distance.

**Memory budgets (matched, in bits per stored item):** B ∈ {3, 10, 30, 100}. That is total memory B·n_S bits. 10 and 30 are the 2018 paper's values.

- Random parameters regenerated from a seed (projections, hyperplanes, hash seeds) are **not** counted toward memory for any method. Their compute is counted in encoding cost.
- Counters count at their stored width.
- Each method's measured in-memory bytes are reported alongside, so any bookkeeping overhead is visible.

**Methods.** Every method is implemented in `src/flyret/novelty/` with the same insert and query interface.

| Method | Construction at budget B·n bits | Novelty score | Tuning grid (≤ 24 configs per dataset × budget) |
|---|---|---|---|
| **FBF** (fly) | m = B·n binary KC cells, initialised to 1. Sparse binary projection, each KC sampling ⌈0.1·d⌉ inputs (2017/2018 construction). Inputs pass through the 2017 normalisation: shift each feature by its \|min\| on S, then rescale each vector to mean 100. Top-k WTA. Insert sets the item's k cells to 0 (δ = ε = 0, the time-ignored binary case). | (1/k) Σ cell values over the query's k active cells | k ∈ {5, 10, 20, 30, 40, 50} × sampling ∈ {0.1·d, 6 inputs} = 12 |
| **GBF** (control: biology removed, same arithmetic budget) | as FBF, but a dense Gaussian projection replaces the sparse binary one | as FBF | k as FBF = 6 |
| **LSBF** (Kirsch & Mitzenmacher 2006; 2018 anchor) | L partitions of B·n/L bits. Each partition hashes a concatenation of r SimHash bits (random hyperplanes) into its partition. | 1 − (fraction of partitions whose bit is set) | L ∈ {4, 8, 16, 32} × r ∈ {4, 8, 12, 16, 20, 24} = 24 |
| **Bloom filter** (anchor) | standard filter, h = round((B) ln 2) hashes of the exact float32 bytes | 1 − (membership ∈ {0, 1}) | none |
| **SimHash store** (Charikar 2002; Manku et al. 2007) | one b-bit SimHash fingerprint per item, b = B (B = 3 is a 3-bit fingerprint, a deliberately honest floor). A full scan is used. Manku's permuted tables change speed, not accuracy, and would cost t× the memory. Their accuracy equals this scan; their memory is reported, not used. | min Hamming distance / b | none (b fixed by B) |
| **MinHash + banded LSH** | weighted MinHash (Ioffe 2010 ICWS, via datasketch `WeightedMinHashGenerator`) on nonnegative inputs. A signed vector is split into [x⁺, x⁻], which is our design choice and is flagged as such. There are b bands of r rows, and each band key is hashed into a band-partitioned bit array of B·n/b bits. | 1 − (fraction of bands hit) | (b, r) ∈ {4, 8, 16, 32} × {1, 2, 4, 8} minus configurations needing > 256 hashes = ≤ 16 |
| **Count-min sketch over LSH band keys** (Cormode & Muthukrishnan 2005; LSH-keyed as in RACE) | SimHash band keys (b bands of r bits) are inserted into a CMS of depth D and width w with 8-bit saturating counters, where D·w·8 = B·n. It supports deletion by decrement, which is exact unless a counter saturated; saturation counts are reported. | 1 − (1/b) Σ_bands 1[min-count > 0] | D ∈ {2, 4} × b ∈ {4, 8, 16} × r ∈ {8, 16} = 12 |

**Tuning (fixed budget, identical rule for every method):** the full grid is run on the validation pair, and the configuration with the highest validation Spearman ρ is selected, with ties going to lower encoding cost. That configuration is then evaluated once on test folds 0–7.

**Metrics.**

- **Primary:** Spearman ρ between predicted novelty and f(x, S) over all test queries (held-out items and near-duplicates), computed per fold and then averaged over folds. The held-out-only ρ is also reported; that is the 2018 protocol, and the reproduction anchor uses it. Spearman is chosen over Pearson because methods emit scores on unrelated scales, and the 2018 paper's correlation type is unverified. Pearson r is also reported for comparison with 0.535 / 0.345 / 0.002.
- **Secondary:**
  - AUROC and AUPRC for the binary familiar label.
  - **False positive rate (novel item called familiar) and false negative rate (familiar item called novel)** at the decision threshold that minimises FPR + FNR on the validation pair, applied unchanged to the test folds.
  - FNR at FPR = 1%.
  - Every section-7 cost, including encoding cost per item (multiply-adds and ns, single thread), insert time per item, query time per item, and deletion support (FBF and Bloom filters: no; CMS: yes).

**Statistics.** The 95% CI comes from a bootstrap over test folds and, within each fold, over queries, with 10,000 resamples. The paired difference Δ = ρ_FBF − max(ρ_SimHash, ρ_MinHash, ρ_CMS) is computed per (dataset, budget). "Best production baseline" is chosen per cell on validation, never on test.

**Predeclared outcomes.**

- **Reproduction anchor (checked before the production comparison is interpreted):** at B = 30 on SIFT, using held-out queries only, the expected order is ρ_FBF > ρ_LSBF > ρ_BF (2018: 0.535 / 0.345 / 0.002). If our LSBF ties or beats our FBF, this is reported as a failure to reproduce 2018, and every FBF claim below is qualified by it.
- **Narrow win ("holds up"):** Δ has a lower CI bound > 0 at ≥ 3 of 4 budgets, on ≥ 4 of the datasets run, including the text corpus. The write-up must then state FBF's encoding cost relative to the winning baseline's. If FBF costs ≥ 10× more per item, the label becomes "accuracy win at matched memory, at higher encoding cost".
- **Does not survive:** Δ has an upper CI bound < 0 at ≥ 3 of 4 budgets on ≥ 4 datasets. The branch closes with the statement that the one remaining fly-derived retrieval advantage does not survive contact with production baselines.
- **Mixed:** every other pattern is reported cell by cell, labelled "weakly supported" or "contradicted under specified conditions" per dataset and budget. It is never summarised as a win.
- **Biology-removed control:** ρ_FBF − ρ_GBF is reported per cell. If GBF ≥ FBF, the advantage, if any, is not attributable to the fly's sparse binary wiring.


## 5. Track B: replicate Senge with the baselines the field uses

### B1. Connectome versus the null ladder

**Extraction (frozen):** `configs/olfactory_extraction.yaml` and `src/flyret/extract.py`.

- **Filtering:** status `Traced`, duplicate weight rows summed, autapses dropped. This is the LC10a discipline from `fly_track/configs/extraction.yaml`.
- **Projection neurons:** uniglomerular olfactory PNs (`class == ALPN`, glomerulus whitelist reproducing Senge's code rule: M_*, CB*, VP*, MZ* and Z dropped).
- **Kenyon cells:** all `Kenyon_Cell`. PNs and KCs are taken from the same hemisphere.
- **Matrix:** M[g, i] = 1 iff some PN of glomerulus g makes ≥ `min_weight` synapses onto KC i. KCs with no such input are dropped.
- **Threshold, a modelling choice and not a measurement:** `min_weight = 5` is primary, matching the LC10a extraction. `min_weight = 1` is the **Senge-fidelity arm**, his own rule. `min_weight = 10` is sensitivity only. The synapse-weighted W (input y = Wᵀx) is a sensitivity arm.
- **Positive control:** at w ≥ 1 the rule reproduces Senge's reported MaleCNS-R matrix exactly: d = 51 and m = 1,886, with maximum fan-out 473 on DC1 and mean fan-out 195.4 (he reports "up to 473 cells for DC1 against a mean near 195").

| Matrix | Hemisphere | d | m (KCs) | mean inputs/KC | fan-out min/mean/max (max glomerulus) | matrix hash (first 16) |
|---|---|---|---|---|---|---|
| malecns_upn_kc_w5 (primary) | L | 51 | 1,855 | 4.86 | 15 / 176.7 / 463 (DP1m) | `3aa37cec6d4f4a25` |
| malecns_upn_kc_w5 (primary) | R | 51 | 1,878 | 4.79 | 12 / 176.3 / 437 (DC1) | `244cfbc53073953b` |
| malecns_upn_kc_w1 | L | 51 | 1,865 | 5.30 | 17 / 193.9 / 489 (DP1m) | `a4f257f5d6cd5d2e` |
| malecns_upn_kc_w1 | R | 51 | 1,886 | 5.28 | 19 / 195.4 / 473 (DC1) | `03bf3f3a36979b1d` |
| malecns_upn_kc_w10 | L | 51 | 1,849 | 4.18 | 10 / 151.6 / 426 (DP1m) | `01ebc11cf243d9e3` |
| malecns_upn_kc_w10 | R | 51 | 1,853 | 4.22 | 11 / 153.2 / 374 (DC1) | `d2e696acff831eb5` |

The primary k is round(0.05·m): 93 (L) and 94 (R) at w ≥ 5. Full hashes and data-file checksums are in `graphs/extraction_summary.json`.

**Null ladder (frozen):** `src/flyret/nulls.py`. Invariants are checked by `scripts/check_nulls.py`, gate G2.

| Level | Preserves | Sampler |
|---|---|---|
| N0 | edge count only (Erdős–Rényi; weak null, anchors scale only) | uniform placement |
| N1 | glomerular fan-out (row sums) and inputs per KC (column sums); Senge's null | curveball trades, 30 sweeps |
| N2 | N1 plus each KC's claw-count distribution | see "N2 collapse" below |
| N3 | N2 plus glomerulus × KC-class block counts (γ, α′β′, αβ, other) | curveball trades only within a KC class |
| NQ (A1) | N3 plus per-glomerulus co-convergence Q_g held within 0.5 N1-null SD of its BIO value | curveball trades within a KC class, accepted only if every Q_g stays in tolerance |
| BIO | real wiring | — |

**N2 collapse (needs a decision at sign-off).** In the binary glomerulus × KC matrix used by Senge and by Dasgupta 2017, a KC's claw count *is* its column sum. N1 already preserves that sum exactly, so on the binary primary **N2 is the same ensemble as N1**. N2 is not sampled separately for binary arms; it is reported as "= N1 by construction". N2 differs from N1 only on the synapse-weighted arm, where each KC also keeps the exact multiset of its claw weights. The alternative, a PN-level matrix in which sister PNs of one glomerulus count as separate claws, is set out in section 11 for the reviewer to choose.

The measured mixing at w ≥ 5 is a BIO overlap (Jaccard) of 0.070–0.080 for N1 and N3, against 0.053 for N0. N3's block constraint therefore barely restricts the ensemble. That is reported as a finding about this connectome, not tuned.

**NQ (amendment A1, frozen).** Implementation: `src/flyret/nulls.py` `sample_nq`.

- **Sampler:** start from BIO and propose N3 moves (curveball trades between same-class KC columns), 30 sweeps of proposals.
- **Acceptance rule:** a trade is accepted only if every glomerulus afterwards satisfies |Q_g − Q_g(BIO)| ≤ 0.5 · sd_N1(Q_g).
- **Tolerance scale:** sd_N1 comes from 200 N1 draws, seeds 750000–750199, per matrix (`configs/nq_sd.json`).
- **Per-draw reporting:** the achieved Q deviation (maximum and mean |dev| in null SD), the acceptance rate, and the BIO Jaccard.
- **Informative only if:**
  - (i) every draw stays within tolerance and keeps all N3 invariants;
  - (ii) the mean BIO Jaccard is ≤ 0.5, so NQ has actually moved away from BIO;
  - (iii) N3 draws do *not* already preserve Q (mean |Q dev| ≥ 1.0 null SD).
- **Collapse rule:** if (ii) or (iii) fails, NQ has collapsed, and the ladder is reported as uninformative at that rung.
- **Seeds:** NQ draws in B1 use 780000 + 100·trial + draw.

Pre-measurement check (`scripts/freeze_nq.py`, 5 trial draws per matrix, seeds 770000+; no retrieval):

| Matrix | NQ acceptance | NQ max \|Q dev\| (null SD) | NQ BIO Jaccard | N3 mean \|Q dev\| (null SD) |
|---|---|---|---|---|
| malecns_upn_kc_w5_L | 0.45 | 0.50 | 0.081 | 1.92 |
| malecns_upn_kc_w5_R | 0.44 | 0.50 | 0.082 | 1.65 |
| malecns_upn_kc_w1_L | 0.43 | 0.50 | 0.088 | 1.71 |
| malecns_upn_kc_w1_R | 0.41 | 0.50 | 0.092 | 1.67 |

NQ therefore shuffles edges as freely as N1 and N3 (Jaccard ≈ 0.08–0.09). It differs from them in the statistic it holds fixed: N3 draws drift 1.6–1.9 null SD from BIO's Q, and NQ draws stay within 0.5. Edge overlap does not separate NQ from N3; Q fidelity does. All three criteria pass on every matrix.

**Datasets and protocol (Senge's 2017-style protocol, independently reimplemented; his code is not used):**

- **SIFT, GloVe and MNIST.** For each trial:
  - Draw a seeded subset of 10,000 database vectors and 1,000 query vectors.
  - Fit PCA on the database to d components, one per glomerulus of the matrix (51).
  - Assign components to glomeruli by a fresh random permutation per trial.
  - Centre each vector by its own mean.
  - Ground truth is the top 2% (200) by Euclidean distance in the *original* space.
  - Sources: SIFT and MNIST are the ANN-Benchmarks `sift-128-euclidean` and `mnist-784-euclidean` train splits. GloVe is `glove-100-angular` train. This departs from Senge, who used GloVe 6B 300d; the departure is declared.
  - Trial seeds are 700000–700019 (20 trials), with 50 null draws per level per trial; null seeds are 710000 + 100·trial + draw.
- **Odours (Senge's primary).** DoOR 2.0 consensus matrix at commit db323a4.
  - Keep glomeruli measured for ≥ 40 odorants and odorants measured on ≥ 12 of those glomeruli.
  - Unmeasured entries are 0 (primary). Mean imputation is a sensitivity arm, reported beside the primary, because Senge's deficit disappears under imputation.
  - **Two filters (A2):**
    - **Senge-reproduced filter (primary):** before any odour number, our reimplementation of his mapping must reproduce 35 glomeruli, 172 odorants and 28.7% missing. If it cannot, the deviation is logged and ours is primary.
    - **Our filter (sensitivity):** 37 glomeruli, 178 odorants, 33.8% missing.
    - If the two disagree on the primary endpoint, that is reported as a robustness finding about Senge's conclusion.
  - Build 4,000 mixtures of 2–5 profiles with Dirichlet(1) weights, seed 720000, normalised to unit mean.
  - Every mixture is a query against the other 3,999. Ground truth is the 10 nearest by Euclidean distance on raw responses; the metric is AP@10.
  - Glomeruli without DoOR data get input 0.
  - There are 200 null draws per level, with seeds 730000–730199.
  - Checked 2026-10-23: the download and parse work, but the filter does not yet reproduce Senge's counts (section 11, item 4). Before any odour measurement, a reproduction check must reproduce 35 glomeruli, 172 odorants and 28.7% missing.
- **k:** k = round(0.05·m) is primary. Secondary k ∈ {8, 16, 32, 64} are Senge's secondary sizes and are reported descriptively.
- **Metrics:**
  - Primary: AP@n = (1/n) Σ_{i≤n} prec@i · rel(i), with n = 200 for the protocol datasets and n = 10 for odours. A neighbour that is never retrieved counts as a miss.
  - Also reported: recall@n and Dasgupta 2017's mAP, which averages over retrieved neighbours only, for comparison with the original numbers.
- **Endpoint:** Δ_ℓ = AP(BIO) / mean AP(N_ℓ) − 1, per hemisphere, dataset and threshold.

**Predeclared readings, all on odours at the primary k.** The replication verdict is judged against Senge's **odour primary (−2.06%, MaleCNS R)**. His −1.6% protocol median is used only in the secondary comparison (A5).

- **Replicates Senge** (flat from N1 onward): in **both** hemispheres, at **both** w ≥ 5 and w ≥ 1, the upper 95% CI bound of Δ_1 and of Δ_3 is < +2.5%. Whether the CI also lies inside ±2.5% (equivalence), and its sign, are reported against Senge's −2.06% for MaleCNS R.
- **Contradicts Senge** (monotone rise toward BIO): in both hemispheres at w ≥ 5, the lower CI bound of Δ_1 is > +2.5%, **and** the point estimates order as AP(N1) ≤ AP(N3) ≤ AP(BIO).
- **Partial:** any other pattern, for example one hemisphere only, or the result changes between w ≥ 5 and w ≥ 1. It is reported as "threshold-dependent" or "hemisphere-dependent", never as a replication.
- **Secondary:** the median Δ_1 over (dataset × hemisphere × k) on SIFT, GloVe and MNIST is compared with Senge's protocol median of −1.6% (IQR −3.2% to −0.3%, over 168 combinations).
- **Localization reading (NQ, A1; kept out of the replication verdict, which stays on N1 and N3 for comparability with Senge, who had no NQ):** write Δ_Q = AP(BIO) / mean AP(NQ) − 1, odours, primary k, w ≥ 5.
  - **"Q carries the effect":** the lower CI bound of Δ_1 is > +2.5% and the CI of Δ_Q lies inside ±2.5%.
  - **"The effect lives outside Q":** the lower CI bound of Δ_Q is > +2.5%.
  - **"No effect to localize":** the upper CI bound of Δ_1 is < +2.5%. NQ is then reported descriptively only.
  - Both hemispheres are required for "demonstrated".
- **Holm family:** 2 hemispheres × 2 thresholds × 3 levels (N1, N3, NQ) = 12 tests (A1).
- **Imputation, reported next to the primary rather than after it (A2):** Senge's deficit disappears under mean imputation. Our mean-imputation arm is shown in the same table row as the zero-filled primary.
- **Scope statement, written into the report whatever the outcome:** this replicates MaleCNS only, 2 of Senge's 7 hemispheres. Hemibrain, FlyWire and BANC are not re-extracted. Extending to them is a possible later amendment.

### B2. The ANN-Benchmarks frontier (expected: fly methods sit well inside it)

**Harness:** github.com/erikbern/ann-benchmarks at commit `2e081ad32c1eccab72dcb739ad886c310b90f715`, which was the head of main on 2026-10-23 (recorded in `configs/ann_benchmarks_commit.txt`). The README now says the harness is "no longer actively maintained" (last commit 2026-07-10). We use it anyway because the brief asks for comparability with published numbers. VIBE is noted as its successor and is not used.

**Methodology is the harness's own:**

- k = 10.
- A returned point counts toward recall if its distance is ≤ the k-th true distance + 1e-3.
- QPS = 1 / mean per-query time, best of 5 runs, single CPU pinned.
- Build time = wall-clock time of `fit()`. Index size = RSS after `fit()` minus RSS before.

**Datasets (A4):** `sift-128-euclidean` and `glove-100-angular` only, with full train and test splits as distributed. These are the 2017 paper's two datasets that sit at about 1M points. Fashion-MNIST, MNIST and NYTimes become a logged amendment only if these two show something unexpected.

**Gating (A4):** B2 runs after B1. ConnectomeHash is carried only as B1's outcome warrants:
- If B1 replicates Senge, the B1 matrix is known to be no better than a null. B2 then reduces to FlyHash and DenseFly against modern indexes, and the report says ConnectomeHash was dropped for that reason.
- Otherwise ConnectomeHash runs as specified below.

**Baselines and their tuning budgets.** Published `config.yml` grids are used unmodified:

| Method | Build grid | Query grid | Configs |
|---|---|---|---|
| hnswlib | M ∈ {4, 8, 12, 16, 24, 36, 48, 64, 96}, efConstruction = 500 | ef ∈ {10, 20, 40, 80, 120, 200, 400, 600, 800} | 81 |
| faiss-ivfpqfs (published) | `IVF{nlist},PQ{d/2}x4fs`, nlist ∈ {512, 1204 [sic, as published], 2048, 4096} | k_reorder ∈ {0, 10, 100, 1000}, nprobe per published file | as published |
| **faiss-ivfpq** (added, because the brief names IVF-PQ and ann-benchmarks has no plain IVFPQ entry) | `IndexIVFPQ`, nlist ∈ {1024, 4096, 16384}, M_pq = largest divisor of d ≤ d/4 (SIFT 32, GloVe 25, MNIST/Fashion 196, NYT 64), nbits 8 | nprobe ∈ {1, 5, 10, 20, 50, 100, 200} | 21 |
| ScaNN | published (num_leaves, threshold, dims_per_block) | published [leaves_to_search, reorder] pairs | as published |

**Fly methods** are new harness modules written for this experiment and frozen in `src/flyret/ann/`. Each has a tuning budget of **≤ 81 configurations**, hnswlib's budget, so no fly method is tuned more than the strongest baseline.

- **FlyHash-index (Dasgupta 2017 construction):**
  - Sparse binary random projection with m ∈ {10d, 20d} and each KC sampling ⌈0.1·d⌉ inputs.
  - Top-k WTA with k ∈ {16, 32, 64}.
  - Inverted list per KC. A query gathers candidates from its k active KCs' lists, ranks them by overlap, and re-ranks the top C by exact distance, with C ∈ {10, 20, 50, 100, 200, 500, 1000, 2000, 5000}.
  - Total configs: 2 × 3 × 9 = 54.
- **DenseFly (Sharma & Navlakha 2018):**
  - The same projection, binarised by sign (threshold 0) instead of WTA, as in the verified DenseFly description.
  - Candidate generation by its pseudo-hash buckets with multiprobe, then the same exact re-rank with C as above.
  - Configs: m ∈ {10d, 20d} × pseudo-hash length ∈ {16, 32} × C (9) = 36.
- **ConnectomeHash:** the best-scoring matrix from B1 (BIO or a null, whichever wins on the B1 odour primary).
  - Applied after PCA to 51 dimensions fitted on train, with k = round(0.05·m).
  - Same inverted index and C sweep (9 configs).
  - Its d = 51 bottleneck is stated as a design limit of any connectome-wired hash on these datasets.

**Additional costs recorded per method, beyond the harness:**

- Encoding cost per item: the projection's multiply-adds and the measured ns per item, single thread.
- Insertion: whether the index supports it, and the time per item for 10,000 inserts after the build.
- Deletion: whether the method supports it (hnswlib `mark_deleted`; FAISS IVF `remove_ids`, verified on IVFPQ; fly inverted lists support deletion).

**Readout (predeclared):**

- For each dataset, interpolate every method's Pareto front and report QPS at recall@10 ∈ {0.5, 0.8, 0.9, 0.95}.
- **"Inside the frontier"** means that at every recall ≥ 0.8 reached by both a fly method and a baseline, the best fly QPS is below the best baseline QPS.
- **"Competitive"** means any recall level ≥ 0.8 at which a fly method's QPS is ≥ the best baseline's.
- **"Not reached"** means the fly method never reaches that recall within its budget. That is a reportable outcome in its own right.
- The expected result, stated in advance: inside the frontier on every dataset. B2 is run because the comparison is missing from the literature, and a documented negative is a contribution.

## 6. Track C: the skewed-distribution hypothesis (speculative; the experiment author's hypothesis)

**Labelled throughout as the hypothesis of the experiment's author, not a finding from the literature.**

**Frozen definition:** `configs/trackC_skew_definition.md` (SHA-256 below). It was written and hashed before any Track C or B1 retrieval measurement. The ranking it produces is computed from connectome statistics alone and also frozen: `configs/trackC_ranking.json` (SHA-256 below, produced by `scripts/rank_trackC.py`).

- `configs/trackC_skew_definition.md` SHA-256 `509fa96a73e884fc865cdb7dfde2f3e3bf121789286d14e9ca7f150996b3e065`
- `configs/trackC_ranking.json` SHA-256 `7d27d29bdb3502ef87f14032d474295997886c84c4c777d450db6d0fd8785e36`
- `src/flyret/skew.py` SHA-256 `9270911699f47f0d426afaa4d5250d8cfbf0b555085a731784e1e63a5756f0cf`

**The definition in brief:**

1. Per-glomerulus co-convergence is Q_g = Σ_{l≠g} (MMᵀ)²_{gl}, z-scored against 1,000 N1 nulls.
2. The matched order is glomeruli by z, descending. The mismatched order is its reverse.
3. Glomerulus sampling weights are p_g ∝ r_g^(−β), with β ∈ {0, 0.5, 1, 1.5, 2}.
4. Each item has 3–10 active glomeruli with LogNormal(0, 1) amplitudes, normalised to unit mean.
5. Each trial has 10,000 database items and 1,000 queries, with ground truth the top 2% by Euclidean distance and the metric AP@200. There are 20 trials.
6. Matrices are w ≥ 5, both hemispheres. Each hemisphere uses its own ranking.
7. Nulls are N0–N3 (N2 = N1 on binary), with 20 null draws per level per trial; seeds are 740000 + 100·trial + draw.

**The frozen ranking.** It was computed 2026-10-23 from the w ≥ 5 matrices only, with 1,000 N1 nulls per hemisphere.

| Hemisphere | global Q z | matched top 10 (most overconverged first) | matched bottom 5 | overlap with Zheng 2022 core community (descriptive only) |
|---|---|---|---|---|
| L | 8.40 | DM4, DM1, DL2v, DM5, DM6, DM2, VM3, VA4, VA7l, VM2 | VM4, DA4l, VA6, VL2a, VL2p | 7 / 10 |
| R | 6.05 | DC3, DL2v, VM5d, D, DL2d, VC1, VA4, VA1d, DM4, VC4 | DL3, VL1, DA2, VL2p, VM6 | 3 / 10 |

The L/R Spearman agreement of per-glomerulus z is **0.46**. The two hemispheres' overconvergence orders therefore agree only moderately. The right hemisphere matches Zheng's core community (from the hemibrain, which is a right hemisphere) less well than the left does. This was measured after the definition was frozen and is reported, not acted on.

- It means Track C tests two partly different matched distributions.
- A crossover in one hemisphere only is labelled "weakly supported", as the decision rules already require.
- The global co-convergence departs strongly from N1 in both hemispheres, in line with Senge's report that Q departs from its null in 6 of 7 hemispheres.

**Predicted signature: a crossover.** Write Δ_ℓ(β, order) = AP(BIO) / mean AP(N_ℓ) − 1 for ℓ ∈ {1, 3}. The hypothesis predicts Δ ≤ 0 at β = 0 (nulls win at uniform), Δ > 0 at matched high β, and Δ ≤ 0 at mismatched high β.

**Decision rules (each must hold in both hemispheres to be labelled "demonstrated"; in one only, "weakly supported"):**

- **Crossover supported:**
  - (a) the upper CI bound of Δ_ℓ(β = 0) is < +2.5%;
  - (b) the lower CI bound of Δ_ℓ(matched, β = 2) is > +2.5%;
  - (c) the lower CI bound of the interaction Δ_ℓ(matched, 2) − Δ_ℓ(mismatched, 2) is > 0, and the upper CI bound of Δ_ℓ(mismatched, 2) is < +2.5%;
  - all for both ℓ = 1 and ℓ = 3.
- **Contradicted under these conditions:** the upper CI bound of Δ_ℓ(matched, β) is < +2.5% for β ∈ {1.5, 2}, for both ℓ, in both hemispheres.
- **Otherwise inconclusive.** The full Δ(β) curves are reported in every case.
- **Holm family:** 2 hemispheres × 2 levels for (b).

**Interpretation limit, stated in the write-up whatever the outcome.** Even a clean crossover would show only that the wiring structure can be exploited under a matched distribution. That is a scientific result about the fly's adaptation, not useful engineering, because a learned projection (BioHash's approach) could probably capture the same structure more cheaply. **Fitted-to-nothing claim:** this may be asserted only because the definition hash in this document predates every Track C number. The analysis script checks the hash and refuses to run if it does not match.

## 7. Metrics reported for every method in every track (brief section 4)

| Metric | A | B1 | B2 | C |
|---|---|---|---|---|
| recall@k / AP or mAP at the predeclared k | Spearman ρ with true novelty (primary), plus AUROC/AUPRC; retrieval recall does not apply to a membership filter | AP@n, recall@n, 2017 mAP | recall@10 | AP@200, recall@200 |
| QPS at matched recall, and the full curve | queries per second of the novelty test | brute-force tag-scan QPS (descriptive; not a frontier) | full recall-QPS Pareto curve | brute-force tag-scan QPS (descriptive) |
| index construction time and cost | yes | yes (tag build) | harness build time | yes |
| index memory footprint | the matched budget itself, plus measured bytes | bits per stored tag | harness index size | bits per stored tag |
| encoding cost per item | multiply-adds and ns per item, including the projection | multiply-adds and ns | multiply-adds and ns | multiply-adds and ns |
| update cost (insert time; deletion support) | yes | insert = one tag; deletion trivial | yes | as B1 |
| false positive / false negative rates at matched memory | yes | — | — | — |

Hardware, precision, batch size, thread count and dataset version (section 2) are written into every result file header.

## 8. Analysis code and stopping rules

- Analysis scripts are written and hashed before their track's first measurement. They regenerate every reported number from `raw_results/`.
- A run that fails (non-finite values, a crash, a harness timeout) is recorded as failed and never dropped silently.
- Test sets are evaluated once.
- No track's design changes after any of its numbers exist, except by a logged amendment that states which numbers had been seen.

## 9. Honesty requirements carried into every report

- Every conclusion carries one of the five labels.
- Absence of evidence is kept distinct from evidence of no benefit.
- Senge 2026 is marked as a single-author unreviewed preprint wherever it is relied on, and B1's report states whether the replication agreed.
- Track C is marked as the experiment author's speculative hypothesis.
- No fly method is compared against a weak baseline and reported as a win. Every Track A and B2 comparison is at matched memory or matched tuning budget, and includes encoding cost.
- A negative result is written up as a result.

## 10. The open direction, noted and not attempted

Meaning 2, choosing which observation, document or tool to inspect next under a budget, has no fly-derived work. That is a clean absence of evidence. The mechanism it would need is a novelty or familiarity score that prioritises gathering. The mushroom body output neurons implicated in familiarity (for instance MBON-α′3) compute something like such a score. Whether the connection is more than an analogy is **unknown**. EXP3 does not move it.

## 11. Decisions the reviewer should confirm or change at sign-off

Each item has a default. **The default applies unless the reviewer changes it.**

1. **N2 collapse (B1, C).** On the binary glomerulus × KC matrix, N2 equals N1 by construction (section 5).
   - Default: report N2 as "= N1" on binary arms, and sample it as a distinct ensemble only on the synapse-weighted arm.
   - Alternative: rebuild every matrix at PN level, so that sister PNs count as separate claws. N2 would then preserve each KC's number of distinct glomeruli under PN-level rewiring. This departs from Senge's representation.
2. **Threshold.** The default is w ≥ 5 primary (the brief: the LC10a discipline; also Li et al. 2020's convention), with w ≥ 1 as the Senge-fidelity arm. A "replicates Senge" verdict requires both.
3. **B1 scope.** The default is MaleCNS only (2 of Senge's 7 hemispheres). Adding hemibrain v1.2, FlyWire v783 and BANC v888 would need new downloads and the same extraction rule.
4. **DoOR preprocessing fidelity.** Our first pass at Senge's stated filter (≥ 40 odorants per glomerulus, ≥ 12 measured glomeruli per odorant) gives 37 glomeruli, 178 odorants and 33.8% missing. Senge reports 35 glomeruli, 172 odorants and 28.7% missing. The gap comes from receptor-to-glomerulus mapping with duplicated glomeruli (VC3, DM3, DM5 each have two DoOR columns).
   - Default: re-implement his mapping from the flypath code text (reading only, no execution). It must reproduce 35 / 172 / 28.7% before any odour measurement. If it cannot, our numbers are used and the deviation is logged as an amendment.
5. **Primate faces dataset (Track A).** No public source was found. The default is one more targeted search after sign-off. If it is still unavailable, the face dataset is ABANDONED with a handoff note, and Track A's "≥ 4 datasets" criterion is evaluated over the datasets actually run. That count is stated in the report.
6. **Text corpus (Track A).** The default is `nytimes-256-angular` (CC BY 4.0; TF-IDF + random projection, already downloaded). The alternative is VIBE `yahoo-minilm-384-normalized`, a neural open-model embedding whose source-text licence is unverified. Choose one, or both.
7. **Track A near-duplicate augmentation and τ.** The defaults are noise of 0.25 × and a familiarity threshold of 0.5 × the median within-S nearest-neighbour distance. These numbers are our choice; the 2018 paper has no threshold. τ affects only the binary metrics (AUROC, FPR, FNR). The noise level also enters the primary all-queries ρ, through which near-duplicates are queried. The held-out-only ρ, which is the 2018 protocol, depends on neither.
8. **Track A MinHash on dense vectors.** The default is weighted MinHash (ICWS) on [x⁺, x⁻]. Splitting a signed vector this way is our design inference, not something taken from a source. MinHash on raw shingles would need raw text, which neither candidate corpus provides.
9. **Track C item generator.** The defaults are 3–10 active glomeruli, LogNormal(0, 1) amplitudes and β ∈ {0, …, 2}. These are frozen in the hashed definition. Changing any of them requires re-hashing before any Track C number exists. The connectome-derived ranking itself does not change.
10. **B2 compute.** The full ANN-Benchmarks runs (1M-point SIFT and GloVe, 81-config hnswlib, ScaNN, 5 datasets, single CPU) are estimated at several days of wall-clock on this machine.
    - Default: run all five datasets.
    - Fallback, if the reviewer prefers: SIFT, GloVe and Fashion-MNIST first, with the remainder as a logged amendment.

**Decisions taken at sign-off:**
- Items 1–9: defaults accepted, with these additions:
  - item 1: no PN-level rebuild, plus the NQ rung (A1);
  - item 4: both filters (A2);
  - item 6: both corpora (A3).
- Item 10: default **rejected**; B2 is reduced and gated (A4).

## 12. Sign-off

- [x] Signed 2026-10-23 (`../SIGNOFF_EXP3_signed.md`). Amendments requested: A1–A4, plus reporting obligations A5. All are logged in `docs/exp3_amendments.md` before taking effect.
