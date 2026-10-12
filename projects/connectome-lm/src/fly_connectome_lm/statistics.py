from __future__ import annotations
from collections import defaultdict
import numpy as np

def interpretation(mean:float,low:float,high:float) -> str:
    if low>.02: return 'Evidence of a practical advantage under this protocol; replication required.'
    if mean<0: return 'Fly wiring may be worse under this protocol; inspect uncertainty.'
    if low>=-.02 and high<=.02: return 'No substantial advantage established here.'
    return 'Inconclusive; a positive estimate with a wide interval is not established benefit.'

def paired_effects(records:list[dict],nulls_per_seed:int=3,bootstrap_seed:int=1729) -> dict:
    groups=defaultdict(list)
    for r in records: groups[(r['sampling_seed'],r['training_seed'])].append(r)
    deltas=defaultdict(list); incomplete=[]; pairs=[]
    for (graph,seed),rows in sorted(groups.items()):
        flies=[r for r in rows if r['condition']=='FLY-TOPOLOGY']
        nulls=[r for r in rows if r['condition']=='DEGREE-REWIRED']
        if len(flies)!=1 or len(nulls)!=nulls_per_seed or len({r['null_index'] for r in nulls})!=nulls_per_seed:
            incomplete.append({'graph':graph,'seed':seed,'flies':len(flies),'nulls':len(nulls)}); continue
        fly=flies[0]['bpb']; control=[r['bpb'] for r in nulls]; delta=float(np.mean(control)-fly)
        deltas[graph].append(delta); pairs.append({'sampling_seed':graph,'training_seed':seed,'fly_bpb':fly,'rewired_bpbs':control,'delta':delta})
    rng=np.random.default_rng(bootstrap_seed); per_graph={}
    for graph,values in deltas.items():
        x=np.array(values); samples=rng.choice(x,size=(10000,len(x)),replace=True).mean(1)
        low,high=np.quantile(samples,[.025,.975]); mean=float(x.mean())
        per_graph[str(graph)]={'mean_delta':mean,'ci95':[float(low),float(high)],'training_seed_count':len(x),
                              'interpretation':interpretation(mean,low,high) if len(x)>=5 else 'Insufficient confirmation seeds; descriptive only.'}
    hierarchy=None
    if len(deltas)>1:
        keys=sorted(deltas); samples=[]
        for _ in range(10000):
            graphs=rng.choice(keys,len(keys),replace=True)
            samples.append(float(np.mean([rng.choice(deltas[g],len(deltas[g]),replace=True).mean() for g in graphs])))
        hierarchy={'mean_delta':float(np.mean([np.mean(v) for v in deltas.values()])),
                   'ci95':np.quantile(samples,[.025,.975]).tolist(),
                   'note':'Resamples graphs then paired training seeds. Overlapping samples from one specimen, not population inference across flies.'}
    return {'pairs':pairs,'per_graph':per_graph,'hierarchical':hierarchy,'incomplete_pairs':incomplete,
            'resamples':10000,'bootstrap_seed':bootstrap_seed,'warning':'Five seeds offer limited uncertainty; never bootstrap individual test bytes.'}
