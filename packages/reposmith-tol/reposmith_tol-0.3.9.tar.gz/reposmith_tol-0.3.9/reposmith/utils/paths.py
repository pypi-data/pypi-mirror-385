from __future__ import annotations
import os
from pathlib import Path

def venv_python(root: Path) -> Path:
    venv = root / ".venv"
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
