# EXP3 Track C: is the fly's non-random wiring an adaptation to a skewed odour distribution?

**Status of the idea.** This is a **hypothesis proposed by the experiment's author** (EXP3 brief, section 2), not a finding from the literature. It is **speculative**. It proposes that the fly's non-random PN→KC wiring is adapted to a skewed, heavy-tailed natural odour distribution. If so, the wiring should help retrieval only when queries are skewed onto the overconverged channels, and not under uniform or mismatched skew. That would explain Senge's null (single-author preprint, not peer reviewed) as a distribution mismatch.

**Fitted to nothing.** The matched skew was defined from connectome statistics alone, in `configs/trackC_skew_definition.md`. That file, and the ranking it produces (`configs/trackC_ranking.json`), were **frozen** and their SHA-256 written into the preregistration before any Track C or B1 retrieval number existed. The analysis script checks both hashes on every run and refuses to proceed if either has drifted. Gate G9 tests that refusal live, by running the analysis on a tampered copy of the definition. Because the definition predates every number, the claim "fitted to nothing" is earned here and may be asserted.

**The definition, briefly.**
- **Overconvergence score:** per-glomerulus co-convergence Q_g = Σ_{l≠g} (MMᵀ)²_{gl} on the w ≥ 5 matrix, z-scored against 1,000 degree-preserving (N1) nulls.
- **Orders:** the matched order ranks glomeruli by that z score, descending; the mismatched order is its reverse.
- **Skew family:** items activate 3–10 glomeruli, drawn with probability ∝ rank^(−β) for β ∈ {0, 0.5, 1, 1.5, 2}. Amplitudes are LogNormal(0, 1), and each item is normalised to unit mean.
- **Scale:** 10,000 database items and 1,000 queries per trial, 20 trials, ground truth the top 2% by Euclidean distance, metric AP@200.
- **Comparison:** BIO against N0, N1 and N3, with N2 = N1 on the binary matrix and 20 draws per level per trial.

**The two hemispheres disagree about which glomeruli are overconverged.**
- Per-glomerulus z agrees between L and R only at Spearman 0.46.
- 7 of Zheng et al.'s 10 core-community glomeruli fall in the left hemisphere's top 10, but only 3 in the right's.
- Zheng's reference connectome, the hemibrain, is itself a **right hemisphere**, so the left hemisphere's better agreement with it is the surprising direction. That bears on whether the overconvergence structure is a stable feature of the species or varies between individuals and sides, and Track C's premise depends on which.
- These were measured after the definition was frozen and change nothing in it. Each hemisphere uses its own ranking, so Track C tests two partly different matched distributions.

**Hardware.** Apple M5 (10 cores, 32 GB), macOS 26.6.2, single-threaded BLAS per worker (8 workers, nice 19), Python 3.12.13, numpy 2.5.4; float64 hashing, float32 overlap scoring; batch = the 1,000 queries against 10,000 items per evaluation; 40 trial files in 4,496 s at load 30–60. The machine was shared with other sessions, which affects wall time only; Track C measures accuracy.

## Result

**Predeclared overall verdict: CONTRADICTED UNDER THESE CONDITIONS**, in both hemispheres. The upper 95% CI bound of Δ(matched, β) is below +2.5% for β ∈ {1.5, 2}, against both N1 and N3, on L and on R. The hash checker ran first on every analysis run and passed; the definition and ranking are byte-identical to the hashes in the preregistration.

