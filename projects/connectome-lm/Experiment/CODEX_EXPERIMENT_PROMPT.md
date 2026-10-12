# Codex experiment prompt: Does fly-connectome wiring help a language model learn?

You are my research engineer. Implement a reproducible, local-first experiment, not merely a proposal. Build working code, tests, configuration files, data provenance, analysis tools, and a report generator. Use the staged execution policy below: implement the complete pipeline, run correctness tests and a bounded smoke test, and provide explicit commands for larger experiments. Never invent measurements or call an unrun experiment successful.

## 1. Scientific question and boundaries

Research question: At a fixed training-data budget, does a recurrent language model constrained by real MaleCNS connectivity predict unseen text better than an otherwise identical model with degree-preserving randomized connectivity?

The model must learn language from scratch. Its pipeline is:

    UTF-8 bytes -> learned byte embeddings -> trainable graph-constrained
    recurrent network -> small linear readout -> next-byte probabilities.

Do not use a pretrained language model, pretrained embeddings, distillation, a hosted text-generation API, a frozen language backbone, or a transformer that can bypass the graph. In the main condition, recurrent weights INSIDE the fly-derived graph must receive gradients and change during training.

This is an artificial architecture experiment, not a physiological brain simulation. A model node corresponds to a reconstructed neuron only for connectivity bookkeeping. Tanh states are not measured membrane voltages; a model step is not a biological time interval; gradient descent is not a claim about how flies learn. Arbitrary text interfaces are engineering choices, not olfactory or language organs. Do not call this an emulated fly, a recovered memory, or a large language model. Describe it as a small connectome-constrained language model.

Use a neuron-level subnetwork for the first experiment. Do not claim it is the whole brain or whole CNS. Do not silently substitute a type-level aggregate graph, a female specimen, or synthetic data. The question is whether this particular structural prior helps under these conditions, not whether flies understand language.

Before training, create `docs/analysis_plan.md` containing hypotheses, extraction rules, conditions, seeds, hyperparameter selection, budgets, metrics, and interpretation rules. Save its SHA-256 and Git revision. This is a timestamped local analysis plan; do not describe it as publicly preregistered unless I actually register it externally.

## 2. Primary hypothesis and outcome

Primary comparison: FLY-TOPOLOGY versus DEGREE-REWIRED.

Primary metric: test negative log-likelihood in bits per byte (BPB), computed as total natural-log cross-entropy divided by the number of scored bytes and by ln(2). Lower is better. Byte perplexity is 2**BPB; do not compare it directly with word- or subword-token perplexities.

For each training seed, define:

    delta = mean(BPB of its rewired controls) - BPB of the fly model.

Positive delta favors the fly topology. Predeclare 0.02 BPB as a chosen practical-effect threshold, not a biological constant. Report effect estimates and uncertainty rather than selecting whichever metric looks favorable.

A fly model generating plausible fragments or beating an untrained network does not establish that its wiring helps. That requires the controlled comparison.

## 3. Inspect the environment and protect the workspace

Inspect the existing repository, instructions, Python environment, CPU, RAM, free disk, and available accelerators. Preserve unrelated files. Work in a new `fly_connectome_lm` directory unless an existing project clearly provides the appropriate destination.

Use Python and PyTorch, with NumPy, SciPy, PyArrow, NetworkX for SMALL extracted graphs, pytest, and matplotlib. Use the existing dependency manager when reasonable; otherwise create an isolated virtual environment. Pin the versions actually installed and record OS, hardware, backend, precision, and deterministic settings. Do not assume that a package version or sparse backend supports an operation: test it.

Do not purchase services, launch paid cloud jobs, publish the repository, upload data, or change credentials. Never log tokens. Support CPU. Use CUDA or Apple MPS only after forward/backward checks pass; keep a tested CPU fallback. Do not silently change device or precision for only one arm of a comparison.

Create a short project `AGENTS.md` recording the experiment's invariants and telling future sessions to read this specification. Do not put the entire specification into AGENTS.md. Track progress and limitations in `docs/STATUS.md`.

## 4. Authoritative data and provenance

Use these starting sources, verifying their current contents and then pinning the selected release:

