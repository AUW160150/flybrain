# Checkpoint 02 — Interactive educational MVP

7 October 2026. Existing repository: `/Users/Rodela1/Code/Flybrain/sandbox/flyworld`.

**Implementation, unit checks, and production build complete. Browser and manual visual acceptance remain pending because the execution sandbox blocks localhost binding. Stopped before real MaleCNS integration and neural dynamics.**

Prompt 01's implementation and 52-test/build baseline were complete before this expansion. Its optional browser check was unsupported in this environment; the original checkpoint is preserved as history. No second repository was created.

## Implemented features

- Procedural head, thorax, abdomen, faceted compound eyes, antennae, six legs, wings, and proboscis. Explicit idle, walk, turn, feed, groom, takeoff, flight-idle, land, escape, and courtship gesture states.
- Direct keyboard/pointer movement in a lit, shadowed scene with ground, tree, flower/food, neutral landmark, world bounds, and swept obstacle collisions. The visible label is `COLLISION HANDLING: GAME PHYSICS`.
- Transparent head and linked world-follow, world-orbit, fly-inspection, and brain-inspection cameras. Inspection holds physical movement; focus targets a selected system or node, and return restores the previous world camera.
- Five educational systems, 13 generic demo nodes in one instanced mesh, eight illustrative relations, and five separately downloadable category packages. Layers support show/hide, opacity, isolation, reset, hover, selection, focus, and whole-brain return.
- Persistent inspector with generic ID, educational role category, current gesture, normalized intensity, event cause/times, original source mode, evidence, upstream/downstream demo relations, source-design references, and geometry warning. Layer and node buttons provide keyboard alternatives to canvas selection.
- User event recording, a fixed educational rule tour, and bundled synthetic or session replay. The timeline supports fades, pulse, pause, deterministic forward/backward scrub, speed, Clear, and Reset. Live scrubbing enters session replay without rewriting the original recording.
- Visible `USER CONTROL`, `EDUCATIONAL RULE`, `DATA REPLAY`, and `SIMULATION UNAVAILABLE` badges. Original user/rule activation labels survive replay.
- Six disabled experiment controls: stimulate, silence, lesion, restore, load brain, and compare brains. Status: `NOT CONNECTED TO A VALIDATED SIMULATOR`.
- Reduced-motion preference/toggle, text and symbols alongside color, keyboard shortcuts/help, lazy dialog content, bounded histories, and a live performance overlay for measured FPS, visible mesh objects, draw calls, active targets, camera, and mode.

These features are implemented and covered by the checks below; rendered appearance and real browser interaction have not been visually verified in this session.

## Placeholder and scientific status

**PROCEDURAL PLACEHOLDER AVATAR.** All geometry, coordinates, gestures, timings, motion scales, collisions, system boundaries, and display intensities are authored approximations. Every educational region and node has `geometryStatus: PLACEHOLDER_GEOMETRY`. The persistent label is `PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA`.

No rendered anatomy, neuron identity, biological circuit membership, relation, function, or physiological activation is scientifically verified. Generic `demo-*` IDs are not body IDs. The demo schema contains no transmitter or synapse-count fields. Entity evidence is `UNVERIFIED`; local source references identify teaching-design files, not biological evidence.

Every activation is `USER_DRIVEN_ILLUSTRATION` or `RULE_DRIVEN_EDUCATIONAL`. The bundled 24.3-second, nine-event replay is labeled `SYNTHETIC_EDUCATIONAL_REPLAY`. Replay demonstrates gestures in place, not a recorded physical trajectory. Intensity is dimensionless in [0, 1], not a firing rate. No activity value drives physical motion. Food is a visual marker, not a sensory/ingestion model.

The MaleCNS research repository and existing Python FlyWorld project were not modified. No real dataset, body IDs, scientific geometry, neural dynamics, or experiment adapter was imported. The original biological contract remains separate from the new educational schema.

## Exact run commands

