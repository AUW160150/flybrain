# MaleCNS connectivity and architecture atlas

This is a separate, read-only inspection project. The Shakespeare experiment, its environment, graph, configurations, checkpoints and corpus are protected inputs. No training, sampling, optimizer, test loader, accelerator, upload, or background service is used.

From `/Users/Rodela1/Code/Flybrain`, open the interactive viewer:

```sh
./visualization/viz serve --host 127.0.0.1 --port 8765
```

Then visit **http://127.0.0.1:8765**. Stop this viewer with Ctrl-C. This command must be launched from your terminal: the agent sandbox rejected listening sockets. The route handlers were tested without opening a socket; live browser integration is explicitly skipped. A static report is available immediately at [reports/current/index.html](reports/current/index.html).

## What is available now

- Exact `male-cns:v1.0` saved graph: **512 IDs, 3,061 directed pairs, 38,708 contacts**. Graph hash `354ccf91b989f38883c0f72a0acb678f99ef7f7a4a52695197c2e7dca710534b`.
- Independent verification against the saved parent arrays and the matching published bulk product. Exact model-index and parameter-index CSV exports; zero structural weights remain allowed edges.
- Separate pre-threshold graph on the same IDs: **7,405 pairs, 47,404 contacts**. No replacement sample.
- Exact incoming/outgoing G1 partner access for each selected neuron, including outside partners, from a complete raw-file scan. The disk index contains **259,286 unique curated pairs incident to the saved IDs**. It is not a full G1 index. Use “Partner table scope → Full G1 partners for this saved neuron”.
- Binary/contact matrices, zoomable bins, conserving superclass quotient graph, exact pair/partner lookup, complete filtered CSV downloads, fixed topological layouts and per-neuron removal ledgers.
- Eight genuine native-space skeletons, with explicit **8/512 subset coverage**. All 512 nodes stay in graph statistics.
- Actual executed-source predictor diagrams, folded and unrolled, with the dense interfaces and engineered retention; **52,981 active parameters**.
- Untrained MLP (33,152 parameters), causal 1D CNN (17,216), and repository decoder-only transformer (52,924) references, with instantiated shapes and causal-prefix tests. No performance comparison.

## Implemented but incomplete in production

**G0/G1/G2 whole-release ingestion and indexes are not run.** The source has 151,856,684 ordered pairs. The interface exposes separate blocked scopes and exact recovery commands. Production whole-graph matrices, groups, partner queries and drill-down become available only after the complete disk index is published. Tiny isolated fixtures exercise the actual full-ingestion pipeline, including resume and duplicate rejection; that is not a production-completeness claim.

**Learned weight and activity overlays are blocked.** Eleven completed FLY-TOPOLOGY final checkpoints were copied atomically to content-addressed immutable snapshots. `torch.load(..., weights_only=True)` rejected their NumPy RNG pickle state. No unsafe fallback or guessed initialization was used. The run selector chooses a fixed snapshot explicitly; its default is topology only. [Safe-export requirements](docs/ERRORS.md).

## Commands

All output paths must be under `visualization/`. The launcher selects CPU, one processing thread, lower process priority, and disables bytecode writes. It uses a separate `visualization/.venv` with read-only reuse of already-installed workspace packages via one `.pth` file. No package or lock in the experiment environment was installed, upgraded, or changed. `requirements.lock` records the visible package closure.

```sh
./visualization/viz inspect-workspace
./visualization/viz inspect-data-schema
./visualization/viz plan-resources --dry-run
./visualization/viz verify-run
./visualization/viz verify-run --run-dir fly_connectome_lm/runs/confirmation-g101-s33-fly-topology-k0-441b7753ad8e
./visualization/viz ingest-subset --rss-mib 512 --max-seconds 120
./visualization/viz inspect-model
./visualization/viz build-views
./visualization/viz validate
./visualization/viz export-neuron --scope G3 --id 10029
./visualization/viz export-edges --scope G3
./visualization/viz export-figures
```

The example run flag is an explicit selector, not a recommended seed or a model-quality choice. Shared topology is selected only when compatible real run manifests have one graph hash. No checkpoint is chosen by loss, filename recency or seed order.

### Resource-heavy commands — NOT RUN on full production data

Run during a quiet period after checking available memory. Keep the RSS budget below 20% of available RAM. Current RAM/process inspection was restricted; a 512 MiB guard is a conservative limit, not an OS memory-pressure guarantee. Disk planning allows 64 GiB for SQLite, indexes and sorts; this is an estimate, not measured production usage. A whole-CNS dense matrix is never allocated.

```sh
./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 300
```

Repeat that exact command to resume committed batches. Completion publishes `cache/full.sqlite` atomically; `*.partial.sqlite` never satisfies a complete scope. Index construction can be resumed with the same command, or:

```sh
./visualization/viz build-indexes
./visualization/viz build-views
./visualization/viz validate
```

Index creation/ordering can require a longer uninterrupted final transaction than 300 seconds. Once resources permit, an explicitly longer bound is supported:

```sh
./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 1800
```

No automatic repeating job is installed. Broad whole-release CSV export is an offline, potentially very large operation and has **not run**:

```sh
./visualization/viz export-edges --scope G0 --output visualization/reports/current/tables/G0-edges.csv
```

### Morphology and browser tests

```sh
./visualization/viz fetch-morphology --ids-from visualization/reports/current/subset-ids.json --max-ids 8 --download-mib 32 --max-seconds 60
./visualization/viz fetch-morphology --ids-from visualization/reports/current/subset-ids.json --max-ids 8 --offline
node visualization/tests/browser.cjs
```

Eight skeletons were actually acquired through bounded top-level curl calls after child-process DNS failed. Receipt-verified offline import succeeded. A larger acquisition has **not run**:

```sh
./visualization/viz fetch-morphology --ids-from visualization/reports/current/subset-ids.json --max-ids 512 --download-mib 256 --max-seconds 300
```

The browser harness owns and cleans up its own loopback server and Chrome process. Its current outcome is skipped because loopback bind was denied; a separate static Chrome attempt aborted. Pillow-rendered figure companions were visually inspected and are not presented as browser screenshots.

## Artifacts

- [Static report](reports/current/index.html)
- [Status and execution record](docs/STATUS.md)
- [Identity verification](reports/current/identity.json)
- [Validation results](reports/current/validation.json)
- [Audit](reports/current/audit.json) and [source/run inventory](reports/current/inventory.json)
- [Node mapping](reports/current/tables/nodes.csv), [edge-vector ordering](reports/current/tables/G3-edge-parameter-order.csv), [exact binary/contact arrays](reports/current/tables/G3-exact-matrices.npz)
- [Actual model and reference inventories](reports/current/architecture.json)
- `reports/current/figures/`: SVG/PNG plus input/order/filter/reduction/count/hash sidecars
- `snapshots/`: immutable checkpoint/source archive copies; `reports/current/snapshots/`: receipts and safe-loading outcomes

See [methods](docs/METHODS.md), [sources](docs/DATA_SOURCES.md), [limitations](docs/LIMITATIONS.md), and [errors](docs/ERRORS.md). These diagrams do not establish biological language processing or a model-quality advantage.
