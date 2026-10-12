# FlyWorld — educational exploration and real-source inspection

A local React/TypeScript/Vite app with a procedural fly, educational brain overlays, and bounded MaleCNS structural packages.

**The avatar and teaching brain are placeholders. Real structural records are separate from educational activity. No neural dynamics or autonomous biological behavior is implemented.**

## Run

Node >=22.18.0; installed dependencies are already available in this workspace.

    cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
    npm run dev

Open Vite's printed Local URL, normally http://127.0.0.1:5173. If occupied, startup tries the next port. A clean reinstall uses npm ci. For a production preview:

    npm run build
    npm run preview

## Explore

**Explore** opens the original procedural world, game collisions, transparent head, five educational systems, 13 generic nodes, metadata inspector and synthetic/session timeline.

| Input | Action |
| --- | --- |
| W / S or up/down arrows | Hold forward / backward |
| A / left arrow | Left turn |
| D / right arrow | Right turn |
| Shift | Hold for 1.75× movement speed |
| Space | Takeoff / land |
| F / G / E / C | Feed / groom / escape / courtship gesture |
| X | Stop |
| B | Transparent head |
| Tab with viewport focus | Brain inspection |
| Escape | Previous world camera |
| P | Pause/play educational timeline |

Visible buttons provide alternatives. Reduced motion is available. Every overlay retains USER_DRIVEN_ILLUSTRATION or RULE_DRIVEN_EDUCATIONAL. Physics is explicitly game physics; replay gestures occur in place.

Take off raises the fly above a stable ground reference; the button becomes Land and the world footer shows height in scene units. Courtship plays a 2.4-second scripted single-wing display. Reduced motion retains a static wing pose. The behavior panel shows the active gesture; if inspection, replay or the data workspace prevents commands, **Enable behavior controls** returns to the world in USER CONTROL. Click the viewport before using Space or C.

Click the world viewport until **CONTROLS ACTIVE** appears. Hold movement and turning together for a curved path. Forms, dialogs and other controls keep their keyboard focus and release held movement. Both inspection modes pause locomotion. After Stop, a behavior command, inspection or a focus change, click the viewport and press movement again. Performance shows held keys, measured speeds, pose, collision, camera, focus and movement state.

**MaleCNS data** opens the real-source workspace. Choose focused bodies, paper motif, candidates, LB3b, LB3c, motors, empty sugar-selection status, or separate cached anatomy. Use body/population/region-context/raw-edge/morphology views, side/type/evidence filters, partner/path isolation and the full provenance inspector.

The verified local source tuple is male-cns:v1.0 / v1.0 / 4b2087c0fbe046bfaf0d60bc970e3e5d. The focused package has 110 bodies and 1,923 raw edges; the paper subset has 102/274. Counts and warnings retain their original source scope. Partner totals are IN-PACKAGE ONLY.

The saved packages retain their original anatomy coverage: three incidental source-matched bodies in ANATOMY_ONLY. The new circuit atlas separately recovers five requested bodies and fetches further anatomy on demand. Anatomical orientation remains unverified. Puddle stays unassigned; sugar-selected stays empty.

FEED can illustrate source-labelled motors through a separate unreviewed educational mapping. It does not imply that imported connectivity produced the behavior. Experiments remain disabled.

## Real circuit anatomy

**Restart the dev server after this update**, then open **Brain → Real circuit anatomy** (also available from MaleCNS data). Choose **Load recovery five** to start with verified anatomy. Search a neuron type, body ID or source alias; add results, inspect recorded connections, show synapse sites, and expand upstream/downstream partners. Drag to orbit and scroll to zoom.

The local catalogue contains **165,122 Traced neurons and 25,563,197 recorded connections** from the pinned MaleCNS v1.0 files. The ~1.5-GB query index stays on the server. Up to 24 selected neurons load in shared native coordinates, with official brain/VNC reference surfaces and on-demand cached anatomy. Five initial SWCs and four reference surfaces are already recovered; uncached requests need network access. No neuPrint token is needed for the public source route.

This is structural inspection. Typing a behavior name does not define a validated circuit, and no visual system has been trained. Official coarse skeletons, synapse positions, source counts and historical mutation limitations remain explicit. See [setup, bounds and use](docs/CHECKPOINT_04C_CIRCUIT_ATLAS.md), [five-body recovery](docs/CHECKPOINT_04B_ASSET_RECOVERY.md), and [validation](docs/validation/circuit-atlas/README.md).

## Regenerate and import

The offline preprocessor uses Python 3.9+ standard library and pinned read-only local source files. It performs no network queries.

    npm run preprocess

For selected-ID/type and bounded one-hop exports, see [DATA_INTEGRATION](docs/DATA_INTEGRATION.md). Custom JSON packages can be imported through MaleCNS data; unknown datasets, missing provenance/endpoints, invalid counts, unsupported labels and oversized files are rejected.

The browser loads bounded packages or requested atlas records/geometry. The complete Traced-to-Traced query index is local server data, never a browser asset. No credential is copied into the app.

## Verification and previews

    npm test
    npm run test:preprocess
    npm run test:anatomy
    npm run build
    FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e

Alternatively install Playwright Chromium with npx playwright install chromium, then npm run test:e2e.

Current checks: **199 application tests, 20 preprocessing tests, 18 anatomy tests, and production build pass**. The suite now contains **11 browser scenarios**, including the takeoff/courtship follow-up and new circuit atlas. These two additions have not run here because Vite cannot bind localhost in this environment (EPERM). The prior nine have user-run passing evidence across earlier runs. See [current validation and focused browser command](docs/validation/circuit-atlas/README.md).
- [Static HTML source preview](docs/previews/realdata-static.html): generated by node scripts/render_preview.mjs, no browser/server required.
- [Offline native-anatomy plot](docs/previews/native-anatomy.png): three genuine cached bodies; not a browser screenshot.
- Production build: dist/index.html, served through npm run preview rather than opened as a file.

## Documentation

- [Circuit atlas](docs/CHECKPOINT_04C_CIRCUIT_ATLAS.md), [Checkpoint 04B recovery](docs/CHECKPOINT_04B_ASSET_RECOVERY.md)
- [Checkpoint 04A anatomy audit](docs/CHECKPOINT_04A_ANATOMY_AUDIT.md), [anatomy evidence and proposed next prompt](docs/anatomy/README.md)
- [Checkpoint 03A controls audit](docs/CHECKPOINT_03A_CONTROLS_AUDIT.md), [Checkpoint 03 data](docs/CHECKPOINT_03_REAL_DATA.md), [current status](STATUS.md)
- [Data integration](docs/DATA_INTEGRATION.md), [package format](docs/CIRCUIT_PACKAGE_FORMAT.md), [anatomy status](docs/ANATOMY_STATUS.md)
- [Scientific boundaries](docs/SCIENTIFIC_BOUNDARIES.md), [UX](docs/UX_SPEC.md), [architecture](docs/ARCHITECTURE.md)
- [Decisions](docs/DECISIONS.md), [unresolved issues](docs/UNRESOLVED.md), [roadmap](docs/ROADMAP.md)
- Historical [Checkpoint 01](docs/CHECKPOINT_01_FOUNDATION.md) and [Checkpoint 02](docs/CHECKPOINT_02_MVP.md)

The research repository and existing Python FlyWorld project remain unmodified. This delivery stops before a neural experiment framework.
