# Scientific plan for an embodied fly sensory simulation

The target is a first-person simulation whose sensory transformations can be traced to the local MaleCNS neurons, documented physiology, and explicit model assumptions. The test of improvement is prediction of independent sensory and behavioral measurements. Visual plausibility and neuron count alone are insufficient criteria.

## 1 Establish the full dataset and sensory atlas

Implemented in the baseline: index every local Traced neuron; retain source identities, class/type, NT evidence, side fields and column labels; extract all raw traced-to-traced connection rows; account for excluded partners; propose one-hop visual column support; evaluate recovery of withheld source columns.

The baseline retains 165,122 neurons and 25,563,197 connection rows, representing 124,025,046 raw synapses. It recovers 4,548 of 4,733 withheld column pairs (96.1%), while Tm4 reaches only 41.0%. Five coordinate shuffles within type/side strata recover 0.11–0.21%. This initial result supports further investigation of the mapping method; it does not transfer a validation claim to physiological receptive fields or cell types lacking ground truth.

Acceptance: no duplicate/missing included IDs, no invented endpoints, no lost one-synapse rows, explicit source checksums, reproducible indexing, preserved source uncertainty, and separate inference outputs. Software tests and hash checks establish implementation integrity. They do not certify physiology.

The full CNS remains the reference graph. The first calibrated runtime can be a bounded visual circuit if its excluded inputs and feedback are reported. A runtime containing all nodes with generic parameters would not establish greater biological accuracy.

## 2 Register visual inputs in physical visual space

Recover published eye geometry, receptor sampling directions, and compatible retinotopic assignments. The source hex grid is an anatomical indexing frame with an arbitrary origin [2]. The mapping into visual angle must address orientation, left/right correspondence, nonuniform sampling, optical blur, and visual-field boundaries.

Use the eye-geometry and T4 study's source material as a candidate calibration resource [3], with an explicit dataset/body-ID compatibility check. Use the MaleCNS visual-pathway study to guide receptive-field inference [4]. Recover its full methods and executable resources before claiming method reproduction; the inspected abstract alone does not specify an implementable algorithm.

Photoreceptor-labelled bodies currently have no assignedOlHex1/2 values in the local annotation file. Their outgoing connections can support candidate input locations, but incomplete terminals, neural superposition, and pooling must be accounted for. Do not treat each R1-R6-labelled body as a complete ommatidium or a fully reconstructed set of six receptors.

Acceptance: a receptor-to-ray mapping with exact body IDs, origin and transform provenance, coverage/ambiguity, and evaluation against independent maps or measurements. Compare with shuffled coordinate assignments and simpler type-based mappings. Mark unresolved inputs explicitly; do not create real body IDs for modeled missing receptors.

## 3 Fit and validate visual dynamics

Use the source graph as the connectivity constraint. Model graded membrane responses where appropriate; choose spiking models only with justification. Keep raw counts apart from fitted efficacies. Receptor/channel effects can depend on the postsynaptic target; a presynaptic neurotransmitter label alone is not a universal synaptic sign. Missing signs, time constants, adaptation, delays and modulatory effects need uncertainty or explicit fitted parameters.

FlyVis demonstrates a useful connectome-constrained, task-optimized approach and tests model responses against physiological studies [5]. It is a method reference here, not a replacement for the local MaleCNS graph or a source of automatically transferable fitted parameters.

Register training and evaluation splits before parameter selection. Possible calibration inputs include designated recordings and optic-flow tasks. Hold back stimulus families, conditions, or recordings for evaluation. Record the species, sex, cell-type matching, recording modality and experimental state of each physiological reference.

| Test | Measurement | Failure that it can expose |
| --- | --- | --- |
| Bright and dark flashes | Response polarity, amplitude, latency, adaptation | Incorrect contrast pathways or baseline dynamics |
| Moving edges and gratings | Direction and speed tuning, spatial and temporal frequency curves | Wrong retinotopy or integration times |
| Expanding and receding objects | Responses versus angular size/expansion and position | Generic motion response misidentified as looming selectivity |
| Spatially localized stimulation | Receptive-field center, shape and extent | Incorrect input registration or lateral integration |
| Held-out naturalistic motion | Response prediction across scenes | Overfitting to simple stimuli |
| Circuit silencing or perturbation | Predicted changes versus published experimental effects | Wrong circuit dependencies despite plausible baseline behavior |

Required comparisons: retinal sampling alone; an explicitly defined simple motion model; the same dynamics with degree/type-controlled rewiring; and parameter uncertainty ensembles. Define tolerances from measurement uncertainty and recorded variability before inspecting evaluation results. Do not manufacture a universal numerical threshold for scientific validity.

