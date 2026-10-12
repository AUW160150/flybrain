# On-demand circuit atlas

8 October 2026. Target: search the real MaleCNS neuronal population, inspect selected neurons in a shared native coordinate frame, display recorded synaptic partners and contacts, and expand upstream/downstream without loading the whole connectome into browser memory.

## Use

Restart `npm run dev` after this update; the new local API is installed through the Vite configuration. Open **Brain → Real circuit anatomy**, or the same button in **MaleCNS data**. Choose **Load recovery five** for the verified starting set. Search a body ID, source type (for example `LB3b`) or source alias (`Quasimodo`), then add individual results or a complete result set of up to 24 bodies. A behavioral phrase is not treated as a validated functional circuit.

The connection table contains induced recorded edges among the selected neurons. Select a neuron to page through its upstream/downstream partners and add them. **Synapse sites** fetches an edge's recorded pre/post contacts. Orange marks the presynaptic endpoint; blue marks the postsynaptic endpoint. Confidence and count filters remain explicit. Drag to orbit, scroll to zoom, and use **Fit anatomy** to frame visible geometry. Region checkboxes control CB, both optic lobes and VNC context. **Open same IDs in Neuroglancer** provides an external source-view comparison.

The atlas is separate from the procedural teaching brain inside the avatar. Switching to it pauses world locomotion and educational world input. **Back to fly** restores the world view. Source evidence is available in the neuron inspector, reference details, synapse table and dataset footer.

## Exact catalogue scope

| Record set | Count |
| --- | ---: |
| All annotation rows in the pinned file | 211,577 |
| Neurons with source status `Traced` | 165,122 |
| All raw source edge rows | 151,856,684 |
| Induced Traced-to-Traced edges | 25,563,197 |
| Summed synaptic contacts on included edges | 124,025,046 |

The often rounded “167K” is not used as an exact promise. This index includes CNS neurons, not just brain neurons; untraced segments and glial annotation rows are excluded. Edge confidence follows the source's 0.5 export. The [index manifest](../data/connectome/index.manifest.json) pins both original Feather hashes and the generated SQLite hash. Source identity remains male-cns:v1.0 / `4b2087c0fbe046bfaf0d60bc970e3e5d`.

## Local operation and setup

The existing workspace is ready: the server-only SQLite index is built (~1.5 GB), and the five-body/four-surface recovery cache is populated (~84 MB at this checkpoint). Future anatomy and synapse requests use the official public bucket and are cached after byte/hash validation. Initial uncached requests need network access. No neuPrint token is required for this route.

For another checkout, use Node **22.18+**, `npm ci`, the two pinned files in `../../data/flat-connectome`, and Python with PyArrow. `npm run index:connectome` uses the workspace `.venv/bin/python` or `FLYWORLD_PYTHON`. It streams source edge batches, builds directional indexes, checks integrity and refuses to overwrite an existing index. Do not place the database, full source files or raw cache in `public/`. Static `dist/` hosting alone cannot serve the API; `npm run preview` includes it.

The UI retrieves uncached official assets automatically. For a reproducible bounded recovery without starting the UI:

```sh
npm run recover:connectome
```

When the planner reports queued requests, run these as separate commands:

```sh
curl --fail-early --config data/connectome/recovery/requests.curl
npm run recover:connectome -- import
npm run recover:connectome
```

Repeat only while requests remain, stopping on a download/import error. Metadata, shard indexes and payloads require successive planning rounds. A complete run reports zero queued requests and PASS for every entry. Plans and the working report are regenerable; the validation snapshots linked below preserve this checkpoint. Raw cache receipts/bytes are reused, checked and never silently refreshed after a mismatch. Cache growth has no global eviction policy yet.

## Bounds and accuracy

The browser receives pages of 50 search results/partners and up to 24 selected neurons. Geometry budgets are 250,000 points per SWC, 800,000 points per view, and 5,000 displayed contacts per edge with full matching totals shown. A contact has two endpoint markers. The coordinate table previews 100 rows. Region downloads are bounded to 64 MB per fragment and simplified with an explicitly labeled 2-µm preview grid; skeletons retain official coarse source cables. Oversized/invalid assets report an error instead of substituting invented anatomy.

Original 8-nm SWC/synapse coordinates and nm reference meshes share one origin and are converted uniformly to µm. There is no per-neuron centering. These source formats provide anatomical structure, not a physiological model. Historical mutation alignment and anatomical axis directions remain unverified. The five sampled edges' aggregate/individual counts match; global source equivalence has not been established. See [recovery evidence](CHECKPOINT_04B_ASSET_RECOVERY.md).

The local API permits same-origin GET requests, validates dataset/body identities and resource limits, restricts downloads to the official bucket, rejects redirects, checks byte ranges and shard ETags, and records SHA256/source receipts. It never reads a neuPrint credential. Unknown bodies or missing assets stay explicitly unavailable.

## Verification and next gate

See [validation and exact commands](validation/circuit-atlas/README.md). Application, anatomy, preprocessing and build checks pass. The new browser scenario is supplied but has not run here: Vite fails at localhost binding with EPERM. Prior nine-scenario acceptance predates the atlas and behavior follow-up; it is not reused as evidence for either feature.

Next, run the 11-scenario browser suite on the user's Mac and review native geometry, synapse alignment, camera feel, mobile layout and loading latency. Then choose any named scientific circuit from an explicitly sourced membership definition. Vision training requires a separate scoped model, input/output definition, task data and evaluation; raw anatomical connectivity alone supplies none of those. Avatar registration and biological simulation remain separate unimplemented milestones.
