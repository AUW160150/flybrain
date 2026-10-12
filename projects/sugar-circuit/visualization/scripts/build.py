"""Build immutable visualization artifacts from an existing audited structural run."""
import argparse
import datetime as dt
import importlib.metadata
import json
import platform
import subprocess
from pathlib import Path
import networkx as nx
from model import ROOT, VIZ, DATASET, UUID, SENSORY, PAPER, MOTORS, SUPPORT_AUDIT, build_model, write_json, write_csv, sha
from figures import render_all
from anatomy import render_anatomy
from fetch_skeletons import fetch


def graph_exports(model,out):
    nodes=model['nodes'];edges=model['edges'];byid={n['body_id']:n for n in nodes}
    scopes=[('raw_focused','RAW STRUCTURAL',nodes,edges),
            ('paper_associated','PAPER-ASSOCIATED',[n for n in nodes if n['type'] in SENSORY+PAPER+MOTORS],[e for e in edges if e['paper_associated']]),
            ('candidate_comparison','CANDIDATE',[n for n in nodes if n['candidate']],[])]
    for condition,result in model['selected_results'].get('conditions',{}).items():
        scopes.append(('selected_'+condition,'SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY',[byid[v] for v in result['node_ids']],result['edges']))
    def flatten(row):
        return {k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else ('UNAVAILABLE' if v is None else v) for k,v in row.items()}
    records=[]
    for name,label,ns,es in scopes:
        graph=nx.DiGraph(name=label)
        graph.graph.update(dataset=DATASET,dataset_uuid=UUID,scientific_label=label,
                           interpretation='Display derivative only; raw counts are not selected sugar membership or physiology',
                           source_run=model['source_run'])
        for n in ns:graph.add_node(n['body_id'],**flatten(n))
        for e in es:
            row=flatten(e);row['weight']=e['raw_synapse_count'];row['weight_semantics']='raw synapse count'
            graph.add_edge(e['source'],e['target'],**row)
        nx.write_graphml(graph,out/(name+'.graphml'))
        nx.write_gexf(graph,out/(name+'.gexf'))
        records.append(dict(name=name,label=label,nodes=len(ns),edges=len(es)))
    return records


