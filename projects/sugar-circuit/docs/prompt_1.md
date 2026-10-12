You are continuing an existing computational-neuroscience research project.

Do NOT start this task from scratch.

This repository already contains:
- the governing research protocol
- initial identity validation
- MaleCNS v1.0 dataset validation
- body-ID validation
- raw structural-connectivity validation
- bounded structural path searches
- provenance/audit logs
- mismatch logs
- visualization-ready graph exports

Your next task is to move from:

“many structurally possible LB3 → feeding-motor paths”

to:

“a scientifically defensible, paper-grounded sensorimotor circuit selected using the published methodology.”

======================================================================
0. PRIMARY RESEARCH GOAL — READ THIS AT THE START OF EVERY SESSION
======================================================================

The overarching scientific goal of this repository is:

Determine the end-to-end neuronal wiring architecture connecting
sugar-associated gustatory sensory neurons to feeding/proboscis motor
output, using the current MaleCNS v1.0 connectome, while preserving
the distinction between:

1. raw structural connectivity,
2. paper-style effective-connectivity selection,
3. later dynamical/simulation evidence,
4. experimental biological evidence.

We are NOT trying to force a single “correct” pathway.

We expect there may be multiple scientifically useful versions:

A. PUBLISHED_REFERENCE
   The pathway reported by the original paper using its original
   MaleCNS snapshot / analysis.

B. V1_PAPER_REPLICATION
   The same published methodology applied to current male-cns:v1.0.

C. V1_SUGAR_RESTRICTED
   The validated paper methodology applied specifically to
   LB3b and/or LB3c.

D. V1_CANDIDATE_EXTENSIONS
   Additional current-v1.0 neurons or branches that survive the same
   scientific standard but were not reported by the paper.

E. SHIU_FLYWIRE_REFERENCE
   A separate later comparison against the Shiu/FlyWire sugar-response
   literature.

These versions must remain separate.

Differences are not failures.
Differences are scientific results that must be documented.

The immediate goal is NOT simulation.

The immediate goal is:

REPRODUCE THE PUBLISHED STRUCTURAL/EFFECTIVE-CONNECTIVITY CIRCUIT
ON CURRENT MALECNS v1.0,
THEN APPLY THE SAME FROZEN METHOD TO LB3b/LB3c.

======================================================================
1. REQUIRED SESSION STARTUP
======================================================================

Before doing any scientific work, read in this order:

1. `AGENTS.md`
2. `docs/RESEARCH_PROTOCOL.md`
3. `STATUS.md`
4. `docs/initial_validation_checkpoint.md`
5. `docs/structural_connectivity_checkpoint.md`
6. `docs/paper_method_reconstruction.md`
7. `docs/prompt_vs_paper_audit.md`
8. `logs/decision_log.md`
9. `logs/unresolved_questions.md`
10. `logs/mismatch_ledger.csv`
11. `logs/claim_ledger.csv`

Also inspect the most recent structural-run README/manifests and current
experiment YAML files.

Do not answer scientific questions from conversational memory when the
repository contains the underlying record.

If anything in this prompt conflicts with:
- the final paper,
- supplementary material,
- official source data,
- official paper-associated code,
- or verified MaleCNS records,

the primary source wins.

Record the discrepancy rather than silently changing the interpretation.

======================================================================
2. CURRENT VERIFIED BASELINE
======================================================================

The previous phases established a current-v1.0 structural baseline.

Do NOT redo all of this unless a concrete inconsistency is discovered.

The target dataset is:

`male-cns:v1.0`

Previous validation recorded UUID:

`4b2087c0fbe046bfaf0d60bc970e3e5d`

However, verify the dataset identity at the beginning of this new run
and log the result.

Previously verified source populations:

LB3a
LB3b
LB3c
LB3d

Previously verified motor targets:

MN4a
MN6
MN8
MN9

Previously tracked named neurons include:

GNG042 / Quasimodo
ANXXX462a / Clavicle
GNG015
GNG021

