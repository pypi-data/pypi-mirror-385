import sys, tempfile
from pathlib import Path
import pytest

def test_install_requirements_nonempty_triggers_installer(monkeypatch, capsys):
    try:
        import reposmith.venv_utils as vu
    except Exception:
        pytest.skip("venv_utils غير متاح")

    if not hasattr(vu, "install_requirements"):
        pytest.skip("install_requirements غير متاح")

    calls = []
    def fake_run(cmd, *a, **k):
        calls.append(tuple(cmd))
        class R: returncode = 0
        return R()

    monkeypatch.setattr("subprocess.run", fake_run, raising=True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "requirements.txt").write_text("anypkg==0.0.0\n", encoding="utf-8")

        # تواقيع مختلفة محتملة
        tried = False
        try:
            vu.install_requirements(root); tried = True
        except TypeError:
            for kw in ("python","python_path","py_exe","interpreter","exe","python_exe"):
                try:
                    vu.install_requirements(root, **{kw: sys.executable}); tried = True; break
                except TypeError:
                    continue
            if not tried:
                try:
                    vu.install_requirements(root, sys.executable); tried = True
                except TypeError:
                    pass
        if not tried:
            pytest.skip("لم نجد توقيعًا مناسبًا لـ install_requirements")

    out, err = capsys.readouterr()

    # نقبل أي من المسارات:
    # 1) pip -r requirements.txt عبر subprocess
    joined = [" ".join(c) for c in calls]
    pip_called = any(("pip" in j and "-r" in j and "requirements.txt" in j) for j in joined)
    # 2) uv استُخدم (إما عبر subprocess أو via طباعته)
    uv_called = any("uv" in j for j in joined) or ("uv" in out.lower())

    assert pip_called or uv_called, f"Expected pip or uv path. calls={joined}, stdout={out!r}"
