"""Scripted headless scenarios on the real NPC circuit. Prints PASS/FAIL lines and BEHAVIOUR OK."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from flyworld.game import Game
from flyworld.config import WorldParams
from flyworld.encoders import SensoryEncoder

FPS = 30


def fresh(seed=0, idle=True):
    g = Game(seed=seed)
    w = g.world
    # isolate fly 1 in open space; park everyone else far away in a corner
    w.flies[1].pos = np.array([0.0, 0.0]); w.flies[1].heading = 0.0
    w.big.pos = np.array([-w.p.arena_half + 2, -w.p.arena_half + 2]); w.big.heading = 0.0
    for f in w.npcs[1:]:
        f.pos = np.array([w.p.arena_half - 2, w.p.arena_half - 2 - f.id * 0.7])
    for fd in w.foods:
        fd.pos = np.array([w.p.arena_half - 3, -w.p.arena_half + 3 + fd.id % 10])
    for o in w.obstacles:
        o.pos = np.array([-w.p.arena_half + 3 + (o.id % 10) * 2.5, w.p.arena_half - 3])
    if not idle:
        for d in g.decoders.values():
            d.p.idle_s = 1e9
    return g


def scenario_stim_dnp09():
    g = fresh(idle=False)
    fly = g.world.flies[1]
    start = fly.pos.copy()
    g.panel.focus = 1
    g.panel.stim.add((1, "DNp09"))
    g.run_headless(5 * FPS)
    disp = float(np.linalg.norm(fly.pos - start))
    r = g.last_rates[1]
    ok = disp > 1.0 and r["DNp09"] >= 50
    print(f"{'PASS' if ok else 'FAIL'} stim DNp09: forward displacement {disp:.2f} > 1.0 in 5 s (DNp09 {r['DNp09']:.0f} Hz, DNa02 L/R {r['DNa02_L']:.0f}/{r['DNa02_R']:.0f}, heading {math.degrees(fly.heading):.0f} deg)")
    return ok


def scenario_rest():
    g = fresh(idle=False)
    fly = g.world.flies[1]
    start = fly.pos.copy()
    g.run_headless(5 * FPS)
    disp = float(np.linalg.norm(fly.pos - start))
    r = g.last_rates[1]
    ok = disp < 0.2 and r["DN_all"] == 0.0 and g.brain.runaway_total == 0
    print(f"{'PASS' if ok else 'FAIL'} rest: displacement {disp:.3f} < 0.2 in 5 s, DN rate {r['DN_all']:.2f} Hz, runaway {g.brain.runaway_total}")
    return ok


def scenario_loom():
    g = fresh(idle=False)
    w = g.world
    fly = w.flies[1]
    w.big.pos = np.array([7.0, 0.0]); w.big.heading = math.pi          # 7 units ahead, facing the fly
    g.big_cmd = (w.p.big_speed, 0.0)                                    # charge straight at it
    first_lc = first_dnp01 = jump_frame = contact_frame = None
    probe = SensoryEncoder(w.p)          # separate instance so the probe never disturbs the game's encoder state
    peak_lc = 0.0
    for frame in range(4 * FPS):
        g.tick()
        amps = probe.encode(1, fly.pos, fly.heading, w.objects_for(fly), g.dt)
        peak_lc = max(peak_lc, amps.get("LC4_L", 0.0))
        if first_lc is None and any(v > 0.02 for k, v in amps.items() if k.startswith("LC4")):
            first_lc = frame
        if first_dnp01 is None and g.last_rates[1]["DNp01"] > 0:
            first_dnp01 = frame
        if jump_frame is None and ("jump", 1) in w.events:
            jump_frame = frame
        if contact_frame is None and np.linalg.norm(w.big.pos - fly.pos) < w.big.radius + fly.radius + 0.05:
            contact_frame = frame
        if jump_frame is not None and frame > jump_frame + FPS:
            break
    ok = first_dnp01 is not None and jump_frame is not None and (contact_frame is None or jump_frame <= contact_frame)
    lat = None if first_lc is None or first_dnp01 is None else (first_dnp01 - first_lc) * w.p.bio_ms_per_tick
    print(f"{'PASS' if ok else 'FAIL'} loom: LC4 onset frame {first_lc}, DNp01 first spike frame {first_dnp01} (latency {lat} bio-ms), jump frame {jump_frame}, contact frame {contact_frame}, peak LC4 amp {peak_lc:.2f}, final distance {np.linalg.norm(w.big.pos - fly.pos):.2f}")
    return ok


def scenario_food_report():
    g = fresh(idle=False)
    w = g.world
    fly = w.flies[1]
    fd = w.foods[0]
    fd.pos = np.array([5.0 * math.cos(0.5), 5.0 * math.sin(0.5)])      # 5 units away, 30 deg to the left
    d0 = float(np.linalg.norm(fd.pos - fly.pos))
    g.run_headless(10 * FPS)
    d1 = float(np.linalg.norm(fd.pos - fly.pos))
    r = g.last_rates[1]
    print(f"REPORT food approach: distance delta = {d1 - d0:+.2f} over 10 s (MN9 {r['MN9']:.0f} Hz, DNp09 {r['DNp09']:.0f} Hz, DNa02 L/R {r['DNa02_L']:.0f}/{r['DNa02_R']:.0f}); not a pass condition")
    return True


def scenario_taste_eat():
    g = fresh(idle=False)
    w = g.world
    fly = w.flies[1]
    fd = w.foods[0]
    fd.pos = fly.pos.copy()
    before = fd.amount
    g.run_headless(3 * FPS)
    r = g.last_rates[1]
    ok = fly.eaten > 0.5 and r["MN9"] >= 20
    print(f"{'PASS' if ok else 'FAIL'} taste: standing on food drives MN9 {r['MN9']:.0f} Hz and eats {fly.eaten:.2f} units in 3 s (food {before:.1f} -> {fd.amount:.1f})")
    return ok


if __name__ == "__main__":
    results = [scenario_stim_dnp09(), scenario_rest(), scenario_loom(), scenario_taste_eat(), scenario_food_report()]
    if all(results):
        print("BEHAVIOUR OK"); sys.exit(0)
    print("BEHAVIOUR FAIL"); sys.exit(1)
