# Codex task: Authentic MaleCNS connectivity and architecture atlas

## Task in one sentence

Build a local, auditable visualization application that lets me inspect the **full released MaleCNS connection graph**, the **exact neuron subset used by my existing next-byte experiment**, and the **actual implemented model**, and compare their structure with clearly identified MLP, causal CNN, and decoder-only transformer architectures.

This is a visualization and inspection task. **Do not retrain, resample, repair, replace, or interrupt my running experiment.** Implement working software and produce data-backed artifacts where inputs and resources permit. Do not stop at a proposal. Never fabricate a completed diagram or measurement to make a deliverable appear finished.

Read this specification completely before implementation. Follow existing repository and parent `AGENTS.md` instructions. The existing `CODEX_EXPERIMENT_PROMPT.md` describes the intended experiment; actual saved run artifacts determine what was really executed. This new document is not a replacement for either file.

---

## 1. Questions the finished application must answer

1. Which reconstructed neurons or segments connect to which others in the released dataset?
2. What does the biological wiring look like as an anatomical reconstruction, a directed graph, and a connectivity matrix?
3. Which exact 512 biological IDs were used in my experiment, and where do they fit within the larger dataset?
4. Which connections were retained, removed by the experiment's filters, or cut because their other endpoint is outside the subset?
5. Which connections are anatomical counts, which are learned artificial weights, and which are engineered input/output or state-retention operations?
6. How does the actual text model compute one prediction and carry state to the next byte?
7. How do its structural rules differ from a multilayer perceptron, a causal convolutional network, and a causal transformer?
8. What is actually loaded, verified, rendered, aggregated, filtered, unavailable, or only schematic in each view?

A reader must be able to click a neuron, see exact incoming and outgoing partners, inspect connection counts, and trace a displayed relationship back to a versioned source or a saved experiment artifact. The project must not consist solely of a decorative network image.

## 2. Non-negotiable authenticity rules

- Use real published connectivity for views labelled MaleCNS. Do not generate a plausible-looking graph or silently substitute FlyWire, MANC, a type-level graph, or a different release.
- Use the exact saved subset for views labelled my experiment. **Do not rerun sampling simply to obtain another 512-node graph.** Size equality is not identity.
- Do not infer experimental neuron identity from a graph drawing, nearest anatomical position, or NBLAST similarity. This is an ID/provenance task, not a cross-specimen morphology-matching task.
- Distinguish reconstructed anatomy, published annotations, computed summaries, saved learned parameters, artificial activations, and illustrative architectures.
- The connectome is not an MLP with a known number of hidden layers. Do not force its recurrent graph into layers and call those layers anatomical facts.
- A force-directed coordinate is not a measured anatomical location. A line between node markers is not an axonal trajectory.
- A contact count is not a measured physiological weight. A learned negative model weight is not evidence that the corresponding biological neuron is inhibitory.
- Preserve directed connections. Do not symmetrize the graph, add reverse edges, keep only a BFS tree, or silently remove loops or isolates from a view labelled complete.
- Missing labels, coordinates, or skeletons must remain missing, not fabricated or placed at `(0,0,0)`.
- Do not infer absent measurements as zero. A verified missing entry in a fully ingested release graph can mean no represented connection; an unqueried, failed, or partially loaded region cannot.
- Never call an aggregate, sample, top-k graph, or partially downloaded product “all individual connections.” A complete aggregate may use all input edges while not showing them individually; say exactly that.
- No training results, performance rankings, biological conclusions, or claims of intelligence follow from these diagrams.
- Do not use image-generation tools to invent data-driven anatomy or connectivity. Render those from records. Hand-designed architectural schematics are permitted only when labelled as schematics and generated from explicit model descriptions.

## 3. Protect the current experiment

Work in a new, self-contained `visualization/` directory, or an equivalent clearly separate destination if the repository already has one. Do not edit training code, configs, graph files, analysis plans, checkpoints, RNG states, or existing dependency locks. Do not kill processes, resume training, run optimizers on my models, or consume their accelerator.

Inspect hardware and existing workloads. Use CPU and a bounded resource budget by default. Put optional dependencies in a separate visualization environment. Do not upgrade the environment used by an active run. Avoid importing training entry points that execute work at import time.

Read only completed, stable artifacts. If a checkpoint is being written, do not read a partial pickle. Prefer an atomically published checkpoint, then copy it into an immutable visualization snapshot using a temporary destination and atomic rename. Record its hash, step, source path, and snapshot time. Validate that the source did not change during copying. Do not change the writer's files.

Prefer safe tensor-only loading or `torch.load(..., weights_only=True)` where compatible. Do not automatically fall back to arbitrary pickle execution. If the format cannot be inspected safely, report the blocker and the required safe export.

Create `visualization/AGENTS.md` with brief visualization-only invariants, without overwriting the existing project `AGENTS.md`. Keep status in `visualization/docs/STATUS.md`. Use only the selected workspace and explicitly configured data directories; do not search unrelated personal folders.

Do not upload data, publish the dashboard, launch paid services, change credentials, or leave a server running. A local server must bind to loopback, not a public interface. Provide its launch command at handoff; use bounded server sessions only for tests.

