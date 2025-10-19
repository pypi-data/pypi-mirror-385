from pathlib import Path
import subprocess
import sys

def _run(cmd: list[str], cwd: Path | None = None) -> None:
    """
    Print and execute a shell command using subprocess.

    Args:
        cmd (list[str]): Command to execute.
        cwd (Path | None): Optional working directory for the command.
    """
    print("[uv]", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)

def install_deps_with_uv(root: Path) -> None:
    """
    Ensure the 'uv' tool is available and install dependencies using it.

    Args:
        root (Path): Project root directory containing dependency files.

    Notes:
        - Tries to use 'pyproject.toml' with `uv sync` if present.
        - Falls back to 'requirements.txt' if available.
        - Skips installation if neither file is found.
    """
    try:
        _run([sys.executable, "-m", "uv", "--version"], cwd=root)
    except subprocess.CalledProcessError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uv"])

    pyproject = root / "pyproject.toml"
    req = root / "requirements.txt"

    if pyproject.exists():
        _run([sys.executable, "-m", "uv", "sync"], cwd=root)
    elif req.exists():
        _run([sys.executable, "-m", "uv", "pip", "install", "-r", "requirements.txt"], cwd=root)
    else:
        print("[uv] No dependency file found; skipping.")