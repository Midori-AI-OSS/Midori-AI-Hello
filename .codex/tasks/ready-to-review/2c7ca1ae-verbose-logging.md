# Verbose file logging

## Problem
Running the TUI produces no log output and makes debugging difficult.

## Task
Add more verbose logging with file output so camera and TUI activity can be inspected after running.

## Steps
- [x] Introduce a log configuration that writes DEBUG-level output to a file (e.g., `midori-ai-hello.log`) while preserving existing console info.
- [x] Update `midori_ai_hello.__main__` to initialize the logging config early and respect a `--log-level` or `LOG_LEVEL` env var.
- [x] Ensure modules like `presence_service` and `capture_screen` emit useful debug messages for camera discovery and capture actions.
- [x] Document the logging behavior and configuration options in `.codex/implementation/`.
- [x] Add tests verifying log file creation and sample log entries when running core components.

## Context
Requested after observing that the TUI prompts to capture images without emitting any diagnostic logs, complicating issue triage.
