"""Textual screen for capturing images and writing YOLO labels."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable, Tuple

try:  # pragma: no cover - environment dependent
    import cv2  # type: ignore
except Exception:  # pragma: no cover - handled gracefully
    cv2 = None  # type: ignore
import numpy as np
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static


BBox = Tuple[int, int, int, int]


def list_cameras(max_devices: int = 10) -> list[int]:
    """Return indices of available camera devices."""
    cameras: list[int] = []
    if cv2 is None:
        return cameras
    for index in range(max_devices):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            cameras.append(index)
        cap.release()
    return cameras


def _box_to_yolo(box: BBox, width: int, height: int) -> tuple[float, float, float, float]:
    x, y, w, h = box
    x_center = (x + w / 2) / width
    y_center = (y + h / 2) / height
    return x_center, y_center, w / width, h / height


def save_sample(
    image: np.ndarray,
    face_box: BBox,
    body_box: BBox,
    subject: str,
    camera_id: str,
    dataset_path: Path,
) -> tuple[Path, Path]:
    """Save an image and YOLO-format labels under ``dataset_path``."""

    h, w = image.shape[:2]
    image_dir = dataset_path / "images" / camera_id
    label_dir = dataset_path / "labels" / camera_id
    image_dir.mkdir(parents=True, exist_ok=True)
    label_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    image_name = f"{subject}_{timestamp}.jpg"
    image_path = image_dir / image_name
    label_path = label_dir / image_name.replace(".jpg", ".txt")

    cv2.imwrite(str(image_path), image)

    face_line = "0 {} {} {} {}".format(*_box_to_yolo(face_box, w, h))
    body_line = "1 {} {} {} {}".format(*_box_to_yolo(body_box, w, h))
    label_path.write_text(f"{face_line}\n{body_line}\n")
    return image_path, label_path


class CaptureScreen(Screen):
    """Screen for capturing and labeling images."""

    BINDINGS = [
        ("c", "capture", "Capture"),
        ("n", "next_camera", "Next camera"),
    ]

    def __init__(self, dataset_path: Path, cameras: Iterable[int] | None = None) -> None:
        super().__init__()
        self.dataset_path = Path(dataset_path)
        self.cameras = list(cameras) if cameras is not None else [0]
        self._current = 0
        self._cap: cv2.VideoCapture | None = None

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("Press 'c' to capture or 'n' to switch camera")

    def on_mount(self) -> None:  # type: ignore[override]
        if cv2 is not None:
            self._open_camera()

    def _open_camera(self) -> None:
        if cv2 is None or not self.cameras:
            return
        if self._cap:
            self._cap.release()
        self._cap = cv2.VideoCapture(self.cameras[self._current])

    def action_next_camera(self) -> None:
        if not self.cameras:
            return
        self._current = (self._current + 1) % len(self.cameras)
        self._open_camera()

    def action_capture(self) -> None:
        if cv2 is None or not self._cap:
            return
        ok, frame = self._cap.read()
        if not ok:
            return
        face = cv2.selectROI("face", frame, showCrosshair=True)
        body = cv2.selectROI("body", frame, showCrosshair=True)
        cv2.destroyAllWindows()
        name = input("Subject name: ")
        save_sample(frame, face, body, name, str(self.cameras[self._current]), self.dataset_path)
