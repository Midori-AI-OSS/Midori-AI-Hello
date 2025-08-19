"""Textual screen for managing authorised user whitelist."""
from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from .whitelist import WhitelistManager


class WhitelistScreen(Screen):
    """Screen allowing users to manage the encrypted whitelist."""

    BINDINGS = [
        ("escape", "menu", "Back to menu"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, model_path: Path, config_dir: Path | None = None) -> None:
        super().__init__()
        self._manager = WhitelistManager(model_path, config_dir=config_dir)

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("Whitelist")
        self._status = Static(id="status")
        yield self._status
        self._users = Static(id="users")
        yield self._users
        self._name_input = Input(
            placeholder="Name",
            id="name",
            tooltip="Enter the user name to add or remove",
        )
        yield self._name_input
        yield Button("Add", id="add", tooltip="Add the name to the whitelist")
        yield Button(
            "Remove",
            id="remove",
            tooltip="Remove the name from the whitelist",
        )
        yield Button(
            "Re-encrypt",
            id="reencrypt",
            tooltip="Re-encrypt the stored whitelist",
        )
        self._refresh()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _refresh(self) -> None:
        """Refresh displayed users and hash status."""
        self._users.update("\n".join(self._manager.users()))
        status = "Hash mismatch" if self._manager.is_hash_mismatch() else "Hash OK"
        self._status.update(status)

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:  # type: ignore[override]
        if event.button.id == "add":
            self.action_add_user()
        elif event.button.id == "remove":
            self.action_remove_user()
        elif event.button.id == "reencrypt":
            self.action_reencrypt()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_add_user(self, name: str | None = None) -> None:
        name = name or self._name_input.value.strip()
        if name:
            try:
                self.app.status = f"Adding {name}..."
            except Exception:
                pass
            self._manager.add_user(name)
            self._name_input.value = ""
            self._refresh()
            try:
                self.app.status = "Whitelist updated"
            except Exception:
                pass

    def action_remove_user(self, name: str | None = None) -> None:
        name = name or self._name_input.value.strip()
        if name:
            try:
                self.app.status = f"Removing {name}..."
            except Exception:
                pass
            self._manager.remove_user(name)
            self._name_input.value = ""
            self._refresh()
            try:
                self.app.status = "Whitelist updated"
            except Exception:
                pass

    def action_reencrypt(self) -> None:
        try:
            self.app.status = "Re-encrypting whitelist..."
        except Exception:
            pass
        self._manager.reencrypt()
        self._refresh()
        try:
            self.app.status = "Whitelist re-encrypted"
        except Exception:
            pass

    def action_menu(self) -> None:  # pragma: no cover - trivial
        self.app.switch_screen("menu")
