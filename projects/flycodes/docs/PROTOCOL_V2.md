# Expanded curriculum protocol v2

Recorded before any v2 model training or candidate evaluation. The pilot-v1 records remain intact. This is a development experiment, not a preregistered external study. No hosted LLM calls are authorized for this stage; the comparison is deferred as requested.

## Evidence behind changes

The previous model had very weak recurrent drive, almost identical to its no-recurrence control. Fixed reservoirs require calibration of recurrence, input scale and leaking rate; see Mantas Lukoševičius, *A Practical Guide to Applying Echo State Networks* (2012), author copy: https://mantas.info/get-publication/?f=Practical_ESN.pdf . Spectral-radius scaling is a practical configuration technique, not by itself a proof of the echo-state property. We estimate the positive count matrix's dominant eigenvalue by power iteration and record convergence. A shared global gain changes the model's count-to-current conversion, never topology or individual raw count ratios.

The earlier state also forgot problem information while emitting an answer. Encoder–decoder conditioning motivates explicitly retaining a representation of the input throughout generation: Cho et al. (2014), https://arxiv.org/abs/1406.1078 . Here the context is the mean and last pooled reservoir state of the **prompt only**, retained as fixed auxiliary memory. No answer state enters the context. This is a proposed engineering adaptation, not a reproduction of Cho's trainable RNN or evidence of a biological mechanism.

Use a nonlinear feedforward readout to learn interactions between prompt context and current state. Bianchi et al., *Bidirectional deep-readout echo state networks*, https://arxiv.org/abs/1711.06509 , provides precedent for trainable nonlinear readouts of fixed reservoirs in time-series classification. Our code generator is unidirectional and causal; we do not claim that paper established code generation. The external readout is larger than v1 and its contribution must be controlled.

Use a simple lossless lexical tokenizer trained on **training text only**, with UTF-8 byte fallback. This shortens code trajectories and preserves exact text. It is not BPE or a pretrained language model. Sennrich et al. (2016), https://arxiv.org/abs/1508.07909 , motivates the broader tradeoff between token granularity and open-vocabulary text; it does not validate this particular tokenizer. Fixed sine/cosine output-position features add an explicit decoder clock. All v2 arms receive the same clock, context mechanism and head.

## Data and scope

Google Research's MBPP is described in Austin et al. (2021), https://arxiv.org/abs/2108.07732 . Official split definitions: https://github.com/google-research/google-research/tree/master/mbpp . Dataset attribution: Austin et al./Google Research; CC BY 4.0. Downloaded full source is SHA-256 pinned in `data/curriculum-v2/manifest.json`; original ID assignments are retained.

The current bounded judge supports a subset of Python. Curation retains a single function with literal JSON-compatible equality tests, which passes all provided reference tests without imports, helper definitions, recursion, or unsupported constructs. Renaming the entry point to `solve` and AST formatting are documented transformations. All exclusion reasons are saved. Exact canonical code and description duplicates are removed with test > validation > train priority. This does not remove all semantic overlap.

Resulting corpus: 134 MBPP training tasks, 100 authored parameterized exercises and 12 original elementary training examples (**246 total**, compared with 12 before). Validation: 40 MBPP + 20 authored examples. The 209 eligible official-test tasks remain separate; a deterministic sample of 24 will be fixed in the run configuration before training for this bounded run. No model is selected from their results. Thirty unseen-constant exercises are a secondary transfer set, explicitly labeled seen-template interpolation, not new algorithm generalization. The old six exposed pilot tasks are not used for a fresh headline result.

All retained reference programs are executed by the bounded interpreter during curation, before model training. Passing these tests validates the dataset/harness compatibility, not model performance. MBPP has only its supplied tests here; no claim of complete functional verification is made.

## Model and selection

Retain every traced neuron and all recorded edges including weak edges and self-edges. Frozen count matrix; fixed input mapping and 768-dimensional signed pooling; one scalar state per neuron. The v2 output feature is current pooled state + mean prompt state + final prompt state + 16 clock features. The learned head has two hidden layers of width 384 with GELU. No raw prompt bypass or reference-code lookup is available to the model. The context buffer and learned head are artificial components, not fly anatomy.

Calibrate three declared recurrence settings on a fixed subset of 64 training examples and 16 validation examples only: (a) old maximum-row scaling, leak .5, input scale .35; (b) spectral target .9, leak .5, input .1; (c) spectral target .99, leak .2, input .1. Each trial gets 400 readout updates. Choose the lowest full calibration-validation next-token cross entropy. Training states may be cached because everything producing them is frozen. Record every trial, including failures. The chosen setting is not guaranteed to amplify useful task information.

On the full expanded training set, compare the selected fly reservoir against a separately trained no-recurrence control with identical input mapping, leak, context, head architecture, exposure count and optimization. Use two readout initialization seeds (7 and 19) with the same fixed reservoir/input seed 7; these test output-optimization variability, not independently sampled brains or reservoir encodings. Each fit gets 1,600 minibatch updates of 512 solution-token/EOS targets with AdamW at .001 and gradient clipping. Cache states once and reuse across head seeds. Report actual parameter counts, cache time and optimization time separately.

Checkpoint choice: minimum full validation next-token loss. At inference use one greedy program, max 192 generated tokens / 2,048 UTF-8 bytes, no syntax repair, test feedback, search, retrieval or reranking. All arms receive identical problem statements and limits. Save checkpoint hashes, source snapshot, data hashes, raw programs, stop reasons, per-test verdicts and activity traces.

## Interpretation

Score training reproduction, unseen-constant transfer, and fresh sampled MBPP test results separately. Report failures and empty outputs. An untrained readout's selected-task predictions supply a learning baseline. A trained generator must pass functional tests to support a coding-performance claim. Improvement against initialization does not establish a fly-connectome advantage; the separately trained no-recurrence control is required for that attribution. Two head seeds and a small filtered test sample cannot establish broad LeetCode capability. The pretrained LLM baseline remains not run.

If v2 still fails, retain the negative result. Further changes require another recorded development revision and fresh final-test evaluation boundaries. Do not silently replace the generator with retrieved solutions, a larger external language model, or a handwritten algorithm selector.
