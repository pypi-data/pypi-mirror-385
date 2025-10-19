import unittest
import tempfile
from pathlib import Path

from reposmith.gitignore_utils import create_gitignore, PRESETS

class TestGitignoreUtils(unittest.TestCase):
    """Unit tests for the gitignore creation utility functions."""

    def setUp(self):
        """Create a temporary directory for test isolation."""
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.tmp = Path(self.tmp_ctx.name)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.tmp_ctx.cleanup()

    def test_create_gitignore_python_preset(self):
        """Test .gitignore creation using the 'python' preset."""
        state = create_gitignore(self.tmp, preset="python", force=False)
        self.assertEqual(state, "written")
        gi = (self.tmp / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("__pycache__/", gi)
        self.assertIn("*.py[cod]", gi)

    def test_create_gitignore_node_preset(self):
        """Test .gitignore creation using the 'node' preset."""
        state = create_gitignore(self.tmp, preset="node", force=False)
        self.assertEqual(state, "written")
        gi = (self.tmp / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("node_modules/", gi)
        self.assertIn("yarn-error.log*", gi)

    def test_create_gitignore_django_preset(self):
        """Test .gitignore creation using the 'django' preset."""
        state = create_gitignore(self.tmp, preset="django", force=False)
        self.assertEqual(state, "written")
        gi = (self.tmp / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("db.sqlite3", gi)
        self.assertIn("staticfiles/", gi)

    def test_existing_gitignore_without_force(self):
        """Test behavior when .gitignore already exists and force=False."""
        p = self.tmp / ".gitignore"
        p.write_text("OLD", encoding="utf-8")
        state = create_gitignore(self.tmp, preset="python", force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "OLD")
        self.assertFalse((p.with_suffix(p.suffix + ".bak")).exists())

    def test_existing_gitignore_with_force_and_backup(self):
        """Test overwriting .gitignore with force=True and creating a backup."""
        p = self.tmp / ".gitignore"
        p.write_text("v1", encoding="utf-8")
        state = create_gitignore(self.tmp, preset="python", force=True)
        self.assertEqual(state, "written")
        gi = p.read_text(encoding="utf-8")
        self.assertIn("__pycache__/", gi)
        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

if __name__ == "__main__":
    unittest.main(verbosity=2)