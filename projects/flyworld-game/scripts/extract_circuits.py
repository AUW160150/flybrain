"""Extract the NPC sub-circuit and the whole-CNS group index table.

Prints `OK circuit_npc N=... E=... DNs=...` plus group counts. With --verify it also checks the
size band and every expected group count and prints CIRCUIT OK only when all checks pass.
"""
import sys, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from flyworld import circuits
from flyworld.groups import EXPECTED_COUNTS, LOOM_SEEDS, ODOUR_SEEDS, TASTE_SEEDS, TARGETS, FORCE_INCLUDE, group_counts
from flyworld.config import PATHS

SIZE_BAND = (6_000, 12_000)
MIN_DNS = 400


def main(verify=False):
    t0 = time.time()
    whole_all = circuits.load_whole(min_w=None)
    whole_counts = circuits.save_groups_whole(whole_all)
    print(f"whole: N={whole_all['N']:,} E={len(whole_all['pre']):,} groups_whole.json written ({time.time()-t0:.1f}s)")
    def run(min_w):
        keep = np.abs(whole_all["weight"]) >= min_w
        whole = dict(whole_all, pre=whole_all["pre"][keep], post=whole_all["post"][keep], weight=whole_all["weight"][keep])
        mask, _ = circuits.extract_circuit(whole, min_w=min_w)
        print(f"  min_w={min_w}: N={int(mask.sum()):,}")
        return min_w, whole, mask
    chosen = run(5)
    n = int(chosen[2].sum())
    if n > SIZE_BAND[1]:
        chosen = run(8)
    elif n < SIZE_BAND[0]:
        chosen = run(3)
    min_w, whole, mask = chosen
    circ = circuits.remap(whole, mask)
    circuits.save_circuit(circ)
    g = circ["groups"]
    n_dn = int(len(g["DN_all"]))
    print(f"OK circuit_npc N={circ['N']} E={len(circ['pre'])} DNs={n_dn} min_w={min_w} ({time.time()-t0:.1f}s)")
    names = TARGETS + LOOM_SEEDS + ODOUR_SEEDS + TASTE_SEEDS + FORCE_INCLUDE
    print("groups:", " ".join(f"{n} {len(g[n])}" for n in names))
    if not verify:
        return 0
    failures = []
    if not (SIZE_BAND[0] <= circ["N"] <= SIZE_BAND[1]):
        failures.append(f"N={circ['N']} outside {SIZE_BAND}")
    if n_dn < MIN_DNS:
        failures.append(f"DNs={n_dn} < {MIN_DNS}")
    for name, exp in EXPECTED_COUNTS.items():
        got = whole_counts.get(name)
        if got != exp:
            failures.append(f"whole group {name}: {got} != {exp}")
    for name in TARGETS + LOOM_SEEDS + ODOUR_SEEDS + TASTE_SEEDS + FORCE_INCLUDE:
        if len(g[name]) != EXPECTED_COUNTS[name]:
            failures.append(f"circuit group {name}: {len(g[name])} != {EXPECTED_COUNTS[name]}")
    for name in TARGETS + LOOM_SEEDS:
        if len(g[name + "_L"]) == 0 or len(g[name + "_R"]) == 0:
            failures.append(f"circuit group {name} lacks a side: L={len(g[name+'_L'])} R={len(g[name+'_R'])}")
    # every kept node must have at least one edge, except force-included panel cells
    deg = np.bincount(circ["pre"], minlength=circ["N"]) + np.bincount(circ["post"], minlength=circ["N"])
    isolated = int((deg == 0).sum())
    if isolated > 200:
        failures.append(f"{isolated} isolated neurons in circuit")
    if failures:
        print("CIRCUIT FAIL:\n  " + "\n  ".join(failures))
        return 1
    print(f"isolated={isolated}")
    print("CIRCUIT OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(verify="--verify" in sys.argv))
