# Checkpoint 01 — Foundation

7 October 2026. Project: `/Users/Rodela1/Code/Flybrain/sandbox/flyworld`.

**Implementation and unit/build verification complete. Browser validation unavailable in the creation sandbox. Stop before real dataset integration or neural simulation.**

## What is implemented

- A local React/TypeScript/Vite application using stable React Three Fiber, drei, Three.js WebGL, and Zustand, with a lockfile and separate Git repository.
- A procedural low-poly fly with body, six animated legs, wings, eyes, antennae, and an animated feeding appendage in a small ground-grid environment.
- Forward/backward movement, turning, stop, takeoff/land, feed, groom, and escape animations. Explicit keyboard/pointer events carry `CONTROL MODE: USER` and user provenance.
- Follow/orbit/fly-inspection/brain-inspection cameras, eased transitions, orbit/zoom, breadcrumb, previous-world-mode return, and paused locomotion in inspection.
- Transparent head, visible placeholder brain, clickable display volumes, metadata inspector, persistent geometry warning, scientific-status badge, and native information dialogs.
- A separate display clock, pause/resume, labeled user overlays, and a fixed educational A/B/C pulse rule. No activity output drives motion.
- Typed contracts, runtime package validation, resource caps, reference checks, string body IDs, separate transmitter fields, and explicit rejection of unsupported simulator/replay activity modes.
- Documentation, read-only source inventory, unit tests, and two browser smoke tests.

The state behavior and validation boundaries are tested. The compiled renderer and UI are implemented but cannot be described as visually verified until the blocked browser check runs outside this sandbox.

## What is placeholder

All fly, head, brain, and environment geometry; world units; movement speed; behavior timing; wing/leg/feed/escape animation; and display volume colors/positions. A/B/C have no anatomical or functional identity. The event strip is a control log, and its decorative tick heights do not encode neural amplitudes. Pulse intensities are dimensionless illustrative values.

Visible label: `PLACEHOLDER_GEOMETRY — NOT ANATOMICAL DATA`.

## What is scientifically verified

**No rendered anatomy, neural activation, circuit membership, or physiological function is verified by FlyWorld.** The demo intentionally contains zero neurons and zero edges, and no body IDs or transmitter assignments.

The source repository's saved dataset identity and dated research status were inspected as context, not revalidated. The latest workflow manifest states no frozen selection method, biological selected-circuit run, or simulation. Its visualization build records no actual SWCs. Exact references and hashes are in [RESEARCH_CONTEXT](RESEARCH_CONTEXT.md) and [the context manifest](research-context-manifest.json). No source research file was modified.

## Exact commands

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. Use Node >=22.12.0 and a WebGL 2 capable browser. The creation environment used Node 26.4.0 / npm 11.18.0. For a reproducible reinstall use `npm ci`.

```sh
npm test
npm run build
npm run preview
```

Preview: <http://127.0.0.1:4173>.

```sh
npx playwright install chromium
npm run test:e2e
```

An installed Chrome alternative on macOS:

```sh
FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e
```

## Verification results

| Check | Result |
| --- | --- |
| Dependency installation | PASS — 170 packages installed from hydrated local npm cache after direct npm DNS failed; standard registry URLs retained in lockfile |
| `npm test` | PASS — 52 tests in 3 files: 27 contract/provenance tests, 20 state/motion/camera tests, 5 keyboard-adapter tests |
| `npm run build` | PASS — strict TypeScript check and Vite production bundle |
| `npm run test:e2e` with installed Chrome | BLOCKED — Vite server cannot bind `127.0.0.1:5173`: `listen EPERM` |
| Direct Chrome launch probe without Vite | BLOCKED — installed Chrome exits `SIGABRT` under current sandbox |
| Browser screenshot / visual review | NOT PERFORMED — no successful browser launch |

Unit coverage includes valid/invalid/oversized packages, duplicate or dangling references, precision-safe IDs, source requirements, preserved transmitter distinctions, user/rule activity provenance, rejection of simulation labels, motion/flight/stop, event lifecycles, separate timeline pause, inspection pause, camera return, cleared held input, and bounded movement/history.

Known nonfatal build messages: Three.js exceeds the default 500 kB chunk warning; Zod source comments cause Rollup annotation warnings. The Three.js bundle is approximately 704 kB minified / 180 kB gzip and contains no scientific dataset. Logs are retained under `docs/validation/`.

## Files created

[FILES_CREATED.txt](FILES_CREATED.txt) is the complete project source/document/test inventory. Generated `node_modules`, `dist`, temporary dependency-download caches, Git internals, and Playwright diagnostic artifacts are excluded.

The requested directories exist: `docs`, all three asset namespaces, demo data, `src/app`, `world`, `fly`, `brain`, `circuits`, `activity`, `controls`, `inspector`, `experiments`, `data`, `state`, `ui`, `utils`, `scripts/preprocess`, and `tests`. Required product/science/architecture/data/UX/roadmap/decision/unresolved/checkpoint documents are present. No preprocessing or simulator implementation was added.

## Next recommended step

Run `npm run dev` and the browser smoke tests from a normal local terminal, then review fly framing, transparent-head clicking, camera transitions, focus behavior, and performance on the target Mac. The smoke tests check actual WebGL readiness, movement, inspection/return, source labels, file validation, and narrow-screen overflow.

After reviewing this foundation, request the next milestone with explicit source-backed compact-package and anatomy requirements. No real dataset integration or neural simulation has been started.
