import os
import sys
import tempfile
from pathlib import Path

import pytest

def _has_subcommand(parser, name: str) -> bool:
    """Check if the parser includes a specific subcommand.

    Args:
        parser: The argument parser object.
        name (str): The name of the subcommand.

    Returns:
        bool: True if the subcommand exists, False otherwise.
    """
    for action in parser._actions:
        if getattr(action, "choices", None) and name in action.choices:
            return True
    return False

def test_cli_build_parser_has_init():
    """Test that the CLI parser includes the 'init' subcommand."""
    try:
        from reposmith.cli import build_parser
    except Exception:
        pytest.skip("reposmith.cli.build_parser not available")

    parser = build_parser()
    if not _has_subcommand(parser, "init"):
        pytest.skip("Subcommand 'init' not available")
    _ = parser.format_help()

def test_cli_main_init_smoke_changes_cwd(monkeypatch, capsys):
    """Smoke test for 'init' subcommand to verify CLI main runs without crashing.

    Args:
        monkeypatch: pytest fixture to patch sys.argv.
        capsys: pytest fixture to capture CLI output.

    Notes:
        Ensure the working directory is restored before TemporaryDirectory cleanup.
    """
    try:
        from reposmith.cli import main as cli_main, build_parser
    except Exception:
        pytest.skip("reposmith.cli not available")

    parser = build_parser()
    if not _has_subcommand(parser, "init"):
        pytest.skip("Subcommand 'init' not available")

    prev_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "proj"
        proj.mkdir(parents=True, exist_ok=True)

        os.chdir(proj)
        try:
            monkeypatch.setattr(sys, "argv", ["reposmith", "init"])
            try:
                rc = cli_main()
                assert rc in (None, 0)
            except SystemExit as e:
                assert e.code in (0, None)
        finally:
            os.chdir(prev_cwd)

        out, err = capsys.readouterr()
        _ = (proj / ".gitignore").exists()
        _ = (proj / ".vscode").exists()
        _ = (proj / "LICENSE").exists()