import os
import sys
from pathlib import Path
import pytest

def _has_subcommand(parser, name: str) -> bool:
    """Check if the parser has a specific subcommand.

    Args:
        parser: The main argument parser object.
        name (str): The name of the subcommand to check.

    Returns:
        bool: True if the subcommand exists, False otherwise.
    """
    for act in getattr(parser, "_subparsers", None)._group_actions:  # type: ignore[attr-defined]
        if hasattr(act, "choices") and name in act.choices:
            return True
    return False

def _help_for_sub(parser, name: str) -> str:
    """Retrieve help text for a specific subcommand.

    Args:
        parser: The main argument parser object.
        name (str): The name of the subcommand.

    Returns:
        str: Help text of the subcommand, or the main help if not found.
    """
    for act in getattr(parser, "_subparsers", None)._group_actions:  # type: ignore[attr-defined]
        if hasattr(act, "choices") and name in act.choices:
            sp = act.choices[name]
            return sp.format_help()
    return parser.format_help()

def test_brave_profile_e2e_smoke(monkeypatch, tmp_path):
    """End-to-end smoke test for the brave-profile CLI subcommand.

    Args:
        monkeypatch: pytest fixture to patch functions.
        tmp_path: pytest fixture providing a temporary directory.

    Notes:
        Skips the test if CLI or subcommand is unavailable.
    """
    try:
        from reposmith.cli import build_parser, main as cli_main
    except Exception:
        pytest.skip("CLI not available")

    parser = build_parser()
    if not _has_subcommand(parser, "brave-profile"):
        pytest.skip("brave-profile not supported")

    help_text = _help_for_sub(parser, "brave-profile")
    has_dir = "--dir" in help_text or "-d " in help_text
    has_name = "--name" in help_text or "-n " in help_text

    # Disable external side-effects
    monkeypatch.setattr("subprocess.run", lambda *a, **k: type("R", (), {"returncode": 0})(), raising=True)
    monkeypatch.setattr("os.system", lambda *a, **k: 0, raising=True)
    try:
        import webbrowser
        monkeypatch.setattr(webbrowser, "open", lambda *a, **k: True, raising=True)
    except Exception:
        pass

    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        argv = ["reposmith", "brave-profile"]
        if has_dir:
            argv += ["--dir", str(tmp_path)]
        if has_name:
            argv += ["--name", "CIProfile"]

        monkeypatch.setattr(sys, "argv", argv)

        try:
            rc = cli_main()
            assert rc in (0, None)
        except SystemExit as e:
            # Accept exit codes of 0 or None for normal parser behavior
            assert e.code in (0, None)

        if has_dir:
            assert any(p.is_file() for p in Path(tmp_path).rglob("*")), (
                "Expected brave-profile to create files when --dir is supported"
            )
    finally:
        os.chdir(prev)
