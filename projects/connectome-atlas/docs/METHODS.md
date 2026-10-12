# Methods

## Identity before pictures

All compatible non-synthetic FLY-TOPOLOGY manifests with 512 states share one saved graph. The topology is therefore unambiguous; trained weights are not chosen automatically. The graph's NPZ hash, JSON content digest, nodes TSV and ordered edges TSV are independently checked. Biological IDs are decimal strings in JSON, URLs and CSV; int64 in NumPy/SQLite. Floating IDs are rejected, including integral-looking floats. A synthetic fixture above 2**53 verifies lossless storage and encoding.

The saved file is `fly_connectome_lm/data/processed/fly-n512-sample101.npz`. It is never regenerated. Source and target arrays are in target-major, source-minor order. This is the exact `GraphRNN.theta[k]` order, independently confirmed by the archived constructor's lexsort. A compatible checkpoint must also provide buffers exactly equal to those arrays before a weight overlay is enabled; equal vector length is insufficient.

The exact 512-node graph was independently compared with the induced graph in the immutable saved canonical parent arrays. Its counts/pairs were then compared with the raw released Feather records. All identities and counts agreed. Discovery and model inspection never import training or corpus entry points.

## Scopes and records

- G0 includes the connection-file endpoint universe, including unannotated segments, every represented pair and self-edge. Additional eligible annotation isolates are not mislabeled G0 endpoints.
- G1 contains every Traced annotation inventory entry except explicit glia/error/non-neuronal/artifact labels in statusLabel/superclass/class/type. Null types and eligible isolates are retained. This follows the verified experiment's curated inventory rule; it is stated explicitly rather than claiming all annotation rows are neurons.
- G2 applies contacts >=5 and then removes self-edges, retaining the G1 node inventory.
- G3 is the exact saved mask; it must equal G2 induced on the saved IDs.
- `G1-subset` is G1 induced on those same IDs before thresholding. It has its own identity, counts and cache keys.
- The bounded incidence cache scans the entire matching release product but stores only curated pairs touching at least one exact selected ID. It supports complete G1 partners for those selected neurons only. Looking up an outside neuron's complete neighborhood fails with a full-index prerequisite; it never reports a false zero.

`body_pre → source_body_id`, `body_post → target_body_id`, `weight → synapse_count`. The product consists of whole ordered-pair totals, not ROI components. Duplicate pairs abort import; no regional totals are summed. The raw SHA matches the existing official-origin verification receipt, which also records an exact all-pair duplicate audit. The new production full index additionally enforces a unique ordered-pair primary key.

Canonical `annotation_class` maps explicitly to the published **superclass**, which provides a useful disjoint high-level grouping for this sample. `annotation_type` maps to `type`, and `side` to `somaSide`. Original `class` remains in the source annotation product. Null superclass maps to an explicit Unknown group only for display. A type is not inferred to be a functional claim. Groups retain within-group pairs and conserve pairs/contacts exactly.

## Direction and reductions

Every table, arrow and matrix uses source → target. Rows receive; columns send: C[target,source], A[target,source], W[target,source]. The batched computation `h @ W.T` does not reverse biological direction. The synthetic seven-contact fixture asserts both orientation and the recurrent contribution. Synthetic fixture outputs use temporary test directories and never appear in the authentic gallery.

Matrix ranks are deterministic ID, superclass/type/ID grouping, or exact model-index order. Integer rank-to-bin arithmetic assigns every edge once. Independent reductions count pairs, sum contacts, and optionally take maximum contacts. The overview uses log1p only for colour. Each bin returns exact index endpoints and first/last IDs in that ordering; for grouped order those endpoints are not a numeric interval of all IDs. Only one-source/one-target cells are exact pairs. Zoom retains original ordering and queries smaller rank ranges.

G3 exact arrays are additionally exported at 512×512 with explicit int64 IDs, binary permitted mask and anatomical counts. Allowed model weights equal to zero remain structural edges. Learned weights have a separate schema and cannot overwrite contact counts.

Boundary categories are tested in this order per direction: outside subset, internal count below five, internal self-edge, retained G3. Denominators are full incident G1 or G2 contacts, with zero denominators returning null/undefined. Incoming and outgoing incidence totals are never summed as unique network edges.

## Storage and resource behavior

PyArrow IPC is read in original record batches through buffered OSFile reads. An initial mmap scan hit the 512 MiB guard as resident pages accumulated; it stopped after committed batches. The buffered implementation resumed and completed below 180 MB process peak. No partial index was published. SQLite uses disk-backed tables, a 16 MiB page cache, file-backed sort storage, one processing thread, unique source/target primary-key access and a target/source index. Source rows have stable zero-based references into the canonical released file ordering.

