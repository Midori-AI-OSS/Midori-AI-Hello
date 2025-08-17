"""Command-line entry point for Midori-AI Hello."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .app import MidoriApp
from .kde_lock import KDEScreenLocker, PowerInhibitor
from .presence_service import CameraPresenceService
from .screen_lock_manager import NullPresenceService
from .whitelist import WhitelistManager
from .config import load_config
from .yolo_train import YOLOTrainingScheduler


def configure_logging(level: str) -> None:
    """Configure root logger with console and file handlers."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_path = Path("midori-ai-hello.log")
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(file_handler)
    root.addHandler(console_handler)


def main(argv: list[str] | None = None) -> int:
    """Run the Midori-AI Hello Textual application."""
    parser = argparse.ArgumentParser(prog="midori-ai-hello")
    try:
        pkg_version = version("midori-ai-hello")
    except PackageNotFoundError:
        pkg_version = "0.0.0"
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"))
    parser.add_argument("--version", action="version", version=pkg_version)
    args = parser.parse_args(argv)
    configure_logging(args.log_level)

    async def _run() -> None:
        config_path = Path("config.yaml")
        config = load_config(config_path)
        locker = KDEScreenLocker()
        scheduler = YOLOTrainingScheduler(locker, config_path)
        whitelist = WhitelistManager(Path(config.model))
        presence: CameraPresenceService | NullPresenceService
        if config.cameras:
            presence = CameraPresenceService(
                config.cameras, config.model, whitelist
            )
        else:
            presence = NullPresenceService()
        async with PowerInhibitor(locker, "midori-ai-hello running"):
            app = MidoriApp(
                config_path,
                scheduler=scheduler,
                locker=locker,
                presence_service=presence,
            )
            await app.run_async()

    asyncio.run(_run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
