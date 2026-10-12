import numpy as np
import pytest

from flyvision.eye_reference import validate_permutation
from flyvision.optics import Pose, angles_to_rays, display_projection, pinhole_rays, rays_to_angles, rotate_rays, scene_radiance, unit_vectors


def test_axis_conventions_and_roundtrip():
    az = np.array([0, 90, -90, 179, -179, 30])
    el = np.array([0, 0, 0, 20, -30, 80])
    vectors = angles_to_rays(az, el)
    assert np.allclose(vectors[:3], [[1, 0, 0], [0, 1, 0], [0, -1, 0]])
    az_out, el_out = rays_to_angles(vectors)
    assert np.allclose(az, az_out) and np.allclose(el, el_out)
    assert np.allclose(rotate_rays([[1, 0, 0]], 90, 0), [[0, 1, 0]])
    assert np.allclose(rotate_rays([[1, 0, 0]], 0, 90), [[0, 0, 1]])


def test_invalid_vectors_and_correspondence_fail_closed():
    for vectors in [[[0, 0, 0]], [[1, np.nan, 0]], [[1, 0]]]:
        with pytest.raises(ValueError): unit_vectors(vectors)
    for values in [[0, 1, 2], [1, 1, 3], [1, 2, 4], [1, 2.5, 3]]:
        with pytest.raises(ValueError): validate_permutation(values, 3)
    assert validate_permutation([2, 3, 1], 3).tolist() == [1, 2, 0]


def test_projection_masks_unsampled_directions():
    idx, visible = display_projection(np.array([[1, 0, 0]]), width=360, height=180, max_distance_deg=3)
    assert visible[90, 180] and not visible[90, 0]
    assert visible.sum() < 50
    assert idx.shape == (180, 360)


def test_scene_depends_on_pose_and_is_reproducible():
    rays = pinhole_rays(64, 48)
    p = Pose()
    a = scene_radiance(rays, p, 0)
    assert np.isfinite(a).all() and (a >= 0).all() and (a <= 1).all()
    assert np.array_equal(a, scene_radiance(rays, p, 0))
    p.move(1, 0, 0.5, 0.5)
    b = scene_radiance(rays, p, 0)
    assert np.mean(a != b) > 0.1


def test_surface_signs_and_inside_sphere_intersection():
    rays = np.array([[1, 0, -1], [0, 0, 1], [1, 0, 0]])
    signals = scene_radiance(rays, Pose(x=3, y=4, z=2), 0)
    assert np.allclose(signals, 0.25)  # exit intersection when the origin is inside the landmark


def test_zero_time_motion_and_negative_time_validation():
    p = Pose()
    original = (p.x, p.y, p.yaw_deg)
    p.move(1, 1, 1, 0)
    assert (p.x, p.y, p.yaw_deg) == original
    with pytest.raises(ValueError): p.move(1, 0, 0, -1)
