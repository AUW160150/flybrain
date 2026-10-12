# Mobile overflow follow-up — 8 October 2026

The user's initial post-repair suite run reported **8 passed / 1 failed**. Both controls scenarios, all four foundation scenarios and the first two real-data scenarios pass. The [saved controls report](controls-acceptance-before.json) records all 13 acceptance steps passing with no page errors. Human visual review remains pending.

The final scenario loads native morphology and passes the provenance/orientation checks, then fails because document width exceeds the 390×844 viewport. The preserved trace shows the morphology canvas at left 39, right 351, width 312; it fits. The original test did not record widths for other elements, so the exact overflowing element is unconfirmed. See [user-run.json](user-run.json) and [error context](user-error-context.md). Original trace and screenshot are preserved in `.cache/mobile-overflow-user-run`.

The repair gives real-data form labels an explicit `minmax(0, 1fr)` grid track and constrains native selects/inputs to their container width with a zero minimum width. This addresses intrinsic sizing of long source labels. The browser scenario still requires document width ≤390, now polling for resize layout to settle. It also checks field bounds and attaches `mobile-layout` JSON with overflowing element widths, including on assertion failure.

- **173 application tests PASS:** [unit-tests.txt](unit-tests.txt).
- **Strict TypeScript and production build PASS:** [build.txt](build.txt).
- **Focused browser rerun BLOCKED before tests:** sandbox localhost EPERM, [browser-check.txt](browser-check.txt).
- **Mobile fix browser verification PASS, user-confirmed on 8 October 2026.** The user replied “yes it passed” after the focused rerun request. The local Playwright last-run record reports passed with no failed tests. Together with the prior eight passing scenarios, all nine now have passing results; no new full-suite run or human visual acceptance is inferred. See [confirmation](user-confirmation.json). Scientific data and control bindings are unchanged.

For reference, the focused rerun command was:

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e -- --headed tests/e2e/realdata.spec.ts --grep "geometry provenance"
```
