"""Command-line entry point for Midori-AI Hello."""
from __future__ import annotations

import argparse
import asyncio
import logging
import os
import yaml
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .app import MidoriApp
from .kde_lock import KDEScreenLocker, PowerInhibitor
from .presence_service import CameraPresenceService
from .screen_lock_manager import NullPresenceService
from .whitelist import WhitelistManager
from .config import load_config, update_config
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
        raw: dict[str, object] = {}
        if config_path.exists():
            raw = yaml.safe_load(config_path.read_text()) or {}
        missing = [k for k in ("device", "model_size") if k not in raw]
        if missing:
            try:
                device = input("Use CPU or GPU? [cpu/gpu]: ").strip() or "cpu"
            except (EOFError, OSError):
                device = "cpu"
            try:
                size = (
                    input("Model size (n/s/m/l/xl) [n]: ").strip() or "n"
                )
            except (EOFError, OSError):
                size = "n"
            updates: dict[str, str] = {}
            if "device" not in raw:
                updates["device"] = device
            if "model_size" not in raw:
                updates["model_size"] = size
            if updates:
                update_config(config_path, **updates)
        config = load_config(config_path)
        locker = KDEScreenLocker()
        scheduler = YOLOTrainingScheduler(locker, config_path)
        whitelist = WhitelistManager(Path(config.model))
        presence: CameraPresenceService | NullPresenceService
        if config.cameras:
            presence = CameraPresenceService(
                config.cameras, config.model, whitelist, device=config.device
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
