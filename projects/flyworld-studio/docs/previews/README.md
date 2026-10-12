# Local previews

The generated functional preview is `../../dist/index.html`, with assets beside it. Serve it with:

```sh
npm run build
npm run preview
```

Open http://127.0.0.1:4173. Do not open the entry directly as a file; Vite expects HTTP asset paths.

No screenshots were generated in the restricted creation session because localhost binding was denied. A successful `npm run test:e2e` run in a normal local session writes these files here:

- `mvp-world.png`: world, transparent head, provenance and performance overlay.
- `mvp-brain.png`: selected generic neuron, metadata, layer inspection.
- `mvp-mobile.png`: narrow layout.

Those are planned output paths, not existing or visually verified screenshots. Playwright failure traces/screenshots, when available, live in ignored `test-results/`.

## Prompt 03 generated previews

These artifacts now exist:

- realdata-static.html: standalone server-rendered markup using the actual graph/inspector components, with a paper-associated one-hop view. It is static and does not claim browser interaction validation. Regenerate with node scripts/render_preview.mjs.
- native-anatomy.png and native-anatomy.svg: offline native X/Z projection of bodies 10093, 10807 and 11369, using original SWC parent links. The PNG was inspected. Native orientation remains unverified.
- native-anatomy.manifest.json: geometry/package/script/output hashes for that plot.

The optional plot generator requires Matplotlib. This session reused the already installed workspace interpreter read-only:

    MPLCONFIGDIR=/tmp/flyworld-matplotlib ../../visualization/.venv/bin/python scripts/render_anatomy_preview.py

No browser screenshot was produced. The new smoke scenarios write realdata-package.png and realdata-anatomy.png only after a successful local browser run. Those paths are planned outputs, not existing screenshots.

## Checkpoint 03A — controls

No new browser screenshots were generated on 8 October 2026. Playwright startup failed with localhost EPERM and a direct Chrome launch exited SIGABRT. All 13 manual acceptance steps remain NOT RUN; see [the audit](../CHECKPOINT_03A_CONTROLS_AUDIT.md).

A successful local run of tests/e2e/controls.spec.ts will produce controls-forward.png, controls-left.png, controls-tree.png, controls-brain.png and controls-return.png here, plus docs/validation/prompt03a/browser-acceptance.json. These are planned outputs, not existing visual evidence. The JSON distinguishes automated browser assertions from the still-required human review. Existing data/anatomy previews remain historical artifacts with their previously documented scope.

## Later user browser run

The user subsequently ran all nine scenarios: three passed and six failed. Browser screenshots now exist from that run, including world, brain, mobile and controls-forward/left/tree evidence. The controls sequence reached step 12 and failed at an obstructed click; steps 12–13 were not accepted. The agent inspected the saved controls failure screenshot and repaired an overlapping label. Original traces/screenshots are preserved in .cache/browser-fix-user-run; [the follow-up](../validation/browser-fix/README.md) distinguishes these observed results from the pending corrected rerun.

A subsequent user rerun reported **8 passed / 1 failed**, including all 13 automated controls steps passing. After the mobile form-sizing fix, the user confirmed the final anatomy scenario also passes. All nine scenarios now have passing results across those runs. Human visual acceptance remains pending. The earlier failure screenshot and trace remain historical evidence; see [the mobile follow-up](../validation/mobile-overflow/README.md).
