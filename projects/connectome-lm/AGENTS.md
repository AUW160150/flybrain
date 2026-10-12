# Persistent experiment invariants
Read Experiment/CODEX_EXPERIMENT_PROMPT.md completely before changing this project.
- This is a small connectome-constrained byte language model, not a biological simulation.
- Main recurrent edge weights train from scratch on real male-cns:v1.0 neuron connectivity. No pretrained backbone or graph bypass.
- Preserve labelled per-node in/out degrees, edge-slot/interface initialization, data order and budgets in matched controls. Never pad parameter counts.
- Contiguous 90/5/5 byte splits precede windows. Training/tuning cannot load test bytes. Explicit frozen final evaluation only.
- Confirmation test evaluation is complete; preserve its frozen selection and results. Later revisions must not treat that test split as unseen or retune this study using its scores.
- Synthetic graphs require BOTH --synthetic and --smoke. Never use them for scientific results.
- Default execution stops at tests and bounded smoke. No automatic pilot/sweep, paid jobs, uploads or background training.
- Keep analysis-plan hashes, provenance, failures and actual execution in docs/STATUS.md. Smoke is not evidence that fly wiring helps.
- Preserve unrelated workspace files and permission boundaries; no sub-agent delegation is requested.
