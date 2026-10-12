"""Human-facing exploration aids and authored fly actors, separate from sensing.

Object positions here are gameplay metadata, never neural inputs. Actor motion,
proximity reactions, discovery radii and names are authored, not fly physiology.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .optics import rotate_rays

ACTOR_VERSION = "scripted-garden-flies-v1"
LANDMARKS = [
    ("fruit", "The fruit grove", (-1., -.5, 1.2), 2.3),
    ("purple", "The purple flower", (1., -6.8, 5.5), 2.5),
    ("yellow", "The yellow flower", (7., 6.5, 6.5), 2.5),
]


def fly_actors(time_s, pose):
    """Deterministic animation with smooth spatial repulsion, not neural behavior."""
    t = float(time_s)
    paths = [
        ("nearby", (-5.7 + .85 * np.sin(.4 * t), .7 + .9 * np.cos(.4 * t), 1.9 + .3 * np.sin(.8 * t))),
        ("grove", (1. + 3.4 * np.cos(.28 * t), 2.6 + 3.4 * np.sin(.28 * t), 4.9 + .4 * np.sin(.7 * t))),
        ("flower", (2. + 1.8 * np.cos(.35 * t), -8. + 1.7 * np.sin(.35 * t), 6.6 + .4 * np.cos(.6 * t))),
    ]
    observer = np.array([pose.x, pose.y, pose.z])
    actors = []
    for index, (actor_id, center) in enumerate(paths):
        center = np.array(center, dtype=float)
        away = center - observer
        distance = np.linalg.norm(away)
        direction = away / distance if distance > 1e-8 else np.array([0., 1., 0.])
        response = .9 * max(0., 1 - distance / 3.2) ** 2
        center += response * direction
        actors.append({"id": actor_id, "position": center, "phase": 7 * t + index * 2.1,
                       "responding": response > .02})
    return actors


def fly_objects(time_s, pose):
    """Stylized fly-shaped ellipsoids, sampled as scene geometry by both views."""
    objects = []
    for actor in fly_actors(time_s, pose):
        center, phase = actor["position"], actor["phase"]
        def part(offset, radii, color):
            objects.append((center + offset, radii, color))
        part((.2, 0, 0), (.43, .23, .23), (.14, .12, .09))
        part((-.18, 0, .06), (.25, .24, .25), (.24, .22, .16))
        part((-.39, 0, .08), (.22, .24, .21), (.15, .13, .10))
        for side in [-1, 1]:
            part((-.43, .19 * side, .11), (.12, .105, .14), (.85, .19, .10))
            part((.1, side * .43, .16 + .15 * np.sin(phase)), (.47, .42, .055), (.78, .85, .78))
            for x in [-.2, .08, .32]:
                part((x, side * .26, -.21), (.045, .16, .055), (.12, .12, .08))
    return objects


def screen_direction(target, pose, width, height, fov_deg=110):
    """HUD direction only: azimuth/pitch relative to the observer, plus projection."""
    delta = np.asarray(target) - [pose.x, pose.y, pose.z]
    # rotate_rays uses row vectors; transpose the head-to-world basis to invert.
    local = delta @ rotate_rays(np.eye(3), pose.yaw_deg, pose.pitch_deg).T
    az = np.degrees(np.arctan2(local[1], local[0]))
    el = np.degrees(np.arctan2(local[2], np.hypot(local[0], local[1])))
    tangent = np.tan(np.radians(fov_deg) / 2)
    forward = max(float(local[0]), 1e-9)
    x = width / 2 * (1 - local[1] / (forward * tangent))
    y = height / 2 - width / 2 * local[2] / (forward * tangent)
    visible = local[0] > 0 and 28 < x < width - 28 and 30 < y < height - 55
    if visible:
        return float(x), float(y), "ahead"
    if abs(az) > 45:
        return (32. if az > 0 else width - 32.), height / 2, "left" if az > 0 else "right"
    return width / 2, (35. if el > 0 else height - 60.), "up" if el > 0 else "down"


@dataclass
class Exploration:
    visited: set = field(default_factory=set)
    events: list = field(default_factory=list)
    message: str = ""
    message_until: float = 0.
    near_time: float = 0.

    def update(self, pose, time_s, dt):
        observer = np.array([pose.x, pose.y, pose.z])
        nearby = fly_actors(time_s, pose)[0]["position"]
        if np.linalg.norm(nearby - observer) < 2.8:
            self.near_time += dt
        else:
            self.near_time = 0.
        candidates = [("nearby", "You found another fly!", self.near_time >= .6)]
        candidates += [(key, f"Discovered: {name.lower()}", np.linalg.norm(observer - point) < radius)
                       for key, name, point, radius in LANDMARKS]
        for key, message, reached in candidates:
            if reached and key not in self.visited:
                self.visited.add(key)
                self.events.append({"id": key, "time_s": time_s, "observer": observer.tolist()})
                self.message = message
                self.message_until = time_s + 4.

    def objective(self, pose, time_s):
        if "nearby" not in self.visited:
            return ("Find the nearby fly", "Follow the marker; move closer and fly alongside it.",
                    fly_actors(time_s, pose)[0]["position"])
        for key, name, point, _ in LANDMARKS:
            if key not in self.visited:
                hint = "Follow the path toward the fruit." if key == "fruit" else "Hold Space to rise toward the flower."
                return f"Explore {name.lower()}", hint, np.array(point)
        return "The garden is yours", "All four discoveries found. Keep exploring with the flies.", None
