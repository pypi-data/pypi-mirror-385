import os
import sys
import tempfile
from pathlib import Path
import pytest

def _has_flag(help_text: str, flag: str) -> bool:
    """Check if a specific flag exists in the CLI help text.

    Args:
        help_text (str): The CLI help message.
        flag (str): The flag to check for.

    Returns:
        bool: True if the flag is found, False otherwise.
    """
    return flag in help_text

def test_cli_init_with_supported_flags(monkeypatch):
    """Test the 'init' CLI command with all supported optional flags.

    Args:
        monkeypatch: pytest fixture to patch sys.argv.

    Notes:
        This test dynamically adapts to available flags in the CLI help.
    """
    try:
        from reposmith.cli import build_parser, main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    parser = build_parser()
    help_text = parser.format_help()

    args = ["reposmith", "init"]
    if _has_flag(help_text, "--with-gitignore"):
        args.append("--with-gitignore")
    if _has_flag(help_text, "--with-vscode"):
        args.append("--with-vscode")
    if _has_flag(help_text, "--no-venv"):
        args.append("--no-venv")
    if _has_flag(help_text, "--with-license"):
        args.append("--with-license")
        if _has_flag(help_text, "--author"):
            args += ["--author", "CIUser"]
        if _has_flag(help_text, "--year"):
            args += ["--year", "2099"]
    if _has_flag(help_text, "--entry"):
        args += ["--entry", "run.py"]

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

        assert proj.exists()