# Circuit atlas validation — 8 October 2026

Target: full searchable source catalogue, bounded shared native anatomy, recorded connections and contacts, and upstream/downstream expansion. See [implementation](../../CHECKPOINT_04C_CIRCUIT_ATLAS.md) and [recovery](../../CHECKPOINT_04B_ASSET_RECOVERY.md).

| Check | Result |
| --- | --- |
| `npm test` | **199 passed**, including 22 new catalogue/source/coordinate/request-guard checks; [log](unit-tests.txt) |
| `npm run test:anatomy` | **18 passed** during this delivery |
| `npm run test:preprocess` | **20 passed** during this delivery |
| `npm run build` | **PASS**: strict TypeScript and production bundle; existing chunk-size warnings remain; [log](build.txt) |
| Five-body recovery | **5/5 SWCs**, four reference surfaces, five independently decoded contact totals matching source aggregates; [snapshot](recovery-report.json) |
| Integrity | **1,180 protected files unchanged**, including 968 research files and 28 public assets; 22 pinned research files and both flat source hashes rechecked; [report](integrity.json) |
| Atlas browser scenario | **BLOCKED before execution**: Vite localhost bind EPERM; [attempt](browser-attempt.txt) |
| Human visual review / target-device performance | **PENDING** |

The official-source integration tests use the built index and recovered cache. When the index is absent, those integration tests are explicitly skipped; format/request guards still run. A fresh setup must build the index and populate recovery before claiming the full real-source test result. The saved index checksum and [asset receipts](asset-receipts.json) identify the exact checked bytes. [Coverage](body-coverage.csv) includes all 110 requested bodies and distinguishes recovered from not requested; it does not infer source absence.

The suite now has **11 browser scenarios**: the prior nine, a takeoff/courtship follow-up, and `circuit-atlas.spec.ts`. Earlier user-run nine-scenario acceptance predates these additions. This attempt provides no browser or screenshot acceptance for the new code.

Run the focused atlas scenario on the user's Mac:

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyworld
FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e -- tests/e2e/circuit-atlas.spec.ts --headed
```

Then run all scenarios:

```sh
FLYWORLD_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" npm run test:e2e -- --headed
```

Playwright manages its own test server. Stop a stale test server if its configured port is occupied. Restart any manually running development server before exploring this update so the new API plugin is active. The atlas scenario checks exact catalogue counts, five-body loading, a recorded downstream expansion, 86 contacts at confidence 0.5 and 13 at 0.95, upstream partners, Quasimodo source alias, 390-pixel layout, and return to the fly. It captures screenshots only when it actually runs.

Manual review should inspect native cable/region placement, source pre/post sites at close zoom, camera fit, mobile controls and uncached loading latency. Source provenance and matching counts do not establish anatomical axis directions, fine-branch completeness, current mutation equivalence, functional membership, or neural physiology.
