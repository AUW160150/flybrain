"""Shared data prep for the activity displays: LED levels per fly and the focus fly's spike raster."""
import numpy as np

from .profiles import LED_GROUPS, RASTER_GROUPS
from .brain import RING_MS

BG = (25, 28, 35)


def led_levels(rates, groups=LED_GROUPS, full=100.0):
    """0..1 brightness per LED group from a {group: Hz} dict."""
    return [min(1.0, max(0.0, rates.get(g, 0.0) / full)) for g in groups]


def raster_image(brain, b, ring, ptr, color, groups=RASTER_GROUPS):
    """uint8 (rows, RING_MS, 3) image: time runs left to right and ends now; brightness = spikes / cells."""
    rows = [g for g in groups if g in brain.out_index]
    img = np.empty((len(rows), RING_MS, 3), dtype=np.uint8)
    img[:] = BG
    order = (np.arange(ptr, ptr + RING_MS) % RING_MS)          # oldest ... newest
    col = np.array([c * 255 for c in color], dtype=np.float32)
    for r, g in enumerate(rows):
        counts = ring[b, brain.out_index[g], order]
        size = len(brain.groups[g])
        inten = np.clip(counts / max(1.0, 0.05 * size), 0.0, 1.0)[:, None]
        img[r] = (BG * (1 - inten) + col * inten).astype(np.uint8)
    return img, rows
