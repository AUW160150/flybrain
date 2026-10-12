"""Cheap geometric proxies that turn the world around a fly into currents on named sensory groups.

All angles in radians, fly-centred: bearing phi > 0 means the object is on the fly's left.
"""
import math
import numpy as np

from .config import WorldParams

MAX_AMP = 0.25


def hemifield(phi):
    """Odour-style weights: 0.5/0.5 straight ahead, 1/0 at 90 deg left."""
    wl = min(max(0.5 + math.sin(phi), 0.0), 1.0)
    wr = min(max(0.5 - math.sin(phi), 0.0), 1.0)
    return wl, wr


def binocular(phi):
    """Looming weights with frontal overlap: 1/1 straight ahead, 1/0 at 90 deg left."""
    wl = min(max(1.0 + math.sin(phi), 0.0), 1.0)
    wr = min(max(1.0 - math.sin(phi), 0.0), 1.0)
    return wl, wr


def relative(fly_pos, fly_heading, obj_pos):
    dx, dy = obj_pos[0] - fly_pos[0], obj_pos[1] - fly_pos[1]
    d = math.hypot(dx, dy)
    phi = math.atan2(dy, dx) - fly_heading
    phi = (phi + math.pi) % (2 * math.pi) - math.pi
    return d, phi


class SensoryEncoder:
    """Keeps last-frame angular sizes so expansion velocity can be computed."""

    def __init__(self, params=None):
        self.p = params or WorldParams()
        self.prev_theta = {}
        self.odour_decay = getattr(self.p, "odour_decay", 4.0)

    def encode(self, fly_id, fly_pos, fly_heading, objects, dt, on_food=False):
        """objects: iterable of (obj_id, pos, radius, kind) with kind in {big, fly, food, obstacle}.
        Returns {group_name: amplitude} (only nonzero entries)."""
        p = self.p
        amps = {}

        def add(name, val):
            if val > 0:
                amps[name] = amps.get(name, 0.0) + val

        fov = math.radians(p.fov_deg)
        seen = set()
        for oid, pos, radius, kind in objects:
            d, phi = relative(fly_pos, fly_heading, pos)
            if d < 1e-6:
                continue
            key = (fly_id, oid)
            theta = 2.0 * math.atan2(radius, max(d, radius))
            prev = self.prev_theta.get(key, theta)
            self.prev_theta[key] = theta
            seen.add(key)
            if kind == "food":
                if d <= p.odour_range:
                    c = math.exp(-d / self.odour_decay)
                    wl, wr = hemifield(phi)
                    add("ORN_DM1_L", 0.15 * c * (0.5 + 0.5 * wl)); add("ORN_DM1_R", 0.15 * c * (0.5 + 0.5 * wr))
                    for g in ("ORN_DM4", "ORN_DC1"):
                        add(g + "_L", 0.075 * c * (0.5 + 0.5 * wl)); add(g + "_R", 0.075 * c * (0.5 + 0.5 * wr))
                continue
            if d > p.sense_range or abs(phi) > fov:
                continue
            wl, wr = binocular(phi)
            theta_dot = (theta - prev) / max(dt, 1e-6)
            if kind in ("big", "fly", "obstacle"):
                # LC4: expansion velocity saturating at 1.5 rad/s; LPLC2/LC16: angular size above 0.15 rad while expanding
                vel = 0.2 * min(max(theta_dot / 1.5, 0.0), 1.0)
                size = 0.2 * min(max((theta - 0.15) / 0.6, 0.0), 1.0) * (1.0 if theta_dot > 0 else 0.0)
                for side, w in (("_L", wl), ("_R", wr)):
                    add("LC4" + side, vel * w); add("LC6" + side, vel * w)
                    add("LPLC2" + side, size * w); add("LC16" + side, size * w)
            if kind == "fly" and theta < 0.3:
                add("LC11_L", 0.1 * wl); add("LC11_R", 0.1 * wr)
            if kind == "big" and d <= p.da1_range:
                c = math.exp(-d / 4.0)
                add("ORN_DA1", 0.1 * c)          # parent group: non-lateralized, covers unknown-side cells
        # forget objects that left the field so re-entry does not look like a huge expansion
        for key in [k for k in self.prev_theta if k[0] == fly_id and k not in seen]:
            del self.prev_theta[key]
        if on_food:
            add("LB3c_L", 0.2); add("LB3c_R", 0.2)
        return {k: min(v, MAX_AMP) for k, v in amps.items() if v > 0}


def amps_to_matrix(brain, per_fly_amps):
    """per_fly_amps: list (len B) of {group: amp}. Unknown-side cells (group without _L/_R) are
    handled by also driving the parent group at the mean of both sides when only sided keys exist."""
    a = np.zeros((brain.B, len(brain.in_names)), dtype=np.float32)
    for b, amps in enumerate(per_fly_amps):
        for name, val in amps.items():
            if name in brain.in_index:
                a[b, brain.in_index[name]] += val
    return a
