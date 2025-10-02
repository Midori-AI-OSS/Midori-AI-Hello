import asyncio
from typing import Any, Callable

from midori_ai_hello.screen_lock_manager import ScreenLockManager


class FakeLocker:
    def __init__(self) -> None:
        self.events: list[str] = []
        self._handler: Callable[[bool], None] | None = None

    async def add_active_changed_handler(self, handler: Callable[[bool], None]) -> None:
        self._handler = handler

    async def lock(self) -> None:
        self.events.append("lock")
        if self._handler:
            await asyncio.create_task(self._handler(True))

    async def set_active(self, active: bool) -> None:
        self.events.append(f"set_active:{active}")
        if self._handler:
            await asyncio.create_task(self._handler(active))


class FakePresence:
    def __init__(self) -> None:
        self._listeners: list[Callable[[bool], None]] = []

    def add_listener(self, cb: Callable[[bool], None]) -> None:
        self._listeners.append(cb)

    def emit(self, present: bool) -> None:
        for cb in list(self._listeners):
            result = cb(present)
            if asyncio.iscoroutine(result):
                asyncio.create_task(result)


def test_lock_and_unlock() -> None:
    messages: list[tuple[str, Any]] = []
    locker = FakeLocker()
    presence = FakePresence()

    async def run() -> None:
        mgr = ScreenLockManager(
            locker, presence, absent_timeout=0.01, notify=messages.append
        )
        await mgr.start()
        presence.emit(False)
        await asyncio.sleep(0.02)
        presence.emit(True)
        await asyncio.sleep(0.01)

    asyncio.run(run())
    assert "lock" in locker.events
    assert "set_active:False" in locker.events
    assert ("presence", False) in messages
    assert any(kind == "countdown" and value is None for kind, value in messages)
    assert messages[-1] == ("lock", False)


def test_presence_cancels_lock() -> None:
    locker = FakeLocker()
    presence = FakePresence()

    async def run() -> None:
        mgr = ScreenLockManager(locker, presence, absent_timeout=0.05)
        await mgr.start()
        presence.emit(False)
        await asyncio.sleep(0.02)
        presence.emit(True)
        await asyncio.sleep(0.05)

    asyncio.run(run())
    assert locker.events == []
