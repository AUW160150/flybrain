import numpy as np
import pytest
import torch
from flyworld.brain import BatchedLIF
from flyworld.config import LIFParams


def tiny(B=2):
    # 0 -> 1 excitatory (10 synapses), 1 -> 2 inhibitory (-10), 3 isolated
    pre, post, w = np.array([0, 1]), np.array([1, 2]), np.array([10.0, -10.0], dtype=np.float32)
    groups = {"A": [0], "DNp09": [1], "C": [2], "DN_all": [1, 2], "D": [3]}
    return BatchedLIF(4, pre, post, w, groups, B=B, params=LIFParams(gain=0.05), device="cpu")


def test_stimulus_propagates_and_batch_is_independent():
    b = tiny()
    b.set_amp(0, "A", 0.2)
    b.step(200)
    r = b.rates(100)
    assert r[0, b.out_index["DNp09"]] > 0            # A drives B
    assert r[1, b.out_index["DNp09"]] == 0           # fly 1 unstimulated
    assert b.runaway_total == 0


def test_silence_clamps_group():
    b = tiny()
    b.set_amp(0, "A", 0.2)
    b.set_clamp(0, "DNp09", True)
    b.step(200)
    assert b.rates(100)[0, b.out_index["DNp09"]] == 0


def test_reset_clears_one_fly():
    b = tiny()
    b.set_amp(0, "A", 0.2); b.set_amp(1, "A", 0.2)
    b.step(100)
    b.reset(0)
    assert float(b.v[0].abs().sum()) == 0 and float(b.ring[0].sum()) == 0
    assert float(b.ring[1].sum()) > 0


def test_rate_units():
    # a cell driven hard fires every refr_ms+1 steps at most; rate must be bounded accordingly
    b = tiny()
    b.set_amp(0, "DNp09", 1.0)
    b.step(200)
    r = b.rates(100)[0, b.out_index["DNp09"]]
    assert 0 < r <= 1000.0 / (b.p.refr_ms + 1) + 1e-6


def test_governor_damps_runaway():
    pre, post = np.array([0, 1]), np.array([1, 0])
    w = np.array([50.0, 50.0], dtype=np.float32)
    b = BatchedLIF(2, pre, post, w, {"A": [0], "DNp09": [1], "DN_all": [1]}, B=1,
                   params=LIFParams(gain=1.0, refr_ms=0, governor_frac=0.4, governor_steps=5), device="cpu")
    b.set_amp(0, "A", 2.0)
    b.step(100)
    assert b.runaway_total > 0 and b.max_frac >= 0.5


def test_event_driven_matches_dense():
    rng = np.random.default_rng(0)
    N, E = 300, 3000
    pre, post = rng.integers(0, N, E), rng.integers(0, N, E)
    w = rng.choice([-8.0, 6.0, 12.0], E).astype(np.float32)
    groups = {"A": list(range(0, 30)), "DNp09": list(range(30, 40)), "DN_all": list(range(30, 60))}
    outs = []
    for ev in (False, True):
        b = BatchedLIF(N, pre, post, w, groups, B=3, params=LIFParams(gain=0.02, min_w=5), device="cpu", event_driven=ev)
        b.set_amp(0, "A", 0.3); b.set_amp(2, "A", 0.12)
        b.step(150)
        outs.append((b.ring.clone(), b.v.clone()))
    assert torch.equal(outs[0][0], outs[1][0]) and torch.allclose(outs[0][1], outs[1][1])
    assert float(outs[0][0][0].sum()) > 0 and float(outs[0][0][1].sum()) == 0
