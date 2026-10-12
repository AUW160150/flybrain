"""Read-only adapters for audited MaleCNS records. No circuit-selection algorithm."""
from pathlib import Path
import csv
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT / 'visualization'
DATASET = 'male-cns:v1.0'
UUID = '4b2087c0fbe046bfaf0d60bc970e3e5d'
LABELS = ['RAW STRUCTURAL', 'PAPER-ASSOCIATED', 'TASTEKIN-EFFECTIVE-CONNECTIVITY',
          'SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY', 'SHIU-CROSS-VALIDATION', 'CANDIDATE']
PALETTE = dict(LB3b='#56B4E9', LB3c='#009E73', sensory='#999999',
               second_order='#E69F00', higher_order='#CC79A7', premotor='#0072B2',
               motor='#D55E00', unknown='#BDBDBD')
SENSORY = ['LB3a', 'LB3b', 'LB3c', 'LB3d']
MOTORS = ['MN4a', 'MN6', 'MN8', 'MN9']
PAPER = ['GNG042', 'ANXXX462a', 'GNG015', 'GNG585', 'GNG108', 'GNG120', 'GNG472']
CANDIDATES = ['GNG042', 'GNG015', 'GNG021', 'GNG232', 'DNg67', 'DNge080']
ALIASES = dict(GNG042='Quasimodo', ANXXX462a='Clavicle', GNG585='Sternum',
               GNG108='Roundup', GNG120='Roundtree', GNG232='G2N-1',
               DNg67='Fudog', DNge080='Rounddown')
# Roles describe positions in the mapped Figure 6 motifs, never physiological sign.
ROLES = {'GNG042': 'second_order', 'ANXXX462a': 'second_order', 'GNG585': 'higher_order',
         **{t: 'premotor' for t in ['GNG015', 'GNG108', 'GNG120', 'GNG472']}}
ROLE_SOURCE = 'docs/structural_connectivity_checkpoint.md; paper/primary/figure6.jpg I/J; C037-C040'
SUPPORT_AUDIT = ROOT / 'results/method_recovery/20261006T214639Z/audit_snapshot_final/logs/claim_ledger.csv'
PANEL_SUPPORT = {'GNG232': 'S16A label; passage of selection criterion and Figure 6G membership UNVERIFIED',
                 'DNg67': 'S16A and S19 labels / Fudog; Figure 6G selection UNVERIFIED',
                 'DNge080': 'S19 label / Rounddown; Figure 6G selection UNVERIFIED'}
PANEL_SOURCE = 'paper/supplement/supplemental_information.pdf pp17,20; results/method_recovery/20261006T214639Z/audit_snapshot_final/logs/claim_ledger.csv C061'
CONDITIONS = ['lb3b_only', 'lb3c_only', 'lb3b_lb3c_combined']


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read_csv(path):
    with Path(path).open(newline='') as f:
        yield from csv.DictReader(f)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')


def write_csv(path, rows, fields=None):
    rows = list(rows)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v
                        for k, v in r.items()})


def width(value, maximum):
    """All raw views share this zero-anchored sqrt scale, in points/pixels."""
    if maximum <= 0 or value < 0:
        raise ValueError('Invalid width domain')
    return 0.7 + 4.3 * math.sqrt(value / maximum)


