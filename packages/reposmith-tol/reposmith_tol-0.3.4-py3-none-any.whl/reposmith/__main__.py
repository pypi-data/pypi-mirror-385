# -*- coding: utf-8 -*-
"""
Entry point for `python -m reposmith`.
Delegates to the same unified CLI as other entry points.
"""

from __future__ import annotations

from .cli import main as cli_main


def main() -> int | None:
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main() or 0)
