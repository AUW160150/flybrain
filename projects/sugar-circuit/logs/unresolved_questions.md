# Unresolved questions

Track missing information that blocks or could change the reconstruction or experiments.

| ID | Question | Why it matters | Evidence checked | Owner | Status/next step |
|---|---|---|---|---|---|
| Q-001 | Where is the exact full master prompt for `docs/RESEARCH_PROTOCOL.md`? | It is required to populate the protocol faithfully. | Workspace and conversation context available at scaffold creation. |  | Open |
| Q-002 | What is the source paper and its supplement? | Required to reconstruct and audit the method. |  |  | Open |

## Checkpoint update — 6 October 2026

Earlier rows above are retained as history.

| ID | Question | Why it matters | Current evidence | What is missing | What would resolve it | Status |
|---|---|---|---|---|---|---|
| Q-001 | Where is the full master prompt? | Governs the work | User-supplied protocol v0.1 is now present and was read in full | Nothing for this checkpoint | Completed | RESOLVED |
| Q-002 | What is the source paper and supplement? | Identifies primary evidence | Final DOI/citation, final 28-page supplement and Table S1 obtained | Main text remains unavailable; tracked separately | Citation/supplement identification completed | RESOLVED for identity/supplement; see Q-003 |
| Q-003 | Can the complete final paper and STAR Methods be read? | Exact algorithm reconstruction must use final sources | Main publisher routes 403; FULL API 401; metadata-only basic API | Final main Results/Methods and any additional source-data files | Provide a local legally obtained final PDF/HTML path or accessible author/publisher link | BLOCKED — SOURCE REQUIRED |
| Q-004 | Where is the paper's effective-connectivity implementation and used commit? | Needed to resolve formula, bootstrap, pruning and text/code discrepancies | Public lab/author inventories searched; no identified paper-specific code | Official repo/archive/version | Supply official link or author-provided code; no contact sent | BLOCKED — SOURCE REQUIRED |
| Q-005 | Which MaleCNS snapshot did the paper analyze? | Controls interpretation of replication | Table S1 says maleCNS; target bodies match v1.0 | Explicit dataset snapshot/date/version in Methods/code | Read final Methods/data provenance or obtain author clarification | UNVERIFIED |
| Q-006 | Why is entryNerve missing for LB3c body 957530? | Nerve-based filtering could discard a paper-listed body | Table S1 I250 says MxLbN; neuPrint/flat annotation missing | Explanation/corrected source annotation | Inspect tracing/official curator record; preserve both values meanwhile | SOURCE CONFLICT |
| Q-007 | How should body NT predictions and consensus be interpreted? | Affects future sign assignment | 22 unclear and 11 differing named body predictions; raw fields retained | Paper/model sign policy and dataset consensus construction | Verify primary methods and code before signed analysis | OPEN |
| Q-008 | Are raw body-edge weights consistent across neuPrint and flat connectivity? | Protocol requires agreement before pathway claims | Access and IDs verified; connectivity comparison not performed | Saved edge queries, official weights and matching filters | Future raw-connectivity validation after method/source review | NOT ASSESSED IN THIS CHECKPOINT |
| Q-009 | Does GNG021 appear in the complete paper graph/code? | Distinguishes a new candidate from a reported node | No name match in extracted supplement; relevant named panels inspected; some nodes unlabeled | Full main text and graph/node source data | Check full text/code without inferring absence from unnamed nodes | UNCLEAR |
| Q-010 | Does LB3c dominate the complete Quasimodo pathway? | H1 concerns full pathways, not just initial connections | S16A shows a qualitative first-edge difference; no new path results | Validated algorithm and later authorized experiment results | Run the specified comparisons only after validation | NOT TESTED |
| Q-011 | Is authenticated neuPrint access available? | Needed for independent raw checks | User supplied token locally; Meta and 95 neuron queries returned HTTP 200 | Nothing for present ID check | Completed; failed anonymous responses retained | RESOLVED |
| Q-012 | Are undocumented implementation choices still required? | Prevents false strict-replication claims | Exact formula, normalization, inclusion filters, bootstrap parameters and later pruning unverified | Final Methods and paper-linked implementation | Reconcile sources and log decisions before implementation | BLOCKED — SOURCE REQUIRED |

Remaining uncertainty: I am uncertain about the exact effective-connectivity and pruning procedure because the final STAR Methods and paper-specific implementation are not available. I am uncertain about the paper's dataset snapshot because the retrieved artifacts identify MaleCNS without establishing the release used for its calculations.

## Structural checkpoint update — 2026-10-06T18:58:31.925343+00:00

