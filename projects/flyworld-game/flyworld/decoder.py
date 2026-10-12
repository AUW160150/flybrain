"""Turn descending-neuron firing rates into a body command with hysteresis and smoothing."""
import math
from dataclasses import dataclass, field
import numpy as np

from .config import DecoderParams


@dataclass
class MotorCommand:
    v: float = 0.0          # forward speed, units/s (negative = backward)
    omega: float = 0.0      # turn rate, rad/s (positive = left)
    jump: bool = False
    jump_turn: float = 0.0  # rad added to heading when a jump starts
    groom: bool = False
    eat: bool = False
    idle: bool = False


class MotorDecoder:
    def __init__(self, params=None, calib=None, rng=None):
        self.p = params or DecoderParams()
        self.r_base = (calib or {}).get("r_base", {})
        self.turn_bias = float((calib or {}).get("turn_bias_per_dnp09_hz", 0.0))
        self.ema = {}
        self.v_actual = 0.0
        self.omega_actual = 0.0
        self.jump_timer = 0.0        # seconds remaining in the jump burst
        self.cooldown = 0.0
        self.groom = False
        self.quiet_s = 0.0
        self.rng = rng or np.random.default_rng(0)
        self.idle_dir = 0.0
        self.idle_t = 0.0

    def _r(self, name):
        return max(0.0, self.ema.get(name, 0.0) - self.r_base.get(name, 0.0))

    def update(self, rates, dnp01_spikes, dt, on_food=False, bio_ms=10.0):
        """rates: {group: Hz} over the last window; dnp01_spikes: count in the jump window this frame."""
        p = self.p
        a = 1.0 - math.exp(-bio_ms / p.ema_ms)
        for k, v in rates.items():
            self.ema[k] = self.ema.get(k, 0.0) + a * (v - self.ema.get(k, 0.0))
        cmd = MotorCommand()
        r09, rmdn = self._r("DNp09"), self._r("MDN")
        vf = p.v_forward * min(max((r09 - p.walk_thr) / (p.walk_sat - p.walk_thr), 0.0), 1.0)
        vb = p.v_back * min(max((rmdn - p.walk_thr) / (p.walk_sat - p.walk_thr), 0.0), 1.0)
        v_target = vf - vb
        right = self._r("DNa02_R") + 0.5 * self._r("DNa01_R")
        left = self._r("DNa02_L") + 0.5 * self._r("DNa01_L")
        delta = (right - left) + self.turn_bias * r09      # calibrated walk-coupled asymmetry removed
        if abs(delta) < p.turn_dead:
            delta = 0.0
        omega_target = -math.radians(p.turn_deg) * math.tanh(delta / p.turn_scale)   # positive delta = turn right = negative omega
        # groom with hysteresis
        rg = self._r("DNg11")
        if not self.groom and rg > p.groom_on:
            self.groom = True
        elif self.groom and rg < p.groom_off:
            self.groom = False
        cmd.groom = self.groom
        if self.groom:
            v_target, omega_target = 0.0, 0.0
        # jump / escape
        self.cooldown = max(0.0, self.cooldown - dt)
        if dnp01_spikes > 0 and self.cooldown <= 0.0 and self.jump_timer <= 0.0:
            side = self._r("DNp01_L") - self._r("DNp01_R")
            away = -1.0 if side > 0 else 1.0            # stronger left input -> threat on left -> turn right
            cmd.jump = True
            cmd.jump_turn = away * math.radians(p.jump_turn_deg)
            self.jump_timer = p.jump_dur_s
            self.cooldown = p.jump_cooldown_s
        if self.jump_timer > 0.0:
            self.jump_timer -= dt
            self.v_actual = p.jump_speed
            self.omega_actual = 0.0
            cmd.v, cmd.omega = self.v_actual, 0.0
            cmd.eat = False
            return cmd
        # idle: scripted slow wander when the brain has been silent
        dn_max = max([self._r(k) for k in ("DNp09", "MDN", "DNa02_L", "DNa02_R", "DNg11", "MN9", "DNp01_L", "DNp01_R")] + [0.0])
        self.quiet_s = self.quiet_s + dt if dn_max < 5.0 else 0.0
        cmd.idle = self.quiet_s >= p.idle_s
        if cmd.idle:
            self.idle_t -= dt
            if self.idle_t <= 0.0:
                self.idle_t = float(self.rng.uniform(1.0, 3.0))
                self.idle_dir = float(self.rng.uniform(-0.6, 0.6))
            v_target, omega_target = p.idle_speed, self.idle_dir
        k = min(1.0, dt / p.lowpass_s)
        self.v_actual += (v_target - self.v_actual) * k
        self.omega_actual += (omega_target - self.omega_actual) * k
        cmd.v, cmd.omega = self.v_actual, self.omega_actual
        cmd.eat = on_food and self._r("MN9") > p.eat_thr
        return cmd
