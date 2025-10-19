"""
Thin entry point delegating to the real CLI in reposmith/cli.py
"""
from .cli import main as _cli_main

__all__ = ["main"]

def main():
    _cli_main()

if __name__ == "__main__":
    _cli_main()