Dependencies are already installed in this workspace. Use Node >=22.12.0 and a WebGL 2 capable browser. The tested environment used Node 26.4.0 and npm 11.18.0.

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
npm run dev
```

Open <http://127.0.0.1:5173>. For a clean installation, run `npm ci` first.

```sh
npm test
npm run build
npm run preview
```

The generated production entry exists at `dist/index.html`; serve it through <http://127.0.0.1:4173> using the preview command. It is not intended for direct `file:` loading.

Browser checks from a normal terminal with installed Chrome on macOS:

```sh
FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e
```

Alternatively:

```sh
npx playwright install chromium
npm run test:e2e
```

## Validation results

| Check | Result / evidence |
| --- | --- |
| Unit, state, adapter, schema, and server-rendered shell checks | **PASS: 93 tests in five files** — [unit log](validation/prompt02/unit-tests.txt) |
| Strict TypeScript and production build | **PASS** — [build log](validation/prompt02/build.txt) |
| Browser scenario discovery | Four smoke scenarios supplied; discovery only does not execute a browser — [test listing](validation/prompt02/browser-test-list.txt) |
| Playwright with installed Chrome | **BLOCKED before tests:** Vite cannot bind `127.0.0.1:5173`, `listen EPERM` — [observed error](validation/prompt02/browser-check.txt) |
| Browser interaction / successful WebGL frame | **NOT VERIFIED** in this execution environment |
| Manual visual review / screenshots | **NOT PERFORMED** because the browser/server could not run |
| Target-Mac performance / assistive-technology audit | **NOT MEASURED**; implementation is not a device acceptance result |

The 93 passing checks comprise 27 original contract/provenance tests, 30 state/transport/camera/layer tests, 29 educational package/sampler/animation/collision tests, five keyboard-adapter tests, and two server-rendered UI checks. Coverage includes body-field rejection, generic-ID/reference integrity, independently valid category packages, finite replay bounds, source/evidence matching, seek/fade/pulse behavior, reduced motion, held-input lifecycles, session preservation, stopped physical pose in replay/inspection, directional highlights, world bounds, and swept/landing collision cases.

The UI shell checks render the no-WebGL fallback and disabled controls on the server. They do not validate canvas drawing, browser focus, hit testing, contrast on a display, or animation quality.

## Preview paths and pending manual acceptance

The existing functional preview is [`../dist/index.html`](../dist/index.html), served with `npm run preview`. [Preview instructions](previews/README.md) record the distinction between this generated build and screenshots. No screenshots currently exist. A successful browser-suite run writes:

- `docs/previews/mvp-world.png`
- `docs/previews/mvp-brain.png`
- `docs/previews/mvp-mobile.png`

All requested manual checks remain pending: movement and collision; transparent head; actual region/node clicking; brain orbit/focus/return; inspector content and scrolling; timeline pause/scrub/speed; mode/provenance labels; reduced motion; and absence of false simulation labels. The supplied browser scenarios cover these flows in part; a human should additionally review animation, readability, camera framing, and desktop/mobile feel.

## Performance notes and remaining limits

The scene uses 13 instanced nodes and five memoized system volumes, shared scratch objects for frame updates, memoized limb transforms, capped display/control/behavior histories (120/40/30), no particles, lazy dialogs, DPR <=1.75, and one 1024px shadow map. Text telemetry samples at 10 Hz; rendering metrics update about once per second. No full connectome or anatomical asset is bundled. The overlay waits for actual WebGL samples instead of displaying a fabricated FPS.

The production Three.js chunk remains about 704 kB minified / 180 kB gzip. The renderer chunk is about 448 kB / 140 kB gzip; the application about 163 kB / 46 kB gzip; the lazy dialog about 5 kB / 2 kB gzip. These are build sizes, not memory or runtime measurements. The build reports the existing Three.js size warning and nonfatal Zod comment-annotation warnings.

Recordings are bounded, in memory, and lost on reload. Physics uses conservative cylinders rather than rigid bodies. Replay holds the current physical location. Canvas picking, layout, real FPS, and accessibility still require browser/device acceptance. Scientific source gaps remain unresolved. See [UNRESOLVED](UNRESOLVED.md), [UX_SPEC](UX_SPEC.md), and [SCIENTIFIC_BOUNDARIES](SCIENTIFIC_BOUNDARIES.md).

## Readiness and stop point

The educational implementation is ready for local browser acceptance. It is **not yet accepted as a real-data viewer or biological simulator**. Before real data integration, review the browser MVP and separately specify verified compact packages, source/version identities, body-ID mapping, evidence rules, anatomical assets/transforms, and rendering budgets. No validation result here establishes biological function or simulator validity.

The current work stops at Prompt 02. The source/document/test inventory is [FILES_CHECKPOINT_02.txt](FILES_CHECKPOINT_02.txt). Historical research context remains [read-only and dated](RESEARCH_CONTEXT.md); a scoped hash audit of the 16 inventoried source files is retained in [source-integrity.txt](validation/prompt02/source-integrity.txt).
