# Flybrain

Seven experiments on one fly connectome (MaleCNS v1.0), and the portfolio site that presents them.

**Site:** the landing page at `/`, one page per project under `/projects/…`, and four things you can run in the browser:

| Path | What |
|---|---|
| `/` | Landing page with the FlyWorld sub-circuit (10,203 neurons) simulated live in JavaScript |
| `/projects/flyworld-game/` | The Python arena game, with the full brain panel ported to the browser |
| `/flyworld/` | FlyWorld Studio, the React/three.js exploration and MaleCNS data workspace |
| `/flycodes/` | Flycodes results platform (self-contained) |
| `/atlas/` | MaleCNS atlas static report |
| `/sugar/interactive/…` | Sugar circuit explorer |

## Layout

```
site/            the website: src/ (hand-written HTML, CSS, JS), build.sh, public/ (build output)
projects/        curated source of each project (large data, runs and caches are excluded)
  flyworld-game/      Python + panda3d arena; extracted circuit and calibration included
  flyworld-studio/    React + three.js studio (Vite); built into /flyworld/ at deploy time
  flyvision/          first-person fly-eye garden and structural atlas (Python)
  connectome-lm/      connectome-constrained language model experiment, with confirmation reports
  flycodes/           fixed-reservoir code-writing experiment, with the results platform
  connectome-atlas/   read-only graph inspection project, with the static report
  sugar-circuit/      Tastekin et al. gustatory pathway audit, with ledgers and explorer
scripts/export_circuit.py   regenerates site/src/assets/circuit/* from the game's processed arrays
render.yaml      Render Blueprint (static site)
```

## Build and run locally

```sh
bash site/build.sh                     # needs Node >= 22.18 (node:sqlite) and npm; python not required
cd site/public && python3 -m http.server 8787
```

Open http://127.0.0.1:8787. `site/build.sh` copies `site/src`, builds the studio with `FLYWORLD_BASE=/flyworld/`, and copies the three static explorers into place.

## Deploy

Render: **New → Blueprint** on this repository, or **New → Static Site** with build command `bash site/build.sh`, publish directory `site/public`, and `NODE_VERSION=22.20.0`. Nothing else is needed; there is no server and no environment secret.

## Data

All projects read the MaleCNS v1.0 flat files (FlyEM, HHMI Janelia; University of Cambridge; MRC LMB; Google Research), distributed under CC BY 4.0 at https://male-cns.janelia.org/download/. The raw tables (~1.1 GB) are not in this repository; each project's README says how to fetch them. The browser demos use bounded, pre-extracted subsets committed here.
