# Errors and concrete recovery

Errors are structured records with a code, affected panel, evidence/message and recovery action. An unavailable view is never replaced with synthetic data or reported as zero connections.

## Current: E_INCOMPLETE_INGEST / E_RESOURCE_BUDGET

G0/G1/G2 production indexing was deliberately deferred alongside the Shakespeare workload. The cached source is 151,856,684 ordered pairs. During a quiet period, after checking the memory/disk plan, run:

```sh
./visualization/viz ingest-full --rss-mib 512 --storage-gib 64 --max-seconds 300
```

Repeat to resume committed batches. The equivalent final-stage command is `./visualization/viz build-indexes`. A sort that cannot finish in that bound can be run with `--max-seconds 1800` only when resources permit. Then `./visualization/viz build-views` enables completed scopes. No partial index is accepted as complete.

The first selected-incidence scan stopped at its RSS guard. The buffered implementation resumed and completed. `reports/current/subset-ingest-error.json` retains that historical stop; `cache/subset.sqlite` and its completed metadata establish the subsequent success. It is not an unresolved subset blocker.

## Current: E_CHECKPOINT_UNSTABLE_OR_UNSAFE

Eleven stable completed final checkpoint copies exist under `snapshots/checkpoints/`. Their per-run receipts are in `reports/current/snapshots/`. A safe load rejected `numpy._core.multiarray._reconstruct` in RNG serialization. No `weights_only=False` fallback or allowlist was executed. The reported final step is from the completed result JSON and is explicitly distinct from safely verified checkpoint metadata.

Reproduce one rejection safely:

```sh
./visualization/viz snapshot-run --run-dir fly_connectome_lm/runs/confirmation-g101-s33-fly-topology-k0-441b7753ad8e --checkpoint final.pt
```

The affected views are learned weights, artificial activations and saved-initial comparisons. Topology and archived-source architecture are available. A trusted tensor-only export must be supplied by an independently trusted exporter; this project intentionally does not execute the unsafe source pickle to create one. The export dictionary must contain:

```text
model: tensor-only complete state_dict including exact source/target buffers
signature: original run manifest signature
code_hash: original executed-source hash
graph_hash: exact saved graph content hash
original_checkpoint_sha256: the immutable copied original's SHA-256
step: integer checkpoint update step
initial_theta: optional saved tensor only; omit if not independently verified
```

Save the trusted export at `visualization/snapshots/trusted-confirmation-s33.pt`, then use this exact implemented syntax:

```sh
./visualization/viz snapshot-run --run-dir fly_connectome_lm/runs/confirmation-g101-s33-fly-topology-k0-441b7753ad8e --safe-export visualization/snapshots/trusted-confirmation-s33.pt
```

This command is **not run**; the prerequisite file does not exist. It copies/loads the supplied export with weights_only=True, checks original snapshot identity, graph/code/signature, buffer ordering and shapes, and runs the fixed CPU ASCII probe. Export hashes and tensor shape checks do not independently prove that a trusted exporter preserved the source's trained tensors; the export provenance is labeled accordingly.

## Current: E_GEOMETRY_UNAVAILABLE

Eight saved IDs have real local skeletons; 504 remain unrequested. The viewer returns an error for missing geometry while retaining the node in statistics. On a network-enabled terminal:

```sh
./visualization/viz fetch-morphology --ids-from visualization/reports/current/subset-ids.json --max-ids 512 --download-mib 256 --max-seconds 300
```

This larger command is **not run**. It is sequential, capped and resumable by valid source receipts. Native SWC units are 8nm according to the official catalogue. Unknown units or a second conversion produce `E_COORDINATE_UNITS_UNKNOWN`. No geometry is inferred from the graph layout.

## Current: E_LOCAL_SERVER_UNAVAILABLE (execution sandbox only)

Listening on 127.0.0.1 was denied by this agent's sandbox. No permission prompt was requested, and no server was left running. Run from your own terminal:

```sh
/Users/Rodela1/Code/Flybrain/visualization/viz serve --host 127.0.0.1 --port 8765
```

Browser integration can then be exercised separately with `node visualization/tests/browser.cjs`, which uses its own port 18765 and shuts down its own children. The static report needs no server. Current browser checks are skipped, not passed.

## Identity and data failure behavior

- `E_RUN_AMBIGUOUS`: supply the implemented `--run-dir` flag; no newest/best checkpoint selection occurs.
- `E_RUN_IDENTITY_MISSING`: require a biological-ID mapping and saved graph; anonymous matrices cannot establish IDs.
- `E_DATA_RELEASE_MISMATCH`: do not join releases or resume a cache with changed inputs.
- `E_GRAPH_MASK_MISMATCH`: preserve the saved graph and inspect the recorded extra/missing records; never regenerate the sample.
- `E_EDGE_ORDER_UNVERIFIED`: block only weights until exact checkpoint source/target buffers match saved order.
- `E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN`: quarantine the batch; duplicate/ROI totals and malformed IDs/counts are not silently summed/dropped.
- `E_COUNT_CONSERVATION_FAILED`: do not label a tile, quotient or ledger complete.
- `E_ID_PRECISION_LOSS`: reject floating or noncanonical biological IDs.
- `E_PROTECTED_INPUT_CHANGED`: stop the affected stage and inspect source identity; never overwrite the experiment.

HTTP tables distinguish represented pairs, verified absence in a complete named scope, endpoints outside scope, no matching node, missing data and query failure.
