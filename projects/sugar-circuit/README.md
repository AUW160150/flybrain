# MaleCNS sugar circuit v1

Current checkpoint: [Gates 2 and 3 — structural connectivity](docs/structural_connectivity_checkpoint.md). [Result bundle](results/structural/20261006T180116Z/README.md). All exported edges are cross-checked; bounded route/count exports and GraphML are ready. Experiments and simulations remain disabled. Earlier initial-checkpoint notes below are retained as history.


This project reconstructs and audits the gustatory sensorimotor method in Tastekin et al. (Cell, 2026), then plans three experiments using MaleCNS v1.0.

The authoritative [research protocol](docs/RESEARCH_PROTOCOL.md) is present (v0.1, 6 October 2026). Read [AGENTS.md](AGENTS.md), the full protocol, [STATUS.md](STATUS.md), [ASSUMPTIONS.md](ASSUMPTIONS.md), and the logs before scientific work.

The [initial validation checkpoint](docs/initial_validation_checkpoint.md) verifies authenticated dataset access and 95 target body identities. Method reconstruction is partial: full final STAR Methods and the paper's implementation/version remain required. **No experiments or simulations have been run.**

- [Primary sources and access limitations](SOURCES.md)
- [Partial method reconstruction](docs/paper_method_reconstruction.md)
- [Protocol-versus-paper audit](docs/prompt_vs_paper_audit.md)
- [Discrepancies](docs/discrepancy_report.md)
- [Manual validation](docs/manual_validation_guide.md)
- [Claim ledger](logs/claim_ledger.csv), [mismatch ledger](logs/mismatch_ledger.csv), [decisions](logs/decision_log.md), [unresolved questions](logs/unresolved_questions.md)
- [Latest validation output](results/validation/20261006T171922Z/summary.json) and [body records](results/validation/20261006T171922Z/resolved_bodies.csv)

Validation dependencies are pinned in `requirements-validation.txt`. `scripts/04_resolve_neuron_ids.py` compares saved primary records and creates a new timestamped output directory. It is not an experiment runner. Source downloads and raw queries have hashes and provenance logs; earlier results are retained.

The three experiment configs remain drafts with unvalidated methods/parameters. `config/analysis.yaml` records the checkpoint scope and disabled experiment/simulation state.

## Visualization framework

[Open local explorer](visualization/interactive/index.html) · [Figure index](visualization/docs/VISUALIZATION_INDEX.md) · [Build/reuse instructions](visualization/README.md). Current raw/paper-associated and independent candidate views are available. Sugar-selection panels await validated results; actual anatomy is explicitly BLOCKED by skeleton retrieval access and unverified camera orientation.

## Visualization framework

[Open local explorer](visualization/interactive/index.html) · [Figure index](visualization/docs/VISUALIZATION_INDEX.md) · [Build/reuse instructions](visualization/README.md). Current raw/paper-associated and independent candidate views are available. Sugar-selection panels await validated results; actual anatomy is explicitly BLOCKED by skeleton retrieval access and unverified camera orientation.
