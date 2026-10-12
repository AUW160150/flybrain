"""Sealed test capability, deliberately separate from training/tuning commands."""
from pathlib import Path
import torch
from .experiment import validate_freeze,CORPUS,matrix,base_graph,resolved_graph
from .evaluate import FinalTestCorpus,evaluate,ngram_references
from .models import build
from .text_data import DevelopmentCorpus
from .util import ROOT,read_json,atomic_json,digest,sha256,setup,now

def final_evaluate(freeze_path:Path) -> dict:
    freeze=read_json(freeze_path); config=freeze['config']; optional=tuple(freeze['optional']); rates=freeze['learning_rates']
    validate_freeze(freeze,config,optional,rates)
    if config['profile'] not in ('confirmation','replication'): raise PermissionError('No pilot test access')
    rows=matrix(config,False,optional,rates)
    # Validate the COMPLETE design before opening any test byte.
    for row in rows:
        run_dir=ROOT/'runs'/row['run_id']
        if not (run_dir/'result.json').exists(): raise PermissionError(f'Incomplete frozen matrix: {row["run_id"]}')
        manifest=read_json(run_dir/'manifest.json'); result=read_json(run_dir/'result.json')
        if manifest['status']!='complete' or manifest['code_hash']!=freeze['code_hash'] or result['config_hash']!=digest(row['config']):
            raise PermissionError('Incomplete or mismatched run')
        if row['config'].get('protocol')!='fixed-time' and result['final_step']!=row['config']['updates']: raise PermissionError('Incomplete byte budget')
        for kind,expected_step in [('best',result['selected_checkpoint_step']),('final',result['final_step'])]:
            checkpoint=torch.load(run_dir/f'{kind}.pt',map_location='cpu',weights_only=False)
            if checkpoint['signature']!=manifest['signature'] or checkpoint['code_hash']!=freeze['code_hash'] or checkpoint['step']!=expected_step:
                raise PermissionError('Checkpoint does not match its frozen run/selected step')
        if (run_dir/'test.json').exists():
            old=read_json(run_dir/'test.json')
            for kind in ['best','final']:
                if sha256(run_dir/f'{kind}.pt')!=old['checkpoint_sha256'][kind]:
                    raise PermissionError('Checkpoint changed after test evaluation')
    setup(config['device'],config['threads'])
    corpus=FinalTestCorpus(CORPUS,freeze,digest(freeze)); results=[]
    for row in rows:
        run_dir=ROOT/'runs'/row['run_id']; out=run_dir/'test.json'
        if out.exists():
            old=read_json(out)
            # Completed confirmation sample101 can be reused by a compatible replication freeze.
            if old['code_hash']!=freeze['code_hash'] or old['corpus_manifest_sha256']!=freeze['corpus_manifest_sha256']:
                raise PermissionError('Existing test artifact belongs to another frozen study')
            results.append(old); continue
        graph=resolved_graph(row,base_graph(config,row['sampling_seed']))
        model=build(row['condition'],graph,row['config'],row['training_seed']).to(config['device'])
        scores={}; hashes={}
        for kind in ['best','final']:
            path=run_dir/f'{kind}.pt'; checkpoint=torch.load(path,map_location='cpu',weights_only=False)
            if checkpoint['code_hash']!=freeze['code_hash']: raise PermissionError('Checkpoint code mismatch')
            model.load_state_dict(checkpoint['model'])
            scores[kind]=evaluate(model,corpus.data,config['context'],config['evaluation_batch'])
            hashes[kind]=sha256(path)
        record={'run_id':row['run_id'],'condition':row['condition'],'sampling_seed':row['sampling_seed'],
                'training_seed':row['training_seed'],'null_index':row['null_index'],'best':scores['best'],'final':scores['final'],
                'checkpoint_sha256':hashes,'freeze_sha256':sha256(freeze_path),'evaluated_utc':now(),
                'code_hash':freeze['code_hash'],'corpus_manifest_sha256':freeze['corpus_manifest_sha256']}
        atomic_json(out,record); results.append(record)
    refs=ngram_references(DevelopmentCorpus(CORPUS).train,corpus.data)
    summary={'freeze_sha256':sha256(freeze_path),'records':results,'train_only_ngram_test':refs}
    path=ROOT/'reports'/f'final-evaluation-{sha256(freeze_path)[:12]}.json'
    if not path.exists(): atomic_json(path,summary)
    return summary
