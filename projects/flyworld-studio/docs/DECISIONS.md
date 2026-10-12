# Decisions

Recorded 7 October 2026 for Prompt 01.

| ID | Decision and reason |
| --- | --- |
| D001 | Create a separate Git repository at `sandbox/flyworld`. Root `flyworld/` already contains an unrelated Python implementation; the example home path is outside writable roots. |
| D002 | Treat `Sugar/malecns_sugar_circuit_v1` as read-only scientific context. Consult the latest status/manifests after the dated checkpoints so recovered method sections are not incorrectly described as wholly unavailable. |
| D003 | Use procedural fly/body/environment and three arbitrarily named display volumes. No reconstructed meshes are supplied; the consulted visualization reports 0 authentic SWCs. |
| D004 | Use React 19 + stable Fiber 9 + drei 10 with ordinary WebGL. Keep `WorldCanvas` as the backend boundary; do not introduce WebGPU requirements. The lockfile records exact tested versions. |
| D005 | Separate held physical inputs, behavior commands, and scalar display frames. Source labels are mandatory, and simulation/replay frames fail the MVP runtime boundary. |
| D006 | Add schema version 1, resource limits, string body IDs, reference integrity checks, and required provenance presence. A schema pass remains distinct from scientific verification. |
| D007 | The demo has 0 neurons and 0 edges. Display names A/B/C carry no roles. A JSON validator is exposed, but the biological package renderer is deferred at the required stop point. |
| D008 | Both inspection modes pause locomotion. Preserve the previous world camera and head-toggle preference; entering inspection clears held input. |
| D009 | Tab inspects only while the viewport is focused. Native keyboard navigation and dialog/input behavior are preserved elsewhere. Add visible equivalents and X to stop. |
| D010 | The activity clock pauses separately from movement. During pause, suppress new overlays rather than assigning later timestamps to earlier commands. Control events continue to be recorded at the frozen display time. |
| D011 | No replay demo is necessary for Prompt 01. Reserve the contract but reject replay frames until a source-aware adapter is implemented. |
| D012 | Direct npm DNS failed in the restricted session. A temporary ignored helper hydrated a local npm cache using permitted registry downloads; normal package/lockfile registry URLs were retained. No runtime dependency on this helper exists. |
| D013 | Do not claim browser success. Vite binding failed with EPERM and installed Chrome aborted with SIGABRT. Ship smoke tests and exact normal-local commands; retain these observed limits in the checkpoint. |

