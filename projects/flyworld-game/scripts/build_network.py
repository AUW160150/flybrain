"""Build a signed sparse connectome from the MaleCNS v1.0 flat files and save it as NPZ.
Nodes: Traced neurons. Edges: weight>=MIN_W synapses. Sign: +1 ACh, -1 GABA/Glu, 0/+1 others."""
import pyarrow.feather as pf, pandas as pd, numpy as np, time, sys
MIN_W = int(sys.argv[1]) if len(sys.argv) > 1 else 1
D = "data/flat-connectome/"
ann = pf.read_feather(D+"body-annotations-male-cns-v1.0-minconf-0.5.feather")
nt  = pf.read_feather(D+"body-neurotransmitters-male-cns-v1.0.feather")[["body","consensus_nt"]]
w   = pf.read_feather(D+"connectome-weights-male-cns-v1.0-minconf-0.5.feather")

nodes = ann[ann.status=="Traced"].merge(nt, left_on="bodyId", right_on="body", how="left")
nodes = nodes.reset_index(drop=True)
idx = pd.Series(nodes.index.values, index=nodes.bodyId.values)
sign_map = {"acetylcholine":1.0,"gaba":-1.0,"glutamate":-1.0,"histamine":-1.0,
            "dopamine":0.0,"octopamine":0.0,"serotonin":0.0,"unclear":1.0}
nodes["sign"] = nodes.consensus_nt.map(sign_map).fillna(1.0)

e = w[w.body_pre.isin(idx.index) & w.body_post.isin(idx.index) & (w.weight>=MIN_W)]
pre  = idx[e.body_pre.values].values.astype(np.int32)
post = idx[e.body_post.values].values.astype(np.int32)
wt   = e.weight.values.astype(np.float32) * nodes.sign.values[pre].astype(np.float32)
np.savez_compressed(f"processed/malecns_v1.0_traced_minw{MIN_W}.npz",
    pre=pre, post=post, weight=wt, body_id=nodes.bodyId.values,
    type=nodes.type.fillna("").values.astype(str), superclass=nodes.superclass.fillna("").values.astype(str),
    cls=nodes["class"].fillna("").values.astype(str), side=nodes.somaSide.fillna("").values.astype(str),
    nt=nodes.consensus_nt.fillna("").values.astype(str))
print(f"saved: {len(nodes):,} neurons, {len(pre):,} edges, min weight {MIN_W}")
print("sign mix:", {k:int((nodes.sign==v).sum()) for k,v in [("exc",1.0),("inh",-1.0),("neutral",0.0)]})
