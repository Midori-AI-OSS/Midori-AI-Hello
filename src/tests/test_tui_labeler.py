from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from midori_ai_hello.capture_screen import CaptureScreen, cv2, list_cameras, save_sample


@pytest.mark.skipif(cv2 is None, reason="opencv not available")
def test_list_cameras_mocks_video_capture(monkeypatch):
    opened = {0: True, 1: False, 2: True}

    class DummyCap:
        def __init__(self, index: int) -> None:
            self.index = index

        def isOpened(self) -> bool:  # noqa: N802
            return opened.get(self.index, False)

        def release(self) -> None:
            pass

    monkeypatch.setattr("cv2.VideoCapture", DummyCap)
    cams = list_cameras(max_devices=3)
    assert cams == [0, 2]


@pytest.mark.skipif(cv2 is None, reason="opencv not available")
def test_save_sample_writes_image_and_label(tmp_path: Path):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    face = (10, 10, 20, 20)
    body = (0, 0, 100, 100)
    image_path, label_path = save_sample(img, face, body, "alice", "0", tmp_path)
    assert image_path.exists()
    assert label_path.exists()
    lines = label_path.read_text().strip().splitlines()
    assert lines[0].startswith("0 ")
    assert lines[1].startswith("1 ")


def test_capture_screen_handles_empty_camera_list(tmp_path: Path):
    screen = CaptureScreen(tmp_path, cameras=[])
    screen._open_camera()
    assert screen._cap is None
