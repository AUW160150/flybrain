# Checkpoint 03 — Real data integration

7 October 2026. Existing repository: /Users/Rodela1/Code/Flybrain/sandbox/flyworld.

**Data integration, runtime guards, offline preprocessing, unit/adapter tests and production build are implemented. Browser visual acceptance remains pending because localhost binding is blocked in this sandbox. Stopped before neural dynamics and experimental interventions.**

Both earlier MVP implementations and their unit/build checkpoints were complete. Their unsupported browser acceptance is retained as a limitation; no second repository was created.

## Dataset and source authority

- Dataset: **male-cns:v1.0**
- Version: **v1.0**
- neuPrint dataset UUID: **4b2087c0fbe046bfaf0d60bc970e3e5d**
- Structural run: **20261006T180116Z**
- Visualization run: **20261006T221533490089Z**
- Latest workflow status run: **20261007T221035718347Z**
- Read-only root: /Users/Rodela1/Code/Flybrain/Sugar/malecns_sugar_circuit_v1

Identity was checked against saved source/manifests and authenticated start/end metadata; no live API request or Internet source query occurred. The complete 22-file path/byte/hash inventory is [malecns_source_lock.json](../config/malecns_source_lock.json). It includes source/config manifests, structural nodes/raw edges/paper paths/motif comparisons/named validation/important intermediates, validation reports, both saved Meta responses, focused model/build manifest, workflow status, claims, mismatches, unresolved questions, and local anatomy units/status documentation.

Body records and weights come from the single frozen structural run; the visualization model supplies already-validated requested membership and scoped paper evidence. Generation cross-checks the join and saved paths. No incompatible runs are merged. The full raw Feather graph is never read or copied into FlyWorld. Its upstream hash is explicitly inherited from the frozen manifest, not represented as a new full-graph verification.

Source outputs remain untouched: [source-integrity audit](validation/prompt03/source-integrity.txt) confirms all 22 pinned hashes still match and the eight existing SWC receipts match their files. This is a scoped integrity audit, not a claim to hash every file in the research repository.

## Packages created

| Package | Scientific label | Bodies | Edges | JSON bytes |
| --- | --- | ---: | ---: | ---: |
| malecns-focused | RAW_STRUCTURAL | 110 | 1923 | 1,723,513 |
| malecns-paper | PAPER_ASSOCIATED | 102 | 274 | 995,791 |
| malecns-candidates | CANDIDATE | 12 | 0 | 35,275 |
| malecns-lb3b | RAW_STRUCTURAL | 11 | 43 | 56,490 |
| malecns-lb3c | RAW_STRUCTURAL | 23 | 221 | 161,387 |
| malecns-motors | RAW_STRUCTURAL | 10 | 29 | 48,925 |
| malecns-sugar-selected | UNRESOLVED | 0 | 0 | 14,906 |
| malecns-anatomy | ANATOMY_ONLY | 3 | 0 | 19,749 |

The separately generated custom example contains **2 bodies / 2 edges / 19,873 bytes** (GNG042 bodies 15321 and 15734), with RAW_STRUCTURAL labeling. It is a CLI selection example, not a new pathway claim.

[Catalog](../public/data/malecns/manifest.json), [package checksums](../public/data/malecns/SHA256SUMS), [custom example](../public/data/custom-example/malecns-custom.json), and [geometry checksums](../public/data/geometry/SHA256SUMS) are present. Each package retains UTC generation time, run IDs, source hashes and both preprocessing-script hashes. The largest is about 1.72 MB, below the 4 MiB limit.

All 110 requested focused bodies are included. The 102-body paper package retains the exact 274-edge saved motif union and 3,564 paper-associated paths; it is not strict replication. The candidate package retains six tracked types as 12 independent bodies with zero comparison edges. LB3b/LB3c/motors retain every verified requested type member, with induced in-package raw edges. Sugar-selected is **UNRESOLVED and empty**; no raw path is substituted.

## Implemented inspection and preservation

The main navigation's **MaleCNS data** workspace offers package selection, abstract directional body diagrams, population cards, explicit placeholder-region context, paginated raw edges, conditional native morphology, side/type/evidence filters, incoming/outgoing/one-hop/full-membership isolation, and exact saved-path isolation.

The inspector preserves string IDs, aliases/types, side/root/soma provenance, class/superclass, nerves, NT body/cell-type predictions and confidence, separate consensus, evidence/source references, source and package memberships, missing fields and mismatch warnings. Upstream/downstream summaries always state **IN-PACKAGE ONLY**.

The dataset panel exposes dataset/version/UUID, body/edge counts, bytes, source runs/hashes, unresolved warnings, anatomy, selection and simulation status. Custom files receive strict size/schema/identity/reference checks and a visible warning that supplied scientific provenance is not independently reverified by the browser. Incompatible datasets are rejected; comparison mode is unavailable.

Educational behavior mappings remain in [a separate configuration](../config/educational_behavior_mappings.json). FEED illustrates source-labelled motors with USER_DRIVEN_ILLUSTRATION, explicit author/date/source/confidence/review metadata, and no validated functional claim. Other behavior keys have no assigned imported-body map. Raw packages remain immutable to these UI actions.

## Anatomy availability

The requested 110-body circuit has **0 available local morphologies**. It remains abstract, with ANATOMY UNAVAILABLE FOR THIS BODY. The fly/educational region model stays PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA.

A separate read-only workspace cache contains eight canonical SWCs. Only three match bodies in the frozen source; none overlaps the 110 requested circuit bodies. The ANATOMY_ONLY package therefore contains:

