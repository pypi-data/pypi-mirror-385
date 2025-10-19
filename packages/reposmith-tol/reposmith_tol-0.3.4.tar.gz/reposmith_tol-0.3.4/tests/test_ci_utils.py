import unittest
import tempfile
from pathlib import Path

from reposmith.ci_utils import ensure_github_actions_workflow

class TestCIUtils(unittest.TestCase):
    """Unit tests for the ensure_github_actions_workflow utility."""

    def setUp(self):
        """Set up a temporary directory for test context."""
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_ctx.name)

    def tearDown(self):
        """Clean up the temporary directory after each test."""
        self.tmp_ctx.cleanup()

    def test_generate_default_workflow(self):
        """Test generating a default GitHub Actions workflow file."""
        state = ensure_github_actions_workflow(self.root, force=False)
        self.assertEqual(state, "written")
        p = self.root / ".github" / "workflows" / "ci.yml"
        yml = p.read_text(encoding="utf-8")

        self.assertIn("actions/checkout@v4", yml)
        self.assertIn("actions/setup-python@v5", yml)
        self.assertIn('python-version: "3.12"', yml)
        self.assertIn("Run unit tests", yml)

    def test_existing_without_force(self):
        """Test behavior when a workflow file already exists and force is False."""
        p = self.root / ".github" / "workflows" / "ci.yml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("OLD", encoding="utf-8")

        state = ensure_github_actions_workflow(self.root, force=False)
        self.assertEqual(state, "exists")
        self.assertEqual(p.read_text(encoding="utf-8"), "OLD")
        self.assertFalse(p.with_suffix(p.suffix + ".bak").exists())

    def test_force_overwrite_creates_backup_and_applies_customs(self):
        """Test that forcing overwrite creates a backup and applies custom options."""
        p = self.root / ".github" / "workflows" / "ci.yml"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("v1", encoding="utf-8")

        state = ensure_github_actions_workflow(
            self.root,
            py="3.13",
            force=True
        )
        self.assertEqual(state, "written")

        bak = p.with_suffix(p.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "v1")

        yml = p.read_text(encoding="utf-8")
        self.assertIn('python-version: "3.13"', yml)
        self.assertIn("Run unit tests", yml)

if __name__ == "__main__":
    unittest.main(verbosity=2)