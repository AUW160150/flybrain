"""Export readable direct/indirect structural tables from frozen validated data.

This is a descriptive report, not paper-method selection. No database query or
new live-data claim is made. Every input is checked against its saved manifest.
"""
from collections import Counter, defaultdict, deque
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
STRUCT = ROOT / 'results/structural/20261006T180116Z'
VIEW = ROOT / 'visualization/data/20261006T221533490089Z'
TYPES = ['LB3a','LB3b','LB3c','LB3d','GNG042','ANXXX462a','GNG015','GNG021',
         'GNG585','GNG108','GNG120','GNG472','GNG232','DNg67','DNge080','MN4a','MN6','MN8','MN9']
UUID = '4b2087c0fbe046bfaf0d60bc970e3e5d'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields=None):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def indirect_witness(adj, source, target, bound=4):
    """Shortest >=2-edge vertex-simple path; direct edge is excluded.

    In a simple source-to-target path of >=2 edges, source->target cannot
    appear. Removing that edge lets ordinary BFS find the shortest indirect
    alternative, even for body pairs that also have a direct connection.
    """
    queue = deque([(source, (source,))])
    visited = {source}
    while queue:
        body, path = queue.popleft()
        if len(path)-1 >= bound:
            continue
        for other in adj[body]:
            if body == source and other == target:
                continue
            if other in visited:
                continue
            candidate = path + (other,)
            if other == target:
                return candidate
            visited.add(other)
            queue.append((other, candidate))
    return None


