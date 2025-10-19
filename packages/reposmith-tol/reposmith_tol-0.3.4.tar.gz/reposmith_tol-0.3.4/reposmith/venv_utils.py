from __future__ import annotations

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

def _venv_python(venv_dir: str | os.PathLike) -> str:
    """
    Return the Python executable path inside a virtual environment.

    Args:
        venv_dir (str | os.PathLike): Path to the virtual environment.

    Returns:
        str: Full path to the Python executable inside the venv.
    """
    v = str(venv_dir)
    return (
        os.path.join(v, "Scripts", "python.exe")
        if os.name == "nt"
        else os.path.join(v, "bin", "python")
    )

def create_virtualenv(venv_dir: str | os.PathLike, python_version: Optional[str] = None) -> str:
    """
    Create a virtual environment if it doesn't already exist.

    Args:
        venv_dir (str | os.PathLike): Path to the virtual environment directory.
        python_version (Optional[str]): Ignored in this implementation.

    Returns:
        str: "written" if created, "exists" if already present.
    """
    print("\n[2] Checking virtual environment")
    vdir = str(venv_dir)
    if not os.path.exists(vdir):
        print(f"Creating virtual environment at: {vdir}")
        subprocess.run([sys.executable, "-m", "venv", vdir], check=True)
        print("Virtual environment created.")
        return "written"
    else:
        print("Virtual environment already exists.")
        return "exists"

def _resolve_paths_for_install(
    venv_or_root: str | os.PathLike,
    requirements_path: Optional[str | os.PathLike],
) -> tuple[str, str]:
    """
    Resolve venv and requirements.txt paths based on input.

    Args:
        venv_or_root (str | os.PathLike): Either a venv path or project root.
        requirements_path (Optional[str | os.PathLike]): Path to requirements.txt.

    Returns:
        tuple[str, str]: Resolved venv path and requirements file path.
    """
    p = Path(venv_or_root)
    if p.name == ".venv":
        venv_dir = p
        root = p.parent
    else:
        root = p
        venv_dir = root / ".venv"

    req = Path(requirements_path) if requirements_path else root / "requirements.txt"
    return str(venv_dir), str(req)

def install_requirements(
    venv_dir_or_root: str | os.PathLike,
    requirements_path: Optional[str | os.PathLike] = None,
    *args,
    **kwargs,
) -> str:
    """
    Install packages from a requirements.txt file into the virtual environment.

    Supports different argument signatures for flexibility.

    Returns:
        str: Installation method used ("written(pip)", "written(uv)", or "skipped").
    """
    print("\n[4] Installing requirements")

    py_kw_names = ("python", "python_path", "py_exe", "interpreter", "exe", "python_exe")
    user_python = next((str(kwargs[k]) for k in py_kw_names if k in kwargs and kwargs[k]), None)

    if user_python is None and len(args) == 1:
        candidate = str(args[0])
        if os.path.basename(candidate).lower().startswith("python"):
            user_python = candidate
        else:
            requirements_path = candidate

    venv_dir, req_file = _resolve_paths_for_install(venv_dir_or_root, requirements_path)
    py = user_python or _venv_python(venv_dir)

    if not (os.path.exists(req_file) and os.path.getsize(req_file) > 0):
        print("requirements.txt is empty or missing, skipping install.")
        return "skipped"

    if shutil.which("uv"):
        subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        subprocess.run(["uv", "pip", "install", "-r", req_file, "--python", py], check=True)
        print("Packages installed via uv.")
        return "written(uv)"

    subprocess.run([py, "-m", "pip", "install", "-r", req_file, "--upgrade-strategy", "only-if-needed"], check=True)
    print("Packages installed via pip.")
    return "written(pip)"

def upgrade_pip(venv_dir: str | os.PathLike) -> str:
    """
    Upgrade pip inside the virtual environment.

    Args:
        venv_dir (str | os.PathLike): Path to the virtual environment.

    Returns:
        str: "written" after pip upgrade.
    """
    print("\n[5] Upgrading pip")
    py = _venv_python(venv_dir)
    subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)
    print("pip upgraded.")
    return "written"

def create_env_info(venv_dir: str | os.PathLike) -> str:
    """
    Create an environment info file with Python version and installed packages.

    Args:
        venv_dir (str | os.PathLike): Path to the virtual environment.

    Returns:
        str: "written" after file creation.
    """
    print("\n[6] Creating env-info.txt")
    info_path = os.path.join(
        os.path.abspath(os.path.join(str(venv_dir), os.pardir)),
        "env-info.txt",
    )
    py = _venv_python(venv_dir)
    with open(info_path, "w", encoding="utf-8") as f:
        subprocess.run([py, "--version"], stdout=f, check=True)
        f.write("\nInstalled packages:\n")
        subprocess.run([py, "-m", "pip", "freeze"], stdout=f, check=True)
    print(f"Environment info saved to {info_path}")
    return "written"