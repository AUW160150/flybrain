"""Untrained educational references. Never imported by the experiment."""
import torch
from torch import nn
from torch.nn import functional as F

class WindowMLP(nn.Module):
    def __init__(self,window=8,d=16,width=64):
        super().__init__(); self.window=window
        self.embedding=nn.Embedding(256,d)
        self.hidden1=nn.Linear(window*d,width); self.hidden2=nn.Linear(width,width); self.output=nn.Linear(width,256)
    def forward(self,tokens):
        x=self.embedding(tokens); x=F.pad(x,(0,0,self.window-1,0))
        # unfold appends window dimension after embedding dimension.
        windows=x.unfold(1,self.window,1).transpose(-1,-2).flatten(-2)
        return self.output(torch.relu(self.hidden2(torch.relu(self.hidden1(windows)))))

class CausalCNN(nn.Module):
    def __init__(self,d=16,channels=32,kernel=3):
        super().__init__(); self.kernel=kernel
        self.embedding=nn.Embedding(256,d); self.conv1=nn.Conv1d(d,channels,kernel,dilation=1); self.conv2=nn.Conv1d(channels,channels,kernel,dilation=2); self.output=nn.Linear(channels,256)
    def forward(self,tokens):
        x=self.embedding(tokens).transpose(1,2)
        x=torch.relu(self.conv1(F.pad(x,(self.kernel-1,0))))
        x=torch.relu(self.conv2(F.pad(x,(2*(self.kernel-1),0))))
        return self.output(x.transpose(1,2))

def parameter_inventory(model):
    entries=[]; seen=set()
    for name,p in model.named_parameters(remove_duplicate=False):
        if id(p) in seen: continue
        seen.add(id(p)); entries.append(dict(name=name,shape=list(p.shape),elements=p.numel(),trainable=p.requires_grad))
    return dict(parameters=entries,active_trainable=sum(x['elements'] for x in entries if x['trainable']),frozen=sum(x['elements'] for x in entries if not x['trainable']),nontrainable_storage_bytes=sum(b.numel()*b.element_size() for b in model.buffers()))

def shape_and_causality(model):
    model.eval(); a=torch.tensor([[97,98,99,32,100,101,102,46]]); b=a.clone(); b[:,5:]=255
    with torch.inference_mode():
        x=model(a); y=model(b)
    assert x.shape==(1,8,256)
    error=float((x[:,:5]-y[:,:5]).abs().max()); assert error<1e-6
    return dict(shape=list(x.shape),prefix_max_abs_error=error,status='passed',input_bytes=a[0].tolist(),changed_suffix_start=5)
