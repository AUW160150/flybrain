from __future__ import annotations
import math
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
from .text_data import evaluation_blocks
from .util import sha256,read_json

def metrics(nll:float,count:int,correct:int) -> dict:
    if count<=0 or not math.isfinite(nll): raise ValueError('Invalid scored loss')
    bpb=nll/count/math.log(2)
    return {'nll_sum':nll,'scored_bytes':count,'bpb':bpb,'byte_perplexity':2**bpb,'accuracy':correct/count}

@torch.no_grad()
def evaluate(model,data:np.ndarray,context:int,batch:int=32,reset_each_byte:bool=False) -> dict:
    model.eval(); device=next(model.parameters()).device
    nll=0.; count=0; correct=0
    for x,y,mask in evaluation_blocks(data,context,batch):
        x,y,mask=x.to(device),y.to(device),mask.to(device)
        logits=model(x,reset_each_byte=reset_each_byte)
        losses=F.cross_entropy(logits.flatten(0,1),y.flatten(),reduction='none').reshape_as(y)
        nll+=losses[mask].double().sum().item(); count+=mask.sum().item()
        correct+=((logits.argmax(-1)==y)&mask).sum().item()
    assert count==len(data)-1
    return metrics(nll,count,correct)

class FinalTestCorpus:
    """Only final-evaluate imports/instantiates this capability after verifying freeze."""
    def __init__(self,path:Path,freeze:dict,expected_freeze_hash:str):
        from .util import digest
        if digest(freeze)!=expected_freeze_hash or freeze.get('profile') not in ('confirmation','replication'):
            raise PermissionError('Explicit confirmation/replication freeze required')
        manifest=read_json(path/'manifest.json')
        if sha256(path/'manifest.json')!=freeze['corpus_manifest_sha256']:
            raise PermissionError('Frozen corpus changed')
        p=path/'test.bin'
        if sha256(p)!=manifest['splits']['test']['sha256']: raise ValueError('Test hash mismatch')
        self.data=np.frombuffer(p.read_bytes(),dtype=np.uint8).copy()

def ngram_references(train:np.ndarray,evaluation:np.ndarray,smoothing:float=1.) -> dict:
    if smoothing<=0: raise ValueError('Positive smoothing required')
    unigram=np.bincount(train,minlength=256).astype(float)+smoothing
    unigram/=unigram.sum()
    bigram=np.bincount(train[:-1].astype(np.int64)*256+train[1:],minlength=65536).reshape(256,256).astype(float)+smoothing
    bigram/=bigram.sum(1,keepdims=True)
    y=evaluation[1:]; p=bigram[evaluation[:-1],y]
    return {'unigram':metrics(float(-np.log(unigram[y]).sum()),len(y),int((y==unigram.argmax()).sum())),
            'bigram':metrics(float(-np.log(p).sum()),len(y),int((bigram[evaluation[:-1]].argmax(1)==y).sum())),
            'smoothing':smoothing,'fit_split':'train only'}