MaleCNS catalogue:
https://male-cns.janelia.org/download/

Release used for this protocol:
    male-cns:v1.0

Official bulk directory:
    gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/

Needed files listed in the catalogue:
    body-annotations-male-cns-v1.0-minconf-0.5.feather
    connectome-weights-male-cns-v1.0-minconf-0.5.feather

The catalogue lists approximately 13 MB and 1.1 GB respectively. The connectivity file covers segments, not only the curated neuron population. Follow the catalogue's actual links instead of guessing endpoints or schemas. These two products are enough for this experiment; do not download microscopy, skeletons, meshes, all synapse coordinates, or neurotransmitter tables.

Cache downloads, verify HTTP failures, use atomic writes, record file size, retrieval time, exact source URL, SHA-256, release, licence/attribution, and schema. Check disk and memory before acquisition. Set a default raw-download ceiling of 2 GB; stop with an actionable message if the current files exceed it. A content hash records what was downloaded; it does not prove provenance by itself.

Inspect the actual columns. Construct a canonical directed edge table:

    source_body_id, target_body_id, synapse_count

and a canonical curated-neuron table keyed by body ID. Preserve original IDs losslessly as integers or strings. Never round them through floating-point conversion. Document column mappings and direction explicitly.

Filter edges so BOTH endpoints occur in the curated neuron inventory, excluding explicitly marked non-neuronal/error entries where the metadata supports that distinction. Record each exclusion and unresolved classification. A missing type label alone is not grounds to invent a cell identity or discard a valid neuron.

Verify whether the source is already aggregated by ordered pair. Do not sum a whole-neuron total together with its regional breakdown. Resolve duplicate records using the documented schema; stop on unresolved ambiguity. Preserve the raw contact counts. They are anatomical counts, not measured physiological weights.

Process the large file with memory mapping/batches and compact arrays or CSR structures. Do not turn the entire multi-million-edge graph into Python NetworkX objects. Retain only the columns required for extraction.

If official data cannot be obtained, allow synthetic data ONLY under an explicit `--synthetic --smoke` mode. Mark every resulting artifact synthetic. Scientific runs must refuse a synthetic graph. Do not silently replace real data to complete a demonstration.

## 5. Predeclared neuron-level subgraph extraction

Initial research size: 512 nodes. A 64-node graph is allowed only for software smoke tests. Offer 1,024-node scaling as a separately named follow-up, not an automatic change to a started experiment.

Apply this task-independent extraction procedure:

1. Filter to curated endpoints and ordered-pair synapse_count >= 5. This threshold is an experimental choice. Remove anatomical self-edges and report how many were removed.
2. Find the largest weakly connected component, using the graph with direction ignored only for sampling. Resolve size ties deterministically.
3. Select a starting node uniformly using an explicit sampling seed. Perform breadth-first expansion with neighbors shuffled reproducibly. Do not weight selection by language performance or contact count. Stop after 512 distinct nodes.
4. Recover the INDUCED DIRECTED graph: include every retained directed edge whose endpoints are both selected. Do not keep only the discovery tree, symmetrize edges, or add reverse connections.
5. Sort original IDs to create a stable model-index mapping. Save nodes, edges, mapping, extraction configuration, and checksums.

Keep the output even when it is not strongly connected; report that property rather than quietly replacing it with a better-performing graph. Fail clearly if the specified size cannot be obtained.

Save N, E, density, per-node incoming/outgoing degree, degree distributions, contact-count distribution, weak/strong components, reciprocity, and node classes where available. Report how much of the selected neurons' filtered incoming/outgoing connectivity is lost to nodes outside the subset.

Sampling a local connected neighborhood biases the circuit sample. State this explicitly. The pilot uses sampling seed 101. The replication profile uses seeds 101, 202, and 303; these are samples from ONE specimen, not three independent animals. Report overlaps between samples.

Do not select graph samples, anatomical regions, or node counts by held-out language results. This experiment does not need NBLAST or geometric registration because it tests connectivity, not morphological correspondence.

## 6. Text data, byte encoding, and leakage prevention

