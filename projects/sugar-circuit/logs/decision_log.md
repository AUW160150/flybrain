# Decision log

Record decisions that affect interpretation, implementation, or experiment configuration. Link evidence and related claim or mismatch IDs.

| ID | Date | Decision | Rationale/evidence | Alternatives considered | Related IDs |
|---|---|---|---|---|---|


## Initial validation checkpoint — 6 October 2026

### D001 — Project location
- QUESTION: Where should the isolated project live?
- AVAILABLE EVIDENCE: The user created and is working in this workspace project; the protocol's earlier example used a home-directory path.
- OPTIONS: Move it; create another copy; preserve the existing project.
- DECISION: Use the existing workspace directory and initialize its own Git repository.
- WHY: It is the project the user explicitly asked to validate.
- ALTERNATIVES REJECTED: Relocation or a duplicate would divide the audit record.
- WHAT WOULD CHANGE THIS DECISION: An explicit relocation request.

### D002 — Ledger schema migration
- QUESTION: How to adopt the protocol columns without losing history?
- AVAILABLE EVIDENCE: Both scaffold ledgers contained headers only; no claim rows.
- OPTIONS: Overwrite; append incompatible columns; archive and create canonical ledgers.
- DECISION: Move original files intact to `logs/archive/*.scaffold`; create protocol schemas and append claims.
- WHY: The original artifacts remain preserved and every new row has the required provenance.
- ALTERNATIVES REJECTED: Deleting old files or mixing CSV schemas.
- WHAT WOULD CHANGE THIS DECISION: A ledger with existing claims would require a separately documented lossless migration.

### D003 — Inaccessible main paper
- QUESTION: Can method reconstruction be completed from indexed excerpts?
- AVAILABLE EVIDENCE: Final figures, supplement and Table S1 are accessible; main web/PDF requests returned 403 and full API returned 401.
- OPTIONS: Infer from excerpts; substitute the preprint; mark incomplete and validate independent sources.
- DECISION: Record only facts established by retrieved primary artifacts; block exact algorithm reconstruction. Complete the independently requested dataset and ID checks.
- WHY: User scope permits those checks, while the protocol forbids guessed methods.
- ALTERNATIVES REJECTED: Treating snippets or a prior version as final Methods.
- WHAT WOULD CHANGE THIS DECISION: A readable final paper/STAR Methods and official code.

### D004 — Dataset identity guard
- QUESTION: Which returned fields identify the active release?
- AVAILABLE EVIDENCE: Explicit request `dataset=male-cns:v1.0`; public inventory UUID; live Meta stores `dataset=male-cns`, `tag=v1.0`, matching UUID.
- OPTIONS: Test Meta.dataset alone; accept request string alone; verify family/tag/UUID together.
- DECISION: Verify all three; preserve the failed literal-name expectation in M004.
- WHY: The family field omits the version suffix.
- ALTERNATIVES REJECTED: Treating the family name as evidence of a different connectome.
- WHAT WOULD CHANGE THIS DECISION: A different tag/UUID or an explicitly documented release change.

### D005 — Identity inventory and sides
- QUESTION: How should bodies be selected at this checkpoint?
- AVAILABLE EVIDENCE: Exact v1.0 types; Table S1 target IDs; raw rootSide/somaSide and tracing status.
- OPTIONS: Exact type membership; prefix expansion; exclude lower tracing statuses.
- DECISION: Exact type membership, no invented status cutoff, integer IDs; preserve rootSide and somaSide separately. Motor comparisons explicitly compare side labels across different field names.
- WHY: This is an identity inventory, not a circuit-selection rule.
- ALTERNATIVES REJECTED: Pooling MN4a with MN4b, inferring missing nerves, or removing a paper-listed body without a verified method.
- WHAT WOULD CHANGE THIS DECISION: Explicit paper/code inclusion criteria or a corrected body mapping.

### D006 — NT prediction versus consensus
- QUESTION: Which field supplies a physiological sign?
- AVAILABLE EVIDENCE: 33 target records have differing body-prediction and consensus fields; all raw values/confidences retained.
- OPTIONS: Force agreement; choose a field silently; preserve both and defer sign policy.
- DECISION: Preserve body, cell-type, confidence, ground-truth and consensus fields. No signed model is defined.
- WHY: Different fields do not by themselves establish physiological action or an annotation error.
- ALTERNATIVES REJECTED: Converting a consensus label into a verified body-level prediction.
- WHAT WOULD CHANGE THIS DECISION: Verified paper/model rules and documented dataset consensus construction.

