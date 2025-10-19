import os
import sys
import subprocess
import tempfile
from pathlib import Path
import shlex
import re

def _help_text_for(subcmd: str) -> str:
    """رجّع نص المساعدة لأمر معيّن من CLI: python -m reposmith.main <subcmd> --help"""
    proc = subprocess.run(
        [sys.executable, "-m", "reposmith.main", subcmd, "--help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return proc.stdout or ""

def _is_flag_supported(help_text: str, flag: str) -> bool:
    # بحث بسيط عن الـ flag في نص المساعدة
    pat = r"(?:^|\s)" + re.escape(flag) + r"(?:\s|,|$)"
    return re.search(pat, help_text) is not None

class TestCLISmoke:
    def _run(self, args, cwd: Path):
        return subprocess.run(
            [sys.executable, "-m", "reposmith.main"] + args,
            cwd=cwd,
            check=True,
        )

    def test_init_smoke_adaptive(self):
        with tempfile.TemporaryDirectory() as td:
            proj = Path(td) / "proj"
            proj.mkdir(parents=True, exist_ok=True)

            help_text = _help_text_for("init")

            # نبني القائمة حسب الموجود فعليًا
            args = ["init"]

            # إذا مدعوم --entry، نخليه ينشئ ملف run.py
            if _is_flag_supported(help_text, "--entry"):
                args += ["--entry", "run.py"]

            # هذه الخيارات إضافية إن وُجدت
            if _is_flag_supported(help_text, "--with-gitignore"):
                args.append("--with-gitignore")
            if _is_flag_supported(help_text, "--with-license"):
                args += ["--with-license"]
                if _is_flag_supported(help_text, "--author"):
                    args += ["--author", "TestUser"]
                if _is_flag_supported(help_text, "--year"):
                    args += ["--year", "2099"]
            if _is_flag_supported(help_text, "--with-vscode"):
                args.append("--with-vscode")
            if _is_flag_supported(help_text, "--no-venv"):
                args.append("--no-venv")

            # نفّذ الأمر — الهدف: ما يكرّش
            self._run(args, cwd=proj)

            # تحقّقات خفيفة حسب ما طلبناه
            # لو طلبنا --entry run.py، تأكد من وجوده
            if "--entry" in args:
                assert (proj / "run.py").exists()

            # لو طلبنا --with-gitignore، تأكد من وجوده
            if "--with-gitignore" in args:
                assert (proj / ".gitignore").exists()

            # لو طلبنا --with-license، تأكد من وجود LICENSE
            if "--with-license" in args:
                assert (proj / "LICENSE").exists()

            # لو طلبنا --with-vscode، تأكد من مجلد .vscode
            if "--with-vscode" in args:
                assert (proj / ".vscode").exists()