## 4. Discover the existing run before assuming its architecture

Inspect the workspace for the original specification, run directories, resolved configs, graph manifests, node maps, edge arrays, model definitions, checkpoints, and logs. Accept their actual names; do not assume an artifact exists because the earlier prompt requested it.

Create an inventory recording paths, schema, sizes, hashes, run IDs, model conditions, step numbers, graph hashes, and data release. Redact secrets and unrelated personal paths.

Choose the target in this order:

1. An explicit `--run-dir` supplied by the user.
2. An unambiguous documented project selection of the active 512-node real-fly run.
3. Exactly one verified compatible 512-node real-fly graph/run in the workspace.

Multiple training seeds using the same verified graph permit a shared topology view, but not an arbitrary choice of trained weights. Multiple different graph hashes require an explicit selection. Do not choose by best loss, newest filename, or a familiar-looking neuron list. Produce the run selector and other available views while marking the ambiguous panel blocked.

Verify the condition: `FLY-TOPOLOGY` is not `DEGREE-REWIRED`, `RANDOM-DENSITY`, a 64-node smoke graph, or a synthetic fixture.

Required identity evidence:

- exact biological ID list;
- exact biological-ID-to-model-index mapping;
- exact directed edge set;
- exact edge-vector ordering when learned weights are stored as a vector;
- dataset release, extraction rules, and source hashes;
- model implementation/configuration associated with the checkpoint, not merely the latest source file.

A seed alone is not sufficient if versions or sampling code may have changed. A checkpoint containing an exact graph and node mapping can supply identity evidence; an anonymous adjacency matrix cannot establish biological IDs.

If actual N differs from 512, show actual N and an explicit discrepancy. Do not pad, truncate, resample, or change the run to match the document. Missing required identity evidence blocks the authentic experiment view, not necessarily the full published-data view.

## 5. Primary sources and version policy

Use original dataset pages and current official software documentation. Start with:

- [S1] MaleCNS download catalogue: https://male-cns.janelia.org/download/
- [S2] Project and release information: https://male-cns.janelia.org/ and https://male-cns.janelia.org/release/
- [S3] neuPrint query documentation: https://connectome-neuprint.github.io/neuprint-python/docs/queries.html
- [S4] navis repository/documentation entry: https://github.com/navis-org/navis
- [S5] Coordinate transforms and templates: https://github.com/navis-org/navis-flybrains
- [S6] Large-graph rendering: https://datashader.org/user_guide/Networks.html
- [S7] Linear-layer semantics: https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html
- [S8] Convolution semantics: https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv1d.html
- [S9] Transformer primary paper: https://arxiv.org/abs/1706.03762
- [S10] Existing local `CODEX_EXPERIMENT_PROMPT.md`, especially data, extraction, model, and artifact sections.

The original protocol names `male-cns:v1.0`. Resolve the actual run's release before joining. Prefer the matching full release for the direct comparison. A newer published release may be a separately named dataset; never silently mix releases or reuse IDs across them without documented correspondence.

The v1.0 catalogue lists these relevant files under:

    gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/

    body-annotations-male-cns-v1.0-minconf-0.5.feather
    connectome-weights-male-cns-v1.0-minconf-0.5.feather

Discover actual download links and schemas from the catalogue. Do not invent column names, endpoints, or API return order. In particular, test the installed `fetch_adjacencies` return schema rather than copying misleading variable names from an example.

Use bulk files for full-graph ingestion; use neuPrint for bounded validation, selected morphology, and selected synapse queries. Do not repeatedly query the entire public service one neuron at a time.

Record source URLs, release, retrieval date, byte sizes, checksums, available source verification metadata, licence/attribution, schema, and transformations. A downloaded hash identifies bytes but does not by itself prove their origin. Preserve published confidence filtering: “full” means full for that released product, not every possible biological connection.

## 6. Define “all the dataset” with explicit graph scopes

Implement separately named scopes, never a single mutable graph whose meaning changes silently.

### G0: Full released segment graph

Ingest every valid row of the released connection-weight product, with no additional contact-count threshold. Include its synapse-bearing endpoints, including segments without curated neuron annotations. Keep source self-connections if present. Label these objects **segments**, not all verified neurons.

Do not claim G0 contains every zero-synapse fragment in the segmentation volume. The node population is the connection-file endpoint universe, plus any additional inventory explicitly acquired and labelled separately.

### G1: Full curated-neuron graph

Use the complete curated neuron inventory and every G0 edge whose two endpoints meet that inventory's documented eligibility rules. Preserve eligible isolated neurons in the node table. Do not drop neurons merely because a type is null. Report any explicit non-neuronal exclusions and unresolved metadata.

Do not apply the experiment's threshold of five contacts here. Keep all released represented contacts between eligible endpoints, including anatomical self-edges if present. G1 is the main whole-neuron connectivity view; G0 remains accessible as the full released segment graph.

### G2: Experiment-eligible parent graph

Apply the verified experiment's preprocessing rules to G1. The original plan specifies at least five contacts per ordered pair and removal of self-edges, but use the saved run's rules, not this expectation alone. Record every stage and its counts.

### G3: Exact saved experiment graph

