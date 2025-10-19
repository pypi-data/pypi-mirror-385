from pathlib import Path
import subprocess
import sys

def _run(cmd, cwd=None):
    print("[uv]", " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)

def install_deps_with_uv(root: Path):
    # تأكيد uv
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
