import os
import sys
import tempfile
from pathlib import Path

import pytest


def test_module_main_help_exits_zero(monkeypatch, capsys):
    """
    شغّل reposmith.main.main مع argv=['reposmith','-h'] (وليس '-m reposmith.main')
    """
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main غير متاح")

    monkeypatch.setattr(sys, "argv", ["reposmith", "-h"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0
    out, err = capsys.readouterr()
    assert "usage" in out.lower() or "help" in out.lower()


def test_module_main_init_smoke(monkeypatch, capsys):
    """
    شغّل reposmith.main.main مع argv=['reposmith','init'] داخل مجلد مؤقت.
    IMPORTANT: ارجع خارج proj قبل نهاية TemporaryDirectory لتجنب WinError 32.
    """
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main غير متاح")

    prev_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as td:
        proj = Path(td) / "proj"
        proj.mkdir(parents=True, exist_ok=True)

        os.chdir(proj)
        try:
            monkeypatch.setattr(sys, "argv", ["reposmith", "init"])
            try:
                rc = mod.main()
                assert rc in (None, 0)
            except SystemExit as e:
                # ينبغي أن يكون 0؛ إن أعاد 2 فهناك خطأ في تمرير argv عادة
                assert e.code in (0, None)
        finally:
            os.chdir(prev_cwd)

        out, err = capsys.readouterr()
        _ = (proj / ".gitignore").exists()
        _ = (proj / ".vscode").exists()
        _ = (proj / "LICENSE").exists()
