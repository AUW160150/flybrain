"""Read-only model diagnosis; synthetic probe fits never replace coding checkpoints."""
import sys
import time
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import torch
import pyarrow.feather as feather
from torch.nn import functional as F
from flycodes.common import ROOT, read_json, write_json, now, sha256
from flycodes.curriculum_dashboard import latest_v2
from flycodes.curriculum_experiment import setup, head, reservoir
from flycodes.curriculum_model import Tokenizer
from flycodes.connectome import load_graph


def prediction_metrics(model, x, y):
    predictions=[];cross_entropy=0.
    with torch.no_grad():
        for start in range(0,len(y),512):
            logits=model(torch.from_numpy(x[start:start+512]))
            target=torch.from_numpy(y[start:start+512])
            predictions.extend(logits.argmax(-1).tolist())
            cross_entropy+=float(F.cross_entropy(logits,target,reduction='sum'))
    predictions=np.asarray(predictions)
    return dict(cross_entropy=cross_entropy/len(y),token_accuracy=float(np.mean(predictions==y))),predictions


def rank_metrics(x):
    # A fixed sample bounds CPU work. Rank is numerical, not biological capacity.
    rows=np.linspace(0,len(x)-1,min(2048,len(x)),dtype=int)
    a=torch.from_numpy(x[rows].astype(np.float64));a-=a.mean(0)
    eigen=torch.linalg.eigvalsh(a.T@a).clamp_min(0).numpy()[::-1]
    return dict(sampled_rows=len(rows),columns=x.shape[1],
        participation_ratio=float(eigen.sum()**2/max(np.square(eigen).sum(),1e-30)),
        variance_99_dimensions=int(np.searchsorted(np.cumsum(eigen)/eigen.sum(),.99)+1),
        singular_values_above_1e_minus_4_of_max=int(np.sum(eigen>eigen[0]*1e-8)))


def delayed_bit_probe(res, sequence):
    states=[];ratios=[];saturation=[]
    begin=time.perf_counter()
    for index,token in enumerate(sequence):
        if index%32==0 and res.recurrence:
            signal=torch.mv(res.matrix,torch.from_numpy(res.h)).numpy()*res.gain
            drive=res.bank[token,res.channels]*res.input_signs
            ratios.append(float(np.linalg.norm(signal)/max(np.linalg.norm(drive),1e-12)))
        states.append(res.step(int(token)))
        if index%32==0:saturation.append(float(np.mean(np.abs(res.h)>.95)))
    states=np.stack(states).astype(np.float64)
    delays=np.array([0,1,2,4,8,16,32])
    # Separate blocks with 64-step gaps, exceeding the largest tested delay.
    train=np.arange(128,128+1200);validation=np.arange(1392,1392+320);test=np.arange(1776,1776+640)
    targets=np.stack([(sequence-delayed_bit_probe.zero_token)[np.arange(len(sequence))-lag] for lag in delays],axis=1).astype(np.float64)
    means=states[train].mean(0);scales=states[train].std(0).clip(1e-6)
    x=(states-means)/scales
    ymean=targets[train].mean(0)
    gram=x[train].T@x[train]/len(train)
    eig,vec=np.linalg.eigh(gram)
    rhs=vec.T@(x[train].T@(targets[train]-ymean)/len(train))
    best=None;trials=[]
    for ridge in [1e-8,1e-6,1e-4,.01,1.,100.]:
        weights=vec@(rhs/(eig[:,None].clip(0)+ridge))
        error=np.square(x[validation]@weights+ymean-targets[validation]).mean()
        trials.append(dict(ridge=ridge,validation_mse=float(error)))
        if best is None or error<best[0]:best=(error,ridge,weights)
    predictions=x[test]@best[2]+ymean
    r2=1-np.square(predictions-targets[test]).sum(0)/np.square(targets[test]-targets[test].mean(0)).sum(0)
    return dict(seconds=time.perf_counter()-begin,train_examples=len(train),validation_examples=len(validation),test_examples=len(test),
        ridge_selected=best[1],ridge_trials=trials,
        delayed_bit_r2={str(k):float(v) for k,v in zip(delays,r2)},
        recurrent_to_input_norm_mean=float(np.mean(ratios)) if ratios else 0.,
        recurrent_to_input_norm_max=float(max(ratios)) if ratios else 0.,
        saturated_fraction_mean=float(np.mean(saturation)),
        pooled_state_rank=rank_metrics(states[train].astype(np.float32)))


