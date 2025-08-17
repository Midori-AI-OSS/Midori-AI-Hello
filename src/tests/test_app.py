from pathlib import Path
import asyncio

from midori_ai_hello.app import MidoriApp
from midori_ai_hello.config import Config
from midori_ai_hello.capture_screen import CaptureScreen


class DummyScheduler:
    def __init__(self) -> None:
        self.calls: list[bool] = []

    async def maybe_train(self, force: bool = False) -> bool:
        self.calls.append(force)
        return True

def test_manual_retrain(tmp_path: Path) -> None:
    cfg = Config(
        dataset=str(tmp_path / "data"),
        epochs=1,
        batch=1,
        idle_threshold=0,
        model="yolo.pt",
    )
    cfg.save(tmp_path / "config.yaml")
    scheduler = DummyScheduler()
    app = MidoriApp(tmp_path / "config.yaml", scheduler=scheduler)
    asyncio.run(app.action_retrain())
    assert scheduler.calls == [True]


def test_quit_cancels_background_tasks(tmp_path: Path) -> None:
    cfg = Config(
        dataset=str(tmp_path / "data"),
        epochs=1,
        batch=1,
        idle_threshold=0,
        model="yolo.pt",
    )
    cfg.save(tmp_path / "config.yaml")
    scheduler = DummyScheduler()

    class DummyLocker:
        async def add_active_changed_handler(self, handler):
            self.handler = handler

    app = MidoriApp(
        tmp_path / "config.yaml", scheduler=scheduler, locker=DummyLocker()
    )

    async def run() -> None:
        app.on_mount()
        await asyncio.sleep(0)
        assert app._lock_task is not None
        assert app._train_task is not None
        app.action_quit()
        await asyncio.sleep(0)

    asyncio.run(run())
    assert app._lock_task is not None and app._lock_task.done()
    assert app._train_task is not None and app._train_task.cancelled()


def test_app_detects_cameras_when_config_empty(
    monkeypatch, tmp_path: Path
) -> None:
    cfg = Config(
        dataset=str(tmp_path / "data"),
        epochs=1,
        batch=1,
        idle_threshold=0,
        model="yolo.pt",
        cameras=[],
    )
    cfg.save(tmp_path / "config.yaml")
    monkeypatch.setattr("midori_ai_hello.app.list_cameras", lambda: [42])
    scheduler = DummyScheduler()

    class DummyLocker:
        async def add_active_changed_handler(self, handler):
            self.handler = handler

    app = MidoriApp(
        tmp_path / "config.yaml", scheduler=scheduler, locker=DummyLocker()
    )

    async def run() -> None:
        app.on_mount()
        await asyncio.sleep(0)
        screen = app.get_screen("capture")
        assert isinstance(screen, CaptureScreen)
        assert screen.cameras == [42]
        app.action_quit()
        await asyncio.sleep(0)

    asyncio.run(run())
