"""First-person exploration through published eye samples; RGB is illustrative."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path

import numpy as np

from .evidence import sha256, write_json
from .eye_reference import load_reference
from .exploration import ACTOR_VERSION, Exploration, screen_direction
from .optics import display_projection, pinhole_rays
from .world import (DISPLAY_CUTOFF_DEG, FOV_DEG, SCENE_VERSION, avoid_fruit, fly_pixels,
                    initial_pose, look_observer, move_observer,
                    perspective_projection, scene_rgb)

ROOT = Path(__file__).resolve().parents[1]


def run_viewer(geometry, output, headless=False, frames=None, view="fly", panel=None):
    if output.exists():
        raise ValueError("Use a new recording directory; prior runs are immutable")
    if frames is not None and frames < 1:
        raise ValueError("Frame count must be positive")
    if view not in {"fly", "camera"} or panel not in {None, "help", "science"}:
        raise ValueError("Unknown view or panel")
    if headless:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"
    os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    import pygame

    frame, geometry_manifest = load_reference(geometry)
    registration = json.loads((geometry / "registration_audit.json").read_text())
    rays = frame[["forward", "left", "up"]].to_numpy()
    eye_rows = {eye: np.flatnonzero(frame.eye.eq(eye).to_numpy()) for eye in ["L", "R"]}
    panorama = {eye: display_projection(rays[rows], 280, 100, DISPLAY_CUTOFF_DEG)
                for eye, rows in eye_rows.items()}
    output.mkdir(parents=True)
    try:
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.set_mode((1200, 760), pygame.RESIZABLE)
    except pygame.error as exc:
        write_json(output / "manifest.json", {
            "status": "FAILED", "stage": "DISPLAY_INITIALIZATION", "error": str(exc),
            "neural_simulation_run": False, "physiological_validation": False,
        })
        pygame.quit()
        raise RuntimeError("No desktop display is available. Run this command in a local desktop terminal, or use --headless --frames 90 for an offscreen recording.") from exc
    pygame.display.set_caption("FlyVision — explore the garden")
    fonts = {size: pygame.font.Font(None, size) for size in [18, 20, 22, 24, 28, 32, 38]}
    clock = pygame.time.Clock()
    pose, elapsed, frame_index, paused = initial_pose(), 0., 0, False
    running, captured = True, False
    exploration, guidance = Exploration(), True
    last_values = np.zeros((len(rays), 3), dtype=np.float32)
    projection_size, projection, camera_rays = None, None, None
    recording = (output / "optical_samples.f32").open("wb")
    poses = (output / "trajectory.csv").open("w")
    poses.write("frame,time_s,x_scene,y_scene,z_scene,yaw_deg,pitch_deg,paused,view\n")
    manifest = {
        "status": "RUNNING", "kind": "REFERENCE_OPTICAL_SIMULATION", "schema_version": 2,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "geometry_run": str(geometry), "geometry_manifest_sha256": sha256(geometry / "manifest.json"),
        "reference_commit": geometry_manifest["reference_commit"],
        "code_sha256": {name: sha256(Path(__file__).with_name(name))
                        for name in ["viewer.py", "world.py", "exploration.py", "optics.py", "eye_reference.py"]},
        "neural_simulation_run": False, "physiological_validation": False, "malecns_registered_neurons": 0,
        "parameters": {
            "scene": SCENE_VERSION, "renderer": "world.scene_rgb", "display": "nearest measured ray in forward perspective",
            "display_horizontal_fov_deg": FOV_DEG, "reference_camera_horizontal_fov_deg": FOV_DEG,
            "display_interpolation_cutoff_deg": DISPLAY_CUTOFF_DEG,
            "binocular_display": "nearest ray from union of both eyes; no physiological binocular fusion",
            "optical_acceptance_blur": "NONE; ideal directional samples",
            "radiance": "authored RGB display intensities; not spectral radiance or fly receptor responses",
            "eye_origin": "co-located point", "scene_units": "authored arbitrary units; not calibrated biomechanics",
            "manual_movement": "manual observer translation with authored fruit clearance; no neural motor or body physics model",
            "time": "elapsed simulation seconds", "headless_fixed_dt_seconds": 1 / 30 if headless else None,
            "retinal_muscle_motion": "not modeled", "phototransduction": "not modeled",
            "spectral_sensitivity_and_uv": "not modeled", "initial_pose": asdict(pose),
            "headless_trajectory": "forward=.75, turn=.18, dt=1/30" if headless else None,
            "other_flies": ACTOR_VERSION + "; authored paths and observer proximity repulsion, not neural agents",
            "exploration_guide": "human HUD using scene positions; excluded from recorded optical samples and neural inputs",
        },
        "sample_format": {"file": "optical_samples.f32", "dtype": "little-endian float32",
                          "layout": "frame by ray by RGB", "channels": ["R", "G", "B"],
                          "ray_count": len(rays), "ray_order": "reference_rays.csv order"},
    }
    write_json(output / "manifest.json", manifest)

    def label(text, xy, size=22, color=(235, 242, 230)):
        screen.blit(fonts[size].render(text, True, color), xy)

    def draw_rgb(rgb, rect):
        pixels = np.clip(np.round(rgb * 255), 0, 255).astype(np.uint8)
        surface = pygame.surfarray.make_surface(np.transpose(pixels, (1, 0, 2)))
        screen.blit(pygame.transform.scale(surface, rect.size), rect.topleft)

    def grab_mouse(value):
        nonlocal captured
        captured = value and not headless
        pygame.event.set_grab(captured)
        pygame.mouse.set_visible(not captured)
        pygame.mouse.get_rel()

    def buttons(width):
        return [("fly", "1  Fly view", pygame.Rect(width - 524, 16, 132, 34)),
                ("camera", "2  Camera", pygame.Rect(width - 382, 16, 124, 34)),
                ("help", "H  Controls", pygame.Rect(width - 248, 16, 112, 34)),
                ("science", "I  About", pygame.Rect(width - 126, 16, 102, 34))]

    def activate(action):
        nonlocal view, panel
        if action in {"fly", "camera"}:
            view, panel = action, None
        else:
            panel = None if panel == action else action
            grab_mouse(False)

    try:
        while running and (frames is None or frame_index < frames):
            dt = 1 / 30 if headless else min(clock.tick(30) / 1000, .05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((max(900, event.w), max(600, event.h)), pygame.RESIZABLE)
                elif event.type == pygame.WINDOWFOCUSLOST:
                    grab_mouse(False)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if panel:
                            panel = None
                        elif captured:
                            grab_mouse(False)
                        else:
                            running = False
                    elif event.key in (pygame.K_1, pygame.K_2):
                        activate("fly" if event.key == pygame.K_1 else "camera")
                    elif event.key == pygame.K_TAB:
                        activate("camera" if view == "fly" else "fly")
                    elif event.key == pygame.K_h:
                        activate("help")
                    elif event.key == pygame.K_i:
                        activate("science")
                    elif event.key == pygame.K_p:
                        paused = not paused
                    elif event.key == pygame.K_g:
                        guidance = not guidance
                    elif event.key == pygame.K_r:
                        pose = initial_pose()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not captured:
                    clicked = next((name for name, _, rect in buttons(screen.get_width()) if rect.collidepoint(event.pos)), None)
                    if clicked:
                        activate(clicked)
                    elif panel:
                        panel = None
                    elif 64 <= event.pos[1] < screen.get_height() - 70:
                        grab_mouse(True)
                elif event.type == pygame.MOUSEMOTION and captured and not paused and not panel:
                    look_observer(pose, *event.rel)
            if not running:
                break
            if not paused:
                if headless:
                    move_observer(pose, forward=.75, turn=.18, dt=dt)
                elif not panel and pygame.key.get_focused():
                    keys = pygame.key.get_pressed()
                    move_observer(pose,
                                  forward=int(keys[pygame.K_w]) - int(keys[pygame.K_s]),
                                  left=int(keys[pygame.K_a] or keys[pygame.K_q]) - int(keys[pygame.K_d] or keys[pygame.K_e]),
                                  turn=int(keys[pygame.K_LEFT]) - int(keys[pygame.K_RIGHT]),
                                  look_up=int(keys[pygame.K_UP]) - int(keys[pygame.K_DOWN]),
                                  rise=int(keys[pygame.K_SPACE]) - int(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]), dt=dt)
                avoid_fruit(pose)
                elapsed += dt
                exploration.update(pose, elapsed, dt)
            width, height = screen.get_size()
            viewport = pygame.Rect(0, 64, width, height - 134)
            render_width = min(720, width)
            render_height = max(1, round(render_width * viewport.height / width))
            size = (render_width, render_height)
            if size != projection_size:
                projection = perspective_projection(rays, *size)
                camera_size = (360, max(1, round(360 * viewport.height / width)))
                camera_rays = pinhole_rays(*camera_size, FOV_DEG)
                projection_size = size
            values = scene_rgb(rays, pose, elapsed)
            if view == "fly":
                pixels = fly_pixels(values, *projection)
            else:
                pixels = scene_rgb(camera_rays, pose, elapsed).reshape(camera_size[1], camera_size[0], 3)
            screen.fill((19, 29, 26))
            draw_rgb(pixels, viewport)
            label("FLYVISION", (24, 20), 28)
            label("/  THE GARDEN", (157, 24), 20, (144, 167, 151))
            for name, title, rect in buttons(width):
                selected = name == (panel or view)
                pygame.draw.rect(screen, (208, 228, 153) if selected else (39, 53, 46), rect, border_radius=7)
                label(title, (rect.x + 12, rect.y + 9), 20, (27, 43, 27) if selected else (213, 225, 215))
            badge = pygame.Surface((350, 66), pygame.SRCALPHA)
            badge.fill((18, 30, 25, 195))
            screen.blit(badge, (22, 84))
            label("Fly view" if view == "fly" else "Reference camera", (38, 95), 28)
            label("Measured eye sampling  /  illustrative color" if view == "fly" else "Same world, same position, finer detail",
                  (38, 125), 18, (209, 220, 198))
            if paused:
                label("PAUSED  /  P to resume", (width // 2 - 90, 86), 22)
            if captured:
                pygame.draw.circle(screen, (241, 246, 221), viewport.center, 3, 1)
            if guidance and not panel:
                title, hint, target = exploration.objective(pose, elapsed)
                guide = pygame.Surface((410, 92), pygame.SRCALPHA)
                guide.fill((18, 30, 25, 215))
                screen.blit(guide, (width - 432, 84))
                label(title, (width - 414, 96), 28, (224, 237, 175))
                label(hint, (width - 414, 126), 18)
                for i in range(4):
                    pygame.draw.circle(screen, (208, 228, 153) if i < len(exploration.visited) else (88, 109, 81),
                                       (width - 408 + i * 17, 156), 4)
                label(f"{len(exploration.visited)} / 4 discoveries    G hides the guide", (width - 330, 151), 18, (155, 176, 160))
                if target is not None:
                    tx, ty, direction = screen_direction(target, pose, viewport.width, viewport.height, FOV_DEG)
                    tx, ty = round(tx), round(ty + viewport.y)
                    if direction == "ahead":
                        radius = 20 + round(2 * np.sin(elapsed * 3))
                        pygame.draw.circle(screen, (24, 39, 28), (tx, ty), radius + 2, 4)
                        pygame.draw.circle(screen, (240, 233, 148), (tx, ty), radius, 2)
                        text = "Nearby fly" if "nearby" not in exploration.visited else "Explore here"
                        text_y = ty + radius + 10
                    else:
                        vectors = {"left": [(-10, 0), (7, -10), (7, 10)], "right": [(10, 0), (-7, -10), (-7, 10)],
                                   "up": [(0, -10), (-10, 7), (10, 7)], "down": [(0, 10), (-10, -7), (10, -7)]}
                        pygame.draw.polygon(screen, (240, 233, 148), [(tx + dx, ty + dy) for dx, dy in vectors[direction]])
                        text = {"left": "Turn left", "right": "Turn right", "up": "Look up / Space to rise", "down": "Look down / Shift to descend"}[direction]
                        text_y = ty + 18
                    text_width = fonts[20].size(text)[0]
                    text_x = max(14, min(width - text_width - 14, tx - text_width // 2))
                    pygame.draw.rect(screen, (24, 39, 28), (text_x - 7, text_y - 4, text_width + 14, 24), border_radius=5)
                    label(text, (text_x, text_y), 20, (240, 233, 148))
                if elapsed < exploration.message_until:
                    message = exploration.message
                    toast_width = fonts[28].size(message)[0] + 40
                    rect = pygame.Rect((width - toast_width) // 2, viewport.bottom - 66, toast_width, 42)
                    pygame.draw.rect(screen, (208, 228, 153), rect, border_radius=10)
                    label(message, (rect.x + 20, rect.y + 11), 28, (27, 43, 27))
            label("W A S D  move     Mouse / arrows  look     Space / Shift  up / down", (24, height - 54), 22)
            label("Esc  release mouse / quit     Tab  compare     G  guide     R  return     P  pause", (24, height - 28), 18, (155, 176, 160))
            prompt = "Mouse look active" if captured else "Click the world to look around"
            label(prompt, (width - fonts[20].size(prompt)[0] - 24, height - 52), 20, (208, 228, 153))
            status = f"Heading {pose.yaw_deg:+.0f}°   |   Height {pose.z:.1f}"
            label(status, (width - fonts[18].size(status)[0] - 24, height - 27), 18, (155, 176, 160))

            if panel:
                overlay = pygame.Surface((width, height - 134), pygame.SRCALPHA)
                overlay.fill((7, 14, 12, 165))
                screen.blit(overlay, (0, 64))
                card = pygame.Rect((width - 660) // 2, 83, 660, min(550, viewport.height - 38))
                pygame.draw.rect(screen, (25, 39, 32), card, border_radius=14)
                x, y = card.x + 30, card.y + 26
                label("Explore the garden" if panel == "help" else "How this view is made", (x, y), 32)
                if panel == "help":
                    entries = [("W / S", "Move forward / backward"), ("A / D", "Move left / right"),
                               ("Click + mouse", "Look around; Esc releases the pointer"),
                               ("Arrow keys", "Look around without the mouse"),
                               ("Space / Shift", "Fly up / down"), ("Tab or 1 / 2", "Compare eye sampling with a camera"),
                               ("R / P / G", "Return to start / pause / hide the guide")]
                    for j, (key, explanation) in enumerate(entries):
                        label(key, (x, y + 64 + 34 * j), 22, (208, 228, 153))
                        label(explanation, (x + 170, y + 64 + 34 * j), 22)
                else:
                    lines = [f"The view samples the world in {len(rays):,} published eye directions.",
                             "Each visible patch carries one measured-direction sample.",
                             "Both eyes are arranged into one forward view for this display.",
                             "RGB colors are illustrative; fly color sensitivity and UV are absent.",
                             "Eye geometry: female microCT reference. MaleCNS link: unresolved.",
                             f"{registration.get('local_photoreceptor_labelled_neurons', 0):,} local photoreceptor bodies tracked; 0 verified ray bindings.",
                             "Other flies have scripted motion and proximity reactions.",
                             "Guide markers are player aids. Neural dynamics are not running."]
                    for j, line in enumerate(lines):
                        label(line, (x, y + 51 + 26 * j), 20, (204, 217, 205))
                    if card.height >= 480:
                        for eye, px in [("L", x), ("R", x + 310)]:
                            indices, visible = panorama[eye]
                            draw_rgb(fly_pixels(values[eye_rows[eye]], indices, visible), pygame.Rect(px, y + 295, 280, 100))
                            label("Left eye / full panorama" if eye == "L" else "Right eye / full panorama", (px, y + 271), 20)
                        label("Dark areas: outside the 6° display cutoff. This is not optical blur.", (x, y + 411), 18, (155, 176, 160))
                label("Click anywhere in the world or press Esc to return", (x, card.bottom - 37), 20, (208, 228, 153))
            pygame.display.flip()
            values.astype("<f4").tofile(recording)
            poses.write(f"{frame_index},{elapsed:.17g},{pose.x:.17g},{pose.y:.17g},{pose.z:.17g},{pose.yaw_deg:.17g},{pose.pitch_deg:.17g},{int(paused)},{view}\n")
            if frame_index == 0:
                pygame.image.save(screen, output / "first_frame.png")
            last_values = values
            frame_index += 1
        pygame.image.save(screen, output / "last_frame.png")
        write_json(output / "exploration.json", {
            "scope": "AUTHORED_PLAYER_EXPERIENCE; not a biological behavior evaluation",
            "actor_version": ACTOR_VERSION, "discoveries": sorted(exploration.visited),
            "events": exploration.events, "hud_in_optical_samples": False,
        })
        recording.close()
        poses.close()
        manifest.update(status="COMPLETE", frames=frame_index, simulation_elapsed_seconds=elapsed,
                        last_pose=asdict(pose), signal_range_last_frame=[float(last_values.min()), float(last_values.max())])
        manifest["artifacts"] = {p.name: {"sha256": sha256(p), "bytes": p.stat().st_size}
                                 for p in sorted(output.iterdir()) if p.name != "manifest.json"}
        write_json(output / "manifest.json", manifest)
    except Exception as exc:
        manifest.update(status="FAILED", error=str(exc))
        write_json(output / "manifest.json", manifest)
        raise
    finally:
        recording.close()
        poses.close()
        pygame.quit()
    print(f"Recorded {frame_index} RGB optical frames in {output}. Neural simulation: not run.")


def main():
    parser = argparse.ArgumentParser(description="Explore a colored garden through published fly-eye samples")
    parser.add_argument("--geometry", type=Path, default=ROOT / "runs/eye-reference")
    parser.add_argument("--out", type=Path, default=ROOT / "runs" / datetime.now(timezone.utc).strftime("garden-%Y%m%dT%H%M%S-%fZ"))
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--view", choices=["fly", "camera"], default="fly")
    parser.add_argument("--panel", choices=["help", "science"])
    args = parser.parse_args()
    if args.headless and args.frames is None:
        args.frames = 60
    run_viewer(args.geometry.resolve(), args.out.resolve(), args.headless, args.frames, args.view, args.panel)


if __name__ == "__main__":
    main()