Do not substitute MN4b for MN4a.

The previous structural run found that raw reachability is extremely
dense:
most LB3 → requested-motor pairs are reachable within only 2–3 hops.

Therefore:

DO NOT USE SHORTEST-PATH EXISTENCE AS THE MAIN CIRCUIT-SELECTION METRIC.

That phase is complete.

======================================================================
3. IMPORTANT CORRECTIONS FROM THE STRUCTURAL PHASE
======================================================================

Preserve these findings as context, but independently verify them from
the saved results before using them in analysis.

A. GNG021 is NOT a direct LB3 recipient in current MaleCNS v1.0.

It is an INDIRECT candidate.

B. GNG021 overlaps strongly with the Quasimodo/GNG015 network.

Therefore do not describe GNG021 as an already-established independent
parallel circuit.

C. GNG021 has notable current-v1.0 direct connectivity toward MN6,
but structural weight alone is not functional proof.

D. GNG232 appeared naturally in the unrestricted structural search,
but it must not be called “the primary sugar pathway” based on
shortest-path frequency.

GNG232 belongs to a separate Shiu/FlyWire comparison line and should
later be evaluated under the same evidence framework.

E. Puddle's current MaleCNS body identity remains unresolved.

Do not invent a Puddle body ID.

F. Several current-v1.0 pooled raw motif weights differ from values
displayed in the Tastekin figure.

These differences remain scientifically unresolved and are one of the
questions this next experiment should investigate.

======================================================================
4. FIRST TASK — RECOVER AND FREEZE THE PAPER METHODOLOGY
======================================================================

Before running Experiment 1, independently reconstruct the exact
Tastekin methodology relevant to the LB3 → feeding-motor circuit.

Do not trust numerical values in this prompt unless the primary source
confirms them.

Re-fetch/re-open the final published paper and every relevant
supplement/source-data/code artifact that is legally accessible.

Priority:

1. final published Cell article
2. correction/erratum
3. STAR Methods / Methods
4. supplementary tables/figures
5. source data
6. official associated code/archive
7. author repository if explicitly tied to the publication
8. preprint only as a cross-check
9. secondary descriptions only as supporting context

Search specifically for the sections/functions describing:

- connectivity matrix construction
- synapse filtering
- cleft-score filtering
- GRN→MN effective connectivity
- normalization
- multi-hop propagation
- number of hops
- significant-path extraction
- 80th-percentile selection
- pruning
- 99th-percentile motif analysis
- bootstrap/null distributions
- GRN sample sizes
- random-neuron controls
- bilateral pooling
- body-level versus type-level pooling
- figure-generation/pooling rules
- neurotransmitter/sign handling

Create/update:

`docs/paper_method_reconstruction.md`

For EVERY methodological parameter record:

parameter_name
exact_value_or_equation
source_document
section
page_or_figure
quote_or_precise_paraphrase
code_file
function_name
verification_status
notes

Use statuses:

VERIFIED_FROM_FINAL_PAPER
VERIFIED_FROM_SUPPLEMENT
VERIFIED_FROM_CODE
PARTIAL
UNVERIFIED
SOURCE_CONFLICT

Do not begin the main replication if a missing method detail would
materially change node selection.

If a minor implementation detail cannot be recovered, do not guess
silently.

Document:

`RECONSTRUCTED_METHOD_ASSUMPTION`

with:
- what is missing,
- plausible choices,
- which choice is being tested,
- why,
- and a sensitivity analysis when feasible.

======================================================================
5. CRITICAL METHOD-AUDIT QUESTION
======================================================================

One major unresolved issue is that current-v1.0 all-body pooled weights
do not always equal the weights displayed in the paper's Figure 6.

Determine whether those differences can be explained by:

A. selected bodies rather than all bodies,
B. pathway pruning,
C. 99th-percentile partner filtering,
D. type pooling differences,
E. different dataset snapshot,
F. proofreading/version changes,
G. some other documented paper rule.

