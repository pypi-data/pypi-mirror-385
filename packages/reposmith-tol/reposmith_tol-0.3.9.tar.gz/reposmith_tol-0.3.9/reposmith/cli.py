# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

from .logging_utils import setup_logging
from .commands.init_cmd import run_init
from .commands.doctor_cmd import run_doctor
# تم حذف: from .commands.brave_cmd import run_brave

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reposmith",
        description="RepoSmith: Bootstrap Python projects (venv + uv)",
    )
    try:
        ver = version("reposmith-tol")
    except PackageNotFoundError:
        ver = "0.0.0"
    parser.add_argument("--version", action="version", version=f"RepoSmith-tol {ver}")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--no-emoji", action="store_true")

    # لقبول هذه القيم حتى لو جاءت من المستوى الأعلى
    parser.add_argument("--entry", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--no-venv", action="store_true", help=argparse.SUPPRESS)

    sub = parser.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("init", help="Initialize a new project")
    sc.add_argument("--root", type=Path, default=Path.cwd())
    sc.add_argument("--force", action="store_true")
    sc.add_argument("--entry", type=str, default="run.py", help=argparse.SUPPRESS)
    sc.add_argument("--no-venv", action="store_true", help=argparse.SUPPRESS)
    sc.add_argument("--with-license", action="store_true")
    sc.add_argument("--with-gitignore", action="store_true")
    sc.add_argument("--with-vscode", action="store_true")
    sc.add_argument("--use-uv", action="store_true")
    # تم حذف: sc.add_argument("--with-brave", action="store_true")
    sc.add_argument("--all", action="store_true")

    # تم حذف الأمر الفرعي بالكامل: brave-profile

    sub.add_parser("doctor", help="Check environment health")
    return parser

def main() -> int | None:
    parser = build_parser()
    args = parser.parse_args()
    logger = setup_logging(level=getattr(args, "log_level", "INFO"),
                           no_emoji=getattr(args, "no_emoji", False))

    if args.cmd == "init":
        return run_init(args, logger)
    # تم حذف مسار brave-profile
    if args.cmd == "doctor":
        return run_doctor(logger)

    parser.print_help()
    return 0

if __name__ == "__main__":
    from .cli import main as cli_main  # للاتساق مع نقاط الدخول الأخرى
    raise SystemExit(cli_main() or 0)
