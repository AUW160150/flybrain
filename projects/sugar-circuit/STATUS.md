# Project status

## 2026-10-06 — Initial validation checkpoint

### COMPLETED

Read AGENTS.md then the full RESEARCH_PROTOCOL.md before scientific work; read all existing logs and scaffold documents. STATUS.md and ASSUMPTIONS.md did not exist at session start.

Initialized the dedicated Git repository in the existing workspace. Located final publication metadata; retrieved final supplemental PDF, Table S1, Figures 2/6; inspected relevant figures and all supplement legends. Completed a partial method reconstruction and assumption audit with explicit source gaps.

Verified authenticated male-cns:v1.0 metadata and resolved/cross-checked 95 target bodies against official flat files; corroborated all 87 sensory/motor IDs/types with Table S1. Created 33 claims and 229 permanent mismatch entries, source/query/run provenance and the checkpoint report. Earlier anonymous-access failures and the earlier flat-only result directory are preserved.

### CURRENT FINDINGS

The initial checkpoint is complete as an evidence/status report. The full scientific method validation has **not passed**. Stages 2–5 remain partial where they require full main Methods/code; stages 6–7 are verified for the requested populations. Raw-edge stage 8 and stages 9–16 were not executed. No experiments or simulations ran.

### VERIFIED FACTS

C001: final Cell publication. C006–C010: requested identities/counts/aliases and saved NT fields. C013–C022: selected facts from final figures/supplement. C029: active v1.0 release and UUID. C030: 1,615 exact cross-representation field matches and 190 explained precision differences.

### UNVERIFIED ITEMS

Full final Results/STAR Methods, exact effective-connectivity formula and normalization, bootstrap/pruning implementation, paper-specific code/version, paper's analysis snapshot, raw edge agreement and every proposed pathway outcome.

### MISMATCHES

M003: LB3c 957530 entry nerve missing in v1.0 versus Table S1. M010–M042: NT prediction/consensus distinctions. M100–M289: explained numerical precision differences. M001/M002/M004/M005/M006: schema, nomenclature, metadata-format and citation/documentation issues resolved or explicitly scoped.

### NEW QUESTIONS

See Q-003–Q-010 and Q-012 in logs/unresolved_questions.md. Authenticated access is resolved (Q-011). No author contact or external message was sent.

### FILES CREATED

[Checkpoint report](docs/initial_validation_checkpoint.md), SOURCES.md, ASSUMPTIONS.md, config/analysis.yaml, config/source_manifest.yaml, source and query logs, append-only run manifest, validation dependency pins and source/identity scripts. Updated method reconstruction, audit, discrepancy report, manual guide and README. Saved primary sources and raw v1.0 records.

Latest comparison directory: `results/validation/20261006T171922Z/`; prior result: `results/validation/20261006T171412Z/`.

### NEXT ACTION

Obtain the final main paper/STAR Methods and official analysis implementation/version, then finish source reconciliation. Provide a local final-PDF/HTML path or accessible primary-source link. Dataset authentication is working. Keep experiments and simulation unrun until a later request and resolution of the critical validation gaps.

## 2026-10-06T17:33:07.063829+00:00 — Artifact integrity check

Verified unique IDs and CSV structure for 33 claims and 229 mismatch records; all 12 source hashes and latest run input/output hashes match; local document links resolve. Credential scan found no token in project artifacts, and Git ignores the environment file. The temporary curl credential configuration was removed. No experiments or simulations were executed.

## 2026-10-06T18:58:31.925343+00:00 — Gates 2 and 3 completed; STOPPED at structural checkpoint

**Current state: STRUCTURAL CONNECTIVITY ONLY.** The user's later instruction superseded the initial checkpoint's restriction on structural work while retaining the unresolved paper-method gaps. Gate 1 identities were reused; authenticated release metadata was checked at run start/end and is unchanged.

Full released graph retained without an added synapse threshold. All 746,910 exported raw body-edge weights agree with authenticated neuPrint. Exact A–E membership/counts are complete within four-hop simple-path bounds, with full-graph reachability/shortest distances and declared example caps. All 770 sensory–motor pairs are reachable in 2–3 hops. GNG021 has no direct LB3 input, but all 154 LB3-candidate pairs have shortest length 2, and both candidate bodies reach every motor. B+C is the union of B/C; no combined-only path is claimed.

Created [structural checkpoint](docs/structural_connectivity_checkpoint.md), `results/structural/20261006T180116Z/`, raw complete Feather, exact query/response provenance, required CSVs, GraphML, comparisons, growth/recurrence/side tables, code and validation checks. Visualization view: 37,246 nodes/643,834 edges, including explicitly unannotated segments. Four behavior tests and artifact integrity checks pass.