def main():
    setup(7);run=latest_v2();config=read_json(run/'config.json');tok=Tokenizer.load(run/'tokenizer.json')
    output=ROOT/'diagnostics'/('backtrace-'+time.strftime('%Y%m%dT%H%M%S',time.gmtime()));output.mkdir(parents=True)
    plan=dict(created_at=now(),source_run=run.name,source_script_sha256=sha256(Path(__file__)),
        operations=['read-only cached-feature comparisons','fixed-checkpoint validation ablations','input-encoding/annotation inventory',
                    'synthetic delayed-bit linear probe on full frozen graph'],
        preserved='No graph edits, no coding model updates, no new final-test evaluation, no hosted LLM calls',
        probe='IID binary tokens, current pooled state only; train/validation/test blocks separated by 64 ticks. One synthetic stream seed. This is not a complete information-processing-capacity estimate.',
        probe_variants=['selected current reservoir','no recurrence, matched input/leak','gain-only target radius .9, matched input/leak'],
        probe_seed=91009,delays=[0,1,2,4,8,16,32])
    write_json(output/'plan.json',plan)
    (output/'backtrace_model.py').write_bytes(Path(__file__).read_bytes())
    artifacts=read_json(run/'artifacts.json')
    for name,digest in artifacts.items():
        if sha256(run/name)!=digest:raise ValueError('Saved artifact changed: '+name)
    result=dict(run=run.name,started_at=now(),architecture=dict(neurons=read_json(run/'graph.json')['neurons'],
        input_channels=256,pooled_state_features=config['features'],readout_input_features=config['features']*3+16,
        recurrent_weights='nonnegative recorded counts times a global gain',core_trainable_parameters=0,
        transmitter_annotations_used=False,selected_setting=config['selected_setting']))
    result['cached_features']={};result['validation_ablations']={}
    f=config['features']
    for split in ['train','validation']:
        a=np.load(run/f'features-fly-{split}.npz');b=np.load(run/f'features-no-recurrence-{split}.npz')
        x=a['x'];other=b['x'];y=a['y'];assert np.array_equal(y,b['y'])
        comparisons={}
        for label,start,end in [('current_state',0,f),('prompt_mean',f,2*f),('prompt_final',2*f,3*f)]:
            comparisons[label]=dict(relative_frobenius_difference=float(np.linalg.norm(x[:,start:end]-other[:,start:end])/np.linalg.norm(x[:,start:end])),
                                     rank=rank_metrics(x[:,start:end]) if label=='current_state' else None)
        result['cached_features'][split]=comparisons
        if split=='validation':
            offsets=read_json(run/'fly-validation-cache.json')['offsets']
            permutation=np.random.default_rng(810).permutation(len(offsets));shuffled=x.copy()
            for dest,source in zip(offsets,permutation):
                shuffled[dest['start']:dest['start']+dest['targets'],f:3*f]=x[offsets[source]['start'],f:3*f]
            for seed in config['seeds']:
                model=head(config,tok);model.load_state_dict(torch.load(run/f'fly-s{seed}.pt',weights_only=True));model.eval()
                baseline,pred=prediction_metrics(model,x,y)
                ablations=dict(baseline=baseline)
                for label,changed in [('recurrence_removed_same_head',other),('prompt_context_shuffled',shuffled)]:
                    metrics,pred2=prediction_metrics(model,changed,y);metrics['top1_changed_fraction']=float(np.mean(pred2!=pred));ablations[label]=metrics
                for label,start,end in [('context_at_training_mean',f,3*f),('current_state_at_training_mean',0,f)]:
                    changed=x.copy();changed[:,start:end]=model.mean.numpy()[start:end]
                    ablations[label],_=prediction_metrics(model,changed,y)
                categories={}
                for category,keep in [
                    ('digits',np.array([tok.pieces[int(t)].isdigit() for t in y])),
                    ('whitespace',np.array([bool(tok.pieces[int(t)]) and tok.pieces[int(t)].isspace() for t in y])),
                    ('eos',y==tok.eos)]:
                    categories[category]=dict(count=int(keep.sum()),accuracy=float(np.mean(pred[keep]==y[keep])) if keep.any() else None)
                ablations['selected_token_groups']=categories
                result['validation_ablations'][f'fly-s{seed}']=ablations
        del a,b,x,other,y
    result['same_generated_code']={}
    for seed in config['seeds']:
        group=[]
        for split in ['test','transfer','train-reproduction']:
            fly=read_json(run/f'fly-s{seed}-{split}-evaluation.json')['results'];control=read_json(run/f'no-recurrence-s{seed}-{split}-evaluation.json')['results']
            assert [r['problem']['id'] for r in fly]==[r['problem']['id'] for r in control]
            group.extend(a['code']==b['code'] for a,b in zip(fly,control))
        result['same_generated_code'][str(seed)]=dict(identical=sum(group),total=len(group))
    write_json(output/'results.json',result);print('Cached-feature and checkpoint diagnostics saved',flush=True)
    W,ids,graph=load_graph()
    nt_path=ROOT.parents[1]/'data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather'
    nt=feather.read_table(nt_path,columns=['body','consensus_nt','predicted_nt_confidence']).to_pydict()
    keep=set(int(i) for i in ids);mapping={int(id):(label,confidence) for id,label,confidence in zip(nt['body'],nt['consensus_nt'],nt['predicted_nt_confidence']) if id in keep}
    result['neurotransmitter_inventory']=dict(file=str(nt_path),sha256=sha256(nt_path),matched_neurons=len(mapping),
        missing_neurons=len(ids)-len(mapping),consensus_labels=dict(Counter(label or 'unknown' for label,confidence in mapping.values())),
        caution='Transmitter predictions do not directly measure synaptic efficacy or receptor-dependent sign. No signs applied in this diagnostic.')
    result['memory_probe']={}
    sequence=np.random.default_rng(91009).integers(0,2,size=2416)+ord('0');delayed_bit_probe.zero_token=ord('0')
    np.save(output/'probe_tokens.npy',sequence)
    for label,recurrence,setting in [
        ('selected',True,config['selected_setting']),
        ('no_recurrence',False,config['selected_setting']),
        ('gain_only_radius_0.9',True,{**config['selected_setting'],'target_radius':.9})]:
        print('Measuring',label,flush=True)
        res=reservoir(W,tok,config,setting,recurrence)
        result['memory_probe'][label]=delayed_bit_probe(res,sequence)
        write_json(output/'results.json',result);del res
    result['finished_at']=now();result['graph_integrity']=load_graph()[2]['neurons']==len(ids)
    for name,digest in artifacts.items():
        if sha256(run/name)!=digest:raise ValueError('Original artifact changed: '+name)
    result['original_artifacts_unchanged']=True
    write_json(output/'results.json',result)
    write_json(output/'manifest.json',{p.name:sha256(p) for p in output.iterdir() if p.is_file()})
    write_json(ROOT/'diagnostics/latest-backtrace.json',dict(directory=output.name))
    print(output,flush=True)


if __name__=='__main__':main()
