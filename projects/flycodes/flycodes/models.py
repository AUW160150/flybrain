import numpy as np
import torch
from torch import nn

EOS = 256
VOCAB = 257

class Reservoir:
    """Scalar rate per neuron; immutable count matrix, fixed input and pooling maps."""
    def __init__(self, W, seed=7, features=1024, recurrence=True):
        self.W=W
        self.n=W.shape[0]
        self.features=features
        self.recurrence=recurrence
        rng=np.random.default_rng(seed)
        channels=rng.integers(0,64,size=self.n)
        signs=rng.choice(np.array([-1,1],np.float32),size=self.n)
        bank=rng.normal(0,.35,size=(256,64)).astype(np.float32)
        self.inputs=bank[:,channels]*signs
        self.bucket=rng.integers(0,features,size=self.n)
        self.pool_sign=rng.choice(np.array([-1,1],np.float32),size=self.n)
        self.pool_scale=np.sqrt(np.maximum(1,np.bincount(self.bucket,minlength=features)))
        self.gain=.9 / max(1,float(np.asarray(W.sum(axis=1)).max()))
        self.reset()

    def reset(self): self.h=np.zeros(self.n,np.float32)

    def step(self,byte):
        recurrent=(self.W @ self.h)*self.gain if self.recurrence else 0
        self.h=.5*self.h + .5*np.tanh(recurrent + self.inputs[int(byte)])
        return (np.bincount(self.bucket,weights=self.h*self.pool_sign,minlength=self.features)/self.pool_scale).astype(np.float32)

    def activity(self, ids, size=80):
        indices=np.linspace(0,self.n-1,min(size,self.n),dtype=int)
        return dict(mean_abs=float(np.abs(self.h).mean()),std=float(self.h.std()),
                    saturated_fraction=float((np.abs(self.h)>.95).mean()),
                    sample=[dict(body_id=str(ids[i]),value=float(self.h[i])) for i in indices])

class Readout(nn.Module):
    def __init__(self, features=1024):
        super().__init__()
        self.linear=nn.Linear(features,VOCAB)
        self.register_buffer('mean',torch.zeros(features))
        self.register_buffer('scale',torch.ones(features))
    def forward(self,x):return self.linear((x-self.mean)/self.scale)

class TinyTransformer(nn.Module):
    """Causal byte model, trained from scratch. Not called a pretrained LLM."""
    def __init__(self,width=96,layers=2,context=1024):
        super().__init__()
        self.context=context
        self.token=nn.Embedding(VOCAB,width)
        self.position=nn.Embedding(context,width)
        layer=nn.TransformerEncoderLayer(width,4,width*4,dropout=0,batch_first=True,norm_first=True)
        self.blocks=nn.TransformerEncoder(layer,layers,enable_nested_tensor=False)
        self.norm=nn.LayerNorm(width)
        self.head=nn.Linear(width,VOCAB)
    def forward(self,x):
        length=x.shape[1]
        h=self.token(x)+self.position(torch.arange(length,device=x.device))
        mask=torch.triu(torch.ones(length,length,dtype=torch.bool,device=x.device),diagonal=1)
        return self.head(self.norm(self.blocks(h,mask=mask)))

def parameter_count(model):return sum(p.numel() for p in model.parameters() if p.requires_grad)
