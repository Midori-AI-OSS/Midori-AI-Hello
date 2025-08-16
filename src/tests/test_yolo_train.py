from __future__ import annotations

import asyncio
from pathlib import Path

from midori_ai_hello.yolo_train import YOLOTrainingScheduler


class FakeLocker:
    def __init__(self, idle: int) -> None:
        self.idle = idle

    async def get_idle_time(self) -> int:  # pragma: no cover - simple stub
        return self.idle


def write_config(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.yaml"
    cfg.write_text(
        """
dataset: dataset
epochs: 1
batch: 1
idle_threshold: 10
model: yolo11n.pt
profile_hash: profile.hash
        """
    )
    (tmp_path / "dataset").mkdir()
    return cfg


def test_dataset_yaml_contains_paths(tmp_path: Path) -> None:
    cfg = write_config(tmp_path)
    sched = YOLOTrainingScheduler(FakeLocker(0), cfg)
    yaml_path = sched._dataset_yaml()
    content = yaml_path.read_text()
    assert "path:" in content and "train:" in content


def test_maybe_train_runs_when_idle(tmp_path: Path) -> None:
    cfg = write_config(tmp_path)
    sched = YOLOTrainingScheduler(FakeLocker(20), cfg)
    called = False

    def fake_train() -> None:
        nonlocal called
        called = True

    sched._train = fake_train  # type: ignore[assignment]
    assert asyncio.run(sched.maybe_train()) is True
    assert called is True


def test_maybe_train_skips_when_active(tmp_path: Path) -> None:
    cfg = write_config(tmp_path)
    sched = YOLOTrainingScheduler(FakeLocker(5), cfg)
    called = False

    def fake_train() -> None:
        nonlocal called
        called = True

    sched._train = fake_train  # type: ignore[assignment]
    assert asyncio.run(sched.maybe_train()) is False
    assert called is False
