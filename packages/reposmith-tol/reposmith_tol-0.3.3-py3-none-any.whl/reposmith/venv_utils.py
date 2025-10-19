# reposmith/venv_utils.py
from __future__ import annotations
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional

def _venv_python(venv_dir: str | os.PathLike) -> str:
    v = str(venv_dir)
    return (
        os.path.join(v, "Scripts", "python.exe")
        if os.name == "nt"
        else os.path.join(v, "bin", "python")
    )

def create_virtualenv(venv_dir: str | os.PathLike, python_version: Optional[str] = None) -> str:
    print("\n[2] Checking virtual environment")
    vdir = str(venv_dir)
    if not os.path.exists(vdir):
        print(f"Creating virtual environment at: {vdir}")
        subprocess.run([sys.executable, "-m", "venv", vdir], check=True)  # pragma: no cover
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
    يقبل إما مسار venv (…/.venv) أو جذر المشروع.
    يعيد (venv_dir, req_file)
    """
    p = Path(venv_or_root)
    # إذا أُعطي جذر المشروع، فافترض أن venv في .venv تحت الجذر
    if p.name == ".venv":
        venv_dir = p
        root = p.parent
    else:
        root = p
        venv_dir = root / ".venv"

    if requirements_path is None:
        req = root / "requirements.txt"
    else:
        req = Path(requirements_path)

    return (str(venv_dir), str(req))

def install_requirements(
    venv_dir_or_root: str | os.PathLike,
    requirements_path: Optional[str | os.PathLike] = None,
    *args,
    **kwargs,
) -> str:
    """
    يثبّت الحِزم من requirements.txt.

    توقيعات مدعومة:
      - install_requirements(root)
      - install_requirements(venv_dir, requirements_path)
      - install_requirements(root, python=<path>)  # أو python_path/py_exe/interpreter/exe/python_exe
      - install_requirements(root, <python_path>)  # positional
    """
    print("\n[4] Installing requirements")

    # استخرج مسار الـ Python إن مُرر بأسماء مفاتيح مختلفة
    py_kw_names = ("python", "python_path", "py_exe", "interpreter", "exe", "python_exe")
    user_python = None
    for k in py_kw_names:
        if k in kwargs and kwargs[k]:
            user_python = str(kwargs[k])
            break

    # دعم positional ثاني كمفسّر أو كـ requirements_path
    if user_python is None and len(args) == 1:
        candidate = str(args[0])
        base = os.path.basename(candidate).lower()
        if base.startswith("python"):
            user_python = candidate
        else:
            requirements_path = candidate

    venv_dir, req_file = _resolve_paths_for_install(venv_dir_or_root, requirements_path)
    py = user_python or _venv_python(venv_dir)

    # تَحقّق من req
    if not (os.path.exists(req_file) and os.path.getsize(req_file) > 0):
        print("requirements.txt is empty or missing, skipping install.")
        return "skipped"

    # لو uv متاح: استخدمه (فرع بيئي صعب تغطيته في CI المتعددة)
    if shutil.which("uv"):  # pragma: no cover
        subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)  # pragma: no cover
        subprocess.run(["uv", "pip", "install", "-r", req_file, "--python", py], check=True)  # pragma: no cover
        print("Packages installed via uv.")  # pragma: no cover
        return "written(uv)"  # pragma: no cover

    # مسار pip التقليدي
    subprocess.run([py, "-m", "pip", "install", "-r", req_file, "--upgrade-strategy", "only-if-needed"], check=True)
    print("Packages installed via pip.")
    return "written(pip)"

def upgrade_pip(venv_dir: str | os.PathLike) -> str:
    print("\n[5] Upgrading pip")
    py = _venv_python(venv_dir)
    subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip"], check=True)  # pragma: no cover
    print("pip upgraded.")  # pragma: no cover
    return "written"

def create_env_info(venv_dir: str | os.PathLike) -> str:
    print("\n[6] Creating env-info.txt")
    info_path = os.path.join(
        os.path.abspath(os.path.join(str(venv_dir), os.pardir)),
        "env-info.txt",
    )
    py = _venv_python(venv_dir)
    with open(info_path, "w", encoding="utf-8") as f:
        subprocess.run([py, "--version"], stdout=f, check=True)  # pragma: no cover
        f.write("\nInstalled packages:\n")
        subprocess.run([py, "-m", "pip", "freeze"], stdout=f, check=True)  # pragma: no cover
    print(f"Environment info saved to {info_path}")  # pragma: no cover
    return "written"
