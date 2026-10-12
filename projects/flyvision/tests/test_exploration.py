import numpy as np

from flyvision.exploration import Exploration, LANDMARKS, fly_actors, screen_direction
from flyvision.optics import Pose
from flyvision.world import avoid_fruit, initial_pose, scene_rgb


def test_scripted_flies_are_reproducible_react_to_proximity_and_enter_optics():
    distant = initial_pose()
    a = fly_actors(0, distant)
    b = fly_actors(0, distant)
    assert len(a) == 3 and all(np.array_equal(x["position"], y["position"]) for x, y in zip(a, b))
    origin = a[0]["position"]
    close = Pose(*(origin - [1., 0., 0.]))
    reaction = fly_actors(0, close)[0]
    assert reaction["responding"]
    assert reaction["position"][0] > origin[0]
    assert not np.array_equal(a[1]["position"], fly_actors(1., distant)[1]["position"])
    # A ray aimed at the fly's dark abdomen must actually hit it in the scene.
    direction = origin - [distant.x, distant.y, distant.z]
    # Pose pitch must be zero because this test constructs a world-space direction.
    distant.pitch_deg = 0
    pixel = scene_rgb([direction], distant, 0)[0]
    assert pixel.mean() < .3


def test_discoveries_need_proximity_and_hover_then_advance_without_duplicates():
    experience = Exploration()
    p = initial_pose()
    experience.update(p, 0, 1)
    assert not experience.visited
    assert experience.objective(p, 0)[0] == "Find the nearby fly"
    p = Pose(x=-7.2, y=1.6, z=1.9)
    for step in range(8):
        experience.update(p, step / 10, .1)
    assert experience.visited == {"nearby"}
    assert experience.objective(p, 1)[0] == "Explore the fruit grove"
    for i, (_, _, point, _) in enumerate(LANDMARKS):
        p = Pose(*point)
        experience.update(p, 2 + i, .1)
        experience.update(p, 2 + i, .1)
    assert len(experience.visited) == 4 and len(experience.events) == 4
    assert experience.objective(p, 10)[2] is None


def test_direction_cues_follow_head_rotation_and_offscreen_targets():
    p = Pose(x=0, y=0, z=0)
    assert screen_direction([5, 0, 0], p, 1000, 600) == (500., 300., "ahead")
    assert screen_direction([5, 2, 0], p, 1000, 600)[0] < 500
    assert screen_direction([0, 5, 0], p, 1000, 600)[2] == "left"
    assert screen_direction([0, -5, 0], p, 1000, 600)[2] == "right"
    p.yaw_deg = 90
    x, y, direction = screen_direction([0, 5, 0], p, 1000, 600)
    assert np.allclose([x, y], [500, 300]) and direction == "ahead"
    p.pitch_deg = 45
    assert np.allclose(screen_direction([0, 5, 5], p, 1000, 600)[:2], [500, 300])


def test_fruit_clearance_keeps_the_observer_outside_surfaces():
    p = Pose(x=1., y=2.6, z=2.)
    avoid_fruit(p)
    offset = (np.array([p.x, p.y, p.z]) - [1., 2.6, 2.]) / [2.28, 2.18, 2.18]
    assert np.isclose(np.linalg.norm(offset), 1.)
    safe = initial_pose()
    before = [safe.x, safe.y, safe.z]
    avoid_fruit(safe)
    assert np.array_equal(before, [safe.x, safe.y, safe.z])
