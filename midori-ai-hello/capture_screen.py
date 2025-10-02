"""Textual screen for capturing images and writing YOLO labels."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, Tuple

try:  # pragma: no cover - environment dependent
    import cv2  # type: ignore
except Exception:  # pragma: no cover - handled gracefully
    cv2 = None  # type: ignore
try:  # pragma: no cover - environment dependent
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover - handled gracefully
    YOLO = None  # type: ignore
import numpy as np
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Static


log = logging.getLogger(__name__)


BBox = Tuple[int, int, int, int]


def list_cameras(max_devices: int = 10) -> list[int]:
    """Return indices of available camera devices."""
    cameras: list[int] = []
    if cv2 is None:
        log.warning("OpenCV not available; no cameras will be detected")
        return cameras
    log.debug("Scanning for cameras up to index %d", max_devices)
    for index in range(max_devices):
        log.debug("Checking camera index %d", index)
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            log.info("Camera %d is available", index)
            cameras.append(index)
        cap.release()
    if not cameras:
        log.warning("No cameras detected")
    else:
        log.debug("Detected cameras: %s", cameras)
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
    log.info("Saved sample image %s and labels %s", image_path, label_path)
    return image_path, label_path


class ConfirmCaptureModal(ModalScreen[bool]):
    """Simple confirmation modal returning ``True`` for yes choices."""

    def __init__(
        self,
        message: str,
        *,
        confirm_label: str = "Yes",
        cancel_label: str = "No",
    ) -> None:
        super().__init__()
        self._message = message
        self._confirm_label = confirm_label
        self._cancel_label = cancel_label

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Vertical(
            Static(self._message, id="confirm-message"),
            Horizontal(
                Button(self._confirm_label, id="confirm", variant="success"),
                Button(self._cancel_label, id="cancel", variant="primary"),
                id="confirm-buttons",
            ),
            id="confirm-container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm")


class CaptureScreen(Screen):
    """Screen for capturing and labeling images."""

    BINDINGS = [
        ("c", "capture", "Capture"),
        ("n", "next_camera", "Next camera"),
        ("escape", "menu", "Back to menu"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        dataset_path: Path,
        cameras: Iterable[int | str] | None = None,
        model_path: str | Path | None = None,
        *,
        device: str = "cpu",
    ) -> None:
        super().__init__()
        self.dataset_path = Path(dataset_path)
        raw = list(cameras) if cameras is not None else [0]
        self.cameras = [
            int(c) if isinstance(c, str) and c.isdigit() else c for c in raw
        ]
        self._current = 0
        self._cap: cv2.VideoCapture | None = None
        self.model_path = Path(model_path) if model_path else None
        self._model: YOLO | None = None
        self._device = device

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("Press 'c' to capture or 'n' to switch camera")

    def on_mount(self) -> None:  # type: ignore[override]
        if cv2 is not None:
            self._open_camera()
        if self.model_path and YOLO is not None:
            try:
                self._model = YOLO(str(self.model_path)).to(self._device)
                log.info(
                    "Loaded YOLO model %s on %s", self.model_path, self._device
                )
            except Exception:  # pragma: no cover - handled gracefully
                log.warning("Failed to load YOLO model %s", self.model_path)
                self._model = None

    def _open_camera(self) -> None:
        if cv2 is None:
            log.warning("OpenCV not available; cannot open cameras")
            return
        if not self.cameras:
            log.warning("No cameras configured")
            return
        if self._cap:
            self._cap.release()
        index = self.cameras[self._current]
        log.info("Opening camera index %s", index)
        cap = cv2.VideoCapture(index)
        if not cap or not cap.isOpened():
            log.warning("Failed to open camera index %s", index)
            self._cap = None
            return
        self._cap = cap

    def action_next_camera(self) -> None:
        if not self.cameras:
            return
        self._current = (self._current + 1) % len(self.cameras)
        self._open_camera()

    def action_menu(self) -> None:  # pragma: no cover - trivial
        if self._cap:
            self._cap.release()
            self._cap = None
        self.app.switch_screen("menu")

    def on_show(self) -> None:  # type: ignore[override]
        if cv2 is not None and self._cap is None:
            self._open_camera()

    async def action_capture(self) -> None:
        if cv2 is None:
            return
        if self._cap is None:
            self._open_camera()
        if not self._cap:
            return

        capturing = True
        while capturing and self._cap:
            camera_id = str(self.cameras[self._current])
            log.debug("Capturing frame from camera index %s", camera_id)
            try:
                self.app.status = f"Capturing from camera {camera_id}"
            except Exception:
                pass
            ok, frame = self._cap.read()
            if not ok:
                log.warning("Failed to read frame from camera %s", camera_id)
                try:
                    self.app.status = "Capture failed"
                except Exception:
                    pass
                break

            face: BBox | None = None
            body: BBox | None = None
            auto_detected = False
            if self._model is not None:
                try:
                    result = self._model(frame, verbose=False)[0]
                    for x1, y1, x2, y2, _, cls_id in result.boxes.data.tolist():
                        box = (int(x1), int(y1), int(x2 - x1), int(y2 - y1))
                        if int(cls_id) == 0 and face is None:
                            face = box
                        elif int(cls_id) == 1 and body is None:
                            body = box
                    auto_detected = face is not None and body is not None
                except Exception:  # pragma: no cover - handled gracefully
                    log.warning("YOLO detection failed", exc_info=True)

            if face and body:
                preview = frame.copy()
                cv2.rectangle(
                    preview,
                    (face[0], face[1]),
                    (face[0] + face[2], face[1] + face[3]),
                    (0, 255, 0),
                    2,
                )
                cv2.rectangle(
                    preview,
                    (body[0], body[1]),
                    (body[0] + body[2], body[1] + body[3]),
                    (255, 0, 0),
                    2,
                )
                cv2.imshow("Detections", preview)
                cv2.waitKey(1)
                use_auto = await self._confirm(
                    "Use auto-detected bounding boxes?",
                    confirm_label="Use auto",
                    cancel_label="Manual ROI",
                )
                cv2.destroyAllWindows()
                if not use_auto:
                    auto_detected = False
                    face, body = self._manual_select(frame)
                else:
                    auto_detected = True
            else:
                auto_detected = False
                face, body = self._manual_select(frame)

            if face is None or body is None:
                try:
                    self.app.status = "Capture cancelled"
                except Exception:
                    pass
                retry = await self._confirm("Retry capture?", confirm_label="Retry")
                if not retry:
                    break
                continue

            name = await asyncio.to_thread(input, "Subject name: ")
            try:
                self.app.status = "Saving sample..."
            except Exception:
                pass
            save_sample(
                frame,
                face,
                body,
                name,
                camera_id,
                self.dataset_path,
            )
            try:
                self.app.record_capture_event(auto_detected, datetime.now())
            except Exception:
                pass
            try:
                self.app.status = "Sample saved"
            except Exception:
                pass

            capturing = await self._confirm(
                "Capture another photo?",
                confirm_label="Capture",
                cancel_label="Done",
            )

        if self._cap:
            self._cap.release()
            self._cap = None
        try:
            self.app.status = ""
        except Exception:
            pass
        self.app.switch_screen("menu")

    async def _confirm(
        self,
        message: str,
        *,
        confirm_label: str = "Yes",
        cancel_label: str = "No",
    ) -> bool:
        result = await self.app.push_screen_wait(
            ConfirmCaptureModal(
                message,
                confirm_label=confirm_label,
                cancel_label=cancel_label,
            )
        )
        return bool(result)

    def _manual_select(self, frame: np.ndarray) -> tuple[BBox | None, BBox | None]:
        if cv2 is None:
            return None, None
        face = self._select_box("face", frame)
        body = self._select_box("body", frame)
        cv2.destroyAllWindows()
        return face, body

    def _select_box(self, window: str, frame: np.ndarray) -> BBox | None:
        if cv2 is None:
            return None
        box = cv2.selectROI(window, frame, showCrosshair=True)
        if not isinstance(box, tuple) or len(box) != 4:
            return None
        x, y, w, h = map(int, box)
        if w <= 0 or h <= 0:
            return None
        return x, y, w, h
