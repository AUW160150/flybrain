from __future__ import annotations
import importlib.util, sys, types, zipfile, json
from pathlib import Path
import numpy as np
from .provenance import *
from .discover_run import verify_archive, verify_graph, select_runs

# Import only audited model definitions and utility module from hash-verified archive.
# No training entry point, optimizer, corpus loader or test loader is imported.
def archived_modules(archive: Path):
    dest=ROOT/'snapshots/model-source'/sha(archive)
    allowed=['__init__.py','util.py','models/graph_rnn.py','models/transformer_lm.py']
    with zipfile.ZipFile(archive) as z:
        for name in allowed:
            path=dest/'fly_connectome_lm'/name; path.parent.mkdir(parents=True,exist_ok=True)
            data=z.read('src/fly_connectome_lm/'+name)
            if path.exists() and path.read_bytes()!=data: fail('E_PROTECTED_INPUT_CHANGED','Archived source copy changed')
            if not path.exists(): path.write_bytes(data); path.chmod(0o444)
    package='_viz_verified_experiment'
    module=types.ModuleType(package); module.__path__=[str(dest/'fly_connectome_lm')]; sys.modules[package]=module
    sub=types.ModuleType(package+'.models'); sub.__path__=[str(dest/'fly_connectome_lm/models')]; sys.modules[package+'.models']=sub
    def load(name):
        path=dest/'fly_connectome_lm'/(name.replace('.','/')+'.py')
        spec=importlib.util.spec_from_file_location(package+'.'+name,path); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m
    load('util'); return load('models.graph_rnn'),load('models.transformer_lm')

def inspect_models():
    import torch
    from .baselines_schematic import WindowMLP,CausalCNN,parameter_inventory,shape_and_causality
    torch.set_num_threads(1); torch.set_num_interop_threads(1); torch.manual_seed(1)
    g=verify_graph(); runs=select_runs(); hashes={m['code_hash'] for _,m in runs}
    if len(hashes)!=1: fail('E_RUN_AMBIGUOUS','Multiple implementation hashes; select run before actual architecture inspection','architecture')
    archive=verify_archive(next(iter(hashes))); graph_module,transformer_module=archived_modules(archive)
    # All compatible manifests have the same n,d,execution. Hyperparameters displayed per run.
    configs={(m['config']['n'],m['config']['d'],m['config']['execution']) for _,m in runs}
    if len(configs)!=1: fail('E_RUN_AMBIGUOUS','Multiple architecture shapes; select a run','architecture')
    n,d,execution=next(iter(configs))
    model=graph_module.GraphRNN(n,d,g['source'],g['target'],seed=1,execution=execution)
    actual=parameter_inventory(model)
    assert actual['active_trainable']==512*d+2*n*d+n+256+len(g['source'])
    actual.update(name='Actual GraphRNN',status='Executed source/config verified; no checkpoint chosen',biological_nodes=n,state_width=n,context=128,allowed_recurrent_pairs=len(g['source']),alpha=model.alpha,execution=execution,parameter_sharing='Same E,B,W,b,R,O,c at every byte; no interface weight tying',routing='Fixed anatomical mask; artificial signed recurrent coefficients',source_archive_sha256=sha(archive),executed_code_hash=next(iter(hashes)),shapes=shape_and_causality(model))
    # This is a constructor probe, never represented as initial/current experimental weights.
    layers,ff,count=transformer_module.choose_transformer(d,128,actual['active_trainable'])
    transformer=transformer_module.TransformerLM(d,ff,layers,128,seed=1)
    refs=[]
    for name,ref,config,sharing in [
      ('Window MLP',WindowMLP(),dict(window=8,embedding=16,hidden=[64,64],nonlinearities='ReLU',context='last 8 bytes; zero embedding padding'), 'Each dense coefficient separate; weights reused at each window'),
      ('Causal 1D CNN',CausalCNN(),dict(embedding=16,channels=[32,32],kernel=3,dilations=[1,2],stride=1,left_padding=[2,4],receptive_field=7), 'Kernels shared across positions, not multiplied by sequence length'),
      ('Decoder-only transformer (repository implementation)',transformer,dict(d=d,ff=ff,layers=layers,heads=4,context=128,position='learned absolute embedding',norm='post-norm LayerNorm',ff_activation='ReLU',dropout=0.,readout_rank=d), 'Projection/FFN weights shared across positions; causal mask; coefficients input-dependent')]:
        inv=parameter_inventory(ref); inv.update(name=name,status='UNTRAINED illustrative reference; no trained checkpoint found',config=config,sharing=sharing,causality=shape_and_causality(ref),biological_nodes=None)
        refs.append(inv)
    result=dict(actual=actual,references=refs,anatomical_parameter_count='not defined until a computational model is chosen',discrepancies=['Model factory does not pass config alpha; executed GraphRNN uses constructor default 0.5. Observed configs also specify 0.5.','MLP and CNN absent in experiment; visualization-only references, not parameter matched.','Transformer exists in repository; no trained transformer run found. Its repository counting rule selects layers/ff; this reference remains untrained.'],reference_seed=1,initial_reconstruction_used=False,checkpoint_selection='none; explicit run selector',inference='CPU float32, eval/inference_mode, zero recurrent state, fixed ASCII; no corpus read')
    atomic(REPORT/'architecture.json',result); return result

