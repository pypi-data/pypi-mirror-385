import os
import sys
import subprocess
import tempfile
from pathlib import Path
import shlex
import re

def _help_text_for(subcmd: str) -> str:
    """Return the help text for a specific CLI subcommand.

    Args:
        subcmd (str): The subcommand to retrieve help for.

    Returns:
        str: The help message text for the subcommand.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "reposmith.main", subcmd, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return proc.stdout or ""

def _is_flag_supported(help_text: str, flag: str) -> bool:
    """Check if a specific flag is present in the help text.

    Args:
        help_text (str): The CLI help message.
        flag (str): The flag to search for.

    Returns:
        bool: True if the flag is supported, False otherwise.
    """
    pat = r"(?:^|\s)" + re.escape(flag) + r"(?:\s|,|$)"
    return re.search(pat, help_text) is not None

class TestCLISmoke:
    """Smoke tests for the reposmith CLI."""

    def _run(self, args, cwd: Path):
        """Run a CLI command with given arguments and working directory.

        Args:
            args (list): Arguments to pass to the CLI.
            cwd (Path): Directory to run the command in.

        Returns:
            CompletedProcess: Result of subprocess.run.
        """
        return subprocess.run(
            [sys.executable, "-m", "reposmith.main"] + args,
            cwd=cwd,
            check=True,
        )

    def test_init_smoke_adaptive(self):
        """Test 'init' command with available flags to ensure it runs successfully and creates expected files."""
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "proj"
            proj.mkdir(parents=True, exist_ok=True)

            help_text = _help_text_for("init")
            args = ["init"]

            if _is_flag_supported(help_text, "--entry"):
                args += ["--entry", "run.py"]
            if _is_flag_supported(help_text, "--with-gitignore"):
                args.append("--with-gitignore")
            if _is_flag_supported(help_text, "--with-license"):
                args += ["--with-license"]
                if _is_flag_supported(help_text, "--author"):
                    args += ["--author", "TestUser"]
                if _is_flag_supported(help_text, "--year"):
                    args += ["--year", "2099"]
            if _is_flag_supported(help_text, "--with-vscode"):
                args.append("--with-vscode")
            if _is_flag_supported(help_text, "--no-venv"):
                args.append("--no-venv")

            self._run(args, cwd=proj)

            if "--entry" in args:
                assert (proj / "run.py").exists()
            if "--with-gitignore" in args:
                assert (proj / ".gitignore").exists()
            if "--with-license" in args:
                assert (proj / "LICENSE").exists()
            if "--with-vscode" in args:
                assert (proj / ".vscode").exists()