DO NOT assume which explanation is correct.

Create:

`docs/paper_vs_v1_weight_audit.md`

For every paper motif currently mapped, include:

source_type
target_type
paper_displayed_weight
current_v1_all_body_weight
paper_selected_body_ids_if_recoverable
v1_selected_body_ids
selected_v1_weight
difference
probable_explanation
evidence
status

At minimum include the previously mapped motifs involving:

GNG042 → GNG015
GNG015 → MN9
GNG015 → MN4a
ANXXX462a → GNG585
GNG585 → GNG108
GNG585 → GNG120
GNG108 → MN9
GNG108 → MN4a
GNG120 → MN9
GNG120 → MN4a
GNG585 → GNG472
GNG472 → MN8

Do not modify raw data to make values match the paper.

======================================================================
6. IMPLEMENT ONE PAPER-FAITHFUL ANALYSIS ENGINE
======================================================================

Use ONE implementation.

Do not write separate algorithms for different experiments.

Implement the verified paper methodology in:

`src/effective_connectivity.py`

or the existing equivalent.

The implementation must support:

- body-level directed connectivity
- raw synapse count
- paper-defined normalized edge weight
- multi-hop effective connectivity
- layer/hop normalization
- candidate selection
- pruning
- output-to-input or input-to-output criteria where specified
- bilateral handling
- paper-specific motif selection

Use current `male-cns:v1.0` as the replication graph.

Do not insert neurotransmitter signs into the effective-connectivity
calculation unless the paper explicitly does so.

If neurotransmitter sign is not part of the paper metric, preserve it as
metadata only.

======================================================================
7. UNIT TEST THE MATHEMATICS BEFORE BIOLOGICAL EXECUTION
======================================================================

Before applying the method to MaleCNS:

Create small synthetic graphs where the expected result can be
calculated by hand.

Test:

- one-hop score
- two-hop score
- three-hop score
- normalization
- zero-edge behavior
- multiple routes to the same neuron
- recurrent edge handling
- left/right duplicate types
- percentile selection
- pruning
- tie handling
- deterministic output

Write tests under:

`tests/test_effective_connectivity.py`
`tests/test_thresholds.py`

For each test document the hand-calculated expected result.

Do not continue if these tests fail.

======================================================================
8. EXPERIMENT 1R — PUBLISHED CIRCUIT REPRODUCTION IN MALECNS v1.0
======================================================================

This is the NEXT MAIN SCIENTIFIC EXPERIMENT.

Purpose:

Apply the paper's verified analysis method to current MaleCNS v1.0 and
ask whether the published LB3 → feeding-motor circuit is reproduced.

This is NOT yet the sugar-only experiment.

INPUT:

Use the exact paper input population.

If verified as:

LB3a
LB3b
LB3c
LB3d

use all verified bodies.

OUTPUTS:

MN4a
MN6
MN8
MN9

Use current verified body identities.

Run the paper's:
- edge normalization
- multi-hop calculation
- significant-path criteria
- pruning
- hop/layer treatment
- relevant motif filtering

exactly as verified.

Do NOT tune thresholds after seeing the result.

======================================================================
9. EXPERIMENT 1R REQUIRED OUTPUTS
======================================================================

Create a new timestamped directory:

`results/experiment_01_paper_replication/<run_id>/`

Generate at minimum:

`nodes.csv`
`edges.csv`
`effective_connectivity_by_hop.csv`
`selected_nodes.csv`
`selected_edges.csv`
`selection_reasons.csv`
`paper_node_comparison.csv`
`paper_edge_comparison.csv`
`paper_weight_comparison.csv`
`left_right_comparison.csv`
`motor_target_comparison.csv`
`circuit.graphml`
`manifest.json`
`report.md`

For every retained neuron record:

body_id
type
alias
side
role
hop/layer
raw_input_from_previous_layer
raw_output_to_next_layer
fraction_postsynaptic_input
fraction_presynaptic_output
effective_connectivity_from_input
effective_connectivity_to_output
normalized_effective_connectivity
percentile
selection_threshold
selection_status
paper_presence
paper_label
v1_status
source/provenance

For every selected edge:

pre_body_id
post_body_id
pre_type
post_type
raw_synapse_count
paper_normalized_weight
effective_connectivity_contribution_if_defined
hop
paper_edge_presence
paper_displayed_weight_if_any
current_v1_weight
agreement_status
notes

======================================================================
10. EXPERIMENT 1R SUCCESS CRITERIA
======================================================================

Do NOT define success as “looks similar.”

Quantify reproduction.

Produce metrics such as:

- paper neuron recall
- paper neuron precision where meaningful
- paper edge recall
- paper edge precision where meaningful
- exact weight matches
- near weight matches
- unresolved weight differences
- paper named-node recovery
- motor-target recovery
- topology overlap
- left/right mapping consistency

Specifically report whether current v1.0 recovers:

Quasimodo / GNG042
Clavicle / ANXXX462a
GNG015
Sternum / GNG585
Roundup / GNG108
Roundtree / GNG120
GNG472

and other paper-selected nodes recovered from the source material.

Do not force any of them into the result.

If an expected node fails selection, that is a result.

======================================================================
11. VERSIONED CIRCUIT MODEL
======================================================================

Create:

`results/circuit_versions/`

Maintain separate definitions:

`PUBLISHED_REFERENCE`
`V1_PAPER_REPLICATION`
`V1_SUGAR_LB3B`
`V1_SUGAR_LB3C`
`V1_SUGAR_LB3B_LB3C`
`V1_CANDIDATE_EXTENSIONS`
`SHIU_FLYWIRE_REFERENCE`

Do not merge them.

Create:

`results/circuit_versions/version_comparison.csv`

Columns:

node_or_edge
published_reference
v1_paper_replication
v1_lb3b
v1_lb3c
v1_lb3b_lb3c
v1_candidate
shiu_reference
raw_weight
normalized_weight
effective_connectivity
percentile
paper_support
dataset
dataset_version
status
difference_reason
notes

Allowed status labels include:

PAPER_AND_V1_MATCH
PAPER_ONLY
V1_ONLY
WEIGHT_CHANGED
SELECTION_CHANGED
BODY_MAPPING_CHANGED
UNRESOLVED
SUGAR_SELECTED
CANDIDATE_EXTENSION

======================================================================
12. CHECKPOINT AFTER EXPERIMENT 1R
======================================================================

STOP after Experiment 1R initially.

Create:

`docs/experiment_01_replication_checkpoint.md`

Answer:

1. Was the paper's method fully recovered?
2. Which pieces remain assumptions?
3. Did current MaleCNS v1.0 recover the published circuit?
4. Which named neurons were recovered?
5. Which were missing?
6. Which additional v1.0 neurons were selected?
7. Which paper weights now match after correct selection/pooling?
8. Which still differ?
9. What explains each difference?
10. Is the implementation scientifically trustworthy enough to freeze?
11. Is the method ready to be applied unchanged to LB3b/LB3c?

IF the answer to #10 or #11 is NO:
STOP.
Do not run the sugar experiment.

IF YES:
freeze the implementation and configuration.

Record its Git commit/config hash.

======================================================================
13. EXPERIMENT 2 — SUGAR-RESTRICTED V1.0 CIRCUIT
======================================================================

Only run this after Experiment 1R passes the replication checkpoint.

Use the EXACT SAME frozen implementation.

Change only the sensory input population.

Run:

2A — LB3b only

2B — LB3c only

2C — LB3b + LB3c

Targets remain:

MN4a
MN6
MN8
MN9

Do not retune:
- thresholds
- normalization
- hop count
- percentile criteria
- pruning
- pooling rules

because the scientific question is:

“What changes when only the biological input changes?”