def main():
    stamp = dt.datetime.now(dt.timezone.utc)
    out = ROOT / 'results/connection_tables' / stamp.strftime('%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True, exist_ok=False)
    structural_manifest = json.loads((STRUCT/'manifest.json').read_text())
    view_manifest = json.loads((VIEW/'build_manifest.json').read_text())
    expected = {r['path']: r['sha256'] for r in structural_manifest['output_files']}
    expected.update(view_manifest['output_sha256'])
    inputs = [STRUCT/name for name in ['nodes.csv','raw_edges.csv','source_target_reachability.csv',
        'circuit_summary.csv','bounded_circuit_growth.csv','dataset_identity.json','search_config.json']]
    inputs += [VIEW/'nodes.csv',VIEW/'edges.csv']
    input_records = []
    for path in inputs:
        relative = str(path.relative_to(ROOT))
        actual = digest(path)
        assert actual == expected[relative], f'Frozen input changed: {relative}'
        input_records.append(dict(path=relative, sha256=actual))
    identity = json.loads((STRUCT/'dataset_identity.json').read_text())
    assert identity['dataset']=='male-cns' and identity['tag']=='v1.0' and identity['uuid']==UUID
    named = {int(r['body_id']): r for r in read_csv(VIEW/'nodes.csv')}
    assert len(named)==110 and set(r['type'] for r in named.values())==set(TYPES)
    type_bodies = {t: sorted(b for b, r in named.items() if r['type']==t) for t in TYPES}
    def label(body):
        r = named[body]
        alias = f"/{r['display_alias']}" if r['display_alias'] else ''
        return f"{r['type']}{alias} {r['side'] or '?'} [{body}]"
    def type_label(t):
        alias = named[type_bodies[t][0]]['display_alias']
        return t + (f' ({alias})' if alias else '')
    def key(body):
        r = named[body]
        return TYPES.index(r['type']), r['side'], body
    bodies = sorted(named, key=key)
    weights = {(int(r['source']),int(r['target'])): int(r['raw_synapse_count']) for r in read_csv(VIEW/'edges.csv')}
    assert len(weights)==1923 and all(w>0 for w in weights.values())
    adj = {b: sorted(t for s,t in weights if s==b) for b in bodies}
    direct_types = Counter()
    direct_type_pairs = Counter()
    for (source,target), weight in weights.items():
        pair = (named[source]['type'],named[target]['type'])
        direct_types[pair] += weight
        direct_type_pairs[pair] += 1
    pairs = []
    indirect_types = defaultdict(list)
    route_examples = []
    for source in bodies:
        for target in bodies:
            if source == target:
                continue  # Self-loops remain in the direct edge list; cycles are not indirect paths here.
            route = indirect_witness(adj, source, target)
            if route:
                assert 2 <= len(route)-1 <= 4 and len(set(route))==len(route)
                assert all((a,b) in weights for a,b in zip(route,route[1:]))
                indirect_types[named[source]['type'], named[target]['type']].append(len(route)-1)
            row = dict(source=source,source_label=label(source),target=target,target_label=label(target),
                direct_synapses=weights.get((source,target),0),
                indirect_within_4_hops=bool(route), shortest_indirect_hops=len(route)-1 if route else '',
                example_body_ids=' -> '.join(map(str,route)) if route else '',
                example_route=' -> '.join(map(label,route)) if route else '',
                example_edge_synapses=';'.join(str(weights[a,b]) for a,b in zip(route,route[1:])) if route else '',
                scope='110 tracked bodies only; indirect=2-4 edges; example not strongest route')
            pairs.append(row)
            if route and named[source]['type'] in ['LB3b','LB3c'] and named[target]['type'].startswith('MN'):
                route_examples.append(row)
    assert len(pairs)==110*109
    write_csv(out/'tracked_body_pairs_direct_and_indirect.csv',pairs)
    write_csv(out/'tracked_neurons.csv',[dict(body_id=b,type=named[b]['type'],alias=named[b]['display_alias'],
        side=named[b]['side'],role=named[b]['role']) for b in bodies])
    edges = [dict(source=s,source_label=label(s),target=t,target_label=label(t),raw_synapses=weights[s,t],
                  scope='Direct edges among 110 tracked bodies') for s in bodies for t in sorted(adj[s],key=key)]
    write_csv(out/'tracked_direct_edges.csv',edges)
    type_rows = []
    matrix = []
    for source in TYPES:
        row = {'source_type': source}
        for target in TYPES:
            raw = direct_types[source,target]
            paths = indirect_types[source,target]
            # A type diagonal may connect distinct bodies, not the same body.
            row[target] = (f'D{raw}' if raw else '') + ('+' if raw and paths else '') + (f'I{min(paths)}' if paths else '') or '-'
            type_rows.append(dict(source_type=source,target_type=target,direct_pooled_synapses=raw,
                direct_body_pairs=direct_type_pairs[source,target],
                body_pairs_with_indirect_route=len(paths),minimum_indirect_hops=min(paths) if paths else '',
                scope='Existential body-level routes in tracked view; do not chain type rows across mismatched bodies'))
        matrix.append(row)
    write_csv(out/'tracked_type_connection_matrix.csv',matrix)
    write_csv(out/'tracked_type_pair_details.csv',type_rows)

    # Streaming export of every body and direct edge belonging to the previously
    # exhaustive <=4-hop LB3a-d -> requested-motor path union (circuit A).
    node_fields = ['body_id','type','instance','side','annotation_present','classification','source_subtype_membership']
    broad_nodes = []
    with (STRUCT/'nodes.csv').open() as f:
        for row in csv.DictReader(f):
            if 'A' in row['circuit_membership'].split('|'):
                assert row['dataset_uuid']==UUID
                broad_nodes.append({field:row[field] for field in node_fields})
    write_csv(out/'all_lb3_motor_nodes_up_to_4_hops.csv',broad_nodes)
    broad_ids = {int(r['body_id']) for r in broad_nodes}
    edge_fields = ['source','source_type','source_side','target','target_type','target_side','weight',
                   'source_subtype_membership','minimum_bounded_path_hops','verification_status','query_provenance']
    broad_count, matched_named = 0, set()
    with (STRUCT/'raw_edges.csv').open() as source_file, (out/'all_lb3_motor_direct_edges_up_to_4_hops.csv').open('w',newline='') as dest:
        writer = csv.DictWriter(dest,fieldnames=edge_fields)
        writer.writeheader()
        for row in csv.DictReader(source_file):
            pair = (int(row['source']),int(row['target']))
            if pair in weights:
                assert weights[pair]==int(row['weight'])
                matched_named.add(pair)
            if 'A' not in row['circuit_membership'].split('|'):
                continue
            assert pair[0] in broad_ids and pair[1] in broad_ids
            assert row['verification_status']=='VERIFIED' and row['dataset_uuid']==UUID
            writer.writerow({field:row[field] for field in edge_fields})
            broad_count += 1
    assert len(matched_named)==len(weights)
    saved_summary = next(r for r in read_csv(STRUCT/'circuit_summary.csv') if r['circuit']=='A')
    assert len(broad_nodes)==int(saved_summary['nodes'])==23207
    assert broad_count==int(saved_summary['edges'])==354639
    reach = [r for r in read_csv(STRUCT/'source_target_reachability.csv') if r['analysis']=='sensory_to_motor']
    assert len(reach)==770
    write_csv(out/'all_lb3_motor_body_pair_reachability.csv',reach)
    growth = [r for r in read_csv(STRUCT/'bounded_circuit_growth.csv') if r['circuit']=='A']
    write_csv(out/'network_size_by_hop.csv',growth)
    counts = Counter()
    for row in reach:
        for hop in range(1,5):
            counts[hop] += int(row[f'simple_paths_h{hop}'])
    summary = dict(dataset='male-cns:v1.0',dataset_uuid=UUID,source_snapshot='2026-10-06',
        tracked_bodies=len(named),tracked_types=len(TYPES),tracked_direct_edges=len(weights),
        tracked_self_loops=sum(s==t for s,t in weights),tracked_ordered_distinct_pairs=len(pairs),
        tracked_pairs_with_direct_edge=sum(r['direct_synapses']>0 for r in pairs),
        tracked_pairs_with_indirect_2_to_4_hop_route=sum(r['indirect_within_4_hops'] for r in pairs),
        tracked_pairs_with_both=sum(bool(r['direct_synapses']) and r['indirect_within_4_hops'] for r in pairs),
        broad_nodes=len(broad_nodes),broad_edges=broad_count,
        broad_unannotated_nodes=sum(r['annotation_present']=='False' for r in broad_nodes),
        sensory_motor_pairs=len(reach),sensory_motor_direct_pairs=sum(int(r['direct_synapse_count'])>0 for r in reach),
        sensory_motor_reachable_pairs=sum(r['reachable']=='True' for r in reach),
        lb3_motor_simple_path_counts_by_exact_hop=dict(counts),hop_bound=4,
        indirect_examples_complete_path_listing=False,effective_connectivity=False)
    assert summary['broad_unannotated_nodes']==int(saved_summary['unannotated_nodes'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

    header = '''DIRECT AND INDIRECT STRUCTURAL CONNECTIONS
Saved male-cns:v1.0 records from 6 October 2026. This report does not query a newer release.

Direction matters: A -> B does not imply B -> A.
DIRECT = one edge, with a positive raw synapse count.
INDIRECT = a real body-level route through one or more intermediates (2-4 edges here).
A pair may have BOTH. Raw synapse counts are not activation strengths or effective connectivity.

The compact view contains the 110 tracked bodies in 19 types, including candidates.
It is not the paper-selected circuit. Its indirect routes use only these 110 bodies.
No route in this compact view does not establish absence from the whole connectome.
Type summaries pool raw counts for display; every indirect route is checked at body level.
Do not construct a route by joining type-level arrows that refer to different bodies.
Self-loops are retained as direct edges; indirect paths do not repeat bodies.
Puddle and Tentacular have no resolved body mapping and are not assigned invented IDs.

'''
    lines = [header, 'HOW MESSY IS IT?\n']
    lines.append('LB3a-d -> MN4a/MN6/MN8/MN9; complete saved path-union memberships within each bound:\n')
    lines.append(f"{'Maximum hops':<15}{'Bodies/segments':>18}{'Direct edges in union':>25}\n")
    for row in growth:
        lines.append(f"{row['max_hops']:<15}{int(row['nodes']):>18,}{int(row['edges']):>25,}\n")
    lines.append(f"\nAt four hops, {summary['broad_unannotated_nodes']:,} entries lack annotations; they are not all identified neurons.\n")
    lines.append(f"There are {sum(counts.values()):,} distinct simple LB3-to-motor body routes of up to four hops.\n")
    lines.append('The complete node/edge unions and all 770 sensory-to-motor pair counts are exported; the individual broad routes are too numerous for a useful text list.\n')
    lines.append(f"Among the 110 tracked bodies: {len(weights):,} direct edges; {summary['tracked_pairs_with_indirect_2_to_4_hop_route']:,} of {len(pairs):,} ordered distinct pairs have an indirect 2-4-hop route.\n")
    lines.append('This density is why an unfiltered wiring diagram becomes tangled. It does not mean every route carries sugar signals.\n\n')
    lines.append('START HERE: KEY INTERNEURONS, DIRECT INPUTS AND DIRECT MOTOR OUTPUTS\n')
    lines.append('Numbers are summed current raw synapses over tracked body pairs. Zero means no direct edge in the checked pairs.\n')
    lines.append(f"{'Type / alias':<29}{'Bodies':>7}{'LB3b->':>9}{'LB3c->':>9}{'->MN4a':>9}{'->MN6':>9}{'->MN8':>9}{'->MN9':>9}\n")
    for t in TYPES[4:15]:
        values=[len(type_bodies[t]),direct_types['LB3b',t],direct_types['LB3c',t],*(direct_types[t,m] for m in TYPES[15:])]
        lines.append(f'{type_label(t):<29}'+f'{values[0]:>7}'+''.join(f'{v:>9}' for v in values[1:])+'\n')
    lines.append('\nALL 19 TYPES: DIRECT AND INDIRECT TARGETS IN THE TRACKED VIEW\n')
    for t in TYPES:
        lines.append('\n'+type_label(t)+'\n')
        direct = '; '.join(f'{u} ({direct_types[t,u]} synapses)' for u in TYPES if direct_types[t,u]) or 'none'
        indirect = '; '.join(f'{u} ({min(indirect_types[t,u])} hops minimum)' for u in TYPES if indirect_types[t,u]) or 'none within 4 hops'
        lines.append(textwrap.fill('Direct -> '+direct,width=110,subsequent_indent='    ')+'\n')
        lines.append(textwrap.fill('Indirect -> '+indirect,width=110,subsequent_indent='    ')+'\n')
    lines.append('\nEXAMPLE BODY-RESOLVED INDIRECT ROUTES\nChosen by fewest hops then body IDs; not by synaptic strength or paper status.\n')
    for source_type in ['LB3b','LB3c']:
        for target_type in TYPES[15:]:
            choices=[r for r in route_examples if named[r['source']]['type']==source_type and named[r['target']]['type']==target_type]
            if choices:
                r=min(choices,key=lambda r:(r['shortest_indirect_hops'],r['source'],r['target']))
                lines.append(r['example_route']+'\n  Edge synapses: '+r['example_edge_synapses']+'\n')
    lines.append('\nALL TRACKED NEURONS\n')
    lines.extend(label(b)+'\n' for b in bodies)
    lines.append('''
FILES
connections_readable.txt: this compact summary and the full tracked-neuron inventory.
tracked_direct_connections.txt: every outgoing edge among the 110 tracked bodies.
tracked_indirect_connections.txt: one checked example for EVERY connected ordered pair at 2-4 hops in that view.
tracked_body_pairs_direct_and_indirect.csv: all 11,990 distinct ordered pairs, including pairs without a found indirect route.
tracked_type_connection_matrix.csv: 19x19 matrix; D<number>=raw direct synapses, I<number>=minimum indirect hops, +=both.
tracked_type_pair_details.csv: type summaries with body-pair counts. Type diagonals may involve different bodies.
tracked_neurons.csv / tracked_direct_edges.csv: sortable body-level tables.
all_lb3_motor_nodes_up_to_4_hops.csv: every body/segment in the broad saved path union.
all_lb3_motor_direct_edges_up_to_4_hops.csv: every constituent direct edge in that union.
all_lb3_motor_body_pair_reachability.csv: all 770 LB3-to-motor pairs, direct counts and exact path counts at 1/2/3/4 hops.
network_size_by_hop.csv: exact saved path-union sizes at each bound.
manifest.json: source/output hashes, bounds and checks.

Completeness: all tracked-body pairs within the stated view/bound are assessed;
all broad saved <=4-hop union nodes/edges are listed. This is not an all-brain
all-pairs connectivity catalog and does not enumerate infinitely repeatable
walks around cycles. No strength threshold or functional selection was added.
''')
    (out/'connections_readable.txt').write_text(''.join(lines))
    with (out/'tracked_direct_connections.txt').open('w') as f:
        f.write(header+'EVERY DIRECT EDGE IN THE TRACKED VIEW\n\n')
        for source in bodies:
            f.write(label(source)+'\n')
            for target in sorted(adj[source],key=key):
                f.write(f'  -> {label(target)} | {weights[source,target]} raw synapses\n')
            if not adj[source]:
                f.write('  No direct target within this view.\n')
            f.write('\n')
    with (out/'tracked_indirect_connections.txt').open('w') as f:
        f.write(header+'ONE SHORTEST INDIRECT EXAMPLE PER REACHABLE ORDERED PAIR\nAll connected pairs in this bounded view are included; additional routes are not enumerated.\n\n')
        last = None
        for row in pairs:
            if row['source'] != last:
                f.write('\nFROM '+row['source_label']+'\n')
                last = row['source']
            if row['indirect_within_4_hops']:
                f.write(f"  {row['example_route']} | hops={row['shortest_indirect_hops']} | edge synapses={row['example_edge_synapses']} | direct synapses={row['direct_synapses']}\n")
    checks = dict(frozen_input_hashes_verified=len(input_records),dataset_identity_verified=True,
                  tracked_edges_join_raw_export=True,all_indirect_witness_edges_verified=True,
                  all_indirect_witnesses_simple=True,all_ordered_tracked_pairs_assessed=True,
                  broad_node_edge_counts_match_frozen_summary=True,thresholds_added=False)
    manifest = dict(timestamp=stamp.isoformat(),purpose='Readable structural direct/indirect connection tables',
        dataset='male-cns:v1.0',dataset_uuid=UUID,offline_saved_snapshot=True,inputs=input_records,
        summary=summary,checks=checks,script=dict(path=str(Path(__file__).relative_to(ROOT)),sha256=digest(Path(__file__))),
        indirect_scope='2-4-edge vertex-simple paths restricted to the tracked 110 bodies; no same-body cycle queries',
        direct_type_pooling='sum raw weights over tracked body pairs; display aggregation only',
        broad_scope='exact saved LB3a-d-to-MN4a/MN6/MN8/MN9 path-union membership up to four hops',
        output_files=[dict(path=str(p.relative_to(ROOT)),sha256=digest(p),bytes=p.stat().st_size) for p in sorted(out.iterdir())])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Append references using current maxima; preserve records from other work.
    claim_path=ROOT/'logs/claim_ledger.csv'
    old_claims=read_csv(claim_path); fields=list(old_claims[0])
    next_id=max(int(r['claim_id'][1:]) for r in old_claims)+1
    claims=[
        f'The readable structural report covers all {len(pairs)} ordered distinct pairs among 110 tracked bodies: {len(weights)} direct edges and {summary["tracked_pairs_with_indirect_2_to_4_hop_route"]} pairs with an indirect 2-4-edge route restricted to those bodies.',
        f'The complete saved LB3a-d-to-requested-motor path union up to four hops contains {len(broad_nodes)} bodies/segments and {broad_count} edges; {summary["broad_unannotated_nodes"]} nodes lack annotations. This is raw structure, not selected circuitry.',
        f'The frozen sensory-to-motor records count {sum(counts.values())} simple paths of up to four hops across 770 body pairs. Counts and union membership are complete within the bound; the new text does not enumerate every broad route.',
    ]
    with claim_path.open('a',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields)
        for n,claim in enumerate(claims,next_id):
            row={field:'' for field in fields}
            row.update(claim_id=f'C{n:03}',timestamp=stamp.isoformat(),experiment='READABLE_STRUCTURAL_TABLES',claim=claim,
                claim_type='COMPUTATIONAL_RESULT',source_1=str((out/'manifest.json').relative_to(ROOT)),
                source_2=str((STRUCT/'manifest.json').relative_to(ROOT)),dataset='male-cns:v1.0',
                support_level='Frozen validated raw records and checked body-level routes',verification_status='VERIFIED',
                confidence='high within declared scope',notes='No functional or effective-selection inference.')
            w.writerow(row)
    decisions=ROOT/'logs/decision_log.md'
    decision=max(map(int,re.findall(r'\bD(\d{3})\b',decisions.read_text())))+1
    with decisions.open('a') as f:
        f.write(f'\n\n### D{decision:03} — Readable structural connection tables ({stamp.isoformat()})\n'
            'User requested a text/table of direct and indirect connections. Reuse hashed, dataset-verified saved records. '
            'Cover all ordered distinct pairs among the existing 110 tracked bodies; indirect routes are 2–4-hop simple paths with explicit body-resolved witnesses, including alternatives when a direct edge also exists. '
            'Export the complete broad four-hop LB3-to-motor node/edge union and existing exact endpoint path counts. '
            'Do not imply all-brain all-pairs completeness, combine incompatible type-level edges, impose a new biological strength threshold, or call structural routes effective selection. '
            f'Output: `{out.relative_to(ROOT)}`. Claims C{next_id:03}–C{next_id+len(claims)-1:03}.\n')
    with (ROOT/'STATUS.md').open('a') as f:
        f.write(f'\n### {stamp.isoformat()} — Readable direct/indirect connection tables\n\n'
            f'Created [{out.name} text summary]({(out/"connections_readable.txt").relative_to(ROOT)}) plus complete tracked-pair tables and broad four-hop union exports. '
            'Source hashes and route edges checked. Uses saved 6 October v1.0 data; no live refresh or paper-selection run. '
            f'Claims C{next_id:03}–C{next_id+len(claims)-1:03}; D{decision:03}.\n')
    with (ROOT/'logs/run_manifest.jsonl').open('a') as f:
        f.write(json.dumps(dict(timestamp=stamp.isoformat(),experiment='READABLE_STRUCTURAL_TABLES',
            run=str(out.relative_to(ROOT)),manifest_sha256=digest(out/'manifest.json')))+'\n')
    print(json.dumps(dict(output=str(out),summary=summary,checks=checks),indent=2))


if __name__=='__main__':
    main()
