# Expanded curriculum results

Run: `curriculum-20261009T163310`. Generated from saved artifacts at 2026-10-09T16:49:32.605306+00:00.

Training increased from 12 to **246 verified examples**. The fixed network still contains 165,122 neurons and 25,563,197 directed edges.

The pretrained LLM comparison was deferred as requested. No API calls were made in this experiment.

| Model | Fresh MBPP subset | Unseen constants | Seen training examples | Readout parameters |
|---|---:|---:|---:|---:|
| Fly · seed 7 | 0/24 | 0/30 | 1/8 | 1,325,544 |
| Fly · seed 19 | 0/24 | 0/30 | 0/8 | 1,325,544 |
| No recurrence · seed 7 | 0/24 | 0/30 | 1/8 | 1,325,544 |
| No recurrence · seed 19 | 0/24 | 0/30 | 0/8 | 1,325,544 |

The table uses the stronger post-run tests for authored exercises. Original weak tests incorrectly counted three transfer solutions as passing in each seed-19 model. All three used incorrect constants. The audit preserves every original result and rejudges the same code without retraining or regeneration. This correction was made after inspecting outputs, not preregistered.

The added tests cover all lists of length 0–2 over integers −8 through 12, exact threshold neighbors, duplicates and longer lists. MBPP supplied tests remain unchanged. This follows the test-adequacy motivation of [EvalPlus (Liu et al., 2023)](https://arxiv.org/abs/2305.01210); it is a custom audit, not the EvalPlus benchmark. Full cases, original scores and corrected scores are saved under `test-adequacy-audit/`.

MBPP uses 24 problems selected before training from the 209 judge-compatible official-test records. This is not the full MBPP benchmark or an official LeetCode score. Transfer means 30 new constants in the same ten authored templates, not unseen algorithms. Training reproduction uses eight already-seen problems. The two seeds change readout initialization and minibatches; they share one frozen reservoir/input mapping.

## Validation-only calibration

| Setting | Recurrent target radius | Leak | Input scale | Best validation loss |
|---|---:|---:|---:|---:|
| calibration-0 | 0.045263 | 0.5 | 0.35 | 4.333772 |
| calibration-1 | 0.900000 | 0.5 | 0.1 | 4.364111 |
| calibration-2 | 0.990000 | 0.2 | 0.1 | 5.095241 |

Selected `calibration-0` using only calibration-validation cross entropy. The graph dominant eigenvalue estimate was 6031.8350, with relative residual 1.66e-06. Spectral scaling does not itself establish biological plausibility or an echo-state guarantee.

## Learning evidence

| Model | Initial train loss | Final train loss | Selected step | Best validation loss |
|---|---:|---:|---:|---:|
| Fly · seed 7 | 6.6187 | 0.0290 | 100 | 4.3164 |
| Fly · seed 19 | 6.6289 | 0.0369 | 100 | 4.3087 |
| No recurrence · seed 7 | 6.6187 | 0.0449 | 100 | 4.3158 |
| No recurrence · seed 19 | 6.6289 | 0.0481 | 100 | 4.3083 |

Every full-data head received 1,600 updates × 512 targets = 819,200 solution-token/EOS exposures. These repeatedly sample the same corpus, not independent examples. This total is per arm and per head seed. Calibration and feature collection add further cost, retained in their own receipts. No test outcomes selected a checkpoint.

## Initial-head probe

The untrained readouts were evaluated on a fixed small mix of two training, two transfer and two test problems. This probe is separate from the headline denominators.

- fly: 0/6 passed with the untrained head.
- no-recurrence: 0/6 passed with the untrained head.

## Exact program evidence

The following are actual generated programs, with their evaluation split. A training reproduction or familiar-template pass must not be presented as a new algorithm solution.

### fly-s7: curr-offset-sum-0 (train)

solve(nums): Add 0 to the sum of all numbers in nums.

```python
def solve(nums):
    return sum(nums) + 0
```
Passed 470/470 evaluated cases.

fly-s19: no passing program in the evaluated sets.

## Interpretation

The fly-plus-readout system did not solve a fresh sampled MBPP task in either readout seed. Training or template-level gains, if present above, are not evidence of general coding ability.

All graph data and count ratios remain unchanged. Prompt-context memory, lexical tokenization, the output clock and the nonlinear readout are artificial modeling additions shared with the control. Any success belongs to that complete system; the connectome alone is not a demonstrated code-writing biological brain.

The sampled MBPP tasks are now exposed evaluation data. Further model changes should use validation data and fresh final-test tasks. Real-world programming claims need larger independent tests, more than two head seeds, and eventually the separately measured pretrained reference.

See [PROTOCOL_V2.md](PROTOCOL_V2.md) for methodological sources and the pre-training plan. Full source and program artifacts are under the run directory; no test-selected solution repairs or replacements are used.
