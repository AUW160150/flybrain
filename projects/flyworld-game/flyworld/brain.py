"""Batched leaky integrate-and-fire simulation of a connectome sub-graph on torch (MPS or CPU).

Generalizes scripts/lif_bench.py to B independent brains sharing one edge list. Drive and
silence masks are set once per game frame from named groups; spikes of the output groups are
accumulated in a ring buffer of the last 200 biological ms.
"""
import math
import time
import numpy as np
import torch

from .config import LIFParams
from .groups import OUT_GROUPS

RING_MS = 200


def pick_device(name=None):
    if name:
        return torch.device(name)
    return torch.device("mps" if torch.backends.mps.is_available() else "cpu")


def output_group_names(groups):
    """Every named group with cells is read out, so the activity panel can show senses and motor side by side."""
    return sorted(n for n, idx in groups.items() if len(idx) > 0)


class BatchedLIF:
    def __init__(self, N, pre, post, weight, groups, B=1, params=None, device=None, seed=0, event_driven=False):
        self.p = params or LIFParams()
        self.dev = pick_device(device)
        self.N, self.B = int(N), int(B)
        keep = np.abs(weight) >= self.p.min_w
        self.pre = torch.as_tensor(np.asarray(pre)[keep], dtype=torch.long, device=self.dev)
        self.post = torch.as_tensor(np.asarray(post)[keep], dtype=torch.long, device=self.dev)
        self.wt = torch.as_tensor(np.asarray(weight)[keep], dtype=torch.float32, device=self.dev)
        self.E = int(self.pre.numel())
        self.decay = float(math.exp(-self.p.dt / self.p.tau))
        self.event_driven = event_driven
        if event_driven:
            pre_np = np.asarray(pre)[keep]; order = np.argsort(pre_np, kind="stable")
            counts = np.bincount(pre_np, minlength=self.N)
            indptr = np.concatenate([[0], np.cumsum(counts)])
            self.indptr = torch.as_tensor(indptr, dtype=torch.long, device=self.dev)
            self.post_csr = torch.as_tensor(np.asarray(post)[keep][order], dtype=torch.long, device=self.dev)
            self.wt_csr = torch.as_tensor(np.asarray(weight)[keep][order], dtype=torch.float32, device=self.dev)
        self.groups = {k: np.asarray(v, dtype=np.int64) for k, v in groups.items() if len(v) > 0}
        # stimulable groups: every named group with cells
        self.in_names = sorted(self.groups)
        self.in_index = {n: i for i, n in enumerate(self.in_names)}
        M = np.zeros((len(self.in_names), self.N), dtype=np.float32)
        for i, n in enumerate(self.in_names):
            M[i, self.groups[n]] = 1.0
        self.M_in = torch.as_tensor(M, device=self.dev)
        # output groups
        self.out_names = output_group_names(self.groups)
        self.out_index = {n: i for i, n in enumerate(self.out_names)}
        Mo = np.zeros((self.N, len(self.out_names)), dtype=np.float32)
        for i, n in enumerate(self.out_names):
            Mo[self.groups[n], i] = 1.0
        self.M_out = torch.as_tensor(Mo, device=self.dev)
        self.out_sizes = np.array([len(self.groups[n]) for n in self.out_names], dtype=np.float64)
        self.gen = torch.Generator(device="cpu").manual_seed(seed)
        self.amp = torch.zeros(self.B, len(self.in_names), device=self.dev)
        self.clamp = torch.zeros(self.B, len(self.in_names), device=self.dev)
        self.reset_all()

    # ----- state -----
    def reset_all(self):
        B, N = self.B, self.N
        self.v = torch.zeros(B, N, device=self.dev)
        self.spk = torch.zeros(B, N, device=self.dev)
        self.refr = torch.zeros(B, N, device=self.dev)
        self.ring = torch.zeros(B, len(self.out_names), RING_MS, device=self.dev)
        self.ptr = 0
        self.t_ms = 0
        self.run = torch.zeros(B, device=self.dev)
        self.runaway_t = torch.zeros((), device=self.dev)
        self.max_frac_t = torch.zeros((), device=self.dev)
        self.runaway_total = 0
        self.max_frac = 0.0
        self.count_spikes = False
        self.counts = torch.zeros(B, N, device=self.dev)
        self._refresh_drive()

    def reset(self, b):
        self.v[b].zero_(); self.spk[b].zero_(); self.refr[b].zero_(); self.ring[b].zero_(); self.run[b] = 0; self.counts[b].zero_()

    # ----- per-frame inputs -----
    def set_amp(self, b, name, value):
        self.amp[b, self.in_index[name]] = float(value)

    def set_amps(self, amps):
        """amps: (B, G_in) numpy array in in_names order, or dict {(b, name): value} (replaces all)."""
        if isinstance(amps, dict):
            a = np.zeros((self.B, len(self.in_names)), dtype=np.float32)
            for (b, name), val in amps.items():
                a[b, self.in_index[name]] += val
            amps = a
        self.amp = torch.as_tensor(np.asarray(amps, dtype=np.float32), device=self.dev)

    def set_clamp(self, b, name, on):
        self.clamp[b, self.in_index[name]] = 1.0 if on else 0.0

    def clear_amps(self):
        self.amp.zero_()

    def _refresh_drive(self):
        self.drive = self.amp @ self.M_in                       # (B, N)
        if self.p.noise > 0:
            self.drive = self.drive + self.p.noise * torch.rand(self.B, self.N, generator=self.gen).to(self.dev)
        self.mask = 1.0 - torch.clamp(self.clamp @ self.M_in, 0.0, 1.0)

    # ----- dynamics -----
    def step(self, n_steps):
        """Advance every brain by n_steps of dt ms using the current amp/clamp settings."""
        self._refresh_drive()
        p, decay, gain, thr = self.p, self.decay, self.p.gain, self.p.thr
        inp = torch.zeros(self.B, self.N, device=self.dev)
        flat = inp.view(-1)
        for _ in range(int(n_steps)):
            inp.zero_()
            if self.event_driven:
                self._propagate_events(flat)
            else:
                inp.index_add_(1, self.post, self.wt * self.spk[:, self.pre])
            v = decay * self.v + gain * inp + self.drive
            v = v * (self.refr <= 0) * self.mask
            spk = (v >= thr).float()
            v = v * (1.0 - spk) + p.reset * spk
            self.refr = torch.clamp(self.refr - 1.0, min=0.0) + spk * p.refr_ms
            self.v, self.spk = v, spk
            self.ring[:, :, self.ptr] = spk @ self.M_out
            self.ptr = (self.ptr + 1) % RING_MS
            self.t_ms += p.dt
            if self.count_spikes:
                self.counts += spk
            frac = spk.mean(dim=1)
            self.run = torch.where(frac > p.governor_frac, self.run + 1.0, torch.zeros_like(self.run))
            damp = (self.run >= p.governor_steps).float()
            self.v = self.v * (1.0 - 0.5 * damp)[:, None]
            self.runaway_t = self.runaway_t + damp.sum()
            self.max_frac_t = torch.maximum(self.max_frac_t, frac.max())
        # one sync per call, not per step
        self.runaway_total = int(self.runaway_t.item())
        self.max_frac = float(self.max_frac_t.item())

    def _propagate_events(self, flat):
        """Scatter the outgoing synapses of the neurons that spiked (all batches, flattened to B*N)."""
        active = torch.nonzero(self.spk.view(-1)).squeeze(1)          # sync: data-dependent size
        if active.numel() == 0:
            return
        neuron = active % self.N
        starts = self.indptr[neuron]
        counts = self.indptr[neuron + 1] - starts
        total = int(counts.sum())                                       # sync
        if total == 0:
            return
        excl = torch.cumsum(counts, 0) - counts
        eidx = torch.repeat_interleave(starts - excl, counts, output_size=total) + torch.arange(total, device=self.dev)
        boff = torch.repeat_interleave((active // self.N) * self.N, counts, output_size=total)
        flat.index_add_(0, self.post_csr[eidx] + boff, self.wt_csr[eidx])

    # ----- readout -----
    def ring_cpu(self):
        return self.ring.cpu().numpy(), self.ptr

    def window_counts(self, window_ms, ring=None, ptr=None):
        """Spike counts per output group over the last window_ms: (B, G_out)."""
        if ring is None:
            ring, ptr = self.ring_cpu()
        w = int(min(window_ms, RING_MS))
        idx = (np.arange(ptr - w, ptr) % RING_MS)
        return ring[:, :, idx].sum(axis=2)

    def rates(self, window_ms=50, ring=None, ptr=None):
        """Per-neuron mean firing rate in Hz per output group: (B, G_out)."""
        counts = self.window_counts(window_ms, ring, ptr)
        return counts / (self.out_sizes[None, :] * (window_ms / 1000.0))

    def rate_dict(self, b, window_ms=50, ring=None, ptr=None):
        r = self.rates(window_ms, ring, ptr)[b]
        return {n: float(r[i]) for i, n in enumerate(self.out_names)}

    def activity_fraction(self):
        return float(self.spk.mean())


def load_npc_brain(B, params=None, device=None, event_driven=True):
    from .circuits import load_circuit
    c = load_circuit()
    return BatchedLIF(c["N"], c["pre"], c["post"], c["weight"], c["groups"], B=B, params=params, device=device, event_driven=event_driven)


def load_whole_brain(params=None, device=None, event_driven=True):
    from .circuits import load_whole, load_groups_whole
    params = params or LIFParams()
    w = load_whole(min_w=params.min_w, with_root_side=True)
    return BatchedLIF(w["N"], w["pre"], w["post"], w["weight"], load_groups_whole(), B=1, params=params, device=device, event_driven=event_driven)


def bench(B=6, steps=1000, min_steps_per_s=600.0, max_rest_dn_hz=1.0, max_activity=0.01, device=None, whole=False, event_driven=None):
    if whole:
        brain = load_whole_brain(device=device, event_driven=True if event_driven is None else event_driven)
    else:
        brain = load_npc_brain(B, device=device, event_driven=True if event_driven is None else event_driven)
    print(f"event_driven={brain.event_driven}")
    print(f"device={brain.dev} B={brain.B} N={brain.N:,} E={brain.E:,} in_groups={len(brain.in_names)} out_groups={len(brain.out_names)}")
    brain.step(10)                                   # warm-up kernels
    if brain.dev.type == "mps":
        torch.mps.synchronize()
    brain.reset_all()
    t0 = time.time()
    dn_total = 0.0
    done = 0
    while done < steps:
        n = min(RING_MS, steps - done)
        brain.step(n)
        dn_total += brain.window_counts(n)[:, brain.out_index["DN_all"]].sum()
        done += n
    if brain.dev.type == "mps":
        torch.mps.synchronize()
    el = time.time() - t0
    sps = steps / el
    n_dn = len(brain.groups["DN_all"])
    rest_dn_hz = dn_total / (brain.B * n_dn * steps * brain.p.dt / 1000.0)
    print(f"BENCH steps/s={sps:.0f} rest_dn_hz={rest_dn_hz:.3f} max_activity={brain.max_frac:.4f} runaway={brain.runaway_total}")
    ok = sps >= min_steps_per_s and rest_dn_hz <= max_rest_dn_hz and brain.max_frac <= max_activity and brain.runaway_total == 0
    # informational: DNp09 stimulation response
    brain.reset_all()
    for b in range(brain.B):
        brain.set_amp(b, "DNp09", 0.15)
        brain.set_amp(b, "LC4", 0.15); brain.set_amp(b, "LPLC2", 0.15)
    if brain.dev.type == "mps":
        torch.mps.synchronize()
    t0 = time.time(); brain.step(RING_MS)
    if brain.dev.type == "mps":
        torch.mps.synchronize()
    print(f"info stimulated (DNp09+loom) steps/s={RING_MS/(time.time()-t0):.0f} max_activity={brain.max_frac:.4f}")
    r = brain.rate_dict(0, 100)
    print("info DNp09 stim 0.15 -> " + " ".join(f"{k}={v:.0f}" for k, v in r.items() if k in ("DNp09", "DNa02_L", "DNa02_R", "MN9", "DN_all")))
    print("BENCH OK" if ok else "BENCH FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--whole", action="store_true")
    ap.add_argument("--B", type=int, default=6)
    ap.add_argument("--steps", type=int, default=1000)
    ap.add_argument("--min-steps-per-s", type=float, default=600)
    ap.add_argument("--max-rest-dn-hz", type=float, default=1.0)
    ap.add_argument("--max-activity", type=float, default=0.01)
    ap.add_argument("--device", default=None)
    ap.add_argument("--event-driven", dest="event_driven", action="store_true", default=None)
    ap.add_argument("--dense", dest="event_driven", action="store_false")
    a = ap.parse_args()
    if a.bench:
        sys.exit(bench(a.B, a.steps, a.min_steps_per_s, a.max_rest_dn_hz, a.max_activity, a.device, a.whole, a.event_driven))
    ap.print_help()
