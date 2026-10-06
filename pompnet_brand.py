from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"

# =========================================================
# POMP NET BRANDING
# فقط موارد نمایشی و تنظیمات برندینگ تغییر می‌کنند.
# هسته و منطق AHBPanel دستکاری نمی‌شود.
# =========================================================

TEXT_EXTENSIONS = {
    ".py",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".json",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

# فقط متن‌های کاملاً مشخص و نمایشی
REPLACEMENTS = [
    ("Created By Ahb", "Created By Mohammad & Amir | POMP NET"),
    ("Created by Ahb", "Created by Mohammad & Amir | POMP NET"),

    ("پنل AHB", "پنل POMP NET"),
    ("ای اچ بی پنل", "POMP NET"),

    ("@ahb_panel", "@NovaTunneli"),

    ("https://t.me/ahbpanel", "https://t.me/pompnet"),
    ("https://t.me/ahb_panel", "https://t.me/pompnet"),
]


def replace_file(path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return

    original = text

    for old, new in REPLACEMENTS:
        text = text.replace(old, new)

    if text != original:
        path.write_text(text, encoding="utf-8")


def replace_main_settings():
    if not MAIN.exists():
        raise RuntimeError("main.py پیدا نشد؛ سورس AHBPanel درست دریافت نشده است.")

    data = MAIN.read_text(encoding="utf-8")

    # نام نمایشی برنامه
    data = re.sub(
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1,
    )

    # پشتیبانی
    data = re.sub(
        r'SUPPORT_USERNAME\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_USERNAME = "@NovaTunneli"',
        data,
        count=1,
    )

    data = re.sub(
        r'SUPPORT_URL\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_URL = "https://t.me/NovaTunneli"',
        data,
        count=1,
    )

    MAIN.write_text(data, encoding="utf-8")


def main():
    if not ROOT.exists():
        raise RuntimeError("/app وجود ندارد.")

    # ابتدا تنظیمات اصلی برنامه
    replace_main_settings()

    # سپس فقط متن‌های نمایشی مشخص
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if any(part in SKIP_DIRS for part in path.parts):
            continue

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        # main.py جداگانه مدیریت شد
        if path == MAIN:
            continue

        replace_file(path)

    print("=" * 60)
    print(" POMP NET")
    print(" MR: Mohammad Pomp NetPanel")
    print(" Mohammad & Amir")
    print(" Original AHBPanel core preserved")
    print(" Support: @NovaTunneli")
    print(" Admin username: admin")
    print(" Admin password: configured by ADMIN_PASSWORD")
    print("=" * 60)


if __name__ == "__main__":
    main()