Load the saved experiment edge set and mapping. Verify it against G2 induced on the exact selected IDs. A mismatch is an error, not permission to regenerate the graph. Also retain G1 induced on those same IDs as a separate pre-threshold comparison.

Every summary must identify scope, release, filters, distinct node count, distinct directed pair count, summed contact count where defined, loops, unknown annotations, and coverage status. **Contacts, distinct partners, and graph edges are different counts.** Do not hard-code headline counts from a paper or prior conversation.

Provide a dataset-product inventory: connectivity and annotations used for topology; skeletons/meshes for geometry; optional synapse records for contact positions; optional transmitter predictions; microscopy/segmentation for image evidence. Include loaded status and reasons for deferral. Do not download every EM voxel merely to answer a neuron-to-neuron adjacency question. Full raw imagery is not a prerequisite for complete released graph access.

## 7. Canonical records, orientation, and ingestion checks

Use lossless identifiers. Keep source body IDs as integer-safe values in storage and decimal strings in JSON, JavaScript, CSV exports, and URLs. Never convert an ID through floating point. Dense array indices are separate from biological IDs.

Canonical node fields, nullable where appropriate:

    dataset, release, body_id, model_index,
    is_curated_neuron, annotation_class, annotation_type, side,
    in_experiment, coordinate_provenance, source_record_reference

Canonical connectivity fields:

    source_body_id, target_body_id, synapse_count,
    release, graph_scope, source_record_reference

Keep learned weights in a separate table keyed by:

    run_id, checkpoint_hash, source_body_id, target_body_id,
    source_model_index, target_model_index, parameter_index,
    learned_weight, parameter_status

Never replace synapse_count with learned_weight in a shared column called `weight` without an explicit semantic tag.

Before ingestion, inspect whether rows represent unique ordered pairs, ROI components, synaptic contacts, or another documented unit. Resolve duplicates using source semantics. Never add a total to its component subtotals; never sum overlapping ROI hierarchies as if disjoint. Unexpected duplicates or ambiguous units must stop that import.

Store topology as source -> target. Use this matrix convention everywhere unless explicitly labelled otherwise:

    C[target, source] = anatomical contact count
    A[target, source] = 1 when the connection is present
    W[target, source] = artificial model weight

Columns are senders, rows are receivers. The transpose used in a particular batched tensor operation does not change biological direction.

Validate ID uniqueness, foreign keys, nonnegative integral contact counts, finite values, row counts, aggregation conservation, and exact round trips. Malformed rows produce a quarantined report and incomplete status; do not call the result complete after quietly dropping them.

A hand-checkable fixture must establish that A -> B with seven contacts appears in row B, column A and affects B from A's previous state, not the reverse. Fixture IDs must be unmistakably synthetic and must never appear in the scientific gallery.

## 8. Scalable storage and resource limits

Do not construct a dense N-by-N whole-CNS matrix or an enormous Python NetworkX graph. Use batched Arrow/Feather ingestion, disk-backed tables/Parquet, and tested compact sparse arrays or indexes. NetworkX is acceptable for the exact small subset or a small, explicitly aggregated quotient graph.

Build exact source- and target-query access for both G0 and G1, plus the indexes needed by the viewer. A disk-backed engine such as DuckDB with appropriately organized Parquet is acceptable. Indexes must not silently omit low-count pairs. Keep resource estimates and measured use separate.

Separate data ingestion from browser rendering. Do not serialize millions of edges into one HTML file or create one browser object per whole-graph edge. Do not run all-pairs shortest paths or quadratic force-layout algorithms on G0/G1.

Full ingestion and aggregation must be bounded and resumable. Inspect available RAM, disk, and concurrent training before deciding what to execute. Conservative defaults: at most two download workers, at most two processing threads, no accelerator, and a configurable RSS budget no larger than 20% of available RAM with a 4 GiB ceiling. Treat these as implementation guardrails, not a guarantee against OS-level resource pressure.

A resource plan must account for compressed input, decompression, indexes, temporary sorting, cached images, and morphology. Reuse verified downloads from the experiment read-only. Set an explicit download/storage cap; do not mistake compressed file size for peak RAM. If a phase exceeds the budget, implement it and provide its command, mark it not run, and continue with safe independent views. Do not silently replace full processing with a sample.

Cache derived data using release, content hash, scope, filters, ordering, and renderer version. Write files atomically. Partial downloads or partial indexes must not satisfy a completed manifest.

## 9. Whole-dataset explorer: complete access without an unreadable hairball

Build a local dashboard with a clearly visible scope selector for G0/G1/G2/G3. It must offer three complementary views.

### A. Full-data matrix overview

Use all canonical edges in the selected complete scope to build an exact binned matrix overview. Offer separate reductions for:

- number of represented directed pairs per pixel/bin;
- sum of anatomical contacts per pixel/bin;
- optional maximum count, labelled as such.

Create bins from deterministic node orderings without allocating N*N cells. Each edge must enter exactly one bin for the sum/count reductions. Validate that bin sums recover the relevant full totals. A log colour transform is a display transform, not altered stored data.

