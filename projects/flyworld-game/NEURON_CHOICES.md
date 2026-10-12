# Which neurons other projects use (inputs, outputs, subgraphs)

Surveyed 2026-09-24 from repo READMEs and source files. Counts in the last section are from
our local MaleCNS v1.0 annotation table (Traced neurons only).

## A. Research / trainable models

| Project | Dataset | Subgraph | Input neurons | Readout neurons | Model & what's trained |
|---|---|---|---|---|---|
| Shiu et al. 2024 (Nature) | FlyWire v630, ~127k neurons | whole brain | ~20 labellar sugar GRNs (Poisson 10-200 Hz), ~18 water GRNs, bitter Gr66a GRNs, 147 JO neurons (JO-C/E/F/mz) | MN9 proboscis motor neuron (also MN6/8/11, feeding interneurons Zorro, Rattle, Phantom, Bract, Roundup, Usnea, Fudog, Clavicle; grooming aBN1/2, aDN1/2) | Brian2 LIF; nothing trained. One parameter w_syn=0.275 mV per synapse tuned so 100 Hz sugar drive gives ~80% max MN9 rate. tau_m 20 ms, V_rest/reset -52, V_th -45 mV, refractory 2.2 ms, tau_syn 5 ms, delay 1.8 ms |
| flyvis / Lappalainen 2024 (Nature) | FIB-25 + FIB-19 optic lobe | 64 visual cell types, 45,669 neurons, 721-column hex lattice | R1-R6, R7, R8 photoreceptors receive per-column video luminance | decoder over medulla/lobula neurons; T4/T5 tuning used for validation | threshold-linear rate model, BPTT. Trains ~734 params: per-type-pair synaptic scale, per-type time constants and resting potentials. Signs and synapse counts fixed |
| fly-llm | FlyWire | 12,288 hub neurons by total degree, 620k synapses | ALL neurons get the character embedding as input current | ALL neurons' spikes -> MLP -> vocab | surrogate-gradient LIF SNN; trains recurrent weights under fixed binary mask (no sign constraint), embedding, readout |
| AxonWeave | MaleCNS v1.0 | whole CNS or selection by id / mask / `by_type("kenyon_cell")` / `by_region` | user projection, dense to all neurons by default | user readout over all or a selection | PyTorch layer; trainable edge weights with topology kept, optional gain/bias, readout |
| mps-malecns-model | MaleCNS v1.0 | whole CNS | DNp01=up, DNp10=down, DNa02=left, DNge104=right (admittedly artificial) | stimulated neurons + up to 128 postsynaptic targets -> A2C policy | frozen LIF (tau 20, thr 1); trains A2C heads only |
| train-your-fly | FlyWire v783 | whole brain, PyTorch Geometric | R1-6, R7, R8 photoreceptor terminals (~8k per eye), image mapped per ommatidium | Kenyon cells KCapbp-m / ap1 / ap2 (configurable) | 3-pass message passing; trains one gain per synapse (tanh-bounded), optional thresholds, linear readout |
| annel0/flybrain | MaleCNS v1.0 (+FlyWire for replication) | whole CNS; 57% flagged graded (optic lobe) | replicates Shiu: 20 sugar GRNs, 18 water GRNs, 146 JONs; ORN_DA1 for olfaction; 6,098 histaminergic photoreceptors | MN9 (68.0 Hz published vs 67.8 Hz sim), feeding interneurons, aBN/aDN, DA1 lPN, APL, lamina/T4/T5, GF -> TTMn latency | Triton LIF; nothing trained. w_syn refit to 0.075 mV for MaleCNS density |
| gnat (desktop fly) | FlyWire v783 | 668 neurons, 18,968 synapses | LC4/LPLC2 looming (314), wind sensory (16) | DNp09 walk, DNg11 groom, MDN backward, DNa01/DNa02 L-R steer, DNp02/04/11 wings, GF escape | Rust LIF; nothing trained |
| snedea/flybrain (browser) | FlyWire v783 | whole brain, grouped by class | sweet/bitter/water GRNs, R1-6, R7/8, ORNs, JO, bristle, thermo | DN walk/flight/turn/backup/startle groups; leg, wing, proboscis MN groups | browser LIF; nothing trained |
| boltzmann-fly | MaleCNS v1.0 right hemisphere | mushroom body: 343 PNs, 1,918 KCs, 49 MBONs | PN units = visible layer (72 features) | MBON units | Deep Boltzmann machine masked to PN->KC->MBON; trains coupling magnitudes |
| faiku | MaleCNS v1.0 whole | whole CNS LIF | Kenyon cells (4 odor + 4 vision channels) | MBONs approach/avoid -> pen strokes | frozen LIF + dopamine-gated KC->MBON plasticity (PAM reward, PPL1 punishment) |
| mindmeld-with-fly | MaleCNS | 499 cb_intrinsic hub neurons (top 512 by contacts, largest SCC) | 5 EEG bands -> random projection | mean activity | tanh reservoir, spectral radius 0.9; nothing trained |