| Body / type | Native points | Cache bytes |
| --- | ---: | ---: |
| 10093 / Am1 | 54,204 | 2,445,667 |
| 10807 / Pm11 | 23,636 | 1,054,485 |
| 11369 / DNc01 | 18,539 | 817,561 |

Original headers, coordinates, radii and parent links are retained. The native files include 96,375 cable segments in total; disconnected roots are preserved rather than healed. Units are source-backed 8 nm native EM coordinates; orientation is UNVERIFIED. Header segmentation UUIDs are separate from the neuPrint dataset UUID. Receipt/release URL/source/cache hashes are recorded. No new downloads, mirroring, guessed camera orientation or inferred neurites. [ANATOMY_STATUS](ANATOMY_STATUS.md) documents exact sources and exclusions.

## Tests and validation

| Check | Result |
| --- | --- |
| Application unit/state/adapter/schema/SSR tests | **135 PASS in six files** — [log](validation/prompt03/unit-tests.txt) |
| Offline preprocessing tests | **20 PASS** — [log](validation/prompt03/preprocessing-tests.txt) |
| Strict TypeScript and production build | **PASS** — [log](validation/prompt03/build.txt) |
| Real package generation | **PASS** — [log](validation/prompt03/preprocessing.txt) |
| Custom CLI example and runtime schema | **PASS** — [generation](validation/prompt03/custom-example.txt) |
| Package/catalog/geometry checksums and source hashes | **PASS** — [delivery audit](validation/prompt03/delivery-audit.txt), [source audit](validation/prompt03/source-integrity.txt) |
| Browser suite discovery | Seven scenarios in two files — [listing](validation/prompt03/browser-test-list.txt) |
| Browser suite execution | **BLOCKED before tests:** listen EPERM 127.0.0.1:5173 — [log](validation/prompt03/browser-check.txt) |
| Browser visual inspection / FPS / peak memory / accessibility audit | **NOT VERIFIED** on a target browser/device |

New tests cover generation, exact release/UUID guard, hash preservation/tampering, run compatibility, counts, duplicate/dangling IDs/edges, raw weights, source warnings/nulls, separate NT values, scientific-label restrictions, Puddle nonassignment, empty selected-sugar state, size/count/stream limits, oversized one-hop rejection before publication, local custom generation, geometry receipts/body hashes/native topology, source-only highlights, filters/isolation and inspector scope labels. Earlier 93 tests remain intact.

The server-rendered checks and static previews do not prove browser hit testing, focus behavior, 3D rendering or animation quality. Browser scenarios cover the new data flows as well as the original world/brain MVP, but did not execute in this sandbox.

## Performance and previews

Engineering budgets: 500 bodies, 5,000 raw edges, 16 referenced geometry objects, 4 MiB per package, 5,000 saved paths, 100,000 points / 8 MiB per geometry asset. One package and one selected-body morphology load at a time. No full raw graph enters the browser. Diagram arrows are capped at 300 with a visible message; complete edge records remain paginated. Geometry cables are batched in one line mesh.

The data workspace and morphology viewer are lazy chunks (about 26 kB and 5 kB minified). The Three.js chunk remains about 704 kB / 180 kB gzip and retains its warning. Zod comment-annotation build warnings are nonfatal. These are build sizes, not measured browser FPS. Data display statistics expose counts/bytes; browser FPS is explicitly unsampled in that view. The original world retains its actual WebGL sampling overlay.

Existing previews:

- [Static data workspace HTML](previews/realdata-static.html): actual graph/inspector components rendered on the server; no interactive browser claims.
- [Native anatomy PNG](previews/native-anatomy.png) / [SVG](previews/native-anatomy.svg): offline native X/Z plot using original cable links. The PNG was inspected for readable labels and plotted bounds.
- [Plot provenance](previews/native-anatomy.manifest.json): input/package/script/output hashes.
- Production preview entry: [dist/index.html](../dist/index.html), served through npm run preview.

No browser screenshots were generated. Browser tests will produce docs/previews/realdata-package.png and realdata-anatomy.png only when successfully run locally. [Preview notes](previews/README.md) distinguish existing artifacts from planned screenshots.

## Exact commands

    cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
    npm run dev

Open the Local URL printed by Vite, normally http://127.0.0.1:5173. It chooses the next port if occupied. Use Node >=22.12.0; dependencies are installed and npm ci provides a reproducible reinstall.

    npm run preprocess
    npm test
    npm run test:preprocess
    npm run build
    npm run preview

Production preview normally uses http://127.0.0.1:4173. Optional browser check with existing macOS Chrome:

    FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e

Or install Playwright Chromium with npx playwright install chromium, then npm run test:e2e. Offline standard-library preprocessing and custom selector commands are documented in [DATA_INTEGRATION](DATA_INTEGRATION.md).

## Scientific limits and future readiness

No validated selected circuit exists; B01–B04 remain unresolved. Puddle remains unmapped. Eight paper/current pooled differences, body 957530's missing nerve, NT field distinctions, paper snapshot/pooling and anatomical orientation remain explicit. Raw connectivity establishes none of activation, physiology, functional importance, autonomous behavior or effective selection.

The bounded data/visualization boundary is ready for local browser acceptance and future separately specified adapters. It is **not ready for validated neural experiments** without independently resolved methodology, body-level mappings, appropriate scientific validation and an explicit simulator contract. All six experiment controls remain disabled.

Stopped before LIF dynamics, neural stimulation, lesion simulation, full-connectome simulation, automatic motor decoding and autonomous biological behavior. See [UNRESOLVED](UNRESOLVED.md), [SCIENTIFIC_BOUNDARIES](SCIENTIFIC_BOUNDARIES.md), and [the final file inventory](FILES_CHECKPOINT_03.txt).
