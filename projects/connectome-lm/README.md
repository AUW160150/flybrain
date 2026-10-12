# Small connectome-constrained language model

This project implements the protocol in [CODEX_EXPERIMENT_PROMPT.md](../Experiment/CODEX_EXPERIMENT_PROMPT.md). UTF-8 bytes pass through learned embeddings, trainable recurrent weights on an extracted neuron-level **male-cns:v1.0** graph, and a small linear readout. Everything learns from scratch. The graph is a structural constraint on an artificial model, not a physiological simulation or an emulated fly.

Read [STATUS](docs/STATUS.md) for what actually ran. A software smoke test cannot establish that fly wiring helps. The primary research comparison is fly topology versus labelled, directed, degree-preserving rewired controls. Research training is validation-only until an explicit frozen final-test command.

## Environment

Commands below run from this project directory. The `fly-lm` launcher uses this project's `.venv`, if present, otherwise the existing workspace `../.venv`. The initial implementation reused that already isolated environment **without changing its packages**. [requirements.lock](requirements.lock) pins the actual project dependency closure; [environment.json](docs/environment.json) records the inspected system. Config files contain JSON, a strict YAML subset.

```sh
cd /Users/Rodela1/Code/Flybrain/fly_connectome_lm
./fly-lm inspect
../.venv/bin/python -m pytest -q
```

