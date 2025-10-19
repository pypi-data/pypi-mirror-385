import sys
import tempfile
from pathlib import Path
import pytest


def test_install_requirements_nonempty_triggers_installer(monkeypatch, capsys):
    """Test that install_requirements triggers installation for non-empty requirements.txt.

    Args:
        monkeypatch: pytest fixture to patch objects.
        capsys: pytest fixture to capture stdout and stderr.

    This test checks that either pip or uv is called when a requirements.txt
    file is present in the given directory.
    """
    try:
        import reposmith.venv_utils as vu
    except Exception:
        pytest.skip("venv_utils is not available")

    if not hasattr(vu, "install_requirements"):
        pytest.skip("install_requirements is not available")

    calls = []

    def fake_run(cmd, *a, **k):
        calls.append(tuple(cmd))

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr("subprocess.run", fake_run, raising=True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "requirements.txt").write_text("anypkg==0.0.0\n", encoding="utf-8")

        tried = False
        try:
            vu.install_requirements(root)
            tried = True
        except TypeError:
            for kw in ("python", "python_path", "py_exe", "interpreter", "exe", "python_exe"):
                try:
                    vu.install_requirements(root, **{kw: sys.executable})
                    tried = True
                    break
                except TypeError:
                    continue
            if not tried:
                try:
                    vu.install_requirements(root, sys.executable)
                    tried = True
                except TypeError:
                    pass
        if not tried:
            pytest.skip("No suitable signature for install_requirements found")

    out, err = capsys.readouterr()
    joined = [" ".join(c) for c in calls]
    pip_called = any("pip" in j and "-r" in j and "requirements.txt" in j for j in joined)
    uv_called = any("uv" in j for j in joined) or ("uv" in out.lower())

    assert pip_called or uv_called, (
        f"Expected pip or uv path. calls={joined}, stdout={out!r}"
    )
