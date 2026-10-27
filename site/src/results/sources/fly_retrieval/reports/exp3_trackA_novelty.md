# EXP3 Track A: distance-sensitive novelty detection against production baselines

**What this track is.** The 2018 fly Bloom filter (FBF; Dasgupta, Sheehan, Stevens & Navlakha, PNAS 115:13093) is the best fly-derived result in this literature. It had been compared only with a traditional Bloom filter and a locality-sensitive Bloom filter (LSBF). This track compares it, at matched memory, with the methods production systems use for near-duplicate and novelty detection: a SimHash fingerprint store, weighted MinHash with banded LSH, and a count-min sketch over LSH band keys. Encoding cost is included. Design: `docs/exp3_preregistration.md` section 4, plus amendments A3, A6, A7 and A10. The analysis code was frozen before the first measurement; A7 records the one exception, the cost script.

**Hardware, precision, threads, versions.**
- **Machine and software:** Apple M5 (10 cores, 32 GB), macOS 26.6.2, Python 3.12.13, numpy 2.5.4, scipy 1.18.1, datasketch 2.0.0.
- **Accuracy runs:** multi-threaded BLAS, which does not affect accuracy.
- **Cost runs:** a separate single-thread process (OMP/OPENBLAS/VECLIB = 1), over up to 1,000 stored and 1,000 query items per cell, batch = all items per call. Projections are float32 and data float64.
- **Host load:** an unrelated `pc-printjob-spooler` process held about one core at 99% throughout (A6.10).
- **Data:** dataset versions and SHA-256 are in `data/DATASETS.json`.

**Datasets.**
- **Run (five):**
  - fly odours: Hallem & Carlson 2006, 110 × 24, from DoOR.data @ db323a4;
  - SIFT: 5,000 × 128;
  - MNIST: 5,000 × 784;
  - random exponential: 1,000 × 20;
  - nytimes-256-angular: 5,000 × 256, TF-IDF plus random projection, the primary text corpus.
- **Not run (two):**
  - **Primate face-patch responses (2,000 × 99): ABANDONED.** No public deposit was found (A6). Handoff: the owner may obtain the data from the Tsao lab and run it as a later amendment. Nothing was substituted.
  - **Neural text embeddings: dropped.** The VIBE MiniLM corpus was dropped because the licence of its source texts could not be resolved (A6). **The text result here therefore does not speak to neural-embedding practice**, which is the production setting for near-duplicate detection. nytimes is TF-IDF plus a random projection.
- **Data note:** nytimes contains 25 exact-duplicate rows (4,975 distinct). This is why the exact-match Bloom filter scores slightly above zero there. A first run was invalid because of zero-norm rows (A10) and was discarded.

**Protocol in one paragraph.**
- 10-fold cross-validation. Folds 8–9 are used only to tune each method on its frozen grid; the selected configuration is evaluated once on test folds 0–7.
- Each test fold stores the other seven test folds. It queries its own items plus an equal number of noisy copies of stored items (near-duplicates).
- Ground truth is the continuous novelty f(x, S) = min distance to the stored set.
- The primary metric is Spearman ρ between predicted and true novelty. The held-out-only ρ (the 2018 protocol) and Pearson are also reported.
- Memory is matched at B ∈ {3, 10, 30, 100} bits per stored item; 10 and 30 are the 2018 paper's budgets.
- The bootstrap uses 10,000 resamples, two-stage (folds, then queries), and is paired across methods.

## Result

The predeclared verdict is **MIXED**. FBF neither "holds up" (lower CI > 0 at ≥ 3 of 4 budgets on ≥ 4 datasets, including text) nor "does not survive" (upper CI < 0 at ≥ 3 of 4 budgets on ≥ 4 datasets). The pattern behind the mixed verdict is consistent and simple: **the memory budget decides it.**

- **At 3 and 10 bits per item, FBF beats every production baseline at matched memory, with the CI excluding zero.** This holds on SIFT, MNIST, random exponential and nytimes (8 of 8 cells). It also holds for random exponential at 30 bits.
  - In these cells the best production baseline was MinHash (the SimHash store at 10 bits on MNIST). A 3- or 10-bit SimHash fingerprint is too short to separate items: at 3 bits every query matches some stored fingerprint.
  - On odours (n = 110) no cell is significant either way; it is underpowered.
- **At 30 and 100 bits per item, the SimHash fingerprint store beats FBF.** This holds on SIFT, MNIST and nytimes at both budgets, and on random exponential at 100 bits, all with the CI excluding zero. 30 bits per item is the 2018 paper's own budget (m = 30n).
- **The held-out-only (2018-protocol) comparison is more favourable to FBF.** Without near-duplicate queries, FBF's ρ on SIFT at 30 bits is 0.725 against 0.515 for the SimHash store. FBF grades how novel far-away items are better than SimHash does. SimHash separates near-duplicates from novel items far better, and that is the production use case. These held-out differences are descriptive point estimates; they are not a preregistered test.

**The FBF's lead comes at a large encoding cost.**
- **Projection arithmetic.** In every cell FBF wins, its projection costs ≥ 8× the multiply-adds per item of the winning baseline: 8.3–352.7×, and ≥ 15× in 7 of the 9.
- **Scaling with the stored set.** The FBF's expansion is m = B·n cells, so its encoding cost per item grows linearly with the number of stored items, at fixed bits per item. At n = 3,500 and 10 bits per item, FBF projects to 35,000 KCs. SimHash, LSBF and CMS cost the same per item regardless of n.
- **Measured time, single thread.** FBF took 22–807 µs to encode one item in the winning cells. MinHash took 106–794 µs in the same cells, slow here only because datasketch's ICWS runs in Python per item. SimHash and LSBF bits took 6 ns–2.5 µs across all cells.
- **Label rule.** Under the predeclared label rule, each FBF win is therefore an **"accuracy win at matched memory, at higher encoding cost"**.

