# reposmith/brave_profile.py
# -*- coding: utf-8 -*-
"""
Brave per-project profile scaffolding for RepoSmith.

Installs:
- tools/launch_brave.ps1
- tools/make_brave_shortcut.ps1
- tools/cleanup_brave_profile.ps1
- .brave-profile.conf (optional defaults)
- .vscode/tasks.json (adds a Task to launch Brave)
- .gitignore entry for .brave-profile/

Usage (from CLI integration):
    reposmith brave-profile --init
"""

from pathlib import Path
import json

# -------------------------
# Template file contents
# -------------------------

TEMPLATE_FILES = {
    "tools/launch_brave.ps1": r"""param(
  [string]$ProfileDir = "$PSScriptRoot/../.brave-profile",
  [string]$BraveExe   = "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
  [string]$StartUrl   = "",
  [string[]]$Urls     = @(),
  [string[]]$MoreArgs = @()
)

# 1) Resolve paths and ensure profile dir
$ProjectRoot = (Resolve-Path "$PSScriptRoot/..").Path
$ResolvedProfile = (Resolve-Path $ProfileDir -ErrorAction SilentlyContinue)
if (-not $ResolvedProfile) {
  $ResolvedProfile = Join-Path $ProjectRoot ".brave-profile"
  New-Item -ItemType Directory -Path $ResolvedProfile | Out-Null
}

# 2) Optional: read .brave-profile.conf (KEY=VALUE)
$ConfPath = Join-Path $ProjectRoot ".brave-profile.conf"
if (Test-Path $ConfPath) {
  (Get-Content $ConfPath | Where-Object { $_ -match '=' -and $_ -notmatch '^\s*#' }) | ForEach-Object {
    $k,$v = $_.Split('=',2); $k=$k.Trim(); $v=$v.Trim()
    if ($k -ieq "StartUrl" -and -not $StartUrl) { $StartUrl = $v }
    if ($k -ieq "Urls" -and $Urls.Count -eq 0)   { $Urls = $v.Split(',').ForEach({ $_.Trim() }) }
  }
}

# 3) Default StartUrl if not provided
if (-not $StartUrl) { $StartUrl = "http://127.0.0.1:8000" }

# 4) Useful dev flags (feel free to edit/remove)
$flags = @(
  "--user-data-dir=`"$ResolvedProfile`"",
  "--profile-directory=`"Default`"",
  "--disable-features=RendererCodeIntegrity",
  "--disable-background-networking",
  "--no-first-run",
  "--disk-cache-size=0"
) + $MoreArgs

# 5) Compose URLs to open
$OpenList = @()
if ($StartUrl) { $OpenList += $StartUrl }
if ($Urls)     { $OpenList += $Urls }

# 6) Launch Brave
Start-Process -FilePath $BraveExe -ArgumentList ($flags + $OpenList)
""",

    "tools/make_brave_shortcut.ps1": r"""param(
  [string]$ShortcutName = "$(Split-Path (Resolve-Path "$PSScriptRoot/..").Path -Leaf) - Brave Dev.lnk",
  [string]$Desktop      = [Environment]::GetFolderPath("Desktop"),
  [string]$Launcher     = "$PSScriptRoot\launch_brave.ps1"
)

$WScript  = New-Object -ComObject WScript.Shell
$Shortcut = $WScript.CreateShortcut((Join-Path $Desktop $ShortcutName))
$Shortcut.TargetPath       = "pwsh.exe"
$Shortcut.Arguments        = "-NoLogo -NoProfile -ExecutionPolicy Bypass -File `"$Launcher`""
$Shortcut.WorkingDirectory = (Resolve-Path "$PSScriptRoot/..").Path
$Shortcut.IconLocation     = "C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe,0"
$Shortcut.Save()
"Shortcut created: $($Shortcut.FullName)"
""",

    "tools/cleanup_brave_profile.ps1": r"""param([string]$ProfileDir = "$PSScriptRoot/../.brave-profile")

$ResolvedProfile = (Resolve-Path $ProfileDir).Path
$trash = @("Cache","Code Cache","GPUCache","DawnCache","GrShaderCache","ShaderCache")
foreach ($d in $trash) {
  $p = Join-Path $ResolvedProfile $d
  if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
"Cleaned caches in: $ResolvedProfile"
""",

    ".brave-profile.conf": r"""# Default dev URLs for this project
StartUrl=http://127.0.0.1:8000
Urls=http://localhost:3000,http://localhost:5173
""",

    # Special handling below for .vscode/tasks.json and .gitignore
    ".vscode/tasks.json": None,
    ".gitignore": None,
}

TASKS_JSON_SNIPPET = {
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Brave: Launch project profile",
            "type": "shell",
            "command": "pwsh",
            "args": [
                "-NoLogo",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", "${workspaceFolder}/tools/launch_brave.ps1"
            ],
            "problemMatcher": []
        }
    ]
}

# -------------------------
# Helpers
# -------------------------

def ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def write_text(p: Path, content: str) -> None:
    ensure_parent(p)
    p.write_text(content, encoding="utf-8")

def append_gitignore(root: Path) -> None:
    gi = root / ".gitignore"
    line = ".brave-profile/\n"
    if gi.exists():
        txt = gi.read_text(encoding="utf-8")
        if ".brave-profile/" not in txt:
            gi.write_text(txt.rstrip() + "\n" + line, encoding="utf-8")
    else:
        gi.write_text(line, encoding="utf-8")

def merge_tasks_json(root: Path) -> None:
    vs = root / ".vscode"
    vs.mkdir(parents=True, exist_ok=True)
    tj = vs / "tasks.json"
    if tj.exists():
        try:
            data = json.loads(tj.read_text(encoding="utf-8") or "{}")
        except Exception:
            data = TASKS_JSON_SNIPPET
        else:
            tasks = data.get("tasks", [])
            labels = {t.get("label") for t in tasks if isinstance(t, dict)}
            if "Brave: Launch project profile" not in labels:
                tasks.append(TASKS_JSON_SNIPPET["tasks"][0])
                data["tasks"] = tasks
        tj.write_text(json.dumps(data, indent=2), encoding="utf-8")
    else:
        tj.write_text(json.dumps(TASKS_JSON_SNIPPET, indent=2), encoding="utf-8")

# -------------------------
# Public API
# -------------------------

def init_brave_profile(root: Path) -> None:
    """
    Write/merge all scaffolding files into 'root'.
    """
    root = Path(root)

    for rel, content in TEMPLATE_FILES.items():
        target = root / rel
        if rel == ".vscode/tasks.json":
            merge_tasks_json(root)
        elif rel == ".gitignore":
            append_gitignore(root)
        else:
            if content is None:
                continue
            write_text(target, content)

    # Ensure tools directory exists even if scripts already written
    (root / "tools").mkdir(parents=True, exist_ok=True)

    print(f"✅ Brave project profile scaffolding installed in: {root}")

__all__ = ["init_brave_profile"]