Zooming should request higher-resolution bins and ultimately exact pairs. A coarse pixel may represent many neuron pairs: hover must show its ID/index ranges, reduction, and counts. Only a one-pair cell may be presented as one exact connection. The zero background is “no connection represented in this fully indexed release scope,” not proof that no biological synapse exists.

Offer stable ID ordering and a grouping order based on verified annotations. A full raw-segment view can use stable ID ordering even where biological grouping is unavailable. Never hide unannotated objects just to make blocks cleaner.

### B. Aggregated network overview

For readability, provide a quotient graph over a disjoint grouping, such as a mutually exclusive annotation class/type hierarchy. Every eligible object belongs to exactly one group at the chosen level, including explicit unknown groups. Conserve edge counts/contact totals and retain within-group connections.

An aggregate connection means all underlying pair records satisfying the group relation, not a new biological neuron. Expanding it must expose its underlying IDs and exact table.

Do not assign every neuron to one neuropil unless a documented rule supports that assignment. Neurons may innervate multiple regions. A neuron's endpoint region and a synapse's actual location are different facts. Any multi-membership ROI display is a separate incidence view and must warn about double counting; do not use it as a conserving quotient graph.

A force layout of aggregate nodes must be labelled “topological layout; positions are not anatomy.” Grouping algorithms, layout seeds, and any sampled approximations must be recorded. An algorithmic community is not automatically a named brain area or functional module.

### C. Exact neuron/segment lookup

Search by exact biological ID and, where available, type/name. Clicking a node must show full incoming and outgoing partner tables with stable pagination, total distinct partners, total contact counts, graph scope, and links to selected morphology/evidence.

Provide `source_id -> target_id` lookup returning the exact stored count or a scope-specific verified absence. Each table must include enough provenance to recover the source. Allow complete CSV/Parquet export of the filtered result, even when the screen displays one page.

A bounded ego-graph can show selected neighbors. Display “showing X of Y partners” whenever capped; give explicit controls for pagination/expansion. Changing a render threshold must not alter canonical tables, full statistics, or the saved experiment.

Optional short-path queries must be directed, bounded, and labelled candidate anatomical routes. Hitting an exploration limit means incomplete search, not “no path exists.”

## 10. Anatomical view: real geometry, separate from topology

Provide a genuine spatial view using published skeletons or meshes in a verified common coordinate system. Prefer native MaleCNS space for the full brain-and-nerve-cord comparison. Do not combine native coordinates and a reference brain template without the documented transformation and its valid coverage.

Use the official precomputed morphology/segmentation scene where suitable, or a verified navis-compatible renderer. Support lazy loading and caching of selected IDs. Make all indexed, available skeletons addressable; do not imply they are all loaded simultaneously.

For the experimental subset, attempt to load the available skeletons for its exact IDs under the resource budget. Render brain and nerve-cord context if available in the same coordinate system. Keep missing and failed IDs in the coverage report and in connectivity views.

Track source units, target units, transforms, axis conventions, and conversion status. The catalogue distinguishes native SWC, precomputed skeleton, and template coordinate units. Verify against the downloaded format metadata. When those documented units apply:

    native SWC coordinates in 8-nm units -> micrometres: multiply by 0.008
    coordinates in nanometres          -> micrometres: multiply by 0.001
    template coordinates in micrometres -> do not convert again

Do not apply a second conversion because a library has already normalized units. Validate with known reference geometry, bounds, and available corresponding points. Unknown units block anatomical positioning; they do not block a topology-only view.

If using a representative node position, record whether it is a published soma coordinate, a skeleton-derived centroid, or another explicitly defined statistic. A centroid is not a soma. A missing soma is not an error proving the neuron is invalid; some cell bodies can lie outside the represented volume.

A straight graph edge drawn between representative positions is an abstract connectivity chord, not the neurite trajectory or contact location. Label it accordingly. Show real skeleton branches separately. SWC parent-child edges connect points inside one neuron; they are not neuron-to-neuron synapses.

A full overview may use level-of-detail geometry or verified representative positions with coverage labels. It may not replace missing coordinates with a random cloud shaped like a brain. If local geometry cannot be obtained, show an unavailable spatial panel and a verified official-scene entry point; do not claim that substitutes for a completed local anatomical reconstruction.

## 11. Highlight the exact subset and quantify what was removed

Use the same biological IDs across the full dataset and selected subset. Show selections in the full matrix, annotation composition, and available anatomical view. Do not claim 512 neurons proportionally represent every region.

For each selected neuron, report incoming and outgoing values separately:

- full G1 distinct partners and contact totals;
- G1 partners inside versus outside the selected IDs;
- within-subset connections removed by actual preprocessing;
- connections/counts retained in G3;
- retention fractions with explicitly stated denominators.

A useful incoming contact fraction is:

    retained incoming G3 contacts / incoming G1 contacts

A zero denominator yields “undefined,” not zero or 100%. Also report the equivalent fraction relative to G2 to distinguish thresholding from boundary loss.

Provide an explicit, conserving removal ledger. Use a documented order of predicates so categories do not double-count the same pair: for example, outside selected endpoints versus internal filter removal, with internal removal reasons then partitioned by the actual preprocessing order. Show raw-segment-to-curated exclusions separately from within-G1 subset losses.