def load_selected(path, all_nodes, raw_edges):
    """Validate a future result contract; NEVER compute or infer selected membership."""
    if path is None:
        return dict(status='BLOCKED — VALIDATED RESULTS REQUIRED', conditions={},
                    algorithm=None, selected_intermediates=[], effective_edges=[])
    path = Path(path).resolve()
    obj = json.loads(path.read_text())
    if obj.get('schema_version') != 1 or obj.get('dataset') != DATASET or obj.get('dataset_uuid') != UUID:
        raise ValueError('Selected results require schema 1 and the exact v1.0 dataset/UUID')
    if obj.get('status') != 'VALIDATED' or obj.get('scientific_label') != LABELS[3]:
        raise ValueError('Unvalidated or mislabeled selected result')
    for key in ['algorithm_source', 'algorithm_version', 'method_source', 'selection_definition']:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f'Missing algorithm provenance: {key}')
    if not obj.get('artifacts') or not obj.get('validation_artifact'):
        raise ValueError('Hashed analysis artifacts and validation artifact are required')
    for rel, digest in obj['artifacts'].items():
        target = (path.parent / rel).resolve()
        if not target.is_relative_to(ROOT) or sha(target) != digest:
            raise ValueError('Analysis artifact missing, outside project, or hash mismatch')
    if obj['validation_artifact'] not in obj['artifacts']:
        raise ValueError('Validation artifact must be included in hashed artifacts')
    proof = json.loads((path.parent / obj['validation_artifact']).read_text())
    if (proof.get('status') != 'PASS' or proof.get('dataset') != DATASET or
            proof.get('dataset_uuid') != UUID or proof.get('algorithm_version') != obj['algorithm_version']):
        raise ValueError('Validation report must PASS for the same dataset, UUID and algorithm version')
    if set(obj.get('conditions', {})) != set(CONDITIONS):
        raise ValueError('Three independently validated conditions are required')
    for key, result in obj['conditions'].items():
        ids = result.get('node_ids', [])
        if len(set(ids)) != len(ids) or any(v not in all_nodes for v in ids):
            raise ValueError('Unknown or duplicate selected body IDs; extend the audited source first')
        if not result.get('provenance') or result.get('status') != 'VALIDATED':
            raise ValueError('Each condition requires provenance and VALIDATED status')
        expected = {v for v, n in all_nodes.items() if n['type'] in
                    ({'LB3b'} if key == CONDITIONS[0] else {'LB3c'} if key == CONDITIONS[1] else {'LB3b', 'LB3c'})}
        if set(result.get('input_body_ids', [])) != expected or not expected.issubset(ids):
            raise ValueError('Declared input population differs from verified LB3 population')
        seen = set()
        for e in result.get('edges', []):
            pair = (e['source'], e['target'])
            if pair in seen or not set(pair).issubset(ids):
                raise ValueError('Duplicate edge or endpoint outside selected membership')
            seen.add(pair)
            if pair not in raw_edges or e.get('raw_synapse_count') != raw_edges[pair]['raw_synapse_count']:
                raise ValueError('Selected edge raw weight must match an audited body-edge record')
            score = e.get('effective_connectivity_score')
            if isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) or score < 0:
                raise ValueError('A distinct finite nonnegative effective score is required')
            if not e.get('provenance'):
                raise ValueError('Effective edge requires score provenance')
    obj['source_file'] = str(path.relative_to(ROOT))
    obj['source_sha256'] = sha(path)
    return obj


