from __future__ import annotations
import copy
from pathlib import Path
import numpy as np
import torch
from .models import GraphRNN,build
from .experiment import CORPUS,base_graph,resolved_graph
from .evaluate import evaluate
from .text_data import DevelopmentCorpus
from .util import read_json,atomic_json,seed_for,setup,now

@torch.no_grad()
def generate(model,prompt:bytes,context:int,length:int=128,temperature:float=.8,seed:int=1) -> dict:
    if temperature<=0 or length<1: raise ValueError('Invalid sampling settings')
    device=next(model.parameters()).device; tokens=list(prompt); output=[]
    gen=torch.Generator(device='cpu').manual_seed(seed)
    for _ in range(length):
        x=torch.tensor([tokens[-context:]],device=device)
        probabilities=torch.softmax(model(x)[0,-1].cpu()/temperature,dim=-1)
        value=int(torch.multinomial(probabilities,1,generator=gen)); tokens.append(value); output.append(value)
    return {'prompt_hex':prompt.hex(),'generated_hex':bytes(output).hex(),'display_utf8_with_replacement':bytes(output).decode('utf-8',errors='replace'),
            'temperature':temperature,'length_bytes':length,'sampling_seed':seed,
            'context_policy':'Recompute zero-state sliding context up to fixed context length',
            'interpretation':'Illustration only, no claim about topology benefit'}

def run_diagnostics(run_dir:Path) -> dict:
    manifest=read_json(run_dir/'manifest.json'); cfg=manifest['config']; metadata=manifest['metadata']
    if manifest['status']!='complete': raise ValueError('Completed run required')
    setup(cfg['device'],cfg['threads']); corpus=DevelopmentCorpus(CORPUS)
    graph=base_graph(cfg,metadata['sampling_seed'],metadata['synthetic']); graph=resolved_graph(metadata,graph)
    model=build(metadata['condition'],graph,cfg,metadata['training_seed']).to(cfg['device'])
    model.load_state_dict(torch.load(run_dir/'best.pt',map_location='cpu',weights_only=False)['model'])
    baseline=evaluate(model,corpus.validation,cfg['context'],cfg['evaluation_batch'])
    changed=copy.deepcopy(model)
    with torch.no_grad():
        if isinstance(changed,GraphRNN): changed.theta.zero_()
        elif hasattr(changed,'gru'):
            for name,p in changed.gru.named_parameters():
                if 'weight_hh' in name: p.zero_()
    result={'baseline_validation':baseline,
            'reset_each_byte':evaluate(model,corpus.validation,cfg['context'],cfg['evaluation_batch'],reset_each_byte=True),
            'zero_core':evaluate(changed,corpus.validation,cfg['context'],cfg['evaluation_batch']) if not hasattr(model,'blocks') else {'not_applicable':'No recurrent core'},
            'interpretation':'Artificial-model dependence interventions; parameter damage is not special-connectome evidence'}
    if isinstance(model,GraphRNN):
        changed=copy.deepcopy(model); seed=seed_for('perturb',metadata['training_seed']); rng=np.random.default_rng(seed)
        indices=rng.choice(model.theta.numel(),max(1,int(.1*model.theta.numel())),replace=False)
        with torch.no_grad(): changed.theta[torch.tensor(indices,device=cfg['device'])]=0
        result['perturb_10_percent']={'selected_edges':len(indices),'seed':seed,
                                    **evaluate(changed,corpus.validation,cfg['context'],cfg['evaluation_batch'])}
    prompt=bytes(corpus.train[:32]); result['sample']=generate(model,prompt,cfg['context'],seed=seed_for('generation',metadata['training_seed']))
    path=run_dir/'validation-diagnostics.json'
    if path.exists(): return read_json(path)
    atomic_json(path,result); return result
