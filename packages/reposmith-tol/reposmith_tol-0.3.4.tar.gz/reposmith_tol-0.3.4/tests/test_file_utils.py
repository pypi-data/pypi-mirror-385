import unittest
import tempfile
from pathlib import Path

from reposmith.file_utils import create_requirements_file, create_app_file

DEFAULT_REQ_PREFIX = "# Add your dependencies here"

class TestFileUtils(unittest.TestCase):
    """Unit tests for utility functions that generate common project files."""

    def setUp(self):
        """Set up a temporary directory for each test case."""
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.tmp_ctx.cleanup()

    # -------- requirements.txt --------

    def test_create_requirements_new(self):
        """Test creation of a new requirements.txt file."""
        p = self.tmp / "requirements.txt"
        state = create_requirements_file(p, force=False)
        self.assertEqual(state, "written")
        content = p.read_text(encoding="utf-8")
        self.assertTrue(content.startswith(DEFAULT_REQ_PREFIX))

    def test_create_requirements_exists_without_force(self):
        """Test existing requirements.txt is not overwritten if force=False."""
        p = self.tmp / "requirements.txt"
        p.write_text("old", encoding="utf-8")
        state = create_requirements_file(p, force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "old")
        self.assertFalse(p.with_suffix(p.suffix + ".bak").exists())

    def test_create_requirements_with_force_and_backup(self):
        """Test overwriting an existing requirements.txt with force=True and backup."""
        p = self.tmp / "requirements.txt"
        p.write_text("v1", encoding="utf-8")
        state = create_requirements_file(p, force=True)
        self.assertEqual(state, "written")
        content = p.read_text(encoding="utf-8")
        self.assertTrue(content.startswith(DEFAULT_REQ_PREFIX))
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

    # -------- app file (main.py / run.py) --------

    def test_create_app_file_new_with_default_content(self):
        """Test creation of a new app file with default content."""
        p = self.tmp / "main.py"
        state = create_app_file(p, force=False)
        self.assertEqual(state, "written")
        text = p.read_text(encoding="utf-8")
        self.assertIn("Welcome! This is your entry file.", text)
        self.assertIn("You can now start writing your application code here.", text)

    def test_create_app_file_with_custom_content(self):
        """Test creation of an app file with custom content."""
        p = self.tmp / "run.py"
        custom = "print('مرحبا — Berlin 2025')\n"
        state = create_app_file(p, force=False, content=custom)
        self.assertEqual(state, "written")
        self.assertEqual(p.read_text(encoding="utf-8"), custom)

    def test_create_app_file_existing_without_force(self):
        """Test app file is not overwritten when it exists and force=False."""
        p = self.tmp / "app.py"
        p.write_text("old = 1\n", encoding="utf-8")
        state = create_app_file(p, force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "old = 1\n")
        self.assertFalse(p.with_suffix(p.suffix + ".bak").exists())

    def test_create_app_file_force_with_backup(self):
        """Test overwriting an existing app file with force=True and creating a backup."""
        p = self.tmp / "app.py"
        p.write_text("v1\n", encoding="utf-8")
        state = create_app_file(p, force=True, content="v2\n")
        self.assertEqual(state, "written")
        self.assertEqual(p.read_text(encoding="utf-8"), "v2\n")
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1\n")

if __name__ == "__main__":
    unittest.main(verbosity=2)