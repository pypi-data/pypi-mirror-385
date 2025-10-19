import os, sys, tempfile
from pathlib import Path
import pytest

def _has_flag(help_text: str, flag: str) -> bool:
    return flag in help_text

def test_cli_init_with_entry_creates_file(monkeypatch):
    try:
        from reposmith.cli import build_parser, main as cli_main
    except Exception:
        pytest.skip("CLI غير متاح")

    parser = build_parser()
    help_text = parser.format_help()
    if not _has_flag(help_text, "--entry"):
        pytest.skip("--entry غير مدعوم")

    args = ["reposmith", "init", "--entry", "run.py"]
    # لو عندك --no-venv خلّيه أسرع
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

        # نتحقق أن run.py اتأنشأ
        assert (proj / "run.py").exists()
