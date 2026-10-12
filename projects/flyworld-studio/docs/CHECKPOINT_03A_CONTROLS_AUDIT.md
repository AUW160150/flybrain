# Checkpoint 03A — Controls repair and MVP audit

8 October 2026. Existing repository: /Users/Rodela1/Code/Flybrain/sandbox/flyworld.

**Latest browser evidence:** the user confirmed the corrected anatomy/mobile scenario passes. Together with the prior eight passing scenarios, all nine now have passing results; all 13 automated controls steps passed with no page errors. This closes automated verification, without claiming a new full-suite run or human visual acceptance. See [the mobile follow-up](validation/mobile-overflow/README.md). Human visual review remains pending. The original agent-execution results below are retained as history.


**Controls repaired and verified at the input-adapter/state/physics level. Application tests and production build pass. Browser and manual visual acceptance remain BLOCKED, not passed. No neural simulation was added.**

## Target and checkpoint assessment

FlyWorld's target is a scientific and educational workspace for exploring a virtual Drosophila body, brain, circuits and, eventually, separately validated experiments. The present deliverable is a reliable user-controlled procedural fly, explicitly educational activity/replay, and bounded source-backed MaleCNS inspection. Neither the avatar nor its keyboard motion is an autonomous biological fly.

Read AGENTS, STATUS, PRODUCT_NORTH_STAR, SCIENTIFIC_BOUNDARIES, DECISIONS, UNRESOLVED and all three checkpoints before making changes. Checkpoint 01 supplied the foundation (52 tests); 02 added educational interaction (93); 03 added bounded real data (135 application and 20 preprocessing tests). Those historical checkpoints consistently marked browser acceptance as pending. Passing their unit/build checks did not establish successful rendered interaction.

This repair is the appropriate next task. Reliable control, focus and observable movement are prerequisites for useful exploration. Adding a simulator would not resolve the identified input defects or close the browser acceptance gap.

## Root cause and evidence

The original 135 application tests passed again. A new six-case regression probe then reproduced four failures; [before-repair evidence](validation/prompt03a/regression-before.txt) is retained:

- W already advanced the state by 4.2 world units in two seconds from a single keydown.
- ArrowUp and ArrowDown were absent from the input mapping. Their key events caused no translation. ArrowUp produced Z = 0 where W produced Z = 2.1 in one second.
- The keydown adapter rejected every event with Shift held. Shift+W therefore also produced zero translation.
- The integrator clamped world bounds before collision resolution. At the boundary, forward motion stopped while collision telemetry incorrectly reported CLEAR.
- Tree penetration prevention and recovery by backing away already passed. No persistent collision-induced speed-zero defect was reproduced.

Additional audit findings: there was no explicit active-controls state, document focus changes did not clear held movement, and action booleans could not preserve independent physical-key aliases. Animation selection prioritized turning and timed gestures over actual translation; a blocked fly could still display a walking gesture. Focus-visible CSS could raise the canvas over sibling controls. These paths have been corrected, but the CSS/rendered result still requires browser review.

The demonstrated translation failure is the missing arrow bindings and Shift rejection. A separate failure of unmodified W to move the rendered avatar cannot be diagnosed from the available evidence. In Follow mode the camera also tracks the fly; position telemetry and movement relative to the environment should be checked together during visual acceptance.

## Repairs and supported controls

| Input | Result while the world viewport has focus |
| --- | --- |
| W / ArrowUp | Hold forward relative to current heading |
| S / ArrowDown | Hold backward relative to current heading |
| A / ArrowLeft | Hold left turn |
| D / ArrowRight | Hold right turn |
| Movement + turn | Continuous curved path, including W+A and ArrowUp+ArrowRight |
| Shift | Hold either Shift key for 1.75× translation speed |
| X | Clear movement; a fresh movement press is required |
| Space | Existing takeoff/land behavior |
| F / G / E / C | Existing feed/groom/escape/courtship gestures |
| B / P | Transparent head / activity timeline transport |
| Tab / Escape | Brain inspection / return to the previous world camera |
| Shift+Tab | Native backward focus navigation |

A stable input-state Set retains physical key codes; the movement pad has separate ownership. Releasing one alias leaves other held aliases and pad input intact. Key repeats neither drive motion nor restart cleared controls. The existing requestAnimationFrame clock integrates delta time once; no additional frame loop was introduced.

Clicking the viewport activates controls. CONTROLS ACTIVE requires viewport focus, USER CONTROL and a world camera. Moving focus to a form, dialog or another control releases held movement. Window blur, document hiding, mode/camera changes and Stop clear input. Keyboard shortcuts leave editable targets and native dialogs alone. Arrow repeats prevent scrolling only while world controls are active. Listeners are registered once per mount and removed during cleanup, including StrictMode remounts.

The movement pad remains independently usable by mouse/touch and focused Space/Enter. Its pointer press focuses the button before acquiring movement so a focus-loss release cannot erase the new press. Opening MaleCNS data explicitly deactivates world controls. Its feeding button remains available; the obsolete F shortcut hint was removed because world shortcuts now require the world viewport.

