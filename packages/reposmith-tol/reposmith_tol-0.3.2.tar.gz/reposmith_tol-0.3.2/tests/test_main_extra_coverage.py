import sys
import pytest

def _has_subcommand(parser, name: str) -> bool:
    for action in parser._actions:
        if getattr(action, "choices", None) and name in action.choices:
            return True
    return False

def test_main_prints_version_and_exits_zero(monkeypatch, capsys):
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main غير متاح")
    monkeypatch.setattr(sys, "argv", ["reposmith", "--version"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0
    out, err = capsys.readouterr()
    # يكفي أنه طبع رقم/نص نسخة
    assert out.strip() != ""

def test_main_invalid_command_exits_2(monkeypatch):
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main غير متاح")
    monkeypatch.setattr(sys, "argv", ["reposmith", "UNKNOWN_CMD"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 2

def test_main_brave_profile_if_available(monkeypatch):
    """
    جرّب subcommand 'brave-profile' إن كان موجودًا في CLI، وإلا skip.
    """
    try:
        import reposmith.main as mod
        from reposmith.cli import build_parser
    except Exception:
        pytest.skip("CLI غير متاح")
    parser = build_parser()
    if not _has_subcommand(parser, "brave-profile"):
        pytest.skip("brave-profile غير متاح في هذا الإصدار")
    # شغّله بمساعدة --help حتى يكون التنفيذ آمن
    monkeypatch.setattr(sys, "argv", ["reposmith", "brave-profile", "--help"])
    with pytest.raises(SystemExit) as exc:
        mod.main()   # argparse --help يخرج بـ 0
    assert exc.value.code == 0
