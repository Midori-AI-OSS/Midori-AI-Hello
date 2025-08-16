import subprocess
import pytest
import midori_ai_hello.__main__ as cli
from midori_ai_hello.__main__ import main


def test_main_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "0.1.0" in captured.out


def test_cli_entrypoint():
    result = subprocess.run(["midori_ai_hello", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_main_inhibits_screensaver(monkeypatch):
    calls: list[str] = []

    class DummyLocker:
        async def inhibit(self, reason: str) -> int:
            calls.append("in")
            return 1

        async def uninhibit(self, cookie: int) -> None:
            calls.append("out")

    monkeypatch.setattr(cli, "KDEScreenLocker", lambda: DummyLocker())

    class DummyScheduler:
        def __init__(self, locker, config_path):
            pass

    monkeypatch.setattr(cli, "YOLOTrainingScheduler", DummyScheduler)

    class DummyApp:
        def __init__(self, config_path, scheduler=None, locker=None, presence_service=None):
            pass

        async def run_async(self) -> None:
            return None

    monkeypatch.setattr(cli, "MidoriApp", DummyApp)

    class DummyConfig:
        cameras: list[str] = []
        model = "model.pt"

    monkeypatch.setattr(cli, "load_config", lambda path: DummyConfig())
    monkeypatch.setattr(cli, "WhitelistManager", lambda path: object())
    monkeypatch.setattr(
        cli, "CameraPresenceService", lambda cams, model, wl: object()
    )

    cli.main([])
    assert calls == ["in", "out"]
