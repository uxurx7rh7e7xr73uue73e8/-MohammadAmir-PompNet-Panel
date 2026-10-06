from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def main():

    if not MAIN.exists():
        raise RuntimeError("main.py پیدا نشد")

    if not CSS.exists():
        raise RuntimeError("pompnet.css پیدا نشد")

    data = MAIN.read_text(
        encoding="utf-8"
    )

    css = CSS.read_text(
        encoding="utf-8"
    )

    # =====================================================
    # تنظیمات اصلی POMP NET
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
    # فقط متن‌های نمایشی
    # منطق داخلی پنل تغییر نمی‌کند
    # =====================================================

    data = data.replace(
        "Created By Ahb",
        "Created By POMP NET"
    )

    data = data.replace(
        "AHB Panel",
        "POMP NET"
    )

    # =====================================================
    # تزریق CSS
    #
    # چون AHBPanel صفحه‌ها را داخل main.py
    # به صورت HTML داخلی دارد، CSS مستقیماً
    # داخل همان HTML قرار می‌گیرد.
    # =====================================================

    style = (
        '<style id="pompnet-css">\n'
        + css
        + '\n</style>'
    )

    if 'id="pompnet-css"' not in data:

        data = data.replace(
            "</head>",
            style + "\n</head>"
        )

    # =====================================================
    # بنر POMP NET
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
            1
        )

    # =====================================================
    # ذخیره main.py اصلاح‌شده
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    print("=" * 60)
    print("POMP NET BRANDING OK")
    print("CSS injected successfully")
    print("Banner injected successfully")
    print("Original panel logic preserved")
    print("=" * 60)


if __name__ == "__main__":
    main()
