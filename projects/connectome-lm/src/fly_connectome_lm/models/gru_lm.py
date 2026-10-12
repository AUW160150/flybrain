import torch
from torch import nn
from ..util import seed_for

class GRULM(nn.Module):
    def __init__(self,d:int,h:int,seed:int=1):
        super().__init__(); self.h=h; self.d=d
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed_for('gru',seed))
            self.embedding=nn.Embedding(256,d)
            self.gru=nn.GRU(d,h,batch_first=True)
            self.readout=nn.Linear(h,d,bias=False)
            self.output=nn.Linear(d,256)
            nn.init.normal_(self.embedding.weight,std=.1)
            nn.init.xavier_uniform_(self.readout.weight); nn.init.xavier_uniform_(self.output.weight)
            for name,p in self.named_parameters():
                if 'bias' in name: nn.init.zeros_(p)
    def forward(self,tokens:torch.Tensor,reset_each_byte:bool=False):
        x=self.embedding(tokens)
        if reset_each_byte:
            h=torch.cat([self.gru(x[:,i:i+1])[0] for i in range(x.shape[1])],dim=1)
        else: h,_=self.gru(x)
        return self.output(self.readout(h))

def choose_gru(d:int,target:int) -> tuple[int,int]:
    # All actual model parameters participate in forward/backpropagation.
    candidates=[]
    for h in range(1,2049):
        count=512*d+256+3*h*d+3*h*h+6*h+d*h
        candidates.append((abs(count-target),h,count))
    _,h,count=min(candidates)
    if abs(count-target)/target > .05: raise ValueError('No GRU width within 5%')
    return h,count
