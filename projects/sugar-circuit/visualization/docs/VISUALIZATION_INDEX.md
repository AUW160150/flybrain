# Visualization index

Current immutable build: `20261006T221533490089Z`. Dataset: `male-cns:v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`.

[Open local circuit explorer](../interactive/20261006T221533490089Z/index.html) · [Anatomy viewer/status](../anatomy/20261006T221533490089Z/index.html) · [Build manifest](../data/20261006T221533490089Z/build_manifest.json)

Every view carries one explicit scientific label. Figure 1 is PAPER-ASSOCIATED and uses current raw weights; it is not a strict computational replication. Figure 2 is a status/framework view until independently validated results are supplied. Figure 3 is CANDIDATE and does not join the candidates into one pathway.

**Puddle remains UNRESOLVED.** Eight paper/current pooled discrepancies are retained. The original checkpoint and scientific results are unchanged. No effective-connectivity analysis, selection, experiment or simulation was run.

**Anatomy: BLOCKED.** 0 of 110 requested bodies have actual SWCs in this build. No geometry is fabricated. Anatomical camera orientation is UNVERIFIED. See [anatomy retrieval/recovery](ANATOMY.md).

## Shared encoding and provenance

| Biological role | Fill |
|---|---|
| LB3b | `#56B4E9` |
| LB3c | `#009E73` |
| sensory | `#999999` |
| second order | `#E69F00` |
| higher order | `#CC79A7` |
| premotor | `#0072B2` |
| motor | `#D55E00` |
| unknown | `#BDBDBD` |

Roles for the mapped named circuit describe the Figure 6 motif layers (C037–C040); they are not a general biological-order classifier. Unverified order is gray. Candidate status uses an outline and evidence badges, never a special fill.

P = paper-selected/support; here P means support in the inspected paper-associated panels, not selection by a rerun algorithm. R = raw MaleCNS structure. E = validated effective selection. D = dynamic/Shiu evidence. X = body-mapped experimental evidence. Multiple badges are supported. No E/D/X is populated in the current build. Shiu synonyms alone are not dynamic evidence.

Arrows indicate directed body-to-body records, with no inhibitory/excitatory sign. Every raw graph width uses `0.7 + 4.3 * sqrt(raw_synapse_count / visible_max)`; per-panel normalization is disclosed. Future score mode uses the separate score field with the same display transformation and never falls back to raw count. Reciprocal/recurrent edges curve. Skeleton cable segments are morphological geometry, not connectivity edges, and therefore have no directional arrowheads.

**PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION.** Body predictions, confidence and consensus remain separate. Raw incoming/outgoing summaries explicitly describe the frozen export or small explorer universe, not undocumented whole-connectome totals.

Source identity and side fields come from the frozen structural run. LEFT/RIGHT indicate rootSide for sensory bodies and supplied somaSide where available. Opposite-side endpoints do not identify a crossing neurite or synapse. No anatomical midline crossing is claimed.

Frozen source run: `results/structural/20261006T180116Z`. Input and output hashes, package versions, dataset guard and reproducibility metadata: [build manifest](../data/20261006T221533490089Z/build_manifest.json).

## Figure catalog

### figure1_paper_same_side

* Scientific label / raw versus selected: **PAPER-ASSOCIATED**
* Scientific question: Which verified current v1.0 bodies instantiate the mapped Figure 6 motifs?
* Node inclusion rule: All 77 LB3 inputs, 15 verified named counterpart bodies and 10 motors. Sensory display cards group subtype+side, with all member IDs retained.
* Edge inclusion rule: Union of frozen paper_associated_paths.csv edges; split by same/opposite endpoint side; sum only sensory-card outgoing counts.
* Source files: nodes.csv; raw_edges.csv; paper_associated_paths.csv; paper_motif_comparison.csv (relative CSV names resolve in the frozen source run).
* Dataset: `male-cns:v1.0`; no cross-dataset substitution.
* Layout: Layered sensory → second-order → higher-order / premotor → body-level motors; left/right columns.
* Color mapping: shared role palette above; candidate outlines/badges remain separate.
* Edge-width transformation: 0.7 + 4.3*sqrt(raw_count/panel_max); sensory counts are explicit sums
* Display filters: same_side; no weight threshold; no guessed Puddle edges; MN6 retained as an unconnected target in this motif subset
* Known limitations: Not strict replication; eight source discrepancies; sensory aggregation; diagram layers follow paper motifs, not general functional classification; all body pairs available in graph/HTML.
* Files: [figure1_paper_same_side.svg](../static/20261006T221533490089Z/figure1_paper_same_side.svg), [figure1_paper_same_side.pdf](../static/20261006T221533490089Z/figure1_paper_same_side.pdf), [figure1_paper_same_side.png](../static/20261006T221533490089Z/figure1_paper_same_side.png)

### figure1_paper_opposite_side

