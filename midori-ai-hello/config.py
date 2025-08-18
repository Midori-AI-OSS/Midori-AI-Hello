"""YAML-backed configuration management."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


@dataclass
class Config:
    """Application configuration stored in ``config.yaml``."""

    dataset: str
    epochs: int
    batch: int
    idle_threshold: int
    model: str
    device: str = "cpu"
    model_size: str = "n"
    backend: str = "ultralytics"
    cameras: List[str] = field(default_factory=list)
    profile_hash: str | None = None

    @classmethod
    def load(cls, path: Path) -> "Config":
        data = {}
        if path.exists():
            data = yaml.safe_load(path.read_text()) or {}
        model_size = str(data.get("model_size", "n"))
        model = str(data.get("model", f"yolo11{model_size}.pt"))
        return cls(
            dataset=str(data.get("dataset", "dataset")),
            epochs=int(data.get("epochs", 1)),
            batch=int(data.get("batch", 1)),
            idle_threshold=int(data.get("idle_threshold", 0)),
            model=model,
            device=str(data.get("device", "cpu")),
            model_size=model_size,
            backend=str(data.get("backend", "ultralytics")),
            cameras=[str(c) for c in data.get("cameras", [])][:20],
            profile_hash=data.get("profile_hash"),
        )

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "dataset": self.dataset,
            "epochs": self.epochs,
            "batch": self.batch,
            "idle_threshold": self.idle_threshold,
            "model": self.model,
            "device": self.device,
            "model_size": self.model_size,
            "backend": self.backend,
            "cameras": self.cameras[:20],
        }
        if self.profile_hash:
            data["profile_hash"] = self.profile_hash
        path.write_text(yaml.safe_dump(data))
        self._ensure_camera_dirs()

    def update(self, path: Path, **kwargs: object) -> "Config":
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if "cameras" in kwargs:
            self.cameras = [str(c) for c in self.cameras][:20]
        if "model_size" in kwargs and "model" not in kwargs:
            self.model = f"yolo11{self.model_size}.pt"
        self.save(path)
        return self

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_camera_dirs(self) -> None:
        root = Path(self.dataset)
        for cam in self.cameras[:20]:
            (root / "images" / cam).mkdir(parents=True, exist_ok=True)
            (root / "labels" / cam).mkdir(parents=True, exist_ok=True)


def load_config(path: str | Path) -> Config:
    """Load configuration from ``path``."""

    return Config.load(Path(path))


def save_config(config: Config, path: str | Path) -> None:
    """Save ``config`` to ``path``."""

    config.save(Path(path))


def update_config(path: str | Path, **kwargs: object) -> Config:
    """Update specific fields in the config file at ``path``."""

    cfg = load_config(path)
    return cfg.update(Path(path), **kwargs)

