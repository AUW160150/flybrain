"""Write the checkpoint from checked structural artifacts; not an experiment runner."""
from pathlib import Path
import csv,json,collections
ROOT=Path(__file__).resolve().parents[1];REL=(ROOT/'config/current_structural_run.txt').read_text().strip();RUN=ROOT/REL
def read(name):return list(csv.DictReader(open(RUN/name)))
def link(name,label=None):return f'[{label or name}](../{REL}/{name})'
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(str(x).replace('|',' / ') for x in r)+' |' for r in rows])
def main():
    summary=json.loads((RUN/'export_summary.json').read_text());comparison=json.loads((RUN/'structural_comparison_summary.json').read_text());extra=json.loads((RUN/'supplemental_summary.json').read_text());checks=json.loads((RUN/'validation_checks.json').read_text())
    reach=read('source_target_reachability.csv');circs=read('circuit_summary.csv');origins=read('full_lb3_component_origins.csv');motifs=read('paper_motif_comparison.csv');matrix=read('named_neuron_edge_validation.csv');partners=read('gng021_partners.csv');important=read('important_intermediates.csv');growth=read('bounded_circuit_growth.csv')
    def paths(types):return sum(sum(int(r[f'simple_paths_h{h}']) for h in range(1,5)) for r in reach if r['analysis']=='sensory_to_motor' and r['source_type'] in types)
    numbers={c:paths(ts) for c,ts in [('A',['LB3a','LB3b','LB3c','LB3d']),('B',['LB3b']),('C',['LB3c']),('D',['LB3b','LB3c'])]}
    sections=[];add=sections.append
    add(f'''# Structural connectivity checkpoint — Gates 2 and 3

6 October 2026. Run `{REL}`.

**STRUCTURAL CONNECTIVITY ONLY.** Gates 2 and 3 are finished within the bounds below. Gate 1 identities were reused. The structural searches, body-level edge checks, comparisons and visualization exports are complete; Puddle's identity and the paper's exact computational methods remain unresolved. No effective-connectivity calculation, statistical replication, physiological simulation or polished biological figure was produced. No strict computational replication is claimed.

The graph supports many alternative routes, including routes through GNG021. Structural reachability does not establish activation, inhibition, physiological importance or a sugar-specific pathway. In particular, a neuron appearing in these dense unthresholded graphs is not evidence that the paper's selection algorithm would retain it.

## Dataset and raw-edge validation

**VERIFIED:** authenticated `male-cns:v1.0`, UUID `4b2087c0fbe046bfaf0d60bc970e3e5d`. Start and end Meta records agree on family/tag, UUID, last database edit and latest mutation ID `1006591300`. Last edit: `2026-03-28 11:56:30.222612573-04:00 / 2026-06-08T01:31:39-04:00 (segment property update)`. See {link('raw/meta_start.json')} and {link('raw/meta_end.json')}.

The complete [official released graph](https://male-cns.janelia.org/download/) is retained at `data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather`: **88,384,522 segment endpoints and 151,856,684 directed body pairs**. These are segments, not 88 million identified neurons. The raw weight sum is **311,833,243**, matching live Meta `totalPostCount`. Weights range from 1 to 2,591; no duplicate body pair or nonpositive weight was found. The download's GCS MD5 and local checksum agree; SHA256 is `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1`. {link('raw/flat_weights_provenance.json')}; {link('analysis/graph_summary.json')}.

All **746,910 unique exported edges** were checked against authenticated `ConnectsTo.weight`; **zero neuPrint/flat-file disagreements** were found. This comprises 118,272 complete targeted-query comparisons, containing overlaps, and 628,729 additional pair checks. Raw responses also retain `weightHP` and `weightHR`; neither variant controls this search. Every exported edge has query provenance. Agreement compares two representations of the same reconstruction, not independent biological measurements. {link('edge_source_comparison.csv')}; {link('path_edge_source_comparison.csv')}; {link('raw_edges.csv')}.

## Search definition, bounds and preservation

The starting bodies remain LB3a 17 (9 L/8 R), LB3b 11 (5 L/6 R), LB3c 23 (12 L/11 R), and LB3d 26 (11 L/15 R). Targets are four MN4a bodies and two each of MN6, MN8 and MN9. MN4b is excluded from the **target list**, not silently removed as a possible graph intermediate. Missing `entryNerve` for LB3c 957530 remains missing; the body is retained.

Reachability and shortest directed distances use the entire released graph with **no hop cutoff**. All edge costs are one for this purpose; synapse counts remain raw annotations. No synapse-count, ROI, annotation, tracing-status, hemisphere or intermediate-type filter was applied. The filename's `minconf-0.5` is release preprocessing, not a new filter or a verified paper-method parameter.

Before choosing a bound, forward expansion and motor-compatible lower-bound corridors were measured at depths 0–7. For A, the corridor grows from 1,854 nodes/40,533 edges at depth 3, to 23,960/358,931 at depth 4, to 89,113/4,490,174 at depth 5. Corridor counts may include bounded walks and therefore exceed exact simple-path membership. This sharp expansion motivated the uniform **maximum of four edges** for simple paths, with smaller bounds retained. This is an analysis choice, not the paper's pruning algorithm. {link('graph_growth_by_depth.csv')}; {link('search_config.json')}.

Every directed **vertex-simple** path within four hops was visited for A–D and for each of E's two separate legs. A path cannot revisit a body. Other sensory bodies and motor bodies may occur internally; targets are not made absorbing, and no cell class is removed from the graph. Thus “LB3b only” describes the starting population, not a ban on other sensory intermediates. At four hops, B and C each contain all 77 LB3 bodies somewhere in their path unions. This matters when defining a later sugar-restricted experiment.

Counts and node/edge memberships are exhaustive **within these bounds**. Saved simple-path examples are capped at **100 per ordered body pair and exact hop count**, in ascending-body-ID traversal order, without weight ranking. The cap did not affect membership or counting. **195,120 examples** are saved from 364,457,645 paths counted across the three query scopes (A, sensory→GNG021 and GNG021→motor). All **33,851 shortest paths** for all 944 tested ordered pairs were saved; the 10,000-per-pair safety cap was never reached. Exact omitted-example counts are in {link('path_enumeration_counts.csv')}. No completeness beyond four-hop simple paths is asserted.

## Paper-associated named edges

**VERIFIED current raw structure:** all four Quasimodo/GNG042→GNG015 body pairs exist:

{table(['Source','GNG015 L 523590','GNG015 R 28181'],[['Quasimodo L 15321',73,88],['Quasimodo R 15734',87,81]])}

All eight GNG015→MN4a pairs and all four GNG015→MN9 pairs exist:

{table(['Source','MN9 L 10331','MN9 R 16949','MN4a L 18295','MN4a L 36368','MN4a R 27938','MN4a R 522704'],[['GNG015 L 523590',266,16,49,31,10,13],['GNG015 R 28181',177,19,19,18,7,41]])}

These are synapse counts, not activation strengths. GNG042 and GNG015 have supplied GABA prediction/consensus labels; their physiological effects were not tested. {link('named_neuron_edge_validation.csv')}; {link('nodes.csv')}.

Clavicle/ANXXX462a connects to Sternum/GNG585: **514625 L→10961 L:59**, **514625 L→13611 L:39**, **19480 R→12402 R:80**. Sternum has two listed left bodies and one right body; none was collapsed. Its branches through Roundup/GNG108 (523040 L, 26764 R), Roundtree/GNG120 (513162 L, 10881 R), and GNG472 (46013 L, 524254 R) reach the illustrated motor classes. Alias/type/side checks for these additional records match live neuPrint in all 54 compared fields. {link('analysis/additional_alias_crosscheck.json')}; {link('paper_associated_paths.csv')}.

**SOURCE CONFLICT — descriptive paper/current comparison:** all 12 mapped type-pair motifs have current structural edges, but eight pooled raw totals differ from [Figure 6I/J](../paper/primary/figure6.jpg):

{table(['Source type','Target type','Figure label','Current all-body sum','Difference'],[[r['source_type'],r['target_type'],r['paper_figure6_label'],r['current_all_body_sum'],r['difference']] for r in motifs])}

The figure's exact pooling, snapshot and selection rules are unresolved. These discrepancies do not identify their cause, and are **not neuPrint/flat-file disagreements**. Four equal totals also do not establish strict replication. {link('paper_motif_comparison.csv')}.

The illustration is not a complete raw adjacency list. Current direct motor totals also include:

{table(['Source type','MN4a','MN6','MN8','MN9'],[[st]+[sum(int(r['weight']) for r in matrix if r['source_type']==st and r['target_type']==tt) for tt in ['MN4a','MN6','MN8','MN9']] for st in ['GNG042','ANXXX462a','GNG015','GNG021']])}

For example, GNG015→MN8 totals 155, while Quasimodo→MN8 has a single weight-1 edge; Clavicle has no direct edge to any requested motor. Tested absent individual pairs are recorded with `present=False` in the named validation matrix, not inserted as zero-weight edges into the graph.

**BLOCKED — SOURCE REQUIRED:** Puddle has no match in the six searched flat annotation fields or the live synonym/instance query. Figure 6 names Puddle but does not establish its MaleCNS body IDs. Its claimed identity cannot be validated here. All current two-edge Quasimodo→intermediate→MN8 bridges are preserved in {link('quasimodo_mn8_unassigned_bridges.csv')}, without renaming any intermediate Puddle. A paper source-data/curator mapping is needed. {link('analysis/puddle_identity_audit.json')}.
''')
    add('## Circuits A–D and routes to individual motors\n\n**VERIFIED:** no starting LB3 body directly connects to a requested motor. All 770 body pairs are reachable: 718 shortest distances are two hops and 52 are three. Each circuit independently uses its specified starting bodies; named neurons are not required in route selection. Shared graph preparation does not change the separate per-source searches. '+link('source_target_reachability.csv')+'; '+link('shortest_paths.csv')+'.\n\n'+table(['Circuit','Starting population','Nodes ≤4','Edges ≤4','Simple paths ≤4'],[[r['circuit'],{'A':'all 77 LB3a–d','B':'11 LB3b','C':'23 LB3c','D':'34 LB3b+LB3c'}[r['circuit']],r['nodes'],r['edges'],f"{numbers[r['circuit']]:,}"] for r in circs if r['circuit']!='E']))
    motorrows=[]
    for t in sorted({int(r['target']) for r in reach if r['analysis']=='sensory_to_motor'}):
        rr=[r for r in reach if r['analysis']=='sensory_to_motor' and int(r['target'])==t];row=[f"{rr[0]['target_type']} {rr[0]['target_side']} {t}"]
        for ts in [['LB3a'],['LB3b'],['LB3c'],['LB3d']]:
            ds=[int(r['shortest_hops']) for r in rr if r['source_type'] in ts];row.append(str(min(ds)) if min(ds)==max(ds) else f'{min(ds)}–{max(ds)}')
        motorrows.append(row)
    add('\nShortest-distance ranges across individual starting bodies, preserving each motor ID:\n\n'+table(['Motor body','LB3a','LB3b','LB3c','LB3d'],motorrows)+f'\n\nA, B, C and D retain all ten motors. Individual body paths and their raw edge weights are in {link("simple_paths.csv")}, {link("lb3b_paths.csv")}, {link("lb3c_paths.csv")} and {link("lb3b_lb3c_combined_paths.csv")}. The latter three contain capped examples; the table above and {link("circuit_summary.csv")} use exhaustive memberships/counts. Path-count differences are not tests of whole-path dominance and are affected by unequal numbers of starting bodies.\n')
    add('Full-LB3 component origins, including overlap:\n\n'+table(['Origin','Starting bodies','Nodes supported','Edges supported','Nodes unique among a–d','Edges unique among a–d'],[[r['sensory_subtype'],r['starting_bodies'],r['nodes'],r['edges'],r['nodes_unique_within_all_LB3'],r['edges_unique_within_all_LB3']] for r in origins])+f'\n\nMembership for every body/edge is retained in `source_subtype_membership`. {link("full_lb3_component_origins.csv")}.\n')
    add(f'''## Shared structure, convergence and divergence

At the four-hop bound, B and C share **12,575 nodes and 219,958 edges**. B has **3,677 nodes/37,524 edges** absent from C; C has **3,581 nodes/54,278 edges** absent from B. Excluding the fixed 77 sensory and ten motor endpoints leaves **12,488 shared intermediate segments**, with the same unique-segment counts. “Intermediate” does not imply a fully annotated interneuron. {link('structural_node_comparison.csv')}; {link('structural_edge_comparison.csv')}.

**INTERPRETATION:** there are **zero combined-only nodes, edges or paths** under identical static graph bounds: paths from a union of source sets equal the union of their separate paths. Combination can reveal convergence motifs without creating new routes. There are **663 nodes** with at least two incoming partners in D but at most one in each separate B/C graph. {link('combined_only_convergence_motifs.csv')}; {link('structural_comparison_summary.json')}.

{table(['Circuit','Convergence nodes (in-degree >1)','Divergence nodes (out-degree >1)','Opposite-side endpoint edges','Unknown-side edges'],[[r['circuit'],r['convergence_nodes'],r['divergence_nodes'],r['opposite_side_edges'],r['unknown_side_edges']] for r in circs])}

Per-body partners, degrees, source-subtype support and shared incoming branches are available in {link('convergence_divergence.csv')}. Convergence/divergence are graph properties, not evidence of simultaneous activation or summation.

The search discovers numerous intermediates beyond the requested names. Examples ranked by the number of distinct sensory–motor body pairs whose **shortest** paths contain the body are:

{table(['Body/type/side','Body pairs','Body NT prediction','Consensus'],[[f"{r['body_id']} {r['type']} {r['side']}",r['sensory_motor_pairs_with_this_shortest_intermediate'],r['predicted_neurotransmitter'],r['consensus_nt']] for r in important[:8]])}

This is descriptive route occurrence, not functional importance. All 900 bodies appearing as shortest-path intermediates are listed in {link('important_intermediates.csv')}; all other bounded-path intermediates remain in the node/edge tables. The histamine consensus versus unclear/serotonin body predictions for GNG043 illustrate why the two NT fields cannot be silently substituted.
''')
    er=[r for r in reach if r['analysis']=='gng021_to_motor'];e_table=[]
    for t in sorted({int(r['target']) for r in er}):
        x={int(r['source']):r for r in er if int(r['target'])==t};r=x[27203]
        e_table.append([f"{r['target_type']} {r['target_side']} {t}",x[27203]['direct_synapse_count'],x[27203]['shortest_hops'],x[521222]['direct_synapse_count'],x[521222]['shortest_hops']])
    top_partners=[]
    for v in [27203,521222]:
        for direction in ['upstream','downstream']:
            for r in partners:
                if int(r['candidate_body'])==v and r['direction']==direction and int(r['raw_weight_rank'])<=5:top_partners.append([v,direction,f"{r['partner_body']} {r['partner_type']} {r['partner_side']}",r['weight']])
    add(f'''## Circuit E — GNG021 hypothesis

**VERIFIED:** neither GNG021 body—27203 L or 521222 R—receives a direct edge from any of the 77 LB3 bodies. All **154** LB3→GNG021 ordered pairs have shortest length **2**, including every subtype and source side. This is an indirect structural candidate, not a direct LB3 recipient or a paper-selected neuron. {link('named_neuron_edge_validation.csv')}; {link('source_target_reachability.csv')}.

Both bodies structurally reach all ten motor bodies. Direct counts and unbounded shortest lengths are:

{table(['Motor','27203 L direct count','Hops','521222 R direct count','Hops'],e_table)}

Zero means no direct record in the release, not no indirect route. Shortest motor distances are one or two hops. Direct MN8 and MN9 outputs occur only to the left target bodies, whereas both MN6 bodies receive direct edges; this is not left/right weight symmetry. All four LB3 source populations have symmetric two-hop *reachability* to both candidates, which does not imply symmetric edge weights.

Strongest raw upstream/downstream partners for each candidate (top five by synapse count, complete unfiltered lists retained separately):

{table(['GNG021 body','Direction','Partner body/type/side','Synapses'],top_partners)}

{link('gng021_partners.csv')} retains every partner, ranks, NT fields, membership and reciprocal status. The upstream lists establish convergence from multiple distinct bodies, including GNG028, GNG025 and GNG140, as well as Quasimodo. Intermediate paths from each sensory subtype are preserved in {link('gng021_candidate_paths.csv')} and the complete shortest-path file.

GNG021 overlaps directly with the Quasimodo/GNG015 network:

- Quasimodo **15321→27203:98; 15321→521222:82; 15734→27203:79; 15734→521222:120**.
- GNG021 **27203→523590:216; 27203→28181:228; 521222→523590:157; 521222→28181:182**, where the targets are GNG015 L/R.
- Reverse GNG021→Quasimodo edges are **27203→15321:9; 27203→15734:6; 521222→15321:3; 521222→15734:6**.
- GNG015 **523590→27203:1** and **28181→521222:1** provide additional reciprocal motifs. The GNG021 pair itself has **27203→521222:9** and **521222→27203:7**.

Every number joins to {link('named_neuron_edge_validation.csv')}. Opposite-side body pairs are explicit; the crossing neurite has not been identified anatomically. These feedback motifs do not establish physiological recurrence or sign.

**INTERPRETATION:** GNG021 survives the structural search as an indirectly reachable, motor-connected candidate. Its neighborhood overlaps the known network, so it is not a structurally disjoint replacement for Quasimodo/GNG015. A distinct functional role and paper membership remain unverified. Post hoc examples containing Quasimodo→GNG021→GNG015 are kept separately in {link('gng021_overlap_examples.csv')}, explicitly not claimed as a paper motif.

E's **34,576 nodes/536,440 edges** are the union of **LB3→GNG021 paths up to four hops** and **GNG021→motor paths up to four hops**, traced independently. These counts are not directly comparable with A's single end-to-end four-hop bound and do not claim exhaustive eight-hop sensory–motor paths. Independently, the unrestricted A search contains **3,641,392 actual simple sensory–motor paths through GNG021 within four hops**, covering all 770 sensory–motor body pairs. {link('gng021_end_to_end_path_counts.csv')}.
''')
    add(f'''## Recurrence and left/right interpretation

Every A–E bounded path-union graph forms one strongly connected component at four hops; accordingly all of its path-union edges lie on a directed cycle **in that union graph**. The cycle may be longer than an individual four-hop path. No repeated-vertex walk was enumerated as a simple path. The export plus explicitly added reciprocal/self-loop context contains **643,924 cycle edges**, **145,594 distinct reciprocal pairs**, and **78 self-loops**. {link('recurrent_edges.csv')}; {link('reciprocal_pairs.csv')}; {link('circuit_summary.csv')}.

There are **55,599 three-edge cycle records around GNG021 in the exported graph**, indexed by the candidate body at which the cycle starts; cycles containing both candidates can therefore appear twice. This is not an enumeration of every full-connectome cycle. {link('gng021_three_edge_cycles.csv')}.

The A path union includes **997 motor-origin edges**, 524 of weight one. Examples include MN4a 27938→GNG108 26764 (33) and MN8 16827→GNG120 513162 (17), both independently query-checked. These records explain why an absorbing-motor interpretation cannot be silently substituted for the actual search. Presynaptic placement/segmentation and functional interpretation need separate manual review. {link('motor_origin_edges_in_circuit_A.csv')}.

All four endpoint-side combinations are preserved before bilateral summaries: **185 L→L**, **185 L→R**, **200 R→R**, **200 R→L** sensory–motor body pairs, all reachable. The graph uses sensory `rootSide` and other bodies' available `somaSide`/`rootSide`, retaining the original fields and provenance. {link('left_right_comparison.csv')}; {link('path_counts_by_side.csv')}.

The raw export contains **221,159 opposite-side endpoint edges** and **210,710 edges with undetermined side relation**. Sample paths retain their full side sequence, opposite-side steps and unknown-side steps, including same-side endpoints whose path switches side internally. A side label is not a synapse coordinate: anatomical midline crossing and which neurite crosses remain **UNVERIFIED**, requiring morphology or synapse locations. Do not relabel every opposite-soma edge as an anatomically localized midline crossing.

Weight asymmetries are concrete: GNG015→MN9 totals **443 to left body 10331 versus 35 to right body 16949**; GNG021 has direct MN8/MN9 edges only to their left bodies; Sternum has two left bodies and one right. These are raw structural observations, without normalization or statistical testing.

## Uncertainties, audit and experiment design

- **BLOCKED — SOURCE REQUIRED:** Puddle's MaleCNS type/body mapping; full final main paper/STAR Methods; paper implementation/commit; exact effective-connectivity equation, normalization, bootstrap, pruning and simulation algorithm. These did not block the authorized structural phase.
- **UNVERIFIED:** the paper's exact dataset snapshot/pooling, causes of eight figure-total discrepancies, GNG021's paper membership, physiological interpretation of raw motor-origin edges and weak fragment connections, and anatomical crossing locations.
- **VERIFIED field distinctions, physiological policy unresolved:** 1,009 exported bodies have different nonempty body-NT prediction and consensus fields (509 unclear predictions; 500 differing named predictions). Thirty-three were already logged; all 976 newly encountered distinctions are retained in the mismatch ledger and {link('nt_field_distinctions.csv')}. Neither field was used to assign physiological sign.
- **Scope limitation:** 7,547 A nodes and 14,392 visualization nodes lack curated annotations; unknown type/side/class remain explicit. Weight-one edges are retained (146,675 in A). A later display or robustness filter must create a separately labeled derivative and retain this baseline.
- **Still not tested:** H1 whole-path dominance, physiological activation, paper algorithm selection and statistical/strict computational replication. A high path count is not evidence for any of them.

The three-experiment scaffold can remain. Its definitions need these clarifications before execution: experiment 1 must reconcile the paper snapshot/weight differences and missing method; experiment 2 must specify whether “restricted” means only starting inputs (as B–D do here) or additionally removing other sensory intermediates; experiment 3 should test GNG021 as an **indirect, overlapping candidate**, not a direct LB3 recipient or an already independent circuit. Puddle identity and an explicit NT interpretation policy remain prerequisites for any claims that rely on them. Experiment configurations remain drafts with `execution_allowed: false`.

## Files, validation and visualization readiness

The full raw graph is retained unchanged. `raw_edges.csv` is a **documented extracted view**, comprising unfiltered targeted-query neighborhoods, all bounded-path edges and reciprocal/self-loop context; it is not a CSV conversion of all 151 million graph edges. It contains 129,125 nodes/746,910 edges, leaving 88,255,397 nodes/151,109,774 edges outside that view. No nodes or edges were removed by a synapse threshold. {link('export_summary.json')} records exact selection counts.

The visualization view has **37,246 nodes and 643,834 edges**. It omits 91,879 raw-context nodes and 103,076 raw-context edges that are outside bounded paths, feedback context and mapped paper motifs; they remain in the raw tables. {link('visualization_views.json')} defines A/B/C/D/E and the paper-associated view. The paper-associated route file contains 3,564 explicitly labeled routes, selected only after the unrestricted searches; it does not define A–D.

Required outputs: {', '.join(link(n) for n in ['nodes.csv','raw_edges.csv','source_target_reachability.csv','shortest_paths.csv','simple_paths.csv','recurrent_edges.csv','left_right_comparison.csv','lb3b_paths.csv','lb3c_paths.csv','lb3b_lb3c_combined_paths.csv','gng021_candidate_paths.csv','named_neuron_edge_validation.csv'])}.

Graph export: {link('circuit_graph.graphml')}, plus {link('visualization_nodes.csv')} and {link('visualization_edges.csv')}. Metadata support body IDs, types/classes, raw annotations, both NT fields, side provenance, edge weight/direction, recurrence, shared/unique membership and source-subtype contribution. Raw responses and exact query files live under `raw/` and `queries/`; full-graph caches/distances and processing logs are under `analysis/`. Additional named, comparison, convergence, growth, NT and provenance tables are indexed in {link('README.md')}; scientific artifacts and requests/responses are hashed in {link('manifest.json')}.

**Validation:** four synthetic behavior tests pass, including cycles, bounds, multiple targets, source-set union, unreachable vertices, SCC direction and annotation grouping. Export checks join every saved path weight and side sequence to the verified body-edge tables, verify shortest-path completeness and path-example caps, check recurrence certificates, and parse GraphML with exact weight/referential-integrity checks. All required files pass. {link('validation_checks.json')}; {link('analysis/search_tests.log')}.

**Ready for side-by-side structural visualization:** yes, using the declared view definitions and preserving unknown annotations, raw strengths and predicted NT labels. The graph is dense; a readable final figure will need explicit display choices. Puddle cannot yet be given a verified body label, and the figures must not imply physiology or strict replication.

**Stop point:** Gates 2 and 3 only. No effective-connectivity, statistical replication or simulation is authorized by this checkpoint. See [STATUS](../STATUS.md), [claim ledger](../logs/claim_ledger.csv), [mismatch ledger](../logs/mismatch_ledger.csv), [query log](../logs/query_log.jsonl), [decisions](../logs/decision_log.md) and [unresolved questions](../logs/unresolved_questions.md).
''')
    (ROOT/'docs/structural_connectivity_checkpoint.md').write_text('\n'.join(sections)+'\n')
    descriptions={'nodes.csv':'All extracted body/segment metadata, annotation JSON, side source, NT fields and exact bounded memberships.','raw_edges.csv':'All extracted edges; every weight checked against live neuPrint. Full unfiltered release retained in data/raw Feather.','source_target_reachability.csv':'944 individually identified ordered pairs; full-graph directed distances and exact per-depth path counts.','shortest_paths.csv':'All 33,851 shortest paths; no truncation.','simple_paths.csv':'195,120 deterministic examples; cap 100 per pair/hop; not a complete path listing.','path_enumeration_counts.csv':'Exact path counts and saved counts per ordered pair/depth.','graph_growth_by_depth.csv':'Prebound full-graph growth (0–7), including lower-bound walk corridors.','bounded_circuit_growth.csv':'Exact simple-path union membership at bounds 1–4.','circuit_graph.graphml':'Visualization graph; directed, numeric raw weights, node and edge metadata.','visualization_views.json':'Six view definitions; E leg bounds differ from A–D end-to-end bounds.','recurrent_edges.csv':'Cycle edges in export graph; separate from vertex-simple path records.','reciprocal_pairs.csv':'Each distinct two-body reciprocal pair once; self-loops separate.','named_neuron_edge_validation.csv':'Positive edges and tested absences for sensory/named/motor queries.','paper_associated_paths.csv':'Post hoc named view, 3,564 paths; not an input restriction on A–D.','gng021_overlap_examples.csv':'3,264 exact named-pattern paths, explicitly candidate extensions rather than paper claims.','gng021_partners.csv':'Complete raw incoming and outgoing partners, not a top-partner cutoff.','gng021_three_edge_cycles.csv':'Candidate-anchored length-3 cycles in export; not full-connectome cycle enumeration.','quasimodo_mn8_unassigned_bridges.csv':'All targeted two-edge bridges; no Puddle identity assigned.','motor_origin_edges_in_circuit_A.csv':'997 verified motor-origin edges retained by the nonabsorbing-target definition.','nt_field_distinctions.csv':'1,009 distinct nonempty NT field pairs; no sign assignment.','validation_checks.json':'Export/path/GraphML checks.','search_config.json':'Explicit bounds, caps, no-filter rules, rationale and exclusions from scientific scope.','export_summary.json':'Counts outside each exported view; no weight-based removal.','manifest.json':'Input/output/script hashes, environment and audit snapshot.'}
    files=sorted(p.name for p in RUN.iterdir() if p.is_file())
    readme=f'''# Run {RUN.name}\n\n**STRUCTURAL CONNECTIVITY ONLY** — authenticated male-cns:v1.0 / UUID 4b2087c0fbe046bfaf0d60bc970e3e5d. [Checkpoint](../../../docs/structural_connectivity_checkpoint.md).\n\nThe full released Feather is `../../../data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather`. No synapse-count/type/side/status/ROI cutoff was used. Raw CSV and GraphML files are selected views with exact scope/counts in `export_summary.json`; they do not replace the complete retained Feather.\n\nSource selection for B/C changes the starting bodies only. Other sensory and motor bodies may be internal vertices. Simple paths cannot repeat vertices. Counts/memberships are exhaustive up to four hops; CSV examples are capped at 100 per ordered pair and hop. E separately bounds each leg to four hops; it does not enumerate all eight-hop end-to-end paths.\n\n`circuit_membership` means an edge/node occurs on a searched simple path within the bound. `context_circuit_membership` identifies reciprocal or self-loop context that need not itself occur on such a path. `recurrence_status` refers to SCC cycle membership in the exported graph; `recurrent_circuits` refers to the individual bounded path-union graphs. A union graph can contain cycles even though each enumerated path is simple.\n\n`source_subtype_membership` is provenance for sensory-to-motor A–D paths; it does not mean functional input strength. Side relationships use soma/root annotation labels, not anatomical synapse crossings. NT body prediction, confidence, consensus and ground-truth source fields remain distinct. GraphML contains selected display fields; nodes.csv retains all raw annotations. Display classification is derived from the supplied superclass; uncertain/missing annotations remain explicit.\n\n`known_paper_motif` marks mapped type-pair motifs, not an assertion that the paper published each individual body edge. `paper_associated_paths.csv` supplies sensory-inclusive named views after unrestricted extraction. Puddle remains unmapped. `weightHP`/`weightHR` are preserved source variants but do not control topology.\n\nA raw CSV edge references `raw/<query>.json`; the corresponding exact Cypher/request is `queries/<query>.json`. Query logs and manifests store hashes. Start/end Meta agree; all exported edges match the full flat source. IDs are integers, direction is source→target, weights are raw counts. Missing edges in the named matrix are tested absences, not zero-weight graph edges.\n\n## Files\n\n'''
    readme+=table(['File','Purpose'],[[f'[{n}]({n})',descriptions.get(n,'Derived structural table/configuration; see checkpoint and column names.')] for n in sorted(set(files)|{'manifest.json','README.md'})])
    readme+='\n\n`queries/` and `raw/` preserve requests/responses, including a failed DNS-only batch transport attempt and successful standard requests. `analysis/export_attempt1.log` records an interrupted export with a redundant set-intersection computation; moving that computation outside the loop changed execution cost, not graph selection or results. `audit_snapshot/` preserves the final ledgers/status.\n\n## Reproducibility\n\nPython 3.12 with requirements-structural.txt. Scripts 05–07 build the complete sparse graph, inspect growth and enumerate bounded simple paths. Script 06 compares complete boundary queries. Script 08 plans pair checks and reciprocal context. After authenticated responses are saved, scripts 09–12 export, summarize and validate. Script 13 writes this report. They use config/current_structural_run.txt and saved source/response files. Exact request JSON is retained; network retrieval uses the user credential only in a temporary ignored curl config, removed after the run. To reproduce, create a fresh timestamped directory and update that pointer; do not overwrite the baseline. No paper-method defaults, signs, simulation or random sampling are implemented.\n'
    (RUN/'README.md').write_text(readme)
    print('Checkpoint and result README written')

if __name__=='__main__':main()
