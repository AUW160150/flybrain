# Research protocol

You are acting as a computational neuroscience research engineer and an independent scientific auditor.

Your task is to reconstruct, verify, and compare gustatory sensorimotor pathways in Drosophila using the MaleCNS v1.0 connectome.

This is not a brainstorming exercise.

Do not invent missing information.

Do not optimize for agreeing with my hypothesis.

The goal is to produce an auditable, reproducible record of what the primary paper actually did, what MaleCNS v1.0 actually contains, where they agree, where they differ, and what conclusions are scientifically defensible.

======================================================================
CORE SCIENTIFIC OBJECTIVE
======================================================================

We want to identify a defensible end-to-end neural subnetwork beginning with sugar-associated gustatory receptor neurons and ending at feeding/proboscis motor output.

The working sensory populations of interest are:

LB3b
LB3c

because the paper we are studying associates these most closely with Gr64f-positive sweet/sugar-related labellar GRNs.

However:

Do NOT assume that LB3b and LB3c are exclusively sugar sensing.

Do NOT assume that every downstream structural connection is functionally significant.

Do NOT assume that anything we discussed previously is correct until you verify it.

We will conduct THREE PARALLEL EXPERIMENTS using the SAME validated analysis implementation.

======================================================================
MOST IMPORTANT RULE: READ THE PAPER FIRST
======================================================================

Before writing or executing the main analysis:

1. Locate the final published Tastekin et al. 2026 Cell paper concerning the complete gustatory connectome of adult Drosophila.

2. Verify:
   - exact title
   - authors
   - publication date
   - DOI
   - journal version
   - whether there are corrections or errata

3. Obtain, where legally/publicly accessible:
   - full paper
   - STAR Methods / Methods
   - supplementary figures
   - supplementary tables
   - Table S1
   - supplementary datasets
   - source-data files
   - associated code repository
   - repository commit/version used by the paper if identifiable

4. Read the relevant Methods and Results sections in full.

5. Inspect the exact figures describing:
   - LB3 classification
   - sugar/sweet receptor matching
   - effective connectivity
   - LB3 → feeding motor pathways
   - Quasimodo / GNG042
   - Clavicle / ANXXX462a
   - GNG015
   - motor neurons
   - significant-path analysis
   - simulation analysis

Do NOT rely on:
- abstract only
- search-result snippets
- our prior conversation
- this prompt
- a secondary summary

The paper and associated official code are the scientific source of truth.

======================================================================
SOURCE PRIORITY
======================================================================

When sources conflict, use this priority:

1. final published paper
2. published correction / erratum
3. supplementary methods and supplementary tables
4. official source-data files
5. official code tied to the paper
6. official Janelia MaleCNS v1.0 resources
7. official neuPrint MaleCNS v1.0 data
8. official MaleCNS annotation repositories
9. secondary resources only as cross-checks

If the published text and associated code disagree:

DO NOT silently choose one.

Record the conflict explicitly.

======================================================================
ANTI-HALLUCINATION RULES
======================================================================

Never invent:

- body IDs
- neuron names
- cell-type mappings
- synapse counts
- connection weights
- percentages
- neurotransmitters
- dataset versions
- thresholds
- hop counts
- equations
- statistical parameters
- aliases
- FlyWire ↔ MaleCNS mappings
- MANC ↔ MaleCNS mappings
- paper claims

Use these labels whenever necessary:

VERIFIED
UNVERIFIED
BLOCKED — SOURCE REQUIRED
SOURCE CONFLICT
INTERPRETATION
PAPER_REPLICATION
PAPER_DERIVED_EXTENSION
NOVEL_V1_STRUCTURAL_CANDIDATE

If you are uncertain, say exactly:

“I am uncertain about X because Y.”

Never convert uncertainty into a confident statement.

======================================================================
CREATE A COMPLETELY ISOLATED PROJECT
======================================================================

Create:

~/malecns_sugar_circuit_v1/

Do not modify unrelated repositories.

Initialize a dedicated Git repository.

Create this structure:

malecns_sugar_circuit_v1/
│
├── README.md
├── SOURCES.md
├── ASSUMPTIONS.md
├── CHANGELOG.md
├── STATUS.md
│
├── config/
│   ├── analysis.yaml
│   ├── source_manifest.yaml
│   └── experiments/
│       ├── experiment_01_paper_replication.yaml
│       ├── experiment_02_sugar_restricted.yaml
│       └── experiment_03_v1_candidate.yaml
│
├── paper/
│   ├── primary/
│   ├── supplement/
│   ├── source_data/
│   └── code/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── scripts/
│   ├── 00_environment_check.py
│   ├── 01_fetch_primary_sources.py
│   ├── 02_parse_paper_methods.py
│   ├── 03_audit_prompt_vs_paper.py
│   ├── 04_resolve_neuron_ids.py
│   ├── 05_query_v1_connectivity.py
│   ├── 06_validate_raw_edges.py
│   ├── 07_effective_connectivity.py
│   ├── 08_experiment_01_paper_replication.py
│   ├── 09_experiment_02_sugar_restricted.py
│   ├── 10_experiment_03_v1_candidate.py
│   ├── 11_cross_experiment_comparison.py
│   └── 12_generate_reports.py
│
├── src/
│   ├── data_access.py
│   ├── effective_connectivity.py
│   ├── graph_utils.py
│   ├── provenance.py
│   ├── validation.py
│   └── audit.py
│
├── tests/
│   ├── test_dataset_version.py
│   ├── test_neuron_resolution.py
│   ├── test_edge_weights.py
│   ├── test_effective_connectivity.py
│   ├── test_thresholds.py
│   └── test_reproducibility.py
│
├── results/
│   ├── experiment_01_paper_replication/
│   ├── experiment_02_sugar_restricted/
│   │   ├── lb3b_only/
│   │   ├── lb3c_only/
│   │   └── lb3b_lb3c_combined/
│   ├── experiment_03_v1_candidate/
│   │   ├── lb3b_only/
│   │   ├── lb3c_only/
│   │   └── lb3b_lb3c_combined/
│   ├── validation/
│   └── cross_experiment/
│
├── docs/
│   ├── paper_method_reconstruction.md
│   ├── prompt_vs_paper_audit.md
│   ├── pre_analysis_decision_report.md
│   ├── experiment_01_notes.md
│   ├── experiment_02_notes.md
│   ├── experiment_03_notes.md
│   ├── discrepancy_report.md
│   ├── manual_validation_guide.md
│   ├── manual_query_examples.md
│   ├── circuit_dictionary.md
│   └── final_interpretation.md
│
└── logs/
    ├── run_manifest.jsonl
    ├── claim_ledger.csv
    ├── mismatch_ledger.csv
    ├── query_log.jsonl
    ├── decision_log.md
    └── unresolved_questions.md

======================================================================
LOCK THE TARGET CONNECTOME
======================================================================

The target dataset for our new analysis is:

male-cns:v1.0

Before doing anything else, verify that this exact dataset is active.

Record:

- server
- dataset
- UUID if available
- dataset release/version
- access date
- package versions
- Python version
- operating system
- Git commit
- analysis configuration
- confidence thresholds
- query settings

If the query is accidentally running against:

male-cns:v0.9

or another connectome:

STOP.

Do not continue.

If the PAPER used a different MaleCNS snapshot, pre-release dataset, v0.9, or an unspecified dataset:

record that fact.

Do NOT falsely claim the paper used v1.0.

Our work should then be described as:

“Replication of the published method using MaleCNS v1.0.”

======================================================================
PAPER METHOD RECONSTRUCTION
======================================================================

Create:

docs/paper_method_reconstruction.md

Extract the exact methodology for:

- GRN identification
- GRN subtype classification
- LB3a/b/c/d definitions
- taste-modality/receptor matching
- motor-neuron identification
- synapse filtering
- cleft-score thresholds
- adjacency construction
- edge weighting
- normalization
- effective connectivity
- multi-hop propagation
- bootstrapping
- null distributions
- random sampling
- percentile thresholds
- significant-path selection
- circuit pruning
- bilateral pooling
- neurotransmitter handling
- disinhibition motif analysis
- network simulation

For every numerical parameter record:

VALUE
SOURCE
PAGE/SECTION
FIGURE/TABLE
CODE FILE/FUNCTION if available

Do not trust any numerical parameter from this prompt unless the paper verifies it.

======================================================================
AUDIT THIS PROMPT AGAINST THE PAPER
======================================================================

Create:

docs/prompt_vs_paper_audit.md

For every important assumption classify:

CONFIRMED BY PAPER
CONFIRMED BY CODE
PARTIALLY SUPPORTED
UNSUPPORTED
CONTRADICTED
UNCLEAR

Audit at minimum:

- whether published analysis starts with LB3a-d
- whether LB3b/LB3c are the best sugar-associated populations
- whether LB3b overlaps with other taste modalities
- identity of Quasimodo / GNG042
- identity of Clavicle / ANXXX462a
- role of GNG015
- whether GNG021 appears in the paper
- motor-neuron identities
- effective-connectivity definition
- percentile rules
- hop rules
- bootstrap procedure
- dataset version

If our prior assumptions are wrong:

CORRECT THEM.

Do not make the paper conform to this prompt.

======================================================================
RESOLVE ALL RELEVANT NEURONS IN MALECNS v1.0
======================================================================

Resolve individual body IDs for:

LB3a
LB3b
LB3c
LB3d

Also resolve the paper's target motor neurons.

Investigate at minimum:

MN4 / MN4a
MN6
MN8
MN9

Also resolve:

GNG042
alias: Quasimodo

ANXXX462a
alias: Clavicle

GNG015

GNG021

For every neuron/body record:

body_id
cell_type
side
soma_side
class
nerve
predicted neurotransmitter
NT confidence
dataset
source
timestamp

Never infer a body ID from a cell-type name.

======================================================================
RAW CONNECTIVITY VALIDATION
======================================================================

For every important edge, validate using at least TWO independent representations when possible:

1. targeted neuPrint query
2. official MaleCNS v1.0 connection/weight table

For especially important edges, inspect individual synapses if necessary.

Record:

pre_body_id
post_body_id
raw_weight_neuprint
raw_weight_flat_file
difference
status

Allowed status values:

EXACT_MATCH
EXPLAINED_DIFFERENCE
MISMATCH
UNVERIFIED

An unexplained mismatch is a blocker.

======================================================================
STRUCTURAL SIGNIFICANCE METRICS
======================================================================

Do not call an edge “important” merely because it exists.

For each candidate edge calculate:

1. raw body-to-body synapse count
2. percentage of presynaptic neuron's total output
3. percentage of postsynaptic neuron's total input
4. rank among presynaptic output partners
5. rank among postsynaptic input partners
6. percentile among comparable edges
7. bilateral consistency
8. body-level consistency within the cell type
9. paper-style effective connectivity
10. whether the edge survives the paper's path-selection procedure

Use these terms carefully:

STRUCTURALLY PRESENT

STRUCTURALLY STRONG

SELECTED BY PAPER METHOD

FUNCTIONALLY SUPPORTED

Do not treat them as synonyms.

======================================================================
IMPORTANT HYPOTHESIS WE ARE TESTING
======================================================================

Current MaleCNS v1.0 summaries suggest that direct input from LB3c to Quasimodo may be substantially stronger than LB3b → Quasimodo.

Do NOT encode that as a conclusion.

Treat it as a hypothesis:

HYPOTHESIS H1:
LB3c contributes more strongly than LB3b to the Quasimodo branch.

Test it using:

- raw body-level edges
- normalized input fraction
- normalized output fraction
- effective connectivity
- full multi-hop pathway score
- paper-style selection thresholds

Only call the WHOLE PATHWAY “LB3c-dominated” if the multi-hop analysis supports it.

======================================================================
ONE CODEBASE — THREE PARALLEL EXPERIMENTS
======================================================================

Do not make three separate implementations.

Use ONE validated implementation of the paper's algorithm.

Only biological inputs/hypotheses may differ.

This is critical for a fair comparison.

######################################################################
EXPERIMENT 01 — STRICT PAPER REPLICATION
######################################################################

Goal:

Reproduce the published LB3 → feeding-motor circuit in MaleCNS v1.0.

Input:

Use exactly the population specified by the final paper.

If the paper confirms LB3a + LB3b + LB3c + LB3d, use those.

Do not substitute LB3b/LB3c here.

Use exactly the paper's:

- normalization
- effective-connectivity implementation
- hop limits
- bootstrap procedure
- percentile thresholds
- pruning logic
- output population

Questions:

1. Does MaleCNS v1.0 reproduce the paper's circuit?

2. Does it recover:
   - Quasimodo / GNG042
   - Clavicle / ANXXX462a
   - GNG015
   - reported motor outputs

3. Which published nodes do not appear?