* Scientific label / raw versus selected: **PAPER-ASSOCIATED**
* Scientific question: Which verified current v1.0 bodies instantiate the mapped Figure 6 motifs?
* Node inclusion rule: All 77 LB3 inputs, 15 verified named counterpart bodies and 10 motors. Sensory display cards group subtype+side, with all member IDs retained.
* Edge inclusion rule: Union of frozen paper_associated_paths.csv edges; split by same/opposite endpoint side; sum only sensory-card outgoing counts.
* Source files: nodes.csv; raw_edges.csv; paper_associated_paths.csv; paper_motif_comparison.csv (relative CSV names resolve in the frozen source run).
* Dataset: `male-cns:v1.0`; no cross-dataset substitution.
* Layout: Layered sensory → second-order → higher-order / premotor → body-level motors; left/right columns.
* Color mapping: shared role palette above; candidate outlines/badges remain separate.
* Edge-width transformation: 0.7 + 4.3*sqrt(raw_count/panel_max); sensory counts are explicit sums
* Display filters: opposite_side; no weight threshold; no guessed Puddle edges; MN6 retained as an unconnected target in this motif subset
* Known limitations: Not strict replication; eight source discrepancies; sensory aggregation; diagram layers follow paper motifs, not general functional classification; all body pairs available in graph/HTML.
* Files: [figure1_paper_opposite_side.svg](../static/20261006T221533490089Z/figure1_paper_opposite_side.svg), [figure1_paper_opposite_side.pdf](../static/20261006T221533490089Z/figure1_paper_opposite_side.pdf), [figure1_paper_opposite_side.png](../static/20261006T221533490089Z/figure1_paper_opposite_side.png)

### figure2_sugar_panels

* Scientific label / raw versus selected: **SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY**
* Scientific question: Which bodies and edges are retained independently for LB3b, LB3c and combined inputs?
* Node inclusion rule: Only explicitly listed membership from validated selected-result contract; currently none.
* Edge inclusion rule: Only validated selected-result edges with separately preserved raw counts and effective scores; currently none.
* Source files: selected_results contract; currently absent (relative CSV names resolve in the frozen source run).
* Dataset: `male-cns:v1.0`; no cross-dataset substitution.
* Layout: Four switchable HTML panels; matching four-panel static status sheet.
* Color mapping: shared role palette above; candidate outlines/badges remain separate.
* Edge-width transformation: HTML supports separate raw sqrt and effective-score sqrt modes; no score fallback.
* Display filters: No raw search memberships used. Overlap/difference derives from the independent validated sets.
* Known limitations: BLOCKED pending validated Tastekin effective-connectivity results. Status sheet is not a circuit result.
* Files: [figure2_sugar_panels.svg](../static/20261006T221533490089Z/figure2_sugar_panels.svg), [figure2_sugar_panels.pdf](../static/20261006T221533490089Z/figure2_sugar_panels.pdf), [figure2_sugar_panels.png](../static/20261006T221533490089Z/figure2_sugar_panels.png)

### figure3_candidate_comparison

* Scientific label / raw versus selected: **CANDIDATE**
* Scientific question: Why are these six types included, and what are their direct raw sensory/motor connections?
* Node inclusion rule: Exactly six user-requested candidate types; 12 individual bodies with preserved sides.
* Edge inclusion rule: Direct LB3b/LB3c→candidate and candidate→four motor types; table sums across endpoint type bodies.
* Source files: nodes.csv; raw_edges.csv; paper/supplement/supplemental_information.pdf pp17,20; results/method_recovery/20261006T214639Z/audit_snapshot_final/logs/claim_ledger.csv C061 (relative CSV names resolve in the frozen source run).
* Dataset: `male-cns:v1.0`; no cross-dataset substitution.
* Layout: Six separate cards with two body rows each; no candidate-to-candidate pathway drawing.
* Color mapping: shared role palette above; candidate outlines/badges remain separate.
* Edge-width transformation: Not applicable: exact raw counts in tables, no drawn edges.
* Display filters: Only requested comparison types and direct sensory/motor boundaries; no effective, Shiu or experimental badges without evidence.
* Known limitations: Raw counts are not normalized strengths; order for GNG021/GNG232/DNg67/DNge080 remains unknown; no dynamic validation implied by aliases.
* Files: [figure3_candidate_comparison.svg](../static/20261006T221533490089Z/figure3_candidate_comparison.svg), [figure3_candidate_comparison.pdf](../static/20261006T221533490089Z/figure3_candidate_comparison.pdf), [figure3_candidate_comparison.png](../static/20261006T221533490089Z/figure3_candidate_comparison.png)

### anatomy

