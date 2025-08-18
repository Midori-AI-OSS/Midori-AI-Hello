"""Textual screen for editing configuration settings."""

from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, ListView, Static

from .config import Config, load_config, update_config


class ConfigScreen(Screen):
    """Simple configuration editor screen."""

    def __init__(self, config_path: str | Path) -> None:
        super().__init__()
        self._config_path = Path(config_path)
        self._config: Config = load_config(self._config_path)

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("Config editor")
        yield Input(value=self._config.dataset, placeholder="Dataset", id="dataset")
        yield Input(value=str(self._config.epochs), placeholder="Epochs", id="epochs")
        yield Input(value=str(self._config.batch), placeholder="Batch", id="batch")
        yield Input(
            value=str(self._config.idle_threshold),
            placeholder="Idle threshold",
            id="idle_threshold",
        )
        yield Input(value=self._config.model, placeholder="Model", id="model")
        yield Input(value=self._config.backend, placeholder="Backend", id="backend")
        yield Input(value=self._config.device, placeholder="Device", id="device")
        yield Input(
            value=self._config.model_size, placeholder="Model size", id="model_size"
        )
        self._camera_list = ListView(*[Static(c) for c in self._config.cameras])
        yield self._camera_list
        yield Button("Add Camera", id="add_cam")

    def action_quit(self) -> None:  # pragma: no cover - trivial
        self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        if event.button.id == "add_cam":
            new_id = str(len(self._config.cameras))
            try:
                self.app.status = "Adding camera..."
            except Exception:
                pass
            self._config.cameras.append(new_id)
            update_config(self._config_path, cameras=self._config.cameras)
            self._camera_list.append(Static(new_id))
            try:
                self.app.status = "Config updated"
            except Exception:
                pass

