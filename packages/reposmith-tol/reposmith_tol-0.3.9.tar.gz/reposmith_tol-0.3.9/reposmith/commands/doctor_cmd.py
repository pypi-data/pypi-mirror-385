from __future__ import annotations
import os, sys, subprocess
from pathlib import Path

def _run_out(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return 0, out.decode("utf-8", errors="ignore").strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output.decode("utf-8", errors="ignore").strip()
    except FileNotFoundError:
        return 127, ""

def _read_pyproject_version(root: Path) -> str | None:
    py = root / "pyproject.toml"
    if not py.exists():
        return None
    text = py.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("version") and "=" in line:
            try:
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val:
                    return val
            except Exception:
                pass
    return None

def run_doctor(logger) -> int:
    root = Path(".").resolve()
    problems: list[str] = []

    logger.info("🩺 RepoSmith Doctor — Checking environment health...\n")
    logger.info("• Python:")
    logger.info("  - Executable: %s", sys.executable)
    logger.info("  - Version   : %s", sys.version.split()[0])

    rc, uv_out = _run_out(["uv", "--version"])
    if rc == 0: logger.info("• uv       : %s", uv_out)
    else:
        logger.warning("• uv       : not found on PATH (recommended)")
        problems.append("uv is not installed or not on PATH")

    rc, git_out = _run_out(["git", "--version"])
    if rc == 0: logger.info("• git      : %s", git_out)
    else:
        logger.warning("• git      : not found on PATH")
        problems.append("git is not installed or not on PATH")

    rc, pip_out = _run_out([sys.executable, "-m", "pip", "--version"])
    if rc == 0: logger.info("• pip      : %s", pip_out)
    else:
        logger.warning("• pip      : not found (unexpected on standard Python)")
        problems.append("pip not available")

    venv_dir = root / ".venv"
    if venv_dir.exists():
        interp = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        if interp.exists():
            rc, v_out = _run_out([str(interp), "--version"])
            logger.info("• .venv    : found%s", f" ({v_out})" if v_out else "")
        else:
            logger.warning("• .venv    : directory exists but interpreter not found")
            problems.append(".venv exists but python interpreter missing")
    else:
        logger.warning("• .venv    : not found (you can create it via 'reposmith init')")

    py_ver = _read_pyproject_version(root)
    if (root / "pyproject.toml").exists():
        logger.info("• pyproject.toml : %s", f"found (version={py_ver})" if py_ver else "found")
    else:
        logger.warning("• pyproject.toml : not found")

    req = root / "requirements.txt"
    if req.exists():
        txt = req.read_text(encoding="utf-8", errors="ignore").strip()
        logger.info("• requirements.txt : %s", "present (non-empty)" if txt else "present (empty)")
    else:
        logger.info("• requirements.txt : not found")

    if problems:
        logger.warning("\n⚠️  Environment issues detected:")
        for p in problems:
            logger.warning("  - %s", p)
        logger.warning("❌ Doctor finished with issues.")
        return 2

    logger.info("\n✅ Environment looks good. (More diagnostics coming soon)")
    return 0
