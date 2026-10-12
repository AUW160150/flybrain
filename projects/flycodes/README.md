# Flycodes

A separate, local project that loads the complete **165,122 traced-neuron MaleCNS v1.0 graph**, preserves its **25,563,197 directed connections**, trains an external code readout, and records what its generated programs actually do. This is a connectome-constrained artificial network, not an emulated living fly.

The expanded **curriculum-v2** experiment uses **246 verified training examples**, 60 validation examples, a fixed 24-task sample from a judge-compatible MBPP test subset, and 30 separately labeled unseen-constant exercises. It tests calibrated reservoir dynamics, retained prompt context, a lossless lexical tokenizer and a nonlinear readout against a matched no-recurrence control, with two readout seeds. See [v2 results](docs/RESULTS_V2.md), [the pre-training protocol and references](docs/PROTOCOL_V2.md), and [the v2 log](docs/LOG_V2.md). The pretrained LLM comparison is deferred at the user's request; no API calls are made by v2 training.

**Measured v2 outcome:** both fly readout seeds scored **0/24 fresh MBPP tasks and 0/30 transfer exercises**, matching their no-recurrence controls. Seed 7 reproduced 1/8 seen training examples; seed 19 reproduced 0/8. Training loss decreased but did not produce general coding ability. A post-run boundary-test audit removed three false-positive transfer passes per seed-19 model; original and corrected evidence are both retained.

**Syntax-tolerant follow-up:** mechanical repairs made 25 fly outputs runnable across both seeds. One additional seen-training answer passed (seed 19, summing a list); no new-task success was verified. Ambiguous/incomplete programs remain unresolved. The [syntax audit report](docs/SYNTAX_AUDIT_RESULTS.md) and [full before/after evidence](docs/SYNTAX_AUDIT_EVIDENCE.md) retain all edits and outcomes. In the platform, select **After mechanical syntax repair** to inspect each interpretation. Original benchmark scores remain unchanged.

Historical pilot-v1: **0/6 held-out coding problems solved by the fly model**. The no-recurrence control and tiny Transformer also scored 0/6. Those original records are preserved. The v1 pretrained reference was unmeasured because authenticated requests failed DNS resolution. Its blank score is not zero.

