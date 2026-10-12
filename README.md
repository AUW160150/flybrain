# Flybrain

Seven experiments on one fly connectome, MaleCNS v1.0, and the site that presents them.

The question behind all of them: what is a complete, synapse-level wiring diagram of a nervous system actually good for when you treat it as an engineering artifact? Four answers were tried: as a game engine (FlyWorld, FlyWorld Studio), as a sensory front end (FlyVision), as an inductive bias for learning (connectome language model, Flycodes), and as a thing to be audited (MaleCNS atlas, sugar circuit audit). Two of the learning experiments came out as null results; they are reported as measured.

Contents

1. [The dataset](#the-dataset)
2. [Project 01 · FlyWorld](#project-01--flyworld-a-garden-arena-driven-by-the-connectome)
3. [Project 02 · FlyWorld Studio](#project-02--flyworld-studio-browser-exploration-and-real-data-workspace)
4. [Project 03 · FlyVision](#project-03--flyvision-the-garden-through-a-flys-eyes)
5. [Project 04 · Connectome language model](#project-04--connectome-language-model)
6. [Project 05 · Flycodes](#project-05--flycodes)
7. [Project 06 · MaleCNS atlas](#project-06--malecns-atlas)
8. [Project 07 · Sugar circuit audit](#project-07--sugar-circuit-audit)
9. [How the work was done](#how-the-work-was-done)
10. [Repository layout, build, data](#repository-layout)

---

## The dataset

**MaleCNS v1.0** (Berg et al., *Cell*, 2026; FlyEM at HHMI Janelia, University of Cambridge, MRC LMB, Google Research; CC BY 4.0) is the first complete wiring diagram of an entire adult male *Drosophila* central nervous system: central brain, both optic lobes and the ventral nerve cord, joined through an intact neck. It was imaged with FIB-SEM at 8 nm isotropic resolution.

Every project here reads the same three released flat files, pinned by content hash in each project's manifest:

| File | What it holds | Size |
|---|---|---|
| `body-annotations-male-cns-v1.0-minconf-0.5.feather` | one row per body: status, type, superclass, class, soma/root side, nerves, cross-references | 14.5 MB |
| `body-neurotransmitters-male-cns-v1.0.feather` | per-body neurotransmitter prediction, confidence and consensus | 43 MB |
| `connectome-weights-male-cns-v1.0-minconf-0.5.feather` | directed body-to-body synapse counts at confidence ≥ 0.5 | 1.05 GB |

Counts that recur throughout:

| Quantity | Value |
|---|---:|
| Bodies with status `Traced` (the neuron set used everywhere) | 165,122 |
| Directed connections between traced neurons, ≥ 1 synapse | 25,563,197 |
| Synapses in those connections | 124,025,046 |
| Directed connections with ≥ 5 synapses | 6,235,649 |
| Raw ordered pairs in the weight table (all bodies) | 151,856,684 |
| Distinct type labels | 11,751 |

Two conventions are shared. A **synapse count is a structural weight**, never a physiological one; where a sign is needed (the game), it is the predicted transmitter sign, and that choice is stated. **Neurotransmitter prediction, confidence and consensus stay separate fields** and are never silently collapsed into excitatory/inhibitory. The raw tables are not in this repository; `projects/*/README.md` says how each project fetches and verifies them.

---

## Project 01 · FlyWorld: a garden arena driven by the connectome

`projects/flyworld-game` · Python, panda3d, PyTorch (Apple MPS or CPU) · *play*

**What it is.** A 3D garden with six small flies and one big fly you drive with the arrow keys. Each small fly runs a spiking neural network whose wiring is a sub-circuit of the connectome. The goal (Shepherd mode) is to get all six flies to eat four fruit patches before a three-minute timer ends. Your tools are the flies' own circuits: loom at a fly and its looming detectors fire the giant fiber, so it jumps away; stimulate its DNp09 neurons and it walks.

**Method.**

- *Which neurons.* A survey of 25 other connectome-driven games and models (`NEURON_CHOICES.md`) showed a recurring vocabulary: looming detectors LC4/LPLC2/LC16/LC6 as inputs, descending neurons DNp01 (escape), DNp09 (walk), MDN (back up), DNa01/DNa02 (steer), DNg11 (groom) and the proboscis motor neuron MN9 (eat) as outputs. FlyWorld adopts that vocabulary and adds odour (ORN_DM1/DM4/DC1/DA1/VA1v), taste (LB3c) and the mushroom body (KC, MBON, PPL1 punishment, PAM reward) so feeding can be circuit-driven.
- *Extraction.* From the traced graph at ≥ 5 synapses, keep every neuron on a path of ≤ 3 hops from the looming cells (≤ 4 from odour and taste cells) to the seven target descending/motor groups, excluding optic-lobe columnar cells. Result: **10,203 neurons, 401,680 edges**. Pressing W swaps the selected fly to the **whole CNS (165,122 neurons)**.
- *Dynamics.* Batched leaky integrate-and-fire: 1 ms steps, τ = 20 ms, threshold 1, 2 ms refractory, weight = synapse count × transmitter sign, gain 0.005. Propagation is event-driven (only neurons that spiked scatter their outgoing synapses), so cost scales with activity, which stays at 1–3% of cells. Six sub-circuit brains step at about 2,500 steps/s on MPS; the whole CNS at about 600 steps/s. A governor damps membrane potentials if more than 5% of cells spike for 20 consecutive steps.
- *Encoders and decoder.* Angular expansion of an approaching object → LC4/LC6; angular size → LPLC2/LC16; food odour decaying with distance → ORNs; standing on food → LB3c. The decoder reads DNp09 (forward), MDN (backward), DNa02/DNa01 left minus right (turn), DNp01 spikes (jump), DNg11 (groom, with hysteresis) and MN9 (eat).
- *Calibration.* A sweep over gain and stimulation amplitude picks the point where rest is silent, DNp09 stimulation walks without recruiting more than 50 descending neurons, and looming reaches DNp01 within 20 ms.

**Why these decisions.** Nothing is trained: the point was to see how much behaviour the raw wiring produces by itself. LIF with signed counts was chosen over a rate model because the escape circuit is a timing circuit (giant-fiber latency is the test). The sub-circuit exists only for speed; it is a bounded view of the same graph the whole-CNS mode runs.

**What was measured.** From `processed/calibration.json`:

| Stimulus | DNp01 L / R | DNp09 | MDN | MN9 | cells active |
|---|---:|---:|---:|---:|---:|
| rest | 0 / 0 Hz | 0 | 0 | 0 | 0.00% |
| loom, both sides | 325 / 310 Hz | 0 | 0 | 0 | 0.83% |
| LC4 right only | 175 / 310 Hz | 0 | 0 | 0 | 0.30% |
| stimulate DNp09 | 0 / 0 | 97.5 Hz | 0 | 0 | 0.03% |
| stimulate MDN | 0 / 0 | 0 | 106 Hz | 0 | 0.03% |
| food odour (ORN_DM1) | 0 / 0 | 0 | 0 | 92.5 Hz | 1.85% |
| taste (LB3c) | 0 / 0 | 0 | 0 | 32.5 Hz | 0.14% |

Looming reaches DNp01 in 9 ms and is lateralised. Odour drives MN9 and suppresses walking, which is why a fly stops on a fruit patch and eats, and also why odour does not steer the flies toward food (the player has to). DNp09 stimulation produces a walk-coupled DNa02 asymmetry; calibration measures it and the decoder subtracts it. Eight verification gates with their check commands and recorded evidence are in `GATES.md`.

**In the browser.** `site/src/js/brain.js` is a line-by-line JavaScript port of `brain.py` and `decoder.py` over the same exported arrays (`scripts/export_circuit.py`), so the website's landing page and the project page run the real 10,203-neuron circuit on one browser thread at about 17–34k steps/s.

---

## Project 02 · FlyWorld Studio: browser exploration and real-data workspace

`projects/flyworld-studio` · React 19, react-three-fiber, TypeScript, Vite · *runs in the browser*

**What it is.** Two halves. *Explore* is a procedural garden with a controllable fly avatar, an educational layered brain (five teaching systems, 13 generic nodes) and a synthetic session timeline. *MaleCNS data* is a real-source workspace that loads bounded circuit packages extracted from the connectome and lets you filter by side, type and evidence, isolate partners and paths, and open a provenance inspector on any body.

**Method.** An offline preprocessor (Python standard library, no network) reads the pinned flat files and the frozen structural results of the sugar circuit audit (Project 07), verifies every input by SHA-256, and writes JSON packages bounded to 500 nodes, 5,000 edges and 4 MB. Eight packages ship: the focused circuit (110 bodies, 1,923 raw edges), the paper motif subset (102 / 274), candidates, LB3b, LB3c, motors, an empty sugar-selected package, and three native-coordinate SWC skeletons (ANATOMY_ONLY). A separate on-demand atlas indexes all 165,122 neurons and 25,563,197 connections into a 1.5 GB SQLite file served by a Vite dev-server plugin (`node:sqlite`), with neuroglancer precomputed formats parsed in TypeScript for skeletons, reference meshes and synapse shards.

**Why these decisions.** The avatar and the teaching brain are deliberately placeholders and labelled as such on screen (USER_DRIVEN_ILLUSTRATION, PLACEHOLDER_GEOMETRY). The design rule is that educational animation and real structural records never share a visual channel: a FEED gesture may illustrate source-labelled motor neurons through a mapping marked unreviewed, but the interface never implies imported connectivity produced the behaviour. Packages are bounded so the browser never holds whole-graph data; the full index stays on the server.

**What was verified.** 199 application tests, 20 preprocessing tests, 18 anatomy tests, a production build, and 11 Playwright scenarios. Five strongest downstream pairs in the atlas have matching aggregate and individual synapse counts (86, 95, 149, 177, 5 at confidence ≥ 0.5). Anatomical orientation remains marked UNVERIFIED. No neural dynamics are implemented.

---

## Project 03 · FlyVision: the garden through a fly's eyes

`projects/flyvision` · Python, pygame, numpy, pyarrow · *desktop*

**What it is.** A first-person garden ray-traced from one pose and displayed through **1,709 published eye directions** (857 left, 852 right) from a microCT-scanned reference fly. Each screen pixel takes the colour of the nearest measured ray from either eye, so the irregular patches are the eye's real angular sampling, not a hexagon filter. Walk around, chase three animated flies, press Tab to compare with an ordinary camera at the same pose.

**Method.** Geometry is imported from the authors' repository for *Eye structure shapes neuron function in Drosophila motion vision* (reiserlab/eyemap_T4, pinned to one commit). The importer checks every file against its Git blob hash, the cone/lens permutation, unit-vector norms and the published head basis, and reproduces the published neighbouring-ray angles to 3.6 × 10⁻¹⁵ rad. Every session records trajectory, raw RGB directional samples, screenshots and a provenance manifest; a verifier replays frames and requires the runtime code hash.

The first milestone also built a **structural atlas** over all traced neurons and asked whether wiring alone can place visual neurons in the eye map. Anchors are neurons with source hex-column coordinates; a candidate's column support is the sum of synapses to (photoreceptors) or from (other visual neurons) same-side anchors.

**What was compared.** Withhold 20% of known coordinate pairs per type/side stratum (4,733 neurons) and predict them from structure: **4,548 / 4,733 recovered exactly (96.1%)**, varying by type (Tm4: 41.0%). A five-seed shuffle control that preserves type, side, connectivity and counts recovers **0.11–0.21%**.

**Why these decisions, and the limit.** The atlas result is deliberately described as within-animal structural consistency, because the coordinates may themselves have been inferred from connectivity. The eye geometry is from a *female* specimen with no verified map onto the male connectome's 4,107 photoreceptor bodies, so the viewer keeps neural simulation explicitly off: registered neuron count is zero, and the research plan states what evidence would be needed (anatomical landmarks, a transform with disclosed assumptions, physiological fits on held-out stimuli) before any model is connected to the world.

---

## Project 04 · Connectome language model

`projects/connectome-lm` · PyTorch, CPU float32, deterministic, locally preregistered · *experiment*

**Question.** Does the fly's wiring carry structure that helps a tiny recurrent network predict text, compared with the same graph rewired at random?

**Model.** UTF-8 bytes → learned 256-entry embedding (width d = 32) → dense input projection onto N = 512 neurons → a recurrent core with **one trainable scalar per observed directed edge** (E = 3,061), tanh, and an engineered α = 0.5 self-memory → dense rank-d readout → 256 logits. Everything learns from scratch; the graph is only a sparsity pattern and signs are unconstrained. Context 128, batch 8, AdamW, lr selected on validation, 20,000 updates (20,480,000 prediction bytes) per run. Active parameters: 52,981.

**Graph.** All 151,856,684 raw ordered pairs audited exactly (no duplicates). 165,122 traced neurons and 6,235,649 directed pairs at ≥ 5 synapses retained; a 512-neuron neighbourhood sampled with seed 101. About 92% of those neurons' filtered connectivity falls outside the subset, which is reported as the main scope limit.

**What was compared.** Five conditions with matched interfaces, matched initial edge-slot weights, identical data windows per seed and equal byte budgets:

| Condition | What changes | Why it is there |
|---|---|---|
| A · Fly topology | the real 3,061 edges | the hypothesis |
| B · Degree-rewired (×3 per seed) | directed three-edge swaps preserving every neuron's exact labelled in/out degree (61,220 accepted swaps, ≈17% edge overlap) | the primary null: same degree sequence, no anatomy |
| C · Random density | random graph at the same density | is degree structure itself doing anything? |
| D · Parameter-matched GRU | conventional recurrence within 5% of the parameter count | what a normal architecture does with the same budget |
| E · No cross-node recurrence | diagonal memory only, same interfaces | how much the recurrence matters at all |

The predeclared primary outcome: per training seed, mean rewired test BPB minus fly test BPB; positive favours fly; practical threshold +0.02 BPB; 10,000 seed-level bootstrap resamples.

**Protocol.** Smoke (5 runs) → pilot (15 runs, 3 seeds) → development grid (30 runs, seeds 901/902, lr ∈ {0.0003, 0.001, 0.003}, selected on pooled fly+rewired validation only; 0.003 chosen) → a freeze file hashing code, analysis plan, corpus, graphs, learning rates and the full run matrix → confirmation (35 runs, seeds 11/22/33/44/55, 4.46 h CPU) → one explicit `final-evaluate` command that opened the test split for the first time. Audits after each stage replayed every saved validation score to within 10⁻⁶ BPB.

**Result.** Held-out test, validation-selected checkpoints, 55,769 scored positions each:

| Condition | Runs | Test BPB | Byte perplexity | Accuracy |
|---|---:|---:|---:|---:|
| Fly topology | 5 | 2.6388 | 6.23 | 46.92% |
| Degree-rewired | 15 | 2.6286 | 6.18 | 47.11% |
| Random density | 5 | 2.5827 | 5.99 | 47.65% |
| Parameter-matched GRU | 5 | 2.5575 | 5.89 | 49.41% |
| No cross-node recurrence | 5 | 2.6738 | 6.38 | 45.92% |

**Primary effect: −0.0103 BPB, 95% paired bootstrap interval [−0.0206, +0.0017].** Four of five seeds favoured rewiring. The interval includes zero: no fly-wiring advantage is established, and no clear disadvantage either. Validation-only dependence checks (zero the core, reset state every byte, zero 10% of coefficients) show every condition relies on its trained recurrence. Equal parameters do not mean equal compute: the GRU trained in 141 s on average, the fly core in 509 s. One subgraph, one specimen, one small corpus, five seeds; it is a null result for this experiment, not a claim about biology. Reports, audits and the figure source are in `projects/connectome-lm/reports/confirmation-211428f1ca1f/`.

---

## Project 05 · Flycodes

`projects/flycodes` · Python, PyTorch, bounded Python judge · *results platform in the browser*

**Question.** Can the **complete** connectome, used as a fixed reservoir with only a readout trained on top, learn to write code?

**Model.** All 165,122 traced neurons and all 25,563,197 recorded edges, including weak edges and 101 self-connections, with **no trainable synaptic weight**. One scalar state per neuron; a fixed input mapping and 768-dimensional signed pooling; a reservoir calibrated on validation only (recurrent spectral target 0.045, leak 0.5, input scale 0.35, chosen from three declared settings). The v2 readout sees the current pooled state, the mean and final pooled state of the prompt (an explicit encoder-style context buffer), and 16 sine/cosine clock features, through a two-layer GELU head (width 384; 1,325,544 parameters). A lossless lexical tokenizer is trained on training text only.

**Why v2 looks like this.** The v1 pilot (12 training exercises, linear readout, UTF-8 bytes) scored 0/6 on six original LeetCode-style problems, and so did its no-recurrence control and a tiny from-scratch Transformer; a diagnostic showed recurrent input was 0.04% of byte input, so the graph was numerically present but inert. v2 therefore calibrated the recurrence (echo-state practice), retained prompt context (the model was forgetting the problem while answering), added a nonlinear readout and a tokenizer, and enlarged training from 12 to **246 verified examples**: 134 curated MBPP tasks, 100 authored parameterised exercises and the 12 originals. Each change is sourced in `docs/PROTOCOL_V2.md`, recorded before training.

**What was compared.** The fly reservoir against a **no-recurrence control** with identical input mapping, leak, context buffer, head, exposures and optimiser, each with two readout seeds (7 and 19). Three disjoint evaluations: 24 fresh MBPP tasks fixed before training (from the 209 judge-compatible records), 30 unseen-constant exercises on familiar templates, and 8 seen training problems. The judge interprets a bounded Python subset in a timed subprocess and never calls `exec`, so the score is explicitly not a full MBPP score.

**Result.**

| Model | Fresh MBPP | Unseen constants | Seen training |
|---|---:|---:|---:|
| Fly · seed 7 | 0 / 24 | 0 / 30 | 1 / 8 |
| Fly · seed 19 | 0 / 24 | 0 / 30 | 0 / 8 |
| No recurrence · seed 7 | 0 / 24 | 0 / 30 | 1 / 8 |
| No recurrence · seed 19 | 0 / 24 | 0 / 30 | 0 / 8 |

The one pass reproduces a seen example (`return sum(nums) + 0`). Training loss fell from 6.6 to 0.03 while validation loss bottomed at step 100 and rose: memorisation. A stronger post-run test audit removed three false-positive transfer passes per seed-19 model (wrong constants); both scores are kept. The measured diagnosis (`docs/BACKTRACE_RESULTS.md`): removing the recurrence changes next-token accuracy from 51.91% to 51.89% while shuffling prompt context drops it to 42.79% (the readout leans on the artificial context, not the reservoir), and raising the recurrent gain toward 0.9 extends a delayed-bit memory horizon without changing any edge. A redesign plan proposes learning dynamics on the fixed topology and staged primitive-to-program evaluation. The self-contained `flycodes.html` shows every generated program, verdict, activity trace and curve.

---

## Project 06 · MaleCNS atlas

`projects/connectome-atlas` · Python, SQLite, Pillow, static HTML · *static report in the browser*

**What it is.** A read-only inspection layer over Project 04. Before trusting a null result you should be able to see the graph it was computed on, so this project verifies the saved 512-neuron graph against the published bulk product and lets you examine it from every angle without touching the experiment's files.

**Method.** Separate virtualenv, read-only reuse of installed packages, CPU only, one thread, lower process priority, and a non-interference receipt. Exact identity check of the saved graph (hash `354ccf91…534b`: 512 IDs, 3,061 directed pairs, 38,708 contacts) against the parent arrays and the published tables; the pre-threshold graph on the same IDs (7,405 pairs, 47,404 contacts); a disk index of 259,286 curated pairs incident to the saved IDs for exact in/out partner lookup including partners outside the subset; binary and contact matrices; a superclass quotient graph; per-neuron removal ledgers; eight native-space skeletons fetched with bounded calls (8/512 coverage stated); executed-source predictor diagrams (52,981 active parameters) and instantiated MLP, causal CNN and transformer references with shape tests and no performance comparison.

**Why these decisions.** The interface exposes separate blocked scopes (G0/G1/G2 whole-release ingestion, estimated at 64 GiB of SQLite) with the exact command that would populate each, instead of showing partial statistics as whole-graph facts. Learned-weight overlays are blocked because `torch.load(weights_only=True)` rejects the checkpoints' NumPy RNG pickle state and no unsafe fallback was used; the report states what a safe export needs.

---

## Project 07 · Sugar circuit audit

`projects/sugar-circuit` · Python, authenticated neuPrint, pandas, matplotlib · *circuit explorer in the browser*

**What it is.** Tastekin et al. (*Cell*, 2026) traced how sugar taste on the labellum reaches the motor neurons that extend the proboscis. This project asks one narrow question: can the paper's named neurons and motifs be found, exactly, in public MaleCNS v1.0, and where do the two disagree?

**Method.** A written research protocol (v0.1, 6 October 2026) came first, then gated checkpoints, each closed by an artifact-integrity check that re-hashes every source, input and output and scans for credentials. Gate 1 resolved **95 target bodies** against authenticated release metadata and the flat files, corroborating all 87 sensory and motor IDs and types with the paper's Table S1 (1,615 exact cross-representation field matches, 190 explained precision differences). Gates 2–3 exported the full released graph with no added threshold and cross-checked **all 746,910 raw body-edge weights** against neuPrint; computed exact A–E membership within four-hop simple-path bounds and full-graph reachability; and built the explorer and figures from the frozen run. Every claim has an ID (33 claims), every mismatch a ledger entry (1,274), every open question a number (12).

**What was found.** All 770 sensory–motor pairs are reachable in 2–3 hops. GNG021 has no direct LB3 input, but all 154 LB3-candidate pairs have shortest length 2 and both candidate bodies reach every motor. Eight pooled Figure 6 counts differ between the paper and v1.0 (for example GNG015 → MN9: 473 vs 478; GNG108 → MN4a: 98 vs 135); flat files and neuPrint agree with each other, and whole-body or whole-edge pruning alone does not explain the gaps. One LB3c body's entry nerve is missing in v1.0 versus Table S1. The neuron "Puddle" is named in the paper with no body or type mapping in any inspected authoritative record, so it is left out of every figure rather than guessed.

**Why these decisions.** The paper's effective-connectivity selection is reconstructed as far as the final STAR Methods allow; a synthetic audit shows reference, pooling and horizon choices change membership, so computational replication is marked BLOCKED rather than approximated, the three proposed experiments stay `execution_allowed: false`, and no simulation was run. Anatomy is likewise BLOCKED (0 of 110 requested skeletons in this build) with a status image named `anatomy_BLOCKED` where a render would go. The explorer never falls back from effective scores to raw counts; raw edge width is `0.7 + 4.3·√(count / visible max)` and carries no sign.

---

## How the work was done

Each project started with a written protocol and ended with a status ledger. Learning experiments were preregistered in the local sense: an analysis plan hashed before training, development selection on validation data only, a frozen configuration, and one explicit command that opened the test split. Every number above is copied from a saved artifact (a run manifest, an audit JSON, a figure sidecar); nothing is re-derived for the write-up. Boundaries are stated alongside results: structural weights are not physiological ones; the arena flies are artificial models constrained by real wiring, not emulated animals; the first-person garden uses a female reference eye not registered to the male connectome; two of the learning experiments found nothing, and say so.

---

## Repository layout

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

Open http://127.0.0.1:8787. `site/build.sh` copies `site/src`, builds the studio with `FLYWORLD_BASE=/flyworld/`, and copies the three static explorers into place. Each project's own README covers running it from source.

## Data

All projects read the MaleCNS v1.0 flat files (FlyEM, HHMI Janelia; University of Cambridge; MRC LMB; Google Research), distributed under CC BY 4.0 at https://male-cns.janelia.org/download/. The raw tables (~1.1 GB) are not in this repository; each project's README says how to fetch them. Eye geometry in FlyVision is from reiserlab/eyemap_T4. MBPP (Austin et al., 2021) is used by Flycodes under CC BY 4.0. The browser demos use bounded, pre-extracted subsets committed here.