### D007 — Precision differences
- QUESTION: Are neuPrint confidence values inconsistent with the flat files?
- AVAILABLE EVIDENCE: 190 differing values match a float32 conversion within 1e-14; 1,615 other compared values are exact.
- OPTIONS: Hide rounding differences; call all mismatches; retain and explain them.
- DECISION: Keep both original values and signed differences; classify the 190 as EXPLAINED_DIFFERENCE, with individual mismatch rows.
- WHY: The numerical explanation is reproducible without assuming exact equality.
- ALTERNATIVES REJECTED: Rounding raw sources or using a broad biological tolerance.
- WHAT WOULD CHANGE THIS DECISION: Values outside the demonstrated float32 conversion behavior.

### D008 — Checkpoint scope and experiment gate
- QUESTION: How far should this session proceed?
- AVAILABLE EVIDENCE: User requested the initial checkpoint only and prohibited experiments; full method still unverified.
- OPTIONS: Start pathway calculations; implement guessed defaults; stop after source/identity validation and reporting.
- DECISION: No edge-weight hypothesis tests, effective-connectivity implementation, experiments, or simulations. Save raw queries, comparisons and report.
- WHY: These are the authorized checkpoint boundaries.
- ALTERNATIVES REJECTED: Treating successful access/ID checks as approval or evidence for circuit results.
- WHAT WOULD CHANGE THIS DECISION: A later user request after critical method sources and validation gaps are resolved.


### D009 — Authorized structural-only Gates 2 and 3
The latest user request authorizes unweighted directed graph extraction, raw synapse counts, bounded path search and structural comparisons. It explicitly permits these while exact paper methods remain unresolved, superseding D008 for this phase. Reuse the 95 validated identities; verify release metadata at run start. No effective connectivity, bootstrap, physiological model or experiment execution. Run: `results/structural/20261006T180116Z`.

### D010 — Full graph and search bounds
The complete official graph is retained: 88,384,522 segment endpoints, 151,856,684 edges, including weight-1 edges and unannotated segments. No synapse-count, type, status, side or ROI filter. Released minconf-0.5 preprocessing is source provenance. After depth-0–7 growth inspection, select uniform maximum 4 hops for exhaustive vertex-simple path counts/memberships (A–D and each E leg); retain depth-2/3 comparisons. A corridor expands from 23,960 nodes/358,931 edges at depth 4 to 89,113/4,490,174 at depth 5. Save at most 100 path examples per ordered body pair and hop count, in ascending-ID order; save up to 10,000 shortest paths per pair. Report exact totals, completeness and omissions; examples do not define circuit membership. Full-graph reachability/shortest distances have no hop cutoff. Evidence: `results/structural/20261006T180116Z/graph_growth_by_depth.csv`, `search_config.json`. These are analysis choices, not paper methods.

### D011 — Vertex-simple paths and nonabsorbing endpoints
Routes use directed individual-body edges; a vertex cannot repeat within a path. Source sets change independently in A–D, but other sensory bodies and motor bodies may occur internally. No class is silently removed and motors are not made absorbing. Cycles are assessed separately via SCCs and reciprocal/self-loop context; a cycle in a path-union graph may be longer than its constituent bounded paths. C048/C055; `results/structural/20261006T180116Z/search_config.json`, `motor_origin_edges_in_circuit_A.csv`. A future absorbing-motor or class-restricted analysis would be a separate derivative.

### D012 — Laterality and display classification
Use original somaSide/rootSide fields, preserving their provenance and missing values. Opposite-side endpoints do not locate a crossing synapse or identify the crossing neurite. Display classification groups supplied superclass annotations; unknown and tentative annotations remain explicit. Preserve predicted NT, confidence, consensus and ground-truth fields without physiological sign assignment. C049/C050; nodes.csv and raw_edges.csv.

### D013 — Raw-query views and recurrence context
Keep the complete released Feather unchanged. Export all targeted query edges plus exact bounded path membership and reciprocal/self-loop context. Context edges carry separate membership flags; a raw CSV slice is not presented as the complete 151-million-edge release. Every exported edge is checked against authenticated neuPrint. Exact retained/outside-view counts are in `results/structural/20261006T180116Z/export_summary.json`. C035/C036/C052.

### D014 — Named paper views after unrestricted search
Named motifs are inspected after A–E extraction and do not control the intermediate universe. Preserve 3,564 sensory-inclusive mapped paper-associated routes in a separate view and 3,264 candidate-overlap routes as non-paper claims. Puddle remains unmapped; graph resemblance is not identity evidence. Eight figure/raw pooled discrepancies are retained without guessing their cause. C037–C040/C046/C054.

### D015 — Completion and stop boundary
All exported edge, path, GraphML and source-set union checks pass. The exact paper method remains unresolved and is not implemented. Keep all three experiment configs execution-disabled. Structural results clarify source-only restriction, broad recurrence and GNG021 overlap; they do not authorize effective connectivity, statistical replication or simulation. Stop after the requested Gates 2 and 3. C051/C053.


## 2026-10-06T21:56:23.667556+00:00 — Method recovery and weight audit

