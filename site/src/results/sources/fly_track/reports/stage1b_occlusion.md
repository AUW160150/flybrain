# Stage 1b: occlusion headroom gate G1b

Protocol `432cb7daac69472c`, `docs/exp1_continuation_preregistration.md` §7. Demonstrations, validation and the convergence rule use the occlusion condition; arms, seeds, rule and gate are Stage 1's. Every number below is rendered from `reports/exp1c/g1b.json`, which `scripts/exp1c_analyze.py g1b` regenerates from the raw per-episode files in `raw_results_exp1c/stage1b/`. Evaluation: fresh set F1b (occlusion), first 2000 episodes, through `scripts/exp1c_evaluate.py` and the access guard only.

This is a headroom gate, not a topology test. The parent experiment's occlusion success (fly_bio 40.8%, fly_bypass 41.0%, `reports/report.md`) came from nominally-trained models evaluated out of distribution; Stage 1b trains and validates on occlusion, so it is a different test and those numbers do not predict it.

## Verdict

**G1b: AMBIGUOUS** (after the single extension; final)

Reading: ambiguous at an underpowered gate: the realized seed SDs are near twice planning or more, so this ambiguity is not weak evidence of no effect.

| Bio minus bypass | Estimate [95% CI] | 90% CI | Registered threshold |
|---|---|---|---|
| Tracked fraction (primary) | +0.0070 [-0.0051, +0.0195] | [-0.0031, +0.0174] | no-go: upper < +0.03; go: lower > 0 and estimate >= +0.03 |
| Success | +0.0247 [+0.0080, +0.0409] | [+0.0109, +0.0382] | no-go also needs upper < +0.03 |

Why: Neither the no-go nor the go condition holds.

Primary verdict before the extension (superseded; 30 seeds per gate arm, first 1000 episodes; rows archived in `raw_results_exp1c/stage1b/primary_1000/`): **AMBIGUOUS**, tracked fraction +0.0085 [-0.0072, +0.0241], success +0.0230 [+0.0023, +0.0440]. Reading: ambiguous at an underpowered gate: the realized seed SDs are near twice planning or more, so this ambiguity is not weak evidence of no effect.

## Realized precision (sign-off decision 1)

| Endpoint | Arm | Realized seed SD | Planning seed SD | Ratio |
|---|---|---:|---:|---:|
| tracked_frac | bio | 0.0267 | 0.0249 | 1.07 |
| tracked_frac | bypass | 0.0233 | 0.0254 | 0.92 |
| success | bio | 0.0371 | 0.0200 | 1.86 |
| success | bypass | 0.0272 | 0.0454 | 0.60 |

Largest ratio 1.86 (the underpowered-gate reading applies to an ambiguous verdict at >= 1.75). P(no-go | true difference 0) recomputed from the realized components: 96% (tracked leg 100%, success leg 96%); planned 83%.

## Every arm (descriptive)

| Arm | Seeds | Tracked fraction | Success | Success without collision clause | Post-collision episodes | Wall-collision episodes | Target-contact episodes |
|---|---:|---:|---:|---:|---:|---:|---:|
| bio | 40 | 0.6916 | 0.4529 | 0.4913 | 0.1817 | 0.2551 | 0.0632 |
| bypass | 40 | 0.6846 | 0.4282 | 0.4601 | 0.2136 | 0.2275 | 0.0606 |
| rew1001 | 15 | 0.6927 | 0.4506 | 0.4867 | 0.1834 | 0.2550 | 0.0646 |
| rew1002 | 15 | 0.7008 | 0.4610 | 0.5004 | 0.1800 | 0.2457 | 0.0658 |
| rew1003 | 15 | 0.6951 | 0.4573 | 0.4950 | 0.1778 | 0.2572 | 0.0649 |
| two_unit | 15 | 0.5917 | 0.3069 | 0.3302 | 0.2209 | 0.3041 | 0.0622 |

Bio minus each other arm, tracked fraction (descriptive intervals, no gate; the rewired arms are the parent role x side null, un-normalized):

| Comparison | Estimate [95% CI] |
|---|---|
| bio - rew1001 | -0.0011 [-0.0131, +0.0108] |
| bio - rew1002 | -0.0092 [-0.0231, +0.0043] |
| bio - rew1003 | -0.0035 [-0.0189, +0.0131] |
| bio - two_unit | +0.0999 [+0.0761, +0.1255] |

Bio minus bypass, secondary endpoints (post and wall collisions are never pooled):

| Endpoint | Estimate [95% CI] |
|---|---|
| post_collision | -0.0319 [-0.0435, -0.0208] |
| wall_collision | +0.0276 [+0.0140, +0.0414] |
| contact | +0.0026 [-0.0023, +0.0077] |
| success_no_collision | +0.0312 [+0.0131, +0.0490] |

## Convergence

| Arm | Converged | Cap | Cap, still rising | Failed | Steps (median, min-max) | Best step (median) |
|---|---:|---:|---:|---:|---|---:|
| bio | 40 | 0 | 0 | 0 | 4500 (4000-13750) | 3625 |
| bypass | 40 | 0 | 0 | 0 | 4000 (4000-6500) | 2125 |
| rew1001 | 15 | 0 | 0 | 0 | 4500 (4000-7250) | 3500 |
| rew1002 | 15 | 0 | 0 | 0 | 4250 (4000-10000) | 3250 |
| rew1003 | 15 | 0 | 0 | 0 | 4500 (4000-10750) | 3250 |
| two_unit | 15 | 0 | 0 | 0 | 7000 (4000-13500) | 5750 |

Mean validation tracked fraction by step (runs still training at that step only):

| Arm | 1000 | 2000 | 4000 | 8000 | 12000 | 16000 |
|---|---:|---:|---:|---:|---:|---:|
| bio | 0.607 (n=40) | 0.646 (n=40) | 0.659 (n=40) | 0.684 (n=3) | 0.704 (n=1) | - |
| bypass | 0.668 (n=40) | 0.675 (n=40) | 0.668 (n=40) | - | - | - |
| rew1001 | 0.599 (n=15) | 0.663 (n=15) | 0.673 (n=15) | - | - | - |
| rew1002 | 0.606 (n=15) | 0.663 (n=15) | 0.665 (n=15) | 0.757 (n=1) | - | - |
| rew1003 | 0.613 (n=15) | 0.673 (n=15) | 0.667 (n=15) | 0.694 (n=1) | - | - |
| two_unit | 0.448 (n=15) | 0.508 (n=15) | 0.527 (n=15) | 0.581 (n=6) | 0.627 (n=1) | - |

## Two-unit learning rate

Rule: highest best validation tracked fraction; tie -> lower mean |bearing|.

| lr | Best validation tracked fraction | Stop | Steps |
|---:|---:|---|---:|
| 0.001 | 0.6723 | converged | 5000 |
| 0.003 | 0.8236 | converged | 10250 |

Chosen: 0.003. Tuned once, in Stage 1 under the nominal condition, and reused here as registered.

## What follows

The extension has been used; the verdict is final. The registered plan does not say what follows a final ambiguous G1b: Stage 2 requires a go at G1 or G1b, and the H2 stopping rule (§7) requires G1 and G1b both no-go. Neither holds, so the next step is a sign-off decision; nothing further is run under this protocol until then.

Work stops here pending sign-off.
