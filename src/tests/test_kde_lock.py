import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from dbus_next import Message
from dbus_next.constants import MessageType

from midori_ai_hello.kde_lock import (
    PATH,
    INTERFACE,
    KDEScreenLocker,
    PowerInhibitor,
)


def test_lock_invokes_dbus():
    bus = SimpleNamespace(call=AsyncMock())
    locker = KDEScreenLocker(bus)  # use provided mock bus
    asyncio.run(locker.lock())
    bus.call.assert_awaited_once()


def test_get_idle_time_returns_int():
    class Reply:
        body = [42]

    bus = SimpleNamespace(call=AsyncMock(return_value=Reply()))
    locker = KDEScreenLocker(bus)
    idle = asyncio.run(locker.get_idle_time())
    assert idle == 42


def test_power_inhibitor_context():
    bus = SimpleNamespace(call=AsyncMock(return_value=SimpleNamespace(body=[1])))
    locker = KDEScreenLocker(bus)

    async def run():
        async with PowerInhibitor(locker, "reason"):
            pass

    asyncio.run(run())
    assert bus.call.await_count == 2


def test_active_changed_handler_invoked():
    class Bus:
        def __init__(self):
            self.call = AsyncMock()
            self._handler = None

        def add_message_handler(self, cb):
            self._handler = cb

    bus = Bus()
    locker = KDEScreenLocker(bus)
    events: list[bool] = []

    asyncio.run(locker.add_active_changed_handler(events.append))

    msg = Message(
        path=PATH,
        interface=INTERFACE,
        member="ActiveChanged",
        message_type=MessageType.SIGNAL,
        body=[True],
    )
    bus._handler(msg)

    assert events == [True]


def test_active_changed_handler_async_invoked():
    class Bus:
        def __init__(self):
            self.call = AsyncMock()
            self._handler = None

        def add_message_handler(self, cb):
            self._handler = cb

    events: list[bool] = []

    async def run():
        bus = Bus()
        locker = KDEScreenLocker(bus)

        async def handler(state: bool) -> None:
            events.append(state)

        await locker.add_active_changed_handler(handler)
        msg = Message(
            path=PATH,
            interface=INTERFACE,
            member="ActiveChanged",
            message_type=MessageType.SIGNAL,
            body=[True],
        )
        bus._handler(msg)
        await asyncio.sleep(0)

    asyncio.run(run())
    assert events == [True]