def build_docs(run_id,model,records,graphs,anatomy):
    path=VIZ/'docs/VISUALIZATION_INDEX.md'
    selected=model['selected_results']['status']=='VALIDATED'
    lines=['# Visualization index', '', f'Current immutable build: `{run_id}`. Dataset: `{DATASET}`, UUID `{UUID}`.', '',
           f'[Open local circuit explorer](../interactive/{run_id}/index.html) · [Anatomy viewer/status](../anatomy/{run_id}/index.html) · [Build manifest](../data/{run_id}/build_manifest.json)', '',
           'Every view carries one explicit scientific label. Figure 1 is PAPER-ASSOCIATED and uses current raw weights; it is not a strict computational replication. Figure 2 '+('consumes the supplied validated selection; its analysis provenance is in the manifest.' if selected else 'is a status/framework view until independently validated results are supplied.')+' Figure 3 is CANDIDATE and does not join the candidates into one pathway.', '',
           '**Puddle remains UNRESOLVED.** Eight paper/current pooled discrepancies are retained. The original checkpoint and scientific results are unchanged. No effective-connectivity analysis, selection, experiment or simulation was run.', '',
           '**Anatomy: '+anatomy['status']+'.** '+str(anatomy['retrieved_bodies'])+' of '+str(anatomy['requested_bodies'])+' requested bodies have actual SWCs in this build. No geometry is fabricated. Anatomical camera orientation is '+anatomy['orientation']['status']+'. See [anatomy retrieval/recovery](ANATOMY.md).', '',
           '## Shared encoding and provenance', '',
           '| Biological role | Fill |','|---|---|']
    lines += [f'| {key.replace("_"," ")} | `{val}` |' for key,val in model['palette'].items()]
    lines += ['', 'Roles for the mapped named circuit describe the Figure 6 motif layers (C037–C040); they are not a general biological-order classifier. Unverified order is gray. Candidate status uses an outline and evidence badges, never a special fill.', '',
              'P = paper-selected/support; here P means support in the inspected paper-associated panels, not selection by a rerun algorithm. R = raw MaleCNS structure. E = validated effective selection. D = dynamic/Shiu evidence. X = body-mapped experimental evidence. Multiple badges are supported. '+('E follows the supplied validated conditions; D/X remain unpopulated.' if selected else 'No E/D/X is populated in the current build.')+' Shiu synonyms alone are not dynamic evidence.', '',
              'Arrows indicate directed body-to-body records, with no inhibitory/excitatory sign. Every raw graph width uses `0.7 + 4.3 * sqrt(raw_synapse_count / visible_max)`; per-panel normalization is disclosed. Future score mode uses the separate score field with the same display transformation and never falls back to raw count. Reciprocal/recurrent edges curve. Skeleton cable segments are morphological geometry, not connectivity edges, and therefore have no directional arrowheads.', '',
              '**PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION.** Body predictions, confidence and consensus remain separate. Raw incoming/outgoing summaries explicitly describe the frozen export or small explorer universe, not undocumented whole-connectome totals.', '',
              'Source identity and side fields come from the frozen structural run. LEFT/RIGHT indicate rootSide for sensory bodies and supplied somaSide where available. Opposite-side endpoints do not identify a crossing neurite or synapse. No anatomical midline crossing is claimed.', '',
              f'Frozen source run: `{model["source_run"]}`. Input and output hashes, package versions, dataset guard and reproducibility metadata: [build manifest](../data/{run_id}/build_manifest.json).', '',
              '## Figure catalog', '']
    for r in records:
        lines += ['### '+r['id'], '', '* Scientific label / raw versus selected: **'+r['label']+'**', '* Scientific question: '+r['question'],
                  '* Node inclusion rule: '+r['node_rule'],'* Edge inclusion rule: '+r['edge_rule'],
                  '* Source files: '+('; '.join(r['sources']))+' (relative CSV names resolve in the frozen source run).',
                  '* Dataset: `'+DATASET+'`; no cross-dataset substitution.', '* Layout: '+r['layout'],
                  '* Color mapping: shared role palette above; candidate outlines/badges remain separate.',
                  '* Edge-width transformation: '+r['width'], '* Display filters: '+r['filters'],
                  '* Known limitations: '+r['limitations'], '* Files: '+', '.join('['+Path(p).name+'](../'+str(Path(p).relative_to(VIZ))+')' for p in r['files']), '']
    lines += ['### Interactive body-level explorer', '',
              '* Scientific question: Which directed records and evidence apply to a chosen body or narrow circuit subset?',
              f'* Node inclusion: {len(model["nodes"])} verified requested bodies in this build; future validated results can explicitly extend the source-backed inventory, up to the 500-body safety cap.',
              '* Edge inclusion: induced frozen raw records among these bodies; paper mode restricts to saved named-route edges. Candidate cards are independent fixed direct-boundary summaries.',
              f'* Sources: [model.json](../data/{run_id}/model.json), nodes.csv, raw_edges.csv and paper_associated_paths.csv in the source run; separate selected-result contract if supplied.',
              '* Dataset and raw/selected status: v1.0; each tab carries its own scientific label. Sugar panels remain empty while blocked.',
              '* Layout: side-separated role layers, explicit individual body labels; responsive cards for independent candidates. Scroll/zoom, inspect nodes and SVG export.',
              '* Palette and width: same role colors and sqrt scale. All exact body weights are on edge hover and in the records table. Missing effective scores produce an unavailable state, never a raw-width substitution.',
              '* Filters: requested types, four motor targets, P/R/E/D/X support, left/right/both, minimum raw count, clicked-body edges. >260 displayed edges suppresses arrows with an explicit message; records remain inspectable. No whole structural export is plotted.',
              '* Limitations: candidate-card boundary totals deliberately pool partner sides and are fixed summaries; explanatory text specifies which graph controls do not apply. Dynamic/experimental evidence requires a future source-backed adapter, not invented badges.', '',
              '## Graph exchange', '', '| File stem | Scientific label | Bodies | Edges |','|---|---|---:|---:|']
    for g in graphs:lines.append(f'| [{g["name"]}](../graph/{run_id}/{g["name"]}.graphml) · [GEXF](../graph/{run_id}/{g["name"]}.gexf) | {g["label"]} | {g["nodes"]} | {g["edges"]} |')
    lines += ['', 'Both graph formats preserve individual body IDs, sides, raw counts, evidence and source metadata. The candidate exchange has no edges because the comparison does not assert a shared pathway. The focused raw graph provides separately labeled structural connections. No selected graph is emitted without a validated result.', '',
              '## Reuse and verification', '', '[Build and validation instructions](../README.md) · [Future selected-result contract](SELECTED_RESULTS.md) · [Scientific validation results](../data/'+run_id+'/validation.json). Static figures are SVG/PDF plus PNG at 320 DPI. SVGs preserve text and edge/node hover titles.', '']
    path.write_text('\n'.join(lines))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-run',type=Path,default=ROOT/(ROOT/'config/current_structural_run.txt').read_text().strip())
    p.add_argument('--run-id',default=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    p.add_argument('--selected-results',type=Path)
    p.add_argument('--fetch-skeletons',action='store_true')
    p.add_argument('--retrieval-manifest',type=Path)
    p.add_argument('--orientation',type=Path)
    a=p.parse_args()
    if '/' in a.run_id or a.run_id in ['.','..']:p.error('Invalid run ID')
    dirs={key:VIZ/key/a.run_id for key in ['data','static','interactive','anatomy','graph']}
    if any(d.exists() for d in dirs.values()):p.error('Never overwrite an existing visualization run; choose a fresh run ID')
    for d in dirs.values():d.mkdir(parents=True)
    model=build_model(a.source_run.resolve(),a.selected_results)
    print('Model',len(model['nodes']),'bodies',len(model['edges']),'edges',flush=True)
    write_json(dirs['data']/'model.json',model)
    write_csv(dirs['data']/'nodes.csv',model['nodes']);write_csv(dirs['data']/'edges.csv',model['edges'])
    write_csv(dirs['data']/'paper_edges.csv',[e for e in model['edges'] if e['paper_associated']])
    write_json(dirs['data']/'selected_results.json',model['selected_results'])
    graphs=graph_exports(model,dirs['graph'])
    records=render_all(model,dirs['static']);print('Static figures complete',flush=True)
    retrieval=fetch(model,dirs['anatomy']/'retrieval') if a.fetch_skeletons else json.loads(a.retrieval_manifest.read_text()) if a.retrieval_manifest else None
    if retrieval is not None:write_json(dirs['anatomy']/'retrieval_manifest.json',retrieval)
    anatomy,anatomy_record=render_anatomy(model,dirs['anatomy'],retrieval,a.orientation);records.append(anatomy_record)
    ap=dirs['anatomy']/'index.html';ap.write_text(ap.read_text().replace('__RUN__',a.run_id))
    template=(VIZ/'interactive/explorer.template.html').read_text()
    html=template.replace('/*__STYLE__*/',(VIZ/'interactive/style.css').read_text()).replace('/*__MODEL__*/',json.dumps(model).replace('<','\\u003c')).replace('/*__SCRIPT__*/',(VIZ/'interactive/explorer.js').read_text()).replace('__RUN__',a.run_id)
    (dirs['interactive']/'index.html').write_text(html)
    files=['nodes.csv','raw_edges.csv','paper_associated_paths.csv','paper_motif_comparison.csv','validation_checks.json','raw/meta_start.json','raw/meta_end.json','manifest.json']
    sources={str((a.source_run/f).resolve().relative_to(ROOT)):sha(a.source_run/f) for f in files}
    for path in [a.retrieval_manifest,a.orientation or VIZ/'anatomy/orientation.json',a.selected_results,SUPPORT_AUDIT,ROOT/'paper/supplement/supplemental_information.pdf']:
        if path is not None:sources[str(path.resolve().relative_to(ROOT))]=sha(path)
    try:commit=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip() or 'NO COMMIT'
    except OSError:commit='UNAVAILABLE'
    manifest=dict(run_id=a.run_id,timestamp=dt.datetime.now(dt.timezone.utc).isoformat(),dataset=DATASET,dataset_uuid=UUID,
                  label='VISUALIZATION DERIVATIVES ONLY',source_run=model['source_run'],scientific_results_modified=False,
                  random_seed=None,layout='deterministic; no randomized algorithm',git_commit=commit,
                  python=platform.python_version(),platform=platform.platform(),
                  packages={k:importlib.metadata.version(k) for k in ['matplotlib','networkx','numpy','pillow']},
                  input_sha256=sources,code_sha256={str(f.relative_to(ROOT)):sha(f) for folder in ['scripts','interactive','anatomy'] for f in (VIZ/folder).glob('*') if f.is_file() and f.name!='index.html'},
                  selected_results=None if not a.selected_results else dict(file=str(a.selected_results),sha256=sha(a.selected_results)),
                  graph_exports=graphs,figures=records,anatomy_status=anatomy['status'],
                  output_sha256={str(f.relative_to(ROOT)):sha(f) for d in dirs.values() for f in sorted(d.rglob('*')) if f.is_file()})
    write_json(dirs['data']/'build_manifest.json',manifest)
    build_docs(a.run_id,model,records,graphs,anatomy)
    for section in ['interactive','anatomy']:
        (VIZ/section/'index.html').write_text(f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>MaleCNS visualization</title><meta http-equiv="refresh" content="0;url={a.run_id}/index.html"></head><body><a href="{a.run_id}/index.html">Open current {section} build</a></body></html>')
    (VIZ/'data/current_run.txt').write_text(a.run_id+'\n')
    print('Build complete',a.run_id,flush=True)


if __name__=='__main__':main()
