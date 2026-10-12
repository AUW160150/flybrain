"""Artifact checks that enforce the scientific display boundaries."""
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import networkx as nx
from PIL import Image
from model import ROOT, VIZ, DATASET, UUID, PAPER, SENSORY, MOTORS, read_csv, sha, write_json


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-id');a=p.parse_args()
    run_id=a.run_id or (VIZ/'data/current_run.txt').read_text().strip()
    data=VIZ/'data'/run_id;model=json.loads((data/'model.json').read_text());manifest=json.loads((data/'build_manifest.json').read_text())
    assert model['dataset']==DATASET and model['dataset_uuid']==UUID
    nodes={n['body_id']:n for n in model['nodes']};edges={(e['source'],e['target']):e for e in model['edges']}
    assert len(nodes)==len(model['nodes']) and len(edges)==len(model['edges'])
    assert len(nodes)<=500
    assert all(a in nodes and b in nodes for a,b in edges)
    assert all(n['dataset']==DATASET and n['dataset_uuid']==UUID for n in nodes.values())
    assert all('Puddle' not in n['type'] and 'Puddle' not in n['display_alias'] for n in nodes.values())
    assert model['unresolved'][0]['body_id'] is None and model['unresolved'][0]['status']=='UNRESOLVED'
    for name,digest in manifest['input_sha256'].items():assert sha(ROOT/name)==digest, 'Input changed: '+name
    for name,digest in manifest['code_sha256'].items():assert sha(ROOT/name)==digest, 'Implementation changed: '+name
    for name,digest in manifest['output_sha256'].items():assert sha(ROOT/name)==digest, 'Output changed: '+name
    source=ROOT/model['source_run'];seen=set()
    for r in read_csv(source/'raw_edges.csv'):
        pair=r['source'],r['target']
        if pair in edges:
            assert edges[pair]['raw_synapse_count']==int(r['weight'])
            assert r['verification_status']=='VERIFIED';seen.add(pair)
    assert seen==set(edges)
    source_nodes={r['body_id']:r for r in read_csv(source/'nodes.csv') if r['body_id'] in nodes}
    for v,n in nodes.items():
        r=source_nodes[v]
        assert n['side']==(r['side'] or 'unknown') and n['type']==r['type']
        assert n['predicted_neurotransmitter']==(r['predicted_neurotransmitter'] or 'unknown')
        assert n['consensus_neurotransmitter']==(r['consensus_nt'] or 'unknown')
        assert set(n['evidence']).issubset(n['evidence_sources'])
        assert not set(n['evidence'])&{'D','X'}
        if n['type'] in ['GNG232','DNg67','DNge080']:
            assert 'P' in n['evidence'] and not n['paper_counterpart']
            assert 'C061' in n['evidence_sources']['P']
        if n['type']=='GNG021':assert 'P' not in n['evidence']
    paper_pairs=set()
    for route in read_csv(source/'paper_associated_paths.csv'):
        ids=[str(v) for v in json.loads(route['body_ids'])];paper_pairs.update(zip(ids,ids[1:]))
    assert {p for p,e in edges.items() if e['paper_associated']}==paper_pairs
    if model['selected_results']['status']!='VALIDATED':
        assert not model['selected_results']['conditions']
        assert all('E' not in n['evidence'] for n in nodes.values())
        assert all(e['effective_connectivity_score'] is None for e in edges.values())
        assert not list((VIZ/'graph'/run_id).glob('selected_*'))
    graphs=[]
    for record in manifest['graph_exports']:
        for ext,reader in [('graphml',nx.read_graphml),('gexf',nx.read_gexf)]:
            g=reader(VIZ/'graph'/run_id/(record['name']+'.'+ext))
            assert g.is_directed() and len(g)==record['nodes'] and g.number_of_edges()==record['edges']
            for v,n in g.nodes(data=True):assert n['body_id']==v and n['side']==nodes[v]['side']
            for u,v,e in g.edges(data=True):assert int(e['raw_synapse_count'])==edges[u,v]['raw_synapse_count'] and e['weight']==edges[u,v]['raw_synapse_count']
            graphs.append(record['name']+'.'+ext)
    pngs=[]
    for directory in ['static','anatomy']:
        for path in (VIZ/directory/run_id).glob('*.png'):
            with Image.open(path) as im:
                assert min(im.info.get('dpi',(0,0)))>=300
                assert min(im.size)>1500
                pngs.append(dict(file=str(path.relative_to(ROOT)),pixels=im.size,dpi=im.info['dpi']))
        for path in (VIZ/directory/run_id).glob('*.svg'):
            tree=ET.parse(path)
            text=' '.join(tree.getroot().itertext())
            assert any(label in text for label in model['labels']),path
    html=(VIZ/'interactive'/run_id/'index.html').read_text()
    assert '/*__' not in html and '__RUN__' not in html
    assert all(t in html for t in ['LB3b','LB3c','GNG042','GNG015','GNG021','GNG232','DNg67','DNge080','MN4a','MN6','MN8','MN9'])
    anatomy=json.loads((VIZ/'anatomy'/run_id/'anatomy.json').read_text())
    assert all(m['body_id'] in nodes for m in anatomy['morphologies'])
    if anatomy['status']=='BLOCKED':assert not anatomy['morphologies']
    if model['selected_results']['status']!='VALIDATED':assert not anatomy['groups']['selected_downstream']['ids']
    result=dict(status='PASS',dataset=DATASET,bodies=len(nodes),edges=len(edges),paper_edges=len(paper_pairs),
                frozen_input_hashes_verified=len(manifest['input_sha256']),output_hashes_verified=len(manifest['output_sha256']),
                graph_roundtrips=graphs,png_checks=pngs,anatomy_status=anatomy['status'],
                checks=['exact raw-weight/source join','paper-route edge union','side and both NT fields preserved',
                        'no guessed Puddle identity','no premature E/D/X badges or selected graph',
                        'directed GraphML and GEXF body/weight roundtrip','SVG scientific labels','PNG >=300 DPI',
                        'source results unchanged','anatomy fail-closed state'])
    write_json(data/'validation.json',result);print(json.dumps(result,indent=2))


if __name__=='__main__':main()