4. Which v1.0 nodes appear that are absent from the paper?

Do NOT tune thresholds to make the result resemble the figure.

Outputs:

results/experiment_01_paper_replication/nodes.csv
results/experiment_01_paper_replication/edges.csv
results/experiment_01_paper_replication/effective_connectivity.csv
results/experiment_01_paper_replication/circuit.graphml
results/experiment_01_paper_replication/report.md

######################################################################
EXPERIMENT 02 — SUGAR-RESTRICTED PAPER-DERIVED CIRCUIT
######################################################################

Goal:

Use the SAME validated algorithm but restrict sensory input to sugar-associated populations.

Run separately:

2A:
LB3b only

2B:
LB3c only

2C:
LB3b + LB3c

Do not combine them prematurely.

Track but do NOT force:

GNG042 / Quasimodo
GNG015
ANXXX462a / Clavicle

Primary paper-derived pathway hypothesis:

LB3 sugar-associated inputs
→ Quasimodo
→ inhibitory/premotor layer including GNG015
→ feeding motor neurons

For every condition determine:

- whether Quasimodo survives selection
- whether GNG015 survives selection
- whether Clavicle survives selection
- strongest downstream routes
- first convergence points
- effective connectivity
- hop count
- structural weights
- motor outputs reached
- left/right asymmetry
- neurotransmitter composition

Specifically compare:

LB3b → Quasimodo

versus

LB3c → Quasimodo

and then compare their COMPLETE downstream paths.

Do not call LB3c dominant simply from the first edge.

Outputs:

results/experiment_02_sugar_restricted/lb3b_only/
results/experiment_02_sugar_restricted/lb3c_only/
results/experiment_02_sugar_restricted/lb3b_lb3c_combined/

Classify findings as:

PAPER_DERIVED_EXTENSION

######################################################################
EXPERIMENT 03 — INDEPENDENT MALECNS v1.0 CANDIDATE BRANCH
######################################################################

Goal:

Test whether a structural candidate discovered in MaleCNS v1.0 survives the exact same analysis used by the paper.

Candidate hypothesis:

LB3b/LB3c
→ GNG042 / Quasimodo
→ GNG021
→ MN6

CRITICAL RULE:

Do NOT manually insert GNG021 into the final graph.

GNG021 is a hypothesis.

The algorithm must decide whether it survives.

Run:

3A:
LB3b only

3B:
LB3c only

3C:
LB3b + LB3c

For GNG021 test:

- body-level structural connectivity
- raw synapse weights
- % presynaptic output
- % postsynaptic input
- bilateral consistency
- percentile ranking
- effective connectivity from sensory input
- effective connectivity toward motor output
- paper-style threshold
- paper-style pruning
- resulting path strength to MN6

Classify GNG021 as exactly one of:

SELECTED_BY_PAPER_METHOD

STRUCTURALLY_STRONG_BUT_NOT_SELECTED

WEAK_STRUCTURAL_CANDIDATE

NO_SUPPORT

Do not describe this branch as paper-confirmed unless the paper explicitly contains it.

Classify findings as:

NOVEL_V1_STRUCTURAL_CANDIDATE

######################################################################
HEAD-TO-HEAD PATH COMPARISON
######################################################################

Directly compare:

Quasimodo
→ GNG015
→ downstream motor output

versus

Quasimodo
→ GNG021
→ downstream motor output

Use exactly the same metrics:

raw synapse count
presynaptic-output fraction
postsynaptic-input fraction
partner rank
percentile
effective connectivity
hop score
left/right consistency
motor target reached
neurotransmitter prediction
paper support
algorithm selection status

Do not favor GNG015 simply because it is in the paper.

Do not favor GNG021 simply because it appears strong in v1.0.

======================================================================
PERMANENT CLAIM LEDGER
======================================================================

Create:

logs/claim_ledger.csv

Every meaningful scientific statement produced by the analysis must receive a unique claim_id.

Columns:

claim_id
timestamp
experiment
claim
claim_type
source_1
source_2
dataset
body_ids
edge_ids
support_level
verification_status
confidence
notes
supersedes_claim_id

Example claim types:

PAPER_CLAIM
RAW_DATA_CLAIM
COMPUTATIONAL_RESULT
INTERPRETATION
DISCREPANCY
CORRECTION

This file must NEVER be overwritten.

Append new information.

