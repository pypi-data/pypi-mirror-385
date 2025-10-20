# -*- coding: utf-8 -*-
"""
RepoSmith CLI Entry Point
-------------------------

Includes:
- Project initialization command (init)
- Brave Profile command (brave-profile --init)
- Doctor command (environment health check)

Usage examples:
    reposmith init --root . --entry run.py --no-venv --with-gitignore --with-license --with-vscode
    reposmith init --all
    reposmith brave-profile --init
    reposmith doctor
"""

from __future__ import annotations

import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

from .file_utils import create_app_file
from .ci_utils import ensure_github_actions_workflow
from .venv_utils import create_virtualenv, install_requirements
from .vscode_utils import create_vscode_files
from .gitignore_utils import create_gitignore
from .license_utils import create_license
from .env_manager import install_deps_with_uv
from .brave_profile import init_brave_profile
from .logging_utils import setup_logging


# =======================================================================
# Helpers
# =======================================================================

def _run_out(cmd: list[str]) -> tuple[int, str]:
    """Run command, return (returncode, stdout_str)."""
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


# =======================================================================
# Parser Construction
# =======================================================================

def build_parser() -> argparse.ArgumentParser:
    """Create and configure RepoSmith CLI commands."""
    parser = argparse.ArgumentParser(
        prog="reposmith",
        description="RepoSmith: Bootstrap Python projects (venv + uv + Brave)",
    )

    # Version
    try:
        ver = version("reposmith-tol")
    except PackageNotFoundError:
        ver = "0.0.0"
    parser.add_argument("--version", action="version", version=f"RepoSmith-tol {ver}")

    # Global options
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default: INFO",
    )
    parser.add_argument(
        "--no-emoji",
        action="store_true",
        help="Disable emojis in console output for maximum portability.",
    )

    # Hidden top-level acceptance of init-specific flags
    parser.add_argument("--entry", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--no-venv", action="store_true", help=argparse.SUPPRESS)

    sub = parser.add_subparsers(dest="cmd", required=True)

    # -------------------------------------------------------------------
    # init command
    # -------------------------------------------------------------------
    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    sc.add_argument("--force", action="store_true", help="Overwrite existing files if needed")

    # Official entry flags (hidden in help, موجودة للحفاظ على التوافق)
    sc.add_argument("--entry", type=str, default="run.py", help=argparse.SUPPRESS)
    sc.add_argument("--no-venv", action="store_true", help=argparse.SUPPRESS)

    # Optional add-ons
    sc.add_argument("--with-license", action="store_true", help="Include default LICENSE file (MIT).")
    sc.add_argument("--with-gitignore", action="store_true", help="Include default .gitignore file.")
    sc.add_argument("--with-vscode", action="store_true", help="Include VS Code settings.")
    sc.add_argument("--use-uv", action="store_true", help="Install dependencies using uv (faster).")
    sc.add_argument("--with-brave", action="store_true", help="Initialize Brave project profile after scaffolding.")

    # NEW: enable all recommended options at once
    sc.add_argument(
        "--all",
        action="store_true",
        help="Enable all recommended options (uv + brave + vscode + license + gitignore)"
    )

    # -------------------------------------------------------------------
    # brave-profile command
    # -------------------------------------------------------------------
    bp = sub.add_parser("brave-profile", help="Manage Brave dev profile scaffolding")
    bp.add_argument("--root", type=Path, default=Path.cwd(), help="Target project folder")
    bp.add_argument("--init", action="store_true", help="Initialize Brave dev profile in the project")

    # -------------------------------------------------------------------
    # doctor command (new)
    # -------------------------------------------------------------------
    sub.add_parser("doctor", help="Check environment health")

    return parser


# =======================================================================
# Doctor
# =======================================================================

def _cmd_doctor(logger) -> int:
    root = Path(".").resolve()
    problems: list[str] = []

    logger.info("🩺 RepoSmith Doctor — Checking environment health...\n")

    # Python
    logger.info("• Python:")
    logger.info("  - Executable: %s", sys.executable)
    logger.info("  - Version   : %s", sys.version.split()[0])

    # uv
    rc, uv_out = _run_out(["uv", "--version"])
    if rc == 0:
        logger.info("• uv       : %s", uv_out)
    else:
        logger.warning("• uv       : not found on PATH (recommended)")
        problems.append("uv is not installed or not on PATH")

    # git
    rc, git_out = _run_out(["git", "--version"])
    if rc == 0:
        logger.info("• git      : %s", git_out)
    else:
        logger.warning("• git      : not found on PATH")
        problems.append("git is not installed or not on PATH")

    # pip
    rc, pip_out = _run_out([sys.executable, "-m", "pip", "--version"])
    if rc == 0:
        logger.info("• pip      : %s", pip_out)
    else:
        logger.warning("• pip      : not found (unexpected on standard Python)")
        problems.append("pip not available")

    # .venv
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

    # pyproject / requirements
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


# =======================================================================
# CLI Entry Point
# =======================================================================

def main() -> int | None:
    """Main entry point for RepoSmith CLI."""
    parser = build_parser()
    args = parser.parse_args()

    logger = setup_logging(
        level=getattr(args, "log_level", "INFO"),
        no_emoji=getattr(args, "no_emoji", False),
    )

    # ---------------------------
    # INIT
    # ---------------------------
    if args.cmd == "init":
        root: Path = args.root
        root.mkdir(parents=True, exist_ok=True)
        logger.info("🚀 Initializing project at: %s", root)

        # Expand --all
        if getattr(args, "all", False):
            args.use_uv = True
            args.with_brave = True
            args.with_vscode = True
            args.with_license = True
            args.with_gitignore = True

        # Normalize entry and no_venv (works whether given top-level or subparser)
        entry_name = args.entry if (args.entry not in (None, "")) else "run.py"
        entry_path = root / entry_name
        no_venv = bool(getattr(args, "no_venv", False))

        # 1) Create virtual environment (unless suppressed)
        venv_dir = root / ".venv"
        if not no_venv:
            create_virtualenv(venv_dir)
        else:
            logger.info("Skipping virtual environment creation (--no-venv).")

        # 2) Install dependencies (uv or pip) — only if venv is created
        if not no_venv:
            req = root / "requirements.txt"
            if args.use_uv:
                install_deps_with_uv(root)
            else:
                if req.exists() and req.stat().st_size > 0:
                    install_requirements(venv_dir, str(req))
                else:
                    logger.debug("No requirements.txt found (or empty) — skipping install.")

        # 3) Create entry Python file at the requested path
        create_app_file(entry_path, force=args.force)
        logger.info("[entry] %s created at: %s", entry_name, entry_path)

        # 4) Optional add-ons
        if args.with_vscode:
            create_vscode_files(root, venv_dir, main_file=str(entry_path), force=args.force)
        if args.with_gitignore:
            create_gitignore(root, force=args.force)
        if args.with_license:
            create_license(root, license_type="MIT", owner_name="Tamer", force=args.force)

        # 5) CI workflow (kept as in your current file)
        ensure_github_actions_workflow(root)

        # 6) Brave integration
        if args.with_brave:
            init_brave_profile(root)
            logger.info("🦁 Brave Dev Profile initialized successfully.")

        logger.info("✅ Project initialized successfully at: %s", root)
        return 0

    # ---------------------------
    # BRAVE PROFILE
    # ---------------------------
    if args.cmd == "brave-profile" and args.init:
        init_brave_profile(args.root)
        logger.info("🦁 Brave Dev Profile ready to use.")
        return 0

    # ---------------------------
    # DOCTOR
    # ---------------------------
    if args.cmd == "doctor":
        return _cmd_doctor(logger)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
