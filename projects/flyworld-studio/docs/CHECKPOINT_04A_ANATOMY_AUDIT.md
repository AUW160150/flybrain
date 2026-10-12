# Checkpoint 04A — Anatomy evidence audit and coordinate lock

8 October 2026. Existing project: `/Users/Rodela1/Code/Flybrain/sandbox/flyworld`.

**Audit complete. Requested anatomy integration remains blocked.** There are **0 verified local skeletons for the 110 requested circuit bodies**, **8 verified separate cached bodies**, and **3 of those bodies available in the current FlyWorld anatomy viewer**. The brain inside the fly is procedural placeholder geometry. No reference brain/CNS mesh or verified anatomical orientation was recovered. No runtime rendering, scientific package, avatar registration or simulation was changed.

The user-authorized Prompt 04A supersedes the earlier instruction to await a new development scope. Prior browser evidence remains valid: eight scenarios passed in the suite run, the final mobile scenario subsequently passed according to the user, and all 13 automated controls steps passed. That evidence is distinct from human visual review and from anatomical validation.

## Required context and search scope

Read the project instructions, status, north star, scientific boundaries, Checkpoints 01–03, decisions, unresolved issues, package catalog, morphology parser/loader and rendering code. Inspected the research instructions/protocol, dated validation and structural checkpoints, latest status, visualization index, source/claim/mismatch/question records and latest immutable manifests. **No required context file was missing.** Exact source paths and SHA256s are in [ANATOMY_SOURCE_MANIFEST.json](anatomy/ANATOMY_SOURCE_MANIFEST.json).

The source identity remains **male-cns:v1.0 / v1.0 / neuPrint UUID 4b2087c0fbe046bfaf0d60bc970e3e5d**. Source runs: structural `20261006T180116Z`, visualization `20261006T221533490089Z`, workflow `20261007T221035718347Z`. These are saved authoritative records, not a fresh live dataset or mutation-state refresh.

Discovery searched only the authorized Flybrain `data`, `processed`, `runs`, `visualization`, `Sugar/malecns_sugar_circuit_v1`, and this application's `public` directories. It produced **703 inventory rows**, including bounded archive members. Seven ZIP/NPZ containers were inspected; none lists SWC/mesh members. No local N5/Zarr container was found. The protected-source baseline covers **1,180 nonexcluded files**, including the public assets and research files. Dependencies, Git internals, credential files and symlinks were excluded; unrelated private directories were not scanned.

All physical candidates are SHA256-hashed. CSV headers, JSON keys, columnar schemas, NPY headers and archive member lists were inspected. Large matrix arrays were not loaded or assumed to be geometry. Archive members larger than 8 MiB retain their container checksum and explicit uninspected status. Absence findings mean **not identified in this bounded search**, not nonexistent globally. [Inventory](anatomy/LOCAL_ASSET_INVENTORY.csv), [discovery scope](../data/anatomy/manifests/discovery.json).

## Answers to the twelve required questions

