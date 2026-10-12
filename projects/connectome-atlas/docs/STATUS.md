# Actual implementation and execution status

Completed bounded work on 2026-10-05. This is an honest partial scientific-data dashboard: the exact saved subset and architecture are verified; full production release indexes and trained-weight overlays remain blocked as described below.

## Built and executed

The complete visualization specification and original experiment protocol were read. The implementation lives entirely in `visualization/`, with its own invariants, environment, lock, source modules, CLI, tests, reports, data caches and immutable snapshots. No experiment file was edited. No training, optimizer, resampling, test loader, accelerator, upload, paid service or background job was invoked. CPU work defaults to one thread and lower priority. No viewer server was left running.

The actual saved experiment was inspected before choosing architecture or IDs. Sixty-one run manifests were inventoried at the initial inspection. Compatible real 512-node runs shared one topology hash; no trained seed was chosen arbitrarily. The source archive reproduces the run implementation digest. Multiple runs use the same graph with distinct recorded seeds/configurations; each remains individually selectable.

| Evidence | Verified result |
|---|---|
| Release | `male-cns:v1.0`, released minconf-0.5 flat-connectome product |
| Exact graph | `fly_connectome_lm/data/processed/fly-n512-sample101.npz` |
| Graph content hash | `354ccf91b989f38883c0f72a0acb678f99ef7f7a4a52695197c2e7dca710534b` |
| NPZ file SHA-256 | `59598775bcd6da1f63ca417b10aee07ce13ba4ef1e4a03395660f22c446d3911` |
| Actual N / directed pairs / contacts | **512 / 3,061 / 38,708** |
| Self-edges | **0** in this exact saved graph |
| Mapping | All 512 biological IDs exactly match the saved model-index TSV |
| Edge-vector order | Every position verified: target-major, then source-minor |
| Parent comparison | Exact equality to verified G2 induced on saved IDs |
| Filters | Traced curated eligibility; contacts >=5; self-edges removed; exact saved ID set |
| Pre-threshold G1 induced subset | **512 nodes / 7,405 pairs / 47,404 contacts / 0 loops** |
| Boundary index | **259,286** unique curated pairs incident to selected IDs, from all **151,856,684** released rows |
| Native geometry | **8/512** exact saved skeletons; 504 unrequested; no fabricated positions |
| Actual model | **52,981** active parameters; **48,976 bytes** of nontrainable edge-index buffers |
| Executed source digest | `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8` |

The boundary scan initially hit the 512 MiB RSS guard and retained only committed batches. It did not publish a partial scope. Buffered IPC reads replaced whole-file mmap residency; resume completed. The successful command reported **178,110,464 bytes** peak RSS including final index construction; its streaming-phase receipt reports 168,181,760 bytes and 5.54 seconds for that resumed invocation. These are measurements of this bounded operation, not estimates for full indexing or total training memory.

All pair/count reductions, grouping totals, exact matrices, real parent equality and removal categories conserve their named scope. Incoming G1 contact incidence is 662,520: 615,116 outside, 8,696 internal below threshold, zero internal self-edges, 38,708 retained. Outgoing incidence is 618,497: 571,093 outside, 8,696 internal below threshold, zero internal self-edges, 38,708 retained. These incoming/outgoing totals are not added as unique edges.

The viewer exposes ID/type search, exact source→target lookup, stable partner pagination and complete filtered CSV exports; full G1 partners for selected neurons include outside-subset partners. Matrix zoom reaches exact pair cells and preserves sender/receiver direction. Linked graph, matrix, partner and geometry selection uses the same decimal IDs. Render thresholds change drawing only. Full scope selection remains visibly blocked until the full index exists.

Static exports include exact binary/contact matrices, all-node directed wiring, annotation matrices, a conserving boundary diagram, native skeleton projection, actual folded and three-step unrolled predictor diagrams, architecture references and local connection rules. Each figure has a source/order/filter/reduction/count/revision sidecar. The actual model shows dense E/B/R/O interfaces, restricted learned recurrent parameters and the distinct engineered 0.5 retention term. The model factory's ignored alpha config argument is documented; its constructor default 0.5 matches observed configurations.

References were instantiated only for shape, parameter and causal-prefix inspection: MLP 33,152 parameters (8-byte context); causal 1D CNN 17,216 (7-byte receptive field); repository decoder-only transformer 52,924 (128-position context, d32, four heads, one block, FF412). They remain explicitly **untrained illustrative references**. No performance results were inferred or compared.

## Snapshots actually copied; overlays blocked

