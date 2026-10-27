# EXP3 synthesis: does fly-brain structure help retrieval, and if so where

**What this experiment was.** A falsification exercise with one open niche attached, not a test of whether the fly brain improves retrieval. Most of the question was settled before EXP3 began, and the settled answer was mostly no. EXP3 asked whether that answer survives three things:
- the production baselines the field actually uses (Track A);
- an independent replication, with a null ladder that grades (Track B1);
- the one hypothesis under which the connectome could still win (Track C, the experiment author's speculative hypothesis).

It also placed fly methods on a modern ANN frontier for the first time (Track B2). Everything was preregistered (`docs/exp3_preregistration.md`, signed 2026-10-23) and amended only through logged amendments A1–A16 (`docs/exp3_amendments.md`). Hardware, precision, batch size, threads and dataset versions for every number are in the track reports.

**Load-bearing source.** Senge 2026 (arXiv:2610.09114 v1) is a **single-author preprint, not peer reviewed**. Wherever it is relied on below, that is why the label is no stronger than it is. Our replication agreed with it (Track B1).

## Verdicts, as predeclared

| Track | Question | Predeclared verdict | Report |
|---|---|---|---|
| A | Does the 2018 fly Bloom filter beat SimHash / MinHash / count-min at matched memory? | **MIXED**: wins at 3–10 bits/item, loses at 30–100 | `reports/exp3_trackA_novelty.md` |
| B1 | Does MaleCNS olfactory wiring beat degree-preserving rewiring (Senge's test)? | **REPLICATES SENGE** | `reports/exp3_trackB_connectome.md` |
| B2 | Where do FlyHash and DenseFly sit on the ANN-Benchmarks frontier? | **INSIDE THE FRONTIER** on SIFT and on GloVe | `reports/exp3_trackB_connectome.md` |
| C | Does the wiring win when queries are skewed onto its overconverged channels? | **CONTRADICTED UNDER THESE CONDITIONS** | `reports/exp3_trackC_skew.md` |

## What each track established

**Track A: distance-sensitive novelty (the one untested niche).**
- **Low memory:** at 3 and 10 bits per stored item, the fly Bloom filter (FBF) beats the best production baseline at matched memory in 8 of 8 cells across SIFT, MNIST, random exponential and nytimes, with CIs excluding 0.
- **High memory:** at 30 and 100 bits per item, which includes the 2018 paper's own budget, the SimHash fingerprint store beats it.
- **Cost of the wins:** they come at 8–353× the projection arithmetic of the winning baseline, and FBF's encoding cost grows with the stored-set size.
- **Usability:** in the regime where FBF wins, no method is a usable near-duplicate detector. At a 1% false-positive rate, every method at ≤ 10 bits per item misses ≥ 84% of familiar items.
- **The 2018 comparison:** its own ordering (FBF > LSBF > Bloom filter) reproduces.
- **Overall:** the "narrow publishable win" is real but narrower than predeclared, and it sits where the task is barely solvable.

**Track B1: does the connectome add anything to the hash.**
- **Replication:** Senge replicated on MaleCNS, 2 of his 7 hemispheres. On his own matrix we measure −2.09% against degree-preserving rewiring; he reports −2.06%.
- **Bounding a benefit:** in both hemispheres and at both synapse thresholds, the upper CI bound is below the +2.5% margin. This is evidence of no benefit, not an absence of evidence.
- **Two findings beyond Senge:**
  - (i) His conclusion depends on how unmeasured DoOR entries are filled. Under mean imputation, the left hemisphere's wiring beats its null by +3.38%, with a CI above the margin.
  - (ii) The null that also preserves per-glomerulus co-convergence (NQ) closes most of the gap. Descriptively, then, the co-convergence structure is what makes the real wiring score below a random shuffle. This is not a predeclared reading.

**Track C: the skew hypothesis.**
- **Verdict:** contradicted under the frozen conditions in both hemispheres. The definition was frozen and hashed before any number existed, and the hash was re-checked on every analysis run, so the result is fitted to nothing.
- **Left hemisphere:** skewing queries onto the connectome's own overconverged glomeruli made the real wiring *worse* against its nulls, down to −7.2% at β = 1.
- **Right hemisphere:** the wiring improved under skew, but by less than the margin, and more under mismatched skew than under matched.
- **What it no longer explains:** Senge's null cannot be explained as a distribution mismatch, in the sense operationalised here.

**Track B2: the ANN frontier (ConnectomeHash dropped, because B1 replicated).**
- **Verdict:** inside the frontier on SIFT 1M and on GloVe 1.2M, as predicted in advance. The comparison is against hnswlib, ScaNN and FAISS IVF-PQ (plain and fast-scan), each on its full published or registered grid, with no fly method given more than hnswlib's 81 configurations.
- **FlyHash:** reaches recall@10 0.9, but at 0.43% (SIFT) and 0.52% (GloVe) of the best baseline's queries per second. The best baseline is ScaNN in both cases. FlyHash does not reach 0.95 on GloVe.
- **DenseFly:** never reaches recall 0.8 on either dataset (maximum 0.525 and 0.420).
- **Why FlyHash is slow:** the gap is not mainly numpy against C++. FlyHash's recall-0.9 configurations touch 1.3–4.1× the database size in inverted-list entries per query, so its per-query work grows with n in any language.
- **Where the fly methods do well:** fly builds are quick (11–67 s), and insertion is about 10–70× faster than hnswlib's. Neither is an advantage over ScaNN or FAISS fast-scan.
- **Incidents, none of which changes a readout:** 26 out-of-memory kills in the first pass, a faiss-ivfpq padding fault, and a 12 h host sleep (A14, A16).
- **The extra costs promised in the preregistration** (encoding, insertion, deletion) were measured late, under a rule logged first (A15).

## Labels on the settled starting points, after EXP3

- **Fly-hash advantage is per active cell, not per operation: contradicted under matched-arithmetic conditions — against real-valued Gaussian projections only; against one-bit codes the fly hash leads from k = 32.** This label rests on Senge (single-author, not peer reviewed); EXP3 did not re-measure it. Track A is consistent with it in spirit: every FBF win costs far more projection arithmetic than the baseline it beats.
- **Connectome wiring adds nothing to the hash.**
  - **Before EXP3:** plausible but untested.
  - **After, for MaleCNS odours with zero-filled inputs:** contradicted under specified conditions as a *benefit*. The wiring is no better than degree-preserving rewiring, and the CIs bound any gain below +2.5%.
  - **Under mean imputation on the left hemisphere:** a benefit appears.
  - **Hemibrain, FlyWire and BANC:** unknown (not re-extracted; absence of evidence).
- **FlyHash has never been benchmarked against a modern ANN index.** Before: absence of evidence. After: **demonstrated: inside the frontier** on SIFT and GloVe against tuned hnswlib, ScaNN and FAISS. This is a measured negative, not an absence of evidence. DenseFly does not reach recall 0.8. That a compiled FlyHash would also stay inside is **plausible but untested**, although its candidates touched per query exceed the database size. Other datasets (MNIST, Fashion-MNIST, NYTimes) remain **unknown**.
- **The non-random PN→KC wiring helps under its matched natural distribution: contradicted under specified conditions** (Track C, the author's speculative hypothesis, frozen definition). Other operationalisations of "natural odour statistics" are **unknown**.
- **Removing the biology improves performance: demonstrated as a pattern before EXP3; EXP3 adds weak, confounded evidence.** In Track A, the dense-Gaussian control (GBF) lost to FBF. That control is confounded by the 2017 non-negative preprocessing, so whether removing sparsity helps here is **plausible but untested**.
- **The fly Bloom filter is the one fly-derived retrieval advantage that survives production baselines: weakly supported, in a narrow regime** (≤ 10 bits per item, at higher encoding cost, where no method is usable at 1% FPR). At the budgets where the task is solvable it is **contradicted under specified conditions**.
- **Neural-embedding near-duplicate practice: unknown.** The MiniLM corpus was dropped for licensing (A6), so Track A's text result (TF-IDF nytimes) does not speak to neural-embedding practice.
- **Face-patch novelty: unknown** (no public data; abandoned with a handoff, nothing substituted).

## Which of the four meanings of "better data fetching" this experiment moved

1. **Meaning 1: similarity search (ANN retrieval). Moved, against the fly.**
   - B1 converts "the connectome adds nothing" from one unreviewed preprint into an independent replication on MaleCNS, with an imputation caveat.
   - C removes the one hypothesis under which the connectome could still have won.
   - B2 places FlyHash and DenseFly on the modern frontier for the first time. Both sit inside it, at under 1% of the best baseline's speed at matched recall, so the fly hash is not a competitive similarity-search index on these benchmarks.
   - Track A, the adjacent fifth reading (distance-sensitive novelty), moved slightly *toward* the fly, in a regime of little practical use.
2. **Meaning 2: choosing what to inspect next under a budget. Not moved.**
   - **Status:** still the largest genuinely open space, a clean absence of evidence and not a negative.
   - **The mechanism it would need:** a novelty or familiarity score that prioritises information gathering. The fly's mushroom body output neurons implicated in familiarity (for instance MBON-α′3) compute something like such a score.
   - **What EXP3 adds:** Track A shows that a fly-style novelty score grades *how* novel a far-away item is better than SimHash does on held-out queries (descriptive), but is worse at the near-duplicate boundary.
   - **Label:** whether the MBON–active-sampling connection is more than an analogy is **unknown**. This is the open direction.
3. **Meaning 3: semantic document retrieval / RAG. Not moved.** Out of scope by design. BioVSS remains the only real system, and its baselines are FAISS IVF variants, never HNSW. EXP3 also dropped its only neural-embedding corpus. Status: **unknown** (absence of evidence).
4. **Meaning 4: database, API and network fetching. Not moved, and not movable.** This is a **category error**, not an absence of evidence: the bottlenecks are I/O, indexes, query plans, permissions and rate limits, and no fly mechanism addresses any of them.

## What was not done, and why

- **Hemibrain, FlyWire and BANC:** not re-extracted (preregistered scope). B1 covers 2 of Senge's 7 hemispheres.
- **PN-level matrix:** declined at sign-off. N2 equals N1 by construction on the binary matrix.
- **Face-patch data:** abandoned; there is no public deposit. Handoff: obtain the data from the Tsao lab as a later amendment.
- **MiniLM text embeddings:** dropped because the source-text licence was unresolved.
- **ConnectomeHash in B2:** dropped, as predeclared, because B1 replicated Senge.

## Bottom line

The settled answer survives, with two qualifications. The fly connectome's specific wiring does not help a fly hash retrieve. That is now replicated independently on MaleCNS and survives the one hypothesis designed to rescue it, but it depends on how missing odour data are filled. The 2018 fly Bloom filter beats production sketches only at memory budgets too small for any method to work. On a modern ANN frontier, FlyHash and DenseFly sit well inside it, at under 1% of the best index's speed at matched recall. The one direction with no fly work at all, budgeted choice of what to inspect next, is where a fly mechanism (MBON familiarity) has a plausible but entirely untested role.
