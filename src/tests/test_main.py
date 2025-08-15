import pytest
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
