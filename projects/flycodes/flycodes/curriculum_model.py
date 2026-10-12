"""Frozen graph, lossless lexical tokens, explicit prompt memory, learned nonlinear readout."""
import re
from collections import Counter
import numpy as np
import torch
from torch import nn
from .common import write_json,read_json

LEX=re.compile(r'[A-Za-z_][A-Za-z_0-9]*|\d+|\s+|[^\w\s]',re.UNICODE)

class Tokenizer:
    # Byte fallback guarantees lossless handling of unknown words and Unicode.
    eos=256
    def __init__(self,pieces):
        self.pieces=[bytes([i]) for i in range(256)]+[b'']+[x.encode('utf-8') for x in pieces]
        self.lookup={x:i for i,x in enumerate(self.pieces) if i!=self.eos}
    @classmethod
    def fit(cls,texts,max_words=1536):
        counts=Counter(piece for text in texts for piece in LEX.findall(text) if len(piece.encode())>1)
        pieces=[p for p,n in sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:max_words]]
        return cls(pieces)
    def encode(self,text):
        # Regex spans can omit non-ASCII word characters; split around spans and use bytes.
        out=[];end=0
        for match in LEX.finditer(text):
            if match.start()>end:out.extend(text[end:match.start()].encode())
            piece=match.group().encode();token=self.lookup.get(piece)
            out.extend([token] if token is not None else list(piece));end=match.end()
        out.extend(text[end:].encode());return out
    def decode(self,tokens):return b''.join(self.pieces[t] for t in tokens if t!=self.eos).decode('utf-8',errors='replace')
    def save(self,path):write_json(path,dict(kind='lossless_lexical_v1',pieces=[x.decode() for x in self.pieces[257:]]))
    @classmethod
    def load(cls,path):return cls(read_json(path)['pieces'])
    def __len__(self):return len(self.pieces)

def estimate_radius(W,max_iter=250,tolerance=2e-6):
    v=np.full(W.shape[0],1/np.sqrt(W.shape[0]),np.float32)
    for i in range(max_iter):
        y=W@v;radius=float(np.linalg.norm(y));new=y/max(radius,1e-12)
        difference=float(np.linalg.norm(new-v));v=new
        if difference<tolerance:break
    residual=float(np.linalg.norm(W@v-radius*v)/max(radius,1e-12))
    if residual>1e-4:raise ValueError('Power iteration did not converge')
    return dict(radius=radius,iterations=i+1,relative_residual=residual,method='positive-vector power iteration, float32')

class CodingReservoir:
    def __init__(self,W,vocab,seed=7,features=768,radius=6031.84,target_radius=.9,leak=.5,input_scale=.1,recurrence=True):
        self.W=W;self.n=W.shape[0];self.features=features;self.recurrence=recurrence
        self.gain=target_radius/radius;self.leak=leak
        rng=np.random.default_rng(seed)
        # Each input uses a fixed, distributed pattern; no embedding learns.
        channels=rng.integers(0,256,size=self.n)
        signs=rng.choice(np.array([-1,1],np.float32),size=self.n)
        bank=rng.normal(0,input_scale,size=(vocab,256)).astype(np.float32)
        # Lazy input cache avoids an O(vocabulary * neurons) allocation.
        self.bank=bank;self.channels=channels;self.input_signs=signs
        self.input_cache={}
        self.bucket=rng.integers(0,features,size=self.n)
        self.pool_sign=rng.choice(np.array([-1,1],np.float32),size=self.n)
        self.pool_scale=np.sqrt(np.maximum(1,np.bincount(self.bucket,minlength=features)))
        self.matrix=torch.sparse_csr_tensor(torch.tensor(W.indptr,dtype=torch.int64),
                    torch.tensor(W.indices,dtype=torch.int64),torch.tensor(W.data),size=W.shape,check_invariants=True) if recurrence else None
        self.reset()
    def reset(self):self.h=np.zeros(self.n,np.float32)
    def pool(self):
        return (np.bincount(self.bucket,weights=self.h*self.pool_sign,minlength=self.features)/self.pool_scale).astype(np.float32)
    def step(self,token):
        if token not in self.input_cache:
            if len(self.input_cache)>=128:self.input_cache.pop(next(iter(self.input_cache)))
            self.input_cache[token]=self.bank[token,self.channels]*self.input_signs
        signal=torch.mv(self.matrix,torch.from_numpy(self.h)).numpy()*self.gain if self.recurrence else 0
        self.h=(1-self.leak)*self.h+self.leak*np.tanh(signal+self.input_cache[token])
        return self.pool()
    def encode_prompt(self,tokens):
        self.reset();total=np.zeros(self.features,np.float32)
        for token in tokens:
            state=self.step(token);total+=state
        return np.concatenate([total/max(1,len(tokens)),state])
    def feature(self,context,position):
        frequencies=np.exp(np.linspace(np.log(.01),np.log(1.),8)).astype(np.float32)
        position_features=np.concatenate([np.sin(position*frequencies),np.cos(position*frequencies)])
        return np.concatenate([self.pool(),context,position_features]).astype(np.float32)
    def activity(self,ids,size=80):
        ix=np.linspace(0,self.n-1,min(size,self.n),dtype=int)
        return dict(mean_abs=float(np.abs(self.h).mean()),std=float(self.h.std()),saturated_fraction=float((np.abs(self.h)>.95).mean()),
                    sample=[dict(body_id=str(ids[i]),value=float(self.h[i])) for i in ix])

class CodeReadout(nn.Module):
    def __init__(self,features,vocab,hidden=384):
        super().__init__();self.input_features=features
        self.register_buffer('mean',torch.zeros(features));self.register_buffer('scale',torch.ones(features))
        self.net=nn.Sequential(nn.Linear(features,hidden),nn.GELU(),nn.Linear(hidden,hidden),nn.GELU(),nn.Linear(hidden,vocab))
    def forward(self,x):return self.net((x-self.mean)/self.scale)