======================================================================
14. IMPORTANT DEFINITION OF “SUGAR-RESTRICTED”
======================================================================

For the PRIMARY experiment:

“LB3b-only” or “LB3c-only” means:

ONLY those neurons are the starting sensory input.

The rest of the MaleCNS network remains intact.

Do NOT delete LB3a, LB3d, or other sensory neurons from the graph unless
the paper methodology explicitly requires it.

This corresponds more closely to an intact biological CNS where only
the selected input population is externally activated.

Separately, as a SENSITIVITY ANALYSIS, optionally test:

`NO_OTHER_GRN_RELAY`

where non-source gustatory sensory neurons are forbidden as intermediate
relays.

Label this clearly as a secondary artificial restriction.

Never mix the results.

======================================================================
15. EXPERIMENT 2 OUTPUTS
======================================================================

For each of 2A, 2B, 2C create:

nodes.csv
edges.csv
effective_connectivity_by_hop.csv
selected_nodes.csv
selected_edges.csv
motor_target_scores.csv
left_right_scores.csv
convergence_points.csv
divergence_points.csv
paper_overlap.csv
candidate_overlap.csv
circuit.graphml
report.md

Then produce:

`results/experiment_02_sugar_restricted/comparison.csv`

Compare:

LB3b
LB3c
LB3b+LB3c

for:

- selected neurons
- selected edges
- first strong downstream partners
- effective connectivity
- motor targets
- hop/layer
- bilateral consistency
- raw synapse weights
- normalized weights
- paper overlap
- unique branches
- shared branches

======================================================================
16. SPECIFIC QUESTIONS FOR EXPERIMENT 2
======================================================================

Answer explicitly:

1. Does Quasimodo survive with LB3b alone?
2. Does Quasimodo survive with LB3c alone?
3. Does Quasimodo survive with combined LB3b+LB3c?

4. Does Clavicle survive each condition?

5. Does GNG015 survive each condition?

6. Is the Quasimodo→GNG015→motor motif retained?

7. Which motor outputs are strongest under:
   LB3b?
   LB3c?
   combined?

8. Is LB3c actually stronger than LB3b through the COMPLETE pathway,
   or only at particular first-hop edges?

9. Where do LB3b and LB3c first converge under the selected circuit?

10. Which selected branches are unique to LB3b?

11. Which are unique to LB3c?

12. Which published nodes disappear when the input becomes sugar-specific?

13. Which current-v1.0 nodes newly enter the sugar-selected circuit?

======================================================================
17. TRACK GNG021 BUT DO NOT FORCE IT
======================================================================

GNG021 is a sentinel candidate, not an input or required result.

For each Experiment 2 condition record:

- selected or not selected
- effective-connectivity score
- percentile
- hop/layer
- strongest upstream selected neurons
- strongest downstream selected neurons
- motor target association
- relation to Quasimodo
- relation to GNG015
- left/right pattern

Classify GNG021 as:

SELECTED_BY_PAPER_METHOD

STRUCTURALLY_STRONG_BUT_NOT_SELECTED

WEAK_STRUCTURAL_CANDIDATE

NO_SUPPORT

Do not call it a separate parallel sugar pathway unless the selected
network actually supports that interpretation.

Given the structural checkpoint, consider the alternative hypothesis:

“GNG021 is an overlapping higher-order branch, potentially associated
more strongly with MN6.”

Test this rather than assuming it.

======================================================================
18. TRACK SHIU/MINECRAFT CANDIDATES SEPARATELY
======================================================================

Do NOT merge Shiu/FlyWire evidence into the Tastekin selection algorithm.

However, after the unrestricted Tastekin-based selection is complete,
check whether these independently motivated neurons appear naturally:

GNG232 / G2N-1
DNg67 / Fudog
DNge080 / Rounddown

For each report:

- selected by Tastekin method?
- present structurally?
- raw weight
- effective-connectivity score
- hop/layer
- motor association
- relation to LB3b/LB3c
- Shiu evidence source

