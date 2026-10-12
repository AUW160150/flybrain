# Checkpoint 04B — authoritative recovery

8 October 2026. The user approved the proposed full searchable catalogue and on-demand circuit viewer after audit 04A. That approval extends the prepared 04B audit-only stop. Recovery evidence is recorded here; the resulting viewer is described in [the circuit atlas checkpoint](CHECKPOINT_04C_CIRCUIT_ATLAS.md).

## Recovered evidence

All five prepared bodies now have official native SWCs. This advances verified local coverage of the original requested set from **0/110 at audit 04A to 5/110**. The other 105 were not bulk-requested; availability is unknown until requested. The eight incidental historical skeletons and three-body public package retain their earlier scope.

| Body | Authoritative type | Native SWC points | Tested downstream partner | Flat-table count | Individual contacts ≥0.5 |
| --- | --- | ---: | --- | ---: | ---: |
| 71254 | LB3b | 379 | 21763 | 86 | 86 |
| 72059 | LB3c | 384 | 15734 | 95 | 95 |
| 15321 | GNG042; source alias Quasimodo | 3,684 | 555256 | 149 | 149 |
| 28181 | GNG015 | 6,700 | 10331 | 177 | 177 |
| 18295 | MN4a | 2,561 | 523040 | 5 | 5 |

Identity is checked against the official pinned annotation table before retrieval. The official route is `https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/{bodyId}.swc`. Original bytes, headers, SHA256, HTTP ETag, GCS generation, retrieval time and native coordinates are retained. These are the source's **coarse** SWCs, not full neuron surface meshes or complete fine branches. No additional skeleton simplification, mirroring, repair or independent centering is applied.

The official release scene also supplies four native reference surfaces: CB, OL(L), OL(R), and the VNC neuropil shell. Their legacy mesh bytes are preserved. A separately labeled 2-µm vertex-clustering preview reduces reference surfaces only. No image/segmentation volume was downloaded. The frozen [recovery report](validation/circuit-atlas/recovery-report.json) records every response used by the checks; [source receipts](validation/circuit-atlas/asset-receipts.json) include metadata and range requests.

Individual presynaptic/postsynaptic sites come from the release's `male-cns-v1.0-synapses-precomputed` annotation store. Bounded HTTP ranges retrieve the selected presynaptic body's shard data. Both endpoint confidences must meet the requested threshold. All five strongest-partner totals match the pinned aggregate table exactly. This validates those pairs, not every connection in the dataset. The UI preserves and flags any future disagreement.

## Coordinates and source alignment

| Source | Storage coordinates | Viewer conversion | Evidence / remaining limit |
| --- | --- | --- | --- |
| Native SWCs | XYZ in 8-nm units | Multiply all coordinates by 0.008 to µm | Release native route and previous native-format audit; preserve all headers |
| Individual synaptic contacts | XYZ; each dimension `[8e-9, "m"]` | Multiply by 0.008 to µm | Official annotation `info`; body identities and five aggregate counts checked |
| Legacy reference meshes | XYZ in nm | Multiply by 0.001 to µm | Official legacy-mesh format and release scene; source volumes have zero voxel offset |
| Shared view | Same native origin for every body and surface | Uniform unit conversion only | No body-specific translation, axis permutation, reflection, anatomical registration or warp |

The release scene references these native sources together. Its x/y/z dimensions are 8 nm; the reference volumes' coarsest stored resolutions are independent of legacy mesh coordinates. They must not be multiplied into mesh vertices. Camera fitting changes the camera, not source coordinates.

**ORIENTATION_UNVERIFIED remains appropriate for anatomical axis directions, handedness relative to anatomy, anatomical landmark origin and alignment to the procedural fly.** A native data coordinate origin is retained without claiming that it is a verified anatomical landmark. The SWC headers contain historical segmentation UUIDs (`86f3689d09a845f38a6831bca5594de5` or `f20f31f1db054c8781f60e909ff4e752`) and mutation IDs. These are preserved separately from neuPrint UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`; current mutation equivalence has not been proved. Synapse coordinates are not snapped to coarse skeleton cables.

## Retrieval history and preservation

The earlier 04A curl DNS failure remains an accurate historical record. During this recovery, standalone approved curl requests reached the public official bucket. A combined shell invocation again encountered DNS restrictions; a direct standalone request succeeded. The first CB mesh attempt exceeded the initial 8-MB budget; the explicit surface-only bound was raised to 64 MB after inspecting the official source. Its 31,411,312-byte raw mesh then passed validation and was reduced only for the labeled display preview. No authentication token was read or used. A neuPrint query required authentication; the implemented public GCS route does not require it.

This checkpoint uses a new `data/connectome` cache and frozen validation snapshots. It does not overwrite the 04A raw/converted cache, claim ledger, retrieval log, or public scientific packages. The new cache replaces the proposed conversion destination for the user-authorized runtime feature; lossless parsing occurs from receipt-checked raw SWCs. [Integrity evidence](validation/circuit-atlas/integrity.json) records the recheck of original files and source locks.

## Readiness

Source recovery, parsers, catalogue and unit conversions are validated. Runtime integration is implemented under the user's broader approval. Browser rendering, target-device performance and human visual review remain pending because this environment cannot bind Vite's localhost port. A source-backed structural view does not establish physiological function, effective connectivity or a trained visual system.
