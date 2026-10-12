# Anatomy status — Prompt 03 (historical)

Current update: [the circuit atlas](CHECKPOINT_04C_CIRCUIT_ATLAS.md) separately recovers five requested SWCs and four official reference surfaces, with shared native coordinates and recorded synaptic contacts. The package inventory below describes the preserved pre-atlas workspace; its three-body public package is unchanged. See [new recovery evidence](CHECKPOINT_04B_ASSET_RECOVERY.md).

**Current follow-up:** [Prompt 04A](CHECKPOINT_04A_ANATOMY_AUDIT.md) independently confirms 0/110 requested geometries, verifies all eight incidental cached bodies against the full official annotation table, and checks the existing three browser caches. The final anatomy browser scenario subsequently passed according to the user. The audit adds no runtime geometry; the original Prompt 03 record follows.

The requested 110-body circuit inventory has **zero locally available verified morphologies**. Those nodes remain abstract and show **ANATOMY UNAVAILABLE FOR THIS BODY**. The fly and educational systems still display PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA.

## Local search and available exception

Read-only workspace search found eight canonical SWCs with acquisition receipts under /Users/Rodela1/Code/Flybrain/visualization/cache/morphology. A separate 10029.probe.swc was excluded.

No cached body overlaps the requested 110. Three canonical IDs occur in the pinned structural source:

| Body | Source type | Original points | Cable segments |
| --- | --- | ---: | ---: |
| 10093 | Am1 | 54,204 | 54,203 |
| 10807 | Pm11 | 23,636 | 23,635 |
| 11369 | DNc01 | 18,539 | 18,537 |

They form a separate ANATOMY_ONLY package with no edges, not replacement geometry for LB3 or feeding circuitry. Other cache IDs 10029, 10053, 11029, 12638 and 12912 are absent from the frozen structural inventory and were not imported.

## Source and coordinates

Each imported receipt matches the actual SWC SHA256 and official flyem-male-cns/v1.0 native SWC URL. Units/space are supported by the saved paper/primary/malecns_download.html and visualization/anatomy/orientation.json, both pinned. No downloads took place.

Release association comes from the official URL and receipt. The header's native segmentation UUID is preserved separately and **not substituted for the neuPrint dataset UUID**. This is release-asset provenance, not a fresh query or assertion of identical live mutation state.

All coordinates, radii, IDs, parent links and headers remain intact. Native EM coordinates are in **8 nm units**, with scale-to-micrometers 0.008. Orientation remains **UNVERIFIED**. No named anatomical cameras, axis-sign guess, mirroring, template registration, interpolation or inferred neurites are used. Skeleton cables are not synaptic edges.

The converter checks point IDs, finite values, radii, parent existence, cycles, body ID, receipts, hashes and budgets. Browser rendering batches the selected body's original cables into one line geometry and centers only the display buffer.

## Artifacts and limits

- [Anatomy package](../public/data/malecns/malecns-anatomy.json)
- [Geometry checksums](../public/data/geometry/SHA256SUMS)
- [Offline PNG](previews/native-anatomy.png), [SVG](previews/native-anatomy.svg), [preview provenance](previews/native-anatomy.manifest.json)
- [Optional Matplotlib preview generator](../scripts/render_anatomy_preview.py)

The offline PNG was inspected for labels, plotted bounds and source/body separation. It is **not a browser screenshot** or proof of WebGL performance. Actual browser morphology acceptance remains pending; the code compiles and assets/topology pass tests.
