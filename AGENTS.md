# Repository Contributor Guide

This repository uses a `.codex` directory for task management and contributor documentation.

## Development Basics
- Use [`uv`](https://github.com/astral-sh/uv) for Python environments and execution.
- Use [`bun`](https://bun.sh/) for any Node tooling.
- Follow commit messages in `[TYPE] Title` format.
- Run available tests (e.g., `pytest`) before committing.

## .codex Layout
- `modes/`: role guides such as `TASKMASTER.md` and `CODER.md`.
- `tasks/`: action items for contributors. Completed tasks go in `tasks/done/`.
- `instructions/` and `implementation/`: process notes and technical documentation.

Review the relevant mode file in `.codex/modes/` before contributing.
