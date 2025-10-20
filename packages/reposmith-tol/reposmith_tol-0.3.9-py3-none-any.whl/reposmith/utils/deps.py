from __future__ import annotations
import subprocess, os, time
from pathlib import Path
from .paths import venv_python


def post_init_dependency_setup(root: Path, prefer_uv: bool = True) -> None:
    """
    Set up dependencies after project initialization.

    This function performs the following steps:
    - If a requirements.txt file is found, installs dependencies using uv or pip.
    - If no requirements.txt is found, ensures uv is installed and initializes pyproject.toml.

    Args:
        root (Path): The root directory of the project.
        prefer_uv (bool, optional): Whether to prefer uv over pip. Defaults to True.

    Returns:
        None

    Notes:
        - If no Python interpreter is found in the .venv directory, the function waits briefly and rechecks.
        - Exceptions during uv operations fall back to using pip.
    """
    
    py = venv_python(root)

    # ⏳ أضف انتظارًا قصيرًا بعد إنشاء البيئة لتفادي فشل الكشف في ويندوز
    if not py.exists():
        time.sleep(1.5)

    if not py.exists():
        print("[INFO] No Python interpreter in .venv — skipping dependency setup.")
        return

    req = root / "requirements.txt"
    pyproject = root / "pyproject.toml"

    def run(cmd: list[str]) -> None:
        print(">", " ".join(cmd))
        subprocess.run(cmd, cwd=root, check=True)

    # ✅ حالة وجود requirements.txt
    if req.exists() and req.stat().st_size > 0:
        if prefer_uv:
            print("[uv] requirements.txt detected → installing via uv...")
            try:
                run([str(py), "-m", "pip", "install", "--upgrade", "pip"])
                run([str(py), "-m", "pip", "install", "--upgrade", "uv"])
                run([str(py), "-m", "uv", "pip", "install", "-r", str(req)])
                return
            except Exception:
                print("[INFO] uv not available → falling back to pip")
        print("[pip] Installing from requirements.txt...")
        run([str(py), "-m", "pip", "install", "-r", str(req)])
        return

    # ✅ حالة عدم وجود requirements.txt
    if prefer_uv:
        print("[check] Ensuring uv is available inside the venv...")
        rc = subprocess.run(
            [str(py), "-m", "pip", "show", "uv"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ).returncode
        if rc != 0:
            print("[install] uv not found → installing now...")
            run([str(py), "-m", "pip", "install", "--upgrade", "uv"])
        else:
            print("[check] uv already installed inside .venv ✅")

        if not pyproject.exists():
            print("[uv] No requirements.txt found → initializing pyproject.toml via uv init...")
            try:
                run([str(py), "-m", "uv", "init"])
                print("[DONE] pyproject.toml created successfully ✅")
            except Exception as e:
                print(f"[WARN] uv init failed: {e}")
        else:
            print("[uv] pyproject.toml already exists — skipping uv init.")
    else:
        print("[INFO] No requirements.txt and prefer_uv=False — nothing to do.")
