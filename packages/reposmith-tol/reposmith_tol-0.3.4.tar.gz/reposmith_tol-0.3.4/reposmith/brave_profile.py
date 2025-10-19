from __future__ import annotations

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Embedded PowerShell scripts and default configuration content
# ---------------------------------------------------------------------------

LAUNCH_BRAVE_PS1 = r'''
<#
.SYNOPSIS
  Launch Brave with a per-project profile and open selected local dev URLs.

.DESCRIPTION
  - Detects common local dev ports (3000, 5173, 8000, 8080, 5000, ...).
  - Reads extra URLs from .brave-profile.conf (one URL per line).
  - Shows an interactive selection menu (or use -Auto / -NoTabs / -Ports).
#>

param(
  [string]$Name = "Brave (Project)",
  [string]$ProfileDir = ".brave-profile",
  [string]$Ports = "",
  [switch]$Auto,
  [switch]$NoTabs
)

# ---- Helpers ---------------------------------------------------------------

function Resolve-Brave {
  $paths = @(
    "$Env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$Env:ProgramFiles(x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
  )
  foreach ($p in $paths) {
    if (Test-Path $p) { return $p }
  }
  throw "Brave not found in Program Files."
}

function Test-PortOpen {
  param([int]$Port)
  try {
    return (Test-NetConnection -ComputerName 'localhost' -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet)
  }
  catch {
    return $false
  }
}

$PORT_LABELS = @{
  3000 = "Next.js / React"
  5173 = "Vite"
  8000 = "FastAPI / Uvicorn / http.server"
  8080 = "Generic dev / Webpack / Serve"
  5000 = "Flask"
  4200 = "Angular"
  5500 = "Live Server"
  8001 = "Service"
  8002 = "Service"
  8888 = "Jupyter"
  7000 = "Service"
  9000 = "Service"
}

function Get-PortFromUrl {
  param([string]$Url)
  try { return [int]([uri]$Url).Port } catch { return $null }
}

function Format-UrlWithLabel {
  param([string]$Url)
  $p = Get-PortFromUrl -Url $Url
  if ($p -and $PORT_LABELS.ContainsKey($p)) {
    return "$Url — $($PORT_LABELS[$p])"
  }
  return $Url
}

function Detect-OpenDevPorts {
  $default = @(3000,5173,8000,8080,5000,4200,5500,7000,9000,8001,8002,8888)
  $extra = @()
  if ($Ports) {
    $Ports.Split(',') | ForEach-Object {
      if ($_ -match '^\s*\d+\s*$') { $extra += [int]$_ }
    }
  }
  $scan = ($default + $extra) | Select-Object -Unique | Sort-Object
  $open = foreach ($p in $scan) {
    if (Test-PortOpen $p) { "http://localhost:$p" }
  }
  return ,$open
}

function Read-ExtraUrlsFromConf {
  $conf = Join-Path (Get-Location) ".brave-profile.conf"
  if (Test-Path $conf) {
    Get-Content $conf | ForEach-Object {
      $u = $_.Trim()
      if ($u -and -not $u.StartsWith('#')) { $u }
    }
  }
}

function Pick-UrlsInteractive {
  param([string[]]$OpenUrls, [string[]]$FromConf)
  $choices = @()

  if ($OpenUrls.Count -gt 0) {
    $choices += $OpenUrls | ForEach-Object { "[RUNNING] " + (Format-UrlWithLabel $_) }
  }
  if ($FromConf.Count -gt 0) {
    $choices += $FromConf | ForEach-Object { "[CONF]    " + (Format-UrlWithLabel $_) }
  }

  if ($choices.Count -eq 0) {
    Write-Host "No running dev servers detected. You can still open Brave profile. (`-NoTabs` to suppress tabs.)" -ForegroundColor Yellow
    return @()
  }

  Write-Host ""
  Write-Host "Select URLs to open (comma-separated indices) or press Enter for all:" -ForegroundColor Cyan
  for ($i=0; $i -lt $choices.Count; $i++) {
    Write-Host ("[{0}] {1}" -f $i, $choices[$i])
  }
  Write-Host ""
  $inputSel = Read-Host "Your choice"

  if ([string]::IsNullOrWhiteSpace($inputSel)) {
    return $OpenUrls + $FromConf | Select-Object -Unique
  }

  $indices = $inputSel -split '[,\s]+' |
    Where-Object { $_ -match '^\d+$' } |
    ForEach-Object { [int]$_ } |
    Where-Object { $_ -ge 0 -and $_ -lt $choices.Count }

  $picked = foreach ($ix in $indices) {
    $raw = $choices[$ix] -replace '^\[(RUNNING|CONF)\]\s+',''
    $raw -replace '\s—\s.*$',''
  }
  return $picked | Select-Object -Unique
}

$brave = Resolve-Brave
$profilePath = Join-Path (Get-Location) $ProfileDir
New-Item -ItemType Directory -Force -Path $profilePath | Out-Null

$urlsRunning = Detect-OpenDevPorts
$urlsConf    = Read-ExtraUrlsFromConf | Where-Object { $_ -match '^https?://' }

if ($NoTabs) {
  $urlsToOpen = @()
}
elseif ($Auto) {
  $urlsToOpen = ($urlsRunning + $urlsConf) | Select-Object -Unique
}
else {
  $urlsToOpen = Pick-UrlsInteractive -OpenUrls $urlsRunning -FromConf $urlsConf
}

$argList = @("--user-data-dir=\"$profilePath\"")
foreach ($u in $urlsToOpen) { $argList += @("--new-tab", $u) }

Start-Process -FilePath $brave -ArgumentList $argList
Write-Host "Brave launched with profile: $profilePath" -ForegroundColor Green
if ($urlsToOpen.Count -gt 0) {
  Write-Host ("Opened tabs:`n - " + ($urlsToOpen -join "`n - "))
} else {
  Write-Host "No tabs opened (profile only). Use -Auto or add URLs to .brave-profile.conf" -ForegroundColor Yellow
}
'''

