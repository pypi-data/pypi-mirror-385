# -*- coding: utf-8 -*-
"""
Thin wrapper for `python -m reposmith.main`.
Always delegate to the unified CLI implemented in `reposmith.cli`.
"""

from __future__ import annotations

from .cli import main as cli_main


def main() -> int | None:
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main() or 0)
