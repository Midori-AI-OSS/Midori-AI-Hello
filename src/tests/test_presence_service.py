import asyncio
from typing import List

from midori_ai_hello.presence_service import CameraPresenceService


class DummyWhitelist:
    def users(self) -> List[str]:
        return ["alice"]


def test_presence_service_emits_events(monkeypatch):
    async def run() -> list[bool]:
        events: list[bool] = []
        service = CameraPresenceService(
            cameras=["0"],
            model_path="model.pt",
            whitelist=DummyWhitelist(),
            present_interval=0.01,
            absent_interval=0.01,
        )

        class DummyModel:
            def to(self, device):  # pragma: no cover - simple stub
                return self

        monkeypatch.setattr(
            "midori_ai_hello.presence_service.YOLO", lambda path: DummyModel()
        )

        results = iter([False, True, False])

        def fake_scan(model):
            return next(results, False)

        monkeypatch.setattr(service, "_scan_once", fake_scan)

        service.add_listener(events.append)
        await asyncio.sleep(0.05)
        await service.stop()
        return events

    events = asyncio.run(run())
    assert events == [True, False]
