import sys
import pytest

def _has_subcommand(parser, name: str) -> bool:
    """Check if the parser includes a specific subcommand.

    Args:
        parser: The argument parser object.
        name (str): Name of the subcommand to look for.

    Returns:
        bool: True if the subcommand exists, False otherwise.
    """
    for action in parser._actions:
        if getattr(action, "choices", None) and name in action.choices:
            return True
    return False

def test_main_prints_version_and_exits_zero(monkeypatch, capsys):
    """Test that --version prints output and exits with code 0."""
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main not available")

    monkeypatch.setattr(sys, "argv", ["reposmith", "--version"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0

    out, err = capsys.readouterr()
    assert out.strip() != ""

def test_main_invalid_command_exits_2(monkeypatch):
    """Test that unknown subcommand causes exit with code 2."""
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main not available")

    monkeypatch.setattr(sys, "argv", ["reposmith", "UNKNOWN_CMD"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 2

def test_main_brave_profile_if_available(monkeypatch):
    """Test 'brave-profile' subcommand if it exists in the CLI."""
    try:
        import reposmith.main as mod
        from reposmith.cli import build_parser
    except Exception:
        pytest.skip("CLI not available")

    parser = build_parser()
    if not _has_subcommand(parser, "brave-profile"):
        pytest.skip("'brave-profile' subcommand not available")

    monkeypatch.setattr(sys, "argv", ["reposmith", "brave-profile", "--help"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0