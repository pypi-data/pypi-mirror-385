import unittest
import tempfile
import os
import json
from pathlib import Path

from reposmith.vscode_utils import create_vscode_files


class TestVSCodeUtils(unittest.TestCase):
    def setUp(self):
        """Set up temporary directory and project structure for testing."""
        self.tmp_ctx = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp_ctx.name) / "proj"
        self.root.mkdir()
        self.venv = self.root / ".venv"

    def tearDown(self):
        """Clean up temporary directory after tests."""
        self.tmp_ctx.cleanup()

    def _make_fake_interpreter(self):
        """Create a dummy Python interpreter file in the virtual environment."""
        if os.name == "nt":
            py = self.venv / "Scripts" / "python.exe"
        else:
            py = self.venv / "bin" / "python3"
        py.parent.mkdir(parents=True, exist_ok=True)
        py.write_text("", encoding="utf-8")
        return str(py)

    def _read_json(self, p: Path):
        """Read and parse a JSON file from a given path."""
        return json.loads(p.read_text(encoding="utf-8"))

    def test_create_vscode_files_with_existing_venv(self):
        """Test VSCode configuration creation when a virtual environment exists."""
        interp = self._make_fake_interpreter()
        create_vscode_files(self.root, self.venv, main_file="run.py", force=False)

        settings = self._read_json(self.root / ".vscode" / "settings.json")
        launch = self._read_json(self.root / ".vscode" / "launch.json")
        workspace = self._read_json(self.root / "project.code-workspace")

        self.assertEqual(settings.get("python.defaultInterpreterPath"), interp)
        self.assertEqual(workspace.get("settings", {}).get("python.defaultInterpreterPath"), interp)

        cfgs = launch.get("configurations", [])
        self.assertTrue(any(c.get("program") == "run.py" for c in cfgs))

    def test_create_vscode_files_without_venv_fallback(self):
        """Test fallback interpreter is used when virtual environment is missing."""
        create_vscode_files(self.root, self.venv, main_file="main.py", force=True)
        settings = self._read_json(self.root / ".vscode" / "settings.json")

        expected = "python.exe" if os.name == "nt" else "python3"
        self.assertEqual(settings.get("python.defaultInterpreterPath"), expected)

    def test_force_overwrites_and_backup(self):
        """Test that force overwrite creates a backup and updates the settings file."""
        vs = self.root / ".vscode"
        vs.mkdir(parents=True, exist_ok=True)
        settings = vs / "settings.json"
        settings.write_text("{\"old\": true}", encoding="utf-8")

        create_vscode_files(self.root, self.venv, main_file="main.py", force=True)

        bak = settings.with_suffix(settings.suffix + ".bak")
        self.assertTrue(bak.exists())
        self.assertEqual(bak.read_text(encoding="utf-8"), "{\"old\": true}")

        new_settings = self._read_json(settings)
        self.assertIn("python.defaultInterpreterPath", new_settings)


if __name__ == "__main__":
    unittest.main(verbosity=2)