import os, sys
from pathlib import Path
import pytest

def _has_subcommand(parser, name: str) -> bool:
    for act in getattr(parser, "_subparsers", None)._group_actions:  # type: ignore[attr-defined]
        if hasattr(act, "choices") and name in act.choices:
            return True
    return False

def _help_for_sub(parser, name: str) -> str:
    # حاول تجيب subparser نفسه ثم اطبع المساعدة الخاصة به
    for act in getattr(parser, "_subparsers", None)._group_actions:  # type: ignore[attr-defined]
        if hasattr(act, "choices") and name in act.choices:
            sp = act.choices[name]
            return sp.format_help()
    return parser.format_help()

def test_brave_profile_e2e_smoke(monkeypatch, tmp_path):
    try:
        from reposmith.cli import build_parser, main as cli_main
    except Exception:
        pytest.skip("CLI غير متاح")

    parser = build_parser()
    if not _has_subcommand(parser, "brave-profile"):
        pytest.skip("brave-profile غير مدعوم")

    help_text = _help_for_sub(parser, "brave-profile")
    has_dir  = "--dir"  in help_text or "-d " in help_text
    has_name = "--name" in help_text or "-n " in help_text

    # تعطيل أشياء خارجية
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
            # لو parser بيعمل exit(0) في المسار الطبيعي
            assert e.code in (0, None)

        # تحقّق لطيف: لو فيه خيارات تدل على إنشاء ملفات، نتوقع وجود شيء
        if has_dir:
            assert any(p.is_file() for p in Path(tmp_path).rglob("*")), \
                "Expected brave-profile to create files when --dir is supported"
    finally:
        os.chdir(prev)
