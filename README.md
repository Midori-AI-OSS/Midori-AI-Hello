# Midori-AI-Hello

Midori-AI Hello is a vision toolkit that captures images, labels them, and trains YOLO models that integrate with KDE's screen locker.

## Features

- KDE screen lock integration through the `org.freedesktop.ScreenSaver` DBus API, automatically inhibiting locking while the app runs
- Textual TUI for photo capture and YOLO-format labeling
- Idle-triggered YOLO training scheduler that runs on CPU
- Screen lock manager that locks after absence and unlocks when authorised users return
- Multi-camera presence detection that recognises authorised users and feeds the lock manager
- Status bar shows current actions and lock state across screens

## Installation

Use [uv](https://github.com/astral-sh/uv) to set up the environment:

```sh
uv sync
```

## Usage

Launch the Textual interface:

```sh
uv run midori_ai_hello
```

## Testing

Execute the test suite with:

```sh
uv run pytest
```