## B. Games and hobby controllers (all MaleCNS v1.0)

| Project | Subgraph | Input neurons | Readout neurons | What's trained |
|---|---|---|---|---|
| fly-craftax | all non-VNC neurons (~146k), edges >=5 | R1-R6, R8p, R8y mapped to hex columns via L1/L2/L3 partners; NPFL1-I hunger, hygrosensory thirst, ER5 fatigue; tonic bias on L1-L5 | forward DNp09, backward MDN, turn DNa01+DNa02 L-R, "do" MN9, sleep FB6/FB7 tangentials; PPO variant: linear readout over all 1,314 DN rates | PPO on linear DN readout (brain frozen). Controls show readout ignores vision |
| flyt3 (tic-tac-toe) | whole CNS 166,700 | 6 R1-R6 cells per board cell (own), 5 R8 cells (opponent); loss -> aversive current into PPL101 pair | top 512 descending + top 512 vnc_motor by out-synapses -> linear head | REINFORCE on readout; variant: dopamine-gated KC->MBON depression. 62% / 74% win vs random |
| flyjump (Chrome Dino) | 80 cells: 32 visual + 32 bridge + 16 DN, 1,296 edges | 8 features -> LC4 proximity, LC11 width, LC9 height, LC15, LC16 speed, LC17, LC21, LPLC2 ground contact (4 cells each) | 16 DNs: DNp01, DNp02, DNp03, DNp04, DNp06, DNp09 x2, DNp11, DNp27 x2, DNp35 x2, DNpe052, DNg40, pIP1 x2 | only a 243-param MLP readout (cross-entropy method). 99/100 held-out; silenced circuit 0/100 |
| doomfly | whole CNS, no threshold | 3,335 R1-R6 (brightness) + 811 R8 (colour) from ViZDoom frames; tonic on L1/L2/L3/L5; damage -> PPL101 DANs; optional LB3c sugar reward | DNp20 R-L -> turn; DNpe017 rate -> move/attack; alt: DNa02/DNp09/MDN/MN9 | v6: dopamine plasticity on 4,184 KC->MBON11 edges. README says it failed its gates |
| flydoom | bounded subgraph 1k-10k: sensory -> descending shortest paths, 6 hops; or seed LC4 -> descending 4 hops | designated sensory nodes get CNN/looming features | designated descending nodes -> policy/value | PPO on internal weights (only project that trains internal connectome weights) + three-factor mode |
| fly-swing (MuJoCo) | escape circuit: 126 LC4 + 185 LPLC2 -> DNp01 (GF), GF->TTMn added | LC4 from angular velocity, LPLC2 from angular size | GF spike -> web shot | nothing |
| fly-blackjack | 80-cell circuit (same as flyjump) + mushroom body: 682 ALPN, 1,200 KC (of 3,811), 97 MBON, 316 PAM + 16 PPL1 | options encoded as odours on ALPNs; win -> PAM, loss -> PPL1 | MBON votes by valence | dopamine-gated KC->MBON depression, k-WTA for APL. -16% vs -45% untrained |
| FlyPong | 44,989 neurons by type regex: R1-8 (1,783), L1-5/Mi/Tm (28,699), T4/T5 (13,585), LC4/LPLC2 (311), LC10a (275), PAM/PPL1 (332), GF + DNa10 (4) | ball Y -> Gaussian current on photoreceptors; reward -> PAM, punish -> PPL1 | GF + DNa10 right vs left -> paddle | three-factor plasticity on visual->descending edges. Notes DNa02 got 0 object synapses |
| Swat | 6,000 neurons: all <=3-hop paths LC16 -> MDN (1,088 core) + 4,912 neighbours | 182 LC16 (looming current by side) | 4 MDN bodies (10763, 11288, 11332, 12348): retreat and heading | nothing |
| neuroterrarium | 51 bodies: both DNp01 (10001 R, 10010 L) + every direct input with >=100 contacts | pulse into a chosen type (demo DNp70) | GF spike count | scalar gain. Negative result: biological == shuffled controls |
| Fly64 (Mario 64) | whole CNS | 6,006 R1-6/R7/R8 sample a cubemap; columns from official optic-column xlsx | DNg100 forward; DNa02 + DNg13 R-L steer; DNp01/DNp10 burst -> jump | nothing |
| closed-loop-fly | optic-lobe rate net (65,799) + whole-CNS LIF on WebGPU | 1,771 ommatidia -> photoreceptors; bridge HS (6), LC4 (126), LPLC2 (185) injected into CNS; tonic on 29 DNg02 | DNg02 L/R -> wing amplitudes; DNa02 L/R steering; DNp01 loom monitor | nothing (hand-set gains) |

