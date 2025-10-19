import tempfile
from pathlib import Path
import pytest

def test_license_exists_without_force_skips(capsys):
    """Test that existing LICENSE file is not overwritten when force=False."""
    try:
        from reposmith.license_utils import create_license
    except Exception:
        pytest.skip("license_utils not available")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "LICENSE"
        target.write_text("OLD", encoding="utf-8")

        create_license(root, license_type="MIT", owner_name="X", force=False)
        assert target.read_text(encoding="utf-8") == "OLD"

def test_license_exists_with_force_overwrites():
    """Test that LICENSE file is overwritten with force=True."""
    try:
        from reposmith.license_utils import create_license
    except Exception:
        pytest.skip("license_utils not available")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        target = root / "LICENSE"
        target.write_text("OLD", encoding="utf-8")

        create_license(root, license_type="MIT", owner_name="Y", force=True)
        new_text = target.read_text(encoding="utf-8")
        assert "MIT License" in new_text
        assert "Y" in new_text

def test_license_unsupported_raises():
    """Test that an unsupported license type raises ValueError."""
    try:
        from reposmith.license_utils import create_license
    except Exception:
        pytest.skip("license_utils not available")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        with pytest.raises(ValueError):
            create_license(root, license_type="Apache-2.0", owner_name="Z", force=False)