| # | Question | Audit answer and evidence |
| --- | --- | --- |
| 1 | Is real MaleCNS anatomy currently loaded in FlyWorld? | **Yes, narrowly:** source-backed native skeletons 10093, 10807 and 11369 are available one selected body at a time in the separate ANATOMY_ONLY viewer. Their JSON numeric fields, headers and topology match canonical SWCs. They are not the requested feeding-circuit anatomy. A002/A008; current-state table. |
| 2 | Is the visible brain real or placeholder geometry? | **Placeholder.** The brain inside the avatar uses authored educational regions and generic demo nodes. It is not a MaleCNS reference surface or registered reconstruction. A003; S-PLACEHOLDER. |
| 3 | How many requested bodies have verified geometry? | **0/110.** The exact requested inventory includes all **67 bodies across the 17 minimum requested types**; the other 43 are LB3a/LB3d. Every requested body has a MISSING row. The eight incidental cached bodies are listed separately. A001; coverage CSV. |
| 4 | Which formats are available? | **SWC**: eight canonical native files plus one byte-identical probe copy. **JSON**: eight existing micrometer skeleton derivatives, three native browser caches, and eight new lossless audit caches. Feather/CSV/JSON metadata, NPY/NPZ matrices and SQLite graphs also exist; those are not meshes or neurites. No OBJ/PLY/STL/OFF/GLB/GLTF/H5/HDF5 anatomy was identified. A002/A009/A010; inventory. |
| 5 | Is a reference brain/CNS mesh available? | **No verified local reference mesh.** No brain surface, VNC envelope, cervical connective, full-CNS envelope, individual neuron mesh or neuropil mesh was found. Saved official documentation describes remote brain/VNC ROI volumes; those are not locally available surfaces. A003; S-DOWNLOAD and S-INVENTORY. |
| 6 | Are units and coordinate axes known? | Native SWC uses XYZ in **8-nm units**, scale **0.008 to micrometers**. Stored coordinates are native EM grid units; skeleton sampling/downresolution is separate. Native precomputed skeletons use **1-nm units**, while JRC2018 template skeletons use **micrometers**. Anatomical axis directions, handedness and anatomical origin remain unverified. A004/A005. |
| 7 | Is anatomical orientation verified? | **ORIENTATION_UNVERIFIED.** No authoritative right/dorsal/anterior matrix or corresponding source is available. Body-side annotations and visual appearance do not establish axis signs. A005; coordinate ledger. |
| 8 | Can assets map directly into a shared coordinate frame? | **Only a limited native-frame basis is supported.** Receipt-backed SWCs share the documented release/native-space convention and unit scale; original coordinates are retained. The current renderer centers bodies independently, so its display buffers do not preserve a common origin. Anatomical registration, annotation/synapse alignment and exact cross-mutation compatibility are unverified. Use original coordinates and one recorded shared transform in any future native view. A004/A005/A008; AM002/AM003. |
| 9 | Which assets are missing? | Requested skeletons, all requested neuron meshes, reference envelopes/neuropil meshes, individual synapse-coordinate tables, anatomical orientation/registration evidence, and an authoritative Puddle identity. Soma annotation points and aggregate body-edge weights do not fill these gaps. A001/A003/A007; unresolved ledger. |
| 10 | What official source/access would resolve them? | The documented official v1.0 native per-body GCS SWC directory, with neuPrint's exact-dataset skeleton API as an alternative. Official release scene/segmentation/ROI metadata can establish reference routes; anatomical axis evidence is still needed. The observed request failed at DNS before any HTTP response. No remote absence was established. Retrieval log and source-access details below. |
| 11 | Is the project ready for coordinate-faithful integration? | **Not for the requested circuit or avatar placement.** The eight incidental skeletons support bounded native-coordinate inspection, with orientation and mutation caveats. The requested anatomy and reference/registration evidence remain absent. Current single-body and abstract views remain valid under their labels. |
| 12 | Which exact prompt should run next? | **Prompt 04B — Authoritative asset recovery and coordinate evidence**, prepared at [docs/anatomy/PROMPT_04B_AUTHORITATIVE_ASSET_RECOVERY.md](anatomy/PROMPT_04B_AUTHORITATIVE_ASSET_RECOVERY.md). It starts with the five-body test set and bounded reference/coordinate metadata; it stops before runtime integration or avatar registration. It has not been executed. |

## Verified incidental bodies and exact requested coverage

| Cached body | Official type | Source points | Disconnected roots | Already available in FlyWorld |
| --- | --- | ---: | ---: | --- |
| 10029 | LoVC16 | 16,415 | 1 | No |
| 10053 | LoVC16 | 15,957 | 1 | No |
| 10093 | Am1 | 54,204 | 1 | Yes |
| 10807 | Pm11 | 23,636 | 1 | Yes |
| 11029 | Pm13 | 26,810 | 9 | No |
| 11369 | DNc01 | 18,539 | 2 | Yes |
| 12638 | MeLo8 | 11,738 | 1 | No |
| 12912 | MeLo8 | 38,691 | 1 | No |

Sources: official annotation table SHA256 `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2`, original acquisition receipts and parsed SWCs, all in the source manifest. Roots remain disconnected; no branch repair was performed. Historical segmentation UUIDs include multiple full and short identifiers. They are preserved in [conversion metadata](../data/anatomy/manifests/conversions.json), without replacing the neuPrint UUID or claiming equal current mutation state.

Required type coverage: LB3b **11**, LB3c **23**, MN4a **4**, MN6/MN8/MN9 **2 each**, GNG042 **2**, ANXXX462a **2**, GNG015 **2**, GNG021 **2**, GNG585 **3**, GNG108 **2**, GNG120 **2**, GNG472 **2**, GNG232 **2**, DNg67 **2**, DNge080 **2**. All have zero verified local skeletons. Aliases and sides are retained from authoritative annotations/requested-body records; no type was assigned a body from its name alone. [All 118 requested/incidental rows](anatomy/BODY_GEOMETRY_COVERAGE.csv).

The `10029.probe.swc` copy was initially held as likely/unverified because it had no acquisition receipt. Byte comparison then established identity with the receipt-backed canonical file. AM005 supersedes provisional AM004; both records remain. This duplicate does not increase unique-body coverage.

## Coordinate lock and scientific plan revision

The [36-row coordinate ledger](anatomy/COORDINATE_FRAME_LEDGER.csv) distinguishes original SWCs, current native browser caches, micrometer derivatives, new audit caches, the duplicate probe, remote format/volume descriptions, annotation points and render-buffer framing. Remote descriptions are not assertions that those files were downloaded.