Do not sum incoming and outgoing incidence totals and label the result unique network edges: an internal edge appears in both roles. Verify totals against independent table queries.

Draw boundary connections as labelled aggregate external inputs/outputs or exact selected external partners, not as 512 additional invented neurons. The fully paginated table remains available even when the boundary diagram is capped.

Show annotation composition and overlap with parent groups without inferring function from names alone. “512/N” is a neuron-coverage fraction under a specified inventory, not a fraction of intelligence, memory, behavior, or brain capability.

## 12. Exact 512-node wiring view and linked matrices

Provide an interactive directed graph containing all actual G3 nodes. Provide linked matrices in the exact saved model-index ordering:

1. binary permitted recurrent adjacency;
2. anatomical counts on retained connections;
3. learned recurrent weights for a verified checkpoint, when available;
4. optional initial weights and learned-minus-initial weights, only when initial values are independently verified.

Keep positions/order fixed across these views so only the displayed quantity changes. Offer a second deterministic grouped layout, but never use its visual order as the saved model-index map.

Preserve all G3 connections in data and exact matrix access. In the node-link view, render all edges when practical; when reducing drawing for readability, display the filter and hidden count prominently. Do not redefine the graph based on whether a learned weight is small or zero.

The topology comes from the stored mask/edge set, not `W != 0`: an allowed learned weight can equal zero. Distinguish absent entries from allowed zero-valued entries with a mask overlay or equivalent encoding.

Use distinct legends for nonnegative contact counts and signed artificial weights. Numeric values and units must be inspectable. Do not label weight sign as biological excitation/inhibition. Do not imply contact counts and learned weights share a physical scale.

Clicking a node or matrix entry must synchronize:

    biological ID <-> model index <-> partner table <-> graph <-> morphology

For edge-vector checkpoints, verify the saved parameter-index mapping. Matching vector length and graph edge count is insufficient. Missing edge order blocks the learned-weight overlay while leaving verified topology available.

## 13. Visualize the real implemented predictor, not just its recurrent core

Read model code/configuration and checkpoint metadata associated with the run. Trace shapes with a small CPU inference call only if safe; do not execute a training script. Capture any difference between the original specification and implementation in a discrepancy report.

The original intended architecture, which must be checked rather than assumed, is:

    byte index
      -> embedding e_t, dimension d
      -> dense input projection B, shape [N,d]
      -> graph-constrained recurrent state h_t, dimension N
      -> readout projection R, shape [d,N]
      -> output projection O, shape [V,d]
      -> V next-byte logits

Intended equations:

    z_t      = W h_(t-1) + B e_t + b
    h_t      = (1-alpha) h_(t-1) + alpha tanh(z_t)
    logits_t = O (R h_t) + c

The earlier specification uses V=256, d=32, N=512, alpha=0.5 and one update per byte. Display actual values from the implementation. Mark a specification-only rendering “intended architecture; implementation unverified,” never “actual model.”

Show five relationship kinds distinctly:

- biological connections used only as a structural mask;
- learned graph-edge parameters;
- engineered dense text-input connections;
- engineered dense readout/output connections;
- engineered same-node state retention.

The dense B and R interfaces mean all modeled states can receive projected text input and contribute to the readout. Do not pretend selected biological sensory cells are the input layer or selected motor cells are the language output layer unless the actual code explicitly implements such an interface and labels it as an engineering choice.

The leak/identity term is not a reconstructed autapse. Biases and pointwise nonlinearities are not anatomical neurons. Any implemented cross-node normalization, dense recurrence, attention, shortcut, or other unexpected mixing must be exposed, not quietly removed to make the model agree with the old prompt.

### Folded and time-unrolled diagrams

Show the recurrent graph as one reused stateful core, then unfold three or four byte steps. The copies at t-1, t, and t+1 are repeated states of the same indexed units with shared weights, not new biological neurons or independent learned layers.

At a synchronous update, a source's previous state contributes to a target's next state. Do not draw cyclic equations as an instantaneous feedforward evaluation. State update count is not a measured biological duration. Unrolling the computation produces an acyclic execution graph even though the reused spatial connectivity is recurrent.

Show byte_t entering a step and the distribution for byte_(t+1) leaving it. Do not reveal future bytes to earlier predictions.

## 14. Optional checkpoint activity and weight inspection

When a compatible saved checkpoint exists, run a bounded read-only CPU probe on a fixed short ASCII string such as `abc def.`. Reset hidden state. Use evaluation/inference mode on a snapshot. Never read sealed test data or change checkpoint selection based on this visualization.

Record input bytes, model/checkpoint hashes, software version, and inference settings. Label states “artificial recurrent activations on the specified text,” not neuronal firing, measured voltage, or biological odor responses.

Keep the structural edge set fixed while animating activity. Activity should not appear to create new anatomical edges. If displaying `learned_weight * previous_state`, call it an instantaneous pre-nonlinearity model contribution, not a measured synaptic current or a complete causal attribution.

Initial-versus-current comparisons need a saved initial snapshot or an independently verified exact reconstruction of initialization. Do not regenerate plausible initial weights from a guessed seed. A missing initial snapshot disables that comparison; it does not require retraining.

