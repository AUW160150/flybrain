"""Engine-free arena: flies, food, obstacles, kinematics, collisions and a trajectory log."""
import math
from dataclasses import dataclass, field
import numpy as np

from .config import WorldParams
from .decoder import MotorCommand
from .profiles import FLY_PROFILES
from .garden import FRUITS, OBSTACLE_KINDS


@dataclass
class Fly:
    id: int
    pos: np.ndarray
    heading: float
    radius: float
    kind: str                 # "big" or "npc"
    speed: float = 0.0
    on_food: bool = False
    groom: bool = False
    jumping: bool = False
    idle: bool = False
    eaten: float = 0.0
    hits: int = 0             # contacts with the big fly
    name: str = ""
    sex: str = "male"
    color: tuple = (0.5, 0.5, 0.5)
    style: str = "fly"


@dataclass
class Food:
    id: int
    pos: np.ndarray
    radius: float
    amount: float = 5.0
    kind: str = "grapes"
    color: tuple = (0.5, 0.2, 0.72)
    accent: tuple = (0.3, 0.55, 0.2)


@dataclass
class Obstacle:
    id: int
    pos: np.ndarray
    radius: float
    kind: str = "bush"


class World:
    def __init__(self, params=None, seed=0):
        self.p = params or WorldParams()
        self.rng = np.random.default_rng(seed)
        p = self.p
        self.t = 0.0
        self.frame = 0
        self.obstacles = []
        for i in range(p.n_obstacles):
            self.obstacles.append(Obstacle(100 + i, self._free_spot(p.obstacle_radius, 3.0), p.obstacle_radius, kind=OBSTACLE_KINDS[i % len(OBSTACLE_KINDS)]))
        self.foods = []
        for i in range(p.n_food):
            fr = FRUITS[i % len(FRUITS)]
            self.foods.append(Food(200 + i, self._free_spot(p.food_radius, 2.0), p.food_radius, kind=fr["name"], color=fr["color"], accent=fr["accent"]))
        big = FLY_PROFILES[0]
        self.flies = [Fly(0, np.array([0.0, -p.arena_half * 0.6]), math.pi / 2, p.big_radius, "big",
                          name=big["name"], sex=big["sex"], color=big["color"])]
        for i in range(p.n_npc):
            ang = 2 * math.pi * i / p.n_npc
            r = p.arena_half * 0.45
            prof = FLY_PROFILES[1 + i % (len(FLY_PROFILES) - 1)]
            radius = p.fly_radius * (1.15 if prof["sex"] == "female" else 1.0)     # female flies are larger
            self.flies.append(Fly(i + 1, np.array([r * math.cos(ang), r * math.sin(ang)]), ang + math.pi, radius, "npc",
                                  name=prof["name"], sex=prof["sex"], color=prof["color"], style=prof.get("style", "fly")))
        self.npcs = self.flies[1:]
        self.big = self.flies[0]
        self.events = []
        self.log = []

    def _free_spot(self, radius, margin):
        p = self.p
        for _ in range(200):
            pos = self.rng.uniform(-p.arena_half + margin, p.arena_half - margin, size=2)
            if np.linalg.norm(pos) < 3.0:
                continue
            if all(np.linalg.norm(pos - o.pos) > o.radius + radius + margin for o in self.obstacles):
                return pos
        return pos

    def objects_for(self, fly):
        objs = []
        for f in self.flies:
            if f.id != fly.id:
                objs.append((f.id, f.pos, f.radius, f.kind if f.kind == "big" else "fly"))
        for fd in self.foods:
            if fd.amount > 0:
                objs.append((fd.id, fd.pos, fd.radius, "food"))
        for o in self.obstacles:
            objs.append((o.id, o.pos, o.radius, "obstacle"))
        return objs

    def food_under(self, fly):
        for fd in self.foods:
            if fd.amount > 0 and np.linalg.norm(fd.pos - fly.pos) < fd.radius + 0.1:
                return fd
        return None

    def step(self, dt, commands, big_cmd=(0.0, 0.0)):
        """commands: {fly_id: MotorCommand} for NPCs; big_cmd: (v, omega) for the big fly."""
        p = self.p
        self.events = []
        for fly in self.flies:
            if fly.kind == "big":
                v, omega = big_cmd
                fly.groom = fly.idle = False
            else:
                cmd = commands.get(fly.id, MotorCommand())
                v, omega = cmd.v, cmd.omega
                if cmd.jump:
                    fly.heading += cmd.jump_turn
                    self.events.append(("jump", fly.id))
                fly.jumping = cmd.jump or (abs(v) > p.big_speed)   # burst speed marks a jump in flight
                fly.groom, fly.idle = cmd.groom, cmd.idle
                fd = self.food_under(fly)
                if cmd.eat and fd is not None:
                    take = min(fd.amount, dt)
                    fd.amount -= take
                    fly.eaten += take
            fly.heading = (fly.heading + omega * dt + math.pi) % (2 * math.pi) - math.pi
            fly.pos = fly.pos + np.array([math.cos(fly.heading), math.sin(fly.heading)]) * v * dt
            fly.speed = v
            # walls
            lim = p.arena_half - fly.radius
            fly.pos = np.clip(fly.pos, -lim, lim)
            # obstacles
            for o in self.obstacles:
                d = fly.pos - o.pos
                dist = np.linalg.norm(d)
                min_d = o.radius + fly.radius
                if dist < min_d and dist > 1e-9:
                    fly.pos = o.pos + d / dist * min_d
            fly.on_food = self.food_under(fly) is not None
        # fly-fly contacts: push apart, count big-fly hits
        for i, a in enumerate(self.flies):
            for b in self.flies[i + 1:]:
                d = b.pos - a.pos
                dist = np.linalg.norm(d)
                min_d = a.radius + b.radius
                if dist < min_d:
                    if dist < 1e-9:
                        d, dist = np.array([1.0, 0.0]), 1.0
                    push = d / dist * (min_d - dist) / 2
                    a.pos = a.pos - push
                    b.pos = b.pos + push
                    if a.kind == "big" or b.kind == "big":
                        npc = b if a.kind == "big" else a
                        npc.hits += 1
                        self.events.append(("hit", npc.id))
        self.t += dt
        self.frame += 1
        self.log.append([[float(f.pos[0]), float(f.pos[1]), float(f.heading), float(f.speed)] for f in self.flies])

    def snapshot(self):
        return dict(t=self.t, frame=self.frame,
                    flies=[dict(id=f.id, name=f.name, sex=f.sex, kind=f.kind, x=float(f.pos[0]), y=float(f.pos[1]), heading=float(f.heading),
                                speed=float(f.speed), eaten=float(f.eaten), hits=f.hits) for f in self.flies],
                    foods=[dict(id=fd.id, kind=fd.kind, x=float(fd.pos[0]), y=float(fd.pos[1]), amount=float(fd.amount)) for fd in self.foods],
                    obstacles=[dict(id=o.id, x=float(o.pos[0]), y=float(o.pos[1]), r=float(o.radius)) for o in self.obstacles])


def behaviour_word(fly):
    if fly.jumping: return "JUMP"
    if fly.groom: return "groom"
    if fly.on_food and fly.kind == "npc": return "eat"
    if abs(fly.speed) > 0.5: return "walk" if fly.speed > 0 else "back"
    if fly.idle: return "wander"      # scripted slow wander after 2 s of brain silence, the only non-connectome behaviour
    return "still"
