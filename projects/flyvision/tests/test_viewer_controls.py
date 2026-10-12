"""SDL event-loop checks. These do not assert a real macOS mouse capture works."""
import json

import numpy as np
import pandas as pd
import pytest


def test_movement_mouse_pause_compare_resize_reset_and_focus_loss(tmp_path, monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("PYGAME_HIDE_SUPPORT_PROMPT", "1")
    pygame = pytest.importorskip("pygame")
    from flyvision import viewer
    from flyvision.optics import pinhole_rays
    from flyvision.world import initial_pose
    rays = pinhole_rays(21, 13)
    frame = pd.DataFrame(rays, columns=["forward", "left", "up"])
    frame["eye"] = np.where(np.arange(len(frame)) % 2, "L", "R")
    geometry = tmp_path / "geometry"
    geometry.mkdir()
    (geometry / "registration_audit.json").write_text("{}")
    (geometry / "manifest.json").write_text("{}")
    monkeypatch.setattr(viewer, "load_reference", lambda _: (frame, {"reference_commit": "test-fixture"}))
    class Clock:
        def tick(self, _): return 33
    monkeypatch.setattr(pygame.time, "Clock", Clock)
    monkeypatch.setattr(pygame.key, "get_focused", lambda: True)
    steps = iter([
        ([pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(500, 300)),
          pygame.event.Event(pygame.MOUSEMOTION, rel=(20, -10))], {pygame.K_w, pygame.K_SPACE}),
        ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB),
          pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p)], set()),
        ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB)], set()),
        ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_p),
          pygame.event.Event(pygame.WINDOWFOCUSLOST)], set()),
        ([pygame.event.Event(pygame.VIDEORESIZE, w=900, h=600),
          pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h)], {pygame.K_w}),
        ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_i)], set()),
        ([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE),
          pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)], set()),
    ])
    active_keys = set()
    def events():
        nonlocal active_keys
        batch, active_keys = next(steps)
        return batch
    class Keys:
        def __getitem__(self, key): return key in active_keys
    monkeypatch.setattr(pygame.event, "get", events)
    monkeypatch.setattr(pygame.key, "get_pressed", Keys)
    mouse_states = []
    monkeypatch.setattr(pygame.event, "set_grab", mouse_states.append)
    # Keep the display ungrabbed under SDL dummy while checking event logic.
    monkeypatch.setattr(pygame.mouse, "set_visible", lambda _: None)
    out = tmp_path / "run"
    viewer.run_viewer(geometry, out, frames=7)
    trajectory = pd.read_csv(out / "trajectory.csv")
    first = trajectory.iloc[0]
    assert first.x_scene > initial_pose().x and first.z_scene > initial_pose().z
    assert first.yaw_deg < 0 and first.pitch_deg > initial_pose().pitch_deg
    assert trajectory.iloc[1].view == "camera" and trajectory.iloc[2].view == "fly"
    assert trajectory.iloc[0].time_s == trajectory.iloc[2].time_s
    samples = np.fromfile(out / "optical_samples.f32", dtype="<f4").reshape(7, len(rays), 3)
    assert np.array_equal(samples[0], samples[1]) and np.array_equal(samples[1], samples[2])
    assert trajectory.iloc[4].x_scene == first.x_scene  # help blocks held movement keys
    assert trajectory.iloc[-1].x_scene == initial_pose().x
    assert mouse_states[:2] == [True, False]
    receipt = json.loads((out / "manifest.json").read_text())
    assert receipt["status"] == "COMPLETE" and receipt["frames"] == 7
    assert receipt["sample_format"]["layout"] == "frame by ray by RGB"