A checkpoint labelled “latest” in the application must actually show its fixed snapshot time and step. This application does not silently monitor or keep copying an active training run.

## 15. Comparison with MLP, CNN, and transformer

Build a side-by-side architecture gallery, not a performance contest. Prefer actual baseline modules/configurations in the repository when present, recording whether they have trained checkpoints. Do not assume the optional transformer was implemented or trained.

If a requested architecture is absent, create a separate, explicitly untrained diagram-only reference in the visualization package. Save its configuration and instantiate it only for verified shape/parameter inspection. Never add it to the experimental training matrix or claim it is a completed baseline.

Use two clearly distinguished comparison levels:

### Level A: Architecture overview

Show the real full connectivity overview, the actual 512-state predictor, and the reference architectures. Use legends explaining that the panels have different scales and levels of abstraction. Do not imply a dot means the same thing in every panel unless it really does.

### Level B: Local connection rules

Show a small real induced neighborhood selected deterministically from G3, alongside explicitly schematic small examples of MLP, CNN, and attention rules. Save the real neighborhood's IDs and selection method; label it a detail, not the full 512-node model. These explanatory reference examples are not biological data or trained results.

#### MLP

Use a standard feedforward multilayer perceptron: a causal fixed window of byte embeddings, flattening, dense hidden layers with explicit nonlinearities, and next-byte logits. Clearly label the window length and all layer widths. No recurrence or future inputs.

A conventional dense layer connects every input activation to every output activation in that layer, with separately learned coefficients unless a specific sharing scheme is explicitly implemented. Make its allowed connection matrix visible. Omitted display edges need a label, not a claim of sparsity.

Do not present a one-byte-only MLP as having the same temporal context as the graph model. A contextual window MLP has a finite supplied context; its inputs should show that. If a reference has a different parameter count, state it rather than padding parameters to fake a match.

#### CNN

For the text task use a **causal 1D CNN**, not an image CNN pretending to process text. Show local receptive fields, kernel width, channels, padding, stride, dilation, and kernel sharing across positions. Validate that earlier outputs cannot see later bytes.

Kernel sharing means multiple drawn computational edges can use the same parameter. A feature-map position/channel is an activation location, not a reconstructed biological neuron. A diagram of connectivity must not count every shared application as a distinct learned weight.

An optional 2D image-CNN illustration is a different-task schematic and must be labelled as such.

#### Decoder-only transformer

Show embedding/position handling, masked self-attention, residual paths, normalization, per-token feedforward blocks, and output projection, matching the actual chosen implementation. Show Q/K/V projections and a separate causal position mask.

Distinguish:

    fixed allowed causal attention relationships
    learned Q/K/V and output projection parameters
    input-dependent attention coefficients for a particular layer/head/input

An attention heatmap is not a static connectome adjacency table. Its entries link vector-valued token representations for one forward pass; they are not individually stored biological synapses. Use rows for query/receiving positions and columns for key/source positions, with j <= t allowed when input position t predicts the next byte.

Never fabricate an interesting attention heatmap. Render a measured forward-pass tensor from a labelled checkpoint or clearly identified untrained reference; otherwise show only the verified causal mask. Attention weights alone are not a complete explanation of a prediction.

Autoregressive repeated application or a key/value cache does not make the transformer's internal block a biological recurrent circuit. Conversely, time-unrolled graph-model layers are copies with tied parameters, not additional anatomical layers.

### Reference configuration policy

Use actual repository configurations where available. For absent references, choose small documented educational configurations with the same byte vocabulary and a declared causal context, and mark them untrained/not parameter matched. Provide full shape tables and a compact explanatory drawing. Do not tune them, load pretrained models, or invent quality comparisons.

## 16. Parameter and graph accounting

Create a comparison table with:

    model/reference identity and verification status
    biological node count, when applicable
    state width and/or layer widths
    context and position/channel dimensions
    distinct allowed recurrent pairs, when applicable
    active trainable parameters, broken down by component
    frozen parameters and nontrainable graph storage
    weight tying/sharing rules
    recurrence and input-dependent routing
    anatomical versus engineered components
    trained/checkpoint status

Count unique active parameter objects correctly, including shared/tied weights only once. Include biases, embeddings, position parameters, normalization parameters, and readout layers as actually implemented. Do not multiply recurrent parameters by sequence length or convolutional parameters by the number of positions.

As a cross-check ONLY when the original specification is exactly implemented with separate untied matrices:

    P = 2*V*d + 2*N*d + N + V + m

where m is the number of allowed trainable recurrent edges. With V=256, d=32, N=512 this is:

    P = 49,920 + m

Check this against the actual parameter inventory; report differences instead of forcing equality. A 512-state model does not have merely 512 parameters. Dense interfaces must not disappear from the comparison.

The full anatomical graph has contact counts and reconstructed cells, not a uniquely defined trainable-parameter count. Mark that field “not defined until a computational model is chosen.” Do not call it an untrained version of the exact artificial model.

Do not compare raw neuron-graph density with whole-transformer execution-graph density under incompatible node definitions. A feedforward graph spans different layers; a recurrent matrix connects time-indexed states; attention relates token vectors. Show density only for explicitly defined comparable blocks. Do not compute a misleading “brain similarity score” from these diagrams.