Both Fly and Brain inspection pause position, heading and flight height, with no background-motion option. Return to a world camera, click the viewport and press movement again.

Motion integrates constant-speed turning arcs, with collision as the single owner of world clamping. Collisions never overwrite requested speed or held input. Measured forward/turn speeds come from displacement after collision resolution; they are arbitrary game units, not calibrated biomechanics. Large time gaps remain capped at 50 ms per update.

The visible movement state distinguishes IDLE, WALK_FORWARD, WALK_BACKWARD, TURN_LEFT, TURN_RIGHT, WALK_TURN, FLY, COLLISION_BLOCKED and BRAIN_INSPECTION_PAUSED. Additional labels cover Fly inspection and rule/replay in place. The existing authored gesture/replay vocabulary is unchanged. Moving limbs take precedence over a still-timed gesture; fully blocked translation no longer selects a walking gait.

Performance mode displays pressed movement/Shift keys, pad inputs, XYZ, yaw, measured forward and turn speeds, movement state, avatar gesture, camera, collision, controls focus, focused element and brain target. Motion samples at 100 ms; actual WebGL metrics retain their one-second sampling. Focus diagnostics show element identity rather than typed contents. The panel scrolls on constrained layouts.

All user activity retains USER_DRIVEN_ILLUSTRATION.

## Feature audit — what the evidence establishes

| Feature | Verified in this audit | Remaining browser acceptance |
| --- | --- | --- |
| Translation | Held W, identical ArrowUp, backward S/Down, heading-relative movement, release, boost and mixed inputs | Visible advancement relative to world |
| Rotation | A/Left-arrow and D/Right-arrow have opposite yaw; movement and turning combine | Perceived left/right direction and camera feel |
| Four cameras | State transitions, previous-world return and both inspection pauses pass | Framing, orbit, zoom, easing and picking |
| Keyboard focus | Activation adapter, native-input guards, release, aliases, scrolling prevention and listener cleanup pass | Actual DOM focus, hit testing, scroll and touch; supplied browser checks did not run |
| Collision | All existing obstacle sweep/landing tests, world-edge contact, tree blocking and turn-away recovery pass | Tree appearance and collision feel |
| Transparent head | Toggle/preference retention through inspection passes | Transparency rendering and head/brain clicking |
| Behavior buttons | All six command handlers preserve provenance; takeoff/flight/land and gesture transitions pass | Actual button interaction and limb quality |
| Circuit packages | 42 real-data tests and 20 offline tests pass; all published checksums match | Interactive package selection, graph filters and inspector |
| Anatomy | Native geometry receipts/topology/schema tests and cache hashes pass; assets unchanged | Actual morphology loading/rendering |
| Activity/replay | Existing timing, pause/seek/speed, recording, original provenance and stationary replay tests pass | Timeline usability and visual highlights |

Tests for keyboard targets use an adapter fixture, not a browser DOM. Server-rendered UI checks validate labels and fallback output, not WebGL. No feature above is called visually working merely because its UI exists.

## Validation results

| Check | Result |
| --- | --- |
| Baseline application tests | 135 PASS — [baseline](validation/prompt03a/baseline-tests.txt) |
| Before-repair regression probe | 4 reproduced failures, 2 passes — [evidence](validation/prompt03a/regression-before.txt) |
| Final application tests | **168 PASS in seven files** — [log](validation/prompt03a/unit-tests.txt) |
| Offline preprocessing tests | **20 PASS** — [log](validation/prompt03a/preprocessing-tests.txt) |
| Strict TypeScript and production build | **PASS** — [log](validation/prompt03a/build.txt) |
| Data integrity | **PASS**: 28 unchanged public assets, 14 published checksums, 22 pinned source hashes — [audit](validation/prompt03a/data-integrity.txt) |
| Browser scenario discovery | Nine scenarios in three files — [listing](validation/prompt03a/browser-test-list.txt) |
| Browser smoke execution | **BLOCKED before tests**, Vite bind EPERM 127.0.0.1:5173 — [log](validation/prompt03a/browser-check.txt) |
| Independent installed-Chrome launch | **BLOCKED**, browser exits SIGABRT — [log](validation/prompt03a/browser-launch.txt) |
| Manual visual acceptance / screenshots | **NOT PERFORMED**; no browser launched successfully |

The 168 tests include 18 keyboard-adapter tests and 19 locomotion tests. Together they cover all 12 requested automated conditions; actual clicking and browser scrolling also have supplied Playwright assertions. Straight and curved two-second paths agree across 30/60/120 FPS to nine decimal places in the collision-free tests. This is a deterministic model result, not a browser FPS measurement.

The existing dev server was observed listening from this same project (PID 81908); it was not killed or replaced. An initial HTTP request succeeded, but sandboxed Playwright could not reuse it and its attempted bind failed. See [server observation](validation/prompt03a/server-observation.txt) and [HTTP observations](validation/prompt03a/server-http.txt). This does not establish browser access. The prior port-in-use report therefore does not require killing an unknown process: use the existing project server, or Vite's printed fallback port.