def build_model(run, selected_path=None):
    meta = json.loads((run / 'raw/meta_start.json').read_text())
    vals = dict(zip(meta['columns'], meta['data'][0]))
    end = json.loads((run / 'raw/meta_end.json').read_text())
    end_vals = dict(zip(end['columns'], end['data'][0]))
    if (vals['dataset'] + ':' + vals['tag'] != DATASET or vals['uuid'] != UUID or
            any(end_vals.get(k) != value for k, value in vals.items())):
        raise ValueError('Cached source dataset guard failed')
    if json.loads((run / 'validation_checks.json').read_text())['status'] != 'PASS':
        raise ValueError('Structural source validation has not passed')
    all_nodes = {r['body_id']: r for r in read_csv(run / 'nodes.csv')}
    audit_claim = next((r for r in read_csv(SUPPORT_AUDIT) if r['claim_id']=='C061'), None)
    if not audit_claim or audit_claim['verification_status']!='VERIFIED':
        raise ValueError('Supplementary candidate paper support requires the frozen verified C061 audit')
    allowed_types = set(SENSORY + MOTORS + PAPER + CANDIDATES)
    allowed = {v for v, n in all_nodes.items() if n['type'] in allowed_types}
    # A future adapter may expand the small view only with explicitly validated results.
    if selected_path:
        draft = json.loads(Path(selected_path).read_text())
        allowed.update(v for c in draft.get('conditions', {}).values() for v in c.get('node_ids', []))
    if len(allowed) > 500:
        raise ValueError('Display/anatomy safety cap: 500 bodies; split the requested view explicitly')
    paper_pairs = set()
    for route in read_csv(run / 'paper_associated_paths.csv'):
        ids = [str(v) for v in json.loads(route['body_ids'])]
        paper_pairs.update(zip(ids, ids[1:]))
    totals = {v: dict(incoming=0, outgoing=0) for v in allowed}
    edges = []
    for r in read_csv(run / 'raw_edges.csv'):
        a, b, w = r['source'], r['target'], int(r['weight'])
        if a in allowed:
            totals[a]['outgoing'] += w
        if b in allowed:
            totals[b]['incoming'] += w
        if a not in allowed or b not in allowed:
            continue
        if r['dataset'] != DATASET or r['dataset_uuid'] != UUID or r['verification_status'] != 'VERIFIED':
            raise ValueError('Edge dataset or source validation failed')
        edges.append(dict(source=a, target=b, raw_synapse_count=w, effective_connectivity_score=None,
                          scientific_label=LABELS[0], evidence=['R'], paper_associated=(a, b) in paper_pairs,
                          source_type=r['source_type'], target_type=r['target_type'],
                          side_relationship=r['side_relationship'], recurrence_status=r['recurrence_status'],
                          query_provenance=str(run.relative_to(ROOT)) + '/' + r['query_provenance'],
                          source_file=str((run / 'raw_edges.csv').relative_to(ROOT)),
                          flat_provenance=r['flat_provenance'], verification_status=r['verification_status'],
                          anatomical_midline_crossing='UNVERIFIED — endpoint sides do not locate a crossing'))
    edge_map = {(e['source'], e['target']): e for e in edges}
    selected = load_selected(selected_path, all_nodes, edge_map)
    nodes = []
    for v in sorted(allowed, key=int):
        r = all_nodes[v]
        if r['dataset'] != DATASET or r['dataset_uuid'] != UUID:
            raise ValueError('Node dataset mismatch')
        t = r['type']
        alias = ALIASES.get(t, '')
        if alias and alias.lower() not in r['synonyms'].lower():
            raise ValueError(f'Alias mapping is not supported for {v}')
        role = 'sensory' if t in SENSORY else 'motor' if t in MOTORS else ROLES.get(t, 'unknown')
        counterpart = t in SENSORY + MOTORS + PAPER
        paper = counterpart or t in PANEL_SUPPORT
        conditions = [c for c, result in selected.get('conditions', {}).items() if v in result['node_ids']]
        n = dict(body_id=v, type=t, aliases=r['synonyms'], display_alias=alias,
                 side=r['side'] or 'unknown', side_source=r['side_source'], soma_side=r['soma_side'],
                 root_side=r['root_side'], role=role, role_source=ROLE_SOURCE if t in ROLES else
                 r['annotation_provenance'] if role != 'unknown' else 'UNVERIFIED biological order; supplied superclass retained',
                 superclass=r['superclass'], color=PALETTE.get(t, PALETTE[role]),
                 candidate=t in CANDIDATES, paper_counterpart=counterpart,
                 evidence=['R'] + (['P'] if paper else []) + (['E'] if conditions else []),
                 predicted_neurotransmitter=r['predicted_neurotransmitter'] or 'unknown',
                 consensus_neurotransmitter=r['consensus_nt'] or 'unknown', nt_confidence=r['predicted_nt_confidence'],
                 paper_status=PANEL_SUPPORT[t] if t in PANEL_SUPPORT else 'Verified input/target or named current counterpart in inspected Figure 6/S16/S17; exact paper-selected body inventory not recovered' if counterpart else
                 'UNVERIFIED in inspected Tastekin circuit; annotation alias is not paper selection',
                 effective_connectivity_status='VALIDATED: ' + ', '.join(conditions) if conditions else 'NOT ASSESSED — no validated selection result for this body',
                 shiu_status='UNVERIFIED — alias provenance is not dynamic/Shiu cross-validation',
                 experimental_status='UNVERIFIED — no body-mapped experimental evidence ingested',
                 evidence_sources=dict(R=str((run / 'nodes.csv').relative_to(ROOT)),
                                      **({'P': PANEL_SOURCE if t in PANEL_SUPPORT else ROLE_SOURCE + '; docs/initial_validation_checkpoint.md; C006-C008,C013,C020-C021'} if paper else {}),
                                      **({'E': selected['source_file']} if conditions else {})),
                 raw_export_incoming_weight=totals[v]['incoming'], raw_export_outgoing_weight=totals[v]['outgoing'],
                 weight_scope='sum over frozen raw_edges.csv export; not asserted whole-connectome totals',
                 source_file=str((run / 'nodes.csv').relative_to(ROOT)),
                 annotation_provenance=r['annotation_provenance'], nt_provenance=r['nt_provenance'],
                 dataset=DATASET, dataset_uuid=UUID)
        nodes.append(n)
    return dict(schema_version=1, dataset=DATASET, dataset_uuid=UUID,
                dataset_verification='cached authenticated start/end metadata from frozen structural run; no live analysis run',
                source_run=str(run.relative_to(ROOT)), labels=LABELS, palette=PALETTE,
                nodes=nodes, edges=edges, selected_results=selected,
                paper_comparisons=list(read_csv(run / 'paper_motif_comparison.csv')),
                unresolved=[dict(name='Puddle', status='UNRESOLVED', body_id=None,
                                 reason='BLOCKED — authoritative body/type mapping required; Q-013, C040, M298')],
                limitations=['Raw structure is not the biologically selected sugar pathway.',
                             'No physiological sign is assigned to arrows.',
                             'PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION',
                             'Opposite-side endpoints do not establish an anatomical midline crossing.',
                             'Pooled paper/current differences and unknown paper snapshot prevent strict replication.'])