**Reproduction anchor (2018, SIFT, 30 bits per item, held-out queries).** The order FBF > LSBF > Bloom filter is reproduced: Spearman 0.725 / 0.442 / 0.000, Pearson 0.646 / 0.485 / 0.000. The 2018 paper reports correlations of 0.535 / 0.345 / 0.002; the corrected source audit confirms these are correlations, not AUCs. Our absolute values are higher. The 2018 SI, with its distance measure and LSBF parameters, could not be accessed, so its exact configuration is not reproduced. The ordering is.

**Biology-removed control (GBF: a dense Gaussian projection with the same WTA and filter).** FBF beats GBF in 15 of 20 cells, and GBF never beats FBF significantly. **This control is confounded and should not be read as "the fly's sparse binary wiring is better".** Both methods use the 2017 preprocessing, which shifts every feature to be non-negative and rescales each vector to mean 100. A dense Gaussian projection of such inputs is dominated by a common-mode term, so the same few KCs win for every input; GBF's ρ on nytimes is ≤ 0.054. Whether a centred dense projection would close the gap is **plausible but untested** here.

**False positives and negatives at matched memory** (familiar = within τ = 0.5 × the median within-set nearest-neighbour distance; threshold chosen on validation; full table below).
- At the validation-chosen threshold, most methods sit at a degenerate operating point. For example, the 3-bit SimHash store and the exact Bloom filter call everything novel (FPR 0, FNR 1).
- At a strict FPR of 1%, **every method at ≤ 10 bits per item misses ≥ 84% of familiar items** (FNR ≥ 0.84 in all 70 such method-cells). No method is a usable near-duplicate detector in the regime where FBF leads.
- Usable operating points appear only at 30–100 bits per item, and mostly for the SimHash store. At 100 bits its FNR is 0.009 on nytimes, 0.106 on random, 0.108 on MNIST and 0.281 on SIFT.
- FBF's best is 0.244 on random at 100 bits, then 0.535 on nytimes at 100 bits.

**Update cost and deletion.** Every method supports insertion. Insert cost per item is in the table.
- **No deletion:** FBF and every Bloom-type structure (FBF, GBF, LSBF, BF, banded MinHash), because a zeroed or set cell cannot be attributed to one item.
- **Deletion:** the count-min sketch supports it by decrement, exact unless a counter saturated; saturation events are recorded per cell in the raw JSON. A fingerprint store supports it by removing the fingerprint. The method as implemented here does not expose deletion, but the structure trivially permits it.

## Labels

- **FBF beats production baselines at ≤ 10 bits per item, at matched memory: weakly supported.** The pattern is consistent on 4 of 5 datasets (8 of 8 cells there) but rests on our re-specified versions of the 2018 details, on a TF-IDF text corpus only, and at ≥ 8× higher projection arithmetic. It holds in a regime where no method makes a usable near-duplicate detector at a 1% false-positive rate. It is a narrow niche and not a general win.
- **FBF beats production baselines at 30–100 bits per item (including the 2018 budget): contradicted under specified conditions.** Specifically, it fails on Spearman with true novelty over held-out plus near-duplicate queries, on SIFT, MNIST and nytimes. Under the held-out-only 2018 protocol it is undecided, with descriptive point estimates favouring FBF on SIFT.
- **FBF's advantage over LSBF and the Bloom filter (2018's own comparison): demonstrated** (reproduced ordering) on SIFT at 30 bits for held-out queries. With near-duplicate queries included, LSBF's ρ exceeds FBF's on SIFT at 30 and 100 bits (point estimates 0.553 vs 0.500 and 0.698 vs 0.555).
- **Neural-embedding near-duplicate practice: unknown.** It was not tested; an absence of evidence, not a negative.
- **Face-patch dataset: unknown** (abandoned; handed off).
- **The predeclared overall outcome is MIXED.** The branch neither closes as "does not survive" nor yields the narrow publishable win in the form the preregistration defined (≥ 3 of 4 budgets). What it yields is a budget-limited advantage at very low memory per item.

<!-- BEGIN GENERATED (scripts/trackA_analyze.py) -->

**Predeclared verdict: MIXED.** Budgets (of 4) where Δ's lower CI > 0, per dataset: odors 0, sift 2, mnist 2, random 3, nytimes 2. Budgets where Δ's upper CI < 0: odors 0, sift 2, mnist 2, random 1, nytimes 2.

**Reproduction anchor (SIFT, B = 30, held-out queries only):** Spearman FBF 0.725, LSBF 0.442, BF 0.000; Pearson FBF 0.646, LSBF 0.485, BF 0.000 (2018: 0.535 / 0.345 / 0.002). Order FBF > LSBF > BF reproduced: **yes**.

### Δ = ρ(FBF) − ρ(best production baseline, chosen on validation), all test queries