**The predicted crossover did not appear; in the left hemisphere the opposite did.** The hypothesis predicts that skewing items onto the overconverged glomeruli helps the real wiring relative to its nulls. Instead:
- **Left hemisphere:** matched skew makes BIO *worse* against N1 as skew grows: −1.10% at β = 0, −4.20% at 0.5, −7.17% at 1.0, −6.89% at 1.5, −5.54% at 2.0. Every CI lies below 0. Mismatched skew leaves BIO level with N1: +0.02% [−0.32%, +0.38%] at β = 2. The interaction, matched minus mismatched at β = 2, is −5.57% [−6.09%, −5.04%] against N1: significantly in the *wrong* direction.
- **Right hemisphere:** BIO's position does improve with skew, from −1.21% at β = 0 to +1.62% [+1.35%, +1.88%] at matched β = 2 against N1. That stays below the +2.5% margin, and against N3 it is only +0.52%. Mismatched skew improves it *more* (+2.34% at β = 2), so the interaction is again negative: −0.73% [−1.13%, −0.33%].
- **Uniform items (β = 0):** the nulls win slightly in both hemispheres (−1.1% to −1.5%). That matches criterion (a) and B1's direction.

So in neither hemisphere does the distribution the connectome itself marks as "matched" favour the real wiring over the mismatched one. The R hemisphere's modest rise under skew is not specific to the matched order. One reading is that any concentration of input onto a few glomeruli shrinks the nulls' advantage on R, whichever glomeruli those are. That reading is descriptive and post hoc.

**What this does and does not rule out.** It is evidence against the hypothesis as operationalised: the frozen definition is Q_g z-score ranking, power-law skew over 3–10 active glomeruli, LogNormal amplitudes, AP@200 under Euclidean ground truth, and a fixed top-k tag-overlap readout. The CIs exclude the predicted +2.5% gain, so this is a measured negative, not an absence of evidence. It does **not** rule out:
- a different notion of "natural" odour statistics, such as real odour-scene co-occurrence, which no dataset here provides;
- a different overconvergence statistic;
- a readout with plasticity: the MBON learning stage is not modelled.

Those remain unknown, not contradicted.

**Interpretation limit (stated whatever the outcome, as preregistered).** Even a clean crossover would only have shown that the wiring *can be exploited* under a matched distribution. That is a statement about the fly's adaptation, not useful engineering, because a learned projection (BioHash's approach) could probably capture the same structure more cheaply. The negative result makes that limit moot for engineering. It is restated here so that no reading of the R hemisphere's +1.6% is taken as an engineering lead.

**The hemisphere disagreement matters for the premise.** As noted above, the two hemispheres rank glomeruli differently (Spearman 0.46). The left hemisphere agrees better with Zheng et al.'s core community, even though Zheng's hemibrain is a right hemisphere. Track C's premise needs a species-stable overconvergence pattern for natural skew to match. A pattern that differs this much between the two sides of one animal is weak support for that premise, independently of the retrieval numbers.

## Labels

