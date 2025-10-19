import os
import sys
import tempfile
from pathlib import Path
import pytest

def test_cli_rejects_unknown_subcommand(monkeypatch, capsys):
    """Test that the CLI exits with code 2 for an unknown subcommand.

    Args:
        monkeypatch: pytest fixture to patch sys.argv.
        capsys: pytest fixture to capture stdout and stderr.

    Notes:
        Skips the test if the CLI is unavailable.
    """
    try:
        from reposmith.cli import main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    monkeypatch.setattr(sys, "argv", ["reposmith", "___not_a_real_cmd___"])
    with pytest.raises(SystemExit) as exc:
        cli_main()
    assert exc.value.code == 2

    out, err = capsys.readouterr()
    assert "usage" in (out + err).lower()

def test_cli_init_rejects_bad_flag(monkeypatch, tmp_path):
    """Test that the CLI rejects an unknown flag for the init command.

    Args:
        monkeypatch: pytest fixture to patch sys.argv.
        tmp_path: pytest fixture providing a temporary directory.

    Notes:
        Skips the test if the CLI is unavailable.
    """
    try:
        from reposmith.cli import main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        monkeypatch.setattr(sys, "argv", ["reposmith", "init", "--__bad_flag__"])
        with pytest.raises(SystemExit) as exc:
            cli_main()
        assert exc.value.code == 2
    finally:
        os.chdir(prev)