| dataset | B (bits/item) | best production | ρ FBF [95% CI] | ρ baseline [95% CI] | Δ [95% CI] | FBF − GBF [95% CI] |
|---|---|---|---|---|---|---|
| odors | 3 | MinHash | 0.264 [0.025, 0.463] | 0.159 [-0.092, 0.384] | +0.105 [-0.207, +0.414] | -0.049 [-0.321, +0.263] |
| odors | 10 | SimHash | 0.251 [0.007, 0.463] | 0.231 [-0.020, 0.449] | +0.021 [-0.277, +0.310] | -0.052 [-0.327, +0.228] |
| odors | 30 | SimHash | 0.414 [0.167, 0.604] | 0.607 [0.382, 0.752] | -0.192 [-0.423, +0.044] | +0.178 [-0.092, +0.449] |
| odors | 100 | SimHash | 0.581 [0.373, 0.718] | 0.754 [0.588, 0.840] | -0.172 [-0.364, +0.016] | +0.126 [-0.092, +0.352] |
| sift | 3 | MinHash | 0.342 [0.305, 0.377] | 0.148 [0.110, 0.185] | +0.194 [+0.143, +0.244] | +0.190 [+0.142, +0.235] |
| sift | 10 | MinHash | 0.431 [0.395, 0.466] | 0.254 [0.222, 0.286] | +0.177 [+0.133, +0.221] | +0.206 [+0.160, +0.253] |
| sift | 30 | SimHash | 0.500 [0.471, 0.527] | 0.597 [0.573, 0.619] | -0.097 [-0.128, -0.068] | +0.211 [+0.168, +0.254] |
| sift | 100 | SimHash | 0.555 [0.526, 0.581] | 0.852 [0.840, 0.862] | -0.297 [-0.324, -0.270] | +0.226 [+0.192, +0.258] |
| mnist | 3 | MinHash | 0.177 [0.142, 0.212] | -0.006 [-0.039, 0.025] | +0.184 [+0.136, +0.232] | +0.026 [-0.017, +0.067] |
| mnist | 10 | SimHash | 0.287 [0.245, 0.329] | 0.061 [0.012, 0.109] | +0.226 [+0.163, +0.291] | +0.100 [+0.057, +0.145] |
| mnist | 30 | SimHash | 0.328 [0.296, 0.358] | 0.644 [0.621, 0.665] | -0.316 [-0.352, -0.280] | +0.089 [+0.053, +0.124] |
| mnist | 100 | SimHash | 0.383 [0.351, 0.414] | 0.823 [0.812, 0.833] | -0.440 [-0.472, -0.408] | +0.091 [+0.049, +0.133] |
| random | 3 | MinHash | 0.393 [0.325, 0.456] | 0.159 [0.085, 0.232] | +0.235 [+0.134, +0.330] | +0.196 [+0.091, +0.299] |
| random | 10 | MinHash | 0.646 [0.602, 0.682] | 0.343 [0.271, 0.408] | +0.304 [+0.231, +0.377] | +0.445 [+0.356, +0.530] |
| random | 30 | SimHash | 0.744 [0.712, 0.769] | 0.688 [0.641, 0.725] | +0.056 [+0.007, +0.104] | +0.417 [+0.334, +0.498] |
| random | 100 | SimHash | 0.765 [0.740, 0.782] | 0.800 [0.772, 0.820] | -0.036 [-0.065, -0.006] | +0.368 [+0.295, +0.441] |
| nytimes | 3 | MinHash | 0.257 [0.221, 0.293] | 0.124 [0.091, 0.156] | +0.133 [+0.089, +0.180] | +0.236 [+0.187, +0.285] |
| nytimes | 10 | MinHash | 0.440 [0.411, 0.468] | 0.210 [0.170, 0.251] | +0.230 [+0.178, +0.279] | +0.402 [+0.352, +0.451] |
| nytimes | 30 | SimHash | 0.617 [0.594, 0.638] | 0.668 [0.645, 0.690] | -0.051 [-0.085, -0.017] | +0.563 [+0.523, +0.603] |
| nytimes | 100 | SimHash | 0.743 [0.730, 0.754] | 0.812 [0.803, 0.820] | -0.069 [-0.084, -0.055] | +0.706 [+0.666, +0.747] |

### Every method, every cell (test; ρ = Spearman with true novelty over all queries)

