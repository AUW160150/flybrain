"""Authored RGB garden and display projection of the measured reference rays.

RGB is a display convention, not a fly spectral response. The scene and manual
flight are illustrative; neither is inferred from the connectome.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

from .optics import Pose, pinhole_rays, rotate_rays, unit_vectors
from .exploration import fly_objects

SCENE_VERSION = "rgb-garden-flies-v2"
FOV_DEG = 110.0
DISPLAY_CUTOFF_DEG = 6.0


def initial_pose():
    return Pose(x=-10, y=0, z=1.2, pitch_deg=-6)


def perspective_projection(rays, width, height, horizontal_fov_deg=FOV_DEG,
                           max_distance_deg=DISPLAY_CUTOFF_DEG):
    """Project both eyes into one forward display, without binocular processing.

    Each pixel takes ONE nearest measured directional sample. Unobserved gaps
    remain masked. The Voronoi cells and perspective are display choices, not a
    claim about the fly's percept, ommatidial shape or physiological blur.
    """
    if width < 1 or height < 1 or not 0 < max_distance_deg <= 180:
        raise ValueError("Positive dimensions and a cutoff in (0, 180] required")
    query = pinhole_rays(width, height, horizontal_fov_deg)
    distance, indices = cKDTree(unit_vectors(rays)).query(query)
    cutoff = 2 * np.sin(np.radians(max_distance_deg) / 2)
    return indices.reshape(height, width), (distance <= cutoff).reshape(height, width)


def fly_pixels(samples, indices, visible):
    """No invented signals or smoothing between measured samples."""
    rgb = np.asarray(samples)[indices].copy()
    rgb[~visible] = (0.045, 0.065, 0.07)
    return rgb


def move_observer(pose, forward=0., left=0., turn=0., look_up=0., rise=0., dt=0.):
    """Manual free flight in arbitrary scene units; no neural motor controller."""
    if not np.isfinite([forward, left, turn, look_up, rise, dt]).all() or dt < 0:
        raise ValueError("Finite controls and nonnegative time required")
    norm = max(1., float(np.linalg.norm([forward, left, rise])))
    pose.move(forward / norm, left / norm, turn, dt)
    pose.z = float(np.clip(pose.z + 3 * dt * rise / norm, .35, 10.))
    pose.pitch_deg = float(np.clip(pose.pitch_deg + 55 * look_up * dt, -75, 75))


def look_observer(pose, dx, dy):
    # Screen-right motion is negative yaw in the published +y-left head frame.
    pose.yaw_deg = (pose.yaw_deg - .16 * dx + 180) % 360 - 180
    pose.pitch_deg = float(np.clip(pose.pitch_deg - .16 * dy, -75, 75))


def _garden_objects():
    # Ellipsoid centers, radii, display RGB. Procedural assets, no biological scale.
    objects = [
        ((1.0, 2.6, 2.0), (2.1, 2.0, 2.0), (.94, .12, .09)),
        ((1.0, 2.6, 4.1), (.13, .15, .55), (.28, .16, .08)),
        ((1.0, 3.25, 4.35), (.5, .85, .12), (.32, .61, .12)),
        ((6.5, -4.5, 2.3), (2.4, 2.4, 2.3), (1., .53, .06)),
        ((6.5, -4.5, 4.65), (.12, .12, .3), (.27, .22, .08)),
        ((-1., 7., .5), (2.8, 1.4, .28), (.29, .57, .12)),
        ((-4., -7., .4), (2.6, 1.2, .25), (.38, .63, .15)),
        ((9., 7., .6), (1.9, 1.2, .55), (.42, .39, .3)),
        ((-3., 4.5, .18), (.65, .5, .22), (.62, .55, .38)),
        ((-5., -3.5, .13), (.45, .65, .17), (.54, .49, .36)),
    ]
    # Two large flowers form stable, easy-to-recognize turning landmarks.
    for x, y, h, petal in [(2., -8., 6., (.73, .29, .82)), (8., 8., 7., (1., .76, .2))]:
        objects.append(((x, y, h / 2), (.14, .14, h / 2), (.21, .44, .12)))
        objects.append(((x, y + .65, h * .4), (.55, 1., .16), (.31, .55, .13)))
        for angle in np.linspace(0, 2 * np.pi, 6, endpoint=False):
            objects.append(((x, y + np.cos(angle) * .95, h + np.sin(angle) * .95),
                            (.38, .72, .72), petal))
        objects.append(((x - .4, y, h), (.4, .53, .53), (1., .64, .08)))
    for x, y in [(15, 14), (20, 6), (20, -5), (14, -15), (-12, 17), (-17, -16), (-22, 1)]:
        objects.append(((x, y, 2.), (5., 4., 2.7), (.25, .45, .17)))
    return objects


_OBJECTS = _garden_objects()
_LIGHT = unit_vectors([[-.45, -.35, 1.]])[0]


def avoid_fruit(pose):
    """Simple observer clearance for the two fruits, not a fly body physics model."""
    point = np.array([pose.x, pose.y, pose.z])
    for center, radii, _ in [_OBJECTS[0], _OBJECTS[3]]:
        center, extent = np.asarray(center), np.asarray(radii) + .18
        offset = (point - center) / extent
        norm = np.linalg.norm(offset)
        if norm < 1:
            direction = offset / norm if norm > 1e-8 else np.array([-1., 0., 0.])
            point = center + direction * extent
    pose.x, pose.y, pose.z = map(float, point)
    pose.z = max(.35, pose.z)


def scene_rgb(rays, pose: Pose, time_s=0.):
    """Deterministic ideal-direction samples of an illustrative RGB garden.

    Floating values in [0,1] are authored display intensities, not spectral
    radiance or receptor activations. Co-located eyes; no optical blur.
    """
    directions = rotate_rays(unit_vectors(rays), pose.yaw_deg, pose.pitch_deg)
    origin = np.array([pose.x, pose.y, pose.z])
    distance = np.full(len(directions), np.inf)
    sky_mix = np.clip(directions[:, 2], 0, 1)[:, None] ** .6
    color = np.array([.78, .88, .82]) * (1 - sky_mix) + np.array([.27, .62, .85]) * sky_mix
    with np.errstate(divide="ignore", invalid="ignore"):
        t = -pose.z / directions[:, 2]
    ground = (t > 0) & np.isfinite(t)
    xy = origin[:2] + np.where(ground, t, 0)[:, None] * directions[:, :2]
    # Broad grass tufts and a winding earth path provide visible motion parallax.
    texture = (.5 + .24 * np.sin(2.1 * xy[:, 0]) * np.cos(2.6 * xy[:, 1])
               + .13 * np.sin(5.4 * xy[:, 0] + 3.7 * xy[:, 1]))
    grass = np.array([.23, .38, .075]) + texture[:, None] * np.array([.22, .22, .07])
    path_center = -.6 + 1.4 * np.sin(.17 * xy[:, 0])
    path = np.abs(xy[:, 1] - path_center) < (1.9 + .2 * np.sin(xy[:, 0]))
    earth = np.array([.63, .47, .27]) + texture[:, None] * np.array([.16, .14, .10])
    ground_color = np.where(path[:, None], earth, grass)
    # Authored soft contact shading under fruit and plants (not spectral lighting).
    shadow = np.zeros(len(directions))
    for cx, cy, spread in [(1., 2.6, 2.4), (6.5, -4.5, 2.8), (2., -8., 1.2), (8., 8., 1.5)]:
        shadow = np.maximum(shadow, .34 * np.exp(-((xy[:, 0] - cx - .6) ** 2 + (xy[:, 1] - cy - .3) ** 2) / spread ** 2))
    ground_color *= (1 - shadow[:, None])
    color[ground] = ground_color[ground]
    distance[ground] = t[ground]

    # A drifting seed is a moving visual target, not a simulated other animal.
    objects = _OBJECTS + fly_objects(time_s, pose) + [((4., 3 * np.sin(.45 * time_s), 4.8 + .5 * np.sin(.7 * time_s)),
                           (.24, .4, .18), (.98, .94, .63))]
    for center, radii, pigment in objects:
        center, radii = np.asarray(center), np.asarray(radii)
        offset = (origin - center) / radii
        scaled = directions / radii
        a = np.einsum("ij,ij->i", scaled, scaled)
        b = scaled @ offset
        disc = b * b - a * (offset @ offset - 1)
        root = np.sqrt(np.maximum(disc, 0))
        near, far = (-b - root) / a, (-b + root) / a
        t = np.where(near > 1e-7, near, far)
        hit = (disc >= 0) & (t > 1e-7) & (t < distance)
        if not hit.any():
            continue
        points = origin + t[hit, None] * directions[hit]
        normal = unit_vectors((points - center) / radii ** 2)
        diffuse = np.maximum(normal @ _LIGHT, 0)
        shade = .46 + .54 * diffuse
        highlight = .14 * diffuse ** 22
        color[hit] = np.asarray(pigment) * shade[:, None] + highlight[:, None]
        distance[hit] = t[hit]
    # Distance haze is an authored visual cue and is identical in both displays.
    haze = np.where(np.isfinite(distance), .22 * (1 - np.exp(-distance / 45)), 0)[:, None]
    color = color * (1 - haze) + np.array([.78, .88, .82]) * haze
    return np.clip(color, 0, 1).astype(np.float32)
