# First measured result

**The fixed-connectome pilot did not solve any of the six held-out coding tasks.** This establishes a negative result for this specific small experiment, not impossibility of learning with other connectome-constrained models.

Run: [`pilot-20261009T155722-s7`](../runs/pilot-20261009T155722-s7/config.json). Started 2026-10-09 15:57:22 UTC; completed 15:59:34 UTC. Seed 7, CPU, 200 updates, 12 authored training exercises, two validation exercises, six held-out algorithm families. Every locally trained arm had 449 answer-byte/EOS targets per update and 89,800 total target exposures. These exposures reuse the same very small corpus; they are not 89,800 unique bytes of code.

| Model | Solved | Pass@1 | Trainable parameters | Best validation loss (nats/target) | Mean generation time |
|---|---:|---:|---:|---:|---:|
| Full fixed fly graph + linear readout | 0/6 | 0% | 263,425 | 0.902767 | 10.746 s |
| Independently trained no-recurrence control | 0/6 | 0% | 263,425 | 0.903012 | 0.665 s |
| Tiny causal Transformer, from scratch | 0/6 | 0% | 371,777 | 2.013349 | 0.467 s |
| Pretrained GPT-4.1-mini reference | Not measured | — | Not measured | Not applicable | — |

The pretrained reference returned no valid model response because authenticated transport failed DNS resolution in this environment. Its score is null, not 0%. A command and adapter are included to measure it on a host with permitted API access. No published score or assistant-written solution was substituted.

All three trained arms selected step 50 using validation loss. Final training losses at step 200 were 0.162269 (fly), 0.162264 (no recurrence), and 0.005957 (Transformer). Their final validation losses were worse than at step 50. This shows that lower training loss is not sufficient evidence of generalization.

The fly's readout optimization took approximately 0.22 seconds **after** collecting reservoir features; feature collection took 44.81 seconds for training and 7.22 seconds for validation. The Transformer did not have this feature-precomputation phase; its training-loop time was approximately 3.86 seconds. These numbers are not interchangeable end-to-end speed measurements. The same readout-size budget is not imposed on the Transformer; parameter counts are disclosed above. The generation latency includes prompt processing and output generation, but excludes graph/checkpoint loading and judging.

## What the model actually emitted

For Two Sum, the fly's 384-byte output began:

```text
def solve(nums):
    return solve(nums):
    return solve(nums):
    return solve(nums):
```

This is invalid Python. All six fly candidates and all six no-recurrence candidates reached the 384-byte cap and failed syntax checks. The Transformer produced three invalid programs and three empty outputs; the latter are classified by the current judge as `unsupported` because no `solve` function was present. None passed a complete task suite. Raw outputs and detailed verdicts are in the respective `*-evaluation.json` files; no output was edited to make it pass.

The descriptive Wilson 95% interval for 0/6 is approximately 0–39%. With six deliberately selected tasks and one seed, this is not a population-level estimate of general LeetCode performance. The suite is original LeetCode-style text, not official LeetCode submissions or an established standardized benchmark.

## Did the graph help?

There is no demonstrated benefit in this run. The fly and no-recurrence models generated **byte-identical code on all six tasks**. Their validation losses also differed by only about 0.000245 nats/target at the selected checkpoint. This is not a statistical significance test.

A post-pilot diagnostic on the **training** prompt `sum-two` measured:

| Quantity | Value |
|---|---:|
| Frozen global count conversion gain | 0.000007504002 |
| Mean absolute recurrent input | 0.0001036033 |
| Mean absolute byte input | 0.2747753972 |
| Recurrent/input magnitude ratio | approximately 0.0377% |

The conservative maximum-row normalization leaves recurrence very weak for this probe. The graph was still loaded and multiplied on every fly step; all 165,122 traced neurons and 25,563,197 recorded directed edges were retained. A graph participating numerically is not evidence that its structure contributes useful information. These diagnostics are saved separately and were not used to alter or rerank the scored run.

## Verification and remaining work

32 tests passed, covering graph direction and preservation, checksum failures, causal masking, training/test family separation, judge correctness and boundaries, and local HTTP-handler behavior without binding a port. Official object MD5 headers matched both local raw sources. Sixteen captured artifacts and all captured source-file hashes matched their run receipts. Reloading the saved fly checkpoint through the platform's actual interactive backend reproduced the Two Sum output byte-for-byte and returned the same verdict. See [verification.json](verification.json) and [source-verification.json](source-verification.json).

The managed environment denied the local server's socket bind and terminated installed Chrome, so browser rendering, responsiveness and real HTTP transport remain unverified. The self-contained [results page](../flycodes.html) has actual embedded artifacts and disabled execution controls; the live platform can be launched outside that restriction.

Next, define a new development protocol that first tests learnable syntax and short-memory tasks, broadens the training corpus, and explores better recurrent/input scaling using validation data only. Run multiple seeds, establish a real pretrained reference, and use fresh held-out tasks for confirmation. Do not repeatedly tune against these six now-exposed tasks and then present an improved score as a clean test result.
