from pathlib import Path
import logging
import asyncio

import midori_ai_hello.__main__ as cli
from midori_ai_hello.yolo_train import YOLOTrainingScheduler
from midori_ai_hello.screen_lock_manager import ScreenLockManager


def test_logging_file_creation(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cli.configure_logging("INFO")
    logging.getLogger(__name__).debug("debug message")
    log_file = tmp_path / "midori-ai-hello.log"
    assert log_file.exists()
    contents = log_file.read_text()
    assert "debug message" in contents


def test_scheduler_training_logged(tmp_path, caplog):
    async def run() -> bool:
        config_path = tmp_path / "config.yaml"
        dataset = tmp_path / "dataset"
        dataset.mkdir()
        config_path.write_text(
            "dataset: {}\nidle_threshold: 0\nepochs: 1\nbatch: 1\nmodel: model.pt\n".format(
                dataset
            )
        )

        class DummyLocker:
            async def get_idle_time(self) -> int:
                return 10

        scheduler = YOLOTrainingScheduler(DummyLocker(), config_path)
        scheduler._train = lambda: None  # type: ignore
        caplog.set_level(logging.INFO)
        return await scheduler.maybe_train()

    triggered = asyncio.run(run())
    assert triggered
    assert "Starting training run" in caplog.text


def test_screen_lock_manager_logs(caplog):
    async def run() -> None:
        class DummyLocker:
            async def add_active_changed_handler(self, handler):
                self.handler = handler

            async def set_active(self, active: bool) -> None:
                pass

            async def lock(self) -> None:
                pass

        class DummyPresence:
            def add_listener(self, callback):
                self.callback = callback

        locker = DummyLocker()
        presence = DummyPresence()
        mgr = ScreenLockManager(locker, presence, absent_timeout=0.01)
        caplog.set_level(logging.DEBUG)
        await mgr.start()
        presence.callback(False)
        await asyncio.sleep(0.02)

    asyncio.run(run())
    assert "Screen locked due to absence" in caplog.text

