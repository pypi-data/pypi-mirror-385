from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

# --------- Helpers ---------
def _build_parser():
    """Try to import and build the CLI parser."""
    try:
        from reposmith.cli import build_parser
        return build_parser()
    except Exception:
        return None

def _get_subparser(parser, name: str):
    """Retrieve a specific subparser from the main parser.

    Args:
        parser: The main argument parser.
        name (str): Name of the subcommand parser to retrieve.

    Returns:
        Subparser instance if found, else None.
    """
    if parser is None:
        return None
    for action in parser._actions:
        if getattr(action, "choices", None):
            sub = action.choices.get(name)
            if sub is not None:
                return sub
    return None

def _flag_supported(subparser, flag: str) -> bool:
    """Check if a specific flag is supported by a subparser.

    Args:
        subparser: Subcommand parser.
        flag (str): The flag to check.

    Returns:
        bool: True if supported, False otherwise.
    """
    if subparser is None:
        return False
    for action in subparser._actions:
        if any(s == flag for s in getattr(action, "option_strings", ())):
            return True
    try:
        from io import StringIO
        buf = StringIO()
        subparser.print_help(file=buf)
        return flag in buf.getvalue()
    except Exception:
        return False

# --------- Fixtures ---------
@pytest.fixture()
def mute_external(monkeypatch):
    """Patch external effects during E2E tests (e.g., subprocess, os.system, webbrowser)."""
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: type("R", (), {"returncode": 0})(),
        raising=True,
    )
    monkeypatch.setattr("os.system", lambda *a, **k: 0, raising=True)
    try:
        import webbrowser
        monkeypatch.setattr(webbrowser, "open", lambda *a, **k: True, raising=True)
    except Exception:
        pass
    return None

# --------- Tests ---------
def test_e2e_init_happy_path(mute_external, monkeypatch):
    """E2E test for init subcommand with available CLI flags."""
    try:
        from reposmith.cli import main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    parser = _build_parser()
    init_sub = _get_subparser(parser, "init")
    if init_sub is None:
        pytest.skip("init subcommand not supported")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "proj"
        root.mkdir(parents=True, exist_ok=True)

        prev = os.getcwd()
        os.chdir(root)
        try:
            argv = ["reposmith", "init"]
            if _flag_supported(init_sub, "--entry"):
                argv += ["--entry", "run.py"]
            if _flag_supported(init_sub, "--with-gitignore"):
                argv += ["--with-gitignore"]
            if _flag_supported(init_sub, "--with-license"):
                argv += ["--with-license"]
                if _flag_supported(init_sub, "--author"):
                    argv += ["--author", "TestUser"]
                if _flag_supported(init_sub, "--year"):
                    argv += ["--year", "2099"]
            if _flag_supported(init_sub, "--with-vscode"):
                argv += ["--with-vscode"]
            if _flag_supported(init_sub, "--no-venv"):
                argv += ["--no-venv"]

            monkeypatch.setattr(sys, "argv", argv)

            try:
                rc = cli_main()
                assert rc in (None, 0)
            except SystemExit as e:
                assert e.code in (0, None)
        finally:
            os.chdir(prev)

def test_e2e_init_force_overwrite(mute_external, monkeypatch):
    """Test forced file regeneration with --force, handling dir-to-file overwrite cases."""
    try:
        from reposmith.cli import main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    parser = _build_parser()
    init_sub = _get_subparser(parser, "init")
    if init_sub is None:
        pytest.skip("init subcommand not supported")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "proj"
        root.mkdir(parents=True, exist_ok=True)
        (root / "LICENSE").write_text("PREV", encoding="utf-8")

        prev = os.getcwd()
        os.chdir(root)
        try:
            argv = ["reposmith", "init"]
            if _flag_supported(init_sub, "--entry"):
                argv += ["--entry", "run.py"]
            if _flag_supported(init_sub, "--with-license"):
                argv += ["--with-license"]
                if _flag_supported(init_sub, "--author"):
                    argv += ["--author", "X"]
                if _flag_supported(init_sub, "--year"):
                    argv += ["--year", "2000"]
            if _flag_supported(init_sub, "--force"):
                argv += ["--force"]
            if _flag_supported(init_sub, "--no-venv"):
                argv += ["--no-venv"]

            monkeypatch.setattr(sys, "argv", argv)

            def _safe_write_file(path, body, force=False, backup=False):
                p = Path(path)
                if p.exists() and p.is_dir():
                    filename = "run.py" if _flag_supported(init_sub, "--entry") else "app.py"
                    p = p / filename
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body, encoding="utf-8")
                return True

            monkeypatch.setattr("reposmith.file_utils.write_file", _safe_write_file, raising=True)

            try:
                rc = cli_main()
                assert rc in (None, 0)
            except SystemExit as e:
                assert e.code in (0, None)
        finally:
            os.chdir(prev)