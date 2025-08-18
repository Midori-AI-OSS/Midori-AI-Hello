"""Main Textual application with multiple screens and background training."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from textual.app import App
from textual.screen import Screen
from textual.widgets import Static

from .capture_screen import CaptureScreen, list_cameras
from .config import load_config, Config
from .config_screen import ConfigScreen
from .kde_lock import KDEScreenLocker
from .screen_lock_manager import (
    ScreenLockManager,
    NullPresenceService,
    PresenceService,
)
from .whitelist_screen import WhitelistScreen
from .yolo_train import YOLOTrainingScheduler
from .main_menu import MainMenuScreen


log = logging.getLogger(__name__)


class PlaceholderScreen(Screen):
    """Simple placeholder screen displaying a message."""

    def __init__(self, message: str) -> None:
        super().__init__()
        self._message = message

    def compose(self):  # type: ignore[override]
        yield Static(self._message)


class MidoriApp(App):
    """Skeleton Textual application with basic navigation."""

    BINDINGS = [
        ("c", "view_capture", "Capture"),
        ("w", "view_whitelist", "Whitelist"),
        ("g", "view_config", "Config"),
        ("t", "view_training", "Training"),
        ("m", "view_menu", "Menu"),
        ("r", "retrain", "Retrain"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        config_path: str | Path,
        scheduler: YOLOTrainingScheduler | None = None,
        locker: KDEScreenLocker | None = None,
        presence_service: PresenceService | None = None,
    ) -> None:
        super().__init__()
        self._config_path = Path(config_path)
        self._config: Config = load_config(self._config_path)
        log.debug("Loaded config from %s", self._config_path)
        self._locker = locker or KDEScreenLocker()
        self._scheduler = scheduler or YOLOTrainingScheduler(
            self._locker, self._config_path
        )
        self._presence = presence_service or NullPresenceService()
        self._lock_manager = ScreenLockManager(
            self._locker, self._presence, notify=self._update_lock_state
        )
        self._train_task: asyncio.Task[None] | None = None
        self._lock_task: asyncio.Task[None] | None = None

    def _update_lock_state(self, state: str) -> None:
        self.sub_title = state
        self.notify(state)

    def on_mount(self) -> None:  # type: ignore[override]
        cam_ids = [
            int(c) if isinstance(c, str) and c.isdigit() else c
            for c in self._config.cameras
        ]
        if not cam_ids:
            cam_ids = list_cameras()
        self.install_screen(
            CaptureScreen(
                Path(self._config.dataset),
                cam_ids,
                model_path=Path(self._config.model),
                device=self._config.device,
            ),
            name="capture",
        )
        self.install_screen(
            WhitelistScreen(Path(self._config.model)), name="whitelist"
        )
        self.install_screen(ConfigScreen(self._config_path), name="config")
        self.install_screen(
            PlaceholderScreen("Training status"),
            name="training",
        )
        self.install_screen(MainMenuScreen(), name="menu")
        log.debug("Installed application screens")
        self.push_screen("menu")
        log.debug("Pushed main menu screen")
        self._train_task = asyncio.create_task(self._train_loop())
        log.debug("Started training loop task")
        self._lock_task = asyncio.create_task(self._lock_manager.start())
        log.debug("Started screen lock manager")

    async def _train_loop(self) -> None:
        while True:
            await self._scheduler.maybe_train()
            await asyncio.sleep(10)

    def action_view_capture(self) -> None:
        log.debug("Switching to capture screen")
        self.switch_screen("capture")

    def action_view_whitelist(self) -> None:
        log.debug("Switching to whitelist screen")
        self.switch_screen("whitelist")

    def action_view_config(self) -> None:
        log.debug("Switching to config screen")
        self.switch_screen("config")

    def action_view_training(self) -> None:
        log.debug("Switching to training screen")
        self.switch_screen("training")

    def action_view_menu(self) -> None:
        log.debug("Switching to main menu")
        self.switch_screen("menu")

    async def action_retrain(self) -> None:
        log.info("Retrain requested")
        await self._scheduler.maybe_train(force=True)

    def action_quit(self) -> None:  # pragma: no cover - trivial
        if self._train_task:
            self._train_task.cancel()
        if self._lock_task and not self._lock_task.done():
            self._lock_task.cancel()
        log.debug("Application exiting")
        self.exit()
