# MaleCNS v1.0 Dataset Analysis

Written 2026-09-24. Machine: Apple M5, 32 GB RAM, 661 GB free.

## 1. What the dataset is

The Male CNS connectome (Berg et al., *Cell*, published 2026-09-03; preprint bioRxiv 2025-10-30)
is the first complete wiring diagram of an entire adult male *Drosophila* central nervous system:
central brain + both optic lobes + ventral nerve cord (VNC), joined through an intact neck.
Produced by FlyEM (HHMI Janelia), Cambridge, MRC LMB, and Google Research. License: CC-BY 4.0.

| Fact | Value |
|---|---|
| Imaging | enhanced FIB-SEM, 8 nm isotropic voxels, 160 teravoxels, 7 microscopes for 13 months |
| Neurons | 166,700 (165,122 with status `Traced` in the v1.0 flat files) |
| Cell types | 11,710 identifiable across animals (11,751 distinct `type` labels in the file) |
| Presynapses / postsynapses detected | 46 M / 312 M |
| Synapse-level connections (weight table) | 151.9 M rows, 311.8 M synapses |
| Connections between traced neurons, ≥1 synapse | 25.6 M edges, 124 M synapses |
| Connections between traced neurons, ≥5 synapses | 6.2 M edges, 90 M synapses |
| Sex-specific / dimorphic cell types | 262 sex-specific, 114 dimorphic |
| Neurotransmitter predictions (per neuron) | ACh 104k, Glu 29k, GABA 22k, His 8k, DA 396, OA 101, 5-HT 48, unclear 23k |

Comparison to other fly connectomes:

- **FlyWire / FAFB v783** (female brain only): 139k neurons, 2.7 M connections at ≥5 synapses. Most hobby "fly brain" projects to date use this.
- **Hemibrain**: ~25k neurons, half a female central brain.
- **MANC**: male VNC only (~23k neurons). MaleCNS supersedes it and the annotation table carries `mancBodyid` / `mancType` cross-references.
- **BANC**: female brain + nerve cord, still being proofread.
- MaleCNS is the largest, and the only one where you can trace eye → brain → neck → leg motor neuron in one animal.

## 2. Anatomy of the data products (what's on the download page)

The bucket `gs://flyem-male-cns/` is public. No Google account or `gsutil` needed: every object is fetchable over plain HTTPS at
`https://storage.googleapis.com/flyem-male-cns/<path>`. Sizes below were measured directly from the bucket.

### Tier A. Flat connectome tables (Apache Arrow Feather) — the "graph"

| File | Size | Contents | Verdict |
|---|---|---|---|
| `body-annotations-...feather` | 14 MB | 211,577 bodies × 36 columns: type, superclass, class, side, status, dimorphism, fru/dsx, soma location, FlyWire/MANC/hemibrain type matches | **Downloaded.** Essential. |
| `body-neurotransmitters-...feather` | 43 MB | 1.8 M bodies: predicted NT + confidence, consensus by cell type, 85k with ground truth | **Downloaded.** Essential (gives edge sign). |
| `connectome-weights-...feather` | 1.05 GB | 151.9 M rows `(body_pre, body_post, weight)` = number of synapses between each pair | **Downloaded.** Essential. This IS the neural network. |
| `connectome-weights-...-traced-only.feather` | 0.51 GB | same, restricted to traced neurons | Optional; I derived it locally instead. |
| `connectome-weights-...-significant-only.feather` | 0.50 GB | same, filtered to statistically significant pairs | Optional. |
| `body-stats-...feather` | 0.78 GB | per-segment synapse counts | Skip unless you need coverage stats. |
| `syn-partners-...feather` | 6.8 GB (3.0 GB traced-only) | every individual synapse pair with xyz for pre and post and neuropil | Only needed for spatial/compartment-level modeling. |
| `syn-points-...feather` | 13 GB | every pre/post synapse point with ROI membership | Skip for network use. |
| `tbar-neurotransmitters-...feather` | 2.7 GB | per-presynapse NT probabilities | Skip; the per-neuron file already aggregates it. |

Tier A total: 31 GB, of which **1.1 GB is enough to build the complete signed network.**

### Tier B. Morphology (for visualization and 3D projects)

