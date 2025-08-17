"""Textual main menu screen providing navigation options."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from .capture_screen import list_cameras


class MainMenuScreen(Screen):
    """Initial menu guiding the user through application features."""

    def compose(self) -> ComposeResult:  # type: ignore[override]
        config = getattr(self.app, "_config", None)
        if config and not config.cameras and not list_cameras():
            yield Static(
                "No cameras detected. Use 'Configure cameras' to add one.",
                id="help",
            )
        yield OptionList(
            Option("Capture photos", id="capture"),
            Option("Manage whitelist", id="whitelist"),
            Option("View training status", id="training"),
            Option("Configure cameras", id="config"),
            Option("Quit", id="quit"),
        )

    def on_option_list_option_selected(
        self, event: OptionList.OptionSelected
    ) -> None:
        """Handle menu option selection."""
        choice = event.option.id
        if choice == "capture":
            self.app.switch_screen("capture")
        elif choice == "whitelist":
            self.app.switch_screen("whitelist")
        elif choice == "training":
            self.app.switch_screen("training")
        elif choice == "config":
            self.app.switch_screen("config")
        elif choice == "quit":
            self.app.action_quit()
