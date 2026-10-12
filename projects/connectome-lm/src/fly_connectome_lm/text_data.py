from __future__ import annotations
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import hashlib
import numpy as np
import torch
from .util import atomic_json, sha256, read_json

SPLITS=('train','validation','test')

def split_offsets(length:int) -> dict[str,tuple[int,int]]:
    a,b=length*90//100,length*95//100
    if min(a,b-a,length-b)<2: raise ValueError('Corpus too short')
    return {'train':(0,a),'validation':(a,b),'test':(b,length)}

def duplicate_spans(parts:dict[str,bytes],minimum:int=256) -> dict:
    """Exact byte matches, all offsets, extended maximal spans; rolling hashes are verified.

    Index smaller split. Hash collisions never become reported matches. Distinct
    occurrences are retained, but overlapping hits on one alignment are merged.
    """
    result={}
    mask=(1<<64)-1; base=257; power=pow(base,minimum-1,1<<64)
    def hashes(data):
        if len(data)<minimum: return
        value=0
        for v in data[:minimum]: value=(value*base+v+1)&mask
        yield 0,value
        for i in range(1,len(data)-minimum+1):
            value=(((value-(data[i-1]+1)*power)&mask)*base+data[i+minimum-1]+1)&mask
            yield i,value
    for name_a,name_b in combinations(parts,2):
        a,b=parts[name_a],parts[name_b]; index=defaultdict(list)
        for j,h in hashes(b): index[h].append(j)
        spans=[]; ends={}
        for i,h in hashes(a):
            for j in index.get(h,()):
                diagonal=j-i
                if i<ends.get(diagonal,-1): continue
                if a[i:i+minimum]!=b[j:j+minimum]: continue
                length=minimum
                while i+length<len(a) and j+length<len(b) and a[i+length]==b[j+length]: length+=1
                spans.append({'a_offset':i,'b_offset':j,'length':length,
                              'sha256':hashlib.sha256(a[i:i+length]).hexdigest()})
                ends[diagonal]=i+length-minimum+1
        result[f'{name_a}:{name_b}']={'count':len(spans),'spans':spans}
    return result

def prepare_text(raw:Path,out:Path,source_manifest:dict) -> dict:
    out.mkdir(parents=True,exist_ok=True)
    data=raw.read_bytes(); data.decode('utf-8',errors='strict')
    offsets=split_offsets(len(data)); parts={k:data[a:b] for k,(a,b) in offsets.items()}
    manifest={'source':source_manifest,'source_sha256':sha256(raw),'transformations':[],
              'encoding':'exact UTF-8 bytes, vocabulary 0..255','length':len(data),'splits':{}}
    for name,part in parts.items():
        path=out/f'{name}.bin'
        if path.exists() and path.read_bytes()!=part: raise ValueError('Refusing to replace different corpus')
        path.write_bytes(part)
        manifest['splits'][name]={'offsets':list(offsets[name]),'length':len(part),'sha256':sha256(path)}
    manifest['cross_split_duplicates_256']=duplicate_spans(parts)
    atomic_json(out/'manifest.json',manifest)
    return manifest

class DevelopmentCorpus:
    """Training/tuning API deliberately has no test member or test selector."""
    def __init__(self,path:Path):
        self.path=Path(path); self.manifest=read_json(path/'manifest.json')
        self.train=self._read_development('train')
        self.validation=self._read_development('validation')
    def _read_development(self,name:str) -> np.ndarray:
        if name not in ('train','validation'): raise PermissionError('Test data sealed')
        path=self.path/f'{name}.bin'
        if sha256(path)!=self.manifest['splits'][name]['sha256']: raise ValueError('Split hash mismatch')
        return np.frombuffer(path.read_bytes(),dtype=np.uint8).copy()

class WindowSampler:
    def __init__(self,data:np.ndarray,context:int,batch:int,seed:int):
        if context<1 or batch<1 or len(data)<context+1: raise ValueError('Insufficient split length')
        self.data=data; self.context=context; self.batch=batch
        self.rng=np.random.default_rng(seed); self.draws=0
    def next(self) -> tuple[torch.Tensor,torch.Tensor]:
        starts=self.rng.integers(0,len(self.data)-self.context,size=self.batch)
        windows=self.data[starts[:,None]+np.arange(self.context+1)[None,:]].astype(np.int64)
        self.draws+=self.batch
        return torch.from_numpy(windows[:,:-1].copy()),torch.from_numpy(windows[:,1:].copy())
    def state_dict(self): return {'rng':self.rng.bit_generator.state,'draws':self.draws}
    def load_state_dict(self,state): self.rng.bit_generator.state=state['rng']; self.draws=state['draws']

def evaluation_blocks(data:np.ndarray,context:int,batch:int=32):
    if len(data)<2 or context<1 or batch<1: raise ValueError('Invalid evaluation split/context')
    starts=np.arange(0,len(data)-1,context)
    for pos in range(0,len(starts),batch):
        group=starts[pos:pos+batch]
        indices=group[:,None]+np.arange(context)[None,:]
        mask=indices+1<len(data)
        x=np.where(mask,data[np.minimum(indices,len(data)-1)],0).astype(np.int64)
        y=np.where(mask,data[np.minimum(indices+1,len(data)-1)],0).astype(np.int64)
        yield torch.from_numpy(x),torch.from_numpy(y),torch.from_numpy(mask)