| Product | Size (measured, partial) | Notes |
|---|---|---|
| SWC skeletons, MaleCNS coords | ≥2.6 GB for the first 60k files; full set is roughly 7 GB | One file per neuron; download only the neurons you want by body ID. |
| Precomputed skeletons | ≥1.6 GB for the first 60k files | Neuroglancer format. |
| Skeletons in JRC2018 unisex template | ≥1.6 GB for the first 60k files | Use these if you want to overlay with FlyWire/hemibrain neurons. |
| Neuropil ROI meshes | small (KB to MB each) | Under `v1.0/database/dvid-exports/.../roisSmoothedDecimated/`. |
| Soma points, NBLAST scores, meshes mapped to FlyWire space | various | Under `v1.0/`. |

### Tier C. Image volumes and segmentation (do NOT download)

| Product | Size |
|---|---|
| Aligned EM volume, uncompressed N5 | ~160 TB |
| EM volume, CLAHE JPEG precomputed | tens of TB |
| Proofread neuron segmentation, 8 nm | tens of TB |
| Nuclear segmentation, 16 nm | 32.7 GB (measured) |

These are meant to be streamed by `cloud-volume` / `tensorstore` a chunk at a time, or browsed in Neuroglancer. They are irrelevant for network modeling.

### Tier D. Database

- Neo4j 4.4 dump of the neuPrint `male-cns:v1.0` dataset plus the CSVs used to build it. Useful only if you want to self-host neuPrint. The public neuPrint server (free account, API token) already serves the same thing via `neuprint-python`.

## 3. Space decision

| Option | Disk | Recommendation |
|---|---|---|
| Core network (done) | 1.1 GB raw + 90 MB processed | **Do this.** Enough for every "connectome as a neural network" project on the awesome-fly list. |
| + synaptic partners traced-only | +3 GB | Only if you want per-neuropil or spatial models. |
| + all skeletons | +7 to 10 GB | Only for 3D rendering of many neurons. Fetch individual SWCs on demand otherwise. |
| + all Tier A | 31 GB | Not needed. |
| EM volume | 160 TB | Impossible and pointless locally. |

You have 661 GB free, so space is not a constraint for anything except the EM imagery. The constraint is usefulness.

## 4. Data schema notes learned from the files

- `bodyId` is the neuron ID everywhere. The annotation table has 211,577 bodies but only 165,122 are `status == Traced`; the rest are glia (11,864), orphan fragments (15,925), "unimportant" (10,751), etc. **Always filter to Traced.**
- `superclass` is the most useful coarse label: `ol_intrinsic` 89k, `cb_intrinsic` 32k, `vnc_intrinsic` 13k, `visual_projection` 9k, sensory classes ~17k, `ascending_neuron` 1.8k, `descending_neuron` 1.3k, `vnc_motor` 708, `cb_motor` 107.
- `class` gives finer functional groups where known: `Kenyon_Cell` 4,064, `CX` (central complex) 2,950, `olfactory` 2,639, `DAN` (dopaminergic) 340, `MBON` 97, gustatory 1,428, mechanosensory ~5.7k.
- `somaSide` L/R is nearly balanced (75k each), so the graph has an almost mirror-symmetric structure.
- Edge weight = synapse count. Median 1, 90th pct 3, 99th pct 15, max in the thousands. Most published analyses threshold at ≥5 (or ≥2 for VNC).
- Degree: median ~100 in and ~114 out per traced neuron; max ~11k (large local interneurons and neuromodulatory cells).
- Only 101 autapses. The graph is a directed multigraph collapsed to weighted edges.
- Sign convention used by every existing simulator: acetylcholine = excitatory (+), GABA and glutamate = inhibitory (−), histamine (photoreceptors) = inhibitory, monoamines neutral or modeled separately. Applied to the traced set this gives 107k excitatory, 57k inhibitory, 541 neutral neurons.

## 5. Feasibility on this laptop (measured)

Script `scripts/build_network.py` builds the signed sparse graph from the three feather files in 12 s and saves `processed/malecns_v1.0_traced_minw1.npz` (90 MB).

Script `scripts/lif_bench.py` runs a leaky integrate-and-fire model of all 165,122 neurons and 25.6 M edges on the M5 GPU via PyTorch MPS:

| Metric | Value |
|---|---|
| Steps per second (1 ms steps) | 89 |
| Speed vs biological time | 0.09× |
| GPU memory for the graph | ~300 MB |

For comparison, the `mps-malecns-model` project reports 44 steps/s on Apple Silicon; a CUDA RTX 3060 reaches 2.4× realtime. So whole-CNS simulation is practical here, just not real time. Restricting to a sub-circuit (a few thousand neurons) will be far faster than real time.

