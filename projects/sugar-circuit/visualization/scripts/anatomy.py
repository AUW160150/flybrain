"""Actual SWC rendering, or an explicit BLOCKED status artifact; never substitute geometry."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from model import ROOT, VIZ, DATASET, UUID, SENSORY, PAPER, MOTORS, CONDITIONS, write_json, sha
from fetch_skeletons import parse_swc
from figures import header, save


def validate_orientation(config):
    if config.get('status') != 'VERIFIED':
        return None
    if not config.get('orientation_source'):
        raise ValueError('Anatomical orientation requires primary-source provenance')
    matrix=np.asarray(config['raw_to_right_dorsal_anterior'],dtype=float)
    if matrix.shape!=(3,3) or not np.allclose(matrix@matrix.T,np.eye(3),atol=1e-6):
        raise ValueError('Orientation must be a verified orthonormal matrix')
    return matrix


def render_anatomy(model,out,retrieval=None,orientation=None):
    config=json.loads((orientation or VIZ/'anatomy/orientation.json').read_text())
    matrix=validate_orientation(config)
    if config['coordinate_space'] != 'MaleCNS native EM' or config['scale_to_micrometers'] != .008:
        raise ValueError('Unexpected skeleton coordinate space or scale')
    if retrieval is not None and (retrieval['dataset']!=DATASET or retrieval['dataset_uuid']!=UUID):
        raise ValueError('Morphology dataset mismatch')
    byid={n['body_id']:n for n in model['nodes']};morph=[]
    for record in (retrieval or {}).get('bodies',[]):
        if record['status']!='VERIFIED':continue
        body=record['body_id']
        if body not in byid:raise ValueError('Non-allowlisted morphology')
        path=ROOT/record['file']
        if sha(path)!=record['sha256']:raise ValueError('SWC source hash mismatch')
        points,segments=parse_swc(path)
        seg=np.asarray(segments)*.008
        if matrix is not None:seg=seg@matrix.T
        n=byid[body]
        morph.append(dict(body_id=body,type=n['type'],side=n['side'],color=n['color'],
                          source=record['source'],sha256=record['sha256'],segments=seg.tolist()))
    groups={
        'LB3b':dict(label='RAW STRUCTURAL',ids=[n['body_id'] for n in byid.values() if n['type']=='LB3b']),
        'LB3c':dict(label='RAW STRUCTURAL',ids=[n['body_id'] for n in byid.values() if n['type']=='LB3c']),
        'paper_downstream':dict(label='PAPER-ASSOCIATED',ids=[n['body_id'] for n in byid.values() if n['type'] in PAPER]),
        'selected_downstream':dict(label='SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY',ids=sorted({v for c in model['selected_results'].get('conditions',{}).values() for v in c['node_ids'] if byid[v]['type'] not in SENSORY+MOTORS})),
        'motors':dict(label='RAW STRUCTURAL',ids=[n['body_id'] for n in byid.values() if n['type'] in MOTORS]),
        'combined_paper':dict(label='PAPER-ASSOCIATED',ids=[n['body_id'] for n in byid.values() if n['type'] in SENSORY+PAPER+MOTORS]),
        'comparison_candidates':dict(label='CANDIDATE',ids=[n['body_id'] for n in byid.values() if n['candidate']])}
    present={m['body_id'] for m in morph}
    for key,g in groups.items():
        g['missing_ids']=sorted(set(g['ids'])-present,key=int)
        g['status']='BLOCKED — VALIDATED SELECTION REQUIRED' if key=='selected_downstream' and not g['ids'] else 'BLOCKED — SKELETONS REQUIRED' if g['missing_ids'] else 'VERIFIED'
    status=dict(dataset=DATASET,dataset_uuid=UUID,status='BLOCKED' if not morph else 'PARTIAL' if any(g['missing_ids'] for g in groups.values()) else 'VERIFIED',
                retrieved_bodies=len(morph),requested_bodies=len(byid),orientation=config,groups=groups,morphologies=morph,
                limitations=['Skeleton cable is not a synaptic edge; no physiological arrows on neurites.',
                             'No healing, body mirroring, inferred synapses, or soma-only substitute morphology.',
                             'Named anatomical cameras require verified orientation.',
                             'Selected downstream membership is empty until validated algorithm results exist.'])
    write_json(out/'anatomy.json',status)
    files=[]
    if not morph:
        fig=plt.figure(figsize=(16,9));header(fig,'RAW STRUCTURAL','MaleCNS anatomy · BLOCKED',
                    'No authentic requested SWC geometry is available in this build.')
        fig.text(.06,.70,'SKELETON RETRIEVAL BLOCKED',size=23,weight='bold')
        fig.text(.06,.56,'The official v1.0 per-body download failed in this environment.\nNo morphology, synapse positions, or anatomical crossings were invented.',size=16,linespacing=1.8)
        fig.text(.06,.34,'Prepared groups: LB3b · LB3c · paper downstream · motors · combined paper circuit\nSelected sugar downstream: BLOCKED — validated selection required\nPrepared cameras: anterior · posterior · dorsal · lateral · interactive native 3D',size=14,linespacing=1.9)
        fig.text(.06,.12,'Named camera orientation is UNVERIFIED; authoritative orientation evidence is also required.\nSee retrieval_manifest.json, the explicit body allowlist, and docs/ANATOMY.md.',size=13)
        files+=save(fig,out,'anatomy_BLOCKED')
    else:
        # Native projections retain xyz labels until an orientation source is verified.
        views={'anterior':(0,1,-1,1),'posterior':(0,1,1,1),'dorsal':(0,2,1,1),'lateral':(2,1,1,1)} if matrix is not None else {'native_xy':(0,1,1,1),'native_xz':(0,2,1,1),'native_yz':(1,2,1,1)}
        for key,g in groups.items():
            if g['status']!='VERIFIED':continue
            selected=[m for m in morph if m['body_id'] in g['ids']]
            for camera,(h,v,hs,vs) in views.items():
                fig,ax=plt.subplots(figsize=(14,12));fig.subplots_adjust(top=.85,bottom=.13)
                header(fig,g['label'],key.replace('_',' ')+' · '+camera,'male-cns:v1.0 · actual centerline SWCs · micrometers · no connectivity inferred from overlap')
                for m in selected:
                    seg=np.asarray(m['segments'])[:,:,[h,v]]*np.array([hs,vs])
                    ax.add_collection(LineCollection(seg,colors=m['color'],linewidths=.5,alpha=.85))
                ax.autoscale();ax.set_aspect('equal')
                names=['Right (+) / Left (−)','Dorsal (+) / Ventral (−)','Anterior (+) / Posterior (−)'] if matrix is not None else ['Native X','Native Y','Native Z']
                ax.set_xlabel(names[h]+(' [sign reversed]' if hs==-1 else '')+' · µm');ax.set_ylabel(names[v]+' · µm')
                fig.text(.05,.035,'Individual body/type/side and sources: interactive hover and anatomy.json. Neurites have no physiological direction arrows.',size=11)
                files+=save(fig,out,key+'_'+camera)
    template=(VIZ/'anatomy/viewer.template.html').read_text()
    script=(VIZ/'anatomy/viewer.js').read_text()
    template=template.replace('/*__DATA__*/',json.dumps(status).replace('<','\\u003c')).replace('/*__SCRIPT__*/',script)
    (out/'index.html').write_text(template)
    return status,dict(id='anatomy',label='RAW STRUCTURAL / PAPER-ASSOCIATED / CANDIDATE / SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY (per group)',
        question='What are the actual morphologies of the explicitly requested bodies?',node_rule='Only verified paper bodies, explicitly requested candidate bodies, and any later validated selected bodies; maximum 500.',
        edge_rule='Original SWC child-parent cable segments only; not synaptic edges; no healing or inferred connections.',sources=['Official native v1.0 per-body SWCs; retrieval_manifest.json; anatomy.json'],
        layout='3D orthographic interactive orbit with body hover; verified named cameras or explicitly native XYZ projections.',
        filters='LB3b, LB3c, paper downstream, selected downstream, motors, combined paper, comparison candidates; body-side filter.',
        width='Constant cable display width; never encode synapse count as neurite thickness.',
        limitations='Skeleton retrieval status: '+status['status']+'. Named cameras require verified orientation. No actual anatomical renders are claimed for any blocked group.',
        files=[str(p) for p in files]+[str(out/'index.html')])
