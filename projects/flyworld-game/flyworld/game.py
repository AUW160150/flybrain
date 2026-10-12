"""Game loop: senses -> brains -> decoders -> world, with headless, script and focus-whole modes."""
import argparse
import json
import math
import sys
import time
import numpy as np
import torch

from .config import PATHS, LIFParams, DecoderParams, WorldParams
from .world import World
from .encoders import SensoryEncoder, amps_to_matrix
from .decoder import MotorDecoder
from .panel import PanelState
from .brain import load_npc_brain, load_whole_brain
from .profiles import by_name


def load_calibration():
    if PATHS["calibration"].exists():
        with open(PATHS["calibration"]) as f:
            return json.load(f)
    return {}


class Game:
    def __init__(self, seed=0, focus_whole=False, device=None, world_params=None):
        self.wp = world_params or WorldParams()
        self.world = World(self.wp, seed)
        self.calib = load_calibration()
        self.lif = LIFParams(gain=float(self.calib.get("gain", LIFParams.gain)))
        self.device = device
        self.brain = load_npc_brain(B=self.wp.n_npc, params=self.lif, device=device)
        self.encoder = SensoryEncoder(self.wp)
        self.decoders = {f.id: MotorDecoder(DecoderParams(), self.calib, np.random.default_rng(seed + f.id)) for f in self.world.npcs}
        self.panel = PanelState(self.wp.n_npc, amp=float(self.calib.get("panel_amp", 0.15)), groups=self.brain.groups)
        self.whole = None
        self.focus_whole = False
        self.big_cmd = (0.0, 0.0)
        self.last_rates = {}
        self.last_ring = None                 # (ring, ptr) of the NPC batch after the last tick
        self.last_whole_ring = None
        self.tick_ms = []
        self.whole_steps = 0
        self.whole_time = 0.0
        self.dt = 1.0 / self.wp.tick_hz
        self.seed = seed
        self.mode = "sandbox"
        self.time_limit_s = 180.0
        self.round = dict(state="playing", t=0.0, eaten=0.0, remaining=self.food_remaining(), total=self.food_remaining())
        if focus_whole:
            self.enable_whole()

    # ----- rounds (shepherd mode) -----
    def food_remaining(self):
        return float(sum(max(fd.amount, 0.0) for fd in self.world.foods))

    def set_mode(self, mode, time_limit_s=None):
        self.mode = mode
        if time_limit_s is not None:
            self.time_limit_s = float(time_limit_s)
        self.round = dict(state="playing", t=0.0, eaten=0.0, remaining=self.food_remaining(), total=self.food_remaining())

    def restart(self):
        """New arena with the same seed and mode; brains and decoders reset."""
        self.world = World(self.wp, self.seed)
        self.encoder = SensoryEncoder(self.wp)
        self.decoders = {f.id: MotorDecoder(DecoderParams(), self.calib, np.random.default_rng(self.seed + f.id)) for f in self.world.npcs}
        self.brain.reset_all()
        if self.whole is not None:
            self.whole.reset_all()
        self.panel.stim.clear(); self.panel.clamp.clear()
        self.last_rates = {}
        self.set_mode(self.mode)

    def _update_round(self, dt):
        r = self.round
        if r["state"] != "playing":
            return
        r["t"] += dt
        r["remaining"] = self.food_remaining()
        r["eaten"] = float(sum(f.eaten for f in self.world.npcs))
        if self.mode == "shepherd":
            if r["remaining"] <= 1e-6:
                r["state"] = "won"
            elif r["t"] >= self.time_limit_s:
                r["state"] = "lost"

    # ----- whole-CNS focus mode -----
    def enable_whole(self):
        if self.whole is None:
            t0 = time.time()
            self.whole = load_whole_brain(self.lif, self.device)
            print(f"whole CNS loaded: N={self.whole.N:,} E={self.whole.E:,} in {time.time()-t0:.1f}s", flush=True)
        self.focus_whole = True

    def toggle_whole(self):
        if self.focus_whole:
            self.focus_whole = False
        else:
            self.enable_whole()

    # ----- one game tick -----
    def tick(self, dt=None):
        dt = dt or self.dt
        if self.round["state"] != "playing":
            return                                    # round over: the world freezes until restart
        t0 = time.perf_counter()
        w, brain, panel = self.world, self.brain, self.panel
        bio = self.wp.bio_ms_per_tick_focus if self.focus_whole else self.wp.bio_ms_per_tick
        per_fly = []
        for fly in w.npcs:
            amps = self.encoder.encode(fly.id, fly.pos, fly.heading, w.objects_for(fly), dt, fly.on_food)
            for g, a in panel.stim_for(fly.id).items():
                amps[g] = amps.get(g, 0.0) + a
            per_fly.append(amps)
        brain.set_amps(amps_to_matrix(brain, per_fly))
        brain.clamp.zero_()
        for b, fly in enumerate(w.npcs):
            for g in panel.clamp_for(fly.id):
                if g in brain.in_index:
                    brain.set_clamp(b, g, True)
        brain.step(bio)
        focus_b = panel.focus - 1
        if self.focus_whole:
            wb = self.whole
            if getattr(self, "_whole_fly", None) != panel.focus:     # a different fly now owns the whole brain
                wb.reset_all(); self._whole_fly = panel.focus
            wb.set_amps(amps_to_matrix(wb, [per_fly[focus_b]]))
            wb.clamp.zero_()
            for g in panel.clamp_for(panel.focus):
                if g in wb.in_index:
                    wb.set_clamp(0, g, True)
            tw = time.perf_counter()
            wb.step(bio)
            wring, wptr = wb.ring_cpu()            # sync
            self.whole_time += time.perf_counter() - tw
            self.whole_steps += bio
        ring, ptr = brain.ring_cpu()
        self.last_ring = (ring, ptr)
        if self.focus_whole:
            self.last_whole_ring = (wring, wptr)
        rates = brain.rates(50, ring, ptr)
        jump_counts = brain.window_counts(20, ring, ptr)
        commands = {}
        for b, fly in enumerate(w.npcs):
            if self.focus_whole and b == focus_b:
                rd = wb.rate_dict(0, 50, wring, wptr)
                jc = wb.window_counts(20, wring, wptr)[0]
                dnp01 = jc[wb.out_index["DNp01"]]
            else:
                rd = {n: float(rates[b, i]) for i, n in enumerate(brain.out_names)}
                dnp01 = jump_counts[b, brain.out_index["DNp01"]]
            self.last_rates[fly.id] = rd
            commands[fly.id] = self.decoders[fly.id].update(rd, dnp01, dt, fly.on_food, bio)
        w.step(dt, commands, self.big_cmd)
        self._update_round(dt)
        self.tick_ms.append((time.perf_counter() - t0) * 1000.0)

    def isolate(self, fly_id):
        """Put one fly alone at the arena centre and park everything else in the far corners."""
        w = self.world
        half = w.p.arena_half
        target = w.flies[fly_id]
        target.pos = np.array([0.0, 0.0]); target.heading = 0.0
        w.big.pos = np.array([-half + 2, -half + 2]); w.big.heading = 0.0
        for f in w.npcs:
            if f.id != fly_id:
                f.pos = np.array([half - 2, half - 2 - f.id * 0.7])
        for fd in w.foods:
            fd.pos = np.array([half - 3, -half + 3 + (fd.id % 10)])
        for o in w.obstacles:
            o.pos = np.array([-half + 3 + (o.id % 10) * 2.5, half - 3])
        self.encoder.prev_theta.clear()

    def brain_for(self, fly_id):
        """(brain, batch index, ring, ptr) that currently drives this NPC fly."""
        if self.focus_whole and fly_id == self.panel.focus and self.last_whole_ring is not None:
            return self.whole, 0, self.last_whole_ring[0], self.last_whole_ring[1]
        return self.brain, fly_id - 1, self.last_ring[0], self.last_ring[1]

    # ----- headless -----
    def run_headless(self, frames):
        for _ in range(frames):
            self.tick()

    def write_trajectory(self, path):
        data = dict(frames=len(self.world.log), n_flies=len(self.world.flies), tick_hz=self.wp.tick_hz,
                    bio_ms_per_tick=self.wp.bio_ms_per_tick, log=self.world.log, final=self.world.snapshot(),
                    stats=self.stats())
        with open(path, "w") as f:
            json.dump(data, f)

    def stats(self):
        tm = np.array(self.tick_ms) if self.tick_ms else np.zeros(1)
        s = dict(mean_tick_ms=float(tm.mean()), max_tick_ms=float(tm.max()), p95_tick_ms=float(np.percentile(tm, 95)),
                 runaway=self.brain.runaway_total, max_activity=self.brain.max_frac)
        if self.whole_steps:
            s["whole_steps_per_s"] = self.whole_steps / max(self.whole_time, 1e-9)
        return s

    # ----- scripting -----
    def run_script(self, text):
        """Commands separated by ';': focus N | stim G | unstim G | silence G | unsilence G | amp X | whole on|off |
        run N | assert rate G <op> X | assert speed <op> X | report."""
        ops = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, "<": lambda a, b: a < b, "==": lambda a, b: abs(a - b) < 1e-9}
        failures = []
        self._mark = getattr(self, "_mark", {})
        for raw in text.split(";"):
            cmd = raw.strip().split()
            if not cmd:
                continue
            op = cmd[0]
            if op == "focus":
                self.panel.focus = int(cmd[1]) if cmd[1].isdigit() else by_name(cmd[1])
            elif op == "isolate":
                self.isolate(self.panel.focus)
            elif op == "mode":
                self.set_mode(cmd[1])
            elif op == "time_limit":
                self.set_mode(self.mode, float(cmd[1]))
            elif op == "restart":
                self.restart()
            elif op == "food":                       # set every food spot to X units
                for fd in self.world.foods:
                    fd.amount = float(cmd[1])
                self.round["remaining"] = self.round["total"] = self.food_remaining()
            elif op == "onfood":                     # put the focus fly on food spot K
                fly = self.world.flies[self.panel.focus]; fd = self.world.foods[int(cmd[1])]
                fly.pos = fd.pos.copy()
            elif op == "foodahead":                  # move food spot 0 to D units straight ahead of the focus fly
                fly = self.world.flies[self.panel.focus]; fd = self.world.foods[0]
                fd.pos = fly.pos + float(cmd[1]) * np.array([math.cos(fly.heading), math.sin(fly.heading)])
            elif op == "stim":
                self.panel.stim.add((self.panel.focus, cmd[1])); self.panel.clamp.discard((self.panel.focus, cmd[1]))
            elif op == "unstim":
                self.panel.stim.discard((self.panel.focus, cmd[1]))
            elif op == "silence":
                self.panel.clamp.add((self.panel.focus, cmd[1])); self.panel.stim.discard((self.panel.focus, cmd[1]))
            elif op == "unsilence":
                self.panel.clamp.discard((self.panel.focus, cmd[1]))
            elif op == "amp":
                self.panel.amp = float(cmd[1])
            elif op == "whole":
                self.enable_whole() if cmd[1] == "on" else setattr(self, "focus_whole", False)
            elif op == "run":
                self.run_headless(int(cmd[1]))
            elif op == "assert":
                fly = self.world.flies[self.panel.focus]
                if cmd[1] == "rate":
                    val = self.last_rates.get(fly.id, {}).get(cmd[2], float("nan")); o, x = cmd[3], float(cmd[4]); label = f"rate {cmd[2]}"
                elif cmd[1] == "speed":
                    val = abs(fly.speed); o, x = cmd[2], float(cmd[3]); label = "speed"
                elif cmd[1] == "round":
                    ok = self.round["state"] == cmd[3]
                    print(f"{'PASS' if ok else 'FAIL'} round state = {self.round['state']} == {cmd[3]} (t={self.round['t']:.1f}s remaining={self.round['remaining']:.2f})")
                    if not ok:
                        failures.append(raw.strip())
                    continue
                elif cmd[1] == "eaten":
                    val = float(fly.eaten); o, x = cmd[2], float(cmd[3]); label = "eaten"
                elif cmd[1] == "eaten_total":
                    val = float(self.round["eaten"]); o, x = cmd[2], float(cmd[3]); label = "eaten_total"
                elif cmd[1] == "moved":
                    val = float(np.linalg.norm(fly.pos - self._mark.get(fly.id, fly.pos))); o, x = cmd[2], float(cmd[3]); label = "moved"
                else:
                    failures.append(f"unknown assert {raw}"); continue
                ok = ops[o](val, x)
                print(f"{'PASS' if ok else 'FAIL'} fly{fly.id} {label} = {val:.3f} {o} {x}")
                if not ok:
                    failures.append(raw.strip())
            elif op == "mark":
                fly = self.world.flies[self.panel.focus]
                self._mark[fly.id] = fly.pos.copy()
            elif op == "report":
                fly = self.world.flies[self.panel.focus]
                r = self.last_rates.get(fly.id, {})
                print(f"round={self.round['state']} t={self.round['t']:.1f}s food={self.round['remaining']:.2f}/{self.round['total']:.2f} eaten={self.round['eaten']:.2f}")
                print(f"fly{fly.id} {fly.name} pos=({fly.pos[0]:.2f},{fly.pos[1]:.2f}) heading={math.degrees(fly.heading):.0f} speed={fly.speed:.2f} eaten={fly.eaten:.2f} " +
                      " ".join(f"{k}={v:.0f}" for k, v in r.items() if v > 0))
            else:
                failures.append(f"unknown command {raw}")
        return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description="flyworld: a MaleCNS-driven fly arena")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--assert-complete", action="store_true")
    ap.add_argument("--screenshot", default=None)
    ap.add_argument("--min-fps", type=float, default=0.0)
    ap.add_argument("--focus-whole", action="store_true")
    ap.add_argument("--min-whole-steps-per-s", type=float, default=0.0)
    ap.add_argument("--max-tick-ms", type=float, default=0.0)
    ap.add_argument("--script", default=None)
    ap.add_argument("--device", default=None)
    ap.add_argument("--renderer", default="panda", choices=["panda", "pygame"])
    ap.add_argument("--mode", default="shepherd", choices=["sandbox", "shepherd"])
    ap.add_argument("--time-limit", type=float, default=180.0)
    a = ap.parse_args(argv)
    game = Game(seed=a.seed, focus_whole=a.focus_whole, device=a.device)
    game.set_mode("sandbox" if (a.headless or a.script) else a.mode, a.time_limit)
    print(f"flyworld: device={game.brain.dev} npc_brain N={game.brain.N:,} E={game.brain.E:,} gain={game.lif.gain} flies={len(game.world.flies)}", flush=True)
    if a.script:
        failures = game.run_script(a.script)
        st = game.stats()
        print(f"stats mean_tick_ms={st['mean_tick_ms']:.1f} max_tick_ms={st['max_tick_ms']:.1f}")
        if failures:
            print("SCRIPT FAIL: " + " | ".join(failures)); return 1
        print("SCRIPT OK"); return 0
    if a.headless:
        game.run_headless(a.frames)
        st = game.stats()
        print(f"stats mean_tick_ms={st['mean_tick_ms']:.1f} p95_tick_ms={st['p95_tick_ms']:.1f} max_tick_ms={st['max_tick_ms']:.1f} "
              f"runaway={st['runaway']} max_activity={st['max_activity']:.4f}" + (f" whole_steps_per_s={st['whole_steps_per_s']:.0f}" if 'whole_steps_per_s' in st else ""))
        if a.out:
            game.write_trajectory(a.out)
        if a.focus_whole and (a.min_whole_steps_per_s or a.max_tick_ms):
            ok = st.get("whole_steps_per_s", 0) >= a.min_whole_steps_per_s and st["p95_tick_ms"] <= a.max_tick_ms and len(game.world.log) == a.frames
            print(f"FOCUS {'OK' if ok else 'FAIL'} {len(game.world.log)} frames"); return 0 if ok else 1
        if a.assert_complete:
            log = game.world.log
            ok = len(log) == a.frames and all(len(fr) == len(game.world.flies) for fr in log) and np.isfinite(np.array(log)).all() and st["runaway"] == 0
            print(f"GAME {'OK' if ok else 'FAIL'} {len(log)} frames"); return 0 if ok else 1
        return 0
    if a.renderer == "pygame":
        from .render_pygame import PygameRenderer as Renderer
    else:
        from .render_panda import Panda3DRenderer as Renderer
    r = Renderer(game)
    return r.run(frames=a.frames or None, screenshot=a.screenshot, min_fps=a.min_fps)


if __name__ == "__main__":
    sys.exit(main())


def hud_status(game):
    """One HUD line describing the round, shared by both renderers."""
    r = game.round
    if game.mode != "shepherd":
        return "sandbox mode (no goal)   R: restart"
    left = max(0.0, game.time_limit_s - r["t"])
    line = f"SHEPHERD  time {int(left)//60:02d}:{int(left)%60:02d}  food left {r['remaining']:.1f}/{r['total']:.1f}  eaten {r['eaten']:.1f}"
    if r["state"] == "won":
        line += f"   YOU WIN in {r['t']:.0f}s  (R: play again)"
    elif r["state"] == "lost":
        line += "   TIME UP  (R: try again)"
    return line