If a claim later turns out to be wrong:

do not delete it.

Mark it superseded and create a corrected claim.

======================================================================
PERMANENT MISMATCH LEDGER
======================================================================

Create:

logs/mismatch_ledger.csv

Any disagreement must be recorded permanently.

Examples:

paper vs v1.0

neuPrint vs flat file

type-level summary vs body-level records

left vs right

Codex result vs source data

current analysis vs previous run

Columns:

mismatch_id
timestamp
experiment
item
source_A
value_A
source_B
value_B
severity
possible_explanation
resolved
resolution
related_claim_ids
follow_up_required

Do not discard small mismatches.

They may become important later.

======================================================================
DECISION LOG
======================================================================

Create:

logs/decision_log.md

Whenever the analysis makes a methodological decision, record:

DATE/TIME

QUESTION

AVAILABLE EVIDENCE

OPTIONS

DECISION

WHY

ALTERNATIVES REJECTED

WHAT WOULD CHANGE THIS DECISION

This is essential so I can later ask:

“Why did you include this neuron?”

or

“Why was this edge removed?”

and retrieve the original reasoning.

======================================================================
UNRESOLVED QUESTIONS
======================================================================

Create:

logs/unresolved_questions.md

Maintain continuously.

Each unresolved issue must include:

ID

QUESTION

WHY IT MATTERS

CURRENT EVIDENCE

WHAT IS MISSING

WHAT WOULD RESOLVE IT

STATUS

Never silently forget unresolved questions.

======================================================================
QUERY LOGGING
======================================================================

Every query to MaleCNS/neuPrint must be logged.

Save:

logs/query_log.jsonl

Record:

timestamp
experiment
purpose
dataset
query
parameters
returned row count
output file
hash/checksum if possible
errors

Do not include passwords or API tokens.

======================================================================
REPRODUCIBILITY
======================================================================

For every run record:

Git commit
dataset
dataset version
config hash
random seed
package versions
input hashes
output hashes
date/time

Use deterministic random seeds.

Never overwrite previous result directories.

Create run-specific subdirectories if necessary.

======================================================================
MANUAL VALIDATION GUIDE
======================================================================

Create:

docs/manual_validation_guide.md

For each major scientific claim tell me:

WHAT THE ANALYSIS CLAIMS

WHERE I CAN CHECK IT

EXACT QUERY OR PAGE

WHAT I SHOULD EXPECT TO SEE

WHAT WOULD INDICATE AN ERROR

Include checks for:

MaleCNS v1.0 dataset

LB3b body IDs

LB3c body IDs

LB3b/LB3c counts

Quasimodo identity

Clavicle identity

GNG015 identity

GNG021 identity

motor neuron identity

raw edge weights

left/right sides

neurotransmitter predictions

effective-connectivity equation

percentile thresholds

paper replication

sugar-specific path

GNG021 candidate branch

======================================================================
QUESTION-ANSWER TRACEABILITY
======================================================================

The project must be designed so that later, if I ask questions such as:

“Why did GNG021 appear?”

“Why didn't it pass the paper threshold?”

“Why is LB3c stronger than LB3b here?”

“Did the paper actually show this?”

“Which exact body IDs created this type-level result?”

“What changed between runs?”

you can answer from saved source records.

Do not answer those questions from memory.

Retrieve the relevant:

claim_id
query
raw result
paper source
analysis output
decision-log entry
mismatch entry

and cite them.

======================================================================
FINAL CROSS-EXPERIMENT TABLE
======================================================================

Create:

results/cross_experiment/comparison.csv

Columns:

node_or_edge

experiment_01_paper_replication

experiment_02_lb3b

experiment_02_lb3c

experiment_02_combined

experiment_03_lb3b

experiment_03_lb3c

experiment_03_combined

raw_synapse_weight

fraction_pre_output

fraction_post_input

effective_connectivity

percentile_rank

selected_by_algorithm

paper_support

left_right_consistency

interpretation

======================================================================
FINAL SCIENTIFIC QUESTIONS
======================================================================

At the end explicitly answer:

1. Did MaleCNS v1.0 reproduce the published LB3 circuit?

2. What differed?

3. When input is restricted to LB3b/LB3c, which paper-supported paths remain?

4. Is Quasimodo retained?

5. Is Clavicle retained?

6. Is GNG015 retained?

7. Does LB3b alone produce the pathway?

