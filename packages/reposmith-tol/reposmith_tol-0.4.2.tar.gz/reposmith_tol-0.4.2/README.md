# ⚡ RepoSmith — Next-Gen Python Project Bootstrapper

[![PyPI](https://img.shields.io/pypi/v/reposmith-tol?style=flat-square&logo=pypi)](https://pypi.org/project/reposmith-tol/)
![Python](https://img.shields.io/pypi/pyversions/reposmith-tol?style=flat-square)
![License](https://img.shields.io/github/license/TamerOnLine/reposmith-init?style=flat-square)
![CI](https://img.shields.io/github/actions/workflow/status/TamerOnLine/reposmith-init/ci.yml?branch=main&label=CI&logo=github&style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/reposmith-tol?style=flat-square)
[![Sponsor](https://img.shields.io/badge/Sponsor-💖-pink?style=flat-square)](https://github.com/sponsors/TamerOnLine)



> **RepoSmith-tol** builds complete, ready-to-code Python projects —  
> virtual env, dependencies with `uv`, VS Code setup, CI, and automation — all in **one command**.

---

## ✨ Features

| Category | What It Does |
|-----------|--------------|
| 🧱 **Scaffolding** | Generates `main.py`, `.gitignore`, `LICENSE`, and VS Code workspace automatically |
| ⚙️ **Virtualenv** | Creates `.venv` and links it to VS Code |
| ⚡ **Dependency Install** | Installs packages via **[`uv`](https://github.com/astral-sh/uv)** (10× faster than pip) |
| 💻 **VS Code Integration** | Auto-creates `settings.json`, `launch.json`, and `tasks.json` |
| 🧪 **CI Workflow** | Generates `.github/workflows/ci.yml` for tests & linting |
| 🔒 **Idempotent & Safe** | Re-runs cleanly, only overwriting with `--force` |
| 🧾 **License Automation** | Adds MIT license with owner/year metadata |
| 🧰 **Cross-Platform** | Works on Windows / Linux / macOS |

---

## ⚡ Quick Start

### 1️⃣ Install
```powershell
py -m pip install --upgrade reposmith-tol
```

### 2️⃣ Create a new project
```powershell
reposmith init --root demo --use-uv --with-gitignore --with-license --with-vscode --force
```

### 3️⃣ Open & Run
```powershell
code demo
```

---

## 🧠 CLI Reference

| Flag | Description |
|------|--------------|
| `--force` | Overwrite existing files (creates `.bak` backups) |
| `--use-uv` | Install dependencies using **uv** instead of pip |
| `--with-vscode` | Add VS Code configuration (`settings.json`, `launch.json`) |
| `--with-license` | Add MIT LICENSE file |
| `--with-gitignore` | Add Python .gitignore preset |
| `--root <path>` | Target project directory |

Example:
```powershell
reposmith init --root MyApp --use-uv --with-vscode
```

---

## 💡 Quick Summary

| Command | Description |
|----------|--------------|
| `reposmith init` | Create a complete new project |
| `reposmith doctor` | Check environment health (upcoming) |
| `reposmith --version` | Show current version |
| `reposmith --help` | Display help menu |

---

## 🧩 Example Structure

```
MyApp/
├── main.py
├── .venv/
├── tools/
│   ├── setup_env.ps1
│   ├── clean_build.ps1
│   └── run_tests.ps1
├── .vscode/
│   ├── launch.json
│   ├── settings.json
│   └── tasks.json
├── .github/
│   └── workflows/ci.yml
├── .gitignore
└── LICENSE
```

---

## 💻 Development & Testing

```powershell
# Editable install
uv pip install -e . --system

# Run tests
uv run pytest -q --cov=. --cov-report=term-missing
```

---

## 🗺 Roadmap

- [x] UV-based dependency installer  
- [x] VS Code automation  
- [x] CI workflow templates  
- [ ] Template packs (FastAPI, Streamlit, Django)  
- [ ] Interactive wizard mode  
- [ ] Multi-license support (MIT / Apache / GPL)

---

## 🛡 License

Licensed under [MIT](LICENSE) © 2025 **Tamer Hamad Faour (@TamerOnLine)**  

---

## 💬 Community & Support

- 🐞 [Report a Bug](https://github.com/TamerOnLine/reposmith-init/issues/new?template=bug.yml)  
- 💡 [Suggest a Feature](https://github.com/TamerOnLine/reposmith-init/issues/new?template=feature.yml)  
- 💬 [Join Discussions](https://github.com/TamerOnLine/reposmith-init/discussions)  
- 💖 [Support via GitHub Sponsors](https://github.com/sponsors/TamerOnLine)  
- 📧 info@tameronline.com

