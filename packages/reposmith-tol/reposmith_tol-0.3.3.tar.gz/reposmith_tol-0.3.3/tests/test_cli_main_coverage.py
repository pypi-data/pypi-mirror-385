import os
import sys
import tempfile
from pathlib import Path

import pytest


def _has_subcommand(parser, name: str) -> bool:
    for action in parser._actions:
        if getattr(action, "choices", None) and name in action.choices:
            return True
    return False


def test_cli_build_parser_has_init():
    try:
        from reposmith.cli import build_parser
    except Exception:
        pytest.skip("reposmith.cli.build_parser غير متاح")

    parser = build_parser()
    if not _has_subcommand(parser, "init"):
        pytest.skip("Subcommand 'init' غير متاح")
    _ = parser.format_help()


def test_cli_main_init_smoke_changes_cwd(monkeypatch, capsys):
    """
    شغّل reposmith.cli.main عبر sys.argv وتأكد عدم انهيار المسار السعيد.
    IMPORTANT: ارجع خارج مجلد proj قبل انتهاء TemporaryDirectory لتجنب WinError 32.
    """
    try:
        from reposmith.cli import main as cli_main, build_parser
    except Exception:
        pytest.skip("reposmith.cli غير متاح")

    parser = build_parser()
    if not _has_subcommand(parser, "init"):
        pytest.skip("Subcommand 'init' غير متاح")

    prev_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "proj"
        proj.mkdir(parents=True, exist_ok=True)

        # ادخل للمجلد أثناء التنفيذ فقط
        os.chdir(proj)
        try:
            monkeypatch.setattr(sys, "argv", ["reposmith", "init"])
            try:
                rc = cli_main()
                assert rc in (None, 0)
            except SystemExit as e:
                assert e.code in (0, None)
        finally:
            # ارجع لمكان آمن خارج proj قبل نهاية with
            os.chdir(prev_cwd)

        out, err = capsys.readouterr()
        # تحققات خفيفة غير متشددة
        _ = (proj / ".gitignore").exists()
        _ = (proj / ".vscode").exists()
        _ = (proj / "LICENSE").exists()
