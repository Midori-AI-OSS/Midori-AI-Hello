"""Utilities for scheduling YOLO training runs."""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict

import tomllib

from .kde_lock import KDEScreenLocker


class YOLOTrainingScheduler:
    """Train Ultralytics YOLO models when the session is idle."""

    def __init__(self, locker: KDEScreenLocker, config_path: str | Path) -> None:
        self._locker = locker
        self._config_path = Path(config_path)
        with open(self._config_path, "rb") as f:
            self._config: Dict[str, Any] = tomllib.load(f)

    async def maybe_train(self, force: bool = False) -> bool:
        """Run training if idle exceeds the configured threshold or *force*.

        Returns ``True`` if training was triggered.
        """

        idle_time = await self._locker.get_idle_time()
        threshold = int(self._config.get("idle_threshold", 0))
        if force or idle_time >= threshold:
            await asyncio.to_thread(self._train)
            return True
        return False

    def _dataset_yaml(self) -> Path:
        dataset_root = Path(self._config["dataset"])
        yaml_content = (
            "path: " + str(dataset_root) + "\n" "train: images\nval: images\n" "names: [face, body]\n"
        )
        tmp = NamedTemporaryFile("w", suffix=".yaml", delete=False)
        tmp.write(yaml_content)
        tmp.flush()
        return Path(tmp.name)

    def _update_profile_hash(self, weights: Path) -> None:
        hash_path = self._config.get("profile_hash")
        if not hash_path:
            return
        digest = hashlib.sha256(weights.read_bytes()).hexdigest()
        Path(hash_path).write_text(digest)

    def _mark_epoch(self, epoch: int) -> None:
        dataset_root = Path(self._config["dataset"])
        meta_path = dataset_root / "metadata.json"
        data: Dict[str, Any] = {}
        if meta_path.exists():
            data = json.loads(meta_path.read_text())
        data["last_trained_epoch"] = epoch
        meta_path.write_text(json.dumps(data))

    def _train(self) -> None:
        dataset_yaml = self._dataset_yaml()
        epochs = int(self._config.get("epochs", 1))
        batch = int(self._config.get("batch", 1))
        model_path = self._config.get("model", "yolo11n.pt")
        backend = self._config.get("backend", "ultralytics")
        if backend == "yolov9":
            import subprocess

            cmd = [
                "python",
                "train.py",
                "--device",
                "cpu",
                "--data",
                str(dataset_yaml),
                "--epochs",
                str(epochs),
                "--batch",
                str(batch),
            ]
            subprocess.run(cmd, check=False, cwd=self._config.get("yolov9_path", "."))
        else:
            from ultralytics import YOLO  # type: ignore

            model = YOLO(model_path)
            result = model.train(
                data=str(dataset_yaml), epochs=epochs, batch=batch, device="cpu"
            )
            weights = Path(result.save_dir) / "weights" / "last.pt"
            if weights.exists():
                self._update_profile_hash(weights)
                self._mark_epoch(epochs)