- **The fly's non-random PN→KC wiring is adapted so that it helps retrieval under a skewed odour distribution matched to its overconverged glomeruli: contradicted under specified conditions.** Both hemispheres and both null levels show it, under the frozen definition. In L the matched skew hurts the wiring.
- **The hypothesis as stated in the brief (the author's speculative hypothesis), under other definitions of natural odour statistics or overconvergence: unknown.** Untested; an absence of evidence.
- **Senge's null is explained by a distribution mismatch: contradicted under specified conditions.** Removing the mismatch, in the operationalised sense, did not produce a benefit.
- **R-hemisphere wiring gains on its nulls as inputs concentrate onto few glomeruli, regardless of which: plausible but untested** (post hoc; gain < SESOI).
- **The overconvergence pattern is stable across hemispheres of one animal: weakly supported at best.** L–R Spearman is 0.46; descriptive, measured after the freeze.

<!-- BEGIN GENERATED (scripts/trackC_analyze.py) -->

**Predeclared overall verdict: CONTRADICTED UNDER THESE CONDITIONS.** Hemisphere verdicts: L contradicted, R contradicted.

| hemisphere | β | order | AP BIO | Δ vs N0 | Δ vs N1 [95% CI] | Δ vs N3 [95% CI] |
|---|---|---|---|---|---|---|
| L | 0.0 | matched | 0.4711 | -20.40% | -1.10% [-1.20%, -1.00%] | -1.37% [-1.47%, -1.26%] |
| L | 0.0 | mismatched | 0.4707 | -20.14% | -1.09% [-1.19%, -0.99%] | -1.33% [-1.42%, -1.22%] |
| L | 0.5 | matched | 0.4192 | -21.47% | -4.20% [-4.45%, -3.97%] | -3.68% [-3.90%, -3.48%] |
| L | 0.5 | mismatched | 0.4267 | -20.23% | -0.10% [-0.27%, +0.07%] | -0.76% [-0.92%, -0.60%] |
| L | 1.0 | matched | 0.3405 | -20.38% | -7.17% [-7.42%, -6.92%] | -5.89% [-6.11%, -5.66%] |
| L | 1.0 | mismatched | 0.3398 | -20.71% | +0.19% [-0.04%, +0.42%] | -0.86% [-1.08%, -0.64%] |
| L | 1.5 | matched | 0.2957 | -16.14% | -6.89% [-7.21%, -6.59%] | -5.67% [-5.98%, -5.35%] |
| L | 1.5 | mismatched | 0.2783 | -20.74% | +0.11% [-0.22%, +0.44%] | -1.29% [-1.65%, -0.94%] |
| L | 2.0 | matched | 0.2817 | -10.77% | -5.54% [-5.84%, -5.23%] | -4.59% [-4.90%, -4.29%] |
| L | 2.0 | mismatched | 0.2551 | -19.05% | +0.02% [-0.32%, +0.38%] | -1.42% [-1.78%, -1.05%] |
| R | 0.0 | matched | 0.4869 | -18.10% | -1.21% [-1.34%, -1.08%] | -1.45% [-1.58%, -1.31%] |
| R | 0.0 | mismatched | 0.4835 | -18.17% | -1.29% [-1.47%, -1.11%] | -1.50% [-1.67%, -1.34%] |
| R | 0.5 | matched | 0.4425 | -17.32% | -1.46% [-1.68%, -1.24%] | -1.83% [-2.03%, -1.64%] |
| R | 0.5 | mismatched | 0.4268 | -20.23% | -0.66% [-0.84%, -0.47%] | -0.96% [-1.13%, -0.80%] |
| R | 1.0 | matched | 0.3712 | -13.25% | -0.27% [-0.54%, -0.01%] | -1.02% [-1.24%, -0.80%] |
| R | 1.0 | mismatched | 0.3342 | -22.10% | +0.35% [+0.11%, +0.59%] | -0.00% [-0.21%, +0.21%] |
| R | 1.5 | matched | 0.3160 | -9.92% | +0.55% [+0.32%, +0.76%] | -0.32% [-0.57%, -0.08%] |
| R | 1.5 | mismatched | 0.2707 | -23.31% | +1.59% [+1.23%, +1.96%] | +1.23% [+0.93%, +1.56%] |
| R | 2.0 | matched | 0.2931 | -6.51% | +1.62% [+1.35%, +1.88%] | +0.52% [+0.28%, +0.76%] |
| R | 2.0 | mismatched | 0.2433 | -22.19% | +2.34% [+1.99%, +2.68%] | +2.05% [+1.70%, +2.39%] |

| hemisphere | level | interaction Δ(matched, β=2) − Δ(mismatched, β=2) [95% CI] | (a) uniform: no gain | (b) matched gain | (c) interaction | contradicted |
|---|---|---|---|---|---|---|
| L | N1 | -5.57% [-6.09%, -5.04%] | True | False | False | True |
| L | N3 | -3.17% [-3.74%, -2.62%] | True | False | False | True |
| R | N1 | -0.73% [-1.13%, -0.33%] | True | False | False | True |
| R | N3 | -1.53% [-1.99%, -1.09%] | True | False | False | True |

<!-- END GENERATED -->
