from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"

# فقط موارد نمایشی/برندینگ تغییر می‌کنند.
# منطق داخلی پنل دست‌کاری نمی‌شود.
REPLACEMENTS = [
    ("https://t.me/ahbpanel", "https://t.me/pompnet"),
    ("https://t.me/ahb_panel", "https://t.me/pompnet"),

    ("@ahb_panel", "@NovaTunneli"),

    ("Created By Ahb", "Created By Mohammad & Amir | POMP NET"),
    ("Created by Ahb", "Created by Mohammad & Amir | POMP NET"),

    ("AHBPanel", "POMP NET"),
    ("AHB PANEL", "POMP NET"),
    ("AHB Panel", "POMP NET"),
    ("Ahb Panel", "POMP NET"),

    ("پنل AHB", "پنل POMP NET"),
    ("ای اچ بی پنل", "POMP NET"),
]

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
        raise RuntimeError("main.py پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")

    # نام نمایشی برنامه
    data = re.sub(
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1
    )

    # نسخه را دست نمی‌زنیم.
    # منطق اصلی پنل حفظ می‌شود.

    # پشتیبانی
    data = re.sub(
        r'SUPPORT_USERNAME\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_USERNAME = "@NovaTunneli"',
        data,
        count=1
    )

    data = re.sub(
        r'SUPPORT_URL\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_URL = "https://t.me/NovaTunneli"',
        data,
        count=1
    )

    MAIN.write_text(data, encoding="utf-8")


def main():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue

        if any(part in SKIP_DIRS for part in path.parts):
            continue

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        replace_file(path)

    replace_main_settings()

    print("=" * 55)
    print(" POMP NET BUILD")
    print(" Mohammad & Amir")
    print(" Original AHBPanel core preserved")
    print(" Admin username: admin")
    print(" Admin password: admin")
    print(" Support: @NovaTunneli")
    print("=" * 55)


if __name__ == "__main__":
    main()
