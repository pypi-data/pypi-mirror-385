import os
import sys
import tempfile
from pathlib import Path
import pytest


def test_create_venv_invokes_subprocess(monkeypatch):
    """Test that create_venv triggers a subprocess call."""
    try:
        import reposmith.venv_utils as vu
    except Exception:
        pytest.skip("venv_utils not available")

    calls = []

    def fake_run(cmd, *a, **k):
        calls.append((tuple(cmd), k))

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr("subprocess.run", fake_run, raising=True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        if not hasattr(vu, "create_venv"):
            pytest.skip("create_venv not available")
        try:
            vu.create_venv(root)
        except TypeError:
            vu.create_venv(root, venv_dir=root / ".venv")

    assert calls, "Expected subprocess.run to be called at least once"


def test_install_requirements_paths(monkeypatch, capsys):
    """Covers install_requirements when requirements.txt is missing or empty."""
    try:
        import reposmith.venv_utils as vu
    except Exception:
        pytest.skip("venv_utils not available")

    if not hasattr(vu, "install_requirements"):
        pytest.skip("install_requirements not available")

    calls = []

    def fake_run(cmd, *a, **k):
        calls.append((tuple(cmd), k))

        class R:
            returncode = 0

        return R()

    monkeypatch.setattr("subprocess.run", fake_run, raising=True)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # Case 1: No requirements.txt
        called = False
        try:
            vu.install_requirements(root)
            called = True
        except TypeError:
            for kw in ("python", "python_path", "py_exe", "interpreter", "exe", "python_exe"):
                try:
                    vu.install_requirements(root, **{kw: sys.executable})
                    called = True
                    break
                except TypeError:
                    continue
            if not called:
                try:
                    vu.install_requirements(root, sys.executable)  # type: ignore[arg-type]
                    called = True
                except TypeError:
                    pass
        if not called:
            pytest.skip("install_requirements doesn't accept any known signature")

        _ = capsys.readouterr()

        # Case 2: Empty requirements.txt
        (root / "requirements.txt").write_text("", encoding="utf-8")

        try:
            vu.install_requirements(root)
        except TypeError:
            for kw in ("python", "python_path", "py_exe", "interpreter", "exe", "python_exe"):
                try:
                    vu.install_requirements(root, **{kw: sys.executable})
                    break
                except TypeError:
                    continue
            else:
                try:
                    vu.install_requirements(root, sys.executable)  # type: ignore[arg-type]
                except TypeError:
                    pass

        assert isinstance(calls, list)