Primary corpus: Tiny Shakespeare from its original repository:
https://github.com/karpathy/char-rnn/blob/master/data/tinyshakespeare/input.txt

Resolve and record an immutable repository revision and raw-file checksum. Treat it as a small public-domain-text benchmark, not as general language coverage. Preserve the exact downloaded bytes; document any transformation rather than silently normalizing text.

Use the fixed vocabulary 0..255, one token per UTF-8 byte. This requires no pretrained tokenizer and has no unknown-token problem. Do not use test text to construct a vocabulary.

Split bytes CONTIGUOUSLY before making windows: first 90% training, next 5% validation, final 5% test. Record exact byte offsets and split hashes. Never randomly split already-overlapping windows. Never let a window or hidden state cross a split boundary.

Report exact duplicate spans of at least 256 bytes across splits without printing long text. Repeated material can limit interpretation even with correct contiguous splitting. Do not remove inconvenient spans after seeing results; create a separately labelled sensitivity analysis if needed.

Use length-128 next-byte prediction in research runs. A training example takes 129 consecutive bytes; the first 128 are inputs and the last 128 shifted by one are targets. Sample training windows with a reproducible RNG, resetting hidden state for every independent window. Log both unique corpus size and cumulative training-byte exposures.

Evaluation must be deterministic. Partition each split's input/target pairs into consecutive, non-overlapping blocks of at most 128 prediction positions, reset state at every block, and score each target byte after the split's first byte exactly once. Include a masked shorter final block. No random validation batches for final reporting. All architectures receive the same evaluation contexts and scored positions.

Validation may guide tuning. The test loader must be inaccessible to training/tuning commands and activated only by an explicit final-evaluation command after configuration freeze. No checkpoint selection or architecture revision based on test results.

Optional independent-corpus replication: Project Gutenberg ebook 11, Alice's Adventures in Wonderland:
https://www.gutenberg.org/ebooks/11

Fetch its actual UTF-8 link, remove only documented Gutenberg wrapper sections, preserve the source and processed hashes, and create independent 90/5/5 splits. Retrain from scratch with the locked protocol. Do not call this independent replication merely because the Shakespeare-trained model is evaluated on Alice.

## 7. Main recurrent architecture: trainable edges, fixed topology

Let N be the selected neuron count, d=32 the embedding/readout width, and V=256.

Train these parameters:
    embedding E: [256, d]
    input matrix B: [N, d], without its own bias
    one recurrent scalar theta per allowed directed edge
    recurrent bias b: [N]
    readout projection R: [d, N], without bias
    output matrix O: [256, d]
    output bias c: [256]

Construct W so W[target, source] is theta for a source -> target edge, with all unobserved entries EXACTLY zero. For a minibatch, use the equivalent batched implementation of:

    x_t = E[byte_t]
    proposal_t = tanh(W @ h_previous + B @ x_t + b)
    h_t = (1-alpha) * h_previous + alpha * proposal_t
    logits_t = O @ (R @ h_t) + c

Use alpha=0.5 fixed in the primary protocol. The identity term is an engineered state-retention rule, not an additional reconstructed autapse. One recurrent update per byte; initial state is zero. No trainable initial state.

Every trainable recurrent edge is optimized by backpropagation through time. The connectivity mask is a nontrainable buffer. Store only E_edge independent recurrent parameters, not an N*N parameter array with hidden unused optimizer states. A differentiably assembled dense matrix is permitted for small N, but absent edges must not become trainable.

No hidden attention, dense recurrent layer, cross-node LayerNorm, batch-dependent global normalization, convolution across nodes, bidirectional pass, or shortcut from embeddings to logits. Such operations would change the tested information-flow constraint. The intentionally dense input/output interfaces must be documented and identical in all matched graph conditions.

In the primary experiment, use topology ONLY after the predeclared contact-count threshold. Do not use synapse counts for initial magnitudes or impose predicted neurotransmitter signs. Signed learned weights are artificial task parameters.

