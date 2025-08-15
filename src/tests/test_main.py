import pytest
import subprocess
from midori_ai_hello.__main__ import main


def test_main_runs(capsys):
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "not yet implemented" in captured.out


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
