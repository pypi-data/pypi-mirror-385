import os, sys, tempfile
from pathlib import Path
import pytest

def test_cli_rejects_unknown_subcommand(monkeypatch, capsys):
    try:
        from reposmith.cli import main as cli_main
    except Exception:
        pytest.skip("CLI غير متاح")

    monkeypatch.setattr(sys, "argv", ["reposmith", "___not_a_real_cmd___"])
    with pytest.raises(SystemExit) as exc:
        cli_main()
    assert exc.value.code == 2
    out, err = capsys.readouterr()
    assert "usage" in (out + err).lower()

def test_cli_init_rejects_bad_flag(monkeypatch, tmp_path):
    try:
        from reposmith.cli import main as cli_main
    except Exception:
        pytest.skip("CLI غير متاح")

    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        monkeypatch.setattr(sys, "argv", ["reposmith", "init", "--__bad_flag__"])
        with pytest.raises(SystemExit) as exc:
            cli_main()
        assert exc.value.code == 2
    finally:
        os.chdir(prev)
