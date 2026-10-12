"""Ray geometry and scene sampling. These are optical signals, not neural activity."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree


def unit_vectors(values):
    v = np.asarray(values, dtype=np.float64)
    if v.ndim != 2 or v.shape[1] != 3 or not np.isfinite(v).all():
        raise ValueError("Directions must be finite N by 3 vectors")
    norm = np.linalg.norm(v, axis=1)
    if (norm <= 0).any():
        raise ValueError("Zero direction vector")
    return v / norm[:, None]


def angles_to_rays(azimuth_deg, elevation_deg):
    az, el = np.broadcast_arrays(np.radians(azimuth_deg), np.radians(elevation_deg))
    return np.stack((np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)), axis=-1)


def rays_to_angles(rays):
    rays = unit_vectors(rays)
    return np.degrees(np.arctan2(rays[:, 1], rays[:, 0])), np.degrees(np.arcsin(np.clip(rays[:, 2], -1, 1)))


def rotate_rays(rays, yaw_deg=0.0, pitch_deg=0.0):
    """Body coordinates: +x forward, +y left, +z up. Positive yaw turns left."""
    yaw, pitch = np.radians([yaw_deg, pitch_deg])
    rz = np.array([[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]])
    ry = np.array([[np.cos(pitch), 0, -np.sin(pitch)], [0, 1, 0], [np.sin(pitch), 0, np.cos(pitch)]])
    return np.asarray(rays) @ (rz @ ry).T


def display_projection(rays, width=640, height=220, max_distance_deg=6.0):
    """Nearest angular sample for display, masking gaps beyond a declared cutoff.

    Cutoff is a display parameter, not an optical acceptance angle or a measured FOV.
    Positive azimuth is left, so the left edge of the panorama is +180 degrees.
    """
    if max_distance_deg <= 0 or max_distance_deg > 180:
        raise ValueError("Display cutoff must lie in (0, 180] degrees")
    az = 180 - (np.arange(width) + 0.5) * 360 / width
    el = 90 - (np.arange(height) + 0.5) * 180 / height
    query = angles_to_rays(az[None, :], el[:, None]).reshape(-1, 3)
    distances, indices = cKDTree(unit_vectors(rays)).query(query)
    angle = np.degrees(2 * np.arcsin(np.clip(distances / 2, 0, 1)))
    return indices.reshape(height, width), (angle <= max_distance_deg).reshape(height, width)


@dataclass
class Pose:
    x: float = -8.0
    y: float = 0.0
    z: float = 1.0
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0

    def move(self, forward, strafe, turn, dt):
        if not np.isfinite([forward, strafe, turn, dt]).all() or dt < 0:
            raise ValueError("Finite controls and nonnegative elapsed time required")
        # Authored movement in scene units; not a fly motor or biomechanics model.
        self.yaw_deg = (self.yaw_deg + turn * 75 * dt + 180) % 360 - 180
        a = np.radians(self.yaw_deg)
        self.x = float(np.clip(self.x + 4 * dt * (forward * np.cos(a) - strafe * np.sin(a)), -18, 18))
        self.y = float(np.clip(self.y + 4 * dt * (forward * np.sin(a) + strafe * np.cos(a)), -13, 13))


def scene_radiance(rays, pose: Pose, time_s=0.0):
    """Analytic achromatic test arena. Radiance is relative, dimensionless.

    One co-located origin for all rays; no modeled acceptance blur, spectrum,
    adaptation, phototransduction, binocular depth computation or neural dynamics.
    """
    directions = rotate_rays(unit_vectors(rays), pose.yaw_deg, pose.pitch_deg)
    origin = np.array([pose.x, pose.y, pose.z])
    n = len(directions)
    distance = np.full(n, np.inf)
    value = np.clip(0.56 + 0.28 * directions[:, 2], 0, 1)
    with np.errstate(divide="ignore", invalid="ignore"):
        t = -pose.z / directions[:, 2]
    valid = (t > 0) & np.isfinite(t)
    xy = origin[:2] + np.where(valid, t, 0)[:, None] * directions[:, :2]
    checker = ((np.floor(xy[:, 0] / 2) + np.floor(xy[:, 1] / 2)).astype(np.int64) % 2).astype(bool)
    value[valid] = np.where(checker[valid], 0.32, 0.58)
    distance[valid] = t[valid]
    # Walls are large contrast patterns that expose optical flow while moving.
    for axis, location in [(0, 20.0), (0, -20.0), (1, 15.0), (1, -15.0)]:
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (location - origin[axis]) / directions[:, axis]
        eligible = (t > 0) & (t < distance) & np.isfinite(t)
        point = origin + np.where(eligible, t, 0)[:, None] * directions
        eligible &= (point[:, 2] >= 0) & (point[:, 2] <= 9)
        across = point[:, 1 - axis]
        stripes = (np.floor(across / 2).astype(np.int64) % 2).astype(bool)
        value[eligible] = np.where(stripes[eligible], 0.18, 0.8)
        distance[eligible] = t[eligible]
    # A still landmark, a laterally moving dark sphere, and a bright obstacle.
    spheres = [((3, 4, 2), 2.0, 0.25), ((5, 4 * np.sin(time_s * 0.5), 2.2), 1.6, 0.035), ((11, -6, 2.5), 2.5, 0.9)]
    for center, radius, shade in spheres:
        offset = origin - np.asarray(center)
        b = directions @ offset
        disc = b * b - (offset @ offset - radius * radius)
        root = np.sqrt(np.maximum(disc, 0))
        near, far = -b - root, -b + root
        t = np.where(near > 1e-9, near, far)
        visible = (disc >= 0) & (t > 1e-9) & (t < distance)
        value[visible] = shade
        distance[visible] = t[visible]
    return value.astype(np.float32)


def pinhole_rays(width, height, horizontal_fov_deg=100.0):
    if not (0 < horizontal_fov_deg < 180):
        raise ValueError("Pinhole FOV must lie in (0, 180)")
    half_width = np.tan(np.radians(horizontal_fov_deg) / 2)
    yy = (1 - 2 * (np.arange(width) + 0.5) / width) * half_width
    zz = (1 - 2 * (np.arange(height) + 0.5) / height) * half_width * height / width
    y, z = np.meshgrid(yy, zz)
    return unit_vectors(np.column_stack([np.ones(width * height), y.ravel(), z.ravel()]))