For a clean installation on a compatible Python/platform (not executed in this task):

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
```

CPU float32, deterministic algorithms and two PyTorch threads are the default for **all** conditions. Accelerator requests must pass forward/backward and CPU comparison checks; there is no silent per-arm fallback. Dense execution still stores only one independent parameter per allowed edge. `--execution scatter` and `--execution sparse` are alternatives requiring their own common protocol revision.

## Acquire and inspect provenance

```sh
./fly-lm download --cache-dir ../data/flat-connectome
./fly-lm prepare --nodes 64 --sampling-seeds 101 --smoke
./fly-lm prepare --nodes 512 --sampling-seeds 101
```

Acquisition follows the official catalogue links, enforces a 2 GB raw ceiling, checks resources and HTTP errors, verifies cached files against official size/MD5, and saves SHA-256, URL, release, licence, time and actual schemas in `data/raw/malecns-manifest.json`. Downloads use `.part` files, HTTP range resume and atomic rename. Old caches have **unknown original retrieval times**, recorded honestly. Only the two required Feather products are used. The existing neurotransmitter file and simulator-derived networks are not inputs.

In this managed sandbox, top-level `curl` was permitted but Python child network requests failed DNS. Acquisition evidence was fetched with top-level `curl`, then validated by `import_cache.py`. Those manifests and prepared datasets already exist, so the pilot does not need network access. On a normal host, `download` performs the same steps directly. See [DATA_SOURCES](docs/DATA_SOURCES.md) for exact URLs and checksums.

Preprocessing memory-maps Arrow batches, performs an exact all-row ordered-pair duplicate audit using temporary disk partitions, and stores the filtered graph as compact arrays. Only small extracted subnetworks use NetworkX. No whole-CNS dense matrix is constructed. `*.nodes.tsv`, `*.edges.tsv`, NPZ arrays and JSON receipts preserve body IDs, induced directions, raw counts, extraction configuration and hashes. Counts influence thresholding only in the primary study.

Explicit synthetic fallback for **software smoke only**:

```sh
./fly-lm prepare --nodes 64 --sampling-seeds 101 --synthetic --smoke
./fly-lm smoke --synthetic --smoke
```

Non-smoke scientific commands reject synthetic graphs. The real-data smoke does not need this fallback.

## Bounded smoke and planning

```sh
./fly-lm smoke --dry-run
./fly-lm smoke
./fly-lm profile --config smoke
./fly-lm matrix --config pilot > reports/pilot-run-matrix.json
./fly-lm controls --config pilot --dry-run
```

The real smoke runs all five required conditions, 64 nodes, width 16, context 32, batch 2, 20 updates per run, one seed, 1,280 prediction-byte exposures per run. Evaluation is full deterministic validation, not random batches. `profile` is a short synthetic-token forward/backward timing probe, not a training result. `matrix` always previews; `run --dry-run` lists the exact run IDs, order, seeds, parameters, exposures and resource estimates without training. `controls` without `--dry-run` prepares randomized graphs but does not train.

## Validation-only pilot — next stage, not automatic

```sh
./fly-lm run --config pilot
```

This is 15 runs: five required conditions × training seeds 1/2/3, one independently rewired control per seed, sampling seed 101, 512 nodes, context 128, batch 4, 2,000 updates. Every run consumes 1,024,000 prediction bytes; the full matrix consumes 15,360,000. Default lr .001 is an implementation starting point. **No pilot command opens test data.** Validation every 100 updates; full training budget is consumed even if the best checkpoint is earlier. Re-run the identical command with `--resume` to resume interrupted runs including optimizer/RNG/window position. Completed compatible runs are reused; failed seeds remain recorded.

## Development, freeze, confirmation, sealed test

These are explicit future commands and can take substantial local time. No paid compute is configured.

```sh
./fly-lm tune --config pilot --dry-run
./fly-lm tune --config pilot --output configs/development-selection.json
./fly-lm freeze --config confirmation --selection configs/development-selection.json --output configs/confirmation-frozen.json
./fly-lm run --config confirmation --freeze configs/confirmation-frozen.json --dry-run
./fly-lm run --config confirmation --freeze configs/confirmation-frozen.json
./fly-lm final-evaluate --freeze configs/confirmation-frozen.json
```

The development grid uses only seeds 901/902 and rates .0003/.001/.003 at the same pilot trial budget. It runs all required arms but selects the shared A/B/C/E rate by pooled A/B validation, and GRU rate independently. No width selection uses language performance. Freeze binds code, analysis plan, corpus, graphs, learning rates, checkpoint rule and the entire matrix. Code/data changes require a new labelled revision. Final-test refuses an incomplete frozen matrix and evaluates both best-validation and final checkpoints without reselecting. Test outputs are retained for reuse, not checkpoint tuning.

Confirmation uses seeds 11/22/33/44/55, three independently rewired controls each, batch 8, 20,000 updates: 35 runs, with each fly run trained once. Replication prepares samples 101/202/303 from the **same specimen**, reports overlap, and reuses compatible completed seed-101 confirmation runs:

```sh
./fly-lm prepare --nodes 512 --sampling-seeds 101 202 303
./fly-lm freeze --config replication --selection configs/development-selection.json --output configs/replication-frozen.json
./fly-lm run --config replication --freeze configs/replication-frozen.json --dry-run
./fly-lm run --config replication --freeze configs/replication-frozen.json
./fly-lm final-evaluate --freeze configs/replication-frozen.json
```

A separately named fixed-time protocol derives its common time budget from pooled development profiling. It excludes validation consistently from the training meter and records actual updates/exposures. Do not merge its rankings with fixed-byte results:

```sh
./fly-lm freeze --config confirmation --protocol fixed-time --selection configs/development-selection.json --output configs/confirmation-time-frozen.json
./fly-lm run --config confirmation --protocol fixed-time --selection configs/development-selection.json --freeze configs/confirmation-time-frozen.json --dry-run
```

To execute that secondary matrix, remove `--dry-run`; explicit final-test uses its own freeze file.

## Optional baselines and count initialization

`--include TRANSFORMER FROZEN-FLY` adds the from-scratch causal transformer and frozen recurrent-core ablation. Transformer architecture is chosen within 5% of active parameter count, using fixed embedding width/context and no padding. Include it during `tune` and `freeze` for scientific confirmation. Frozen-fly has fewer trainable parameters and is labelled accordingly.

`--include COUNT-INIT SHUFFLED-COUNT-INIT` adds optional **initialization** arms on the same real graph; the existing fly arm is UNIFORM. These are secondary, separate from the topology contrast. Target-row shuffles preserve the incoming count multiset, not each source's weighted outgoing total. They do not impose physiological strengths or fixed signs. Run with a separate bundle/report, never select whichever result looks favorable.

1024-node extraction is available with `prepare --nodes 1024`; research training at that size requires a separately named/approved follow-up protocol. Independent Alice corpus acquisition/retraining is not implemented in this initial project; it is not claimed as completed replication.

## Reports, diagnostics, resumption

Each execution prints the exact bundle JSON path in `runs/`. Substitute that path below:

```sh
./fly-lm report --bundle runs/SMOKE_OR_RESEARCH_BUNDLE.json
./fly-lm diagnose --bundle runs/SMOKE_OR_RESEARCH_BUNDLE.json
./fly-lm run --config pilot --resume
```

Reports include actual logs, failures, hashes, commands and plots for validation BPB versus bytes and training time, resources and graph degrees. Test metrics and paired/hierarchical intervals appear only when real final-test records exist. A smoke-only report is explicitly incomplete scientific evidence. `diagnose` processes **every arm in the bundle**, using validation interventions and fixed training-only prompts; these outputs never alter checkpoint selection. Samples are short illustrations. Run-level JSON retains BPB, byte perplexity, accuracy, timings, memory, parameters, core changes and selected steps.

All output is local. There is no unattended worker, service purchase, repository publication, hosted inference, or upload step.
