# Project instructions

# MaleCNS Sugar Circuit Research Instructions

This repository is a rigorous computational-neuroscience replication
and extension project.

In the beginning of a fresh session involving this research, must read docs/RESEARCH_PROTOCOL.md plus the current STATUS.md and unresolved/mismatch logs before doing work.
## Source of truth

Before performing scientific analysis, read:

`docs/RESEARCH_PROTOCOL.md`

That document defines the complete research protocol, validation rules,
three-experiment design, provenance requirements, and stop conditions.

Also read, when they exist:

- `docs/paper_method_reconstruction.md`
- `docs/prompt_vs_paper_audit.md`
- `logs/decision_log.md`
- `logs/mismatch_ledger.csv`
- `logs/unresolved_questions.md`

Do not rely on conversation memory when these files contain the answer.

## Scientific priority

Primary sources outrank this repository's assumptions.

Priority:

1. Final published Tastekin et al. paper
2. Corrections / errata
3. Supplementary methods and source data
4. Official paper-associated code
5. Official Janelia MaleCNS resources
6. MaleCNS v1.0 neuPrint/raw records
7. Secondary sources only for cross-checking

If repository instructions conflict with a primary source,
record the discrepancy and follow the primary source.

## Target dataset

The target dataset for new analysis is:

`male-cns:v1.0`

Verify the active dataset before every analysis run.

Never silently substitute another dataset.

## Anti-hallucination rule

Never invent:

- body IDs
- neuron identities
- synapse counts
- connectivity weights
- neurotransmitters
- dataset versions
- thresholds
- equations
- paper claims
- cross-dataset mappings

Use:

- VERIFIED
- UNVERIFIED
- SOURCE CONFLICT
- BLOCKED — SOURCE REQUIRED
- INTERPRETATION

when appropriate.

## Three experiments

Use ONE validated implementation of the paper's methodology.

### Experiment 1
Strict paper replication.

### Experiment 2
Sugar-restricted extension:
- LB3b only
- LB3c only
- LB3b + LB3c

### Experiment 3
Independent MaleCNS v1.0 candidate-path test,
including the GNG021 hypothesis.

Do not force hypothesized neurons into results.

## Audit trail

Every important conclusion must be traceable to:

- paper passage,
- raw MaleCNS query,
- body-level connectivity record,
- or reproducible computation.

Append discrepancies to:

`logs/mismatch_ledger.csv`

Append scientific claims to:

`logs/claim_ledger.csv`

Record methodological decisions in:

`logs/decision_log.md`

Never delete an earlier incorrect claim.
Mark it superseded and record the correction.

## Before answering scientific questions

When asked why a neuron or edge was included:

1. inspect the saved query/data,
2. inspect the claim ledger,
3. inspect the relevant paper evidence,
4. inspect the decision/mismatch logs,
5. answer from those records rather than memory.

## Stop rather than guess

If a critical source, mapping, equation, body ID, or dataset version
cannot be verified, stop that analysis and document what is missing.

