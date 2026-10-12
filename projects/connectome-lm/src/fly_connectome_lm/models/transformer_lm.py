import torch
from torch import nn
from ..util import seed_for

class TransformerLM(nn.Module):
    """Optional conventional causal baseline, not part of the graph arms."""
    def __init__(self,d:int,ff:int,layers:int,context:int,seed:int=1):
        super().__init__(); self.context=context; self.d=d; self.ff=ff; self.layers=layers
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed_for('transformer',seed))
            self.embedding=nn.Embedding(256,d); self.position=nn.Embedding(context,d)
            self.blocks=nn.ModuleList([nn.TransformerEncoderLayer(d,4,ff,dropout=0.,batch_first=True) for _ in range(layers)])
            self.readout=nn.Linear(d,d,bias=False); self.output=nn.Linear(d,256)
            nn.init.normal_(self.embedding.weight,std=.1); nn.init.normal_(self.position.weight,std=.1)
            nn.init.xavier_uniform_(self.readout.weight); nn.init.xavier_uniform_(self.output.weight)
            nn.init.zeros_(self.output.bias)
    def forward(self,tokens:torch.Tensor,reset_each_byte:bool=False):
        if reset_each_byte:
            return torch.cat([self(tokens[:,i:i+1]) for i in range(tokens.shape[1])],dim=1)
        t=tokens.shape[1]
        if t>self.context: raise ValueError('Context limit')
        x=self.embedding(tokens)+self.position(torch.arange(t,device=tokens.device))
        mask=torch.ones(t,t,dtype=torch.bool,device=tokens.device).triu(1)
        for block in self.blocks: x=block(x,src_mask=mask)
        return self.output(self.readout(x))

def choose_transformer(d:int,context:int,target:int) -> tuple[int,int,int]:
    candidates=[]
    for layers in range(1,5):
        for ff in range(4,2049,4):
            count=512*d+context*d+d*d+256+layers*(4*d*d+9*d+(2*d+1)*ff)
            candidates.append((abs(count-target),layers,ff,count))
    _,layers,ff,count=min(candidates)
    if abs(count-target)/target>.05: raise ValueError('No transformer within 5%')
    return layers,ff,count
