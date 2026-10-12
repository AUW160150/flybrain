# FlyVision research instructions

The objective is an embodied sensory simulation constrained by the actual local MaleCNS connectome. Read README.md and docs/RESEARCH_PLAN.md before changing the scientific pipeline.

- Keep existing Flybrain source projects and raw datasets read-only. Write derivatives into this project.
- Preserve exact integer body IDs and dataset provenance. JSON exports of body IDs must use decimal strings.
- Preserve raw unsigned synapse counts separately from any modeled efficacy or sign. Keep NT prediction, confidence, consensus and source ground-truth fields separate.
- Do not default missing transmitter signs, physiology, eye coordinates, anatomical sides, or receptive fields to plausible values.
- Distinguish source annotations, structural inference, physiological observations, and model assumptions. Candidate maps are not measured receptive fields.
- Do not substitute another connectome or pretrained graph while describing the runtime as MaleCNS.
- Every run must record source hashes, code hashes, parameters, selection rules, and which validations were actually performed.
- Run the pipeline tests after changes to indexing, extraction, inference, or evidence labels. A code test is not a scientific validation.
- Existing run directories are immutable. Use a new output directory when rerunning changed methods.
- No source-column coordinate is a viewing angle until an eye geometry and coordinate transform have been verified. Side hints are not a substitute for that transform.
- Do not describe an atlas, unsigned structural propagation, or an uncalibrated model as a validated sensory or whole-brain simulation.

