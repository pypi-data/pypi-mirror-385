import unittest
import tempfile
import json
from pathlib import Path

from reposmith.config_utils import load_or_create_config

class TestConfigUtils(unittest.TestCase):
    """Unit tests for the load_or_create_config utility function."""

    def setUp(self):
        """Create a temporary directory for test isolation."""
        self.ctx = tempfile.TemporaryDirectory()
        self.root = Path(self.ctx.name)

    def tearDown(self):
        """Clean up the temporary directory after tests."""
        self.ctx.cleanup()

    def test_creates_default_config_when_missing(self):
        """Test that a default config file is created when missing."""
        cfg = load_or_create_config(self.root)
        p = self.root / "setup-config.json"
        self.assertTrue(p.exists())
        data = json.loads(p.read_text(encoding="utf-8"))

        self.assertEqual(data["main_file"], "main.py")
        self.assertEqual(data["requirements_file"], "requirements.txt")
        self.assertEqual(data["venv_dir"], ".venv")

    def test_reads_existing_config_without_overwrite(self):
        """Test that an existing config file is read correctly without overwriting."""
        p = self.root / "setup-config.json"
        p.write_text(
            json.dumps(
                {
                    "main_file": "run.py",
                    "requirements_file": "req.txt",
                    "venv_dir": ".envx",
                    "project_name": "X",
                    "entry_point": None,
                    "python_version": "3.12"
                },
                indent=2
            ),
            encoding="utf-8"
        )
        cfg = load_or_create_config(self.root)
        self.assertEqual(cfg["main_file"], "run.py")
        self.assertEqual(cfg["requirements_file"], "req.txt")
        self.assertEqual(cfg["venv_dir"], ".envx")

if __name__ == "__main__":
    unittest.main(verbosity=2)