Initialize each target's incoming allowed weights from seeded zero-mean random numbers, normalizing its nonempty row to L2 norm 0.9. Zero-indegree rows stay zero. Use the SAME incoming-slot random numbers for corresponding target rows in fly and degree-rewired models. Since their per-node degrees match, row norms and initial per-row weight multisets can match exactly while partners differ. Share input/output initialization across each matched pair. Initialize biases to zero; document the other initialization rules.

Record initial and learned weight distributions, row norms, estimates of spectral scale, activation saturation, and gradient norms. Spectral diagnostics are descriptive in the primary study; do not silently normalize one arm differently after seeing its behavior.

## 8. Required experimental conditions

Implement these five conditions using the same data protocol:

A. FLY-TOPOLOGY: real extracted directed adjacency; train allowed recurrent weights and interfaces.

B. DEGREE-REWIRED: the same labelled nodes, same edge count, and exactly the same incoming and outgoing degree for EVERY node, with partners randomized. Same architecture, interfaces, initialization scheme, trainable-parameter count, optimizer, and training examples as A. This is the primary control.

C. RANDOM-DENSITY: a uniformly sampled loop-free directed graph with exactly the same N and E, but without preserving node degrees. Same architecture and parameter count. This is a secondary test of generic sparsity versus specific degree organization.

D. PARAMETER-MATCHED GRU: a conventional one-layer causal GRU language model, trained from scratch. Keep byte vocabulary, sequence contexts, embedding width, and readout rank fixed where appropriate. Choose hidden width by actual active trainable-parameter count to within 5% of A, without looking at validation scores to choose width. Report any mismatch; never add unused parameters to fake matching.

E. NO-CROSS-NODE RECURRENCE: same interfaces and N scalar states, replacing graph communication by an independently trainable diagonal coefficient for each state. Keep the leak rule. This tests whether dense interfaces and independent memory units explain performance without inter-neuron wiring. Its lower parameter count is part of an ablation; do not call it parameter matched.

Also support, but do not make prerequisites for the first pilot:

F. A small causal decoder-only transformer matched within 5% of active parameter count, selected by parameter counting rather than validation performance. No pretraining, same bytes and 128-position contexts, no extra training data. Record its different compute cost.

G. FROZEN-FLY: freeze initially random graph weights but train the same interfaces. It diagnoses the role of learning the recurrent core; its trainable-parameter count differs and must be reported.

Include train-only smoothed unigram and bigram predictors as sanity references, not as supposedly parameter-matched neural baselines.

## 9. Correct graph randomization

Use a directed degree-preserving randomization method. NetworkX's documented directed_edge_swap uses directed three-edge swaps; do not accidentally call its undirected double_edge_swap.

Reference:
https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.swap.directed_edge_swap.html

Generate a fresh rewired graph for each specified null seed, starting from a copy of the real graph. Default to 20*E accepted swaps, with at most 500*E proposals/attempts; record what the implementation actually counts. Preserve loop-free/simple-graph constraints and verify exact per-node in/out degrees afterward. Do not confuse attempted swaps with accepted swaps.

Record overlap with the original graph, reciprocity, components, and other diagnostic changes at intermediate checkpoints. High-density degree sequences can force substantial overlap. Do not assert that a fixed number of swaps proves uniform sampling or perfect mixing. If the routine cannot satisfy its declared policy, mark that control invalid and explain; do not silently use the unchanged graph.

Do not reject nulls because they train poorly. Connectivity can change under degree-preserving swaps, so report components rather than claiming the null preserves everything. Connectivity-matched randomization can be a separately labelled sensitivity analysis if that difference matters.

A consistent permutation of node labels is NOT a random-topology control: it leaves an isomorphic graph. Instead use it as an implementation-invariance test, transforming graph weights, states, biases, and input/output axes together and checking equivalent predictions.

## 10. Separate experiment on anatomical contact counts

Only after the topology pipeline works, implement an optional initialization study on the SAME real graph:

    UNIFORM: the primary random row-normalized initialization.
    COUNT-INIT: multiply the same initial noise by log(1+synapse_count),
                then renormalize each incoming row to the same L2 norm.
    SHUFFLED-COUNT-INIT: permute contact counts among incoming edges
                        of each target, then use the identical rule.

