"""DBus helpers for interacting with KDE's screen locker."""

from __future__ import annotations

import asyncio
import inspect
from typing import Awaitable, Callable

from dbus_next import BusType, Message
from dbus_next.aio import MessageBus
from dbus_next.constants import MessageType

SCREEN_SAVER = "org.freedesktop.ScreenSaver"
PATH = "/org/freedesktop/ScreenSaver"
INTERFACE = "org.freedesktop.ScreenSaver"


class KDEScreenLocker:
    """Client for KDE's :code:`org.freedesktop.ScreenSaver` interface."""

    def __init__(self, bus: MessageBus | None = None) -> None:
        """Optionally provide an existing :class:`MessageBus` instance."""
        self._bus = bus

    async def _ensure_bus(self) -> MessageBus:
        """Connect to the session bus if one was not supplied."""
        if self._bus is None:
            self._bus = await MessageBus(bus_type=BusType.SESSION).connect()
        return self._bus

    async def lock(self) -> None:
        """Trigger the desktop screen locker."""
        bus = await self._ensure_bus()
        msg = Message(
            destination=SCREEN_SAVER,
            path=PATH,
            interface=INTERFACE,
            member="Lock",
        )
        await bus.call(msg)

    async def get_idle_time(self) -> int:
        """Return seconds of session idle time."""
        bus = await self._ensure_bus()
        msg = Message(
            destination=SCREEN_SAVER,
            path=PATH,
            interface=INTERFACE,
            member="GetSessionIdleTime",
        )
        reply = await bus.call(msg)
        return int(reply.body[0])

    async def inhibit(self, reason: str) -> int:
        """Disable automatic screen locking and return an inhibition cookie."""
        bus = await self._ensure_bus()
        msg = Message(
            destination=SCREEN_SAVER,
            path=PATH,
            interface=INTERFACE,
            member="Inhibit",
            signature="ss",
            body=["midori-ai-hello", reason],
        )
        reply = await bus.call(msg)
        return int(reply.body[0])

    async def uninhibit(self, cookie: int) -> None:
        """Re-enable automatic screen locking for a prior inhibition cookie."""
        bus = await self._ensure_bus()
        msg = Message(
            destination=SCREEN_SAVER,
            path=PATH,
            interface=INTERFACE,
            member="UnInhibit",
            signature="u",
            body=[cookie],
        )
        await bus.call(msg)

    async def add_active_changed_handler(
        self, handler: Callable[[bool], Awaitable[None] | None]
    ) -> None:
        """Invoke *handler* whenever the screen lock state changes."""

        def _wrapper(msg: Message) -> bool:
            if (
                msg.message_type is MessageType.SIGNAL
                and msg.interface == INTERFACE
                and msg.member == "ActiveChanged"
            ):
                state = bool(msg.body[0])
                result = handler(state)
                if inspect.isawaitable(result):
                    asyncio.create_task(result)
                return True
            return True

        bus = await self._ensure_bus()
        bus.add_message_handler(_wrapper)
        await bus.call(
            Message(
                destination="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                interface="org.freedesktop.DBus",
                member="AddMatch",
                signature="s",
                body=[
                    f"type='signal',interface='{INTERFACE}',member='ActiveChanged'"
                ],
            )
        )


class PowerInhibitor:
    """Async context manager to inhibit the screensaver."""

    def __init__(self, locker: KDEScreenLocker, reason: str) -> None:
        self._locker = locker
        self._reason = reason
        self._cookie: int | None = None

    async def __aenter__(self) -> int:
        self._cookie = await self._locker.inhibit(self._reason)
        return self._cookie

    async def __aexit__(self, exc_type, exc, tb) -> None:
        assert self._cookie is not None
        await self._locker.uninhibit(self._cookie)
