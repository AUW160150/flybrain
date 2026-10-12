import numpy as np
import pytest

from flyvision.optics import Pose, pinhole_rays
from flyvision.world import (fly_pixels, initial_pose, look_observer, move_observer,
                             perspective_projection, scene_rgb)


def test_forward_display_uses_only_reference_samples_and_masks_gaps():
    rays = pinhole_rays(21, 13)
    indices, visible = perspective_projection(rays, 21, 13, horizontal_fov_deg=100)
    assert visible.all()
    assert np.array_equal(indices.ravel(), np.arange(len(rays)))
    samples = np.random.default_rng(3).random((len(rays), 3))
    assert np.array_equal(fly_pixels(samples, indices, visible).reshape(-1, 3), samples)
    indices, visible = perspective_projection([[1, 0, 0]], 21, 13, max_distance_deg=3)
    assert visible[6, 10] and not visible[0, 0]
    assert not np.array_equal(fly_pixels([[1., 0., 0.]], indices, visible)[0, 0], [1, 0, 0])


def test_rgb_garden_is_colored_reproducible_and_changes_with_motion():
    rays = pinhole_rays(90, 50)
    pose = initial_pose()
    a = scene_rgb(rays, pose, 0)
    assert a.shape == (len(rays), 3) and a.dtype == np.float32
    assert np.isfinite(a).all() and a.min() >= 0 and a.max() <= 1
    assert np.mean(np.ptp(a, axis=1) > .1) > .8
    assert np.array_equal(a, scene_rgb(rays, pose, 0))
    move_observer(pose, forward=1, turn=.3, rise=.2, dt=.5)
    b = scene_rgb(rays, pose, 0)
    assert np.mean(np.any(a != b, axis=1)) > .5


def test_controls_follow_head_coordinates_and_do_not_accelerate_diagonally():
    p = Pose(x=0, y=0, z=1, yaw_deg=90)
    move_observer(p, forward=1, dt=.5)
    assert np.allclose([p.x, p.y], [0, 2])
    move_observer(p, left=1, dt=.5)
    assert np.allclose([p.x, p.y], [-2, 2])
    p = Pose(x=0, y=0)
    move_observer(p, forward=1, left=1, dt=1)
    assert np.isclose(np.linalg.norm([p.x, p.y]), 4)
    look_observer(p, 100, -100)
    assert p.yaw_deg < 0 and p.pitch_deg > 0
    move_observer(p, rise=-1, look_up=1, dt=100)
    assert p.z == .35 and p.pitch_deg == 75
    with pytest.raises(ValueError):
        move_observer(p, dt=-1)