Full ingestion commits progress together with each batch. New sources/release/graph identity cannot resume an unrelated cache. Completion requires row/count checks, saved-graph agreement, endpoint node inventory, source/target access and deterministic order indexes. Final rename is atomic. A time/RSS progress callback also interrupts long SQLite operations; an unfinished final sort may need a longer explicit time bound on a later quiet-machine invocation. Disk caps are checked between bounded phases; SQL temporary files and decompression can overshoot a guard before the next check. These are guardrails, not hard OS limits.

Whole-dataset overview queries allocate at most 256×256 bins, never N×N. Individual node-link rendering is restricted to the exact small subset; whole graphs use disjoint quotient records. Query time is bounded in the server. Cache keys include release-derived source identity, graph identity, scope, ordering, bounds, bin resolution and renderer version. Completed files only satisfy queries. Large all-scope CSV export is deliberately offline; bounded per-neuron downloads are finished before HTTP success headers.

## Geometry

Eight catalogue-listed native SWCs were downloaded for the first eight IDs in the exact saved mapping. Files total 7,249,291 bytes. Each has a URL/hash/retrieval receipt. SWC point/parent integrity, finite coordinates and native volume bounds were checked. The catalogue documents 8nm source units and reference volume shape. Coordinates are converted once by 0.008 to micrometres; no mirror/template transform is used. Tests also exercise nm→µm and already-µm rules, and reject a second conversion.

The viewer shows real branches in selectable x/y, x/z, y/z projections and highlights the selected ID. SWC parent-child branches are within-neuron anatomy, not inter-neuron edges. No soma is fabricated; no missing coordinate is assigned an origin. The snapshot currently has 8/512 subset coverage; 504 IDs were not requested. Full brain/VNC context meshes and whole-release geometry remain unavailable. A descending cell reaching the nerve cord is its actual skeleton, not a made-up context silhouette.

## Actual architecture and references

Executed code hash: `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`. The archived source/config/pyproject contents reproduce this digest. Only the archived utility and two model modules are imported under a private package namespace; no training code is imported.

Actual model: E [256,32] (8,192), B [512,32] (16,384), theta [3061], b [512], R [32,512] (16,384), O [256,32] (8,192), c [256]. Total 52,981 active parameters, no frozen parameters; two int64 edge buffers consume 48,976 bytes. The retained identity term is fixed, not an additional trainable edge. Dense input/output interfaces are engineering choices. One synchronous step is 0.5 old-state + 0.5 tanh(proposal), followed by R and O+c. All parameters are shared across byte steps. No cross-node normalization, attention, dense bypass or hidden mixing was found.

The model factory does not pass config alpha into GraphRNN; the constructor default is 0.5, matching every observed compatible configuration. This discrepancy is recorded rather than silently relying on the config. Confirmation configurations use CPU, float32, d32, context128, batch8, dense execution, lr .003 and 20,000 updates. Pilot/development manifests have their own distinct settings; no result comparison is made.

MLP and CNN are absent from the experiment and live only in this visualization package. The MLP uses an 8-byte embedding window (d16), zero embedding padding, 128→64→64→256 dense layers, ReLU, no recurrence, and 33,152 active parameters. The CNN uses d16 embeddings, channels32/32, kernel3, dilations1/2, stride1, left pads2/4, ReLU and a per-position 32→256 output, for 17,216 parameters and receptive field7. Neither is parameter matched to GraphRNN.

The repository transformer is instantiated untrained using its own parameter-count selection: context128, d32, four heads, one block, FF width412, learned absolute position embeddings, masked attention, post-norm residuals, ReLU and dense 32→32→256 readout; 52,924 active parameters. No trained transformer manifest was found. Only the allowed causal mask is drawn, not fabricated attention coefficients. Prefix-invariance and shape tests passed for all references. No optimizer or corpus data were used. Constructor probes are never presented as saved initial experimental weights.

## Checkpoints and UI

All eleven completed compatible final checkpoints were snapshotted without selecting one trained seed. Copies are content addressed, read-only, source stat/hash validated across copy, with source path, fixed time and reported final step from a completed JSON result. Tensor-only loads rejected NumPy RNG pickle reconstruction. This leaves all learned overlays blocked while keeping source-verified architecture available. Safe exports must identify the original copied SHA and graph/code/signature; trust in the exporter is separate from tensor shape validation.

HTTP routes accept only named endpoints, decimal IDs, bounded pagination and predefined SQL fragments; values are parameterized. Static paths cannot escape the report directory. Annotation labels use textContent, never innerHTML. The server binds to loopback only. Browser URLs preserve scope/order/filter/selected ID/run and matrix viewport. The CDP harness implements linked-node, matrix, scope-switch, bookmark, safe-error and screenshot checks, but could not execute because this sandbox denied listening sockets. HTTP handlers were exercised through in-memory requests. Static PNG companions were rendered independently from explicit SVG primitives and inspected visually; they are not browser evidence.
