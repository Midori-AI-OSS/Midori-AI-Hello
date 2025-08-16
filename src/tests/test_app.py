from pathlib import Path
import asyncio

from midori_ai_hello.app import MidoriApp
from midori_ai_hello.config import Config


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
