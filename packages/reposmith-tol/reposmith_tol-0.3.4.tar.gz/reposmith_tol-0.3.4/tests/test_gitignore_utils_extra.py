import tempfile
from pathlib import Path
import pytest

def test_gitignore_unsupported_preset_is_adaptive(capsys):
    """Test that an unsupported .gitignore preset triggers fallback behavior or a warning.

    Args:
        capsys: pytest fixture to capture stdout and stderr.

    Notes:
        Accepts multiple behaviors:
        - Raises a ValueError, KeyError, or SystemExit
        - Falls back to a default or basic .gitignore content
    """
    try:
        from reposmith import gitignore_utils as gi
    except Exception:
        pytest.skip("gitignore_utils not available")

    fn = None
    for name in ("ensure_gitignore", "create_gitignore", "write_gitignore"):
        if hasattr(gi, name):
            fn = getattr(gi, name)
            break
    if fn is None:
        pytest.skip("No gitignore function available")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        try:
            try:
                fn(root, preset="__NOT_A_REAL_PRESET__")
            except TypeError:
                fn(root, preset_name="__NOT_A_REAL_PRESET__")
        except (ValueError, KeyError, SystemExit):
            return

        out, err = capsys.readouterr()
        msg = (out + err).lower()

        gitignore = root / ".gitignore"
        assert gitignore.exists() and gitignore.stat().st_size > 0

        hints = (
            "unknown preset",
            "falling back",
            "available",
            "preset",
            ".gitignore"
        )
        assert any(h in msg for h in hints), f"Expected fallback message. got: {msg!r}"