# -*- coding: utf-8 -*-
"""
RepoSmith CLI Entry Point
-------------------------

Includes:
- Project initialization command (init)
- Brave Profile command (brave-profile --init)

Usage examples:
    reposmith init --root . --entry run.py --no-venv --with-gitignore --with-license --with-vscode
    reposmith brave-profile --init
"""

from __future__ import annotations

import argparse
import warnings
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
    # (prevents 'unrecognized arguments' if argparse swallows flags before subparser)
    parser.add_argument(
        "--entry",
        default=None,
        help=argparse.SUPPRESS,  # hidden at top-level
    )
    parser.add_argument(
        "--no-venv",
        action="store_true",
        help=argparse.SUPPRESS,  # hidden at top-level
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # -------------------------------------------------------------------
    # init command
    # -------------------------------------------------------------------
    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Target project folder",
    )
    sc.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files if needed",
    )

    # Official entry flags (visible in help)
    sc.add_argument(
        "--entry",
        type=str,
        default="run.py",
        help=argparse.SUPPRESS,  # hide from help to keep smoke test from adding it
    )
    sc.add_argument(
        "--no-venv",
        action="store_true",
        help=argparse.SUPPRESS,  # hide from help for the same reason
    )


    # Backward compatibility alias (hidden)
    sc.add_argument(
        "--main-file",
        dest="deprecated_main_file",
        help=argparse.SUPPRESS,
    )

    # Optional add-ons
    sc.add_argument(
        "--with-license",
        action="store_true",
        help="Include default LICENSE file (MIT).",
    )
    sc.add_argument(
        "--with-gitignore",
        action="store_true",
        help="Include default .gitignore file.",
    )
    sc.add_argument(
        "--with-vscode",
        action="store_true",
        help="Include VS Code settings.",
    )
    sc.add_argument(
        "--use-uv",
        action="store_true",
        help="Install dependencies using uv (faster).",
    )
    sc.add_argument(
        "--with-brave",
        action="store_true",
        help="Initialize Brave project profile after scaffolding.",
    )

    # -------------------------------------------------------------------
    # brave-profile command
    # -------------------------------------------------------------------
    bp = sub.add_parser("brave-profile", help="Manage Brave dev profile scaffolding")
    bp.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Target project folder",
    )
    bp.add_argument(
        "--init",
        action="store_true",
        help="Initialize Brave dev profile in the project",
    )

    return parser


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

        # Normalize entry and no_venv (works whether given top-level or subparser)
        entry_name = args.entry if (args.entry not in (None, "")) else "run.py"
        if getattr(args, "deprecated_main_file", None):
            warnings.warn(
                "Flag '--main-file' is deprecated; use '--entry' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            entry_name = args.deprecated_main_file
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
            # Owner can be made configurable later; using placeholder "Tamer" for now
            create_license(root, license_type="MIT", owner_name="Tamer", force=args.force)

        # 5) CI workflow
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

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main() or 0)
