"""One-time recording of recovered primary evidence and the tested partial core.

Preserves old audit directories and appends permanent ledgers. No biological
experiment, source download, simulation, or method freeze is performed here.
"""
import csv
import datetime as dt
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = Path('results/method_recovery/20261006T220302Z')
RUN = ROOT / REL
OLD = Path('results/method_recovery/20261006T214639Z')
STAMP = dt.datetime.now(dt.timezone.utc).isoformat()
FINAL = 'https://www.sciencedirect.com/science/article/abs/pii/S0092867426009438'
PREPRINT = 'https://www.biorxiv.org/content/early/2025/12/13/2025.08.25.671814.source.xml'
COMMIT = '94637d7d82920234ef0bfdbf383c000e74a8b45a'
REFERENCES = {}


def current_refs(text):
    return re.sub(r'\b(?:C\d{3}|M\d+|D\d{3}|Q-\d{3})\b', lambda m: REFERENCES.get(m[0], m[0]), text)


def write_json(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2) + '\n')


def append(path, text):
    with (ROOT / path).open('a') as f:
        f.write(current_refs(text))


def table(path, rows):
    with (ROOT / path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    assert not (RUN / 'checkpoint_recorded.json').exists(), 'Single-use recorder'
    assert not (RUN / 'manifest.json').exists()
    assert 'Ran 27 tests' in (RUN / 'tests.log').read_text() and '\nOK\n' in (RUN / 'tests.log').read_text()
    # Other authorized work may append to the shared ledgers. Allocate from
    # current maxima rather than assuming the previous run still owns the tail.
    claim_rows = list(csv.DictReader((ROOT/'logs/claim_ledger.csv').open()))
    mismatch_rows = list(csv.DictReader((ROOT/'logs/mismatch_ledger.csv').open()))
    first_claim = max(int(r['claim_id'][1:]) for r in claim_rows) + 1
    first_mismatch = max(int(r['mismatch_id'][1:]) for r in mismatch_rows) + 1
    first_decision = max(map(int, re.findall(r'\bD(\d{3})\b', (ROOT/'logs/decision_log.md').read_text()))) + 1
    first_question = max(map(int, re.findall(r'\bQ-(\d{3})\b', (ROOT/'logs/unresolved_questions.md').read_text()))) + 1
    REFERENCES.update({f'C{i:03}': f'C{first_claim+i-64:03}' for i in range(64, 76)})
    REFERENCES.update({f'M{i}': f'M{first_mismatch+i-1284}' for i in range(1284, 1287)})
    REFERENCES.update({f'D{i:03}': f'D{first_decision+i-19:03}' for i in range(19, 22)})
    REFERENCES['Q-019'] = f'Q-{first_question:03}'

    # Retain old parameter rows, replacing current knowledge and identifying
    # exact fields still unverified. Old table stays immutable in OLD.
    rows = list(csv.DictReader((ROOT / OLD / 'method_parameters.csv').open()))
    parameters = {r['parameter_name']: r for r in rows}
    for row in rows:
        row['source_pack_status'] = {'VERIFIED_FROM_FINAL_PAPER': 'FINAL_CELL_CONFIRMED',
            'VERIFIED_FROM_SUPPLEMENT': 'FINAL_SUPPLEMENT_CONFIRMED'}.get(row['verification_status'], 'UNVERIFIED')
        row['code_file'] = ''
        row['function_name'] = ''
    def update(name, value, section, notes='', status='VERIFIED_FROM_FINAL_PAPER', function='', critical=True):
        row = parameters[name] if name in parameters else {key: '' for key in rows[0]}
        row.update(parameter_name=name, exact_value_or_equation=value,
            source_document=str(REL / 'sources/indexed_final_methods_search2.txt'), section=section,
            page_or_figure='indexed final HTML; no PDF page', quote_or_precise_paraphrase=value,
            code_file='src/effective_connectivity.py' if function else '', function_name=function,
            verification_status=status, notes=notes, selection_critical=critical,
            source_pack_status='FINAL_CELL_CONFIRMED' if status=='VERIFIED_FROM_FINAL_PAPER' else 'UNVERIFIED')
        if name not in parameters:
            parameters[name] = row
            rows.append(row)
    ec = 'Effective connectivity algorithm'
    path = 'Calculating significant paths'
    bs = 'GRN-MN pairs with high effective connectivity'
    update('graph_neuron_universe', 'Neuron-pair all-by-all graph; exact eligible membership unresolved', ec,
           'Do not equate all released segment endpoints with neurons or borrow the proofread-only simulation graph.', 'PARTIAL')
    update('connectivity_matrix_orientation', 'Rows presynaptic; columns postsynaptic', ec, function='BodyGraph.from_edges')
    update('cleft_score_filter', '50', 'Connectomic partner analysis',
           'Final and preprint agree; equivalence to MaleCNS released minconf 0.5 is UNVERIFIED.')
    parameters['cleft_score_filter']['source_document'] = str(REL / 'sources/indexed_search5.txt')
    update('replication_synapse_weight_filter', 'No additional global EC edge-count cutoff recovered', 'Connectomic partner analysis',
           'Do not transfer 2/5-synapse clustering thresholds or cited-paper graph thresholds into EC.', 'UNVERIFIED')
    update('edge_weight_equation', 'W[i,j] = raw directed synapse count', ec, function='BodyGraph.from_edges')
    update('edge_normalization_denominator', 'P[i,j] = W[i,j] / total_input_synapses[j]', ec,
           'Denominator is not recomputed on the selected induced graph; graph/filter scope still unresolved.', function='BodyGraph.from_edges')
    update('effective_connectivity_equation', 'E(1)=P[source,:]; E(h+1)=E(h)P', ec,
           'Unsigned matrix multiplication; each source body retained separately in core.', function='BodyGraph.from_inputs;BodyGraph.to_outputs')
    update('multi_hop_aggregation', 'Separate exact-hop matrix products', ec,
           'Per-hop powers follow the described operation; no cumulative sum across h specified.', function='BodyGraph.from_inputs')
    update('layer_hop_normalization', 'score / mean(nonzero layer scores)', ec,
           'Reference axis/grouping with multiple populations remains UNVERIFIED; caller supplies reference.', function='nonzero_mean_scale')
    update('significant_path_hop_limit', 'UNVERIFIED for Figure 6G iteration', path,
           'Seven-hop heatmaps, four/five-hop plateaus, and three/four-hop motifs are distinct contexts.', 'UNVERIFIED')
    update('significant_path_percentile_80', '80th percentile toward outputs AND from original inputs', path,
           'Fixed threshold; no tuning. Preprint caption corroborates both directions.', function='two_stage_selection')
    update('percentile_population', 'UNVERIFIED: candidate/all-neuron, zero scores, body/type grouping', path,
           'Synthetic reference-population example changes membership with threshold percentile fixed.', 'UNVERIFIED')
    update('percentile_estimator_and_ties', 'Strict exceedance confirmed; quantile estimator UNVERIFIED', path,
           'Toy tests use explicit linear/higher estimators; neither declared paper default.', 'PARTIAL', 'above_percentile')
    update('selection_direction', 'Candidate-to-output filter; original-input-to-candidate pruning', path,
           'The latter retains the ORIGINAL input population, not just the previous selected layer.', function='two_stage_selection')
    update('pruning_iteration', 'Survivors become next inputs; desired-layer stopping', path,
           'Candidate expansion and direction-specific hop horizons not specified sufficiently to code.', 'PARTIAL')
    update('recurrence_handling', 'Matrix products include repeated-node walks algebraically', ec,
           'Mathematical consequence, not an explicit paper exclusion policy. Selection revisits unresolved.', 'PARTIAL', 'BodyGraph.from_inputs')
    update('bootstrap_replicates', '10000', bs, critical=False)
    update('bootstrap_grn_sample_size', '75 per replicate', bs, critical=False)
    update('bootstrap_random_neuron_sample_size', '1446 initial brain neurons; 75 per bootstrap replicate', bs, critical=False)
    update('bootstrap_sampling_universe_replacement', 'Per-MN GRN observations; bootstrap replacement=yes', bs,
           'Random control starts from brain neurons; exact eligible set and initial 1446 replacement policy unresolved.', 'PARTIAL', critical=False)
    update('bootstrap_ci_estimator_seed', 'Upper endpoint of 95% CI; estimator and seed UNVERIFIED', bs,
           'Do not silently equate this with NumPy q97.5 or choose a biological seed.', 'PARTIAL', critical=False)
    update('paper_body_vs_type_bilateral_pooling', 'Figures show cell types; numerical pooling order/operator UNVERIFIED', 'Figure 6G; S16',
           'Body-level multiplication and type-level display do not establish pooling semantics.', 'PARTIAL')
    update('paper_motif_extraction_rule', '3-4-hop motifs; top partners >99th percentile of total inputs at each layer', 'Feeding motor circuit Results',
           'Reference universe and counting/pooling unresolved; separate from Figure 6G 80th selection.', 'PARTIAL')
    parameters['paper_motif_extraction_rule']['source_document'] = str(REL / 'sources/indexed_search4.txt')
    update('neurotransmitter_in_metric', 'Synaptic sign excluded', 'Limitations of the study',
           'NT remains metadata; signed motif interpretation/simulation are separate.', function='BodyGraph.from_edges')
    parameters['neurotransmitter_in_metric']['source_document'] = str(REL / 'sources/indexed_search4.txt')
    update('candidate_to_output_horizon', 'UNVERIFIED at each iteration', path,
           'A fixed target horizon versus remaining total hops can select different candidates.', 'UNVERIFIED')
    update('original_input_pruning_horizon', 'UNVERIFIED at each iteration', path, status='UNVERIFIED')
    update('layer_mean_reference_axis', 'UNVERIFIED for multiple source/output bodies or types', ec, status='UNVERIFIED')
    update('initial_partner_rule', 'Top direct partners referenced to S16A; >99th percentile', 'Calculating significant paths; final S16A',
           'Synaptic-weight population, source pooling and estimator still need source code.', 'PARTIAL')
    update('selected_graph_edges', 'All-by-all induced adjacency of retained neurons', path,
           'Not only traversed feedforward edges; final display thresholds/pooling still unresolved.', function='BodyGraph.induced_raw')
    update('bootstrap_random_initial_replacement', 'UNVERIFIED', bs, status='UNVERIFIED', critical=False)
    update('paper_source_code_scope', 'Cited-method repository inspected; Tastekin implementation not recovered', 'Code availability / cited method',
           'Inspected five Rmd scripts and README at pinned commit ' + COMMIT + '; no proxy method imported.', 'UNVERIFIED')
    # Existing supplement-confirmed values are retained; partial display rules
    # and historical-snapshot fields stay unverified rather than guessed.
    confirmed_partial = {'graph_neuron_universe','percentile_estimator_and_ties','pruning_iteration',
        'bootstrap_sampling_universe_replacement','bootstrap_ci_estimator_seed','paper_body_vs_type_bilateral_pooling',
        'paper_motif_extraction_rule','initial_partner_rule'}
    for row in rows:
        if row['parameter_name'] in confirmed_partial:
            row['source_pack_status'] = 'FINAL_CELL_CONFIRMED'
            row['notes'] = 'Only the stated recovered portion is confirmed; unresolved subfields remain explicit. ' + row['notes']
    parameters['paper_body_vs_type_bilateral_pooling']['source_document'] = str(REL/'sources/indexed_search5.txt') + ';paper/supplement/mmc1_extracted.txt'
    parameters['initial_partner_rule']['source_document'] += ';paper/supplement/mmc1_extracted.txt'
    table(REL / 'method_parameters.csv', rows)

    diffs = [
        ('adjacency_normalization', 'W counts; P=W/T_post', 'same', 'FINAL_CELL_CONFIRMED', 'Agreement; filters/universe still unresolved'),
        ('propagation', 'serial matrix products', 'same', 'FINAL_CELL_CONFIRMED', 'Agreement'),
        ('layer_scaling', 'nonzero layer mean', 'same', 'FINAL_CELL_CONFIRMED', 'Grouping axis unresolved'),
        ('sign', 'explicitly excluded in Limitations', 'unsigned matrix method', 'FINAL_CELL_CONFIRMED', 'Keep NT as metadata'),
        ('initial_candidates', 'top downstream; S16A link', 'downstream without explicit S16A link', 'FINAL_CELL_CONFIRMED', 'Final clarifies; >99 criterion in final supplement'),
        ('output_threshold', '>80th percentile', '80th quantile', 'FINAL_CELL_CONFIRMED', 'Use final percentile wording'),
        ('input_pruning_threshold', '80th percentile explicit', 'Methods nonnumeric; Fig8G >80 for both directions', 'FINAL_CELL_CONFIRMED', 'No unresolved numerical conflict'),
        ('iteration', 'survivors become next inputs', 'same', 'FINAL_CELL_CONFIRMED', 'Exact candidate/horizon policy unresolved'),
        ('induced_graph', 'all-by-all retained neurons', 'same', 'FINAL_CELL_CONFIRMED', 'Agreement'),
        ('bootstrap', '10000; size75; replacement', 'dedicated Methods section absent', 'FINAL_CELL_CONFIRMED', 'Final addition'),
        ('random_control', '1446 brain neurons then bootstrap75', 'dedicated Methods section absent', 'FINAL_CELL_CONFIRMED', 'Initial sampling details unresolved'),
        ('confidence_interval', 'upper95% endpoint', 'dedicated Methods section absent', 'FINAL_CELL_CONFIRMED', 'Estimator unresolved'),
        ('cleft_filter', '50', '50', 'FINAL_CELL_CONFIRMED', 'MaleCNS confidence translation unresolved'),
        ('circuit_panel', 'Figure6G', 'Figure8G', 'FINAL_CELL_CONFIRMED', 'Renumbering; both type-level display'),
        ('clavicle_type', 'ANXXX462a', 'ANXXX462', 'SOURCE_CONFLICT', 'Final type specificity governs; broader label mapping not inferred'),
        ('identity_table', 'TableS1', 'SupplementalTable2', 'FINAL_CELL_CONFIRMED', 'Use validated final table'),
        ('simulation', 'separate Methods model', 'no corresponding Methods section', 'FINAL_CELL_CONFIRMED', 'Not executed; do not borrow its graph/sign policy'),
        ('official_implementation', 'not recovered', 'additional information on request', 'UNVERIFIED', 'Cited-method code is not Tastekin implementation'),
    ]
    table(REL / 'final_vs_preprint_method_diff.csv', [dict(parameter_name=p, final_cell=f, preprint_v2=b,
        source_pack_status=s, resolution=n, final_source=FINAL, preprint_source=PREPRINT,
        evidence='docs/final_vs_preprint_method_diff.md') for p, f, b, s, n in diffs])

    blockers = [
        dict(id='B01', detail='Graph neuron eligibility, synapse filtering and input-denominator universe; cleft50 mapping to MaleCNS'),
        dict(id='B02', detail='Source/target body-to-type and bilateral pooling, layer normalization reference axis'),
        dict(id='B03', detail='Initial99 and both80 percentile comparison populations, zeros and estimator'),
        dict(id='B04', detail='Candidate expansion, direction-specific hop horizons, Figure6G depth and revisits'),
    ]
    gate = json.loads((ROOT / 'config/method_readiness.json').read_text())
    gate.update(status='FINAL_METHOD_SECTIONS_RECOVERED_SELECTION_DETAILS_UNRESOLVED',
        main_final_methods_recovered=True, complete_final_document_recovered=False,
        final_methods_access_mode='indexed final HTML sections authorized by user source pack',
        preprint_v2_full_xml_recovered=True, final_vs_preprint_diff_completed=True,
        effective_math_tests_passed=True, effective_math_tests_count=21, total_tests_passed=27,
        method_verified=False, official_implementation_recovered=False,
        core_algebra_implemented=True, significant_path_iterator_implemented=False,
        bootstrap_ci_implemented=False, motif_selector_implemented=False,
        selection_blockers=blockers, parameter_inventory=str(REL / 'method_parameters.csv'),
        latest_method_audit=str(REL), dataset_metadata=str(REL / 'meta_start.json'),
        experiment_01_allowed=False, experiment_02_allowed=False, simulation_allowed=False,
        frozen_implementation_commit=None, method_frozen=False)
    write_json('config/method_readiness.json', gate)
    analysis = (ROOT / 'config/analysis.yaml').read_text()
    analysis = analysis.replace('stage: method_recovery_blocked_before_experiment_01', 'stage: core_math_validated_selection_rules_unresolved')
    analysis = analysis.replace('method_parameters: null', 'method_parameters: "' + str(REL / 'method_parameters.csv') + '"')
    analysis = analysis.replace(str(OLD), str(REL))
    analysis = analysis.replace('notes: "Checkpoint metadata only; there is no experiment runner. No paper-method defaults have been invented."',
        'notes: "Verified algebra core passes 21 tests; full selection iterator remains source-gated. No biological experiment runner or invented defaults."')
    (ROOT / 'config/analysis.yaml').write_text(analysis)

    # Source catalog: primary evidence, user instruction, and cited-code scope
    # are explicitly distinct. HTTP failure bodies are logged but not promoted.
    entries = [
        ('source_pack.md', None, 'User supplied source-recovery instructions; not primary scientific evidence'),
        ('sources/indexed_final_methods_search2.txt', FINAL, 'Indexed final Methods: EC, bootstrap, significant paths and reachability'),
        ('sources/indexed_search4.txt', FINAL, 'Indexed final Results and Limitations: motifs and unsigned metric'),
        ('sources/indexed_search5.txt', FINAL, 'Indexed final Figure6 legend and connectomic partner Methods'),
        ('sources/preprint_v2_response.xml', PREPRINT, 'Full bioRxiv v2 XML; DOI/version/date verified'),
        ('sources/biorxiv_metadata.json', 'https://api.biorxiv.org/details/biorxiv/10.1101/2025.08.25.671814', 'bioRxiv version metadata'),
        ('sources/cited_method_code_tree.json', 'https://api.github.com/repos/flyconnectome/2023neckconnective/git/trees/main?recursive=1', 'Cited Stuerner repository tree; not Tastekin code'),
    ]
    for name in ['1_Plot_DNs_across_datasets.Rmd', '2_FAFB_DNs.Rmd', '3_DNa02_downstream.Rmd', '4_Dimorphic_neuron_partners_manc.Rmd', '5_DN_nr_outputsynapses.Rmd', 'README']:
        entries.append(('sources/cited_' + name, f'https://raw.githubusercontent.com/flyconnectome/2023neckconnective/{COMMIT}/code/{name}',
                        'Pinned cited-method code inspected; does not implement Tastekin selection'))
    for filename in ['indexed_final_methods_search1.txt', 'indexed_search3.txt', 'indexed_search6.txt', 'indexed_search7.txt', 'indexed_search8.txt']:
        entries.append(('sources/' + filename, None, 'Saved search response; primary-source hits only; includes irrelevant hits not used'))
    source_manifest = json.loads((ROOT / 'config/source_manifest.yaml').read_text())
    first = max(int(s['source_id'][1:]) for s in source_manifest['sources']) + 1
    for number, (name, url, description) in enumerate(entries, first):
        p = RUN / name
        if any(s['path']==str(REL/name) for s in source_manifest['sources']):
            continue  # Resume after an earlier recording error without duplicate sources.
        entry = dict(source_id=f'P{number:02}', path=str(REL / name), url=url, description=description,
                     sha256=hashlib.sha256(p.read_bytes()).hexdigest(), bytes=p.stat().st_size,
                     audit_recorded_utc=STAMP)
        source_manifest['sources'].append(entry)
        if url:
            web_search = 'indexed_' in name
            append('logs/source_fetch_log.jsonl', json.dumps(dict(timestamp=STAMP,
                timestamp_scope='audit recording time; acquisition earlier in this run',
                experiment='METHOD_SOURCE_PACK_RECOVERY', purpose=description, url=url,
                parameters={}, returned_row_count=None, http_status=None if web_search else 200,
                transport='web search index' if web_search else 'direct curl',
                errors=None, output_file=str(REL / name), sha256=entry['sha256'])) + '\n')
    failures = [
        ('preprint_v2_response.bin', 'https://www.biorxiv.org/content/10.1101/2025.08.25.671814v2.full.pdf'),
        ('preprint_v2_response.html', 'https://www.biorxiv.org/content/10.1101/2025.08.25.671814v2.full'),
        ('preprint_supplement_landing.html', 'https://www.biorxiv.org/content/10.1101/2025.08.25.671814v2.supplementary-material'),
        ('preprint_supplement_response.pdf', None),
    ]
    for name, url in failures:
        p = RUN / 'sources' / name
        prior_fetches = [json.loads(line) for line in (ROOT/'logs/source_fetch_log.jsonl').read_text().splitlines() if line.strip()]
        if any(r.get('experiment')=='METHOD_SOURCE_PACK_RECOVERY' and r.get('output_file')==str(p.relative_to(ROOT)) for r in prior_fetches):
            continue
        append('logs/source_fetch_log.jsonl', json.dumps(dict(timestamp=STAMP, experiment='METHOD_SOURCE_PACK_RECOVERY',
            purpose='Preserve failed source retrieval; response is not scientific evidence; exact supplement media URL not retained' if url is None else 'Preserve failed source retrieval; response is not scientific evidence', url=url,
            parameters={}, http_status=429, errors='HTTP429; not a usable PDF/HTML source',
            output_file=str(p.relative_to(ROOT)), sha256=hashlib.sha256(p.read_bytes()).hexdigest())) + '\n')
    source_manifest.update(paper_full_text_status='RELEVANT_FINAL_METHODS_INDEXED; COMPLETE_FINAL_DOCUMENT_UNAVAILABLE',
                           preprint_full_text_status='V2_XML_RECOVERED', latest_method_audit=str(REL))
    write_json('config/source_manifest.yaml', source_manifest)

    claims = [
        ('Live metadata again confirms male-cns:v1.0 and UUID 4b2087c0fbe046bfaf0d60bc970e3e5d.', 'RAW_DATA_CLAIM', str(REL/'meta_start.json'), '', ''),
        ('Relevant final Cell Methods were recovered through its search index and full bioRxiv v2 XML was retrieved; the complete final PDF is still unavailable.', 'CORRECTION', 'P31;P32;P33;P34', 'Tastekin_methods_source_pack.md', 'C057'),
        ('The final method uses postsynaptic-input fractions and serial matrix products with nonzero layer-mean scaling; synaptic sign is excluded.', 'PAPER_CLAIM', 'P31;P32', 'P34', ''),
        ('Final significant-path Methods specify 80th-percentile output filtering and original-input pruning; initial top partners reference S16A, whose legend specifies >99th percentile.', 'PAPER_CLAIM', 'P31', 'P02 FigureS16', ''),
        ('Final GRN-MN control Methods specify 10000 replacement bootstrap samples of size75 and an initial random control of1446 brain neurons, using upper95% CI endpoints.', 'PAPER_CLAIM', 'P31', '', ''),
        ('The final/preprint diff distinguishes final-added bootstrap detail, clarified percentile wording, renumbering and unresolved implementation choices; no preprint-only rule was adopted.', 'SOURCE_AUDIT', str(REL/'final_vs_preprint_method_diff.csv'), 'docs/final_vs_preprint_method_diff.md', ''),
        ('The cited Stuerner repository tree and all five code Rmd scripts plus README were inspected at commit94637d7d82920234ef0bfdbf383c000e74a8b45a; they do not supply Tastekin significant-path code.', 'SOURCE_AUDIT', 'P36;P37;P38;P39;P40;P41;P42', '', ''),
        ('Twenty-one hand-calculated EC/threshold tests pass, along with six existing raw-weight tests; this validates the implemented algebra/helpers, not a complete replication selector.', 'COMPUTATIONAL_RESULT', str(REL/'tests.log'), 'src/effective_connectivity.py;tests/test_effective_connectivity.py;tests/test_thresholds.py', ''),
        ('Synthetic examples change retained candidates when the reference population, output pooling or target hop horizon changes, despite a fixed80th percentile.', 'COMPUTATIONAL_RESULT', str(REL/'selection_ambiguity_examples.json'), 'scripts/20_validate_ec_core.py', ''),
        ('Experiment1R and sugar selection remain unrun because graph/denominator scope, pooling, percentile references and iterative horizons remain unresolved. Core mathematics is now implemented; no method freeze or simulations.', 'SCOPE_CLAIM', 'config/method_readiness.json', 'docs/experiment_01_replication_checkpoint.md', 'C062'),
        ('Final Results specify Clavicle as ANXXX462a whereas preprint v2 uses ANXXX462; final specificity governs, without assuming broader-label equivalence.', 'CORRECTION', 'P32;P33', 'P34', ''),
        ('The indexed final motif Results give approximately48% alongside16/31;16/31 is about51.6%. This text/arithmetic discrepancy is retained without inferring a corrected biological count.', 'DISCREPANCY', 'P32', '16/31*100=51.61290322580645', ''),
    ]
    with (ROOT/'logs/claim_ledger.csv').open() as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; existing = list(reader)
    assert first_claim == max(int(r['claim_id'][1:]) for r in existing) + 1, 'Ledger changed during recording; stop before allocating IDs'
    with (ROOT/'logs/claim_ledger.csv').open('a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        for i, (claim, kind, s1, s2, supersedes) in enumerate(claims, first_claim):
            row = {field: '' for field in fields}
            row.update(claim_id=f'C{i:03}', timestamp=STAMP, experiment='METHOD_SOURCE_PACK_RECOVERY',
                claim=claim, claim_type=kind, source_1=s1, source_2=s2, dataset='male-cns:v1.0' if i==first_claim else '',
                support_level='Primary source or reproducible synthetic evidence; scope stated', verification_status='VERIFIED',
                confidence='high within evidence scope', notes='No biological selection or dynamics inferred.', supersedes_claim_id=supersedes)
            writer.writerow(row)
    mismatches = [
        ('Clavicle annotation granularity', 'bioRxivv2 Results', 'ANXXX462', 'Final Cell Results', 'ANXXX462a',
         'SOURCE CONFLICT; resolved by source priority', 'Final refines label; no unverified broad alias mapping.', 'yes', 'Use final ANXXX462a already validated in v1.0.', 'C074', 'None for final type; historical mapping requires source data'),
        ('Selection remains underdetermined after core-method recovery', 'Final Methods', 'Threshold values and matrix algebra specified', 'Synthetic audit', 'Reference/pooling/horizon choices change membership',
         'BLOCKED — SOURCE REQUIRED', 'Text lacks execution-level settings; no choice tuned to expected nodes.', 'no', 'Implement verified algebra only; keep replication disabled.', 'C072;C073', 'Figure6G/S16 function plus config and graph definition'),
        ('Disinhibitory motif percentage in indexed final Results', 'Final indexed text', 'approximately48%;16/31', 'Arithmetic', '16/31=51.61290322580645%',
         'SOURCE CONFLICT; indexed text/arithmetic', 'Possible text or indexing error; cause not established.', 'no', 'Preserve both; do not correct counts or rerun significance.', 'C075', 'Final page/figure source counts or correction'),
    ]
    with (ROOT/'logs/mismatch_ledger.csv').open() as f:
        reader = csv.DictReader(f); fields = reader.fieldnames; existing = list(reader)
    assert first_mismatch == max(int(r['mismatch_id'][1:]) for r in existing) + 1, 'Mismatch ledger changed during recording'
    with (ROOT/'logs/mismatch_ledger.csv').open('a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        for i, values in enumerate(mismatches, first_mismatch):
            row = dict(zip(fields[3:], values))
            row['related_claim_ids'] = current_refs(row['related_claim_ids'])
            row.update(mismatch_id=f'M{i}', timestamp=STAMP, experiment='METHOD_SOURCE_PACK_RECOVERY')
            writer.writerow(row)

    update = f'''\n\n## {STAMP} — Source-pack recovery and verified algebra core

Current status: **FINAL_METHOD_SECTIONS_RECOVERED_SELECTION_DETAILS_UNRESOLVED**. Earlier source-access statements above describe their dated checkpoints. The user source pack authorized indexed final text, which exposed the relevant Methods; the full preprint v2 XML was also recovered and compared. See [final/preprint audit](docs/final_vs_preprint_method_diff.md) and `results/method_recovery/20261006T220302Z/`.

The unsigned postsynaptic-normalized matrix core and explicit-reference threshold/pruning helpers are implemented. **27 tests pass: 21 new mathematical/helper tests plus six weight-audit tests.** Three synthetic comparisons establish that remaining reference-population, pooling and hop choices change candidate membership. These are not biological results.

Figure 6G graph eligibility/filter/denominator scope, score grouping/pooling, percentile reference populations/estimator and iterative hop/candidate policy still need primary definitions. Experiment 1R, all sugar conditions and simulation remain unrun. No method freeze, selected circuit or functional inference is claimed. The prior raw audit remains 4/12 exact and eight unexplained discrepancies. Live v1.0 UUID is unchanged. Claims C064–C075; mismatches M1284–M1286.
'''
    append('STATUS.md', update)
    append('docs/paper_method_reconstruction.md', update.replace('(docs/final_vs_preprint_method_diff.md)', '(final_vs_preprint_method_diff.md)') +
           '\nCurrent detailed parameter inventory: [48 parameter rows](../results/method_recovery/20261006T220302Z/method_parameters.csv). Recovered values and unresolved implementation fields are separated. Earlier tables remain historical.\n')
    append('docs/prompt_vs_paper_audit.md', f'''\n\n## {STAMP} — Final-text cross-check

Postsynaptic normalization, matrix propagation, both 80th-percentile criteria and unsigned effective connectivity are now CONFIRMED BY FINAL PAPER. Bootstrap constants are recovered from the final Methods; the preprint lacks that dedicated section. The source-pack anchors are independently confirmed, but source-pack text alone is not used as evidence. Complete significant-path execution rules remain PARTIALLY SUPPORTED. Seven-hop heatmaps do not establish a seven-hop Figure 6G iterator. Simulation-only proofread/sign settings do not establish EC graph filters. See [diff and implementation limits](final_vs_preprint_method_diff.md), C065–C073.
''')
    append('logs/decision_log.md', f'''\n\n## {STAMP} — Source-pack continuation

### D019 — Indexed final Methods and preprint comparison
The user explicitly supplied a pack permitting indexed final text. Independently recovered contiguous method sections outrank the preprint; verified v2 XML is a cross-check. Preprint-only details remain provisional. Final Clavicle specificity resolves the broader preprint annotation without inventing identity mappings. Earlier source failures remain in history.

### D020 — Implement verified mathematics without inventing a selector
Implement one body-level unsigned algebra core plus explicitly parameterized normalization/threshold/pruning helpers. Synthetic tests cover required mathematics and show that unresolved grouping/reference/horizon choices materially change membership. Linear quantiles in toys are an explicit test choice, not an attributed paper setting. No signed motif selector, bootstrap CI policy or iterative biological selector is asserted implemented.

### D021 — Scientific stop, not an authorization request
User authorization to run experiments persists. The prompt and AGENTS stop condition applies because B01–B04 are still unresolved and materially affect selection. Keep the experiments gated; the minimal missing source is Figure6G/S16 generating code/config plus graph-definition and pooling details. A full paper PDF is no longer the only way forward. Do not reuse simulation filters, tune toward named cells, or freeze the partial core as the published algorithm.
''')
    append('logs/unresolved_questions.md', f'''\n\n## {STAMP} — Current status supersedes earlier source-gap summaries

| ID | Updated evidence | Current state |
| --- | --- | --- |
| Q-003 | Relevant final Results/Methods recovered through index; full preprint v2 XML retrieved | PARTIALLY RESOLVED; complete final PDF unavailable, no longer the blanket blocker |
| Q-004 | Cited Stuerner repository inspected at pinned commit; not Tastekin selection code | Open; Figure6G/S16 function/config is the smallest useful source |
| Q-012 | Core equation, unsigned metric, both80 thresholds and bootstrap constants recovered | Partially resolved; B01–B04 in method_readiness.json remain selection-critical |
| Q-005 | Historical snapshot and figure pooling still unknown; prior subset audit unchanged | UNRESOLVED; eight raw differences |
| Q-013/Q-017 | Puddle/Tentacular and full published selected-node/edge table remain missing | UNRESOLVED; complete precision/recall unavailable |
| Q-019 | Indexed motif text reports48% and16/31 (51.6%) | SOURCE CONFLICT; verify source counts before enrichment replication |

I am uncertain about circuit membership because the percentile comparison populations, pooling order, graph/denominator universe and iterative hop policy remain unspecified. Three synthetic examples demonstrate the effect; this is not evidence that any particular biological neuron passes or fails. Bootstrap CI estimator/seed/initial sampling policy are separate remaining control-analysis gaps.
''')
    append('SOURCES.md', f'\n## Source-pack continuation — {STAMP}\n\nSources P30–P47 document user recovery guidance, independently indexed final Methods, verified preprint v2 XML, metadata, and pinned cited-method code. The latter is not a Tastekin implementation. See `config/source_manifest.yaml` for paths/hashes and [method diff](docs/final_vs_preprint_method_diff.md). Failed 429 responses remain labeled failures.\n')
    append('CHANGELOG.md', f'\n## {STAMP}\n\nRecovered final method sections and preprint v2 XML; added final/preprint diff and updated parameter inventory. Added tested unsigned body-level EC core and explicit-reference threshold/pruning helpers (21 new tests;27 total). Logged material selection ambiguities, retained scientific gates, and preserved prior weight-audit/structural runs.\n')
    write_json(REL / 'checkpoint_recorded.json', dict(timestamp=STAMP, parameter_rows=len(rows), diff_rows=len(diffs),
        claims_added=len(claims), mismatches_added=len(mismatches), sources_added=len(entries), allocated_ids=REFERENCES, status=gate['status']))
    print(json.dumps(dict(parameter_rows=len(rows), diff_rows=len(diffs), sources_added=len(entries), status=gate['status'])))


if __name__ == '__main__':
    main()