Earlier statuses are retained as history. This update concerns Gates 2/3 only; [checkpoint](../docs/structural_connectivity_checkpoint.md).

| ID | Updated finding / question | Evidence | Status / resolution required |
|---|---|---|---|
| Q-008 | All 746,910 exported body pairs and complete targeted boundary queries agree between neuPrint and flat weights; the remaining full graph was not exhaustively re-downloaded through the API | `results/structural/20261006T180116Z/edge_source_comparison.csv`, `path_edge_source_comparison.csv` | RESOLVED for extracted structural data; zero disagreements |
| Q-005 | Eight mapped figure totals differ from current pooled raw counts | `paper_motif_comparison.csv`; M290–M297 | UNVERIFIED paper snapshot/pooling; obtain source data/Methods before strict replication |
| Q-007 | NT distinction extends to 1,009 exported bodies, 976 newly logged | `nt_field_distinctions.csv`; M299–M1274 | Interpretation/sign policy OPEN; field preservation complete; no physiological sign assigned |
| Q-009 | GNG021 has indirect LB3 routes, motor reach and direct overlap with Quasimodo/GNG015 | C044–C047; raw named matrix | Structural candidate VERIFIED within scope; paper selection/membership still UNVERIFIED |
| Q-010 | Raw path counts do not test functional or effective whole-path dominance | C041–C043; no paper algorithm implemented | NOT TESTED; no H1 conclusion |
| Q-013 | Which MaleCNS bodies/type are Puddle? | Zero live alias matches and zero matches in six flat fields; Figure 6 names Puddle | BLOCKED — SOURCE REQUIRED; authoritative paper source-data or curator mapping |
| Q-014 | Which neurite/synapse crosses the anatomical midline? | Body-side labels and opposite-side edges retained | UNVERIFIED; morphology or synapse-position evidence needed |
| Q-015 | How should motor-origin raw edges, weak edges and unannotated segments be interpreted biologically? | 997 motor-origin A edges; 14,392 unannotated visualization nodes | UNVERIFIED physiology/presynaptic placement; inspect raw anatomy before functional claims |
| Q-016 | Does a later sugar restriction select starting inputs only or also remove other sensory intermediates? | B/C source-only graphs each include all 77 LB3 bodies as vertices | Design definition required before experiment 2; current structural definition is explicit |

Q-003/Q-004/Q-012 remain BLOCKED — SOURCE REQUIRED for the full paper/implementation and exact equation, normalization, bootstrap, pruning and simulation algorithm. They did not block the user-authorized structural phase. Q-006 (957530 entry nerve) is unchanged. No experiments or physiological simulations ran.


## 2026-10-06T21:56:23.667556+00:00 — Method gate recheck

| ID | Current evidence and missing source | Status |
| --- | --- | --- |
| Q-003 | Final publisher HTML/PDF still 403; FULL API 401; author-linked final PDF 403. Supplement and Table S1 re-fetched unchanged. Need readable final Results/STAR Methods. | BLOCKED — SOURCE REQUIRED |
| Q-004 | Public lab/author repository lists rechecked; no identified paper-specific analysis repository. Need official analysis scripts/version or fully explicit primary rules. | BLOCKED — SOURCE REQUIRED |
| Q-005 | All eight mismatches cannot arise solely from current raw body/edge subsets. Need historical adjacency, selected bodies and figure-generation pooling. | UNRESOLVED; no cause assigned |
| Q-012 | Parameter-by-parameter gaps saved in method_parameters.csv; no reconstructed mathematical assumptions adopted. | BLOCKED — SOURCE REQUIRED |
| Q-013 | Puddle still unmapped. No graph-based identity assigned. | BLOCKED — SOURCE REQUIRED |
| Q-016 | prompt_1.md explicitly defines starting-input-only restriction; config updated accordingly. | RESOLVED |
| Q-017 | Full Figure 6G selected body/node/edge inventory, including Tentacular and unnamed nodes, not recovered. A partial named reference cannot support complete precision/recall. Need figure source tables/code. | OPEN |
| Q-018 | S16A/S19 contain GNG232/DNg67/DNge080 labels; panel presence and selected-circuit membership must remain distinct. Need full selection output to determine overlap. | OPEN; panel presence verified |

I am uncertain about the effective-connectivity and pruning equations because the complete final Methods and publication-specific implementation are unavailable. I am uncertain about the historical weight differences because arithmetic exclusions do not identify the paper snapshot, synapse filter, or pooling rule.


## Visualization checkpoint — 2026-10-06T22:09:36.363510+00:00

