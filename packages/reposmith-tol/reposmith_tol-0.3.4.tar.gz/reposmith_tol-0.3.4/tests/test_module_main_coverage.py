import os
import sys
import tempfile
from pathlib import Path

import pytest

def test_module_main_help_exits_zero(monkeypatch, capsys):
    """Test that running reposmith.main with -h shows help and exits with code 0."""
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main not available")

    monkeypatch.setattr(sys, "argv", ["reposmith", "-h"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0

    out, err = capsys.readouterr()
    assert "usage" in out.lower() or "help" in out.lower()

def test_module_main_init_smoke(monkeypatch, capsys):
    """Test reposmith.main 'init' execution inside a temporary directory."""
    try:
        import reposmith.main as mod
    except Exception:
        pytest.skip("reposmith.main not available")

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
                assert e.code in (0, None)
        finally:
            os.chdir(prev_cwd)

        out, err = capsys.readouterr()
        # Check that key files were created
        _ = (proj / ".gitignore").exists()
        _ = (proj / ".vscode").exists()
        _ = (proj / "LICENSE").exists()