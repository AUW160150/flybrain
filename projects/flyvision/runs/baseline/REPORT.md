# FlyVision sensory mapping baseline

This run indexes **165,122 traced MaleCNS v1.0 neurons** and preserves **25,563,197 raw directed connection rows**, representing **124,025,046 synapses** between those neurons. The source contains 211,577 annotated bodies in total; non-Traced statuses remain excluded and counted.

## Visual mapping coverage

- Visual superclasses contain 103,268 neurons. This is an annotation-defined set, not all neurons participating in vision.
- 23,720 traced neurons have source hex-coordinate pairs.
- 96,997 visual neurons have one-hop candidate column support; 6,271 have none under this rule.
- All physical stimulus bindings remain UNMAPPED. No neuron has a calibrated physiological model in this milestone.

Source hex coordinates describe locations in an eyemap, not viewing angles. Soma/root side is an explicitly provisional grouping hint, not proof of a visual hemifield. Source annotations remain intact in atlas.parquet. Candidates are kept separately in visual_candidates.parquet and column_support.npz; original coordinates are never overwritten.

## Structural holdout

The run hides 4,733 known coordinate pairs from the mapping anchors. It recovers the exact pair for 4,548 neurons (96.1% of all held-out neurons), with 4,720 supported predictions. Per-type and per-side results, including tied top candidates, are in holdout_validation.json.

This evaluates consistency with source annotations in the same animal. It does not validate physiological receptive fields, angular calibration, unannotated photoreceptors, T4/T5 receptive fields, or behavior. Source annotations themselves may have been inferred using connectivity, so this is not independent evidence of sensory function.

## Data and inference boundaries

Edges retain positive raw counts. Neurotransmitter predictions, confidence, consensus, and source ground-truth fields remain separate. No transmitter is automatically converted to excitation/inhibition; unknown transmitters are not assigned a default sign. No synapse count is presented as a physiological weight.

Candidate support sums counts to or from source-column anchors. Photoreceptors use outgoing links; other visual neurons use incoming links. Both use same-side hints and exclude self loops. Multiple supported columns and their relative mass are retained. Fractions and entropy measure the distribution of structural support, not confidence in the biological interpretation. Coverage denominators include partners outside the Traced set.

## Next scientific requirement

Recover and verify the eye-to-visual-angle transform and photoreceptor input mapping against published eye geometry and compatible source data. Fit temporal and synaptic parameters on designated physiological/training data, then evaluate separate held-out stimuli and interventions before connecting the model to a first-person world.

Primary method references and acceptance criteria are in ../../docs/RESEARCH_PLAN.md. This baseline is a structural foundation; no sensory simulation has been validated or run.
