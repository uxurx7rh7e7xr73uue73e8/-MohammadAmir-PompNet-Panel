from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def main():
    if not MAIN.exists():
        raise RuntimeError("ERROR: /app/main.py پیدا نشد")

    if not CSS.exists():
        raise RuntimeError("ERROR: /app/pompnet.css پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    # =====================================================
    # POMP NET
    # =====================================================

    data = re.sub(
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1,
    )

    data = re.sub(
        r'APP_VERSION\s*=\s*["\'][^"\']*["\']',
        'APP_VERSION = "POMP NET"',
        data,
        count=1,
    )

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

    # =====================================================
    # تغییر نام‌های نمایشی
    # =====================================================

    replacements = {
        "Created By Ahb": "Created By POMP NET",
        "Created By AHB": "Created By POMP NET",
        "AHB Panel": "POMP NET",
        "AHB PANEL": "POMP NET",
        "ahbpanel": "POMP NET",
        "@ahb_panel": "@NovaTunneli",
        "https://t.me/ahbpanel": "https://t.me/NovaTunneli",
    }

    for old, new in replacements.items():
        data = data.replace(old, new)

    # =====================================================
    # CSS
    # =====================================================

    style = (
        '<style id="pompnet-css">\n'
        + css
        + '\n</style>'
    )

    if 'id="pompnet-css"' not in data:
        data = data.replace(
            "</head>",
            style + "\n</head>",
            1,
        )

    # =====================================================
    # Banner
    # =====================================================

    banner = """
<div id="pompnet-brand-banner">
    ⚡ توسعه و طراحی توسط تیم
    <b>POMP NET</b>
    • با همکاری ویژه آقا امیر
    • Mohammad &amp; Amir
    • ساخته‌شده برای یک تجربه سریع، مدرن و حرفه‌ای
</div>
"""

    if 'id="pompnet-brand-banner"' not in data:
        data = data.replace(
            "<body>",
            "<body>\n" + banner,
            1,
        )

    # =====================================================
    # ذخیره
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8",
    )

    print("=" * 60)
    print("POMP NET BUILD PREPARATION OK")
    print("main.py ........ OK")
    print("CSS ............ OK")
    print("Branding ....... OK")
    print("Original core .. PRESERVED")
    print("=" * 60)


if __name__ == "__main__":
    main()