Open [flycodes.html](flycodes.html) directly for the self-contained results platform, including the fly avatar, recorded neuron activity, actual generated code, scores and training curves. This saved view needs no server or external assets. To run new experiments, start the live platform from your terminal:

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flycodes
./flycodes.sh serve
```

Then visit **http://127.0.0.1:8765**. Flycodes defaults to its own port, 8765, which was unused when checked. You can select another port with `./flycodes.sh serve --port 8766`. The initial build's managed environment blocked socket binding and browser launch; its verification limits remain recorded in `docs/verification.json`.

If an older Flycodes server is already running, restart it in its original terminal to load the new Python modules: press Ctrl+C, run `./flycodes.sh serve --port 8765`, then refresh the browser. The interface identifies an outdated server explicitly and blocks unintended old-model attempts. The existing user-started process is left alone. The self-contained `flycodes.html` is regenerated from the latest completed curriculum run and does not require that restart.

## Model diagnosis and redesign

The [measured backtrace](docs/BACKTRACE_RESULTS.md) identifies weak recurrent influence, early operation/constant mistakes and overfitting. A gain-only experiment improved a separate delayed-bit memory task across three random streams, without changing any recorded edge. This is not a coding-score improvement. The [scientific redesign plan](docs/REDESIGN_PLAN.md) proposes fixed-topology dynamics learning and staged primitive-to-program evaluations, with primary references. Diagnostic artifacts are in `diagnostics/backtrace-20261009T180612/`; the live coding model is unchanged.

## Expanded curriculum commands

```sh
./flycodes.sh prepare-curriculum   # curate the downloaded, hash-pinned MBPP source
./flycodes.sh train-curriculum     # calibration, two head seeds, matched control, separate test sets
../../.venv/bin/python scripts/audit_curriculum.py  # recheck original programs; included automatically by train-curriculum
../../.venv/bin/python scripts/report_curriculum.py
../../.venv/bin/python scripts/export_snapshot.py
```

Data curation does not fetch a new mutable dataset automatically. The original download and immutable-commit copy are under `data/mbpp/`, with attribution, provenance, raw SHA-256 and original official task IDs. Exclusions and transformed references are recorded under `data/curriculum-v2/`. The subset is constrained by the bounded Python judge; its score must not be called a full MBPP score. Authored constant variants are familiar-template exercises, not independent new algorithms.

The UI shows fresh-test, transfer, and seen-training results in separate columns for each head seed. The fly and control receive the same external prompt memory, clock features, tokenizer and learned head. A program passing tests shows functional success for that complete model; a fly-specific contribution requires an advantage over the control. The core still has no trainable synaptic weights.

## Original pilot-v1, retained for reproduction

1. **Audit and map the data.** `./flycodes.sh prepare` reads `../../data/flat-connectome`. The first import has already run. It selects every `Traced` neuron, including isolated neurons, and retains all positive-count edges between them, including weak edges and 101 self-connections. There is no neuron subsampling or strength threshold. `data/graph/nodes.tsv` maps array indices back to exact integer body IDs. The manifest records hashes, source URLs, exclusions and raw counts. “167K” is an approximate published scale; the local selected count is shown honestly.
2. **Train a fixed-core pilot.** `./flycodes.sh train --seed 7 --steps 200` runs the full fly graph, a separate no-recurrence control and a small causal Transformer. It never changes the recorded wiring/count arrays. UTF-8 byte input and pooling are fixed; only the fly output layer learns. All models see 12 original training exercises and 89,800 solution-byte/EOS exposures. Checkpoints are selected on two validation exercises, never test scores.
3. **Inspect the evidence.** The live UI can load the graph, regenerate a held-out task, or accept a custom `solve(...)` problem. Custom prompts have no judge cases and are explicitly unscored. New interactive attempts are stored separately and cannot improve the original benchmark score. The avatar displays recorded or live state values from 80 sampled neurons at decorative positions, not real anatomy or a literal thought process.
4. **Run the optional pretrained reference.** With `OPENAI_API_KEY` set in your terminal, `./flycodes.sh baseline` submits six bounded requests to `gpt-4.1-mini-2025-04-14`. This is an API usage charge, not training a hosted model. Requests use `store=false`, at most 512 output tokens each, and no tools or automatic retries. Raw responses, usage, returned model identifiers and timing are retained. The common 384-byte output budget and full provider output are scored separately. A pretrained model has different data, compute and contamination exposure; its result is a reference, not a controlled architecture comparison.
5. **Export and reproduce.** `../../.venv/bin/python scripts/export_snapshot.py` refreshes the portable page from real artifacts. `./flycodes.sh status` prints current data. `../../.venv/bin/python -m pytest -q` verifies data preservation, causal masking, split separation and the bounded judge.

## Evidence and methodology

- [Measured results and interpretation](docs/RESULTS.md)
- [Protocol fixed before the scored pilot](docs/PROTOCOL.md)
- [Scientific rationale and primary references](docs/RESEARCH.md)
- [Decision and execution log](docs/LOG.md)
- [Completed run](runs/pilot-20261009T155722-s7/config.json), with source snapshots, model checkpoints, graph receipt, immutable benchmark outputs and timestamped events

The six tasks are original **LeetCode-style** formulations: Two Sum, palindrome, running sum, valid brackets, stable deduplication and maximum subarray. They are not an official LeetCode evaluation. Generated code is parsed and interpreted using a bounded Python subset in a timed subprocess; it is never passed to `exec` or `eval`. Unsupported syntax, timeouts, runtime errors and harness errors remain distinguishable. MacOS uses instruction/collection/CPU/wall limits; only Linux also enables the address-space limit. This is not a general-purpose Python container.

## Environment and layout

The launcher uses a project `.venv` if present, otherwise the existing `../../.venv`, whose packages were reused without modification. The actual versions are recorded in every run and [requirements.lock](requirements.lock). For an independent environment on a compatible host:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
```

`flycodes/` contains data loading, models, training, the judge, the API adapter and local server. `web/` contains the interface, `data/graph/` the mapped graph (~500 MB), and `runs/` the evidence. The raw ~1 GB source remains in the existing shared data directory and is never modified. The new project does not alter `flyworld`, `flyvision` or the older language experiment.

The next scientific stage needs a much larger licensed code curriculum, multiple seeds, validation-only exploration of memory/dynamics, fresh held-out tasks, a full isolated Python judge, and a measured pretrained baseline. The expanded experiment remains a small development study and cannot establish whether a different fly-constrained architecture could ultimately learn broad algorithmic reasoning.
