"""Record the source-blocked checkpoint; does not implement or run replication."""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT/(ROOT/'config/current_method_audit.txt').read_text().strip()
STAMP = dt.datetime.now(dt.timezone.utc).isoformat()
REL = str(RUN.relative_to(ROOT))
EXP = 'METHOD_RECOVERY_AUDIT'
BASE = ROOT/'results/structural/20261006T180116Z'


def csv_write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def append(path, text):
    with path.open('a') as f:
        f.write(text)


def ledger(name, records, id_field):
    path = ROOT/'logs'/name
    existing = list(csv.DictReader(path.open()))
    old = {r[id_field] for r in existing}
    assert not old.intersection(r[id_field] for r in records), 'Already recorded'
    with path.open('a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(existing[0]))
        for r in records:
            writer.writerow(r)


def main():
    assert not (RUN/'checkpoint_recorded.json').exists(), 'Checkpoint is append-only'
    snap = RUN/'audit_snapshot_before'
    snap.mkdir(exist_ok=False)
    for name in ['docs/paper_method_reconstruction.md','docs/prompt_vs_paper_audit.md',
                 'logs/claim_ledger.csv','logs/mismatch_ledger.csv','logs/decision_log.md',
                 'logs/unresolved_questions.md','STATUS.md','config/analysis.yaml',
                 'config/experiments/experiment_02_sugar_restricted.yaml']:
        target=snap/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT/name).read_bytes())

    parameters=[]
    def param(name,value,source,section,page,paraphrase,status,notes='',critical=True):
        parameters.append(dict(parameter_name=name,exact_value_or_equation=value,
            source_document=source,section=section,page_or_figure=page,
            quote_or_precise_paraphrase=paraphrase,code_file='',function_name='',
            verification_status=status,notes=notes,selection_critical=critical))
    sup='paper/supplement/supplemental_information.pdf'
    fig='paper/primary/figure6.jpg'
    param('replication_input_types','LB3a;LB3b;LB3c;LB3d',fig+'; '+sup,'LB3 circuit','Figure 6G; S16A / PDF p17',
          'Four LB3 subtypes are represented.','VERIFIED_FROM_FINAL_PAPER','Current full body membership was validated earlier; exact paper graph/body filtering is still unresolved.')
    param('requested_motor_types','MN4a;MN6;MN8;MN9',fig+'; '+sup,'Proboscis positioning','Figure 6G; S16B-E / PDF p17',
          'Four distinct motor types are compared.','VERIFIED_FROM_FINAL_PAPER')
    param('grn_clustering_synapse_threshold','2',sup,'S2 legend','PDF p22',
          'LB GRN typing uses cosine-based hierarchical clustering with this cutoff.','VERIFIED_FROM_SUPPLEMENT','Typing only; not a graph-wide replication edge cutoff.',False)
    param('incomplete_lbgrn_exclusion_for_typing','8 right; 9 left',sup,'S2B legend','PDF p22',
          'Incomplete reconstructions are excluded from that clustering.','VERIFIED_FROM_SUPPLEMENT','Not established as the effective-connectivity graph rule.',False)
    param('motor_clustering_synapse_threshold','5',sup,'S12 legend','PDF p25',
          'Motor typing uses input connectivity and cosine similarity.','VERIFIED_FROM_SUPPLEMENT','Typing only.',False)
    param('effective_heatmap_max_hops','7',sup,'S13A legend','PDF p25',
          'Heatmaps use a maximum of seven hops.','VERIFIED_FROM_SUPPLEMENT','Does not establish exact/cumulative propagation or the significant-path hop limit.')
    param('heatmap_clustering','Ward',sup,'S13A legend','PDF p25','Dendrogram uses Ward clustering.','VERIFIED_FROM_SUPPLEMENT','Display-stage rule.',False)
    param('hop_plateau_termination','',''+sup,'S13B legend','PDF pp25-26','Curves end when a plateau is reached; Methods are referenced.','PARTIAL','Plateau equation, tolerance and implementation missing.')
    param('grn_bootstrap_reference','upper 95% confidence limit',sup,'S13B legend','PDF pp25-26',
          'One reference derives from an all-GRN bootstrap.','VERIFIED_FROM_SUPPLEMENT','Estimator, sampling and comparison rule unresolved.')
    param('random_neuron_reference','upper 95% confidence limit',sup,'S13B legend','PDF pp25-26',
          'The other reference uses randomly sampled MaleCNS neurons.','VERIFIED_FROM_SUPPLEMENT','Sampling universe and estimator unresolved.')
    param('s16_partner_percentile','exceeds 99th percentile',sup,'S16A-E legend','PDF pp26-27',
          'Subtype-to-partner weight criterion determines colored boxes and follow-up partners.','VERIFIED_FROM_SUPPLEMENT','Percentile denominator/population, aggregation, and estimator are not specified here.')
    param('s16_laterality','ipsilateral and contralateral scores displayed separately',sup,'S16B-E legend','PDF p27',
          'Both side relationships are shown as observations.','VERIFIED_FROM_SUPPLEMENT','Does not define bilateral pooling for Figure 6 weights.')
    param('display_normalization_per_motor','',''+sup,'S15 legend; S18C legend','PDF pp26-27',
          'Heatmaps are normalized per motor type; S18C describes total effective connectivity per MN.','PARTIAL','Do not substitute this display rule for the unknown edge/layer normalization.')
    param('disinhibitory_motif_depth','3 hops from GRNs',fig,'Disinhibition','Figure 6I','Illustrated disinhibitory motif depth.','VERIFIED_FROM_FINAL_PAPER','Not the general path-search limit.')
    param('feedforward_motif_depth','4 hops from GRNs',fig,'Feedforward excitation','Figure 6J','Illustrated excitatory motif depth.','VERIFIED_FROM_FINAL_PAPER','Not the general path-search limit.')
    unknowns={
        'graph_neuron_universe':'Typed/untyped fragments, brain/VNC, ROI and status inclusions unknown.',
        'connectivity_matrix_orientation':'Body-level directed records available; paper matrix orientation and construction unknown.',
        'cleft_score_filter':'Search-index text mentions 50, but full final Methods were not obtained; scale and mapping to v1 minconf-0.5 are unverified.',
        'replication_synapse_weight_filter':'Do not import the typing thresholds or released filename as paper rules.',
        'edge_weight_equation':'Raw anatomical counts available; paper normalized-weight equation missing.',
        'edge_normalization_denominator':'Total postsynaptic input versus presynaptic output versus included-network sums unresolved.',
        'effective_connectivity_equation':'No verified equation; do not infer ordinary matrix powers.',
        'multi_hop_aggregation':'Exact hop versus cumulative hop, route aggregation and population aggregation unresolved.',
        'layer_hop_normalization':'Equation, denominator and timing unresolved.',
        'significant_path_hop_limit':'Cannot infer from seven-hop heatmaps or 3/4-hop illustrations.',
        'significant_path_percentile_80':'80th percentile is requested in prompt_1.md but not independently verified.',
        'percentile_population':'Zeros, body/type pooling, per-layer or whole-network comparison unresolved.',
        'percentile_estimator_and_ties':'Quantile interpolation and equality handling unresolved.',
        'selection_direction':'Input-to-output versus output-to-input scoring/combination unresolved.',
        'pruning_iteration':'Rules, iteration order and stopping condition unresolved.',
        'recurrence_handling':'Self-loops, revisits, sensory relays and absorbing motors unresolved.',
        'bootstrap_replicates':'No verified replicate count.',
        'bootstrap_grn_sample_size':'Current 77 LB3 bodies do not establish paper null sample size.',
        'bootstrap_random_neuron_sample_size':'No verified control sample size.',
        'bootstrap_sampling_universe_replacement':'Eligible neurons and replacement policy missing.',
        'bootstrap_ci_estimator_seed':'Estimator and random seed missing.',
        'paper_body_vs_type_bilateral_pooling':'No verified summation/averaging or selected-body inventory.',
        'paper_motif_extraction_rule':'99th-percentile S16 partner rule cannot automatically be assigned to every Fig6 motif.',
        'neurotransmitter_in_metric':'No explicit paper metric sign policy recovered; preserve metadata, do not insert signs.',
        'paper_snapshot':'MaleCNS family known; analysis release/mutation/adjacency hash unknown.',
        'official_analysis_code_version':'No publication-specific implementation identified in checked repositories.',
    }
    for name,notes in unknowns.items():
        param(name,'','Final Results/STAR Methods and publication-linked implementation required',
              'Not retrieved','','No verified parameter recovered.','UNVERIFIED',notes)
    csv_write(RUN/'method_parameters.csv',parameters)
    append(ROOT/'docs/paper_method_reconstruction.md',f'\n\n## {STAMP} — Independent method recovery for prompt_1.md\n\n'
        f'**Still PARTIAL; main replication blocked.** Live v1.0 identity passed again. The final supplement and Table S1 were re-fetched and are byte-identical to the earlier copies. '
        'Main final paper/STAR Methods requests returned 403; full API 401. Author-linked PDF also returned 403. '
        'Search-index excerpts were treated as discovery leads, not a substitute for the missing source. No exact algorithm or numerical assumption was adopted.\n\n'
        f'Full parameter records with the requested ten fields, plus a criticality flag, are in [{REL}/method_parameters.csv](../{REL}/method_parameters.csv). '
        'Blank code/function fields mean no paper-specific implementation was recovered. VERIFIED values have narrow figure/stage scopes and do not imply a verified complete method.\n\n'
        '| Parameter | Value / equation | Source and location | Verification | Missing detail / scope |\n| --- | --- | --- | --- | --- |\n'+
        ''.join(f"| {p['parameter_name']} | {p['exact_value_or_equation'] or 'not recovered'} | {p['source_document']}; {p['section']}; {p['page_or_figure']} | {p['verification_status']} | {p['notes']} |\n" for p in parameters)+
        '\nRECONSTRUCTED_METHOD_ASSUMPTION: **none adopted**. The gaps concern selection-changing definitions, so a sensitivity analysis around guessed equations would not establish replication. '
        'Keep the mathematics implementation and biological execution gated. The six new arithmetic tests exercise only the raw pooling audit.\n')

    versions=['PUBLISHED_REFERENCE','V1_PAPER_REPLICATION','V1_SUGAR_LB3B','V1_SUGAR_LB3C','V1_SUGAR_LB3B_LB3C','V1_CANDIDATE_EXTENSIONS','SHIU_FLYWIRE_REFERENCE']
    vroot=ROOT/'results/circuit_versions';vroot.mkdir(exist_ok=True)
    for name in versions:
        p=vroot/name;p.mkdir(exist_ok=True)
        status='PARTIAL_REFERENCE_NOT_COMPLETE' if name=='PUBLISHED_REFERENCE' else ('NOT_ASSESSED' if name=='SHIU_FLYWIRE_REFERENCE' else 'NOT_RUN_METHOD_BLOCKED')
        definition=dict(circuit_version=name,status=status,selected_nodes=None,selected_edges=None,
            dataset='paper snapshot unresolved' if name=='PUBLISHED_REFERENCE' else ('FlyWire reference not yet verified' if name=='SHIU_FLYWIRE_REFERENCE' else 'male-cns:v1.0'),
            source_run=REL,scope='Definition/readiness only; no inferred circuit membership')
        (p/'definition.json').write_text(json.dumps(definition,indent=2)+'\n')
    motifs=list(csv.DictReader((RUN/'weight_audit/paper_weight_comparison.csv').open()))
    csv_write(vroot/'PUBLISHED_REFERENCE/mapped_figure6_motifs.csv',[
        dict(source_type=m['source_type'],target_type=m['target_type'],paper_displayed_weight=m['paper_displayed_weight'],
             paper_source='Final Figure 6I/J',paper_selected_body_ids='',completeness='12 mapped motifs only; Puddle motifs and full Figure 6G inventory incomplete') for m in motifs])
    comparisons=[]
    for m in motifs:
        comparisons.append(dict(node_or_edge=m['source_type']+'->'+m['target_type'],published_reference='PRESENT_FIGURE6_TYPE_MOTIF',
            v1_paper_replication='NOT_RUN',v1_lb3b='NOT_RUN',v1_lb3c='NOT_RUN',v1_lb3b_lb3c='NOT_RUN',v1_candidate='NOT_RUN',shiu_reference='NOT_ASSESSED',
            raw_weight=m['current_v1_all_body_weight'],normalized_weight='',effective_connectivity='',percentile='',paper_support='Figure 6I/J',
            dataset='male-cns:v1.0',dataset_version='v1.0',status='UNRESOLVED',difference_reason=m['probable_explanation'],
            notes='Raw weight is independent of any selected circuit version. Paper figure weight='+m['paper_displayed_weight']))
    csv_write(vroot/'version_comparison.csv',comparisons)
    (vroot/'README.md').write_text('# Circuit versions — readiness inventory\n\nNo effective-connectivity circuit has been selected. Each version has a separate definition. '
        'The comparison contains only twelve mapped reference motifs and current raw weights; it is not a full graph comparison. '
        'NOT_RUN and NOT_ASSESSED must never be interpreted as absence or failed selection. '
        'No node/edge recall or precision denominator can be inferred from this incomplete reference.\n')

    types={'LB3a','LB3b','LB3c','LB3d','MN4a','MN6','MN8','MN9','GNG042','ANXXX462a','GNG015','GNG021','GNG585','GNG108','GNG120','GNG472','GNG232','DNg67','DNge080'}
    evidence=[]
    for n in csv.DictReader((BASE/'nodes.csv').open()):
        if n['type'] not in types:continue
        typ=n['type']
        support='Figure 6 named type/alias; exact selected paper body not recovered'
        if typ in ['GNG232','DNg67']:support='S16A label; does not establish S16B-E or Figure 6G selection'
        if typ=='DNge080':support='S19 label/alias; does not establish Figure 6G selection'
        if typ=='GNG021':support='UNVERIFIED paper presence; absence not established'
        if typ.startswith('LB3') or typ in ['MN4a','MN6','MN8','MN9']:support='Figure 6G type; Table S1 body identity previously cross-checked'
        evidence.append(dict(body_id=n['body_id'],type=typ,alias=n['synonyms'],dataset=n['dataset'],paper_structural_support=support,
            current_v1_raw_support='STRUCTURALLY_PRESENT_IN_PRIOR_EXPORT',tastekin_v1_selection='NOT_RUN',lb3b_selection='NOT_RUN',lb3c_selection='NOT_RUN',combined_selection='NOT_RUN',
            gng021_candidate_status='INDIRECT_OVERLAPPING_STRUCTURAL_CANDIDATE; SELECTION_NOT_ASSESSED' if typ=='GNG021' else '',
            shiu_dynamic_support='',experimental_support='',raw_weight_summary='',effective_connectivity='',percentile='',motor_targets='',
            evidence_notes='Prior structural nodes.csv body/side/alias provenance; no dynamic/experimental source inferred from synonyms; side='+n['side'],confidence='Verified current record; method-selected/functional status unknown'))
    csv_write(ROOT/'results/cross_experiment/neuron_evidence_matrix.csv',evidence)

    gate=dict(status='BLOCKED_BEFORE_EXPERIMENT_1R',dataset_verified=True,method_verified=False,
        main_final_methods_recovered=False,official_implementation_recovered=False,
        effective_math_tests_passed=None,raw_weight_audit_tests_passed=True,
        paper_reference_complete=False,unresolved_weight_differences=8,
        experiment_01_allowed=False,experiment_02_allowed=False,simulation_allowed=False,
        threshold_tuning_allowed=False,frozen_implementation_commit=None,
        source_only_sugar_restriction=True,parameter_inventory=REL+'/method_parameters.csv')
    (ROOT/'config/method_readiness.json').write_text(json.dumps(gate,indent=2)+'\n')
    cfg=ROOT/'config/analysis.yaml';text=cfg.read_text().replace('stage: structural_connectivity_checkpoint','stage: method_recovery_blocked_before_experiment_01')
    text += f'\nlatest_method_audit: "{REL}"\nmethod_readiness: "config/method_readiness.json"\n'
    cfg.write_text(text)
    cfg=ROOT/'config/experiments/experiment_02_sugar_restricted.yaml'
    text=cfg.read_text().replace('restriction_definition: null','restriction_definition: "Change starting sensory bodies only; retain all other MaleCNS graph nodes and edges"')
    text += 'conditions:\n  lb3b_only: [LB3b]\n  lb3c_only: [LB3c]\n  lb3b_lb3c_combined: [LB3b, LB3c]\nmotor_targets: [MN4a, MN6, MN8, MN9]\nno_other_grn_relay_primary: false\nrequires_passed_experiment_01_checkpoint: true\n'
    cfg.write_text(text)

    claims=[]
    statements=[
        ('C056','Live authenticated Meta reconfirms male-cns:v1.0 UUID 4b2087c0fbe046bfaf0d60bc970e3e5d with unchanged mutation/edit metadata.',REL+'/meta_retry.json','RAW_DATA_CLAIM','VERIFIED'),
        ('C057','Re-fetched final supplemental PDF and Table S1 match the baseline SHA256 hashes. Full final Methods remain unavailable through retried publisher HTML/PDF and API routes.',REL+'/sources/','SOURCE_ACCESS_CLAIM','VERIFIED'),
        ('C058','Four of twelve mapped Figure 6 raw type-pair totals match current all-body weights; eight differ. This does not quantify algorithmic replication.',REL+'/weight_audit/paper_weight_comparison.csv','COMPUTATIONAL_RESULT','VERIFIED'),
        ('C059','None of the eight discrepant paper weights equals any subset sum of the current mapped positive raw body-pair weights; whole-body/whole-edge deletion plus additive pooling alone is excluded.',REL+'/weight_audit/subset_enumeration.json','COMPUTATIONAL_RESULT','VERIFIED'),
        ('C060','All-body weightHP matches zero of twelve mapped figure totals; weightHR matches four and equals raw weight for these motifs.',REL+'/weight_audit/paper_weight_comparison.csv','COMPUTATIONAL_RESULT','VERIFIED'),
        ('C061','The final supplement labels GNG232 and DNg67 in S16A and DNg67/Fudog and DNge080/Rounddown in S19; this does not establish their inclusion in the complete selected Figure 6G circuit.', 'paper/supplement/supplemental_information.pdf pp17,20','PAPER_CLAIM','VERIFIED'),
        ('C062','Main replication and sugar experiments did not run because selection-changing equations and rules remain unverified; no paper engine or selected-circuit result is asserted.', 'config/method_readiness.json','SCOPE_CLAIM','VERIFIED'),
        ('C063','Six hand-calculated tests of the raw subset/pooling audit pass. These are not effective-connectivity validation tests.', 'tests/test_weight_audit.py','COMPUTATIONAL_RESULT','VERIFIED'),
    ]
    for cid,claim,source,kind,status in statements:
        claims.append(dict(claim_id=cid,timestamp=STAMP,experiment=EXP,claim=claim,claim_type=kind,source_1=source,
            source_2='docs/effective_connectivity_and_sugar_checkpoint.md',dataset='male-cns:v1.0' if kind!='PAPER_CLAIM' else '',body_ids='',edge_ids='',
            support_level='bounded primary-source or deterministic audit evidence',verification_status=status,confidence='high within stated scope',
            notes='No selected circuit, dynamics or experimental validation inferred.',supersedes_claim_id=''))
    ledger('claim_ledger.csv',claims,'claim_id')
    mismatches=[]
    for i,m in enumerate(x for x in motifs if int(x['difference'])):
        mismatches.append(dict(mismatch_id=f'M{1275+i}',timestamp=STAMP,experiment=EXP,item=m['source_type']+'->'+m['target_type']+' pooling explanation follow-up',
            source_A='Final Figure 6I/J',value_A=m['paper_displayed_weight'],source_B=REL+'/weight_audit/subset_enumeration.json',value_B=m['current_v1_all_body_weight'],
            severity='paper/current numerical source conflict',possible_explanation=m['probable_explanation'],resolved='no',
            resolution='Whole-body/whole-raw-edge pruning alone excluded; historical M290-M297 preserved unresolved',related_claim_ids='C058;C059;C060',follow_up_required='Paper selected-body/source-weight table and snapshot/filter/pooling rules'))
    mismatches.append(dict(mismatch_id='M1283',timestamp=STAMP,experiment=EXP,item='Cross-literature candidate evidence scope',source_A='docs/prompt_1.md sections 3D/18',
        value_A='Track GNG232 and DNg67 in separate Shiu comparison',source_B='Final supplement S16A/S19',value_B='These names also occur in Tastekin supplemental material',
        severity='evidence-scope clarification',possible_explanation='Separate comparison versions should not erase overlapping published structural evidence',resolved='yes',
        resolution='Record Tastekin panel-specific support separately; do not infer selected-circuit membership or merge algorithms',related_claim_ids='C061',follow_up_required='Resolve complete published selected-node list'))
    ledger('mismatch_ledger.csv',mismatches,'mismatch_id')

    append(ROOT/'docs/prompt_vs_paper_audit.md',f'\n\n## {STAMP} — prompt_1.md follow-up\n\n'
        '- The 80th-percentile rule remains UNVERIFIED; prompt text alone is not a method source.\n'
        '- S16A explicitly labels GNG232 and DNg67; S19 labels DNg67/Fudog and DNge080/Rounddown. Preserve Tastekin structural-panel evidence alongside the separate, future Shiu comparison. This is not proof of Figure 6G selection. C061/M1283.\n'
        '- The eight mismatched Figure 6 labels cannot be reproduced by whole-body/whole-raw-edge deletion plus additive pooling using the current mapped counts. Snapshot, synapse filtering and other mapping/pooling remain unresolved. C059.\n'
        '- The prompt supplies no numeric acceptable-recall threshold. Do not invent one, tune weights, or treat four matching raw totals as a passed method gate.\n'
        '- Experiment 2 is explicitly source-only restriction. This resolves Q-016 without deleting other GRN relays. The final continuation instruction permits Experiment 2 only after a trustworthy Experiment 1R; that prerequisite is unmet.\n')
    append(ROOT/'logs/decision_log.md',f'\n\n## {STAMP} — Method recovery and weight audit\n\n'
        '### D016 — New authorization and scientific gate\n'
        '- QUESTION: Does the new prompt permit continuation beyond the structural checkpoint?\n'
        '- EVIDENCE: User explicitly requested prompt_1.md; its sections 4/7/12 require source recovery and mathematical validation before replication/extension.\n'
        '- OPTIONS: Implement inferred equations; recover sources; stop the dependent stage if sources remain missing.\n'
        '- DECISION: Authorization for the proposed experiments is present, superseding the prior session stop; the scientific method gate remains mandatory and currently fails.\n'
        '- WHY: Missing definitions materially affect node selection. No approval question is needed to implement a verified method later.\n'
        '- ALTERNATIVES REJECTED: Treating snippets, generic libraries or shortest paths as a validated algorithm.\n'
        '- CHANGE CONDITION: Readable final Methods and sufficient code/source-data definitions, followed by passing mathematics tests.\n\n'
        '### D017 — Bounded weight-explanation test\n'
        '- QUESTION: Can selecting current bodies/edges alone explain the figure discrepancies?\n'
        '- EVIDENCE: Twelve mapped figure labels and complete previously validated body-pair weights; input hashes match the frozen structural manifest.\n'
        '- OPTIONS: Fit a subset; enumerate all attainable sums without selecting a circuit; assume version changes.\n'
        '- DECISION: Enumerate all sums and body subsets only to exclude arithmetic explanations; do not adopt a best match.\n'
        '- WHY: All eight mismatches are impossible under simple unchanged-edge deletion/addition. This narrows causes without choosing an unknown method.\n'
        '- ALTERNATIVES REJECTED: Blaming proofreading or changing raw data without historical evidence.\n'
        '- CHANGE CONDITION: Recovered paper data establish another mapping, filtering or pooling rule.\n\n'
        '### D018 — Separate versions and paper evidence scopes\n'
        '- QUESTION: How to represent unrun experiments and overlapping literature evidence?\n'
        '- EVIDENCE: S16A/S19 include cross-literature candidate names, but no complete selected-node list is recovered.\n'
        '- OPTIONS: Empty selected graphs interpreted as absent; explicit readiness definitions and panel-specific reference support.\n'
        '- DECISION: Use NOT_RUN/NOT_ASSESSED and partial-reference labels, with blank effective/dynamic values. Keep seven versions separate.\n'
        '- WHY: Missing evidence is not failed selection. Q-016 is resolved to source-only restriction by the new user prompt.\n'
        '- ALTERNATIVES REJECTED: Calling every S16A label selected or giving unknown Puddle an inferred body ID.\n'
        '- CHANGE CONDITION: Verified source tables and successful experiment execution.\n')
    append(ROOT/'logs/unresolved_questions.md',f'\n\n## {STAMP} — Method gate recheck\n\n'
        '| ID | Current evidence and missing source | Status |\n| --- | --- | --- |\n'
        '| Q-003 | Final publisher HTML/PDF still 403; FULL API 401; author-linked final PDF 403. Supplement and Table S1 re-fetched unchanged. Need readable final Results/STAR Methods. | BLOCKED — SOURCE REQUIRED |\n'
        '| Q-004 | Public lab/author repository lists rechecked; no identified paper-specific analysis repository. Need official analysis scripts/version or fully explicit primary rules. | BLOCKED — SOURCE REQUIRED |\n'
        '| Q-005 | All eight mismatches cannot arise solely from current raw body/edge subsets. Need historical adjacency, selected bodies and figure-generation pooling. | UNRESOLVED; no cause assigned |\n'
        '| Q-012 | Parameter-by-parameter gaps saved in method_parameters.csv; no reconstructed mathematical assumptions adopted. | BLOCKED — SOURCE REQUIRED |\n'
        '| Q-013 | Puddle still unmapped. No graph-based identity assigned. | BLOCKED — SOURCE REQUIRED |\n'
        '| Q-016 | prompt_1.md explicitly defines starting-input-only restriction; config updated accordingly. | RESOLVED |\n'
        '| Q-017 | Full Figure 6G selected body/node/edge inventory, including Tentacular and unnamed nodes, not recovered. A partial named reference cannot support complete precision/recall. Need figure source tables/code. | OPEN |\n'
        '| Q-018 | S16A/S19 contain GNG232/DNg67/DNge080 labels; panel presence and selected-circuit membership must remain distinct. Need full selection output to determine overlap. | OPEN; panel presence verified |\n'
        '\nI am uncertain about the effective-connectivity and pruning equations because the complete final Methods and publication-specific implementation are unavailable. '
        'I am uncertain about the historical weight differences because arithmetic exclusions do not identify the paper snapshot, synapse filter, or pooling rule.\n')
    append(ROOT/'STATUS.md',f'\n\n## {STAMP} — Method recovery audited; stopped before Experiment 1R\n\n'
        '### COMPLETED\n\nRead prompt_1.md and required project context; rechecked final paper/correction/code access, re-fetched unchanged final supplement/Table S1, and authenticated live v1.0 identity. '
        'Added a reproducible twelve-motif weight audit with exhaustive subset tests and six passing hand-calculated arithmetic tests. Parameter inventory, circuit-version readiness records, partial evidence matrix and checkpoint reports are saved.\n\n'
        '### CURRENT FINDINGS\n\nFour of twelve mapped raw figure totals match; eight differ. No discrepant label equals any subset of current mapped raw body-pair counts. '
        'Body/whole-edge deletion and additive pooling alone cannot explain them. All-body weightHP matches zero labels; weightHR matches the same four as raw. Causes remain unresolved.\n\n'
        '### VERIFIED FACTS\n\nLive male-cns:v1.0 UUID unchanged. GNG232/DNg67 occur in final S16A, DNg67/Fudog and DNge080/Rounddown in S19; these are scoped paper appearances, not evidence of full-circuit selection. C056–C063.\n\n'
        '### UNVERIFIED ITEMS\n\nFinal full Methods, official implementation, selection-changing equations/threshold rules, snapshot, pooling, complete published reference and every method-selected/sugar circuit. '
        'No paper engine or effective mathematics tests were fabricated.\n\n'
        '### MISMATCHES\n\nM1275–M1282 add constraints to the unresolved M290–M297 weight differences; M1283 clarifies overlapping Tastekin/cross-literature panel evidence.\n\n'
        '### NEW QUESTIONS\n\nQ-017: full reference inventory/Tentacular mapping. Q-018: candidate panel presence versus actual selected circuit. Q-016 resolved to source-only input restriction.\n\n'
        f'### FILES CREATED\n\n`{REL}/`, `docs/paper_vs_v1_weight_audit.md`, `docs/experiment_01_replication_checkpoint.md`, '
        '`docs/effective_connectivity_and_sugar_checkpoint.md`, scripts 16–18, `tests/test_weight_audit.py`, `config/method_readiness.json`, version registry and evidence matrix.\n\n'
        '### NEXT ACTION\n\nObtain readable final Results/STAR Methods and publication-linked analysis/figure source data, resolve the parameter gaps, then implement/test one engine. '
        '**Experiment 1R NOT RUN; Experiment 2 NOT RUN; no simulation.** Dataset access is working; the blocker is scientific source completeness, not authorization.\n')
    append(ROOT/'SOURCES.md',f'\n\n## Method-recovery recheck — {STAMP}\n\n'
        f'New responses and hashes: `{REL}/sources/`, `logs/source_fetch_log.jsonl`; live dataset query: `{REL}/meta_retry.json` and `logs/query_log.jsonl`. '
        'The re-fetched final supplement/Table S1 are byte-identical to P02/P03. '
        'Crossref has no update-to or correction relation in this response; Europe PMC has no PMC full-text link and labels the DOI route subscription-required. This is bounded correction/access coverage. '
        'Public Ribeiro-lab and ibrahimtastekin repository inventories were rechecked; none is identified as this paper\'s analysis implementation. '
        'The [lab publications page](https://ribeirolab.org/publications/) links the final [extended PDF](https://www.cell.com/cell/pdfExtended/S0092-8674(26)00943-8), which returned 403. '
        'Final complete Methods remain unavailable. Search-index excerpts are discovery leads only; no equations were validated from them.\n')
    append(ROOT/'CHANGELOG.md',f'\n- {STAMP}: Continued prompt_1.md through source recovery and exhaustive raw-weight explanation audit; preserved failed method gate and unrun experiments.\n')
    (RUN/'checkpoint_recorded.json').write_text(json.dumps(dict(timestamp=STAMP,status='BLOCKED_BEFORE_EXPERIMENT_1R',claims=[r['claim_id'] for r in claims],mismatches=[r['mismatch_id'] for r in mismatches],evidence_rows=len(evidence)),indent=2)+'\n')
    print(json.dumps(dict(parameters=len(parameters),claims=len(claims),mismatches=len(mismatches),evidence_rows=len(evidence))))


if __name__=='__main__':
    main()
