# FlyVision

FlyVision is a separate research project for experiencing a simulated world through a fruit fly's sensory system, with the processing constrained by the local MaleCNS connectome. Its first milestone makes the connection between source neuron identities, sensory annotations, and candidate visual columns inspectable and reproducible.

The current implementation builds the complete local **Traced** neuron atlas and raw traced-to-traced graph. It also constructs explicitly provisional visual-column candidates and tests them against withheld source annotations. An **interactive first-person garden** uses 1,709 published eye directions. Its geometry comes from a separate female reference specimen; registration to MaleCNS and calibrated neural dynamics remain unresolved. The garden currently simulates directional sampling with illustrative RGB colors, with neural simulation explicitly off.

## Explore the garden

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyvision
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m flyvision.viewer
```

The window opens directly into a colored world viewed through the reference eye samples. Click the world to capture the mouse, then move and look around. Three animated flies share the garden. Start by approaching the marked fly, then follow a gentle four-discovery trail through the fruit grove and flowers. Direction cues help you find targets outside the current view, and discovery messages give feedback as you explore. Press G to hide the guide and explore freely. If an older viewer is still running, close it and rerun the command. [View the garden preview](runs/social-garden-preview-v1/first_frame.png).

| Control | Action |
| --- | --- |
| W / S | Move forward / backward |
| A / D | Strafe left / right (Q / E also work) |
| Mouse after clicking the world | Look around |
| Arrow keys | Look around without mouse capture |
| Space / Shift | Fly up / down |
| Tab, or 1 / 2 | Switch between fly sampling and a reference camera at the same pose |
| H / I | Open controls / scientific details and eye panoramas |
| G | Hide / show the exploration guide |
| R / P | Return to the starting pose (keep discoveries) / pause |
| Escape | Close a panel, release the mouse, then quit when neither is active |

Each session saves its trajectory, raw RGB directional samples, screenshots, authored discovery events, and parameter/provenance manifest in a new run directory. The window can be resized; the main forward view retains a 110-degree horizontal display field.

Offscreen execution, RGB replay, and synthetic keyboard/mouse event handling are verified. The event checks cover movement, turning, altitude, pause, comparison, reset, resizing, help, and focus loss. The agent sandbox cannot open a macOS display, so actual desktop capture remains unverified here.

The main fly view assigns each screen pixel the RGB value of the nearest published ray from either eye. Its irregular patches come from that angular sampling; they are not a decorative hexagon filter. Combining both eyes into a forward perspective is a human-readable display convention, not modeled binocular fusion or a reconstruction of subjective perception. The reference camera observes exactly the same garden and pose at finer spatial resolution.

The garden's fruit, flowers, lighting, RGB colors and scale are authored. RGB intensities are not calibrated spectral radiance or fly receptor responses. This ideal-direction prototype uses a common eye origin and does not simulate UV, optical acceptance blur, phototransduction, neural dynamics or fly biomechanics. Manual movement uses observer flight with a simple clearance guard around the two fruits; other objects have no body collision physics. Locations beyond the declared 6-degree display cutoff remain masked; this cutoff is not a physiological acceptance angle. The full eye panoramas and registration status are available under **I / About**, leaving the world as the main view.

The other flies are stylized scene geometry with scripted paths, visible wing animation and a deterministic proximity response that moves them away from the observer. Their appearance, motion, wing animation rate and interaction distances are authored rather than physiological. They do not run copies of the MaleCNS network or simulate courtship, pheromones or acoustic communication. The discovery guide uses scene positions exclusively as a player aid. It is excluded from raw optical samples and is never passed to a neural model. `exploration.json` explicitly labels discoveries as gameplay events, not biological validation.

The published reference map uses female microCT and FAFB. There is no verified mapping from its rays to the local MaleCNS identities in the inspected files. All 4,107 local photoreceptor-labelled bodies therefore retain unresolved physical bindings. [Optics milestone and evidence](docs/OPTICS_MILESTONE.md).

To rebuild the geometry and produce a deterministic preview in new directories:

```sh
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m flyvision.eye_reference --out runs/new-eye-reference
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m flyvision.viewer --geometry runs/new-eye-reference --headless --frames 90 --out runs/new-optics-preview
```

The additional packages are already present in the parent environment. On another machine install `python -m pip install -e '.[dev,optics]'`. The pinned reference files are stored under references/eyemap_T4, with their original license retained.

The current suite passes 24 tests. Recheck a recording and replay its first, middle and last frames with `../../.venv/bin/python scripts/verify_optics.py runs/social-garden-preview-v1 --out reports/new-social-garden-check.json`. The 90-frame acceptance recording reproduces all three sampled frames exactly, including the animated actors and proximity response. Verification checks artifact and runtime-code hashes and requires the code version used by that recording. Earlier recordings remain unchanged and require their original runtime code.

## Run locally

The parent project's Python environment already provides the required packages:

```sh
cd /Users/Rodela1/Code/Flybrain/sandbox/flyvision
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m pytest -q
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m flyvision build --out runs/my-baseline
PYTHONDONTWRITEBYTECODE=1 ../../.venv/bin/python -m flyvision verify runs/my-baseline
```

The build is offline and streams the connection file. It refuses to overwrite an existing run and verifies all three raw source hashes before and after processing. A moved dataset can be supplied with `--source-dir /path/to/flat-connectome`; contents must still match the pinned hashes. On another machine, create a Python 3.10+ environment and run `python -m pip install -e '.[dev]'` from this folder, then supply the source directory explicitly.

The executed initial run is [runs/baseline/REPORT.md](runs/baseline/REPORT.md). A full build can take several minutes. No real-time neural simulation performance has been measured.

The [baseline plot](reports/baseline.png) shows source coordinates, coverage and the variation in holdout performance between cell types. Reproduce it with `MPLCONFIGDIR=/tmp/flyvision-matplotlib ../../.venv/bin/python scripts/plot_baseline.py runs/baseline reports/baseline.png`.

The first run recovered **4,548 of 4,733 withheld source coordinate pairs (96.1%)**. Recovery varies by type: Tm4 was **41.0%**, so the overall score must not be applied to every cell population. A [five-seed coordinate-shuffle control](reports/shuffle_control.json), preserving type, side, connectivity and counts, recovered **0.11–0.21%**. These results measure structural consistency in this dataset; physiological validation remains pending. Run the control with `../../.venv/bin/python scripts/shuffle_control.py runs/baseline reports/new-shuffle-control.json`.

## Outputs

| File | Meaning |
| --- | --- |
| `atlas.parquet` | All Traced bodies, original annotations, separate NT fields, derived sensory labels and index |
| `edges.parquet` | All raw traced-to-traced rows, unsigned synapse count and source-row index |
| `source_columns.csv` | Distinct source hex-coordinate pairs grouped by provisional side hints |
| `visual_candidates.parquet` | Supported columns, structural coverage, ambiguity and unresolved status per visual neuron |
| `column_support.npz` | Sparse integer matrix: atlas node index by source column index; entries are summed raw counts |
| `holdout_predictions.csv` | Predictions for source coordinates withheld from anchors |
| `holdout_validation.json` | Exact coordinate agreement by type and side, with coverage and tie counts |
| `manifest.json` | Dataset, source/code/artifact hashes, environment and completion status |

Array indices are local indices into atlas.parquet, not body IDs. Raw graph rows are kept even when they have one synapse. Connections to excluded bodies are counted separately, including their contribution to mapping coverage denominators. Large derivatives remain in runs/ and can be regenerated.

The source release is `male-cns:v1.0`; file content hashes pin the local flat tables. The approximately 167K published total and this cache's exact Traced count are different scopes. The build reports all excluded statuses rather than inventing extra neurons or silently combining datasets.

## What improves the simulation

The intended sequence is **physical scene → receptor inputs → source-constrained neural dynamics → sensory readout → movement → new scene**. Each interface needs its own evidence and held-out validation. All traced neurons remain addressable, while the first validated runtime can use a bounded visual circuit with an explicit boundary model.

See [the research plan](docs/RESEARCH_PLAN.md) for the scientific gates, experimental controls, and primary references. [The data contract](docs/DATA_CONTRACT.md) explains precisely what current candidates can support.

Source data attribution: FlyEM, HHMI Janelia, University of Cambridge, MRC LMB, and Google Research. MaleCNS data are distributed under [CC BY 4.0](https://male-cns.janelia.org/download/).