The source SWCs are already generated skeletons; their original headers include coarse/downsampled construction metadata. This audit performs **no further simplification**. Header `ds_intv` is not substituted for the documented coordinate unit or source EM resolution. The eight older micrometer derivatives retain XYZ and parent-child cables after scaling by 0.008, but omit SWC radius/type columns. They therefore remain display derivatives rather than raw sources. The new audit JSONs preserve every numeric SWC column and header.

**SCIENTIFIC_PLAN_REVISION_REQUIRED — AM003:**

1. **Old integration assumption being evaluated:** a source-backed skeleton visible in FlyWorld is already suitable for direct shared-frame or avatar placement.
2. **New evidence:** the existing viewer centers each body's Float32 display buffer independently; the native files have unverified anatomical orientation and historical mutation metadata. The requested bodies and reference envelope are absent.
3. **Consequence:** centered display buffers cannot establish relative anatomical placement; no brain-to-avatar transform is justified.
4. **Recommended revision:** recover the bounded requested test set and coordinate/reference evidence first. A later native multi-body view must retain original coordinates and one explicit shared framing transform with its inverse. Anatomical labels and avatar registration require separately verified evidence.
5. **Prior views:** the placeholder avatar, abstract structural graphs, metadata and individually centered native skeleton views remain valid under their existing labels. No prior anatomical registration was established or silently retrofitted.

## Retrieval outcome and access required

The official native source is recorded in the saved MaleCNS download documentation:

`https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/{body_id}.swc`

The saved research documentation also records the alternate exact-dataset neuPrint route:

`https://neuprint.janelia.org/api/skeletons/skeleton/male-cns:v1.0/{body_id}?format=swc`

The prepared five-body set, selected from authoritative structural records, is **71254 (LB3b), 72059 (LB3c), 15321 (GNG042), 28181 (GNG015), 18295 (MN4a)**. Only the first GET was attempted: curl **exit 6**, HTTP **000**, `Could not resolve host: storage.googleapis.com`. Its timeout was 40 seconds and byte cap 8 MiB. There was no response body or asset checksum to claim. The remaining four entries explicitly say **not attempted after transport failure**. [Exact retrieval records](anatomy/ANATOMY_RETRIEVAL_LOG.jsonl).

Status: **BLOCKED — AUTHORITATIVE GEOMETRY SOURCE REQUIRED**. A network-enabled official request would resolve the access failure; success must still pass identity/version/hash/topology validation. Public GCS requires no token. The neuPrint environment credential was absent, and no credential file was opened or copied. No author/curator messages were sent.

Reference leads from the saved official download page are `gs://flyem-male-cns/rois/fullbrain-roi-v4` and `gs://flyem-male-cns/rois/malecns-vnc-neuropil-roi-v0`, described as 256-nm ROI label volumes. Their paths alone do not establish a ready reference mesh, anatomical orientation, offsets or a release-specific registration. Those require actual metadata and a documented conversion if surfaces are later generated.

## Deliverables, tests and preservation

All requested CSVs, source/claim/mismatch/decision/unresolved records and the retrieval JSONL exist under [docs/anatomy](anatomy/README.md). The 10 claims and five mismatch/correction records retain source references. Raw copies, eight lossless audit conversions, source baseline, body mappings and per-output provenance are under [data/anatomy](../data/anatomy/README.md). No new audit asset was attached to the public package catalog.

| Verification | Result |
| --- | --- |
| New anatomy contract/artifact tests | **18 PASS** — duplicate mappings, wrong release/dataset, missing provenance, hash preservation/tampering, coordinate headers, explicit transform round-trip, body referential integrity, immutability, placeholder/orientation rejection and actual published artifacts. |
| Application tests | **173 PASS** |
| Existing preprocessing tests | **20 PASS** |
| Strict TypeScript and production build | **PASS**, existing Three.js chunk-size and Zod annotation warnings remain. |
| Protected-source integrity | See [integrity report](validation/prompt04a/integrity.json): research/source/public files checked against the pre-audit SHA256 baseline. |
| Browser suite | Prior nine scenarios have passing user-run evidence across runs. No browser rerun was needed for this offline audit; application source/public assets are unchanged, and agent localhost access remains unavailable. |
| Biological/anatomical registration | **Not performed or claimed.** Numerical round-trip tests do not establish an anatomical transform. |

Validation logs: [docs/validation/prompt04a](validation/prompt04a/README.md). Reproduction commands and their dependency scope are in [anatomy/README.md](anatomy/README.md). Source files are read-only and checksummed; no changes were made to the separate research repository. Historical scientific gaps, including empty sugar-selected results and unassigned Puddle, remain intact.

**Stop point reached: audit only.** The exact next prompt is prepared for review; its retrieval work and subsequent anatomy integration have not been started.