## 17. Required visual deliverables

Create an interactive local application plus static exports. Each export has a sidecar manifest with its inputs, filters, graph scope, node ordering, reduction, rendered/available counts, and code revision.

Required when data support them:

1. Full released graph inventory and matrix overview, with separate G0/G1 scope selection.
2. Conserving annotation-group connectivity overview with drill-down.
3. Real anatomical view and exact subset highlight, with geometry coverage stated.
4. Exact G3 directed wiring graph and binary/contact-count matrices.
5. Full-to-subset selection and boundary-loss comparison.
6. Actual text-model block diagram including dense interfaces and state retention.
7. Actual recurrent model unfolded across a few byte steps.
8. MLP/CNN/transformer architecture comparison gallery and connection-rule diagrams.
9. Verified checkpoint weight/activity overlays, if compatible snapshots exist.
10. A neuron/edge explorer and exact machine-readable exports supporting the graphics.

Use HTML plus SVG/PNG where appropriate. Do not embed millions of SVG elements for whole-graph drawings: use raster summaries with searchable structured data underneath. Keep static architecture diagrams readable with legends, arrows, dimensions, and sufficient spacing.

Distinguish colour/line encodings and include textual labels. Never rely on a shared colour alone to imply semantic equivalence between contact counts and learned weights. Use exact values in tooltips/tables. Do not use lighting or a decorative brain silhouette as evidence.

A downloadable architecture comparison page may arrange independent figures side by side. Put the data provenance and status near the figure, not hidden only in a methods document.

## 18. Implementation structure and local UI

A possible layout, adapted to the existing workspace without modifying its training files:

    visualization/
      AGENTS.md
      README.md
      pyproject.toml and separate dependency lock
      configs/view.yaml
      src/connectome_viz/
        discover_run.py
        provenance.py
        ingest.py
        graph_scopes.py
        indexing.py
        morphology.py
        model_inspection.py
        baselines_schematic.py
        matrix_tiles.py
        summaries.py
        render.py
        app.py
        cli.py
      tests/
      docs/{STATUS,DATA_SOURCES,METHODS,LIMITATIONS,ERRORS}.md
      snapshots/                 # immutable copied run artifacts
      cache/                     # ignored by Git
      reports/<snapshot_id>/
        index.html
        figures/
        tables/
        manifests/
        audit.json
        validation.json

Use typed functions, explicit schemas, informative exceptions, deterministic ordering, and resumable processing. Prefer a small, reliable local UI over an elaborate framework. Browser-scale views may use Canvas/WebGL for bounded graphs; full matrix tiles and paginated tables should be served from disk-backed data.

The browser must not receive API secrets. Escape annotation text before rendering HTML; validate IDs and parameterize database queries. Use decimal-string IDs end to end. Do not allow arbitrary filesystem access or arbitrary SQL through UI controls.

Expose commands equivalent to:

    inspect-workspace
    inspect-data-schema
    plan-resources --dry-run
    ingest-full
    verify-run --run-dir PATH
    snapshot-run --run-dir PATH
    build-indexes
    fetch-morphology --ids-from VERIFIED_SUBSET
    build-views
    validate
    serve --host 127.0.0.1
    export-neuron / export-edges / export-figures

These are requirements for the implemented CLI, not assumptions that such commands already exist. At handoff, provide the real tested syntax and paths, not placeholders presented as working commands.

## 19. Mandatory validation and regression tests

Tests must cover at least:

### Data and identity

- Synthetic and real provenance never mix; authentic views refuse synthetic data.
- IDs survive storage/JSON/browser round trips, including a fixture above 2**53.
- Curated nodes include valid isolates and null type labels.
- G0/G1 scope differences are explicit and conserving.
- Ordered-pair aggregation respects schema; ambiguous duplicate/ROI totals fail.
- Every G3 node matches its saved biological ID and model index.
- Saved graph hash and verified parent-induced graph agree, or show a precise mismatch.
- Edge-vector ordering is verified before mapping learned parameters to neuron pairs.
- A zero-valued allowed model weight does not remove its structural edge.

### Direction and mathematics

- The tiny seven-contact A -> B fixture verifies orientation in tables, matrix, UI arrows, and a recurrent update.
- Matrix ordering/reordering preserves IDs and exact values.
- If the model is batched as h @ W.T, the UI still reports source -> target correctly.
- State-retention edges are distinct from anatomical autapses.
- Repeated time steps share weights and do not multiply the parameter count.
- Parameter inventory agrees with the implemented model and any applicable formula.
- Optional MLP/CNN/transformer references have the claimed shapes and causal behavior.

### Conservation and coverage

- Full count/sum raster reductions exactly recover the canonical edge/contact totals.
- Each complete overview includes all eligible records, not a silent sample.
- Aggregate groups conserve totals including unknown groups and within-group edges.
- Within/outside/subset-filter removal ledgers conserve per-direction totals.
- Paginated partner tables have no missing/duplicated rows and agree with degrees/strengths.
- UI caps/thresholds cannot mutate canonical data or the saved model graph.
- Missing geometry appears as missing coverage, not as an invented position or omitted neuron in graph statistics.
- Unit conversions are applied exactly once and verified against format/reference metadata.

