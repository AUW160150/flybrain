import hashlib
import json

import pandas as pd
import pytest

from flyvision.eye_reference import verify_reference


def test_changed_reference_is_rejected(tmp_path):
    data = b"pinned geometry bytes"
    (tmp_path / "rays.data").write_bytes(data)
    digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    lock = {"files": [{"path": "rays.data", "bytes": len(data), "git_blob_sha1": digest}]}
    assert verify_reference(tmp_path, lock)["rays.data"]["sha256"] == hashlib.sha256(data).hexdigest()
    (tmp_path / "rays.data").write_bytes(b"modified geometry!!!")
    with pytest.raises(ValueError, match="Pinned reference differs"):
        verify_reference(tmp_path, lock)


def test_display_failure_is_recorded_without_simulation(tmp_path, monkeypatch):
    pygame = pytest.importorskip("pygame")
    from flyvision import viewer
    frame = pd.DataFrame({"forward": [1., 1.], "left": [0., 0.], "up": [0., 0.], "eye": ["L", "R"]})
    geometry = tmp_path / "geometry"
    geometry.mkdir()
    (geometry / "registration_audit.json").write_text("{}")
    monkeypatch.setattr(viewer, "load_reference", lambda path: (frame, {}))
    def fail_display():
        raise pygame.error("test display unavailable")
    monkeypatch.setattr(pygame.display, "init", fail_display)
    out = tmp_path / "failed-run"
    with pytest.raises(RuntimeError, match="No desktop display"):
        viewer.run_viewer(geometry, out, frames=1)
    receipt = json.loads((out / "manifest.json").read_text())
    assert receipt["status"] == "FAILED"
    assert receipt["stage"] == "DISPLAY_INITIALIZATION"
    assert not (out / "optical_samples.f32").exists()