def snapshot(run_dir: str, checkpoint='final.pt'):
    import torch
    from .baselines_schematic import parameter_inventory
    torch.set_num_threads(1)
    runs=select_runs(run_dir); directory,manifest=runs[0]
    if checkpoint not in ('final.pt','best.pt','latest.pt'): raise ValueError('Named checkpoint only')
    source=directory/checkpoint
    if not source.exists(): fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Requested checkpoint unavailable','weights',f'./visualization/viz snapshot-run --run-dir {directory.relative_to(WORKSPACE)} --checkpoint latest.pt')
    if source.stat().st_size>64*2**20: fail('E_RESOURCE_BUDGET','Checkpoint exceeds 64 MiB inspection cap','checkpoint','Provide a bounded trusted tensor-only export')
    archive=verify_archive(manifest['code_hash']); g=verify_graph()
    if manifest['metadata']['graph_hash']!=g['graph_hash']: fail('E_GRAPH_MASK_MISMATCH','Run topology differs from selected graph')
    copied,receipt=stable_copy(source,ROOT/'snapshots/checkpoints')
    receipt['checkpoint_file']=checkpoint
    if checkpoint=='final.pt' and manifest.get('status')=='complete' and (directory/'result.json').exists():
        result=read(directory/'result.json');receipt['reported_step']=result.get('final_step');receipt['step_evidence_sha256']=sha(directory/'result.json');receipt['step_status']='Reported by completed result JSON; tensor metadata still requires safe verification'
    # The ONLY checkpoint load path. No unsafe fallback, no NumPy pickle allowlist.
    try: payload=torch.load(copied,map_location='cpu',weights_only=True)
    except Exception as exc:
        result=dict(receipt,run_id=directory.name,status='blocked',error=dict(code='E_CHECKPOINT_UNSTABLE_OR_UNSAFE',message='Tensor-only loader rejected checkpoint; no unsafe fallback executed.',detail=str(exc)[:1200],panel='weights/activity',recovery='Provide an independently trusted tensor-only state_dict export with run code hash, graph hash, step, signature, and original snapshot SHA-256; use snapshot-run --safe-export once available.'))
        atomic(REPORT/'snapshots'/f'{directory.name}.json',result); return result
    return inspect_payload(payload,manifest,g,receipt,archive,directory.name)

def inspect_payload(payload,manifest,g,receipt,archive,run_id):
    import torch
    if payload.get('signature')!=manifest['signature'] or payload.get('code_hash')!=manifest['code_hash']: fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Checkpoint metadata disagrees with manifest','weights')
    state=payload['model']; s=state['source'].numpy(); t=state['target'].numpy()
    if not np.array_equal(s,g['source']) or not np.array_equal(t,g['target']): fail('E_EDGE_ORDER_UNVERIFIED','Checkpoint source/target buffers differ from exact saved parameter order','weights')
    for k,v in state.items():
        if not isinstance(v,torch.Tensor) or not torch.isfinite(v).all(): fail('E_CHECKPOINT_UNSTABLE_OR_UNSAFE','Nonfinite or nontensor model state','weights')
    module,_=archived_modules(archive); config=manifest['config']; model=module.GraphRNN(config['n'],config['d'],s,t,execution=config['execution']); model.load_state_dict(state,strict=True); model.eval()
    tokens=torch.tensor([list(b'abc def.')])
    with torch.inference_mode(): logits,states=model(tokens,return_states=True)
    records=[]; initial=payload.get('initial_theta')
    if initial is not None and (initial.shape!=state['theta'].shape or not torch.isfinite(initial).all()): fail('E_EDGE_ORDER_UNVERIFIED','Initial vector incompatible')
    for k,(a,b,c) in enumerate(zip(s,t,g['counts'])):
        records.append(dict(run_id=run_id,checkpoint_hash=receipt['sha256'],source_body_id=str(g['ids'][a]),target_body_id=str(g['ids'][b]),source_model_index=int(a),target_model_index=int(b),parameter_index=k,learned_weight=float(state['theta'][k]),parameter_status='allowed structural edge, including zero weights',initial_weight=float(initial[k]) if initial is not None else None))
    result=dict(receipt,run_id=run_id,status='verified',step=payload['step'],graph_hash=g['graph_hash'],code_hash=manifest['code_hash'],config=config,edge_order_verified=True,weights=records,activity=dict(label='artificial recurrent activations on specified text',input_bytes=list(b'abc def.'),states=states[0].tolist(),logits_shape=list(logits.shape),settings='CPU float32; eval/inference_mode; state reset; one thread',torch_version=torch.__version__),initial_status='saved initial_theta; exact same vector order' if initial is not None else 'unavailable')
    atomic(REPORT/'snapshots'/f'{run_id}.json',result); return result
