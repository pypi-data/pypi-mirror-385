from __future__ import annotations
from pathlib import Path

from ..file_utils import create_app_file
from ..ci_utils import ensure_github_actions_workflow
from ..venv_utils import create_virtualenv
from ..vscode_utils import create_vscode_files
from ..gitignore_utils import create_gitignore
from ..license_utils import create_license
from ..utils.deps import post_init_dependency_setup


def run_init(args, logger) -> int:
    """
    تهيئة مشروع جديد بدون أي تكامل مع Brave.
    - ينشئ .venv (إلا إذا تم تمرير --no-venv)
    - ينشئ ملف الدخول (run.py افتراضياً أو بحسب --entry)
    - يضيف اختيارات اختيارية: VS Code / .gitignore / LICENSE
    - يضبط GitHub Actions CI
    - يهيّئ التبعيات عبر uv أو pip (post_init_dependency_setup)
    """
    root: Path = args.root
    root.mkdir(parents=True, exist_ok=True)
    logger.info("🚀 Initializing project at: %s", root)

    # توسيع --all (بدون Brave)
    if getattr(args, "all", False):
        args.use_uv = True
        args.with_vscode = True
        args.with_license = True
        args.with_gitignore = True

    # (1) إنشاء البيئة الافتراضية (إن لم يُطلب عدم إنشائها)
    venv_dir = root / ".venv"
    no_venv = bool(getattr(args, "no_venv", False))
    if not no_venv:
        create_virtualenv(venv_dir)
    else:
        logger.info("Skipping virtual environment creation (--no-venv).")

    # (2) ملف الدخول
    entry_name = args.entry if (getattr(args, "entry", None) not in (None, "")) else "run.py"
    entry_path = root / entry_name
    create_app_file(entry_path, force=args.force)
    logger.info("[entry] %s created at: %s", entry_name, entry_path)

    # (3) إضافات اختيارية
    if getattr(args, "with_vscode", False):
        create_vscode_files(root, venv_dir, main_file=str(entry_path), force=args.force)
    if getattr(args, "with_gitignore", False):
        create_gitignore(root, force=args.force)
    if getattr(args, "with_license", False):
        # يمكنك تمرير نوع ورخصة/اسم مالك من args لاحقًا إن لزم
        create_license(root, license_type="MIT", owner_name="Tamer", force=args.force)

    # (4) CI
    ensure_github_actions_workflow(root)

    # (5) تثبيت/تهيئة التبعيات (uv أو pip) — بعد إنشاء الملفات
    try:
        post_init_dependency_setup(root, prefer_uv=bool(getattr(args, "use_uv", False)))
    except Exception as e:
        logger.warning(f"Post-init dependency setup failed: {e}")

    logger.info("✅ Project initialized successfully at: %s", root)
    return 0
