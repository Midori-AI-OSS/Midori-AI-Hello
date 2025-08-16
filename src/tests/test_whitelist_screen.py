from pathlib import Path

from midori_ai_hello.whitelist_screen import WhitelistScreen


def test_add_remove_reencrypt(tmp_path: Path) -> None:
    model = tmp_path / "model.pt"
    model.write_text("weights")
    screen = WhitelistScreen(model, config_dir=tmp_path)
    list(screen.compose())

    screen.action_add_user("alice")
    assert "alice" in screen._manager.users()

    screen.action_remove_user("alice")
    assert "alice" not in screen._manager.users()

    # force hash mismatch by changing model weights
    model.write_text("newweights")
    screen._refresh()
    assert "mismatch" in str(screen._status.renderable).lower()

    screen.action_reencrypt()
    assert "mismatch" not in str(screen._status.renderable).lower()