New source issues: eight paper/current pooled discrepancies (M290–M297), unresolved Puddle mapping (M298), and 976 newly preserved NT field distinctions (M299–M1274). The latter are distinctions between supplied fields, not edge-source disagreements. Paper method/snapshot, anatomical crossing locations and physiological interpretation remain unresolved. Existing M003 entry-nerve gap persists.

**Next action: await a new user instruction.** Structural output is ready for side-by-side visualization with stated limitations. No polished figure, effective-connectivity calculation, statistical replication or simulation was produced. All three experiment configurations remain `execution_allowed: false`; the paper algorithm is not implemented. See the report's experiment-design clarifications.

### 2026-10-06T19:01:41.682099+00:00 — Structural artifact integrity

All 13 required outputs, 746,910 edge records, 33,851 complete shortest paths, capped path-example files and 37,246-node/643,834-edge GraphML pass integrity checks. Four synthetic behavior tests pass. Ledgers contain 55 unique claims and 1214 unique mismatch records. Local report links resolve. No credential occurs in project artifacts; the temporary auth config was removed and the original ignored environment file preserved. Run provenance is frozen in `results/structural/20261006T180116Z/manifest.json` and audit snapshots. Stop remains at structural Gates 2/3.

### 2026-10-06T19:04:21.454169+00:00 — Structural artifact integrity

All 13 required outputs, 746,910 edge records, 33,851 complete shortest paths, capped path-example files and 37,246-node/643,834-edge GraphML pass integrity checks. Four synthetic behavior tests pass. Ledgers contain 55 unique claims and 1214 unique mismatch records. Local report links resolve. No credential occurs in project artifacts; the temporary auth config was removed and the original ignored environment file preserved. Run provenance is frozen in `results/structural/20261006T180116Z/manifest.json` and audit snapshots. Stop remains at structural Gates 2/3.


## 2026-10-06T21:56:23.667556+00:00 — Method recovery audited; stopped before Experiment 1R

### COMPLETED

Read prompt_1.md and required project context; rechecked final paper/correction/code access, re-fetched unchanged final supplement/Table S1, and authenticated live v1.0 identity. Added a reproducible twelve-motif weight audit with exhaustive subset tests and six passing hand-calculated arithmetic tests. Parameter inventory, circuit-version readiness records, partial evidence matrix and checkpoint reports are saved.

### CURRENT FINDINGS

Four of twelve mapped raw figure totals match; eight differ. No discrepant label equals any subset of current mapped raw body-pair counts. Body/whole-edge deletion and additive pooling alone cannot explain them. All-body weightHP matches zero labels; weightHR matches the same four as raw. Causes remain unresolved.

### VERIFIED FACTS

Live male-cns:v1.0 UUID unchanged. GNG232/DNg67 occur in final S16A, DNg67/Fudog and DNge080/Rounddown in S19; these are scoped paper appearances, not evidence of full-circuit selection. C056–C063.

### UNVERIFIED ITEMS

Final full Methods, official implementation, selection-changing equations/threshold rules, snapshot, pooling, complete published reference and every method-selected/sugar circuit. No paper engine or effective mathematics tests were fabricated.

### MISMATCHES

M1275–M1282 add constraints to the unresolved M290–M297 weight differences; M1283 clarifies overlapping Tastekin/cross-literature panel evidence.

### NEW QUESTIONS

Q-017: full reference inventory/Tentacular mapping. Q-018: candidate panel presence versus actual selected circuit. Q-016 resolved to source-only input restriction.

### FILES CREATED

`results/method_recovery/20261006T214639Z/`, `docs/paper_vs_v1_weight_audit.md`, `docs/experiment_01_replication_checkpoint.md`, `docs/effective_connectivity_and_sugar_checkpoint.md`, scripts 16–18, `tests/test_weight_audit.py`, `config/method_readiness.json`, version registry and evidence matrix.

### NEXT ACTION

Obtain readable final Results/STAR Methods and publication-linked analysis/figure source data, resolve the parameter gaps, then implement/test one engine. **Experiment 1R NOT RUN; Experiment 2 NOT RUN; no simulation.** Dataset access is working; the blocker is scientific source completeness, not authorization.

### 2026-10-06T21:58:18.589516+00:00 — Method-audit integrity

Verified append-only ledger history, 63 unique claims and 1223 unique mismatch entries, local report links, seven new source hashes, empty unverified functional fields, and disabled experiment gates. Six arithmetic audit tests pass. Credential scan passed; temporary auth config removed. Audit frozen in `results/method_recovery/20261006T214639Z/manifest.json`; no paper-method freeze or biological experiment.


## 2026-10-06T22:09:36.363510+00:00 — Visualization framework checkpoint; STOPPED

### COMPLETED

