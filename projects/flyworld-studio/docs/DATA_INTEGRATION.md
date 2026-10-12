# MaleCNS data integration

Prompt 03 adds offline data packaging and local inspection. No research script is executed, no network source is queried, and no research file is modified. The browser receives bounded derivatives, never the full graph.

## Source authority and dataset guard

Read-only research root: /Users/Rodela1/Code/Flybrain/Sugar/malecns_sugar_circuit_v1

The saved source, structural, visualization and workflow manifests, plus authenticated structural start/end metadata, agree on:

- Dataset: male-cns:v1.0
- Version: v1.0
- neuPrint dataset UUID: 4b2087c0fbe046bfaf0d60bc970e3e5d
- Structural run: results/structural/20261006T180116Z
- Focused visualization run: visualization/data/20261006T221533490089Z
- Latest workflow status: results/workflow/20261007T221035718347Z

This checks saved local records, not a live dataset refresh. [The source lock](../config/malecns_source_lock.json) pins 22 files by path, bytes and SHA256. Generation checks those bytes against the lock and frozen manifests. Changed inputs, unknown runs, mismatched identity, missing endpoints, or changed selected-result status fail closed. Refreshing the lock requires review; no different run is selected silently.

The pipeline reads nodes.csv, raw_edges.csv and paper_associated_paths.csv from one structural run and joins the focused model for requested membership and scoped paper evidence. Every focused edge and displayed identity/side/transmitter field is cross-checked against the structural records. Named-edge validation, important intermediates, motif comparison, validation reports, source manifest, claim/mismatch ledgers, unresolved log, saved metadata and anatomy status are pinned supporting context. Source GraphML/GEXF exports are documented alternatives, not another graph merged into the package.

The full Feather graph is not read or copied. Its upstream hash remains marked RECORDED_IN_FROZEN_MANIFEST, distinct from newly checked SHA256_MATCH source files.

## Rebuild and custom selection

Python 3.9+ standard library is sufficient. No Python packages, authentication or network access are required.

    cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
    npm run preprocess

This regenerates eight catalog packages and checksums under public/data/malecns and three content-addressed morphology caches under public/data/geometry.

A custom export that keeps the shipped catalog intact:

    python3 scripts/preprocess/build_packages.py \
      --source-run 20261006T180116Z \
      --package-type custom \
      --selected-body-ids 15321,15734 \
      --max-body-count 20 \
      --max-edge-count 200 \
      --output-directory public/data/custom-example \
      --geometry-output-directory public/data/custom-example/geometry

Load public/data/custom-example/malecns-custom.json through **MaleCNS data → Import small local package**. The browser checks schema, dataset identity and provenance presence; it does not independently reverify every scientific source supplied by a custom file.

Other options:

- --source-root PATH: relocated read-only root containing exactly the pinned files.
- --package-type: all, focused, paper, candidates, lb3b, lb3c, motors, sugar-selected, custom, anatomy.
- --selected-types LB3b,GNG042: exact source type names for custom selection.
- --one-hop-neighborhood: incident neighbors in the frozen **extracted raw_edges.csv**, not the entire connectome. Oversized neighborhoods are rejected without silent pruning.
- --max-body-count, --max-edge-count, --max-geometry-objects, --max-package-bytes: narrow shared browser budgets.
- --geometry-directory PATH: local receipt-backed SWCs; never triggers downloads.
- --geometry-output-directory PATH: geometry destination. Browser geometry is served from /data/geometry, so external custom geometry must be placed there with its original content-addressed filename. Missing assets fail visibly.
- --output-directory PATH: package destination; output inside the research root is rejected.

Single-package generation replaces the manifest in its output directory. Use a distinct destination for custom exports. One package is loaded at a time; runs and releases are never silently merged.

## Package inclusion

| Package | Bodies | Edges | Inclusion |
| --- | ---: | ---: | --- |
| focused | 110 | 1,923 | All requested focused-explorer bodies; induced raw edges |
| paper | 102 | 274 | Source-defined counterparts and saved motif-path edge union; includes disconnected requested targets |
| candidates | 12 | 0 | GNG021, GNG232/G2N-1, DNg67/Fudog, DNge080/Rounddown, GNG042 and GNG015; independent profiles |
| LB3b | 11 | 43 | All verified LB3b bodies and induced in-population edges |
| LB3c | 23 | 221 | All verified LB3c bodies and induced in-population edges |
| motors | 10 | 29 | All MN4a/MN6/MN8/MN9 bodies and induced edges |
| sugar-selected | 0 | 0 | UNRESOLVED status contract |
| anatomy | 3 | 0 | Separate cached bodies 10093, 10807 and 11369; ANATOMY_ONLY |

The 3,564 saved paper paths remain an explicitly defined structural view, not effective selection or strict replication. Candidate comparison has no edges implying a shared pathway; raw relationships are available in the separately labeled focused package.

## Interface and scientific distinctions

**MaleCNS data** provides package selection, directional body diagrams, population cards, placeholder-region context, paginated raw edges and morphology when available. Side/type/evidence filters combine with incoming, outgoing, one-hop, full-package or saved-path isolation. The graph draws at most 300 arrows with a visible notice; all package edges remain in the table.

The inspector preserves string body IDs, aliases, type/class/superclass, side provenance, root/soma side, entry/exit nerves, body and cell-type NT prediction/confidence, separate transmitter consensus, package/source memberships, evidence, source files, missing fields and ledger warnings. Partner summaries are **IN-PACKAGE ONLY**. Side labels do not locate a crossing neurite.

[Behavior mappings](../config/educational_behavior_mappings.json) are separate from scientific packages. Only FEED illustrates source-labelled motor records, with USER_DRIVEN_ILLUSTRATION and an unreviewed educational disclaimer. Other gestures have no real-body mapping. Raw counts do not determine highlights. Rule/replay remain synthetic demo transport, not imported physiological recordings.

## Validation

    npm test
    npm run test:preprocess
    npm run build
    FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e

See [Checkpoint 03](CHECKPOINT_03_REAL_DATA.md), [package format](CIRCUIT_PACKAGE_FORMAT.md), and [anatomy status](ANATOMY_STATUS.md).