Call this:

`SHIU_CROSS_VALIDATION`

not paper replication.

======================================================================
19. EVIDENCE MATRIX
======================================================================

Create:

`results/cross_experiment/neuron_evidence_matrix.csv`

Columns:

body_id
type
alias
dataset
paper_structural_support
current_v1_raw_support
tastekin_v1_selection
lb3b_selection
lb3c_selection
combined_selection
gng021_candidate_status
shiu_dynamic_support
experimental_support
raw_weight_summary
effective_connectivity
percentile
motor_targets
evidence_notes
confidence

Do not fill Shiu or experimental columns from memory.

Only fill them when their sources have been explicitly verified.

======================================================================
20. DO NOT RUN DYNAMICAL SIMULATION YET
======================================================================

Do not run:
- LIF
- electrical stimulation
- Poisson stimulation
- Minecraft-style stimulus experiments
- lesion/silencing dynamics

during this task.

Those come later.

First establish the selected anatomical/effective-connectivity circuit.

======================================================================
21. VISUALIZATION OUTPUT AFTER SELECTION
======================================================================

Once Experiment 1R and Experiment 2 are complete, update the existing
visualization system.

Generate separate views for:

A. PUBLISHED_REFERENCE
B. V1_PAPER_REPLICATION
C. V1_LB3B
D. V1_LB3C
E. V1_LB3B_LB3C
F. V1_GNG021 candidate overlay
G. SHIU-cross-validation overlay

Each figure must distinguish:

RAW STRUCTURAL EDGE

versus

SELECTED BY EFFECTIVE-CONNECTIVITY METHOD

Do not make a raw structural edge visually equivalent to a selected
pathway edge.

Keep:
- body ID
- side
- synapse count
- normalized weight
- effective-connectivity score
- percentile
- selection status
- evidence category

available on hover or in accompanying tables.

Also prepare body-ID lists for later skeleton/anatomy rendering.

======================================================================
22. ANATOMICAL END-TO-END CIRCUIT DELIVERABLE
======================================================================

The eventual core deliverable should make it possible to say:

“Here are the sugar-associated sensory neurons.
Here are the selected downstream neurons.
Here is the ordered end-to-end architecture leading to each feeding
motor target.
Here are the raw anatomical weights.
Here are the paper-normalized/effective-connectivity values.
Here is what matches the published circuit.
Here is what changed in current v1.0.
Here are current-v1.0-only branches.”

Create a human-readable master table:

`results/final/sugar_sensorimotor_architecture.csv`

with columns:

circuit_version
stage
hop
body_id
type
alias
side
role
upstream_body_id
upstream_type
raw_synapse_count
fraction_postsynaptic_input
fraction_presynaptic_output
effective_connectivity
normalized_effective_connectivity
percentile
selection_status
motor_target
paper_support
v1_support
shiu_support
experimental_support
dataset
dataset_version
source
notes

Do not create a “final” sugar table until Experiment 2 has successfully
run.

======================================================================
23. PERMANENT LOGGING REQUIREMENTS
======================================================================

Continue appending to:

`logs/claim_ledger.csv`
`logs/mismatch_ledger.csv`
`logs/query_log.jsonl`
`logs/decision_log.md`
`logs/unresolved_questions.md`
`STATUS.md`

Do not overwrite historical entries.

If an older claim becomes wrong:

mark it superseded.

Do not delete it.

Every important numerical claim must be traceable to:

paper passage
OR
paper source data
OR
raw MaleCNS record
OR
reproducible computation.

======================================================================
24. SCIENTIFIC STOP / FLAG RULE
======================================================================

This is extremely important.

Your job is NOT to force the project toward the expected conclusion.

At every major stage ask:

“Does this step still answer the project's core scientific question?”

Core question:

Can previously reported gustatory/sugar sensorimotor wiring be
recovered in current MaleCNS v1.0, and when the same validated
selection method is restricted to sugar-associated LB3b/LB3c inputs,
what defensible end-to-end neural architecture remains?

If a proposed step does NOT help answer that question:

FLAG IT.

Do not automatically perform it.

Write:

`DIRECTION_CHECK_FAILED`

and explain:

- proposed action
- why it does not directly support the goal
- what alternative would better support the goal

If new evidence invalidates an assumption in the protocol:

do not force the analysis to preserve the old plan.

Create:

`SCIENTIFIC_PLAN_REVISION_REQUIRED`

and explain:

1. old assumption
2. new evidence
3. consequence
4. recommended revision
5. whether previous results remain valid

Wait for confirmation only if the revision would materially change
the research question or invalidate a major completed experiment.

======================================================================
25. DO NOT EQUATE THESE TERMS
======================================================================

Keep these categories separate:

STRUCTURALLY_PRESENT
= there is an anatomical edge.

STRUCTURALLY_STRONG
= raw/normalized anatomical weight is high under an explicit metric.

SELECTED_BY_PAPER_METHOD
= survives the verified Tastekin selection algorithm.

DYNAMICALLY_RECRUITED
= later LIF simulation activates it.

EXPERIMENTALLY_SUPPORTED
= biological experiment supports its role.

Do not collapse them into one concept called “the pathway.”

======================================================================
26. FINAL CHECKPOINT FOR THIS TASK
======================================================================

At the end create:

`docs/effective_connectivity_and_sugar_checkpoint.md`

The report must include:

PART A — Method
- exact Tastekin methodology recovered
- equations
- thresholds
- hop rules
- filtering
- pooling
- source citations
- unresolved assumptions

PART B — Paper reproduction
- selected current-v1.0 nodes
- selected edges
- paper-v1 overlap
- missing published nodes
- new v1 nodes
- weight comparisons
- explanation/status of previous discrepancies
- quantitative replication metrics

PART C — Sugar-restricted result
- LB3b circuit
- LB3c circuit
- combined circuit
- shared nodes
- unique nodes
- convergence points
- motor outputs
- Quasimodo status
- Clavicle status
- GNG015 status
- GNG021 status

PART D — Cross-literature candidates
- GNG232 status
- Fudog status
- Rounddown status
- whether these naturally intersect the v1 sugar-selected circuit

PART E — Version comparison
- PUBLISHED_REFERENCE
- V1_PAPER_REPLICATION
- V1_SUGAR
- V1_CANDIDATE
- SHIU_REFERENCE

PART F — Scientific interpretation
Explicitly separate:
- what is directly measured anatomy
- what is graph-derived inference
- what is published functional evidence
- what remains unknown

PART G — Next step recommendation

Do NOT automatically start simulation.

Recommend the next step based on the actual results.

======================================================================
27. COMMUNICATION STANDARD
======================================================================

When reporting results, never simply say:

“the pathway matches”
or
“the pathway is different.”

Quantify it.

Whenever possible say:

- X/Y paper nodes recovered
- X/Y paper edges recovered
- exact synapse-count difference
- effective-connectivity difference
- percentile difference
- left/right difference
- which dataset/version each value came from

If a number cannot be traced:
do not report it as fact.

======================================================================
28. BEGIN
======================================================================

Begin with:

A. session startup/context read
B. method recovery/audit
C. paper-v1 pooling discrepancy investigation
D. implementation + synthetic tests
E. Experiment 1R

STOP at the Experiment 1R checkpoint if the method is not trustworthy.

If Experiment 1R passes the predeclared replication criteria, continue
with Experiment 2A/2B/2C using the frozen implementation.

Do not run simulation.

Do not fabricate Puddle.

Do not force GNG021 or GNG232.

Do not alter paper thresholds to improve agreement.

The purpose of this work is to reconstruct an auditable end-to-end
sugar-associated neural architecture, while preserving every meaningful
difference between published wiring and current MaleCNS v1.0.