Constructed `visualization/data`, `scripts`, `static`, `interactive`, `anatomy`, `graph`, and `docs`. Current build: `20261006T220705330361Z`. [Open explorer](visualization/interactive/index.html); [figure index](visualization/docs/VISUALIZATION_INDEX.md). SVG/PDF/320-DPI PNG, self-contained local HTML, directed GraphML/GEXF, provenance manifests and reusable selected-result adapter are present.

### CURRENT FINDINGS

Figure 1 is explicitly PAPER-ASSOCIATED with current raw weights and separate same/opposite-side sheets. Figure 2 has four unpopulated effective-selection panels. Figure 3 has six independent CANDIDATE comparisons. No raw path is represented as the final selected sugar pathway.

### VERIFIED FACTS

110 bodies, 1923 scoped raw edges and 274 mapped paper-associated edges exactly join to the frozen source; both graph formats preserve body IDs, sides and raw weights. All static PNGs are 320 DPI. Eight contract tests and 32 offline JS behavior checks pass. Original structural input hashes are unchanged. Claims: C064, C065, C066, C067, C068.

### UNVERIFIED ITEMS

Actual anatomy is BLOCKED: skeleton download failed due to DNS/network restrictions. Anatomical camera orientation remains unverified. The parser and native 3D renderer are implemented but authentic anatomical renders are not produced. Chrome launch failed, so no full-browser visual test is claimed. Puddle and effective-connectivity methodology remain unresolved.

### MISMATCHES

Existing eight paper/current pooled differences remain visible. M1284 records a resolved metadata-guard implementation expectation, not a dataset mismatch. No scientific raw result was changed.

### NEW QUESTIONS

Q-017 authoritative skeleton retrieval access; Q-018 native anatomical orientation evidence. These block anatomy, not the valid raw/paper-associated display derivatives.

### FILES CREATED

See [VISUALIZATION_INDEX](visualization/docs/VISUALIZATION_INDEX.md), [build instructions](visualization/README.md), [anatomy recovery](visualization/docs/ANATOMY.md), [selected-result contract](visualization/docs/SELECTED_RESULTS.md), and `visualization/data/20261006T220705330361Z/` for manifests and validation reports. Prior drafts remain preserved.

### NEXT ACTION

Stop at the user-requested visualization framework/current-view boundary. No experiments, effective-connectivity calculations, selection, Shiu simulations or physiological analysis ran. Skeleton retrieval may be retried in a network-enabled session; algorithm-selected panels must wait for independently validated results.


## 2026-10-06T22:13:56.977963+00:00 — Visualization framework checkpoint; STOPPED

### COMPLETED

Constructed `visualization/data`, `scripts`, `static`, `interactive`, `anatomy`, `graph`, and `docs`. Current build: `20261006T221324540396Z`. [Open explorer](visualization/interactive/index.html); [figure index](visualization/docs/VISUALIZATION_INDEX.md). SVG/PDF/320-DPI PNG, self-contained local HTML, directed GraphML/GEXF, provenance manifests and reusable selected-result adapter are present.

### CURRENT FINDINGS

Figure 1 is explicitly PAPER-ASSOCIATED with current raw weights and separate same/opposite-side sheets. Figure 2 has four unpopulated effective-selection panels. Figure 3 has six independent CANDIDATE comparisons. No raw path is represented as the final selected sugar pathway.

### VERIFIED FACTS

110 bodies, 1923 scoped raw edges and 274 mapped paper-associated edges exactly join to the frozen source; both graph formats preserve body IDs, sides and raw weights. All static PNGs are 320 DPI. Eight contract tests and 36 offline JS behavior checks pass. Original structural input hashes are unchanged. Claims: C069, C070, C071, C072, C073.

### UNVERIFIED ITEMS

Actual anatomy is BLOCKED: skeleton download failed due to DNS/network restrictions. Anatomical camera orientation remains unverified. The parser and native 3D renderer are implemented but authentic anatomical renders are not produced. Chrome launch failed, so no full-browser visual test is claimed. Puddle and effective-connectivity methodology remain unresolved.

### MISMATCHES

Existing eight paper/current pooled differences remain visible. M1285 records a resolved metadata-guard implementation expectation, not a dataset mismatch. No scientific raw result was changed.

### NEW QUESTIONS

Q-019 authoritative skeleton retrieval access; Q-020 native anatomical orientation evidence. These block anatomy, not the valid raw/paper-associated display derivatives.

### FILES CREATED

See [VISUALIZATION_INDEX](visualization/docs/VISUALIZATION_INDEX.md), [build instructions](visualization/README.md), [anatomy recovery](visualization/docs/ANATOMY.md), [selected-result contract](visualization/docs/SELECTED_RESULTS.md), and `visualization/data/20261006T221324540396Z/` for manifests and validation reports. Prior drafts remain preserved.

### NEXT ACTION