### Application and non-interference

- Click a known real neuron and check synchronized ID/index, incoming/outgoing partners, matrix values, and snapshot badge against backend records.
- Opening both scopes does not share stale counts, cached tiles, or thresholds.
- Browser reload/bookmark preserves scope/order/filter identity.
- Broken geometry/API requests produce an error panel instead of a successful empty view.
- Static protected training files remain unchanged. Account for legitimate external checkpoint writes by inspecting only immutable snapshots; do not falsely claim the visualization froze training.
- No training/test loader or optimizer is invoked by visualization commands.
- Bounded smoke tests complete with no unintended long-running process.

Use browser tests/screenshots when tooling permits, inspect label overlap and direction indicators, and retain the actual evidence. Mark unavailable browser/accelerator tests skipped with reasons, never passed by assumption.

## 20. Explicit errors and partial completion

Do not attempt to guarantee that no bug is possible. Instead, fail closed where a wrong result would look authoritative. Emit structured errors with a human-readable message, affected panel, evidence inspected, and one exact recovery action.

Suggested codes:

    E_RUN_AMBIGUOUS
    E_RUN_IDENTITY_MISSING
    E_DATA_RELEASE_MISMATCH
    E_GRAPH_MASK_MISMATCH
    E_EDGE_ORDER_UNVERIFIED
    E_CHECKPOINT_UNSTABLE_OR_UNSAFE
    E_SCHEMA_OR_ROW_SEMANTICS_UNKNOWN
    E_ID_PRECISION_LOSS
    E_COUNT_CONSERVATION_FAILED
    E_COORDINATE_UNITS_UNKNOWN
    E_GEOMETRY_UNAVAILABLE
    E_RESOURCE_BUDGET
    E_INCOMPLETE_INGEST
    E_PROTECTED_INPUT_CHANGED

Example behavior:

    E_RUN_IDENTITY_MISSING:
    A 512x512 matrix exists, but no verified biological-ID mapping was found.
    Blocked: authentic experiment identity/anatomical overlay.
    Still available: full published-data explorer and explicitly anonymous
    model-matrix inspection, if requested/clearly labelled.
    Recovery: supply the saved node map using the actual implemented CLI flag.

A failed stage must not erase successful independent stages. Create an honest partial dashboard with blocked features labelled. Do not fill blocked views with synthetic cells, fake learned weights, made-up coordinates, or a newly selected 512-node graph.

“Zero connections,” “not loaded,” “no matching neuron,” “query failed,” and “filtered out” are different states. Encode them separately.

## 21. Execution order

1. Inspect existing instructions, workspace, run artifacts, and workload; write the inventory and resource plan.
2. Implement tiny synthetic-fixture ingestion, direction, mapping, conservation, and renderer tests. Keep fixture outputs outside the authentic report.
3. Reuse or acquire verified annotations/connectivity; inspect schemas; build graph scopes with provenance.
4. Resolve and verify the exact existing subset. Build topology-only views even if a checkpoint is unavailable.
5. Build complete disk-backed access and full-data matrix aggregation when within budget. Never label it complete before full validation.
6. Inspect the actual model and stable checkpoints without training. Generate the full computational block/unrolled diagrams.
7. Add real morphology, selected synapse evidence where available, and geometry coverage checks.
8. Add clearly identified MLP/CNN/transformer comparison references.
9. Run numerical, provenance, conservation, and UI tests; visually inspect generated exports; fix issues.
10. Write the dashboard, methods, provenance, limitations, and honest status summary.

Proceed with safe bounded work without unnecessary clarification. When an ambiguity genuinely prevents scientific identity, implement a selection mechanism and report the required flag rather than guessing. When heavy full-data indexing is unsafe alongside the active run, provide a separate exact command and explicitly mark it pending; do not start an uncontrolled background job.

## 22. Completion criteria and final handoff

A successful authentic result requires all of the following, or an explicit partial status for each missing item:

- Verified release and input manifests.
- Full G0/G1 ingestion/query coverage for anything labelled complete.
- Exact node/edge identity for the existing experiment.
- Direction and matrix conventions tested.
- Honest whole-graph aggregation plus exact partner access.
- A true geometry view with quantified coverage, not a synthetic anatomical layout.
- Separate anatomy, learned weight, engineered-interface, and activation semantics.
- Actual implementation-derived predictor diagram with dimensions and parameter accounting.
- Clearly labelled MLP/CNN/transformer comparison level and training status.
- No modifications or interference with the running experiment.

Finish with:

1. What was implemented versus actually executed.
2. Which real datasets, exact graph/run, and checkpoint snapshot were used.
3. Actual N, directed-pair counts, contact totals, filters, and geometry coverage.
4. Passed/failed/skipped tests and any unresolved errors.
5. The artifact paths and **one exact next command** to open the completed viewer or execute the blocking prerequisite.

Do not claim full-brain emulation, biological language processing, a model-quality advantage, or complete biological knowledge. The deliverable is an inspectable account of published connectivity and of the artificial architecture we actually built.
