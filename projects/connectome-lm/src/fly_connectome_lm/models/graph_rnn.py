from __future__ import annotations
import math
import numpy as np
import torch
from torch import nn
from ..util import seed_for

class GraphRNN(nn.Module):
    """Only observed edge scalars are Parameters; indices are the fixed sparse mask."""
    def __init__(self, n: int, d: int, source: np.ndarray, target: np.ndarray,
                 seed: int = 1, alpha: float = .5, execution: str = 'dense',
                 counts: np.ndarray | None = None, initialization: str = 'uniform'):
        super().__init__()
        if execution not in ('dense', 'scatter', 'sparse'): raise ValueError(execution)
        if n < 1 or not 0 < alpha <= 1: raise ValueError('Invalid n or alpha')
        source, target = np.asarray(source, dtype=np.int64), np.asarray(target, dtype=np.int64)
        if source.shape != target.shape or source.ndim != 1: raise ValueError('Edge shape')
        if len(source) and (min(source.min(),target.min()) < 0 or max(source.max(),target.max()) >= n):
            raise ValueError('Out of range edge')
        if len(np.unique(target*n+source)) != len(source): raise ValueError('Duplicate edges')
        order = np.lexsort((source, target))
        source, target = source[order], target[order]
        self.n, self.d, self.alpha, self.execution = n, d, alpha, execution
        self.register_buffer('source', torch.tensor(source))
        self.register_buffer('target', torch.tensor(target))
        # Seed local initialization without consuming a global initialization stream.
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(seed_for('interfaces',seed))
            self.embedding = nn.Embedding(256,d)
            self.input = nn.Linear(d,n,bias=False)
            self.readout = nn.Linear(n,d,bias=False)
            self.output = nn.Linear(d,256,bias=True)
            nn.init.normal_(self.embedding.weight, std=.1)
            for layer in (self.input,self.readout,self.output): nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(self.output.bias)
        self.bias = nn.Parameter(torch.zeros(n))
        theta = torch.zeros(len(source))
        if initialization not in ('uniform','count','shuffled-count'): raise ValueError(initialization)
        if initialization != 'uniform':
            if counts is None or len(counts) != len(source): raise ValueError('Counts required')
            counts = np.asarray(counts)[order].copy()
        for row in range(n):  # Initialization only, never the forward path.
            loc = np.flatnonzero(target == row)
            if not len(loc): continue
            gen = torch.Generator().manual_seed(seed_for('incoming-slots', seed,row))
            v = torch.randn(len(loc),generator=gen)
            if initialization != 'uniform':
                c = counts[loc].copy()
                if initialization == 'shuffled-count':
                    np.random.default_rng(seed_for('count-shuffle',seed,row)).shuffle(c)
                v = v * torch.tensor(np.log1p(c), dtype=v.dtype)
            theta[loc] = .9 * v / torch.linalg.vector_norm(v)
        self.theta = nn.Parameter(theta)

    def dense_weight(self) -> torch.Tensor:
        return self.theta.new_zeros((self.n,self.n)).index_put((self.target,self.source),self.theta)

    def forward(self, tokens: torch.Tensor, state: torch.Tensor | None = None,
                return_states: bool = False, reset_each_byte: bool = False):
        h = self.theta.new_zeros((tokens.shape[0],self.n)) if state is None else state
        inputs = self.input(self.embedding(tokens))
        w = self.dense_weight() if self.execution == 'dense' else None
        if self.execution == 'sparse':
            w = torch.sparse_coo_tensor(torch.stack((self.target,self.source)),self.theta,
                                        (self.n,self.n),check_invariants=True).coalesce()
        states = []
        for t in range(tokens.shape[1]):
            if reset_each_byte: h = torch.zeros_like(h)
            if self.execution == 'dense': recurrent = h @ w.T
            elif self.execution == 'sparse': recurrent = torch.sparse.mm(w,h.T).T
            else:
                recurrent = h.new_zeros(h.shape).index_add(1,self.target,h[:,self.source]*self.theta)
            h = (1-self.alpha)*h + self.alpha*torch.tanh(recurrent + inputs[:,t] + self.bias)
            states.append(h)
        states = torch.stack(states,dim=1)
        logits = self.output(self.readout(states))
        return (logits,states) if return_states else logits

    def dense_reference(self, tokens: torch.Tensor):
        # Independent edge-to-matrix construction for tiny CPU float64 checks.
        basis = torch.nn.functional.one_hot(self.target*self.n+self.source,self.n*self.n).to(self.theta)
        w = (self.theta @ basis).reshape(self.n,self.n)
        h = self.theta.new_zeros((tokens.shape[0],self.n)); states=[]
        for t in range(tokens.shape[1]):
            x = self.embedding(tokens[:,t])
            h = (1-self.alpha)*h + self.alpha*torch.tanh(
                torch.nn.functional.linear(h,w) + torch.nn.functional.linear(x,self.input.weight) + self.bias)
            states.append(h)
        states = torch.stack(states,dim=1)
        return self.output(self.readout(states)),states

    def diagnostics(self, tokens: torch.Tensor | None = None) -> dict:
        with torch.no_grad():
            w = self.dense_weight().detach().double().cpu()
            vals = self.theta.detach().double().cpu()
            q = torch.ones(self.n,dtype=torch.float64) / math.sqrt(self.n)
            for _ in range(40):
                q = w.T @ (w @ q); q = q / q.norm().clamp_min(1e-30)
            out = {'edge_mean': vals.mean().item() if len(vals) else 0.,
                   'edge_std': vals.std(unbiased=False).item() if len(vals) else 0.,
                   'edge_quantiles': torch.quantile(vals,torch.tensor([0.,.25,.5,.75,1.],dtype=vals.dtype)).tolist() if len(vals) else [],
                   'row_norms': w.norm(dim=1).tolist(), 'spectral_norm_power_estimate': (w@q).norm().item()}
            if tokens is not None:
                _, states = self(tokens,return_states=True)
                out['state_saturation_fraction_abs_gt_0.95'] = (states.abs()>.95).float().mean().item()
                prev = torch.cat((states.new_zeros(states.shape[0],1,self.n),states[:,:-1]),dim=1)
                proposal = (states-(1-self.alpha)*prev)/self.alpha
                out['proposal_saturation_fraction_abs_gt_0.95'] = (proposal.abs()>.95).float().mean().item()
            return out
