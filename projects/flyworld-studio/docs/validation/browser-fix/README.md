# Browser failure follow-up — 8 October 2026

**Later result:** the user's corrected rerun has **8 passed / 1 failed**, including all 13 controls acceptance steps passing. This document preserves the original six-failure investigation. See [the mobile overflow follow-up](../mobile-overflow/README.md) for the remaining failure, sizing fix and focused rerun command.

The user's normal-terminal run executed all nine scenarios: **three passed and six failed**. This supersedes the previous lack of browser evidence; it does not establish full acceptance. The agent's attempted rerun still fails before tests with localhost EPERM.

## Evidence and diagnoses

The original six error-context files are saved in this directory. Original trace ZIPs and screenshots are preserved under .cache/browser-fix-user-run before any rerun. [user-run.json](user-run.json) records the user-reported totals and the controls-step outcomes extracted from test.trace.

1. **Controls scenarios:** the fixed click coordinate (35,200) lands on the Back to world button once inspection navigation appears. The first scenario passed steps 1–11, including movement, both curved paths, tree contact and recovery, then timed out trying to click in step 12. Step 13 was not reached. The second scenario encountered the same obstruction. Its timeout is not evidence that inspection motion failed.
2. **Failure-report cleanup:** the first test's finally block called keyboard.up on the closed page before writing its JSON. This masked the original click timeout and lost the step report.
3. **Catalog rejection:** all three real-data scenarios fail before a package loads. Their saved alert reports regex failures at catalog entries 3 and 4: malecns-lb3b.json and malecns-lb3c.json. The browser filename pattern allowed letters and hyphens but excluded digits. Existing package tests parsed individual packages and never exercised this catalog validator.
4. **Replay control:** the trace shows DATA REPLAY selected, fill(6000) executed, then the controlled slider/display persisted at 100 ms. ActivityPanel used a 100 ms sampled snapshot for controlled values while pause state rerendered immediately; the input's native event also relied on React change-value tracking. The repair makes discrete transport and paused time reactive and handles the range's native input event. Browser revalidation of this fix is still pending.
5. **Visible label overlap:** the controls failure screenshot shows the physics label overlapping the focus badge. Badge/navigation spacing and the narrow-layout diagnostic panel offsets were adjusted. Actual revised layout remains to be checked.

The three passing scenarios were world controls/provenance, brain selection/layers/focus/return, and general package/help/experiment/mobile interface. Existing generated screenshots now represent actual browser output from that user run; they are not newly captured by the agent. No human completion of the full manual acceptance sequence is asserted.

## Changes

- Extracted the browser catalog schema into src/realdata/catalog.ts and allowed digits in local package basenames. Existing path, count, size and checksum guards are retained; scientific payloads are unchanged.
- Added a regression using the actual published manifest, including LB3b/LB3c, plus four nonlocal/unsafe filename rejections. The actual-manifest test failed before the regex fix: [catalog-before.txt](catalog-before.txt).
- Made replay mode, duration, events, pause, speed and paused seek position read current Zustand state. Advancing live time still samples at 100 ms. Range input uses onInput.
- Added a shared browser viewport helper that finds a point with actual DOM hit testing, clicks normally and verifies focus. It does not force clicks or bypass overlays.
- Saved acceptance outcomes before best-effort key-release cleanup, preserving the original failure.
- Strengthened the replay scenario with native Home/ArrowRight input, an exact 6000 ms seek and persistence across two telemetry samples.
- Made real-data setup surface the actual rejection text rather than wait for a missing badge.
- Applied the latest requested direction correction: ArrowLeft maps to LEFT and ArrowRight to RIGHT, reversing the preceding swap. Help and unit/browser yaw assertions agree.

## Validation and remaining gate

- **173 application tests PASS** in eight files: [unit-tests.txt](unit-tests.txt).
- **Strict TypeScript and production build PASS**: [build.txt](build.txt).
- **28 public assets unchanged; all 14 published checksums match**: [data-integrity.txt](data-integrity.txt).
- Nine browser scenarios still supplied: [browser-test-list.txt](browser-test-list.txt).
- Agent browser rerun **BLOCKED before tests**, localhost EPERM: [browser-check.txt](browser-check.txt).
- Full corrected browser acceptance remains **PENDING**, not nine passed. Previous 20 preprocessing passes remain historical; preprocessing was not changed or rerun for this UI/test fix.

Run all nine again from a normal terminal so the shared-helper changes and previously blocked data flows are exercised:

    cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
    FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e -- --headed

No data regeneration, dependency installation, simulator work or server termination is needed.