The build retains its prior nonfatal Zod annotation warnings and approximately 704 kB Three.js chunk warning. No dependency was added.

## Exact manual acceptance sequence and outcomes

All rows below are **NOT RUN in a browser** because both server/test startup and the independent browser launch were blocked. Unit assertions provide related evidence but do not replace these manual outcomes.

| Step | Requested action/observation | Manual result |
| --- | --- | --- |
| 1 | Start in Follow mode | NOT RUN |
| 2 | Click the 3D viewport | NOT RUN |
| 3 | Hold W for 2 seconds | NOT RUN |
| 4 | Confirm position changes and visible advance | NOT RUN |
| 5 | Hold A while still holding W | NOT RUN |
| 6 | Confirm a curved left path | NOT RUN |
| 7 | Repeat with ArrowUp + ArrowRight | NOT RUN |
| 8 | Walk into the tree | NOT RUN |
| 9 | Confirm collision prevents penetration | NOT RUN |
| 10 | Turn away and move again | NOT RUN |
| 11 | Enter Brain mode | NOT RUN |
| 12 | Confirm locomotion pauses | NOT RUN |
| 13 | Return to Follow mode and move again | NOT RUN |

[controls.spec.ts](../tests/e2e/controls.spec.ts) encodes this ordered sequence using public keyboard/pointer events and observed telemetry, including steering toward the tree without injecting a pose. A successful run will write browser-acceptance.json under this validation directory and controls-forward/left/tree/brain/return.png under docs/previews. These files were **not generated here**. Automated browser success would still need a human review of visible advance, curved paths and animation feel.

## Data and anatomy status preserved

Dataset remains male-cns:v1.0 / v1.0 / UUID 4b2087c0fbe046bfaf0d60bc970e3e5d. The eight packages retain bodies/edges: focused 110/1923, paper-associated 102/274, candidates 12/0, LB3b 11/43, LB3c 23/221, motors 10/29, sugar-selected 0/0 and separate anatomy 3/0. The custom example remains 2/2.

None of the requested 110 circuit bodies has local verified morphology. The separate source-backed anatomy bodies remain 10093, 10807 and 11369, in native coordinates with unverified orientation. Placeholder brain geometry is still explicitly labelled. Puddle remains unassigned; validated sugar selection remains absent. No source lock, schema, scientific package, anatomy asset or behavior mapping configuration changed. The research repository was read only; integrity evidence is scoped to the 22 pinned files, not every research file.

## Files changed and next step

Runtime: controls/input.ts (new), controls/keyboard.ts, controls/MovementPad.tsx, state/store.ts, fly/motion.ts, fly/animation.ts, app/App.tsx, ui/DebugOverlay.tsx, ui/WorkspaceDialog.tsx, ui/styles.css and the single feeding-button label in realdata/RealDataWorkspace.tsx.

Tests: keyboard.test.ts, locomotion.test.ts (new), support/keyboard.ts (new), state.test.ts, ui-shell.test.ts, e2e/controls.spec.ts (new), e2e/foundation.spec.ts and e2e/realdata.spec.ts. Documentation: this checkpoint, STATUS, README, DECISIONS, UNRESOLVED, PRODUCT_NORTH_STAR, UX_SPEC, ARCHITECTURE, preview notes and validation artifacts. [Complete changed-file inventory](FILES_CHECKPOINT_03A.txt).

Remaining limits: browser/manual acceptance is open; control feel, mobile overlap, touch and accessibility need actual review. Focus loss/Stop/behavior commands intentionally require releasing and pressing movement again. World collisions remain conservative game cylinders; long frames are capped rather than caught up. No neural dynamics or background motion in inspection is available.

Next, refresh the existing dev page or run npm run dev and open the printed Local URL. Choose USER CONTROL and Follow, click the viewport, enable Performance if needed, and perform the 13 steps above. From a normal terminal:

    cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
    FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e

The browser suite uses port 5173; it reuses a matching server there or starts Vite with strictPort. The interactive dev command itself retains fallback ports. After the nine browser scenarios pass, record the human visual review in this checkpoint. Only then scope another development milestone; anatomy acquisition, scientific selection and any future simulation require their own source/validation work. Stop here at the controls repair.

## User follow-up — arrow directions

On 8 October the user requested swapping left/right arrows. The current controls table, shortcut help, yaw assertions and ArrowUp+ArrowRight browser expectation now reflect that change. A/D retain their original bindings. The original audit history and unperformed manual results remain as recorded. Follow-up validation logs are in validation/prompt03a/arrow-swap-*.txt.

Follow-up checks: 168 application tests PASS; strict TypeScript and production build PASS; nine browser scenarios discovered. Browser execution/manual acceptance remains pending as documented above.

Latest direction correction (8 October): the user reported the swapped right arrow turned left and requested another reversal. ArrowLeft now maps to LEFT and ArrowRight to RIGHT, matching A/D. This supersedes the preceding arrow-swap note; current help and yaw assertions match.