## C. The recurring vocabulary

Inputs people actually stimulate:
- Vision: photoreceptors R1-R6 (luminance), R7/R8 (colour), retinotopy via L1/L2/L3 hex columns; looming detectors LC4, LPLC2, LC16; feature detectors LC9/LC11/LC15/LC17/LC21, LC10a; HS cells for optic flow.
- Taste: labellar sugar / water / bitter GRNs (Shiu, snedea, doomfly's LB3c).
- Smell: ORN_DA1 glomerulus, ALPNs as odour vectors (mushroom-body projects).
- Mechanosensory: JO-C/E/F/mz Johnston's organ neurons (grooming, wind).
- Internal state: NPFL1-I (hunger), ER5 (fatigue), hygrosensory (thirst).
- Reward / punishment: PAM dopaminergic neurons (reward), PPL1 / PPL101 pair (punishment).

Outputs people read from:
- Descending neurons: DNp01 (giant fiber, escape/jump), DNp09 (forward walking), MDN (backward walking), DNa01/DNa02 (turning, L minus R), DNg11 (grooming), DNg02 (wing amplitude), DNp10, DNg13, DNg100, DNa10, DNp20, DNpe017, DNp02/04/11 (wing).
- Motor neurons: MN9 (proboscis), TTMn / DLMn (jump, flight), leg/wing MN superclass `vnc_motor`.
- Learning circuit: MBONs (approach vs avoid valence), Kenyon cells as the plastic layer.
- Lazy option: top-N descending + motor neurons by out-synapse count, or all 1,314 DNs.

Subgraph recipes: whole CNS (frozen); type-regex slabs (FlyPong); seed -> n-hop -> descending (flydoom, Swat); top-K by contact count per type + bridge cells (flyjump); direct inputs above a contact threshold (neuroterrarium); mushroom body PN->KC->MBON with DANs.

What gets trained, by frequency: nothing (most) > readout only (flyjump, flyt3, fly-craftax, mps) > dopamine-gated KC->MBON plasticity (blackjack, faiku, doomfly v6, flyt3-MB) > internal weights with mask (flydoom, fly-llm, train-your-fly, flyvis, AxonWeave).

## D. Do these populations exist in our local MaleCNS v1.0 file? (Traced neurons)

| Population | Count | Notes |
|---|---|---|
| DNp01 giant fiber | 2 | bodies 10001 (R), 10010 (L) |
| descending_neuron superclass | 1,314 | |
| DNa02 / DNp10 / DNge104 / DNp09 / MDN | 12 | |
| ORNs (class olfactory, type ORN_*) | 2,635 | |
| ALPN / ALLN | 686 / 420 | |
| Kenyon cells | 4,064 | |
| MBONs | 97 | MBON01-MBON35 |
| DANs: PAM / PPL1 | 316 / 16 | PAM01-15, PPL101-108, PPL201-204 |
| Gustatory (class) | 1,428 | NOT labelled sugar/bitter. Types are LgLG*, LB*, WG* (labellar, leg, wing bristle GRNs); `receptorType` gives putative_ppk23 / ppk25 / IR52b only. Sugar identity has to come from cross-matching FlyWire types (flywireType column) or the literature. |
| MN9 | 2 | bodies 10331 (L), 16949 (R), superclass cb_motor |
| Central complex (class CX) / EPG | 2,950 / 46 | |
| JO neurons | 672 | |
| Photoreceptors R1-R8 | 4,107 | |
| Lamina L1-L5 | 8,883 | |
| T4 / T5 | 13,585 | |
| LC types / LPLC | 4,253 / 417 | |
| vnc_motor | 708 | leg MNs ~493, wing/haltere ~60 |
| Proprioceptive sensory | 1,454 | |
| Ascending neurons | 1,846 | |
