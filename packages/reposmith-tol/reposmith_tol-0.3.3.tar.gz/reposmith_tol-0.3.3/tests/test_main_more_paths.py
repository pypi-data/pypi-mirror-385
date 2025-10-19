import sys, tempfile, os
from pathlib import Path
import pytest

def _run_main(argv):
    import reposmith.main as mod
    prev = list(sys.argv)
    try:
        sys.argv = argv
        try:
            rc = mod.main()
            return rc
        except SystemExit as e:
            return e.code
    finally:
        sys.argv = prev

def test_main_no_args_shows_usage_exits_2(capsys):
    try:
        import reposmith.main  # noqa: F401
    except Exception:
        pytest.skip("reposmith.main غير متاح")
    code = _run_main(["reposmith"])
    assert code == 2
    out, err = capsys.readouterr()
    assert "usage" in (out + err).lower()

def test_main_init_help_zero(capsys, tmp_path):
    try:
        import reposmith.main  # noqa: F401
    except Exception:
        pytest.skip("reposmith.main غير متاح")
    # نبدّل cwd لمجلد مؤقت ثم نرجع قبل انتهاء الاختبار (ويندوز)
    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        code = _run_main(["reposmith", "init", "-h"])
        assert code == 0 or code is None
        out, err = capsys.readouterr()
        assert "usage" in (out + err).lower()
    finally:
        os.chdir(prev)

def test_main_unknown_flag_on_init_exits_2(tmp_path):
    try:
        import reposmith.main  # noqa: F401
    except Exception:
        pytest.skip("reposmith.main غير متاح")
    prev = os.getcwd()
    os.chdir(tmp_path)
    try:
        code = _run_main(["reposmith", "init", "--__not_a_real_flag__"])
        assert code == 2
    finally:
        os.chdir(prev)
