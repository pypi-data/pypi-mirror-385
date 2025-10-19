import os
import sys
import tempfile
from pathlib import Path
import pytest


def _has_flag(help_text: str, flag: str) -> bool:
    """Return True if the flag appears in the CLI help text."""
    return flag in help_text


def test_cli_init_with_entry_creates_file(monkeypatch):
    """
    Verify that `reposmith init` creates the specified entry file.

    The test prefers `--entry` if available; if not, it falls back to
    `--main-file` (deprecated alias), otherwise it skips.
    """
    try:
        from reposmith.cli import build_parser, main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    parser = build_parser()
    help_text = parser.format_help()

    args = ["reposmith", "init"]
    if _has_flag(help_text, "--entry"):
        args += ["--entry", "run.py"]
    elif _has_flag(help_text, "--main-file"):
        args += ["--main-file", "run.py"]
    else:
        pytest.skip("No supported flag to set entry file")

    # Use --no-venv if supported to speed up the test
    if _has_flag(help_text, "--no-venv"):
        args.append("--no-venv")

    prev = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "proj"
        proj.mkdir(parents=True)
        os.chdir(proj)
        try:
            monkeypatch.setattr(sys, "argv", args)
            try:
                rc = cli_main()
                assert rc in (None, 0)
            except SystemExit as e:
                assert e.code in (0, None)
        finally:
            os.chdir(prev)

        assert (proj / "run.py").exists()
