# Takeoff and courtship follow-up — 8 October 2026

The user reported both behaviors were not working. Existing state tests already showed takeoff reaching height 1.65 and landing returning to ground; no disabled physical takeoff path was reproduced. Code inspection identified two presentation gaps: world cameras followed the entire vertical displacement, leaving the fly at almost the same screen height, and courtship only adjusted both wings' roll for 2.4 seconds. Inspection/replay disabled commands without explaining the reason beside the buttons; the data workspace left commands enabled while hiding the avatar. The user's exact failing interaction was not captured, so visual resolution is not yet confirmed.

World cameras now retain a ground-height target, while inspection targets the body's actual altitude. Flight opens both wings; courtship extends one wing laterally with a brief unfold/refold. Reduced motion uses distinct static poses. All poses remain scripted placeholder gestures with USER_DRIVEN_ILLUSTRATION; no anatomical or functional claim is added.

The panel reads behavior, airborne and mode changes synchronously, shows the current gesture, and explains disabled controls. Enable behavior controls explicitly returns to world USER CONTROL. The world footer shows height in scene units. Keyboard shortcuts still require viewport focus. Activity-timeline pause remains separate from physical behavior.

Verification:

- `npm test`: **177 passed**, including four new behavior regressions. They measure rendered-geometry wing endpoints, test Space/repeat/landing and C, static reduced-motion poses, and physical behavior with the activity timeline paused.
- `npm run build`: **passed**, including strict TypeScript. Existing dependency annotation/chunk-size warnings remain.
- `npm run test:e2e -- tests/e2e/behaviors.spec.ts --output=test-results-behaviors`: **blocked before tests** by `listen EPERM: operation not permitted 127.0.0.1:5173`.
- The suite now contains ten browser scenarios. Prior nine-scenario passing evidence is historical. The new scenario checks button/keyboard behavior, altitude, gesture feedback, inspection/replay/data-workspace recovery, reduced-motion feedback and narrow layout; it saves airborne and courtship screenshots for human review. It does not assert pixel-level animation correctness.

Focused browser verification on the user's machine:

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e -- --headed tests/e2e/behaviors.spec.ts
```

Visually check Take off → Land in Follow and Orbit, then Courtship on the ground with reduced motion off and on. Confirm visible ascent/descent, one-wing extension/refolding and no horizontal displacement from courtship alone. Scientific packages, public assets, anatomy audit caches and source research files were not edited.
