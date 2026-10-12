# A scientifically motivated next model

2026-10-09. Proposal following the measured [model backtrace](BACKTRACE_RESULTS.md). These are testable hypotheses, not promised coding improvements. The deployed model and recorded graph are unchanged.

## What should stay fixed

Keep the complete set of 165,122 traced neurons, all 25,563,197 directed edges, body-ID mapping and original count files. Preserve the original reservoir and no-recurrence baselines. Treat topology, measured synapse counts, assumed physiological efficacy and learned model parameters as separate objects.

A fixed topology can still support learned neuron time constants, thresholds, input mappings and positive gain factors on existing edges. That is a different experimental constraint from freezing every effective weight. Any such version must state exactly which parameters learn. It must not be described as the unmodified biological brain.

## Primary methods and how they apply

**Connectome-constrained, task-optimized dynamics.** Lappalainen et al., *Connectome-constrained networks predict neural activity across the fly visual system*, Nature (2024), [primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11525180/). Their visual-system model holds anatomical connectivity as a constraint while fitting cell-type-shared neuronal and synaptic parameters, with signs informed by transmitter/receptor evidence. This motivates learning a small set of physiological parameters instead of treating raw counts as complete weights. It is evidence for visual computation, not for programming or this whole-CNS dataset.

**Transmitter-aware simulation.** Shiu et al., *A Drosophila computational brain model reveals sensorimotor processing*, Nature (2024), [primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/). Their whole-brain model combines connectivity with predicted transmitter identity and is tested on sensorimotor behavior. This motivates using the annotations we already have, with explicit handling of missing/uncertain signs. It does not show that importing these annotations teaches coding.

**Memory and computational-capacity assays.** Dambre et al., *Information Processing Capacity of Dynamical Systems*, Scientific Reports (2012), [primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC3400147/). Their framework separates recoverable functions of an input history and the tradeoff between nonlinear computation and memory. Our selected-lag binary recall tests are a limited adaptation, not a full capacity estimate. Extend with independent copying, delayed XOR, bounded counting and numeric comparisons before requiring Python generation.

**Independent probes.** Alain and Bengio, *Understanding intermediate layers using linear classifier probes*, [primary paper](https://arxiv.org/abs/1610.01644). Separately fitted simple readers test whether task information is accessible in intermediate representations. Their success is evidence about representation, not automatically about what the original decoder uses. Our prompt probes follow this diagnostic principle.

**Reservoir calibration.** Lukoševičius, *A Practical Guide to Applying Echo State Networks* (2012), [author copy](https://mantas.info/get-publication/?f=Practical_ESN.pdf). Calibrate input scale, recurrent gain and leaking rate on validation tasks. Radius alone is not a universal stability or performance guarantee. The measured gain-only memory improvement motivates a broader, controlled sweep before retraining code heads.

**Grammar-constrained generation.** Scholak et al., *PICARD* (2021), [primary paper](https://arxiv.org/abs/2109.05093). Incremental parsing rejects inadmissible next tokens in text-to-SQL generation. For Flycodes, a bounded Python-expression/AST grammar could remove malformed syntax while the neural system must choose the operations, variables, constants and control flow. This is a proposed adaptation; grammar validity does not establish correct algorithms.

**Training/inference mismatch.** Bengio et al., *Scheduled Sampling* (2015), [primary paper](https://arxiv.org/abs/1506.03099), describes error accumulation when training supplies correct previous tokens while generation supplies the model's own tokens. Our traces expose early deviations. Scheduled sampling itself is not an automatic recommendation: [Huszár's analysis](https://arxiv.org/abs/1511.05101) identifies an inconsistent objective. First measure complete validation rollouts and consider explicitly defined sequence objectives, while retaining maximum-likelihood baselines.

## Controlled development stages

| Stage | Change or measurement | What it answers | Evidence required before advancing |
|---|---|---|---|
| 1. Primitive computation | Copy a value, retain several values, delayed comparison/XOR, count list events; direct outputs with no Python syntax | Can the current circuit retain and transform the required information? | Independent generated cases, multiple sequence/input seeds, learning curves and matched no-recurrence results |
| 2. Input and state access | Compare random input/pooling with trainable input adapters and cell-type-aware output pooling, one factor at a time | Is useful information reaching the recurrent network and decoder? | Probe accuracy and end-task gains; controls receive equally capable adapters and comparable trainable parameter budgets |
| 3. Dynamics | Validate gain/leak changes; then separately introduce transmitter-aware coefficients and cell-type-shared gains/time constants | Can the existing topology support more useful dynamics? | Stability, saturation, perturbation decay, primitive performance and clear sign-uncertainty policies |
| 4. Learning computational structure | Supervise operation, variable and literal choices; train a bounded expression/AST decoder | Can the model combine operations and copy the requested values? | Held-out constants, lengths and task compositions; report valid syntax and functional correctness separately |
| 5. Fresh coding evaluation | Freeze a chosen model and evaluate untouched problems | Does improved primitive computation transfer to coding? | Test-suite success on fresh independent tasks; controls, multiple seeds, source/checkpoint hashes and no test-based repairs |

The 24 MBPP tasks and 30 transfer examples already inspected are exposed development evidence. Never tune on them and rebrand their scores as fresh. Keep all new coding attempts separately versioned. A previously seen exercise is not a held-out algorithm result.

## Proposed parameterization, without rewiring

For an existing edge from j to i, derive its simulated efficacy from the recorded count, an evidence-based sign policy and a positive gain shared by an explicitly defined cell-type pair. Learn per-type time constants and thresholds with constrained ranges. No parameter can create an absent edge; original count arrays stay immutable. Preserving count ratios within a type-pair is one useful regularizer, not a biological certainty.

For signed networks, do not reuse the current positive-matrix power-iteration routine as an unquestioned stability certificate. Test driven stability and perturbation growth directly, and use appropriate signed-matrix spectral tools if needed. Fit sparse differentiable dynamics with bounded unroll lengths and gradient checks before a large run; the current NumPy state update does not propagate gradients into the core.

Known physiological signs should be fixed where supported. Unknown transmitter/receptor assignments require recorded alternatives or sensitivity analysis, not invented biological labels. Compare physiological modeling separately from performance-oriented architectural changes, because a model can become a better code generator while becoming less biologically plausible.

## Attribution and stopping rules

Keep a matched no-recurrence model and an independently generated topology control with similar degree/weight statistics. Store the latter only as a separate null model; never overwrite the fly dataset. A fly-specific advantage requires better held-out performance than these controls, not just higher training accuracy or visible activity.

Choose all model variants and stopping criteria using training/validation data. Record failures, total examples, exposures, seeds, parameters and compute. If primitive memory improves but code generation does not, report that distinction. If only the external adapter learns, attribute the success to the full system. Biological fidelity and coding performance are separate objectives.

The immediate next coding-model experiment should test the measured gain-only change and explicit operation/literal supervision under the same data and controls. Full physiological parameter learning is a larger subsequent implementation. None of the cited papers establishes that a fly connectome can acquire general LeetCode ability.
