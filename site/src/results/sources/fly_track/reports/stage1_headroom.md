# Stage 1: headroom gate G1

Protocol `432cb7daac69472c`, `docs/exp1_continuation_preregistration.md` §5. Every number below is rendered from `reports/exp1c/g1.json`, which `scripts/exp1c_analyze.py g1` regenerates from the raw per-episode files in `raw_results_exp1c/stage1/`. Evaluation: fresh set F1, first 1000 episodes, through `scripts/exp1c_evaluate.py` and the access guard only.

## Verdict

**G1: NO-GO**

Reading: no-go.

| Bio minus bypass | Estimate [95% CI] | 90% CI | Registered threshold |
|---|---|---|---|
| Tracked fraction (primary) | -0.0212 [-0.0353, -0.0074] | [-0.0328, -0.0097] | no-go: upper < +0.03; go: lower > 0 and estimate >= +0.03 |
| Success | -0.0227 [-0.0400, -0.0051] | [-0.0375, -0.0078] | no-go also needs upper < +0.03 |

Why: Both upper bounds are below +0.03.

## Realized precision (sign-off decision 1)

| Endpoint | Arm | Realized seed SD | Planning seed SD | Ratio |
|---|---|---:|---:|---:|
| tracked_frac | bio | 0.0271 | 0.0249 | 1.09 |
| tracked_frac | bypass | 0.0201 | 0.0254 | 0.79 |
| success | bio | 0.0301 | 0.0200 | 1.51 |
| success | bypass | 0.0263 | 0.0454 | 0.58 |

Largest ratio 1.51 (the underpowered-gate reading applies to an ambiguous verdict at >= 1.75). P(no-go | true difference 0) recomputed from the realized components: 95% (tracked leg 99%, success leg 95%); planned 83%.

## Every arm (descriptive)

| Arm | Seeds | Tracked fraction | Success | Success without collision clause | Post-collision episodes | Wall-collision episodes | Target-contact episodes |
|---|---:|---:|---:|---:|---:|---:|---:|
| bio | 30 | 0.8889 | 0.7356 | 0.7850 | 0.1323 | 0.0737 | 0.0833 |
| bypass | 30 | 0.9102 | 0.7583 | 0.8034 | 0.1329 | 0.0452 | 0.0827 |
| rew1001 | 15 | 0.8952 | 0.7422 | 0.7924 | 0.1353 | 0.0665 | 0.0795 |
| rew1002 | 15 | 0.8887 | 0.7358 | 0.7861 | 0.1328 | 0.0728 | 0.0792 |
| rew1003 | 15 | 0.9066 | 0.7535 | 0.8083 | 0.1276 | 0.0590 | 0.0775 |
| two_unit | 15 | 0.7848 | 0.5941 | 0.6368 | 0.1747 | 0.1225 | 0.0761 |

Bio minus each other arm, tracked fraction (descriptive intervals, no gate; the rewired arms are the parent role x side null, un-normalized):

| Comparison | Estimate [95% CI] |
|---|---|
| bio - rew1001 | -0.0063 [-0.0218, +0.0086] |
| bio - rew1002 | +0.0002 [-0.0189, +0.0194] |
| bio - rew1003 | -0.0177 [-0.0350, -0.0013] |
| bio - two_unit | +0.1041 [+0.0701, +0.1427] |

Bio minus bypass, secondary endpoints (post and wall collisions are never pooled):

| Endpoint | Estimate [95% CI] |
|---|---|
| post_collision | -0.0006 [-0.0128, +0.0108] |
| wall_collision | +0.0285 [+0.0178, +0.0399] |
| contact | +0.0006 [-0.0074, +0.0082] |
| success_no_collision | -0.0184 [-0.0365, -0.0002] |

## Convergence

| Arm | Converged | Cap | Cap, still rising | Failed | Steps (median, min-max) | Best step (median) |
|---|---:|---:|---:|---:|---|---:|
| bio | 30 | 0 | 0 | 0 | 5250 (4000-11000) | 4500 |
| bypass | 30 | 0 | 0 | 0 | 4500 (4000-13250) | 3625 |
| rew1001 | 15 | 0 | 0 | 0 | 5000 (4000-14500) | 3750 |
| rew1002 | 15 | 0 | 0 | 0 | 5250 (4000-8250) | 4000 |
| rew1003 | 15 | 0 | 0 | 0 | 5750 (4000-8750) | 5000 |
| two_unit | 15 | 0 | 0 | 0 | 6250 (4000-10250) | 4750 |

Mean validation tracked fraction by step (runs still training at that step only):

| Arm | 1000 | 2000 | 4000 | 8000 | 12000 | 16000 |
|---|---:|---:|---:|---:|---:|---:|
| bio | 0.798 (n=30) | 0.849 (n=30) | 0.866 (n=30) | 0.893 (n=4) | - | - |
| bypass | 0.887 (n=30) | 0.897 (n=30) | 0.905 (n=30) | 0.913 (n=1) | 0.929 (n=1) | - |
| rew1001 | 0.800 (n=15) | 0.865 (n=15) | 0.876 (n=15) | 0.901 (n=2) | 0.951 (n=1) | - |
| rew1002 | 0.809 (n=15) | 0.848 (n=15) | 0.881 (n=15) | 0.876 (n=2) | - | - |
| rew1003 | 0.821 (n=15) | 0.866 (n=15) | 0.881 (n=15) | 0.909 (n=1) | - | - |
| two_unit | 0.607 (n=15) | 0.672 (n=15) | 0.736 (n=15) | 0.796 (n=4) | - | - |

## Two-unit learning rate

Rule: highest best validation tracked fraction; tie -> lower mean |bearing|.

| lr | Best validation tracked fraction | Stop | Steps |
|---:|---:|---|---:|
| 0.001 | 0.6723 | converged | 5000 |
| 0.003 | 0.8236 | converged | 10250 |

Chosen: 0.003.

## What follows

G1 is no-go, so Stage 1b (occlusion) is next under the same rule and seeds, once its authorization (`AUTHORIZED G1b`) is recorded. If G1b is also no-go, H2 stops on this task family and the structural explanation is written up as the result.

Work stops here pending sign-off.
