"""Leaky integrate-and-fire simulation of the whole traced MaleCNS on Apple MPS (or CPU).
Stimulates the giant fiber (DNp01) and reports which cell types respond."""
import numpy as np, torch, time, sys, collections
f = sys.argv[1] if len(sys.argv)>1 else "processed/malecns_v1.0_traced_minw1.npz"
dev = "mps" if torch.backends.mps.is_available() else "cpu"
z = np.load(f, allow_pickle=True); N=len(z["body_id"]); E=len(z["pre"])
pre=torch.tensor(z["pre"],dtype=torch.long,device=dev); post=torch.tensor(z["post"],dtype=torch.long,device=dev)
wt=torch.tensor(z["weight"],device=dev)
types=z["type"]; stim = np.where(types=="DNp01")[0]
print(f"device={dev} neurons={N:,} edges={E:,} stim neurons (DNp01/giant fiber)={len(stim)}")
dt,tau,gain,thr=1.0,20.0,0.02,1.0
decay=float(np.exp(-dt/tau))
v=torch.zeros(N,device=dev); spk=torch.zeros(N,device=dev); counts=torch.zeros(N,device=dev)
stim_t=torch.tensor(stim,device=dev)
steps=200; t0=time.time()
for s in range(steps):
    inp=torch.zeros(N,device=dev)
    inp.index_add_(0, post, wt*spk[pre])          # synaptic drive
    drive=torch.full((N,),0.005,device=dev)        # background
    if 20<=s<60: drive[stim_t]+=0.5               # 40 ms giant-fiber pulse
    v=decay*v+gain*inp+drive
    spk=(v>=thr).float(); v=v*(1-spk); counts+=spk
if dev=="mps": torch.mps.synchronize()
el=time.time()-t0
print(f"{steps} steps ({steps*dt:.0f} ms biological) in {el:.2f}s -> {steps/el:.0f} steps/s, {steps*dt/1000/el:.2f}x realtime")
c=counts.cpu().numpy(); order=np.argsort(-c)[:15]
print("most active neurons (spikes, type, superclass):")
for i in order: print(f"  {int(c[i]):4d}  {types[i]:20s} {z['superclass'][i]}")
sc=collections.Counter(); 
for i in np.where(c>0)[0]: sc[z['superclass'][i]]+=1
print("neurons that fired at all:",int((c>0).sum()),"| by superclass:",dict(sc.most_common(8)))