Technical reference for D004: [Fiber installation and React-version pairing](https://r3f.docs.pmnd.rs/getting-started/installation). Runtime requirements: [Vite 7 release](https://vite.dev/blog/announcing-vite7). The selected package versions are stable major lines, not a claim to use every latest major release.

## Prompt 02 — 7 October 2026

Prompt 02 explicitly authorizes the educational expansion and synthetic/session replay; it supersedes the corresponding Prompt 01 implementation limits, without authorizing biological integration or simulation.

| ID | Decision and reason |
| --- | --- |
| D014 | Reuse the existing repository. Baseline verification passed 52 tests and the production build; Prompt 01's optional browser check was unsupported, not an unimplemented foundation feature. |
| D015 | Keep `CircuitPackage` for future biological records and add a separate strict `DemoCircuitPackage` with generic IDs and no body-ID, synapse, or transmitter fields. This extends D007 without weakening scientific identity rules. |
| D016 | Five named systems and 13 generic nodes represent teaching categories only. Eight authored relations are explicitly illustrative; five downloadable category packages contain only their own entities and internal relations. No sourced anatomy or function is assigned. |
| D017 | Separate playback mode from original activation provenance. DATA REPLAY labels transport; bundled events retain RULE_DRIVEN_EDUCATIONAL, and session events retain USER_DRIVEN_ILLUSTRATION. This replaces D011's deliberate omission of replay. |
| D018 | Record bounded, timed events rather than unbounded frame arrays. Sampling is deterministic under reverse seek. Scrubbing live history enters session replay, avoiding accidental rewriting of old live events. Paused live commands do not retroactively create overlays. |
| D019 | Reconstruct replay gestures in place, not physical trajectories. Physical pose remains user-driven and collision-controlled. The rule/demo event includes an explicit gesture command; intensity never causes movement. |
| D020 | Share object placement and conservative cylinder definitions between renderer and collision module. Use swept horizontal checks plus landing-overlap resolution and hard world bounds. This is game physics, never brain-driven avoidance. |
| D021 | Reduced motion disables rhythmic overlays and optional avatar/camera motion, while retaining direct control, static gesture poses, and fades. Initialize from the platform preference and expose an explicit user toggle. |
| D022 | Use the Okabe–Ito palette subset with text, symbols, and light selection outlines. Keep glyph text light against the dark background; colored underlines supplement rather than replace it. Reference: https://jfly.uni-koeln.de/color/index.html |
| D023 | Instance all 13 demo neurons, cap record/highlight counts, memoize stable objects, and lazy-load dialogs. Report measured frame statistics only when WebGL runs; do not publish an invented laptop FPS result. |
| D024 | Preserve the browser-verification limitation: Prompt 02's Playwright attempt still fails at Vite binding with EPERM. Add unit/adapter and server-rendered fallback checks, but do not call them browser, visual, or manual acceptance tests. |

## Prompt 03 — 7 October 2026

| ID | Decision and reason |
| --- | --- |
| D025 | Continue in the existing repo: both MVP implementations and unit/build checkpoints were complete; browser acceptance was explicitly unsupported. The user's Prompt 03 authorizes real-source integration, not neural dynamics. |
| D026 | Pin 22 read-only source files and one structural run. Guard saved metadata, manifests, dataset/version/UUID and hashes before generation; reject changed selected-result state instead of guessing an adapter. No Internet queries. |
| D027 | Use schema 3 for real imported data, retaining the biological scaffold and generic demo separately. Preserve raw metadata, nulls, side provenance, both transmitter fields, raw weights, source hashes and ledger warnings. |
| D028 | Match source-focused inclusion exactly (110/1923), saved paper motif (102/274) and independent candidate comparison (12/0). LB3b/LB3c/motors use all verified type members with induced raw edges. |
| D029 | Keep sugar-selected empty and UNRESOLVED; reject selected-connectivity labels until a validated adapter exists. Puddle remains unassigned. No raw paths replace selected output. |
| D030 | Search cached local anatomy rather than assume all geometry is missing. Eight canonical SWCs exist elsewhere; only three have source-run body matches, none overlaps the 110 requested bodies. Import those three separately as ANATOMY_ONLY; preserve exact cables/native coordinates and unverified orientation. |
| D031 | Use standard-library Python streaming over the 347 MB extracted edge CSV offline. Do not read/copy the 1 GB full graph; its hash is inherited explicitly from the frozen manifest. CLI safety overrides may narrow budgets, never silently truncate data. |
| D032 | Lazy-load one bounded package; use SVG directional diagrams, population cards, raw tables and selected-body batched morphology. Cap drawn arrows visibly at 300 while retaining the complete edge table. Partner summaries are IN-PACKAGE ONLY. |
| D033 | Custom files use strict size/schema/identity/reference guards and an explicit supplied-provenance limitation. No comparison mode or implicit cross-dataset merge is added. |
| D034 | Keep educational behavior mappings outside scientific data. Only FEED maps source-labelled motors, with user provenance, author/date/source/confidence/review metadata and no physiological claim. Other real-body mappings remain absent. |
| D035 | Produce static server-rendered HTML and an offline native X/Z plot where browser capture is blocked. Label them explicitly; do not claim WebGL, browser FPS or interactive acceptance from those artifacts. |

## Checkpoint 03A — 8 October 2026

| ID | Decision and reason |
| --- | --- |
| D036 | Repair the existing control path before another milestone. Before-repair tests reproduce absent Up/Down mappings, Shift rejection and concealed world-edge contact; plain held W and tree recovery already pass. Do not claim an unproven renderer or persistent-speed root cause. |
| D037 | Store physical key codes in a Set and aggregate them with separate movement-pad inputs. Scope keyboard input to viewport focus, USER CONTROL and world cameras; release on focus/window/visibility loss and transitions. Preserve native form/dialog input, independent aliases and listener cleanup. |
| D038 | Integrate constant-speed turning arcs with delta time and retain the 50 ms long-frame cap. Let collision alone clamp world bounds and measure speeds after resolution. Preserve requested input at contact so turning/backing away can recover. |
| D039 | Expose actual locomotion state separately from authored gesture/replay animation. Prefer moving limbs over an old timed gesture; show collision blocking and inspection pause explicitly. Add a focus badge and observable input/pose/speed diagnostics without changing scientific activity schemas. |
| D040 | Keep browser/manual acceptance open. Nine scenarios are supplied, but Playwright bind EPERM and direct Chrome SIGABRT prevent execution. Record all 13 manual steps as NOT RUN and do not substitute unit tests or static previews for visual acceptance. |
| D041 | Preserve every public asset and scientific configuration. All 28 public assets, 14 published checksums and 22 pinned source hashes match. World-only shortcuts remove the misleading F hint on the data workspace's feeding button; the button and educational mapping remain intact. No simulator or anatomical replacement is introduced. |
| D042 | On 8 October the user explicitly requested swapping left/right arrows. ArrowLeft now maps to RIGHT (negative yaw), ArrowRight to LEFT (positive yaw); A/D retain their bindings. Update shortcut help and existing unit/browser assertions to match. |

## Browser failure follow-up — 8 October 2026

| ID | Decision and reason |
| --- | --- |
| D043 | Preserve actual user browser evidence: 3 passed / 6 failed, controls steps 1–11 passed, step 12 blocked by an overlay click. Supersede the absence-of-evidence status without claiming complete visual acceptance. |
| D044 | Extract and test the browser catalog validator against the shipped manifest. Permit digits in local package basenames so LB3b/LB3c load, retaining all scientific payload, checksum, path and resource guards. |
| D045 | Read transport edits and paused seek position directly from the store while sampling advancing time. Use native range input; validate keyboard scrubbing and persistence through telemetry updates in the browser scenario. |
| D046 | Find unobstructed viewport points with DOM hit testing; do not force clicks through navigation controls. Write acceptance results before best-effort keyboard cleanup so a closed page cannot mask the original failure. |
| D047 | The latest user direction correction supersedes D042: restore ArrowLeft → LEFT and ArrowRight → RIGHT. This reverses the immediately preceding arrow behavior and aligns arrows with A/D and their diagnostic states. |
| D048 | Record the user's 8-pass/1-fail rerun and all 13 automated controls steps passing. Address the remaining mobile overflow by making nested form grid tracks and native controls shrink to their containers. Keep the strict document-width assertion, poll after resize, and attach width diagnostics. The failure trace shows a fitting morphology canvas but does not identify the exact overflowing element; the sizing fix awaits browser verification. |
| D049 | Accept the user’s confirmation that the final anatomy/mobile scenario passes, supported by the local Playwright last-run status. Combined with the earlier eight passing scenarios, automated verification is complete. Preserve the distinction between results across runs, a fresh full-suite run, and human visual review; do not infer a new development scope. |

## Prompt 04A — 8 October 2026

| ID | Decision and reason |
| --- | --- |
| D050 | Execute the user-authorized anatomy audit within the existing project. Preserve prior browser acceptance and keep remaining human visual review separate from scientific anatomy evidence. |
| D051 | Use the full official v1.0 annotation table and exact official per-body receipts to verify eight incidental cached SWCs. The focused requested set still has 0/110 geometries; five additional cache identities do not change circuit membership or browser packages. |
| D052 | Preserve original source bytes and create separate content-addressed raw copies and lossless audit conversions. Test all numeric SWC fields, topology, units and provenance; no anatomy is registered, simplified, mirrored or publicly imported. |
| D053 | Record the first public official test request as DNS-blocked and the remaining four as unattempted. Keep raw XYZ/unit scale, anatomical orientation, historical segmentation UUID and neuPrint dataset UUID separate. Prepare exact Prompt 04B recovery instructions and stop after the audit. |

## Takeoff/courtship follow-up — 8 October 2026

| ID | Decision and reason |
| --- | --- |
| D054 | Preserve working physical takeoff/landing and repair presentation: world cameras track horizontal position with a ground-height target; inspection still targets the actual airborne body. Open both flight wings and give the 2.4-second authored courtship gesture a lateral single-wing extension. These are placeholder educational poses, not biological kinematics or autonomous behavior. |
| D055 | Show immediate behavior/toggle state, scene height and reasons for disabled controls. Explicitly returning via Enable behavior controls restores world USER CONTROL; do not execute hidden gestures from the data workspace or silently resume inspection/replay. Keep native button/form focus and explain that keyboard shortcuts need viewport focus. |
| D056 | Add geometry-endpoint and input/state regression checks plus a dedicated browser scenario. Report 177 application tests/build passing and browser startup EPERM separately. Prior nine-scenario acceptance does not verify the new visuals; the user's precise original failing interaction remains unconfirmed. |

## User-authorized recovery and on-demand circuit atlas — 8 October 2026

| ID | Decision and reason |
| --- | --- |
| D057 | Execute the user's approval of a full searchable catalogue and on-demand viewer. This supersedes the prepared 04B audit-only runtime stop within the approved scope. Preserve prior audit evidence and scientific packages; keep training, dynamics, functional selection and avatar registration outside this delivery. |
| D058 | Index exact pinned source-status Traced neurons and their induced raw graph in a server-only SQLite database: 165,122 neurons and 25,563,197 edges. Use precise scope instead of treating rounded 167K as a verified brain-only count. Page queries and bound each view to 24 neurons; never ship the full index to the browser. |
| D059 | Recover the five prepared native SWCs through the public official v1.0 bucket, then cache bounded source-backed requests on demand. Use public sharded synapse annotations and original aggregate tables rather than requiring a neuPrint credential. Validate IDs, bytes, formats, confidence, ranges, checksums and shard ETags; preserve errors and source disagreement. |
| D060 | Use one native coordinate origin with uniform conversion to µm: SWC/synapse XYZ ×0.008 and nm meshes ×0.001. Retain official coarse skeletons and contact positions. Simplify only source reference surfaces using a labeled 2-µm clustering preview. Keep anatomical direction, historical mutation alignment and avatar registration unverified. |
| D061 | Freeze new receipts, coverage and integrity evidence separately under validation/circuit-atlas; do not rewrite historical 04A claims or copy recovered assets into the prior public packages. Five sampled strongest-partner contact totals agree exactly with the source graph; this is not global or physiological validation. |
| D062 | Add the eleventh browser scenario for catalogue search, five-body anatomy, expansion, contact filtering, aliases, mobile layout and world return. Record 199 application tests, 20 preprocessing tests, 18 anatomy tests and build passing; localhost EPERM blocks browser execution. Do not reuse earlier browser acceptance or offline parser checks as visual acceptance. |
