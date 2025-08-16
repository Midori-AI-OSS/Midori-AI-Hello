"""Multi-camera presence detection using YOLO models."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Awaitable, Callable, List

try:  # pragma: no cover - optional dependency
    from ultralytics import YOLO  # type: ignore
except Exception:  # pragma: no cover - handled gracefully
    YOLO = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import cv2  # type: ignore
except Exception:  # pragma: no cover - handled gracefully
    cv2 = None  # type: ignore

from .whitelist import WhitelistManager

Listener = Callable[[bool], Awaitable[None] | None]


class CameraPresenceService:
    """Detect authorised user presence across multiple cameras."""

    def __init__(
        self,
        cameras: List[str],
        model_path: str | Path,
        whitelist: WhitelistManager,
        *,
        present_interval: float = 10.0,
        absent_interval: float = 5.0,
    ) -> None:
        self._cameras = cameras
        self._model_path = str(model_path)
        self._whitelist = whitelist
        self._listeners: list[Listener] = []
        self._task: asyncio.Task[None] | None = None
        self._present = False
        self._present_interval = present_interval
        self._absent_interval = absent_interval

    def add_listener(self, callback: Listener) -> None:
        """Register *callback* for presence changes."""

        self._listeners.append(callback)
        if self._task is None:
            self._task = asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        """Stop background polling."""

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:  # pragma: no cover - normal shutdown
                pass
            self._task = None

    async def _poll_loop(self) -> None:
        """Periodically scan cameras for authorised users."""

        if YOLO is None:  # pragma: no cover - dependency missing
            return
        model = YOLO(self._model_path)
        try:
            while True:
                present = await asyncio.to_thread(self._scan_once, model)
                if present != self._present:
                    self._present = present
                    for cb in list(self._listeners):
                        result = cb(present)
                        if asyncio.iscoroutine(result):
                            await result
                await asyncio.sleep(
                    self._present_interval if present else self._absent_interval
                )
        except asyncio.CancelledError:  # pragma: no cover - normal shutdown
            pass

    def _scan_once(self, model: YOLO) -> bool:  # pragma: no cover - I/O heavy
        """Return ``True`` if an authorised user is detected."""

        if cv2 is None:
            return False
        authorised = set(self._whitelist.users())
        for cam in self._cameras:
            cap = cv2.VideoCapture(cam)
            if not cap.isOpened():
                continue
            ret, frame = cap.read()
            cap.release()
            if not ret:
                continue
            results = model(frame)
            for r in results:
                names = getattr(r, "names", {})
                boxes = getattr(getattr(r, "boxes", None), "cls", [])
                for cls in boxes:
                    name = names.get(int(cls), str(cls))
                    if name in authorised:
                        return True
        return False