This shuffle preserves each target's count multiset and incoming total, but not every source's weighted outgoing total; report that limitation. All three have identical learnable parameters and unrestricted learned signs.

This tests whether the placement of anatomical counts helps INITIALIZATION. It does not impose biological synaptic strengths throughout training. With freely learned weights, a fixed multiplicative scaling is largely a parameterization/optimization choice, not a new function class. Keep this result separate from the topology hypothesis.

## 11. Training, tuning, and parameter accounting

Use cross-entropy and AdamW, gradient clipping at global norm 1.0, no dropout in the main graph models, and zero weight decay initially. Report all optimizer settings. Default learning rate 0.001 for smoke/pilot implementation checks; do not claim it is universally optimal.

Before confirmation, allow a fixed development grid of learning rates {0.0003, 0.001, 0.003}, with the same update and validation budget for each trial. Select ONE common learning rate for A/B/C/E by pooled validation performance on A and B using development-only training seeds 901 and 902, then lock it. Conventional architectures may choose their learning rate from the same-size grid under the same trial budget. Do not give the fly model extra tuning or select the best of many fly variants against an untuned baseline.

Keep development training seeds separate from reported confirmation seeds. Development may use validation but never test data. After inspecting pilot test results, any revised hypothesis requires a new labelled study; avoid opening that test during the pilot by default.

For paired graph arms, use identical minibatch-window sequences, effective batch size, update count, contexts, optimizer, precision, and evaluation schedule. Separate RNG streams for graph sampling, rewiring, initialization, data order, and sample generation. Log their derivation. Randomize or alternate run order to reduce hardware-order bias.

Every run must report total parameters, active trainable parameters, recurrent-edge parameters, interface parameters, and nontrainable graph storage. Verify parameter matching with executable assertions. A mask alone does not justify pretending an unused dense parameter tensor costs nothing.

Train every run to the full declared budget; do not stop weak baselines early while giving the fly model all its updates. Save final and best-validation checkpoints. Primary evaluation uses the best-validation checkpoint found within the fixed budget; also report final-checkpoint results separately. The full budget still counts as consumed. Validation frequency must match across arms.

Stop and record nonfinite losses, backend errors, or out-of-memory failures. Do not hide failed seeds or silently fix just one condition. A changed training recipe creates a new experiment revision.

## 12. Resource profiles and execution policy

Implement configuration presets:

SMOKE:
    64 nodes; d=16; context=32; batch=2; 20 updates;
    one seed; synthetic or real explicitly identified;
    all required conditions, no statistical claims.

PILOT:
    512 nodes; d=32; context=128; batch=4; 2,000 updates;
    one graph sample; training seeds 1, 2, 3;
    one independently rewired control per training seed;
    five required conditions; validation-only comparisons.

CONFIRMATION:
    512 nodes; d=32; context=128; batch=8; 20,000 updates;
    one fixed graph sample initially; training seeds 11,22,33,44,55;
    three independent rewired controls per training seed;
    five required conditions; explicit final-test evaluation.

REPLICATION:
    the confirmation design repeated on sampling seeds 101,202,303,
    and optionally on the independently split Alice corpus.
    Reuse completed seed-101 confirmation runs rather than duplicating them.

These budgets are chosen starting specifications, not promises of runtime, convergence, or statistical power. Print the exact run matrix, training-byte exposures, memory estimate, and storage estimate before launching a sweep. Reuse the already trained real graph run when comparing it to its three nulls; do not count the reused run as three independent samples.

During this initial Codex task, run unit tests and a bounded smoke test. Run a real-data smoke test when acquisition and hardware permit. Do NOT automatically launch the pilot, confirmation, replication, paid compute, or an unattended background process. Implement and print their commands. Do not leave training running after reporting completion.

If a chosen preset exceeds local resources, emit a smaller explicitly named preset and report the changed scope. Never silently reduce only a baseline's capacity or token budget. Research results from different presets must not be merged as matched comparisons.

## 13. Backend correctness and efficiency

Provide a small dense-reference implementation and a graph implementation using a parameter vector plus sparse multiplication or gather/scatter. A differentiably assembled dense W is acceptable at N=512 when it is faster and the parameterization remains genuinely edge-restricted.