## 4 Build the first-person interactive world

Use a world renderer with physical scale, camera pose, spectral surface properties and an explicit simulation clock. The sensory model receives rendered light samples, not object labels, distance-to-food variables, or precomputed threat flags. Keep the retinal image, neural response visualization, and human-readable sensory display distinct.

Start with manual walking and turning through a small arena, where the same trajectory can be replayed for all models. Compare reference images, sampled receptor signals and modeled responses. UV channels require spectral scene information; RGB textures alone cannot recover UV reflectance [6]. False-colour assignments are display conventions, not claims about a fly's experienced colours.

Separate physics time, sensory sampling time, neural integration time, and display time. Report actual biological-time/wall-time throughput and error under time-step refinement. A slow model can support offline trajectory replay before it supports live interaction.

NeuroMechFly v2 is a candidate embodied backend: its published examples combine vision, olfaction, ascending feedback and a connectome-constrained visual model [7]. Confirm current interfaces, dependency compatibility, anatomical scale and model provenance before adopting it. Its controller outputs also require their own validation.

## 5 Add other senses and close the behavior loop

The full atlas retains sensory classes for olfaction, taste, mechanosensation, proprioception, thermosensation and hygrosensation where annotated. A class name is not a receptor transfer function. Add each modality when stimulus units, receptive surfaces/locations, receptor identities, and neural response models are supportable.

For example, odor requires concentration/plume dynamics and receptor tuning; touch requires contact location and force; proprioception requires joint state and its sensory encoding. Wind and vibration mappings require appropriate mechanosensory evidence rather than generic stimulation of all mechanosensory cells. Hunger, arousal and adaptation should be treated as state variables when evidence supports their effects.

Trace visual and other sensory processing toward the central brain, descending pathways and motor circuits in the reference graph. Fit or specify a motor/body interface separately. Validate closed-loop trajectories, orientation responses, collision behavior and intervention effects on held-out conditions. Manual control remains a distinct mode from neural control, with no silent wandering or object-geometry shortcuts in biological evaluations.

## Milestone record

| Milestone | Current status |
| --- | --- |
| Full local atlas and unsigned structural graph | Implemented; run receipts in runs/baseline |
| Candidate column support and structural holdout | Implemented; exploratory within-dataset evidence |
| Reference eye geometry | Imported 1,709 published directions; source/index/angle checks passed |
| Receptor-to-visual-angle registration | MaleCNS crosswalk unresolved; all local photoreceptor ray bindings remain null |
| Calibrated visual neural dynamics | Not implemented |
| Independent physiological validation | Not performed |
| First-person optical world | Colored garden with measured-ray forward view, manual flight and camera comparison; RGB illustrative, neural dynamics and MaleCNS registration pending |
| Validated whole-CNS sensory and motor simulation | Long-term objective |

## Primary references and scope

1. [MaleCNS official download catalogue](https://male-cns.janelia.org/download/): release files, schemas, coordinate units and license. Local flat-table identity is pinned by content hashes, not an assumed database UUID.
2. [Reiser Lab coordinate-system documentation](https://github.com/reiserlab/male-drosophila-visual-system-connectome-code/blob/main/docs/coordinate-systems.md): hex-coordinate conventions. This earlier optic-lobe resource does not by itself validate correspondence to every MaleCNS record.
3. [Eye structure shapes neuron function in Drosophila motion vision](https://www.nature.com/articles/s41586-025-09276-5), [author analysis repository](https://github.com/reiserlab/eyemap_T4): reference eye geometry imported from pinned commit 99d2a43123db636cedb55af9ff31a59657e7d17e. Published direction/index consistency checked; full analysis and physiological results have not been reproduced. See [the optics milestone](OPTICS_MILESTONE.md).
4. [Hoeller and colleagues, The organization of visual pathways in the Drosophila brain](https://www.janelia.org/publication/the-organization-of-visual-pathways-in-the-drosophila-brain): MaleCNS pathway and receptive-field framework. Abstract inspected; full-method reproduction remains future work.
5. [Lappalainen and colleagues, Connectome-constrained networks predict neural activity across the fly visual system](https://www.nature.com/articles/s41586-024-07939-3), [FlyVis implementation](https://github.com/TuragaLab/flyvis): dynamics/task-fitting and validation precedent.
6. [The spectral sensitivity of Drosophila photoreceptors](https://www.nature.com/articles/s41598-020-74742-1): experimentally measured spectral responses and optical filtering.
7. [NeuroMechFly v2](https://www.nature.com/articles/s41592-024-02497-y): embodiment and multimodal sensorimotor simulation precedent.
