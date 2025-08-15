# Midori-AI-Hello

Midori-AI Hello is a vision toolkit that lets you collect images, label them, and train YOLO models that integrate with KDE's screen locker.

## Features

- Async DBus client for KDE's `org.freedesktop.ScreenSaver` interface
- Textual TUI for capturing camera frames and saving YOLO-format labels
- Idle-triggered scheduler that trains Ultralytics models on CPU

## Installation

Use [uv](https://github.com/astral-sh/uv) to set up the environment:

```sh
uv sync
```

## Usage

Run the placeholder TUI (prints a stub message for now):

```sh
uv run midori_ai_hello
```

## Testing

Execute the test suite with:

```sh
uv run pytest
```
