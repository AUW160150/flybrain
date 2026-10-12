"""Garden dressing shared by both renderers: fruit patches, obstacle kinds, flowers, sky."""
import numpy as np

# Each food patch is one fruit. Colours are exact-match keys in the render check, chosen to differ from every fly.
FRUITS = [
    dict(name="grapes",     color=(0.50, 0.20, 0.72), accent=(0.30, 0.55, 0.20)),
    dict(name="watermelon", color=(0.20, 0.60, 0.25), accent=(0.98, 0.35, 0.45)),
    dict(name="cherries",   color=(0.62, 0.05, 0.12), accent=(0.30, 0.55, 0.20)),
    dict(name="kiwi",       color=(0.45, 0.35, 0.18), accent=(0.55, 0.78, 0.22)),
]
OBSTACLE_KINDS = ["tree", "bush", "rock", "bush", "tree"]
FLOWER_COLORS = [(1.0, 1.0, 1.0), (1.0, 0.55, 0.8), (1.0, 0.85, 0.2), (0.65, 0.45, 0.95), (1.0, 0.4, 0.3)]
SKY = (0.53, 0.78, 0.98)
GRASS = (0.36, 0.62, 0.26)
GRASS_DARK = (0.28, 0.52, 0.20)
FENCE = (0.96, 0.96, 0.92)
TRUNK = (0.45, 0.30, 0.15)
LEAF = (0.22, 0.52, 0.18)
ROCK = (0.55, 0.55, 0.52)


def flower_field(arena_half, n=60, seed=7, keep_clear=None):
    """Random flower positions and colour indices, away from the centre and from the given circles."""
    rng = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        p = rng.uniform(-arena_half + 1, arena_half - 1, size=2)
        if np.linalg.norm(p) < 3.0:
            continue
        if keep_clear and any(np.linalg.norm(p - c) < r + 0.8 for c, r in keep_clear):
            continue
        out.append((p, int(rng.integers(len(FLOWER_COLORS))), float(rng.uniform(0.8, 1.2))))
    return out


def grass_texture(size=128, seed=3):
    """uint8 (size, size, 3) mottled grass tile."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, (size, size))
    for _ in range(2):                       # cheap blur
        noise = (noise + np.roll(noise, 1, 0) + np.roll(noise, -1, 0) + np.roll(noise, 1, 1) + np.roll(noise, -1, 1)) / 5
    t = (noise - noise.min()) / (noise.max() - noise.min())
    base = np.array(GRASS_DARK)[None, None, :] * (1 - t[..., None]) + np.array(GRASS)[None, None, :] * t[..., None]
    speck = rng.random((size, size)) < 0.03
    base[speck] = np.array(GRASS) * 1.25
    return (np.clip(base, 0, 1) * 255).astype(np.uint8)