Eleven completed compatible FLY-TOPOLOGY **final.pt** files were copied to read-only, content-addressed snapshots, with source stat/hash validation and atomic rename. Every copied hash was rechecked at handoff. Per-run receipts record original path, snapshot time, copied SHA and reported completed-result step. No active latest checkpoint was repeatedly polled and no live run was frozen.

Example: confirmation seed33 run `confirmation-g101-s33-fly-topology-k0-441b7753ad8e`, final-copy SHA `04025e071fa2532b705ea27e9c3587d7fbc10ad36c2f0fb369b1f251a6844860`, reported final step20,000. This is a provenance example, not a selected trained overlay. All eleven tensor-only loads rejected NumPy RNG pickle state. **No checkpoint weights or activations were used**, no unsafe load fallback occurred, and no synthetic initialization was substituted. The exact next trusted-export prerequisite and implemented import command are in ERRORS.md.

## Validation actually run

Final numerical/data/application suite: **35 passed, 0 failed**. Tests cover:

- Exact real node/edge identity and ordering, parent equality, synthetic rejection, int64/string IDs above 2**53, duplicate/ROI/negative-row rejection and null-type isolates.
- Seven-contact source→target orientation in tables/matrices/recurrent update; JavaScript arrow direction; reordered matrix identity; allowed zero weights; engineered retention; tied parameter counting; actual inventory/formula equality and reference causality/shapes.
- Raster/quotient conservation, unknown groups and loops, per-direction ledger partitions, exact pagination, G0/G1 scope differences, display/query immutability and complete selected-neuron boundary access.
- Full-ingestion code on isolated synthetic fixtures, atomic completion, interrupted-batch resume and quarantine behavior. This does not claim full production ingestion.
- SWC parent/point validity, single unit conversion, missing geometry failure, exact real scale/coverage, safe query bounds, loopback-only binding policy, protected static hashes and no optimizer/corpus entry-point imports.
- HTTP handlers through in-memory requests, including real 10053→10029 = 23 contacts, unavailable G0, missing geometry, traversal rejection and invalid tile requests.

Live browser integration is **skipped**, with actual evidence in `browser-validation.json`: this agent sandbox denied 127.0.0.1 listening sockets. Standalone Chrome also aborted (exit134). The included CDP test implements clicks, bookmarks, scope changes, snapshot badges, missing-data panels and screenshots, but no browser pass is claimed. Node syntax and JavaScript arrow/ID checks ran. SVG/PNG companion figures were visually inspected; missing subscript glyphs and obscured arrow tips were fixed. These companions are not browser screenshots.

Additional unexecuted checks: production G0/G1 conservation (requires full index), trained checkpoint numerical replay (safe-loader blocker), neuPrint return-schema check (package not installed or used), accelerator tests (CPU-only scope).

Thirty-eight protected static files matched their initial hashes at the final audit. Both raw released products were rehashed, and all 11 immutable checkpoint copy hashes matched. Canonical parent hashes were independently checked during verification. Writer-owned checkpoint/manifests were permitted to progress externally. Evidence: `reports/current/non-interference.json`.

## Not run and exact recovery commands

Full G0/G1/G2 indexing/whole-release overview is **implemented but NOT RUN** on production data. Current RAM/process inspection is restricted and documented training was treated as active. At a quiet time, after checking available RAM and disk:

```sh
./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 300
```

Repeat to resume. Use `build-indexes` for the equivalent final preparation, then `build-views`. Longer final sorts have an explicit `--max-seconds 1800` option. No unattended loop is installed. The full source is never replaced with a small sample.

A 512-ID morphology acquisition, whole-release CSV export and trusted safe checkpoint export have **not run**. Their exact commands and prerequisites are in README and ERRORS. Microscopy, full synapse-position products, full context meshes and transmitter predictions were not downloaded.

## Handoff paths and opening command

- `visualization/reports/current/index.html`: readable static report.
- `visualization/reports/current/{audit,identity,validation,inventory,resource-plan,non-interference}.json`.
- `visualization/reports/current/tables/`: exact ID map, edge order, canonical G3 edges, exact matrices and aggregate bins.
- `visualization/reports/current/figures/`: source-backed SVG/PNG exports with sidecars.
- `visualization/reports/current/geometry/`: individual lazy-load geometry payloads; `geometry.json` records coverage and hashes.
- `visualization/snapshots/`: immutable copied checkpoints and executed source.
- `visualization/cache/subset.sqlite`: complete selected-incidence index; `cache/topology.sqlite`: independent exact topology fallback.

From your own terminal, run:

```sh
/Users/Rodela1/Code/Flybrain/visualization/viz serve --host 127.0.0.1 --port 8765
```

Open http://127.0.0.1:8765. This starts only the local viewer. No server was left running by this task.
