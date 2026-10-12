import math
import numpy as np
from flyworld.world import World
from flyworld.config import WorldParams
from flyworld.decoder import MotorCommand


def test_layout_and_snapshot():
    w = World(WorldParams(), seed=1)
    assert len(w.flies) == 7 and len(w.foods) == 4 and len(w.obstacles) == 5
    s = w.snapshot()
    assert len(s["flies"]) == 7 and s["flies"][0]["kind"] == "big"


def test_walls_clamp():
    w = World(WorldParams(), seed=1)
    f = w.flies[1]
    f.pos = np.array([w.p.arena_half - 0.5, 0.0]); f.heading = 0.0
    for _ in range(30):
        w.step(1 / 30, {1: MotorCommand(v=10.0)})
    assert f.pos[0] <= w.p.arena_half - f.radius + 1e-9


def test_obstacle_pushes_out():
    w = World(WorldParams(), seed=1)
    f = w.flies[1]; o = w.obstacles[0]
    f.pos = o.pos + np.array([0.1, 0.0])
    w.step(1 / 30, {1: MotorCommand()})
    assert np.linalg.norm(f.pos - o.pos) >= o.radius + f.radius - 1e-6


def test_eat_and_hit_events():
    w = World(WorldParams(), seed=1)
    f = w.flies[1]; fd = w.foods[0]
    f.pos = fd.pos.copy()
    w.step(1 / 30, {1: MotorCommand(eat=True)})
    assert f.on_food and fd.amount < 5.0 and f.eaten > 0
    w.big.pos = f.pos + np.array([0.5, 0.0])
    w.step(1 / 30, {1: MotorCommand()})
    assert ("hit", 1) in w.events and f.hits == 1


def test_jump_turns_heading_and_logs():
    w = World(WorldParams(), seed=1)
    f = w.flies[1]; h0 = f.heading
    w.step(1 / 30, {1: MotorCommand(v=8.0, jump=True, jump_turn=math.radians(45))})
    assert abs(((f.heading - h0 + math.pi) % (2 * math.pi) - math.pi) - math.radians(45)) < 1e-6
    assert ("jump", 1) in w.events and len(w.log) == 1 and len(w.log[0]) == 7


def test_fly_profiles():
    from flyworld.profiles import FLY_PROFILES, by_name
    w = World(WorldParams(), seed=0)
    names = [f.name for f in w.flies]
    assert names == ["Nick", "Kathy", "Isshan", "Parth", "Leyla", "Jack", "Rodela"]
    assert w.big.name == "Nick" and w.big.sex == "male" and w.big.color == (0.96, 0.96, 0.96)
    assert {f.sex for f in w.npcs} == {"male", "female"}
    assert all(f.radius > WorldParams().fly_radius for f in w.npcs if f.sex == "female")
    assert len({f.color for f in w.flies}) == 7 and by_name("leyla") == 4