MAKE_SHORTCUT_PS1 = r'''
param(
  [string]$Name = "Brave (Project)",
  [string]$ProfileDir = ".brave-profile"
)
$brave = "${env:ProgramFiles}\BraveSoftware\Brave-Browser\Application\brave.exe"
if (-not (Test-Path $brave)) {
  $brave = "${env:ProgramFiles(x86)}\BraveSoftware\Brave-Browser\Application\brave.exe"
}
if (-not (Test-Path $brave)) { Write-Error "Brave not found."; exit 1 }

$target = "`"$brave`" --user-data-dir=`"$PWD\$ProfileDir`""
$WScriptShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WScriptShell.CreateShortcut("$Desktop\$Name.lnk")
$Shortcut.TargetPath = $brave
$Shortcut.Arguments = "--user-data-dir=`"$PWD\$ProfileDir`""
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop."
'''

CLEANUP_PS1 = r'''
param([string]$ProfileDir = ".brave-profile")
$path = Join-Path (Get-Location) $ProfileDir
if (Test-Path $path) {
  Remove-Item -Recurse -Force $path
  Write-Host "Removed $path"
} else {
  Write-Host "Nothing to remove at $path"
}
'''

DEFAULT_CONF = """# Lines starting with # are ignored.
# Put any URLs you want Brave to open with this project profile, one per line.
# Examples:
# http://127.0.0.1:8000
# http://localhost:3000
# http://localhost:5173
"""

# ---------------------------------------------------------------------------
# Python functions
# ---------------------------------------------------------------------------

def init_brave_profile(root: Path) -> None:
    """Scaffold per-project Brave profile and tools into the specified root directory.

    Args:
        root (Path): The project root directory to initialize.
    """
    root = Path(root)
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)

    prof = root / ".brave-profile"
    prof.mkdir(exist_ok=True)

    (prof / "README.txt").write_text(
        "Per-project Brave profile. Launch Brave with --user-data-dir pointing here.\n",
        encoding="utf-8"
    )

    (prof / "prefs.json").write_text(
        json.dumps({"homepage": "about:blank", "first_run_tabs": []}, indent=2),
        encoding="utf-8"
    )

    (root / ".brave-profile.conf").write_text(DEFAULT_CONF, encoding="utf-8")

    (tools / "launch_brave.ps1").write_text(LAUNCH_BRAVE_PS1.lstrip(), encoding="utf-8")
    (tools / "make_brave_shortcut.ps1").write_text(MAKE_SHORTCUT_PS1.lstrip(), encoding="utf-8")
    (tools / "cleanup_brave_profile.ps1").write_text(CLEANUP_PS1.lstrip(), encoding="utf-8")

def add_vscode_task(root: Path) -> None:
    """Append Brave-related launch tasks to VS Code tasks.json configuration.

    Args:
        root (Path): The root directory of the project.
    """
    vscode = root / ".vscode"
    vscode.mkdir(exist_ok=True)
    tasks = vscode / "tasks.json"

    task_obj = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Brave: Launch project profile",
                "type": "shell",
                "command": "pwsh",
                "args": ["-File", "${workspaceFolder}/tools/launch_brave.ps1"],
                "problemMatcher": []
            },
            {
                "label": "Brave: Launch (Auto)",
                "type": "shell",
                "command": "pwsh",
                "args": ["-File", "${workspaceFolder}/tools/launch_brave.ps1", "-Auto"],
                "problemMatcher": []
            },
            {
                "label": "Brave: Launch (No Tabs)",
                "type": "shell",
                "command": "pwsh",
                "args": ["-File", "${workspaceFolder}/tools/launch_brave.ps1", "-NoTabs"],
                "problemMatcher": []
            }
        ]
    }

    if tasks.exists():
        try:
            existing = json.loads(tasks.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                ex_tasks = existing.setdefault("tasks", [])
                existing_labels = {t.get("label") for t in ex_tasks if isinstance(t, dict)}
                for t in task_obj["tasks"]:
                    if t["label"] not in existing_labels:
                        ex_tasks.append(t)
                tasks.write_text(json.dumps(existing, indent=2), encoding="utf-8")
                return
        except Exception:
            pass

    tasks.write_text(json.dumps(task_obj, indent=2), encoding="utf-8")

def setup_brave(root: Path) -> None:
    """Set up Brave profile integration including tools and VS Code tasks.

    Args:
        root (Path): The root directory to configure.
    """
    init_brave_profile(root)
    add_vscode_task(root)

__all__ = ["setup_brave", "init_brave_profile", "add_vscode_task"]
