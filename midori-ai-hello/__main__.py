"""Command-line entry point for Midori-AI Hello."""
from __future__ import annotations

import argparse
import asyncio
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .app import MidoriApp
from .kde_lock import KDEScreenLocker, PowerInhibitor
from .presence_service import CameraPresenceService
from .screen_lock_manager import NullPresenceService
from .whitelist import WhitelistManager
from .config import load_config
from .yolo_train import YOLOTrainingScheduler


def main(argv: list[str] | None = None) -> int:
    """Run the Midori-AI Hello Textual application."""
    parser = argparse.ArgumentParser(prog="midori-ai-hello")
    try:
        pkg_version = version("midori-ai-hello")
    except PackageNotFoundError:
        pkg_version = "0.0.0"
    parser.add_argument("--version", action="version", version=pkg_version)
    parser.parse_args(argv)

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
