from __future__ import annotations
import csv, html, math, os, shutil
from pathlib import Path
from .provenance import *
from .discover_run import verify_graph,select_runs
from . import indexing as ix

INK='#173b46';TEAL='#147c72';ORANGE='#c86035';BLUE='#316fa8'
def esc(s): return html.escape(str(s))
def svg_start(w,h,title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{esc(title)}</title><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="context-stroke"/></marker></defs><rect width="100%" height="100%" fill="#fff"/><g font-family="Arial, sans-serif" fill="{INK}">'''
def label(x,y,s,size=16,color=INK,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{esc(s)}</text>'
def line(x1,y1,x2,y2,color=TEAL,dash=None,width=2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" marker-end="url(#arrow)"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>'
def box(x,y,w,h,title,detail,color=TEAL):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" fill="#f0f7f5" stroke="{color}"/>'+label(x+w/2,y+27,title,16,color,'middle')+''.join(label(x+w/2,y+50+19*i,t,12,INK,'middle') for i,t in enumerate(detail))
def save_svg(name,s,meta):
    p=REPORT/'figures'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s+'</g></svg>');sidecar(p,meta)
    from .raster import raster_svg
    companion=raster_svg(p);sidecar(companion,dict(meta,rasterization='Pillow companion of explicit SVG primitives; browser rasterization not available in this sandbox'))
def sidecar(path,meta):
    atomic(path.with_suffix(path.suffix+'.manifest.json'),dict(code_revision=revision(),renderer_version='1',export_sha256=sha(path),export_time=now(),**meta))

def architectures(a,g):
    actual=a['actual'];n=len(g['ids']);m=len(g['source']);d=32
    meta=dict(inputs={'graph_hash':g['graph_hash'],'executed_code_hash':actual['executed_code_hash'],'source_archive_sha256':actual['source_archive_sha256']},graph_scope='G3 computational architecture',node_ordering='saved model index',filters='none',reduction='explicit implementation-derived schematic',rendered_counts={'state_units':n,'recurrent_parameters':m},available_counts={'active_parameters':actual['active_trainable']})
    s=svg_start(1200,395,'Actual implemented graph-constrained byte predictor')
    s+=label(26,35,'ACTUAL PREDICTOR / complete computational interfaces',22)+label(26,61,'Source archive verified against run code hash. Scalar state units correspond to biological IDs only for wiring bookkeeping.',13)
    xs=[25,220,460,780,985];ws=[145,180,260,145,180]
    specs=[('Byte embedding',['byte t → e[t] in R^32','E [256,32] · 8,192']),('Dense input B',['B [512,32]','16,384 coefficients','All 512 states receive input']),('Recurrent update',['W[target,source] · 3,061 θ','bias b [512] · tanh','512 scalar artificial states']),('Dense readout R',['R [32,512]','16,384 coefficients']),('Output O + c',['O [256,32] + c [256]','8,192 + 256','256 next-byte logits'])]
    for i,((title,detail),x,w) in enumerate(zip(specs,xs,ws)):
        s+=box(x,130,w,112,title,detail,BLUE if i!=2 else TEAL)
        if i<4:s+=line(x+w,185,xs[i+1],185,BLUE)
    s+=f'<path d="M 570 130 L 570 92 L 698 92 L 698 130" fill="none" stroke="{TEAL}" stroke-width="2" marker-end="url(#arrow)"/>'
    s+=label(634,82,'W h[t-1] : reused learned recurrence',12,TEAL,'middle')
    s+=f'<path d="M 590 242 L 590 276 L 695 276 L 695 242" fill="none" stroke="{ORANGE}" stroke-dasharray="6 4" stroke-width="2" marker-end="url(#arrow)"/>'
    s+=label(710,279,'Engineered 0.5 h[t-1] retention',13,ORANGE)
    s+=label(25,315,'h[t] = 0.5 h[t-1] + 0.5 tanh(W h[t-1] + B E[byte[t]] + b)     logits[t] = O R h[t] + c',18)
    s+=label(25,345,'52,981 active parameters · 49,408 dense interface parameters + 512 recurrent biases + 3,061 recurrent edge scalars',14)
    s+=label(25,373,'Teal: learned graph core • Blue: engineered dense interfaces • Dashed orange: engineered retention, not an anatomical autapse',12)
    save_svg('folded.svg',s,meta)
    s=svg_start(1200,400,'Actual recurrent predictor unrolled for three byte steps')+label(25,35,'THREE BYTE STEPS / same units, shared parameters',22)
    s+=label(25,63,'Synchronous update: sources at the previous step affect receivers at the next. No future-byte input.',14)
    for i in range(3):
        x=165+i*350
        s+=box(x,145,245,95,f'State h at t + {i}',[f'{n} scalar states · W restricted to {m} pairs','0.5 previous + 0.5 tanh(proposal)'])
        s+=label(x+122,99,f'byte at t + {i} → E → dense B',14,BLUE,'middle')+line(x+122,106,x+122,145,BLUE)
        s+=line(x+122,240,x+122,285,BLUE)+label(x+122,310,f'R → O+c → predict byte t + {i+1}',14,BLUE,'middle')
        if i==0:s+=label(20,180,'zero state',14)+line(20,200,x,200,TEAL)
        else:s+=line(x-105,175,x,175,TEAL)+line(x-105,219,x,219,ORANGE,'5 3')
    s+=label(25,355,'Every step reuses E, B, W, b, R, O, c. Unrolling does not add neurons, anatomical layers, or parameters.',15)
    s+=label(25,382,'Solid teal: W h(previous). Dashed orange: same-node identity retention. One update per byte is not a biological duration.',13)
    save_svg('unrolled.svg',s,meta)
    refs=a['references'];s=svg_start(1200,700,'Explicit untrained reference architectures')+label(25,36,'ARCHITECTURE REFERENCES / untrained, no quality comparison',22)
    s+=label(25,64,'MLP and CNN: visualization-only educational modules. Transformer: repository module and parameter-counting configuration.',13)
    row_specs=[('WINDOW MLP',120,[('8 causal bytes',['E [256,16]','zero embedding padding']),('Flatten 8 × 16',['128 activations','finite supplied context']),('Dense 128 → 64',['+ bias · ReLU']),('Dense 64 → 64',['+ bias · ReLU']),('Dense 64 → 256',['+ bias','next-byte logits'])]),
    ('CAUSAL 1D CNN',300,[('Byte sequence',['Embedding [256,16]']),('Conv1d 16 → 32',['k=3, dilation=1','left pad=2 · ReLU']),('Conv1d 32 → 32',['k=3, dilation=2','left pad=4 · ReLU']),('32 channels / position',['stride=1 · shared kernels','receptive field=7']),('Dense 32 → 256',['per position + bias'])]),
    ('DECODER-ONLY TRANSFORMER',480,[('Byte + position',['d=32 · context=128','learned absolute position']),('Masked self-attention',['Q/K/V + output projection','4 heads · j ≤ t']),('Residual + LayerNorm',['post-normalization','no future positions']),('FFN + residual + LN',[f"32 → {refs[2]['config']['ff']} → 32",'ReLU · 1 block']),('Readout 32 → 32',['then 32 → 256 + bias','next-byte logits'])])]
    for i,(title,y,items) in enumerate(row_specs):
        s+=label(25,y-20,f'{title} · {refs[i]["active_trainable"]:,} unique active parameters',17)
        for k,(title,detail) in enumerate(items):
            x=25+k*235;s+=box(x,y,205,92,title,detail,BLUE)
            if k<4:s+=line(x+205,y+45,x+235,y+45,BLUE)
        s+=label(25,y+(180 if i==2 else 119),['No recurrence. Every dense input activation connects to every output in the next layer; omitted drawing edges are not sparsity.','Kernel coefficients are reused across positions. Feature locations are artificial activations, not biological neurons.','Causal mask is fixed. Attention coefficients depend on input; no attention heatmap is fabricated.'][i],12)
    s+=f'<path d="M 245 525 L 245 608 L 595 608 L 595 572" fill="none" stroke="{ORANGE}" stroke-dasharray="5 3" stroke-width="2" marker-end="url(#arrow)"/>'
    s+=f'<path d="M 715 525 L 715 632 L 910 632 L 910 572" fill="none" stroke="{ORANGE}" stroke-dasharray="5 3" stroke-width="2" marker-end="url(#arrow)"/>'
    s+=label(300,629,'Residual input x + attention(x)',12,ORANGE)+label(720,650,'Residual y + FFN(y)',12,ORANGE)
    save_svg('references.svg',s,dict(meta,graph_scope='untrained illustrative architectures',inputs={'reference_configs':[x['config'] for x in refs]},rendered_counts={'reference_architectures':3},available_counts={'parameters':[x['active_trainable'] for x in refs]}))

def rules(g):
    # Small real detail: lowest biological ID and first seven distinct neighbors by ID.
    ids=g['ids'];root=0;neighbors=sorted(set(g['source'][g['target']==root].tolist())|set(g['target'][g['source']==root].tolist()),key=lambda i:int(ids[i]))[:7]
    chosen=[root]+neighbors;selected=set(chosen);edges=[(int(s),int(t),int(c)) for s,t,c in zip(g['source'],g['target'],g['counts']) if int(s) in selected and int(t) in selected]
    s=svg_start(1200,430,'Local connection rules: a real saved neighborhood and schematic references')
    titles=['REAL G3 DETAIL','SCHEMATIC MLP','SCHEMATIC CAUSAL CNN','CAUSAL ATTENTION MASK']
    for i,t in enumerate(titles):s+=label(25+i*300,35,t,16)
    pos={v:(150+100*math.cos(i/len(chosen)*2*math.pi),180+100*math.sin(i/len(chosen)*2*math.pi)) for i,v in enumerate(chosen)}
    for u,v,c in edges:
        x,y=pos[u];xx,yy=pos[v];length=math.hypot(xx-x,yy-y)
        s+=line(x,y,xx-(xx-x)*8/length,yy-(yy-y)*8/length,TEAL,width=1.2)
    for v,(x,y) in pos.items():s+=f'<circle cx="{x}" cy="{y}" r="5" fill="{TEAL}"/>'+label(x,y-10,str(ids[v]),10,INK,'middle')
    for i in range(4):
        for j in range(3):s+=line(350,100+i*48,520,122+j*48,BLUE,width=.8)
    for x,n,start in [(350,4,100),(520,3,122)]:
        for i in range(n):s+=f'<circle cx="{x}" cy="{start+i*48}" r="7" fill="{BLUE}"/>'
    for i in range(5):
        for j in range(max(0,i-2),i+1):s+=line(640+j*40,230,640+i*40,130,[ORANGE,BLUE,TEAL][i-j],width=1)
        s+=f'<circle cx="{640+i*40}" cy="230" r="6" fill="{BLUE}"/><circle cx="{640+i*40}" cy="130" r="6" fill="{TEAL}"/>'
    for y in range(6):
        for x in range(6):s+=f'<rect x="{950+x*27}" y="{90+y*27}" width="25" height="25" fill="{TEAL if x<=y else "#e3e9e8"}"/>'
    s+=label(950,75,'key/source position →',12)+label(915,275,'rows: query / receiving position',12)
    foot=[f'{len(chosen)} exact IDs / {len(edges)} induced pairs','Every adjacent-layer pair allowed','k=3; colours identify shared taps','j ≤ t allowed; not measured attention']
    for i,t in enumerate(foot):s+=label(25+i*300,327,t,12)
    s+=label(25,365,'Real detail selection: lowest saved biological ID plus first seven distinct incoming/outgoing partners in biological-ID order.',13)
    s+=label(25,392,'The reference nodes mean layer activations, position/channel activations, and token vectors respectively. They are not anatomical units.',13)
    meta=dict(inputs={'graph_hash':g['graph_hash']},graph_scope='G3 induced detail + separately labelled schematics',filters='deterministic local detail',node_ordering='recorded selected IDs',reduction='none',rendered_counts={'real_nodes':len(chosen),'real_pairs':len(edges)},available_counts={'G3_nodes':len(ids),'G3_pairs':len(g['source'])})
    save_svg('rules.svg',s,meta)
    result=dict(description='Lowest saved biological ID plus first seven distinct incoming/outgoing partners ordered by biological ID; real induced detail, not full model.',ids=[str(ids[i]) for i in chosen],edges=[dict(source_body_id=str(ids[u]),target_body_id=str(ids[v]),synapse_count=c) for u,v,c in edges]);atomic(REPORT/'neighborhood.json',result);return result

def matrix_png(tile,name,reduction):
    from PIL import Image
    import math
    im=Image.new('RGB',(tile['bins_x'],tile['bins_y']),(246,249,249));px=im.load();maximum=max([r[reduction] for r in tile['rows']]+[1])
    for r in tile['rows']:
        v=math.log1p(r[reduction])/math.log1p(maximum);px[r['x'],r['y']]=(int(233-221*v),int(242-129*v),int(239-124*v))
    p=REPORT/'figures'/name; im.resize((768,768),Image.Resampling.NEAREST).save(p)
    sidecar(p,dict(inputs={'index_identity':tile['identity']},graph_scope=tile['scope'],node_ordering=tile['ordering'],filters={'bounds':tile['bounds']},reduction=reduction,rendered_counts={'bins':len(tile['rows']),'pairs':tile['pairs'],'contacts':tile['contacts']},available_counts={'nodes':tile['n']},matrix_convention='row target, column source',colour_transform='log1p display only'))

def build():
    from .app import database,query,WEB
    from .ingest import removal_ledger,SMALL
    g=verify_graph();(REPORT/'figures').mkdir(parents=True,exist_ok=True);(REPORT/'tables').mkdir(exist_ok=True)
    p=REPORT/'tables/nodes.csv'
    md=g['manifest']['metadata'];
    with p.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['body_id','model_index','dataset','release','annotation_class','annotation_type','coordinate_provenance'])
        for i,v in enumerate(g['ids']):w.writerow([str(v),i,'MaleCNS',RELEASE,md['node_classes']['superclass'][i],md['node_classes']['type'][i],'missing unless geometry.json records a loaded skeleton'])
    sidecar(p,dict(inputs={'graph_hash':g['graph_hash']},graph_scope='G3',node_ordering='saved model index',filters='none',reduction='none',rendered_counts={'nodes':len(g['ids'])},available_counts={'nodes':len(g['ids'])}))
    scopes={};errors=[]
    for scope in ix.SCOPES:
        try:
            db=database(scope);scopes[scope]=ix.summary(db,scope);order='model' if scope in ('G3','G1-subset') else 'id'
            t=query('tile',{'scope':[scope],'order':[order],'bins':['128']})
            assert t['pairs']==scopes[scope]['pairs'] and t['contacts']==scopes[scope]['contacts']
            gr=ix.groups(db,scope);assert gr['pairs']==t['pairs'] and gr['contacts']==t['contacts']
            atomic(REPORT/'tables'/(scope+'-groups.json'),gr)
            atomic(REPORT/'tables'/(scope+'-matrix-bins.json'),t)
            for reduction in ['pairs','contacts']:matrix_png(t,scope+'-'+reduction+'.png',reduction)
            db.close()
        except EvidenceError as e:scopes[scope]=dict(status='blocked',error=e.detail);errors.append(e.detail)
    if SMALL.exists():
        db=ix.connect(SMALL,True);atomic(REPORT/'removal-ledger.json',removal_ledger(db));db.close()
    if not (REPORT/'architecture.json').exists():fail('E_RUN_IDENTITY_MISSING','Run inspect-model before build-views','architecture','./visualization/viz inspect-model')
    a=read(REPORT/'architecture.json');architectures(a,g);neighborhood=rules(g);exact_exports(g);boundary_figure()
    runs=[]
    for p,m in select_runs():
        snap=REPORT/'snapshots'/(p.name+'.json');r=read(snap) if snap.exists() else {}
        runs.append(dict(run_id=p.name,config=m['config'],manifest_sha256=sha(p/'manifest.json'),snapshot_status=r.get('status','not snapshotted'),snapshot_sha256=r.get('sha256'),step=r.get('step')))
    if any(r['snapshot_status']=='blocked' for r in runs):errors.append(dict(code='E_CHECKPOINT_UNSTABLE_OR_UNSAFE',panel='weights/activity',message='Completed checkpoints include NumPy RNG pickle state rejected by tensor-only loading. No unsafe fallback. Exact copied bytes are retained.',recovery='Use snapshot-run --safe-export with a trusted tensor-only export; schema in docs/ERRORS.md.'))
    geometry=read(REPORT/'geometry.json') if (REPORT/'geometry.json').exists() else {'loaded':0,'total':len(g['ids'])}
    raw_rows=next(f['schema']['rows'] for f in read(EXPERIMENT/'data/raw/malecns-manifest.json')['files'] if f['name'].startswith('connectome-weights'))
    products=[dict(name='G0 full released segment connectivity',status='complete' if 'pairs' in scopes['G0'] else 'not indexed',note=f'Official bulk file verified; full {raw_rows:,}-row disk index deferred; no additional count threshold'),dict(name='G1 curated-neuron graph',status='complete' if 'pairs' in scopes['G1'] else 'not indexed',note='Complete Traced inventory eligibility; valid isolates and null types preserved by implementation'),dict(name='G3 exact saved subset',status='verified / complete',note=f'{len(g["ids"])} IDs; {len(g["source"])} directed pairs; {int(g["counts"].sum())} contacts'),dict(name='G1 subset and selected-neuron boundary evidence',status='complete' if SMALL.exists() else 'not loaded',note='Complete source scan, only curated edges incident to exact selected IDs retained; not a full G1 index'),dict(name='Native skeleton geometry',status=f'{geometry["loaded"]}/{geometry["total"]} subset skeletons',note='Real SWC, source 8nm units → micrometres exactly once; whole-CNS geometry/context not loaded'),dict(name='Synapse coordinates / microscopy / meshes',status='not loaded',note='Not prerequisites for exact released pair access; large optional evidence products'),dict(name='Neurotransmitter predictions',status='not loaded',note='Learned model weight sign is not biological transmitter identity')]
    data=dict(built_utc=now(),release=RELEASE,graph_hash=g['graph_hash'],code_revision=revision(),scopes=scopes,runs=runs,products=products,blockers=errors,neighborhood=neighborhood,snapshot_selection='none by default',geometry_coverage=geometry.get('coverage'))
    atomic(REPORT/'dashboard.json',data)
    # Portable static report embeds only bounded figures/tables, never millions of edges.
    parts=['<!doctype html><html><head><meta charset="utf-8"><title>Connectome inspection report</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;color:#173b46}img{width:100%}pre{white-space:pre-wrap}td,th{padding:8px;border-bottom:1px solid #ddd;text-align:left}</style></head><body><h1>MaleCNS connectivity & architecture atlas</h1>',f'<p>Exact graph {esc(g["graph_hash"])} · {len(g["ids"])} nodes · {len(g["source"])} pairs · {int(g["counts"].sum())} contacts.</p>','<p>Interactive exact lookups: run <code>./visualization/viz serve --host 127.0.0.1 --port 8765</code>.</p>','<h2>Coverage</h2><ul>']
    parts += [f'<li>{esc(x["name"])}: <b>{esc(x["status"])}</b>. {esc(x["note"])}</li>' for x in products];parts.append('</ul>')
    parts.extend(f'<h2>{title}</h2><img src="figures/{name}" alt="{title}">' for name,title in [('native-skeletons.png','Real skeletons: 8/512 saved IDs, native x/z micrometre projection'),('selection-boundary.svg','Conserving incoming and outgoing boundary ledger'),('G3-contacts.png','G3 contacts: rows receive, columns send; 128 bins; all edges included'),('folded.svg','Actual predictor'),('unrolled.svg','Same model through time'),('references.svg','Untrained illustrative references'),('rules.svg','Local connection rules')])
    parts.append('<h2>Unresolved evidence</h2>');parts.extend(f'<p>{esc(e["code"])}: {esc(e["message"])} Recovery: {esc(e["recovery"])}</p>' for e in errors)
    parts.append('<p>FlyEM / HHMI Janelia, University of Cambridge, MRC LMB, Google Research. <a href="https://male-cns.janelia.org/download/">Official dataset catalogue</a>; CC BY 4.0. No model-quality claim.</p></body></html>');(REPORT/'index.html').write_text(''.join(parts));sidecar(REPORT/'index.html',dict(inputs={'graph_hash':g['graph_hash']},graph_scope='explicitly named panels',node_ordering='per-panel manifest',filters='per-panel manifest',reduction='per-panel manifest',rendered_counts={'panels':5},available_counts={'scopes':list(scopes)}))
    atomic(REPORT/'audit.json',dict(identity=read(REPORT/'identity.json'),architecture=read(REPORT/'architecture.json'),coverage=data['scopes'],geometry={k:v for k,v in geometry.items() if k not in ('records','eligible_ids','not_requested')},blockers=errors,non_interference={'protected_baseline':'inventory.json','checkpoints':'immutable snapshots only; writer allowed to progress','training_or_test_loader_invoked':False,'optimizer_invoked':False,'accelerator_used':False},code_revision=revision()))
    return dict(report=str(REPORT/'index.html'),interactive_command='./visualization/viz serve --host 127.0.0.1 --port 8765',scopes={k:v.get('coverage',v.get('status')) for k,v in scopes.items()},geometry_loaded=geometry['loaded'])

def exact_exports(g):
    import numpy as np
    from PIL import Image,ImageDraw,ImageFont
    from .raster import FONT
    n=len(g['ids']);adj=np.zeros((n,n),dtype=np.uint8);contacts=np.zeros((n,n),dtype=np.int64)
    adj[g['target'],g['source']]=1;contacts[g['target'],g['source']]=g['counts']
    p=REPORT/'tables/G3-exact-matrices.npz';np.savez_compressed(p,body_ids=g['ids'],model_index=np.arange(n),adjacency=adj,synapse_count=contacts)
    meta=dict(inputs={'graph_hash':g['graph_hash']},graph_scope='G3',filters='none',node_ordering='exact saved model index',reduction='none: one cell per directed pair',rendered_counts={'nodes':n,'allowed_pairs':len(g['source'])},available_counts={'nodes':n,'allowed_pairs':len(g['source'])},matrix_convention='rows receive; columns send; body_ids NPZ stored as int64; JSON/CSV IDs are decimal strings')
    sidecar(p,meta)
    order_path=REPORT/'tables/G3-edge-parameter-order.csv'
    with order_path.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['parameter_index','source_model_index','target_model_index','source_body_id','target_body_id','synapse_count'])
        for k,(a,b,c) in enumerate(zip(g['source'],g['target'],g['counts'])):writer.writerow([k,int(a),int(b),str(g['ids'][a]),str(g['ids'][b]),int(c)])
    sidecar(order_path,meta)
    for name,values in [('binary',adj),('contact-count',contacts)]:
        im=Image.new('RGB',(n,n),'#f6f9f9');px=im.load();maxval=float(values.max())
        for a,b in zip(g['source'],g['target']):
            intensity=math.log1p(int(values[b,a]))/math.log1p(maxval);px[int(a),int(b)]=(int(233-221*intensity),int(242-129*intensity),int(239-124*intensity))
        p=REPORT/'figures'/('G3-exact-'+name+'.png');im.save(p);sidecar(p,dict(meta,quantity=name,colour_transform='log1p for count; binary exact mask'))
    # All 3,061 edges and all 512 IDs retained in a compact native SVG export.
    s=svg_start(1000,1100,'Exact G3 directed wiring in an abstract circular layout')+label(30,35,'G3 / exact saved directed mask',22)
    pos={i:(500+425*math.cos(i/n*2*math.pi),510+425*math.sin(i/n*2*math.pi)) for i in range(n)}
    for a,b in zip(g['source'],g['target']):
        x,y=pos[int(a)];xx,yy=pos[int(b)];length=math.hypot(xx-x,yy-y)
        s+=line(x,y,xx-(xx-x)*4/length,yy-(yy-y)*4/length,'#9fbeb866',width=.4)
    for i,(x,y) in pos.items():s+=f'<circle cx="{x}" cy="{y}" r="2.3" fill="{TEAL}"><title>body {g["ids"][i]}, model index {i}</title></circle>'
    s+=label(30,1000,f'{n} exact IDs; {len(g["source"])} directed pairs. Positions are topological, not anatomical.',16)
    s+=label(30,1030,'All arrows rendered here; use the interactive selected-neuron highlight to resolve overlapping edges.',14)
    save_svg('G3-wiring.svg',s,dict(meta,node_ordering='circle in saved model-index order',reduction='none'))
    gp=REPORT/'geometry.json'
    if gp.exists():
        geometry=read(gp);available=[r for r in geometry['records'].values() if r['status']=='loaded'];records=[read(REPORT/'geometry'/(r['body_id']+'.json')) for r in available[:16]]
        if records:
            pts=np.concatenate([np.array(r['points'])[:,[0,2]] for r in records]);lo=pts.min(0);hi=pts.max(0);scale=min(1100/(hi[0]-lo[0]),650/(hi[1]-lo[1]));im=Image.new('RGB',(1200,800),'white');d=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),17)
            colours=['#0e796f','#bb613b','#5478a6','#765a97','#3b867e','#b18b3f','#849a49','#686f87']
            for k,r in enumerate(records):
                xy=(np.array(r['points'])[:,[0,2]]-lo)*scale+np.array([(1200-(hi[0]-lo[0])*scale)/2,75]);
                d.line([(25,90+k*28),(50,90+k*28)],fill=colours[k%len(colours)],width=3);d.text((60,80+k*28),'body '+r['body_id'],font=font,fill=INK)
                for a,b in r['branches']:d.line([tuple(xy[a]),tuple(xy[b])],fill=colours[k%len(colours)],width=1)
            d.text((25,20),f'Reconstructed native skeletons: {len(records)}/512 saved IDs; x / z projection, micrometres',font=font,fill=INK)
            d.text((25,755),f'x: {lo[0]:.2f}–{hi[0]:.2f} µm; z: {lo[1]:.2f}–{hi[1]:.2f} µm. No template, invented positions or inter-neuron chords.',font=font,fill=INK)
            p=REPORT/'figures/native-skeletons.png';im.save(p);sidecar(p,dict(inputs={r['body_id']:r['sha256'] for r in records},graph_scope='exact-subset geometry: partial coverage',node_ordering='biological ID',filters='first 8 saved IDs within acquisition budget',reduction='native x/z orthographic projection',rendered_counts={'skeletons':len(records),'branch_segments':sum(len(r['branches']) for r in records)},available_counts={'saved_ids':512,'downloaded_skeletons':len(available)},coordinate_units='source 8nm; target micrometre; multiply 0.008 once; no transform'))

def boundary_figure():
    p=REPORT/'removal-ledger.json'
    if not p.exists():return
    ledger=read(p);s=svg_start(1100,405,'Conserving selected-neuron connectivity removal ledger')+label(25,35,'FULL CURATED CONNECTIONS → EXACT SAVED SUBSET',22)
    s+=label(25,65,'Complete G1 incident records for the saved IDs. Incoming and outgoing totals are separate incidences, not unique edges.',13)
    categories=['outside_subset','internal_below_threshold','internal_self_edge','retained_G3'];colours=['#becacb','#e0a678','#99627a',TEAL];totals={}
    for i,direction in enumerate(['incoming','outgoing']):
        totals[direction]={key:sum(n[direction]['categories'].get(key,{}).get('contacts',0) for n in ledger['rows']) for key in categories};total=sum(totals[direction].values());y=110+i*115
        s+=label(25,y,f'{direction.title()} G1 contacts: {total:,}',17);x=25
        for key,colour in zip(categories,colours):
            w=1020*totals[direction][key]/max(1,total)
            if w:s+=f'<rect x="{x}" y="{y+15}" width="{w}" height="30" fill="{colour}"/>'
            x+=w
        s+=label(25,y+70,' · '.join(key.replace('_',' ')+': '+format(totals[direction][key],',') for key in categories),12)
    s+=label(25,361,'Predicate order: outside subset → internal count < 5 → internal self-edge → retained G3. Categories do not overlap.',13)
    s+=label(25,388,'G0 segment-to-curated exclusions are separate. A contact is not a learned physiological or artificial coefficient.',13)
    save_svg('selection-boundary.svg',s,dict(inputs={'ledger_sha256':sha(p)},graph_scope='G1 selected-neuron incidence vs G3',node_ordering='exact saved subset',filters=ledger['predicate_order'],reduction='sum of contacts by disjoint removal category, per direction',rendered_counts=totals,available_counts={'selected_nodes':len(ledger['rows'])}))