| ID | Question | Evidence / why it matters | Required resolution | Status |
|---|---|---|---|---|
| Q-017 | Can authentic allowlisted v1.0 SWCs be downloaded? | Official per-body request failed with curl DNS code 6; elevated download rejected by disabled sandbox escalation. Zero SWCs rendered. | Run the documented public/neuPrint retrieval in a network-enabled session; preserve response hashes and original geometry. | BLOCKED — ACCESS REQUIRED |
| Q-018 | What authoritative axis-sign mapping establishes anterior/posterior/dorsal/lateral cameras in native MaleCNS EM coordinates? | Official source establishes 8-nm units; complete anatomical handedness was not verified here. | Supply verified orthonormal raw-to-right/dorsal/anterior matrix and primary source; see visualization/anatomy/orientation.json. | UNVERIFIED — SOURCE REQUIRED |

Q-003/Q-004/Q-012 remain blocked for effective-connectivity methodology. Q-013 Puddle remains unresolved. Q-014 crossing locations are not inferred from diagrams. No selection, Shiu dynamics, experimental validation or physiological simulation was performed by this visualization task.


## Visualization checkpoint — 2026-10-06T22:13:56.977963+00:00

| ID | Question | Evidence / why it matters | Required resolution | Status |
|---|---|---|---|---|
| Q-019 | Can authentic allowlisted v1.0 SWCs be downloaded? | Official per-body request failed with curl DNS code 6; elevated download rejected by disabled sandbox escalation. Zero SWCs rendered. | Run the documented public/neuPrint retrieval in a network-enabled session; preserve response hashes and original geometry. | BLOCKED — ACCESS REQUIRED |
| Q-020 | What authoritative axis-sign mapping establishes anterior/posterior/dorsal/lateral cameras in native MaleCNS EM coordinates? | Official source establishes 8-nm units; complete anatomical handedness was not verified here. | Supply verified orthonormal raw-to-right/dorsal/anterior matrix and primary source; see visualization/anatomy/orientation.json. | UNVERIFIED — SOURCE REQUIRED |

Q-003/Q-004/Q-012 remain blocked for effective-connectivity methodology. Q-013 Puddle remains unresolved. Q-014 crossing locations are not inferred from diagrams. No selection, Shiu dynamics, experimental validation or physiological simulation was performed by this visualization task.


### 2026-10-06T22:14:56.853746+00:00 — Identifier reconciliation
The visualization rows labeled Q-017/Q-018 at 22:09:36 were duplicate identifiers; they are superseded by **Q-019** (skeleton access) and **Q-020** (camera orientation). Original method-audit Q-017 (reference inventory) and Q-018 (panel versus selected membership) retain their meanings. See M1286.


## 2026-10-06T22:16:22.713335+00:00 — Current status supersedes earlier source-gap summaries

| ID | Updated evidence | Current state |
| --- | --- | --- |
| Q-003 | Relevant final Results/Methods recovered through index; full preprint v2 XML retrieved | PARTIALLY RESOLVED; complete final PDF unavailable, no longer the blanket blocker |
| Q-004 | Cited Stuerner repository inspected at pinned commit; not Tastekin selection code | Open; Figure6G/S16 function/config is the smallest useful source |
| Q-012 | Core equation, unsigned metric, both80 thresholds and bootstrap constants recovered | Partially resolved; B01–B04 in method_readiness.json remain selection-critical |
| Q-005 | Historical snapshot and figure pooling still unknown; prior subset audit unchanged | UNRESOLVED; eight raw differences |
| Q-013/Q-017 | Puddle/Tentacular and full published selected-node/edge table remain missing | UNRESOLVED; complete precision/recall unavailable |
| Q-021 | Indexed motif text reports48% and16/31 (51.6%) | SOURCE CONFLICT; verify source counts before enrichment replication |

I am uncertain about circuit membership because the percentile comparison populations, pooling order, graph/denominator universe and iterative hop policy remain unspecified. Three synthetic examples demonstrate the effect; this is not evidence that any particular biological neuron passes or fails. Bootstrap CI estimator/seed/initial sampling policy are separate remaining control-analysis gaps.


## 2026-10-07T22:18:43.582985+00:00 — Sequential workflow follow-up
Q-004/Q-012 and B01–B04 remain open after bounded author/lab and pinned official-software checks. The final Resource availability supplies the lead-contact route; `docs/tastekin_methods_request.txt` is prepared but unsent. The exact four condition lists are prepared independently of the missing graph/pooling/percentile/iteration policies. A request response or the generating script/configuration remains the actionable dependency. No new mismatch was identified.
