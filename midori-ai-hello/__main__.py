"""Command-line entry point for Midori-AI Hello."""
from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
import argparse


def main(argv: list[str] | None = None) -> int:
    """Placeholder Textual TUI entry point."""
    parser = argparse.ArgumentParser(prog="midori-ai-hello")
    try:
        pkg_version = version("midori-ai-hello")
    except PackageNotFoundError:
        pkg_version = "0.0.0"
    parser.add_argument("--version", action="version", version=pkg_version)
    parser.parse_args(argv)
    print("Midori-AI Hello TUI not yet implemented")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