### D016 — New authorization and scientific gate
- QUESTION: Does the new prompt permit continuation beyond the structural checkpoint?
- EVIDENCE: User explicitly requested prompt_1.md; its sections 4/7/12 require source recovery and mathematical validation before replication/extension.
- OPTIONS: Implement inferred equations; recover sources; stop the dependent stage if sources remain missing.
- DECISION: Authorization for the proposed experiments is present, superseding the prior session stop; the scientific method gate remains mandatory and currently fails.
- WHY: Missing definitions materially affect node selection. No approval question is needed to implement a verified method later.
- ALTERNATIVES REJECTED: Treating snippets, generic libraries or shortest paths as a validated algorithm.
- CHANGE CONDITION: Readable final Methods and sufficient code/source-data definitions, followed by passing mathematics tests.

### D017 — Bounded weight-explanation test
- QUESTION: Can selecting current bodies/edges alone explain the figure discrepancies?
- EVIDENCE: Twelve mapped figure labels and complete previously validated body-pair weights; input hashes match the frozen structural manifest.
- OPTIONS: Fit a subset; enumerate all attainable sums without selecting a circuit; assume version changes.
- DECISION: Enumerate all sums and body subsets only to exclude arithmetic explanations; do not adopt a best match.
- WHY: All eight mismatches are impossible under simple unchanged-edge deletion/addition. This narrows causes without choosing an unknown method.
- ALTERNATIVES REJECTED: Blaming proofreading or changing raw data without historical evidence.
- CHANGE CONDITION: Recovered paper data establish another mapping, filtering or pooling rule.

### D018 — Separate versions and paper evidence scopes
- QUESTION: How to represent unrun experiments and overlapping literature evidence?
- EVIDENCE: S16A/S19 include cross-literature candidate names, but no complete selected-node list is recovered.
- OPTIONS: Empty selected graphs interpreted as absent; explicit readiness definitions and panel-specific reference support.
- DECISION: Use NOT_RUN/NOT_ASSESSED and partial-reference labels, with blank effective/dynamic values. Keep seven versions separate.
- WHY: Missing evidence is not failed selection. Q-016 is resolved to source-only restriction by the new user prompt.
- ALTERNATIVES REJECTED: Calling every S16A label selected or giving unknown Puddle an inferred body ID.
- CHANGE CONDITION: Verified source tables and successful experiment execution.


### D016 — Visualization framework only (2026-10-06T22:09:36.363510+00:00)
- QUESTION: How to display the verified structure without claiming a selected sugar circuit?
- AVAILABLE EVIDENCE: Initial/structural checkpoints, all current logs, frozen raw tables and mapped paper routes; explicit user visualization request.
- OPTIONS: Show the large raw export; infer a selected sugar circuit; create small explicitly labeled derivatives and pending selection panels.
- DECISION: Use 110 verified requested bodies. Paper mode uses only the 274 saved mapped-route edges. Split same/opposite endpoint-side sheets; preserve all body IDs. Independent candidate cards carry source-backed P/R badges. Unknown order stays gray. Puddle stays unresolved. No E/D/X badge without corresponding evidence. Raw and effective weights are separate fields.
- WHY: Structural presence and paper association do not establish algorithm selection or physiological action. No entire dense path union is drawn.
- ALTERNATIVES REJECTED: Forced candidate membership, anatomy inferred from topology, signs assigned from NT predictions, and anatomical crossings inferred from soma sides.
- WHAT WOULD CHANGE THIS DECISION: Independently validated, hashed Tastekin results or new body-mapped evidence; see visualization/docs/SELECTED_RESULTS.md.
- IMPLEMENTATION / VALIDATION: Build `20261006T220705330361Z`; directed GraphML/GEXF roundtrips, exact source joins, 320-DPI checks, eight Python contract tests and 32 offline JavaScript behavior checks. Chrome could not launch (exit 134), so full browser visual verification is not claimed. Static images were visually inspected; arrow routing was revised to avoid passing behind unrelated nodes. Earlier drafts are retained and marked superseded in visualization/data/build_history.json.
- ANATOMY: Official per-body downloads failed with curl DNS code 6; automatic approval rejected sandbox escalation. Stop retrieval after transport failure. Store explicit BLOCKED status, actual SWC parser/renderer and retry instructions. Camera handedness requires an authoritative orientation source before named anatomical views are enabled. No synthetic morphology.
- RELATED: C064, C065, C066, C067, C068; M1284.