Reference:
https://docs.pytorch.org/docs/stable/generated/torch.sparse.mm.html

Test logits, loss, hidden states, and recurrent-parameter gradients against the dense reference on a tiny graph in float64 on CPU. Then run forward/backward tests on the actual selected device. Do not assume sparse CUDA/CPU support implies sparse MPS support. Avoid per-node/per-edge Python loops; sequence-time loops may be necessary.

Do not construct a dense whole-CNS matrix. Use the SAME tested implementation for matched graph arms. Log sparse/dense execution separately from the number of learned parameters. Synchronize accelerators when measuring elapsed computation. Report graph initialization, compilation, validation, and preprocessing costs separately from training.

## 14. Two distinct fairness protocols

Primary protocol is FIXED TRAINING BYTES: all arms see the same number of prediction targets and the same contexts. A/B additionally match N, E, interfaces, and parameter count exactly. Record elapsed time, throughput, peak memory, and operation-count estimates.

Secondary protocol is FIXED TRAINING TIME on the same device: choose a time budget from the pooled development profiling before test access and run all arms under it. Log actual updates and training bytes. Include equivalent validation schedules or exclude validation consistently from the training-time meter, reporting its cost separately.

Do not state that equal parameter count means equal FLOPs or wall time. Across GRUs, transformers, and sparse recurrence, parameter count, byte exposures, and compute cannot generally all be matched simultaneously. Present the two protocols separately rather than claiming a single perfectly compute-matched ranking.

## 15. Mandatory correctness tests

Tests must cover:

- Source -> target orientation with a hand-checkable tiny graph.
- Dense/graph forward AND backward equivalence.
- Absent recurrent edges remaining exactly absent after optimizer steps.
- Nonzero recurrent-edge gradients and an actual change in trained core weights.
- Identical outputs after a consistent complete node relabeling.
- Exact per-node incoming/outgoing degree preservation for rewired controls.
- Rewired graphs actually changing partners, subject to documented constraints.
- Matched parameter counts and no unused parameter padding.
- Exact split/window boundaries, shifted next-byte targets, and tail masking.
- Causal prefix invariance: changing future input cannot change earlier logits.
- Hidden-state reset and no crossing of train/validation/test boundaries.
- Byte encoding/decoding and BPB/perplexity arithmetic on known probabilities.
- No use of the test loader by tuning/training code.
- Checkpoint/resume equivalence on CPU, including optimizer, RNG, and data position.
- A tiny synthetic sequence overfit test validating that training works at all.
- Explicit rejection of synthetic graphs in non-smoke scientific runs.

Do not mark unsupported accelerator tests passed; mark them skipped with reasons. Tests are necessary checks, not proof that every implementation is correct.

## 16. Evaluation and uncertainty

Report each run's test BPB, byte perplexity, next-byte accuracy, training/validation curves, selected checkpoint step, total training-byte exposures, elapsed time, throughput, peak memory, seed values, graph hash, and config hash. Metrics must come from real logs/checkpoints.

For each training seed, average its three rewired test scores, then subtract the single fly score. Bootstrap these PAIRED seed-level differences, not individual test bytes or repeated uses of the same fly run. Use 10,000 resamples and a 95% interval, while explicitly flagging that five training seeds provide limited uncertainty estimation.

For multi-subgraph replication, preserve the graph/seed hierarchy and also show every graph separately. Graph samples can overlap and come from one specimen; do not present a hierarchical interval as population-level evidence across flies. Retain all run-level values so another analyst can inspect the dependence.

Use the predeclared topology contrast as the primary result. Other architectures, count initializations, graph diagnostics, and memory probes are secondary/exploratory. Do not run many comparisons and report only the favorable one. If hypothesis tests are added, predeclare them and account for multiplicity.

Interpretation:
    Interval entirely above +0.02 BPB: evidence of a practically meaningful
    advantage under the specified experiment, still requiring replication.
    Positive estimate with a wide interval: inconclusive.
    Small narrow differences: no substantial advantage established here.
    Negative estimate: the fly wiring may be worse for this task/protocol.

