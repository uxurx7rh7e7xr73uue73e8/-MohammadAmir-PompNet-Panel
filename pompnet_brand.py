from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"

# =========================================================
# POMP NET BRANDING
# قالب و منطق اصلی AHBPanel حفظ می‌شود.
# فقط ظاهر، نام برند و لینک‌های نمایشی تغییر می‌کنند.
# =========================================================

TEXT_EXTENSIONS = {
    ".py", ".html", ".htm", ".css", ".js",
    ".json", ".md", ".txt", ".yml", ".yaml"
}

SKIP_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
}

# =========================================================
# اطلاعات رسمی POMP NET
# =========================================================

BRAND = "POMP NET"
TITLE = "MR: Mohammad Pomp NetPanel"
TEAM = "Mohammad & Amir"

AMIR_USERNAME = "@vpnstan2"
AMIR_CHANNEL = "https://t.me/vpnstan1"

POMP_CHANNEL = "https://t.me/pompnet"
POMP_GROUP = "https://t.me/+UV34C7Ohs9hiZTc0"

SUPPORT_USERNAME = "@NovaTunneli"
SUPPORT_URL = "https://t.me/NovaTunneli"

GITHUB_USERNAME = "uxurx7rh7e7xr73uue73e8"
GITHUB_URL = "https://github.com/uxurx7rh7e7xr73uue73e8"

TOP_BANNER = (
    "⚡ توسعه و طراحی توسط تیم POMP NET "
    "• با همکاری ویژه آقا امیر | Mohammad & Amir "
    "• ساخته‌شده برای یک تجربه سریع، مدرن و حرفه‌ای"
)

# =========================================================
# فقط جایگزینی‌های برندینگ
# =========================================================

REPLACEMENTS = [

    # AHB branding
    ("Created By Ahb",
     "⚡ توسعه و طراحی توسط تیم POMP NET • با همکاری ویژه آقا امیر | Mohammad & Amir"),

    ("Created by Ahb",
     "⚡ توسعه و طراحی توسط تیم POMP NET • با همکاری ویژه آقا امیر | Mohammad & Amir"),

    ("Created By AHB",
     "⚡ توسعه و طراحی توسط تیم POMP NET • با همکاری ویژه آقا امیر | Mohammad & Amir"),

    ("Created by AHB",
     "⚡ توسعه و طراحی توسط تیم POMP NET • با همکاری ویژه آقا امیر | Mohammad & Amir"),

    ("پنل AHB",
     "پنل POMP NET"),

    ("ای اچ بی پنل",
     "POMP NET"),

    ("AHBPanel",
     "POMP NET"),

    ("ahbpanel",
     "pompnet"),

    ("AHB PANEL",
     "POMP NET"),

    ("@ahb_panel",
     SUPPORT_USERNAME),

    ("@ahbpanel",
     SUPPORT_USERNAME),

    # Telegram
    ("https://t.me/ahbpanel",
     POMP_CHANNEL),

    ("https://t.me/ahb_panel",
     SUPPORT_URL),

    # Branding
    ("Mohammad Pomp NetPanel",
     TITLE),
]


# =========================================================
# تغییر متن فایل‌ها
# =========================================================

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


# =========================================================
# تنظیمات اصلی main.py
# =========================================================

def replace_main_settings():

    if not MAIN.exists():
        raise RuntimeError(
            "main.py پیدا نشد؛ سورس اصلی AHBPanel دریافت نشده است."
        )

    data = MAIN.read_text(encoding="utf-8")

    # نام برنامه
    data = re.sub(
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1,
    )

    # عنوان نسخه
    data = re.sub(
        r'APP_VERSION\s*=\s*["\'][^"\']*["\']',
        'APP_VERSION = "POMP NET"',
        data,
        count=1,
    )

    # پشتیبانی
    data = re.sub(
        r'SUPPORT_USERNAME\s*=\s*["\'][^"\']*["\']',
        f'SUPPORT_USERNAME = "{SUPPORT_USERNAME}"',
        data,
        count=1,
    )

    data = re.sub(
        r'SUPPORT_URL\s*=\s*["\'][^"\']*["\']',
        f'SUPPORT_URL = "{SUPPORT_URL}"',
        data,
        count=1,
    )

    MAIN.write_text(data, encoding="utf-8")


# =========================================================
# افزودن اطلاعات POMP NET به HTML/CSS/JS
# =========================================================

def inject_brand_style(path: Path):

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return

    original = text

    # فقط فایل‌های HTML
    if path.suffix.lower() in {".html", ".htm"}:

        banner = f"""
<!-- =====================================================
 POMP NET BRAND
 ===================================================== -->

<div id="pompnet-brand-banner"
     style="
       width:100%;
       text-align:center;
       padding:9px 14px;
       margin:0 0 12px;
       border-radius:14px;
       background:linear-gradient(
         135deg,
         rgba(116,35,255,.18),
         rgba(0,130,255,.16)
       );
       border:1px solid rgba(150,100,255,.25);
       color:#e8ddff;
       font-size:12px;
       line-height:1.8;
       box-shadow:
         0 0 25px rgba(100,40,255,.12),
         inset 0 1px rgba(255,255,255,.06);
       backdrop-filter:blur(14px);
     ">
    ⚡ توسعه و طراحی توسط تیم <b>POMP NET</b>
    • با همکاری ویژه آقا امیر
    • Mohammad &amp; Amir
    • ساخته‌شده برای یک تجربه سریع، مدرن و حرفه‌ای
</div>
"""

        # فقط یک‌بار به ابتدای body اضافه شود
        if 'id="pompnet-brand-banner"' not in text:

            text = re.sub(
                r'(<body[^>]*>)',
                r'\1' + banner,
                text,
                count=1,
                flags=re.IGNORECASE,
            )

    if text != original:
        path.write_text(text, encoding="utf-8")


# =========================================================
# اجرای اصلی
# =========================================================

def main():

    if not ROOT.exists():
        raise RuntimeError("/app وجود ندارد.")

    if not MAIN.exists():
        raise RuntimeError(
            "سورس AHBPanel در /app پیدا نشد."
        )

    # تنظیمات اصلی
    replace_main_settings()

    # پردازش تمام فایل‌های متنی
    for path in ROOT.rglob("*"):

        if not path.is_file():
            continue

        if any(part in SKIP_DIRS for part in path.parts):
            continue

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        if path == MAIN:
            continue

        replace_file(path)
        inject_brand_style(path)

    print("=" * 70)
    print("                 POMP NET")
    print("=" * 70)
    print("MR: Mohammad Pomp NetPanel")
    print("Mohammad & Amir")
    print()
    print("⚡ توسعه و طراحی توسط تیم POMP NET")
    print("🤝 با همکاری ویژه آقا امیر")
    print()
    print("Amir:", AMIR_USERNAME)
    print("Amir Channel:", AMIR_CHANNEL)
    print("PompNet Channel:", POMP_CHANNEL)
    print("PompNet Group:", POMP_GROUP)
    print("Support:", SUPPORT_USERNAME)
    print("GitHub:", GITHUB_USERNAME)
    print()
    print("Theme: Black / Neon Purple / Neon Blue / Pink")
    print("Glassmorphism: Enabled")
    print("RTL: Persian")
    print("=" * 70)


if __name__ == "__main__":
    main()
