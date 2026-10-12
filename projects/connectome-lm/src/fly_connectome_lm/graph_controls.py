from __future__ import annotations
import numpy as np
from .graph_extract import Graph,diagnostics

class InvalidControl(RuntimeError):
    def __init__(self,message:str,diagnostic:dict): super().__init__(message); self.diagnostic=diagnostic

def degrees(graph:Graph):
    return np.bincount(graph.source,minlength=len(graph.ids)),np.bincount(graph.target,minlength=len(graph.ids))

def rewire(original:Graph,seed:int,swaps_per_edge:int=20,attempts_per_edge:int=500) -> Graph:
    """Instrumented directed three-edge path swap, including 3-cycle reversals.

    Start sampled proportional to total degree, then outgoing neighbors uniformly.
    Reject EVERY proposed self-loop/parallel edge. Count every start draw as one
    proposal, including dead ends. No connectivity or language-based rejection.
    """
    n=len(original.ids); e=len(original.source)
    if e<3 or n<4: raise InvalidControl('Too few edges/nodes for policy',{'valid':False})
    rng=np.random.default_rng(seed)
    outgoing=[{} for _ in range(n)]
    for s,t in zip(original.source,original.target): outgoing[int(s)][int(t)]=None
    degree_out,degree_in=degrees(original)
    cdf=np.cumsum(degree_out+degree_in)/float(2*e)
    accepted=0; proposed=0; target=swaps_per_edge*e; maximum=attempts_per_edge*e
    checkpoints=[]; milestones=set([0,e,5*e,10*e,target])
    def snapshot():
        s=[]; t=[]
        for a,row in enumerate(outgoing):
            for b in row: s.append(a);t.append(b)
        return Graph(original.ids.copy(),np.array(s,dtype=np.int64),np.array(t,dtype=np.int64),
                     np.ones(e,dtype=np.int64),{'condition':'DEGREE-REWIRED'})
    checkpoints.append({'accepted':0,'proposals':0,**diagnostics(snapshot(),original)})
    while accepted<target and proposed<maximum:
        proposed+=1
        a=int(np.searchsorted(cdf,rng.random(),side='right'))
        if not outgoing[a]: continue
        b=int(rng.choice(list(outgoing[a])))
        if not outgoing[b]: continue
        c=int(rng.choice(list(outgoing[b])))
        if not outgoing[c]: continue
        d=int(rng.choice(list(outgoing[c])))
        old=((a,b),(b,c),(c,d)); new=((a,c),(c,b),(b,d))
        if len(set(old))!=3 or len(set(new))!=3: continue
        if any(s==t or t in outgoing[s] for s,t in new): continue
        for s,t in old: del outgoing[s][t]
        for s,t in new: outgoing[s][t]=None
        accepted+=1
        if accepted in milestones:
            checkpoints.append({'accepted':accepted,'proposals':proposed,**diagnostics(snapshot(),original)})
    graph=snapshot()
    info={'null_seed':seed,'method':'directed three-edge path swap a->b->c->d to a->c->b->d, loop-free guard',
          'proposal_definition':'one start-node draw, including dead ends and all rejections',
          'accepted_swaps':accepted,'proposals':proposed,'required_swaps':target,'maximum_proposals':maximum,
          'valid':accepted==target,'checkpoints':checkpoints,'mixing_note':'Fixed swaps do not prove uniformity or mixing'}
    for before,after in zip(degrees(original),degrees(graph)):
        if not np.array_equal(before,after): raise AssertionError('Degree changed')
    changed=not np.array_equal(original.source* n+original.target,graph.source*n+graph.target)
    info['partners_changed']=changed
    if accepted!=target or not changed:
        info['valid']=False
        raise InvalidControl('Rewiring did not meet declared policy; control invalid',info)
    graph.metadata={**original.metadata,'condition':'DEGREE-REWIRED','original_graph_hash':original.hash,'randomization':info,
                    'counts_note':'ones are placeholders; contact counts are not used for randomized topology'}
    return graph

def random_density(original:Graph,seed:int) -> Graph:
    n=len(original.ids); e=len(original.source); rng=np.random.default_rng(seed)
    flat=rng.choice(n*(n-1),e,replace=False); s=flat//(n-1); t=flat%(n-1); t=t+(t>=s)
    return Graph(original.ids.copy(),s,t,np.ones(e,dtype=np.int64),
                 {**original.metadata,'condition':'RANDOM-DENSITY','original_graph_hash':original.hash,'null_seed':seed,
                  'method':'uniform E-subset of all N*(N-1) ordered loop-free pairs',
                  'counts_note':'ones are placeholders; no anatomical counts'})