A failure to reject zero is not proof of equality. Even a positive result does not establish biological language ability, consciousness, whole-brain emulation, or superiority to large pretrained models.

## 17. Diagnostics after the main experiment

Support validation-set diagnostics without changing primary test selection: zero the trained recurrent core, reset recurrent state every byte, and perturb a controlled fraction of learned edges. Report how predictions change. These are interventions on the ARTIFICIAL model, not experiments on a living fly. Parameter destruction can harm any trained model, so these are dependence checks, not proof of a special connectome benefit.

Generate short text samples from fixed training-only prompts with identical temperature, length, and sampling seeds. Select prompts before seeing model outputs; include samples from all compared arms. Treat them as illustrations, never the primary metric. Do not print long source passages or rely on selected impressive examples.

Produce separate plots for BPB versus training bytes, BPB versus elapsed training time, paired seed-level effects, parameter/memory/time accounting, graph degree distributions, and optional anatomical-count ablations. Label smoke, pilot, and confirmation results unmistakably. No fabricated result tables, significance stars, or decorative dashboards in place of evidence.

## 18. Repository and deliverables

Use a modular layout resembling:

    README.md
    AGENTS.md
    pyproject.toml
    dependency lock file
    configs/{smoke,pilot,confirmation,replication}.yaml
    src/fly_connectome_lm/
        data_download.py
        graph_extract.py
        graph_controls.py
        text_data.py
        models/{graph_rnn,gru_lm,diagonal_lm,transformer_lm}.py
        train.py
        evaluate.py
        statistics.py
        report.py
        cli.py
    tests/
    docs/{analysis_plan,DATA_SOURCES,METHODS,STATUS,LIMITATIONS}.md
    data/raw/              # ignored by Git
    data/processed/        # with manifests
    runs/                  # immutable per-run IDs
    reports/

Paths can change for a genuine engineering reason, but preserve the separation of acquisition, preprocessing, models, training, evaluation, and analysis. Keep checkpoints and large data out of Git. Use typed functions, input validation, informative errors, resumable downloads/runs, and atomic checkpoint writes.

Provide a CLI, with README examples covering:

    environment inspection
    data download and schema inspection
    graph extraction and control generation
    tests and smoke execution
    profiling and run-matrix dry run
    validation-only pilot
    hyperparameter/configuration freeze
    confirmation training
    explicit sealed-test evaluation
    report generation and checkpoint resumption

Make `--dry-run` list exactly what will execute. The report generator must render an honest incomplete report when only smoke runs exist, rather than creating empty final conclusions. Include full commands, code revision, data and graph hashes, conditions, failures, and limitations in every completed report.

## 19. Implementation order and final handoff

First inspect the workspace and write the plan/invariants. Then build the tiny graph model, byte data pipeline, and numerical tests. Add authoritative data acquisition and graph extraction. Implement matched controls and baselines. Add training/resume, metrics, uncertainty tools, and report generation. Execute tests and the bounded smoke run, fix failures, and update STATUS.md.

Do not stop after writing architecture notes. Deliver working code as far as tools and access permit. When blocked by authentication, data availability, memory, package support, or execution limits, name the blocker precisely and preserve completed work. Do not fake completion, fabricate data, or substitute a different scientific experiment.

Finish by stating what files were created, what actually ran, which tests passed/failed/skipped, whether real MaleCNS data was used, the measured smoke results if any, and the single exact next command for the validation-only pilot. Clearly distinguish implemented functionality from experiments already executed. Do not promise background work.

## 20. Research context and source handling

The general precedent of optimizing unknown parameters under connectome constraints is:
https://www.nature.com/articles/s41586-024-07939-3

That study concerns fly visual computations, not evidence that fly wiring improves language modeling. Cite it as methodological context, not as confirmation of this hypothesis.

For persistent Codex project guidance:
https://developers.openai.com/codex/guides/agents-md/

Keep these references and the actual resolved dataset/software URLs in DATA_SOURCES.md. Record retrieval dates. Prefer original papers, official dataset pages, and package documentation over secondary claims. Do not claim novelty, publishability, a benchmark win, or a causal biological discovery merely because the pipeline runs.
