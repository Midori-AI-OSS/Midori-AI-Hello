"""Textual screen for managing authorised user whitelist."""
from __future__ import annotations

from pathlib import Path

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Input, Static

from .whitelist import WhitelistManager


class WhitelistScreen(Screen):
    """Screen allowing users to manage the encrypted whitelist."""

    def __init__(self, model_path: Path, config_dir: Path | None = None) -> None:
        super().__init__()
        self._manager = WhitelistManager(model_path, config_dir=config_dir)

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Static("Whitelist")
        self._status = Static(id="status")
        yield self._status
        self._users = Static(id="users")
        yield self._users
        self._name_input = Input(placeholder="Name", id="name")
        yield self._name_input
        yield Button("Add", id="add")
        yield Button("Remove", id="remove")
        yield Button("Re-encrypt", id="reencrypt")
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
            self._manager.add_user(name)
            self._name_input.value = ""
            self._refresh()

    def action_remove_user(self, name: str | None = None) -> None:
        name = name or self._name_input.value.strip()
        if name:
            self._manager.remove_user(name)
            self._name_input.value = ""
            self._refresh()

    def action_reencrypt(self) -> None:
        self._manager.reencrypt()
        self._refresh()