Caveat from the benchmark: with uncalibrated gain the network saturates (thousands of neurons fire every step). Every serious project tunes gain/threshold/background so that baseline firing is sparse, following Shiu et al. 2024 (FlyWire LIF model). The `annel0/flybrain` project documents that ~57% of neurons (optic lobe T4/T5 etc.) are graded-potential, not spiking, so an LIF model of the optic lobe is a crude approximation.

## 6. How other people use a connectome "as their own neural network"

Three distinct paradigms, in increasing order of "training":

1. **Fixed biological simulation (no training).** LIF or rate model, weights = synapse counts × sign. You inject current into sensory or descending neurons and read out motor neurons. Examples: Shiu et al. FlyWire model, `mps-malecns-model`, `snedea/flybrain` browser sim, `Connectome-OS`. Fun uses: desktop pet flies, Doom/Mario/Pong controllers wired sensory → motor, "what happens if I silence this neuron".

2. **Reservoir computing / frozen brain + trained readout.** The connectome dynamics are frozen; you train only an input projection and a linear or PPO readout on top of the spiking state. Examples: `fly-craftax` (PPO readout), `FLYT3` tic-tac-toe, `mindmeld-with-fly`, the email-sorter in the MindStudio article (~80% of a small MLP's accuracy, pattern-matching to templates). This is the cheapest way to "have it do a task" and works on CPU or MPS.

3. **Connectome-constrained trainable network.** Keep the biological sparsity mask (and optionally signs), but learn the edge weights by backprop. Examples: `flyvis` (Lappalainen et al., Nature 2024, visual system, task-trained on optic flow, predicts real neural tuning), `AxonWeave` (MaleCNS as a PyTorch `nn.Module` with trainable edges), `fly-llm` (12k FlyWire hub neurons, surrogate-gradient SNN doing char-level language modeling on a 6 GB GPU), `train-your-fly` (PyTorch Geometric message passing on FlyWire). This is the scientifically interesting paradigm and the only one where the network genuinely learns.

Whole-body embodiment: `TuragaLab/flybody` (MuJoCo fly, Nature 2025) and `NeLy-EPFL/flygym` (NeuroMechFly) give a physics body to plug the brain into.

## 7. Recommended plan for a fun deployment

Given the M5/32 GB, no CUDA:

- **Start with paradigm 2** on a sub-circuit: e.g. olfactory pathway (ORNs → ALPN → Kenyon cells → MBONs, ~8k neurons) or the visual → descending → motor pathway. It is fast, and the mushroom body is literally the fly's learning circuit (DAN-gated plasticity), which makes for a good story.
- **Build a web demo** (Three.js or WebGPU) that renders a few hundred skeletons and animates spikes. Skeletons for a chosen circuit are a few MB fetched on demand from the bucket.
- **Move to paradigm 3** if you want it to "train": AxonWeave or a small custom PyTorch sparse layer with the mask from `processed/*.npz`, MPS works.

Suggested next downloads only when needed: `syn-partners-...-traced-only.feather` (3 GB) if you want per-neuropil sub-circuits with spatial info; individual SWC skeletons by body ID for visualization.

## 8. Tools already set up

- `.venv` (Python 3.12) with pyarrow, pandas, numpy, scipy, torch 2.14 (MPS works), navis, neuprint-python.
- neuPrint web: https://neuprint.janelia.org/?dataset=male-cns:v1.0 (free login; generate an API token there for `neuprint-python`).
- Cell Type Explorer: https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/
- Curated project list: https://github.com/ArtyMend07/awesome-fly

## Sources

- https://male-cns.janelia.org/ and https://male-cns.janelia.org/download/
- https://www.janelia.org/project-team/flyem/male-cns-connectome
- https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6
- https://mrclmb.ac.uk/news-events/articles/first-complete-connectome-of-male-fly-central-nervous-system-allows-for-unprecedented-male-female-brain-comparison/
- https://github.com/ArtyMend07/awesome-fly
- https://github.com/seohyunjun/mps-malecns-model
- https://github.com/annel0/flybrain
- https://github.com/dhakalnirajan/axonweave
- https://github.com/uzzambutt/fly-llm
- https://github.com/TuragaLab/flyvis
- https://www.mindstudio.ai/blog/fruit-fly-brain-connectome-ai-training
