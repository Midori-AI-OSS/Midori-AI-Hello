"""Manage KDE screen lock state based on presence events."""
from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, Protocol, Tuple

from .kde_lock import KDEScreenLocker


log = logging.getLogger(__name__)


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
        notify: Callable[[Tuple[str, object]], None] | None = None,
    ) -> None:
        self._locker = locker
        self._presence = presence
        self._absent_timeout = absent_timeout
        self._notify = notify or (lambda event: None)
        self._lock_task: asyncio.Task[None] | None = None
        self._locked = False

    async def start(self) -> None:
        """Begin listening for presence and lock state changes."""
        log.debug(
            "Starting ScreenLockManager with absent_timeout=%s", self._absent_timeout
        )
        await self._locker.add_active_changed_handler(self._on_active_changed)
        self._presence.add_listener(self._on_presence)

    def _on_presence(self, present: bool) -> None:
        log.info("Presence %s", "detected" if present else "lost")
        self._notify(("presence", present))
        if present:
            if self._lock_task:
                self._lock_task.cancel()
                self._lock_task = None
            self._notify(("countdown", None))
            if self._locked:
                asyncio.create_task(self._locker.set_active(False))
        else:
            if self._lock_task:
                self._lock_task.cancel()
            self._lock_task = asyncio.create_task(self._lock_after_delay())

    async def _lock_after_delay(self) -> None:
        start = asyncio.get_running_loop().time()
        target = start + self._absent_timeout
        try:
            log.debug(
                "Absent for %s seconds, will lock screen", self._absent_timeout
            )
            while True:
                now = asyncio.get_running_loop().time()
                remaining = max(0.0, target - now)
                if remaining <= 0:
                    break
                self._notify(("countdown", remaining))
                await asyncio.sleep(min(1.0, remaining))
            await self._locker.lock()
            log.info("Screen locked due to absence")
        except asyncio.CancelledError:
            log.debug("Lock delayed cancelled")
        finally:
            self._notify(("countdown", None))
            self._lock_task = None

    async def _on_active_changed(self, active: bool) -> None:
        self._locked = active
        state = "Locked" if active else "Unlocked"
        log.info("Screen %s", state.lower())
        self._notify(("lock", active))
