from __future__ import annotations

import json
import os
from pathlib import Path

from .core.fs import write_file

def _venv_python_path(venv_dir: Path) -> str:
    """
    Return the Python interpreter path for Visual Studio Code.

    Args:
        venv_dir (Path): The directory of the virtual environment.

    Returns:
        str: The path to the Python interpreter.
             Falls back to system default if not found in venv.
    """
    if os.name == "nt":
        candidate = venv_dir / "Scripts" / "python.exe"
        return str(candidate) if candidate.exists() else "python.exe"
    else:
        candidate = venv_dir / "bin" / "python3"
        return str(candidate) if candidate.exists() else "python3"

def create_vscode_files(
    root_dir: Path,
    venv_dir: Path,
    *,
    main_file: str = "main.py",
    force: bool = False,
) -> None:
    """
    Safely create/update VS Code configuration files for a project.

    Generates:
        - .vscode/settings.json: Python interpreter from venv.
        - .vscode/launch.json: Debug config for main script.
        - project.code-workspace: Workspace with Python settings.

    Args:
        root_dir (Path): Project root directory.
        venv_dir (Path): Path to the virtual environment.
        main_file (str, optional): Main script name. Defaults to "main.py".
        force (bool, optional): Overwrite files if True. Defaults to False.
    """
    root = Path(root_dir)
    vscode = root / ".vscode"
    vscode.mkdir(parents=True, exist_ok=True)

    py_path = _venv_python_path(venv_dir)

    # settings.json
    settings = {
        "python.defaultInterpreterPath": py_path,
        "python.analysis.autoImportCompletions": True,
        "terminal.integrated.env.windows": {},
    }
    write_file(
        vscode / "settings.json",
        json.dumps(settings, indent=2),
        force=force,
        backup=True,
    )

    # launch.json
    launch = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": f"Python: {main_file}",
                "type": "python",
                "request": "launch",
                "program": main_file,
                "console": "integratedTerminal",
            }
        ],
    }
    write_file(
        vscode / "launch.json",
        json.dumps(launch, indent=2),
        force=force,
        backup=True,
    )

    # project.code-workspace
    workspace = {
        "folders": [{"path": "."}],
        "settings": {"python.defaultInterpreterPath": py_path},
    }
    write_file(
        root / "project.code-workspace",
        json.dumps(workspace, indent=2),
        force=force,
        backup=True,
    )

    print("VS Code files updated: settings.json, launch.json, project.code-workspace")
