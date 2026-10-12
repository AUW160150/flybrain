"""Sweep synaptic gain and stimulus amplitude on the NPC circuit and pick the operating point.

Writes processed/calibration.json and prints PASS/FAIL lines, then CALIBRATION OK when every
acceptance rule holds for the chosen point.
"""
import sys, json, time, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
import torch
from flyworld.brain import load_npc_brain, RING_MS
from flyworld.config import PATHS, LIFParams

STIMULI = {            # fly index -> groups driven
    "rest": [], "DNp09": ["DNp09"], "MDN": ["MDN"], "DNa02_L": ["DNa02_L"], "DNa02_R": ["DNa02_R"],
    "loom": ["LC4", "LPLC2"], "LC4_R": ["LC4_R"], "ORN_DM1": ["ORN_DM1"], "ORN_DM1_L": ["ORN_DM1_L"], "LB3c": ["LB3c"],
}
GAINS = [0.003, 0.005, 0.007, 0.01]
AMPS = [0.05, 0.10, 0.15, 0.20]
REST_MS, STIM_MS = 300, 1000     # 1 s of stimulation so the readout rates are steady-state
REPORT = ["DNp01_L", "DNp01_R", "DNp09", "MDN", "DNa01_L", "DNa01_R", "DNa02_L", "DNa02_R", "DNg11", "MN9", "DN_all"]


def run_point(brain, gain, amp):
    brain.p.gain = gain
    brain.reset_all()
    brain.count_spikes = True
    brain.clear_amps()
    brain.step(REST_MS)
    rest_rates = brain.rates(200)                      # (B, G_out) at rest (all flies identical)
    rest_counts = brain.counts.clone()
    for b, (name, groups) in enumerate(STIMULI.items()):
        for g in groups:
            brain.set_amp(b, g, amp)
    # first 50 ms one step at a time to catch DNp01 latency on the loom fly
    b_loom = list(STIMULI).index("loom")
    i_dnp01 = [brain.out_index["DNp01_L"], brain.out_index["DNp01_R"]]
    latency = None
    for t in range(1, 51):
        brain.step(1)
        ring, ptr = brain.ring_cpu()
        if latency is None and ring[b_loom, i_dnp01, (ptr - 1) % RING_MS].sum() > 0:
            latency = t
    brain.step(STIM_MS - 50)
    rates = brain.rates(200)                           # last 200 ms of stimulation
    stim_counts = (brain.counts - rest_counts).cpu().numpy()   # spikes during STIM_MS
    dn = brain.groups["DN_all"]
    dn_hz = stim_counts[:, dn] / (STIM_MS / 1000.0)
    spread = (dn_hz > 5).sum(axis=1)                   # DNs above 5 Hz per fly
    frac = stim_counts.sum(axis=1) / (brain.N * STIM_MS)  # mean fraction active per step
    res = {}
    for b, name in enumerate(STIMULI):
        res[name] = {g: float(rates[b, brain.out_index[g]]) for g in REPORT if g in brain.out_index}
        res[name]["dn_spread"] = int(spread[b]); res[name]["active_frac"] = float(frac[b])
    res["rest"]["r_base"] = {n: float(rest_rates[0, i]) for i, n in enumerate(brain.out_names)}
    res["loom"]["dnp01_latency_ms"] = latency
    res["_runaway"] = brain.runaway_total
    return res


def judge(res):
    checks = {
        "rest quiet (DN mean < 1 Hz, no runaway)": res["rest"]["DN_all"] < 1.0 and res["_runaway"] == 0,
        "DNp09 stim walks (DNp09 >= 50 Hz, <= 50 DNs above 5 Hz)": res["DNp09"]["DNp09"] >= 50 and res["DNp09"]["dn_spread"] <= 50,
        "loom reaches DNp01 within 20 ms": res["loom"]["dnp01_latency_ms"] is not None and res["loom"]["dnp01_latency_ms"] <= 20,
        "right-only LC4 is lateralized (DNp01_R > DNp01_L)": res["LC4_R"]["DNp01_R"] > res["LC4_R"]["DNp01_L"],
        "no stimulus saturates the circuit (active fraction < 5%)": all(v["active_frac"] < 0.05 for k, v in res.items() if not k.startswith("_")),
    }
    return checks


def main():
    t0 = time.time()
    brain = load_npc_brain(B=len(STIMULI))
    print(f"device={brain.dev} N={brain.N:,} E={brain.E:,} stimuli={list(STIMULI)}")
    table = {}
    best = None
    for gain, amp in itertools.product(GAINS, AMPS):
        res = run_point(brain, gain, amp)
        checks = judge(res)
        n_ok = sum(checks.values())
        table[f"{gain}/{amp}"] = dict(res=res, ok=n_ok == len(checks))
        print(f"gain={gain:<6} amp={amp:<5} pass={n_ok}/{len(checks)} DNp09={res['DNp09']['DNp09']:.0f}Hz spread={res['DNp09']['dn_spread']} "
              f"loom_lat={res['loom']['dnp01_latency_ms']} DNp01(LC4_R) L/R={res['LC4_R']['DNp01_L']:.0f}/{res['LC4_R']['DNp01_R']:.0f} "
              f"DNa02(DNp09) L/R={res['DNp09']['DNa02_L']:.0f}/{res['DNp09']['DNa02_R']:.0f} maxfrac={max(v['active_frac'] for k,v in res.items() if not k.startswith('_')):.3f}")
        if n_ok == len(checks):
            # prefer the planned operating point (0.005, 0.15) so signals propagate, then the smallest DN spread
            score = (round(abs(gain - 0.005) * 100 + abs(amp - 0.15), 3), res["DNp09"]["dn_spread"])
            if best is None or score < best[0]:
                best = (score, gain, amp, res, checks)
    if best is None:
        print("CALIBRATION FAIL: no (gain, amp) passed every rule")
        return 1
    _, gain, amp, res, checks = best
    for name, ok in checks.items():
        print(("PASS " if ok else "FAIL ") + name)
    r09 = res["DNp09"]
    turn_bias = (r09["DNa02_L"] - r09["DNa02_R"]) / max(r09["DNp09"], 1e-6)   # Hz of L-R asymmetry per Hz of DNp09
    calib = dict(gain=gain, panel_amp=amp, r_base=res["rest"]["r_base"], turn_bias_per_dnp09_hz=turn_bias,
                 measured=res, device=str(brain.dev), elapsed_s=time.time() - t0)
    with open(PATHS["calibration"], "w") as f:
        json.dump(calib, f, indent=1)
    for k in ("ORN_DM1", "ORN_DM1_L", "LB3c", "loom", "MDN"):
        print(f"  {k:10s} " + " ".join(f"{g}={res[k][g]:.0f}" for g in ("DNp01_L","DNp01_R","DNp09","MDN","DNa02_L","DNa02_R","MN9","DN_all")) + f" spread={res[k]['dn_spread']}")
    print(f"chosen gain={gain} amp={amp} turn_bias_per_dnp09_hz={turn_bias:.3f} -> {PATHS['calibration'].name} ({time.time()-t0:.0f}s)")
    print("CALIBRATION OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
