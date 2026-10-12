# Data and source provenance

Consulted on 2026-10-05. Source files were reused read-only from the workspace. Original cache acquisition time is unknown; the experiment's recorded official HTTP verification time is 2026-10-05. New SHA checks reproduced the recorded bytes. No newer release, FlyWire graph, MANC graph or alternate sample was joined.

## Primary dataset

[Official MaleCNS catalogue](https://male-cns.janelia.org/download/) and [release notes](https://male-cns.janelia.org/release/) identify the `male-cns:v1.0` product and its geometry formats. Attribution: FlyEM / HHMI Janelia, University of Cambridge, MRC Laboratory of Molecular Biology and Google Research. Data licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

| Product | Official source | Verified bytes | SHA-256 |
|---|---|---:|---|
| Annotations | [v1.0 minconf-0.5 Feather](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather) | 14,483,314 | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |
| Ordered-pair contacts | [v1.0 minconf-0.5 Feather](https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather) | 1,051,241,946 | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` |

Raw source schemas and batching are recorded in `reports/current/schema.json`; the saved experiment's origin receipt includes official MD5/size, generation, timestamps and original HTTP headers in `fly_connectome_lm/data/raw/malecns-manifest.json`. This visualization's inventory records source URLs and hashes. A SHA hash alone identifies bytes, not their origin: the catalogue links and saved official object headers provide separate origin evidence.

The annotation table has 211,577 rows. The verified Traced curated inventory has 165,122 entries, including 2,605 null type labels. The contact file has 2,318 record batches and 151,856,684 ordered-pair records, with int64 `body_pre`, `body_post`, `weight`. `weight` in this file is preserved as anatomical contact count. It is never presented as a trained coefficient.

## Geometry

Native SWC directory discovered in the official catalogue:

```text
https://storage.googleapis.com/flyem-male-cns/v1.0/segmentation/skeletons-malecns/skeletons-swc/
```

Downloaded IDs: 10029, 10053, 10093, 10807, 11029, 11369, 12638, 12912. These are the first eight exact saved biological IDs, not a new graph sample. Source receipts are `cache/morphology/<ID>.source.json`; geometry coordinates and coverage are in `reports/current/geometry.json`. Total SWC bytes: 7,249,291. Units: native 8nm values, converted once to µm. The catalogue documents a native volume shape of 94,088 × 78,317 × 134,576 at 8nm; bounds were checked in that reference. No registration or template transformation was applied.

The [catalogue's Neuroglancer scene entry](https://male-cns.janelia.org/download/) remains available as an external reference; it does not substitute for a completed local whole-CNS geometry view. No microscopy, full synapse-position tables or mesh volumes were acquired.

## Implementation and architecture sources

- [neuPrint query API](https://connectome-neuprint.github.io/neuprint-python/docs/queries.html): bounded-query and ROI semantics reference. The installed-return-schema test is skipped because neuprint is not installed or used. Bulk topology import does not rely on the catalogue example's return-variable names.
- [navis](https://github.com/navis-org/navis) and [navis-flybrains](https://github.com/navis-org/navis-flybrains): geometry/template references. Neither is installed or invoked; native SWC is parsed directly with explicit units.
- [Datashader network documentation](https://datashader.org/user_guide/Networks.html): large-graph rendering reference. Implementation uses exact SQLite bin reductions and Canvas/Pillow rather than a full node/edge browser object graph.
- [PyTorch Linear](https://docs.pytorch.org/docs/stable/generated/torch.nn.Linear.html) and [Conv1d](https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv1d.html): official semantics references; current web pages redirected, so installed module behavior and executable shape tests are the implementation evidence.
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762): primary attention reference. This project's decoder-only module is identified exactly; it is not claimed to be the original paper's complete encoder-decoder architecture.
- Actual executed source: `fly_connectome_lm/reports/implementation-source-be167f981fad.zip`, archive SHA `3c1424882f2da4d318df8d757c95b060c6019da2ff410e7be7414e8b07b3ab48`. Its content digest is the recorded run code hash `be167f981fada51829a4d6519e42adf2481c08e85c5d753781c58918bdbd41e8`.
- Local intended protocol and visualization specification: `fly_connectome_lm/Experiment/CODEX_EXPERIMENT_PROMPT.md` and `CODEX_CONNECTOME_VISUALIZATION_PROMPT.md`. Actual saved artifacts, not the intended protocol alone, determine the diagrams.

The synthetic direction/schema fixtures use IDs above 2**53 in temporary directories. They are software tests only and do not appear in real anatomy or connectivity exports.