### D019 — Visualization framework only (2026-10-06T22:13:56.977963+00:00)
- QUESTION: How to display the verified structure without claiming a selected sugar circuit?
- AVAILABLE EVIDENCE: Initial/structural checkpoints, all current logs, frozen raw tables and mapped paper routes; explicit user visualization request.
- OPTIONS: Show the large raw export; infer a selected sugar circuit; create small explicitly labeled derivatives and pending selection panels.
- DECISION: Use 110 verified requested bodies. Paper mode uses only the 274 saved mapped-route edges. Split same/opposite endpoint-side sheets; preserve all body IDs. Independent candidate cards carry source-backed P/R badges. Unknown order stays gray. Puddle stays unresolved. No E/D/X badge without corresponding evidence. Raw and effective weights are separate fields.
- WHY: Structural presence and paper association do not establish algorithm selection or physiological action. No entire dense path union is drawn.
- ALTERNATIVES REJECTED: Forced candidate membership, anatomy inferred from topology, signs assigned from NT predictions, and anatomical crossings inferred from soma sides.
- WHAT WOULD CHANGE THIS DECISION: Independently validated, hashed Tastekin results or new body-mapped evidence; see visualization/docs/SELECTED_RESULTS.md.
- IMPLEMENTATION / VALIDATION: Build `20261006T221324540396Z`; directed GraphML/GEXF roundtrips, exact source joins, 320-DPI checks, eight Python contract tests and 36 offline JavaScript behavior checks. Chrome could not launch (exit 134), so full browser visual verification is not claimed. Static images were visually inspected; arrow routing was revised to avoid passing behind unrelated nodes. Earlier drafts are retained and marked superseded in visualization/data/build_history.json.
- ANATOMY: Official per-body downloads failed with curl DNS code 6; automatic approval rejected sandbox escalation. Stop retrieval after transport failure. Store explicit BLOCKED status, actual SWC parser/renderer and retry instructions. Camera handedness requires an authoritative orientation source before named anatomical views are enabled. No synthetic morphology.
- RELATED: C069, C070, C071, C072, C073; M1285.


### 2026-10-06T22:14:56.853746+00:00 — Audit reconciliation (M1286)
The visualization-only D016 entry timestamped 2026-10-06T22:09:36 is a historical duplicate identifier and is superseded by **D019**. The earlier METHOD_RECOVERY_AUDIT D016/D017/D018 remain unchanged. C071 supersedes the visualization paper-support omission in C066 using frozen C061 evidence. Current candidate P badges for GNG232/Fudog/Rounddown mean S16A/S19 label support only, never selected Figure 6 membership.


## 2026-10-06T22:16:22.713335+00:00 — Source-pack continuation

### D020 — Indexed final Methods and preprint comparison
The user explicitly supplied a pack permitting indexed final text. Independently recovered contiguous method sections outrank the preprint; verified v2 XML is a cross-check. Preprint-only details remain provisional. Final Clavicle specificity resolves the broader preprint annotation without inventing identity mappings. Earlier source failures remain in history.

### D021 — Implement verified mathematics without inventing a selector
Implement one body-level unsigned algebra core plus explicitly parameterized normalization/threshold/pruning helpers. Synthetic tests cover required mathematics and show that unresolved grouping/reference/horizon choices materially change membership. Linear quantiles in toys are an explicit test choice, not an attributed paper setting. No signed motif selector, bootstrap CI policy or iterative biological selector is asserted implemented.

### D022 — Scientific stop, not an authorization request
User authorization to run experiments persists. The prompt and AGENTS stop condition applies because B01–B04 are still unresolved and materially affect selection. Keep the experiments gated; the minimal missing source is Figure6G/S16 generating code/config plus graph-definition and pooling details. A full paper PDF is no longer the only way forward. Do not reuse simulation filters, tune toward named cells, or freeze the partial core as the published algorithm.


### D023 — Readable structural connection tables (2026-10-07T22:00:46.456321+00:00)
User requested a text/table of direct and indirect connections. Reuse hashed, dataset-verified saved records. Cover all ordered distinct pairs among the existing 110 tracked bodies; indirect routes are 2–4-hop simple paths with explicit body-resolved witnesses, including alternatives when a direct edge also exists. Export the complete broad four-hop LB3-to-motor node/edge union and existing exact endpoint path counts. Do not imply all-brain all-pairs completeness, combine incompatible type-level edges, impose a new biological strength threshold, or call structural routes effective selection. Output: `results/connection_tables/20261007T220046456321Z`. Claims C086–C088.


### D024 — Sequential preparation while source gaps remain (2026-10-07T22:18:43.582985+00:00)
The user authorized proceeding step by step. Reverified the active dataset, checked additional primary/public code sources, and prepared exact source/target lists plus an unsent lead-contact request. Do not adopt generic coconatfly/malecns defaults as the historical Figure 6G settings. B01–B04 still materially affect selection, so preserve all disabled execution gates. Resume the same engine after source resolution, then Experiment 1R, its checkpoint/freeze, and the three sugar conditions. No new biological experiment or simulation. Audit: `results/workflow/20261007T221035718347Z`. Claims: C089, C090, C091.
