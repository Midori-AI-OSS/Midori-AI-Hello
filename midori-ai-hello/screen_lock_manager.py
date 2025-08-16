"""Manage KDE screen lock state based on presence events."""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Protocol

from .kde_lock import KDEScreenLocker


class PresenceService(Protocol):
    """Minimal protocol for presence detection services."""

    def add_listener(self, callback: Callable[[bool], Awaitable[None] | None]) -> None:
        ...


class NullPresenceService:
    """Presence service that never emits events."""

    def add_listener(self, callback: Callable[[bool], Awaitable[None] | None]) -> None:
        return None


class ScreenLockManager:
    """Subscribe to presence events and control the KDE screen locker."""

    def __init__(
        self,
        locker: KDEScreenLocker,
        presence: PresenceService,
        *,
        absent_timeout: float = 30.0,
        notify: Callable[[str], None] | None = None,
    ) -> None:
        self._locker = locker
        self._presence = presence
        self._absent_timeout = absent_timeout
        self._notify = notify or (lambda msg: None)
        self._lock_task: asyncio.Task[None] | None = None
        self._locked = False

    async def start(self) -> None:
        """Begin listening for presence and lock state changes."""
        await self._locker.add_active_changed_handler(self._on_active_changed)
        self._presence.add_listener(self._on_presence)

    def _on_presence(self, present: bool) -> None:
        if present:
            if self._lock_task:
                self._lock_task.cancel()
                self._lock_task = None
            if self._locked:
                asyncio.create_task(self._locker.set_active(False))
        else:
            if self._lock_task:
                self._lock_task.cancel()
            self._lock_task = asyncio.create_task(self._lock_after_delay())

    async def _lock_after_delay(self) -> None:
        try:
            await asyncio.sleep(self._absent_timeout)
            await self._locker.lock()
        except asyncio.CancelledError:
            pass
        finally:
            self._lock_task = None

    async def _on_active_changed(self, active: bool) -> None:
        self._locked = active
        self._notify("Locked" if active else "Unlocked")