Stop at the user-requested visualization framework/current-view boundary. No experiments, effective-connectivity calculations, selection, Shiu simulations or physiological analysis ran. Skeleton retrieval may be retried in a network-enabled session; algorithm-selected panels must wait for independently validated results.

### 2026-10-06T22:14:56.853746+00:00 — Final visualization evidence reconciliation
Current build `20261006T221324540396Z` includes scoped supplementary P support for GNG232, Fudog and Rounddown from frozen C061. C071 supersedes earlier visualization C066; prior drafts are preserved as superseded. Figure 1 membership and all raw counts remain unchanged. The visualization decision/question IDs are D019 and Q-019/Q-020; the earlier duplicate IDs in the 22:09 visualization entry are historical. M1286. Eight Python tests and 36 offline JavaScript behavior checks pass; full Chrome rendering and authentic anatomy remain blocked as documented.


## 2026-10-06T22:16:22.713335+00:00 — Source-pack recovery and verified algebra core

Current status: **FINAL_METHOD_SECTIONS_RECOVERED_SELECTION_DETAILS_UNRESOLVED**. Earlier source-access statements above describe their dated checkpoints. The user source pack authorized indexed final text, which exposed the relevant Methods; the full preprint v2 XML was also recovered and compared. See [final/preprint audit](docs/final_vs_preprint_method_diff.md) and `results/method_recovery/20261006T220302Z/`.

The unsigned postsynaptic-normalized matrix core and explicit-reference threshold/pruning helpers are implemented. **27 tests pass: 21 new mathematical/helper tests plus six weight-audit tests.** Three synthetic comparisons establish that remaining reference-population, pooling and hop choices change candidate membership. These are not biological results.

Figure 6G graph eligibility/filter/denominator scope, score grouping/pooling, percentile reference populations/estimator and iterative hop/candidate policy still need primary definitions. Experiment 1R, all sugar conditions and simulation remain unrun. No method freeze, selected circuit or functional inference is claimed. The prior raw audit remains 4/12 exact and eight unexplained discrepancies. Live v1.0 UUID is unchanged. Claims C074–C085; mismatches M1287–M1289.

### 2026-10-06T22:17:20.683764+00:00 — Final visualization build integrity
Current immutable build: `20261006T221533490089Z`. This supersedes earlier display drafts and retains C071 supplementary-P reconciliation. Verified all 12 source input hashes, 15 implementation hashes and 30 output hashes. Eight Python tests and 36 offline JavaScript behavior checks pass; all source weights and directed graph roundtrips pass. M1290 resolves generated-shortcut provenance bookkeeping. Scientific results and disabled experiment gates are unchanged. Anatomy remains BLOCKED; no authentic morphology or full Chrome visual check is claimed. STOP at the visualization framework/current-view boundary.

### 2026-10-06T22:19:38.514929+00:00 — Source-pack audit integrity

Verified 27 tests from saved successful run,18 source hashes, 48 unique parameter records, append-only prior history, unique claim/mismatch IDs, current checkpoint links, current dataset identity and credential hygiene. All biological experiment gates remain disabled. Audit manifest: `results/method_recovery/20261006T220302Z/manifest.json`. Full method is not frozen. Concurrent visualization ledger entries were preserved; new method records used currently available IDs.

### 2026-10-07T22:00:46.456321+00:00 — Readable direct/indirect connection tables

Created [20261007T220046456321Z text summary](results/connection_tables/20261007T220046456321Z/connections_readable.txt) plus complete tracked-pair tables and broad four-hop union exports. Source hashes and route edges checked. Uses saved 6 October v1.0 data; no live refresh or paper-selection run. Claims C086–C088; D023.

### 2026-10-07T22:06:21.943039+00:00 — Excel export of broader structural network

Created [MaleCNS_LB3_Broader_Network.xlsx](results/excel/20261007T220621943039Z/MaleCNS_LB3_Broader_Network.xlsx): all 23,207 saved broad-network nodes/segments,354,639 edges and770 sensory-to-motor pairs, plus separate compact reference sheets. All data cells round-trip against their hashed CSV inputs; body IDs preserved as text, counts numeric, filters/frozen headers enabled. Uses the existing four-hop structural scope; no new analysis or biological selection.


## 2026-10-07T22:18:43.582985+00:00 — Sequential workflow source check and input preparation

Reverified live v1.0 identity, inspected additional official sources, and checked all four input sets (77/11/23/34 sensory bodies; 10 fixed motors). 27 existing tests pass; input hashes, 185 exported body rows, and the blocking execution gate verified. B01–B04 remain unresolved; no biological selection or method freeze. The generic package functions are not a verified Figure 6G implementation. See [workflow steps](docs/workflow_next_steps.txt), [unsent methods request](docs/tastekin_methods_request.txt), and [audit](results/workflow/20261007T221035718347Z/report.txt). Claims C089, C090, C091; decision D024.