* Scientific label / raw versus selected: **RAW STRUCTURAL / PAPER-ASSOCIATED / CANDIDATE / SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY (per group)**
* Scientific question: What are the actual morphologies of the explicitly requested bodies?
* Node inclusion rule: Only verified paper bodies, explicitly requested candidate bodies, and any later validated selected bodies; maximum 500.
* Edge inclusion rule: Original SWC child-parent cable segments only; not synaptic edges; no healing or inferred connections.
* Source files: Official native v1.0 per-body SWCs; retrieval_manifest.json; anatomy.json (relative CSV names resolve in the frozen source run).
* Dataset: `male-cns:v1.0`; no cross-dataset substitution.
* Layout: 3D orthographic interactive orbit with body hover; verified named cameras or explicitly native XYZ projections.
* Color mapping: shared role palette above; candidate outlines/badges remain separate.
* Edge-width transformation: Constant cable display width; never encode synapse count as neurite thickness.
* Display filters: LB3b, LB3c, paper downstream, selected downstream, motors, combined paper, comparison candidates; body-side filter.
* Known limitations: Skeleton retrieval status: BLOCKED. Named cameras require verified orientation. No actual anatomical renders are claimed for any blocked group.
* Files: [anatomy_BLOCKED.svg](../anatomy/20261006T221533490089Z/anatomy_BLOCKED.svg), [anatomy_BLOCKED.pdf](../anatomy/20261006T221533490089Z/anatomy_BLOCKED.pdf), [anatomy_BLOCKED.png](../anatomy/20261006T221533490089Z/anatomy_BLOCKED.png), [index.html](../anatomy/20261006T221533490089Z/index.html)

### Interactive body-level explorer

* Scientific question: Which directed records and evidence apply to a chosen body or narrow circuit subset?
* Node inclusion: 110 verified requested bodies in this build; future validated results can explicitly extend the source-backed inventory, up to the 500-body safety cap.
* Edge inclusion: induced frozen raw records among these bodies; paper mode restricts to saved named-route edges. Candidate cards are independent fixed direct-boundary summaries.
* Sources: [model.json](../data/20261006T221533490089Z/model.json), nodes.csv, raw_edges.csv and paper_associated_paths.csv in the source run; separate selected-result contract if supplied.
* Dataset and raw/selected status: v1.0; each tab carries its own scientific label. Sugar panels remain empty while blocked.
* Layout: side-separated role layers, explicit individual body labels; responsive cards for independent candidates. Scroll/zoom, inspect nodes and SVG export.
* Palette and width: same role colors and sqrt scale. All exact body weights are on edge hover and in the records table. Missing effective scores produce an unavailable state, never a raw-width substitution.
* Filters: requested types, four motor targets, P/R/E/D/X support, left/right/both, minimum raw count, clicked-body edges. >260 displayed edges suppresses arrows with an explicit message; records remain inspectable. No whole structural export is plotted.
* Limitations: candidate-card boundary totals deliberately pool partner sides and are fixed summaries; explanatory text specifies which graph controls do not apply. Dynamic/experimental evidence requires a future source-backed adapter, not invented badges.

## Graph exchange

| File stem | Scientific label | Bodies | Edges |
|---|---|---:|---:|
| [raw_focused](../graph/20261006T221533490089Z/raw_focused.graphml) · [GEXF](../graph/20261006T221533490089Z/raw_focused.gexf) | RAW STRUCTURAL | 110 | 1923 |
| [paper_associated](../graph/20261006T221533490089Z/paper_associated.graphml) · [GEXF](../graph/20261006T221533490089Z/paper_associated.gexf) | PAPER-ASSOCIATED | 102 | 274 |
| [candidate_comparison](../graph/20261006T221533490089Z/candidate_comparison.graphml) · [GEXF](../graph/20261006T221533490089Z/candidate_comparison.gexf) | CANDIDATE | 12 | 0 |

Both graph formats preserve individual body IDs, sides, raw counts, evidence and source metadata. The candidate exchange has no edges because the comparison does not assert a shared pathway. The focused raw graph provides separately labeled structural connections. No selected graph is emitted without a validated result.

## Reuse and verification

[Build and validation instructions](../README.md) · [Future selected-result contract](SELECTED_RESULTS.md) · [Scientific validation results](../data/20261006T221533490089Z/validation.json). Static figures are SVG/PDF plus PNG at 320 DPI. SVGs preserve text and edge/node hover titles.

## Supplementary support and verification scope

Figure 3 and the explorer use frozen C061 supplementary evidence: GNG232 in S16A, Fudog in S16A/S19, Rounddown in S19. P badges mean scoped type/alias support, not recovered selected-body membership. Figure 1 membership remains unchanged. C071 supersedes earlier visualization C066; drafts are retained as superseded.

The final build passed eight Python contract tests and 36 offline JavaScript behavior checks. Full-browser visual testing was unavailable because Chrome exited with code 134. Static figures were visually inspected. Authentic requested SWCs were unavailable, so anatomical output is BLOCKED and the renderer is not claimed tested on those actual morphologies.