8. Does LB3c alone produce the pathway?

9. Is the combined result different?

10. Does LB3c truly dominate the complete Quasimodo→motor pathway, or only the first edge?

11. Does GNG021 naturally survive the exact paper-style filter?

12. If yes, how does GNG021 compare quantitatively with GNG015?

13. Is GNG021 a genuine parallel route to a different motor output?

14. Are the GNG015 and GNG021 branches:
    - parallel
    - convergent
    - divergent
    - partially overlapping

15. Which conclusions are:
    PAPER_REPLICATION

16. Which are:
    PAPER_DERIVED_EXTENSION

17. Which are:
    NOVEL_V1_STRUCTURAL_CANDIDATE

18. Which remain:
    UNRESOLVED

======================================================================
DO NOT RUN PHYSIOLOGICAL SIMULATION YET
======================================================================

Do not perform electrical stimulation modeling or leaky-integrate-and-fire simulation until:

- paper method is verified
- body IDs are validated
- raw connectivity agrees
- Experiment 01 is complete
- Experiment 02 is complete
- Experiment 03 is complete
- mismatch ledger has been reviewed

Instead create:

NEXT_STEP_SIMULATION_PLAN.md

Explain:

- what the paper simulated
- which neurons were stimulated
- which neurons were tonically driven
- what neurotransmitter signs were assumed
- what model parameters were used
- whether the exact model can be reproduced
- whether applying it to the sugar-restricted network is justified

======================================================================
STOP CONDITIONS
======================================================================

STOP rather than guessing if:

- paper cannot be retrieved
- critical supplement is missing
- body IDs cannot be resolved
- dataset version is ambiguous
- effective-connectivity formula is unclear
- source code contradicts Methods
- key raw edge values disagree without explanation
- motor-neuron mapping is uncertain
- a result depends on an undocumented assumption

When blocked, report exactly:

WHAT IS BLOCKED

WHY

WHAT SOURCE OR ACCESS IS REQUIRED

HOW I CAN PROVIDE IT

======================================================================
FIRST EXECUTION ORDER
======================================================================

Proceed in this order:

STAGE 1
Create isolated folder and Git repo.

STAGE 2
Fetch and read the complete paper and supplements.

STAGE 3
Find associated code and source-data files.

STAGE 4
Create paper_method_reconstruction.md.

STAGE 5
Create prompt_vs_paper_audit.md.

STAGE 6
Confirm male-cns:v1.0.

STAGE 7
Resolve body IDs.

STAGE 8
Validate raw LB3 / Quasimodo / Clavicle / GNG015 / GNG021 / motor records.

STAGE 9
Implement and test the paper's effective-connectivity method.

STAGE 10
Run Experiment 01.

STAGE 11
Run Experiment 02A, 02B, 02C.

STAGE 12
Run Experiment 03A, 03B, 03C.

STAGE 13
Create head-to-head GNG015 vs GNG021 comparison.

STAGE 14
Generate cross-experiment report.

STAGE 15
Generate the manual-validation guide.

STAGE 16
Generate NEXT_STEP_SIMULATION_PLAN.md.

======================================================================
REPORT PROGRESS AT CHECKPOINTS
======================================================================

At the end of each stage, update:

STATUS.md

Use this format:

COMPLETED

CURRENT FINDINGS

VERIFIED FACTS

UNVERIFIED ITEMS

MISMATCHES

NEW QUESTIONS

FILES CREATED

NEXT ACTION

Do not erase earlier entries.

Append them chronologically.

======================================================================
FINAL PRINCIPLE
======================================================================

Your purpose is not to prove our hypothesis.

Your purpose is to determine:

what the paper actually established,

what MaleCNS v1.0 actually contains,

which published results reproduce,

which sugar-specific results emerge when we change only the input population,

whether GNG021 survives the same scientific standard,

and exactly where the evidence becomes uncertain.

Every conclusion must remain traceable back to:

a paper passage,
a primary data query,
a body-level network record,
or a reproducible computation.

If that provenance does not exist, do not present the claim as established.

On session start, open status.md and unresolved_questions.md.

## Source and version

- Source/location: 
- Author/date: Rodela/Oct 6th, 2026
- Version: 0.1
- You are logged in as: rodela@proveai.com
- Authorization token: Auth Token: in .env file for this website: https://neuprint.janelia.org/account

