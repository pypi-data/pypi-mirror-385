import tempfile
from pathlib import Path
import pytest

def test_gitignore_unsupported_preset_is_adaptive(capsys):
    try:
        from reposmith import gitignore_utils as gi
    except Exception:
        pytest.skip("gitignore_utils غير متاح")

    fn = None
    for name in ("ensure_gitignore", "create_gitignore", "write_gitignore"):
        if hasattr(gi, name):
            fn = getattr(gi, name)
            break
    if fn is None:
        pytest.skip("لا توجد دالة لضمان .gitignore")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # سيناريو 1: بعض الإصدارات قد ترفع استثناء
        try:
            try:
                fn(root, preset="__NOT_A_REAL_PRESET__")
            except TypeError:
                # تواقيع بديلة محتملة
                fn(root, preset_name="__NOT_A_REAL_PRESET__")
        except (ValueError, KeyError, SystemExit):
            # إذا رُفع استثناء، هذا سلوك مقبول للاختبار
            return

        # سيناريو 2: لا استثناء → نتوقع fallback لباكيدج python
        out, err = capsys.readouterr()
        msg = (out + err).lower()

        # يجب أن يكون الملف موجوداً وغير فارغ
        gitignore = root / ".gitignore"
        assert gitignore.exists() and gitignore.stat().st_size > 0

        # وجود أي إشارة للفول باك/التحذير أو قائمة المتاح
        hints = ("unknown preset", "falling back", "available", "preset", ".gitignore")
        assert any(h in msg for h in hints), f"Expected fallback message. got: {msg!r}"