| dataset | B | method | selected config | ρ | ρ held-out | Pearson held-out | AUROC | AUPRC | FPR @val-thr | FNR @val-thr | FNR @FPR 1% | bits used | encode madds/item | encode ns/item | insert ns/item | query ns/item |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| odors | 3 | FBF | {"k": 10, "s": 6} | 0.264 | 0.217 | 0.309 | 0.604 | 0.690 | 0.609 | 0.188 | 1.000 | 231 | 1,386 | 5976 | 93 | 160 |
| odors | 3 | GBF | {"k": 5} | 0.314 | 0.293 | 0.341 | 0.608 | 0.691 | 0.750 | 0.036 | 1.000 | 231 | 5,544 | 5328 | 76 | 164 |
| odors | 3 | LSBF | {"L": 4, "r": 12} | 0.372 | 0.343 | 0.361 | 0.674 | 0.732 | 0.359 | 0.366 | 1.000 | 228 | 1,152 | 37 | 903 | 24 |
| odors | 3 | BF | {} | 0.018 | 0.105 | 0.104 | 0.542 | 0.659 | 0.000 | 1.000 | 1.000 | 231 | 0 | 0 | 805 | 1028 |
| odors | 3 | SimHash | {"b": 3} | 0.000 | 0.000 | 0.000 | 0.500 | 0.636 | 0.000 | 1.000 | 1.000 | 231 | 72 | 21 | 129 | 95 |
| odors | 3 | MinHash | {"b": 8, "r": 2} | 0.159 | 0.013 | 0.026 | 0.617 | 0.696 | 0.594 | 0.188 | 1.000 | 224 | 384 | 2140216 | 5081 | 1 |
| odors | 3 | CMS | {"D": 2, "b": 4, "r": 8} | 0.000 | 0.000 | 0.000 | 0.500 | 0.636 | 0.000 | 1.000 | 1.000 | 224 | 768 | 52 | 2319 | 0 |
| odors | 10 | FBF | {"k": 10, "s": 3} | 0.251 | 0.133 | 0.266 | 0.648 | 0.719 | 0.406 | 0.348 | 1.000 | 770 | 2,310 | 14299 | 95 | 177 |
| odors | 10 | GBF | {"k": 20} | 0.304 | 0.367 | 0.353 | 0.638 | 0.708 | 0.609 | 0.134 | 1.000 | 770 | 18,480 | 9214 | 91 | 186 |
| odors | 10 | LSBF | {"L": 8, "r": 16} | 0.423 | 0.348 | 0.311 | 0.771 | 0.821 | 0.531 | 0.125 | 0.902 | 768 | 3,072 | 74 | 1777 | 0 |
| odors | 10 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.636 | 0.000 | 1.000 | 1.000 | 770 | 0 | 0 | 1085 | 1506 |
| odors | 10 | SimHash | {"b": 10} | 0.231 | 0.451 | 0.537 | 0.628 | 0.702 | 0.531 | 0.268 | 1.000 | 770 | 240 | 26 | 128 | 780 |
| odors | 10 | MinHash | {"b": 16, "r": 8} | 0.456 | 0.092 | 0.154 | 0.711 | 0.782 | 0.266 | 0.375 | 0.839 | 768 | 3,072 | 584174 | 30880 | 441 |
| odors | 10 | CMS | {"D": 2, "b": 4, "r": 8} | 0.171 | 0.096 | 0.155 | 0.542 | 0.657 | 0.906 | 0.009 | 1.000 | 768 | 768 | 36 | 2207 | 0 |
| odors | 30 | FBF | {"k": 10, "s": 6} | 0.414 | 0.213 | 0.237 | 0.708 | 0.764 | 0.391 | 0.348 | 1.000 | 2,310 | 13,860 | 32497 | 108 | 200 |
| odors | 30 | GBF | {"k": 5} | 0.236 | 0.279 | 0.348 | 0.582 | 0.677 | 0.703 | 0.152 | 1.000 | 2,310 | 55,440 | 24095 | 97 | 193 |
| odors | 30 | LSBF | {"L": 32, "r": 16} | 0.672 | 0.502 | 0.502 | 0.890 | 0.910 | 0.141 | 0.232 | 0.929 | 2,304 | 12,288 | 232 | 6940 | 447 |
| odors | 30 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.636 | 0.000 | 1.000 | 1.000 | 2,310 | 0 | 0 | 1733 | 3015 |
| odors | 30 | SimHash | {"b": 30} | 0.607 | 0.621 | 0.651 | 0.854 | 0.869 | 0.547 | 0.027 | 1.000 | 2,310 | 720 | 34 | 139 | 947 |
| odors | 30 | MinHash | {"b": 32, "r": 4} | 0.510 | 0.336 | 0.366 | 0.803 | 0.833 | 0.141 | 0.518 | 1.000 | 2,304 | 3,072 | 601038 | 34686 | 475 |
| odors | 30 | CMS | {"D": 4, "b": 4, "r": 8} | 0.309 | 0.384 | 0.420 | 0.667 | 0.728 | 0.500 | 0.170 | 1.000 | 2,304 | 768 | 33 | 3524 | 0 |
| odors | 100 | FBF | {"k": 10, "s": 6} | 0.581 | 0.389 | 0.436 | 0.842 | 0.854 | 0.188 | 0.312 | 1.000 | 7,700 | 46,200 | 93252 | 127 | 269 |
| odors | 100 | GBF | {"k": 30} | 0.455 | 0.439 | 0.499 | 0.753 | 0.782 | 0.250 | 0.455 | 1.000 | 7,700 | 184,800 | 44206 | 140 | 283 |
| odors | 100 | LSBF | {"L": 16, "r": 24} | 0.609 | 0.267 | 0.223 | 0.891 | 0.925 | 0.000 | 0.554 | 0.554 | 7,696 | 9,216 | 193 | 3435 | 218 |
| odors | 100 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.636 | 0.000 | 1.000 | 1.000 | 7,700 | 0 | 0 | 3845 | 7640 |
| odors | 100 | SimHash | {"b": 100} | 0.754 | 0.653 | 0.713 | 0.945 | 0.961 | 0.156 | 0.071 | 0.500 | 7,700 | 2,400 | 70 | 148 | 1574 |
| odors | 100 | MinHash | {"b": 16, "r": 8} | 0.639 | 0.252 | 0.270 | 0.825 | 0.886 | 0.312 | 0.196 | 0.705 | 7,696 | 3,072 | 590717 | 32089 | 0 |
| odors | 100 | CMS | {"D": 4, "b": 4, "r": 8} | 0.449 | 0.490 | 0.520 | 0.779 | 0.806 | 0.188 | 0.438 | 1.000 | 7,680 | 768 | 33 | 3576 | 102 |
| sift | 3 | FBF | {"k": 20, "s": 6} | 0.342 | 0.459 | 0.427 | 0.604 | 0.566 | 0.683 | 0.118 | 1.000 | 10,500 | 63,000 | 114922 | 28 | 40 |
| sift | 3 | GBF | {"k": 10} | 0.152 | 0.211 | 0.213 | 0.531 | 0.523 | 0.868 | 0.070 | 1.000 | 10,500 | 1,344,000 | 98497 | 21 | 28 |
| sift | 3 | LSBF | {"L": 4, "r": 16} | 0.218 | 0.268 | 0.259 | 0.590 | 0.560 | 0.393 | 0.463 | 1.000 | 10,500 | 8,192 | 57 | 142 | 73 |
| sift | 3 | BF | {} | -0.000 | 0.016 | 0.013 | 0.500 | 0.507 | 0.000 | 1.000 | 1.000 | 10,500 | 0 | 0 | 897 | 849 |
| sift | 3 | SimHash | {"b": 3} | 0.000 | 0.000 | 0.000 | 0.500 | 0.507 | 0.000 | 1.000 | 1.000 | 10,500 | 384 | 18 | 15 | 1282 |
| sift | 3 | MinHash | {"b": 4, "r": 8} | 0.148 | 0.133 | 0.132 | 0.567 | 0.548 | 0.318 | 0.579 | 1.000 | 10,500 | 4,096 | 156193 | 786 | 191 |
| sift | 3 | CMS | {"D": 4, "b": 4, "r": 8} | 0.009 | 0.025 | 0.027 | 0.500 | 0.507 | 0.998 | 0.002 | 1.000 | 10,496 | 4,096 | 32 | 383 | 112 |
| sift | 10 | FBF | {"k": 50, "s": 13} | 0.431 | 0.655 | 0.579 | 0.657 | 0.604 | 0.435 | 0.316 | 1.000 | 35,000 | 455,000 | 358909 | 52 | 68 |
| sift | 10 | GBF | {"k": 30} | 0.224 | 0.327 | 0.322 | 0.564 | 0.542 | 0.708 | 0.173 | 1.000 | 35,000 | 4,480,000 | 319699 | 49 | 65 |
| sift | 10 | LSBF | {"L": 8, "r": 20} | 0.369 | 0.302 | 0.317 | 0.690 | 0.651 | 0.325 | 0.387 | 1.000 | 35,000 | 20,480 | 124 | 293 | 172 |
| sift | 10 | BF | {} | -0.006 | -0.015 | -0.013 | 0.500 | 0.507 | 0.000 | 1.000 | 0.992 | 35,000 | 0 | 0 | 920 | 870 |
| sift | 10 | SimHash | {"b": 10} | 0.076 | 0.083 | 0.077 | 0.512 | 0.513 | 0.941 | 0.035 | 1.000 | 35,000 | 1,280 | 20 | 22 | 9460 |
| sift | 10 | MinHash | {"b": 4, "r": 8} | 0.254 | 0.237 | 0.254 | 0.624 | 0.595 | 0.557 | 0.266 | 1.000 | 35,000 | 4,096 | 156191 | 810 | 187 |
| sift | 10 | CMS | {"D": 2, "b": 8, "r": 8} | 0.074 | 0.098 | 0.098 | 0.507 | 0.510 | 0.973 | 0.013 | 1.000 | 34,992 | 8,192 | 57 | 535 | 161 |
| sift | 30 | FBF | {"k": 40, "s": 6} | 0.500 | 0.725 | 0.646 | 0.704 | 0.639 | 0.573 | 0.092 | 1.000 | 105,000 | 630,000 | 1082635 | 83 | 107 |
| sift | 30 | GBF | {"k": 50} | 0.289 | 0.419 | 0.399 | 0.604 | 0.568 | 0.488 | 0.345 | 1.000 | 105,000 | 13,440,000 | 977814 | 80 | 92 |
| sift | 30 | LSBF | {"L": 16, "r": 20} | 0.553 | 0.442 | 0.485 | 0.791 | 0.754 | 0.243 | 0.324 | 0.941 | 104,992 | 40,960 | 265 | 588 | 342 |
| sift | 30 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.507 | 0.000 | 1.000 | 1.000 | 105,000 | 0 | 0 | 1011 | 946 |
| sift | 30 | SimHash | {"b": 30} | 0.597 | 0.515 | 0.523 | 0.815 | 0.772 | 0.369 | 0.156 | 1.000 | 105,000 | 3,840 | 32 | 27 | 12186 |
| sift | 30 | MinHash | {"b": 8, "r": 8} | 0.367 | 0.341 | 0.362 | 0.677 | 0.643 | 0.311 | 0.430 | 0.996 | 105,000 | 8,192 | 305600 | 1570 | 361 |
| sift | 30 | CMS | {"D": 2, "b": 4, "r": 16} | 0.214 | 0.258 | 0.256 | 0.590 | 0.561 | 0.385 | 0.472 | 1.000 | 104,992 | 8,192 | 57 | 325 | 93 |
| sift | 100 | FBF | {"k": 30, "s": 6} | 0.555 | 0.765 | 0.699 | 0.746 | 0.678 | 0.438 | 0.160 | 1.000 | 350,000 | 2,100,000 | 3620522 | 168 | 179 |
| sift | 100 | GBF | {"k": 30} | 0.329 | 0.480 | 0.460 | 0.627 | 0.583 | 0.668 | 0.130 | 1.000 | 350,000 | 44,800,000 | 3105014 | 166 | 185 |
| sift | 100 | LSBF | {"L": 32, "r": 20} | 0.698 | 0.633 | 0.677 | 0.870 | 0.832 | 0.226 | 0.182 | 0.921 | 349,984 | 81,920 | 540 | 1177 | 674 |
| sift | 100 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.507 | 0.000 | 1.000 | 1.000 | 350,000 | 0 | 0 | 1224 | 1238 |
| sift | 100 | SimHash | {"b": 100} | 0.852 | 0.737 | 0.755 | 0.994 | 0.992 | 0.032 | 0.045 | 0.281 | 350,000 | 12,800 | 94 | 35 | 18814 |
| sift | 100 | MinHash | {"b": 32, "r": 8} | 0.492 | 0.453 | 0.484 | 0.741 | 0.703 | 0.329 | 0.303 | 0.960 | 349,984 | 32,768 | 1221472 | 6459 | 1404 |
| sift | 100 | CMS | {"D": 2, "b": 8, "r": 16} | 0.413 | 0.481 | 0.474 | 0.690 | 0.644 | 0.424 | 0.285 | 1.000 | 350,000 | 16,384 | 113 | 914 | 153 |
| mnist | 3 | FBF | {"k": 20, "s": 79} | 0.177 | 0.180 | 0.182 | 0.563 | 0.574 | 0.763 | 0.114 | 1.000 | 10,500 | 829,500 | 238189 | 28 | 40 |
| mnist | 3 | GBF | {"k": 10} | 0.151 | 0.154 | 0.151 | 0.550 | 0.566 | 0.800 | 0.103 | 1.000 | 10,500 | 8,232,000 | 105844 | 21 | 28 |
| mnist | 3 | LSBF | {"L": 4, "r": 16} | 0.192 | 0.123 | 0.152 | 0.619 | 0.612 | 0.320 | 0.494 | 1.000 | 10,500 | 50,176 | 312 | 138 | 71 |
| mnist | 3 | BF | {} | 0.004 | 0.021 | 0.010 | 0.498 | 0.539 | 0.000 | 1.000 | 1.000 | 10,500 | 0 | 0 | 2759 | 2856 |
| mnist | 3 | SimHash | {"b": 3} | 0.000 | 0.000 | 0.000 | 0.500 | 0.540 | 0.000 | 1.000 | 1.000 | 10,500 | 2,352 | 102 | 14 | 1345 |
| mnist | 3 | MinHash | {"b": 16, "r": 8} | -0.006 | 0.049 | 0.058 | 0.498 | 0.539 | 0.867 | 0.137 | 1.000 | 10,496 | 100,352 | 794271 | 3110 | 726 |
| mnist | 3 | CMS | {"D": 2, "b": 4, "r": 8} | -0.001 | 0.030 | 0.027 | 0.500 | 0.540 | 0.998 | 0.003 | 1.000 | 10,496 | 25,088 | 191 | 251 | 80 |
| mnist | 10 | FBF | {"k": 20, "s": 79} | 0.287 | 0.272 | 0.270 | 0.635 | 0.619 | 0.519 | 0.245 | 1.000 | 35,000 | 2,765,000 | 806750 | 39 | 51 |
| mnist | 10 | GBF | {"k": 30} | 0.187 | 0.192 | 0.195 | 0.591 | 0.591 | 0.578 | 0.264 | 1.000 | 35,000 | 27,440,000 | 363631 | 45 | 62 |
| mnist | 10 | LSBF | {"L": 16, "r": 16} | 0.324 | 0.239 | 0.284 | 0.708 | 0.695 | 0.364 | 0.322 | 1.000 | 34,992 | 200,704 | 1055 | 545 | 303 |
| mnist | 10 | BF | {} | -0.001 | -0.027 | -0.027 | 0.500 | 0.540 | 0.007 | 0.993 | 0.993 | 35,000 | 0 | 0 | 2884 | 2872 |
| mnist | 10 | SimHash | {"b": 10} | 0.061 | 0.070 | 0.068 | 0.513 | 0.546 | 0.937 | 0.037 | 1.000 | 35,000 | 7,840 | 127 | 24 | 10068 |
| mnist | 10 | MinHash | {"b": 8, "r": 8} | -0.035 | 0.224 | 0.269 | 0.480 | 0.528 | 0.797 | 0.220 | 1.000 | 35,000 | 50,176 | 399341 | 1577 | 365 |
| mnist | 10 | CMS | {"D": 4, "b": 4, "r": 8} | 0.013 | 0.042 | 0.041 | 0.500 | 0.540 | 0.995 | 0.004 | 1.000 | 34,976 | 25,088 | 180 | 396 | 100 |
| mnist | 30 | FBF | {"k": 20, "s": 79} | 0.328 | 0.340 | 0.327 | 0.666 | 0.642 | 0.617 | 0.130 | 1.000 | 105,000 | 8,295,000 | 2429845 | 66 | 79 |
| mnist | 30 | GBF | {"k": 40} | 0.239 | 0.224 | 0.220 | 0.622 | 0.612 | 0.615 | 0.187 | 1.000 | 105,000 | 82,320,000 | 1110670 | 81 | 106 |
| mnist | 30 | LSBF | {"L": 32, "r": 16} | 0.547 | 0.375 | 0.476 | 0.849 | 0.845 | 0.181 | 0.285 | 0.857 | 104,992 | 401,408 | 2064 | 1111 | 635 |
| mnist | 30 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.540 | 0.000 | 1.000 | 1.000 | 105,000 | 0 | 0 | 2984 | 2970 |
| mnist | 30 | SimHash | {"b": 30} | 0.644 | 0.366 | 0.466 | 0.901 | 0.887 | 0.121 | 0.215 | 0.819 | 105,000 | 23,520 | 173 | 29 | 12252 |
| mnist | 30 | MinHash | {"b": 4, "r": 8} | -0.064 | 0.232 | 0.316 | 0.473 | 0.527 | 0.017 | 0.978 | 1.000 | 105,000 | 25,088 | 203096 | 824 | 160 |
| mnist | 30 | CMS | {"D": 2, "b": 4, "r": 16} | 0.185 | 0.139 | 0.166 | 0.612 | 0.607 | 0.353 | 0.464 | 1.000 | 104,992 | 50,176 | 307 | 330 | 93 |
| mnist | 100 | FBF | {"k": 10, "s": 79} | 0.383 | 0.346 | 0.350 | 0.706 | 0.673 | 0.556 | 0.125 | 1.000 | 350,000 | 27,650,000 | 8022181 | 146 | 152 |
| mnist | 100 | GBF | {"k": 30} | 0.292 | 0.288 | 0.291 | 0.663 | 0.643 | 0.459 | 0.289 | 1.000 | 350,000 | 274,400,000 | 3613507 | 164 | 178 |
| mnist | 100 | LSBF | {"L": 32, "r": 20} | 0.699 | 0.378 | 0.556 | 0.945 | 0.942 | 0.094 | 0.159 | 0.599 | 349,984 | 501,760 | 2501 | 1197 | 730 |
| mnist | 100 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.540 | 0.000 | 1.000 | 1.000 | 350,000 | 0 | 0 | 3250 | 3152 |
| mnist | 100 | SimHash | {"b": 100} | 0.823 | 0.618 | 0.712 | 0.996 | 0.995 | 0.031 | 0.015 | 0.108 | 350,000 | 78,400 | 488 | 37 | 18662 |
| mnist | 100 | MinHash | {"b": 4, "r": 8} | -0.063 | 0.268 | 0.361 | 0.470 | 0.527 | 0.072 | 0.930 | 1.000 | 350,000 | 25,088 | 201571 | 782 | 187 |
| mnist | 100 | CMS | {"D": 4, "b": 4, "r": 16} | 0.393 | 0.284 | 0.362 | 0.746 | 0.731 | 0.473 | 0.179 | 1.000 | 349,984 | 50,176 | 322 | 582 | 117 |
| random | 3 | FBF | {"k": 5, "s": 6} | 0.393 | -0.035 | -0.042 | 0.726 | 0.654 | 0.373 | 0.212 | 1.000 | 2,100 | 12,600 | 22224 | 19 | 36 |
| random | 3 | GBF | {"k": 50} | 0.197 | 0.143 | 0.158 | 0.552 | 0.529 | 0.815 | 0.084 | 1.000 | 2,100 | 42,000 | 22470 | 40 | 67 |
| random | 3 | LSBF | {"L": 4, "r": 12} | 0.228 | 0.048 | 0.044 | 0.622 | 0.577 | 0.378 | 0.414 | 1.000 | 2,100 | 960 | 18 | 167 | 67 |
| random | 3 | BF | {} | 0.018 | -0.055 | -0.053 | 0.511 | 0.507 | 0.223 | 0.754 | 1.000 | 2,100 | 0 | 0 | 595 | 619 |
| random | 3 | SimHash | {"b": 3} | 0.000 | 0.000 | 0.000 | 0.500 | 0.501 | 0.000 | 1.000 | 1.000 | 2,100 | 60 | 6 | 18 | 944 |
| random | 3 | MinHash | {"b": 8, "r": 8} | 0.159 | -0.002 | -0.001 | 0.584 | 0.551 | 0.526 | 0.310 | 1.000 | 2,096 | 1,280 | 293754 | 2164 | 156 |
| random | 3 | CMS | {"D": 2, "b": 4, "r": 8} | 0.005 | -0.006 | -0.006 | 0.501 | 0.502 | 0.000 | 1.000 | 1.000 | 2,096 | 640 | 14 | 329 | 75 |
| random | 10 | FBF | {"k": 5, "s": 6} | 0.646 | 0.035 | 0.033 | 0.906 | 0.871 | 0.122 | 0.211 | 1.000 | 7,000 | 42,000 | 63883 | 20 | 42 |
| random | 10 | GBF | {"k": 50} | 0.202 | 0.115 | 0.154 | 0.582 | 0.547 | 0.623 | 0.229 | 1.000 | 7,000 | 140,000 | 63334 | 42 | 72 |
| random | 10 | LSBF | {"L": 8, "r": 12} | 0.420 | 0.114 | 0.099 | 0.741 | 0.695 | 0.233 | 0.421 | 1.000 | 7,000 | 1,920 | 32 | 319 | 152 |
| random | 10 | BF | {} | -0.013 | -0.001 | 0.005 | 0.499 | 0.501 | 0.000 | 1.000 | 0.996 | 7,000 | 0 | 0 | 643 | 687 |
| random | 10 | SimHash | {"b": 10} | 0.183 | 0.075 | 0.079 | 0.564 | 0.536 | 0.713 | 0.160 | 1.000 | 7,000 | 200 | 8 | 28 | 7050 |
| random | 10 | MinHash | {"b": 8, "r": 8} | 0.343 | 0.055 | 0.062 | 0.694 | 0.655 | 0.289 | 0.425 | 1.000 | 7,000 | 1,280 | 292335 | 2162 | 162 |
| random | 10 | CMS | {"D": 2, "b": 4, "r": 8} | 0.073 | 0.069 | 0.083 | 0.515 | 0.509 | 0.927 | 0.044 | 1.000 | 6,992 | 640 | 18 | 360 | 78 |
| random | 30 | FBF | {"k": 20, "s": 6} | 0.744 | 0.091 | 0.070 | 0.969 | 0.962 | 0.125 | 0.061 | 0.514 | 21,000 | 126,000 | 194310 | 39 | 80 |
| random | 30 | GBF | {"k": 50} | 0.327 | 0.234 | 0.254 | 0.646 | 0.593 | 0.451 | 0.297 | 1.000 | 21,000 | 420,000 | 195070 | 52 | 94 |
| random | 30 | LSBF | {"L": 16, "r": 12} | 0.588 | 0.093 | 0.094 | 0.854 | 0.828 | 0.346 | 0.128 | 0.862 | 20,992 | 3,840 | 64 | 630 | 306 |
| random | 30 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.501 | 0.000 | 1.000 | 1.000 | 21,000 | 0 | 0 | 732 | 867 |
| random | 30 | SimHash | {"b": 30} | 0.688 | 0.061 | 0.056 | 0.928 | 0.911 | 0.211 | 0.095 | 0.815 | 21,000 | 600 | 14 | 32 | 8908 |
| random | 30 | MinHash | {"b": 16, "r": 8} | 0.505 | 0.122 | 0.135 | 0.789 | 0.771 | 0.194 | 0.378 | 0.951 | 20,992 | 2,560 | 585704 | 4081 | 765 |
| random | 30 | CMS | {"D": 2, "b": 4, "r": 8} | 0.150 | 0.100 | 0.104 | 0.555 | 0.531 | 0.774 | 0.116 | 1.000 | 20,992 | 640 | 18 | 361 | 82 |
| random | 100 | FBF | {"k": 40, "s": 6} | 0.765 | 0.058 | 0.062 | 0.987 | 0.986 | 0.090 | 0.027 | 0.244 | 70,000 | 420,000 | 634512 | 82 | 174 |
| random | 100 | GBF | {"k": 50} | 0.397 | 0.292 | 0.279 | 0.695 | 0.635 | 0.251 | 0.486 | 1.000 | 70,000 | 1,400,000 | 597471 | 79 | 154 |
| random | 100 | LSBF | {"L": 32, "r": 16} | 0.750 | 0.093 | 0.102 | 0.963 | 0.962 | 0.078 | 0.116 | 0.349 | 69,984 | 10,240 | 176 | 1338 | 640 |
| random | 100 | BF | {} | 0.000 | 0.000 | 0.000 | 0.500 | 0.501 | 0.000 | 1.000 | 1.000 | 70,000 | 0 | 0 | 1081 | 1479 |
| random | 100 | SimHash | {"b": 100} | 0.800 | 0.188 | 0.185 | 0.997 | 0.996 | 0.029 | 0.015 | 0.106 | 70,000 | 2,000 | 35 | 42 | 12856 |
| random | 100 | MinHash | {"b": 32, "r": 8} | 0.674 | 0.072 | 0.089 | 0.902 | 0.897 | 0.086 | 0.278 | 0.713 | 69,984 | 5,120 | 1169098 | 8333 | 1494 |
| random | 100 | CMS | {"D": 4, "b": 4, "r": 16} | 0.474 | 0.056 | 0.056 | 0.771 | 0.732 | 0.382 | 0.198 | 0.859 | 69,984 | 1,280 | 28 | 614 | 118 |
| nytimes | 3 | FBF | {"k": 5, "s": 26} | 0.257 | 0.042 | 0.061 | 0.637 | 0.597 | 0.464 | 0.292 | 1.000 | 10,500 | 273,000 | 136595 | 19 | 24 |
| nytimes | 3 | GBF | {"k": 20} | 0.021 | -0.018 | -0.016 | 0.503 | 0.515 | 0.989 | 0.006 | 1.000 | 10,500 | 2,688,000 | 109158 | 29 | 43 |
| nytimes | 3 | LSBF | {"L": 8, "r": 16} | 0.074 | 0.005 | 0.025 | 0.539 | 0.536 | 0.553 | 0.378 | 1.000 | 10,496 | 32,768 | 189 | 281 | 149 |
| nytimes | 3 | BF | {} | 0.015 | 0.017 | 0.044 | 0.503 | 0.515 | 0.245 | 0.750 | 1.000 | 10,500 | 0 | 0 | 1202 | 1225 |
| nytimes | 3 | SimHash | {"b": 3} | 0.000 | 0.000 | 0.000 | 0.500 | 0.514 | 0.000 | 1.000 | 1.000 | 10,500 | 768 | 35 | 14 | 1343 |
| nytimes | 3 | MinHash | {"b": 4, "r": 4} | 0.124 | 0.030 | 0.046 | 0.567 | 0.554 | 0.397 | 0.489 | 1.000 | 10,500 | 4,096 | 105820 | 431 | 93 |
| nytimes | 3 | CMS | {"D": 2, "b": 4, "r": 8} | 0.000 | 0.000 | 0.000 | 0.500 | 0.514 | 0.000 | 1.000 | 1.000 | 10,496 | 8,192 | 63 | 270 | 68 |
| nytimes | 10 | FBF | {"k": 5, "s": 26} | 0.440 | 0.106 | 0.141 | 0.759 | 0.711 | 0.360 | 0.227 | 1.000 | 35,000 | 910,000 | 449462 | 28 | 34 |
| nytimes | 10 | GBF | {"k": 30} | 0.039 | -0.015 | -0.012 | 0.507 | 0.517 | 0.971 | 0.016 | 1.000 | 35,000 | 8,960,000 | 328594 | 47 | 64 |
| nytimes | 10 | LSBF | {"L": 4, "r": 16} | 0.247 | 0.040 | 0.084 | 0.640 | 0.617 | 0.479 | 0.312 | 1.000 | 35,000 | 16,384 | 99 | 136 | 72 |
| nytimes | 10 | BF | {} | 0.046 | 0.054 | 0.192 | 0.503 | 0.516 | 0.007 | 0.987 | 0.987 | 35,000 | 0 | 0 | 1251 | 1237 |
| nytimes | 10 | SimHash | {"b": 10} | 0.043 | -0.006 | 0.003 | 0.509 | 0.519 | 0.952 | 0.029 | 1.000 | 35,000 | 2,560 | 38 | 24 | 10068 |
| nytimes | 10 | MinHash | {"b": 16, "r": 4} | 0.210 | 0.034 | 0.067 | 0.627 | 0.604 | 0.428 | 0.380 | 1.000 | 34,992 | 16,384 | 395888 | 1630 | 408 |
| nytimes | 10 | CMS | {"D": 2, "b": 4, "r": 16} | 0.032 | -0.003 | -0.007 | 0.504 | 0.516 | 0.981 | 0.010 | 1.000 | 34,992 | 16,384 | 101 | 286 | 92 |
| nytimes | 30 | FBF | {"k": 20, "s": 26} | 0.617 | 0.080 | 0.162 | 0.889 | 0.865 | 0.216 | 0.162 | 0.782 | 105,000 | 2,730,000 | 1335993 | 65 | 80 |
| nytimes | 30 | GBF | {"k": 30} | 0.054 | 0.041 | 0.038 | 0.507 | 0.518 | 0.969 | 0.017 | 1.000 | 105,000 | 26,880,000 | 1029117 | 73 | 91 |
| nytimes | 30 | LSBF | {"L": 16, "r": 16} | 0.390 | 0.020 | 0.121 | 0.740 | 0.723 | 0.247 | 0.403 | 0.961 | 104,992 | 65,536 | 370 | 558 | 292 |
| nytimes | 30 | BF | {} | 0.079 | 0.112 | 0.325 | 0.502 | 0.516 | 0.000 | 0.996 | 0.996 | 105,000 | 0 | 0 | 1381 | 1384 |
| nytimes | 30 | SimHash | {"b": 30} | 0.668 | 0.100 | 0.236 | 0.912 | 0.908 | 0.177 | 0.140 | 0.534 | 105,000 | 7,680 | 60 | 29 | 12615 |
| nytimes | 30 | MinHash | {"b": 32, "r": 4} | 0.351 | 0.055 | 0.123 | 0.712 | 0.695 | 0.282 | 0.403 | 0.951 | 104,992 | 32,768 | 783530 | 3336 | 871 |
| nytimes | 30 | CMS | {"D": 2, "b": 4, "r": 16} | 0.127 | 0.040 | 0.065 | 0.569 | 0.556 | 0.354 | 0.531 | 1.000 | 104,992 | 16,384 | 108 | 354 | 94 |
| nytimes | 100 | FBF | {"k": 30, "s": 26} | 0.743 | 0.131 | 0.247 | 0.965 | 0.960 | 0.097 | 0.091 | 0.535 | 350,000 | 9,100,000 | 4431509 | 165 | 180 |
| nytimes | 100 | GBF | {"k": 20} | 0.037 | 0.007 | 0.015 | 0.506 | 0.517 | 0.973 | 0.014 | 1.000 | 350,000 | 89,600,000 | 3260341 | 152 | 165 |
| nytimes | 100 | LSBF | {"L": 32, "r": 16} | 0.608 | 0.041 | 0.212 | 0.877 | 0.870 | 0.193 | 0.217 | 0.827 | 349,984 | 131,072 | 748 | 1059 | 667 |
| nytimes | 100 | BF | {} | 0.079 | 0.112 | 0.325 | 0.502 | 0.516 | 0.000 | 0.996 | 0.996 | 350,000 | 0 | 0 | 1656 | 1606 |
| nytimes | 100 | SimHash | {"b": 100} | 0.812 | 0.323 | 0.593 | 0.998 | 0.999 | 0.001 | 0.016 | 0.009 | 350,000 | 25,600 | 161 | 38 | 18848 |
| nytimes | 100 | MinHash | {"b": 32, "r": 4} | 0.461 | 0.078 | 0.174 | 0.783 | 0.767 | 0.218 | 0.370 | 0.951 | 349,984 | 32,768 | 785125 | 3302 | 761 |
| nytimes | 100 | CMS | {"D": 2, "b": 4, "r": 16} | 0.288 | -0.004 | 0.074 | 0.672 | 0.646 | 0.296 | 0.437 | 0.965 | 350,000 | 16,384 | 107 | 460 | 99 |

Bootstrap: 10,000 resamples, two-stage (folds, then queries within fold), paired across methods.
Biology-removed control over 20 cells: FBF > GBF (CI) in 15, GBF > FBF (CI) in 0.

<!-- END GENERATED -->
