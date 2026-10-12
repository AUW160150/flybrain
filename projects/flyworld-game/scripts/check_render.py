"""Headless render check (SDL dummy driver): every named fly appears in its own colour, and the
activity panel on the right changes when a fly's looming neurons are stimulated."""
import os, sys
from pathlib import Path
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import numpy as np
from flyworld.game import Game
from flyworld.render_pygame import PygameRenderer
from flyworld.profiles import FLY_PROFILES, rgb255, EYE_WHITE
from flyworld.garden import FRUITS, GRASS


def main():
    game = Game(seed=0)
    game.set_mode("shepherd")
    r = PygameRenderer(game)
    r.step_frames(15)
    img1 = r.frame_array()
    r.save("runs/check_render_rest.png")
    failures = []
    half = game.wp.arena_half
    x0, y0 = r.to_px(-half, half); x1, y1 = r.to_px(half, -half)
    mean = img1[y0:y1, x0:x1].reshape(-1, 3).mean(axis=0)
    print(f"lawn mean colour {tuple(int(v) for v in mean)}")
    if not (mean[1] > mean[0] + 30 and mean[1] > mean[2] + 30):
        failures.append("lawn is not green")
    for p in FLY_PROFILES + FRUITS:
        c = np.array(rgb255(p["color"]), dtype=np.uint8)
        n = int(np.all(img1 == c, axis=-1).sum())
        print(f"{p['name']:8s} colour {tuple(int(x) for x in c)} pixels={n}")
        if n < 20:
            failures.append(f"{p['name']} colour not drawn")
    kathy = game.world.flies[1]
    kx, ky = r.to_px(*kathy.pos)
    eye = np.array(rgb255(EYE_WHITE), dtype=np.uint8)
    ys, xs = np.nonzero(np.all(img1 == eye, axis=-1))
    near = int(((xs - kx) ** 2 + (ys - ky) ** 2 <= (kathy.radius * r.scale * 3) ** 2).sum())
    print(f"Kathy eyes: {near} eye-white pixels within her body at ({kx},{ky})")
    if near < 5:
        failures.append("Kathy's Jigglypuff eyes not drawn")
    game.panel.focus = 1
    game.panel.stim.add((1, "LC4")); game.panel.stim.add((1, "LPLC2"))
    r.step_frames(15)
    img2 = r.frame_array()
    r.save("runs/check_render_stim.png")
    region = slice(r.arena_right, None)
    diff = np.abs(img1[:, region].astype(int) - img2[:, region].astype(int)).sum()
    rates = game.last_rates[1]
    print(f"activity panel pixel change={diff}  Kathy LC4={rates.get('LC4', 0):.0f} Hz DNp01={rates.get('DNp01', 0):.0f} Hz")
    if diff < 1000:
        failures.append("activity panel did not change under stimulation")
    if rates.get("LC4", 0) < 50:
        failures.append("LC4 stimulation not reflected in readout")
    r.close()
    if failures:
        print("RENDER CHECK FAIL: " + " | ".join(failures)); return 1
    print("RENDER CHECK OK"); return 0


if __name__ == "__main__":
    sys.exit(main())
