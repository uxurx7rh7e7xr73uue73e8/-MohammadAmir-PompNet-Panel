from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def replace_once(data, pattern, replacement):
    return re.sub(pattern, replacement, data, count=1)


def main():
    if not MAIN.exists():
        raise RuntimeError("ERROR: main.py پیدا نشد")

    if not CSS.exists():
        raise RuntimeError("ERROR: pompnet.css پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    # =====================================================
    # مشخصات اصلی
    # =====================================================

    data = replace_once(
        data,
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"'
    )

    data = replace_once(
        data,
        r'APP_VERSION\s*=\s*["\'][^"\']*["\']',
        'APP_VERSION = "POMP NET"'
    )

    data = replace_once(
        data,
        r'SUPPORT_USERNAME\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_USERNAME = "@NovaTunneli"'
    )

    data = replace_once(
        data,
        r'SUPPORT_URL\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_URL = "https://t.me/NovaTunneli"'
    )

    # =====================================================
    # حذف برند قدیمی از متن‌های نمایشی
    # =====================================================

    replacements = {
        "AHB PANEL": "POMP NET",
        "AHB Panel": "POMP NET",
        "AhbPanel": "POMP NET",
        "AHBPanel": "POMP NET",

        "ahbpanel": "pompnet",
        "ahb_panel": "NovaTunneli",

        "@ahb_panel": "@NovaTunneli",
        "@ahbpanel": "@NovaTunneli",
        "@ahbpanelgap": "@NovaTunneli",

        "https://t.me/ahb_panel":
            "https://t.me/NovaTunneli",

        "https://t.me/ahbpanel":
            "https://t.me/NovaTunneli",

        "https://github.com/ahb-panel/ahb_panel":
            "https://github.com/uxurx7rh7e7xr73uue73e8",

        "ahb-panel/ahb_panel":
            "uxurx7rh7e7xr73uue73e8",

        "Created By Ahb":
            "Created By POMP NET",

        "Created By AHB":
            "Created By POMP NET",

        "به پنل مدیریت AHB خوش آمدید":
            "به پنل مدیریت POMP NET خوش آمدید",

        "درگاه عمومی AHB Panel":
            "درگاه عمومی POMP NET",

        "AHB":
            "POMP NET",
    }

    for old, new in replacements.items():
        data = data.replace(old, new)

    # =====================================================
    # عنوان‌های HTML
    # =====================================================

    data = data.replace(
        "<title>AHB PANEL</title>",
        "<title>POMP NET</title>"
    )

    data = data.replace(
        "<title>AHBPanel 14.3.0</title>",
        "<title>POMP NET</title>"
    )

    # =====================================================
    # برند پایین صفحه
    # =====================================================

    data = data.replace(
        "AHB PANEL</b>",
        "POMP NET</b>"
    )

    # =====================================================
    # لینک پشتیبانی
    # =====================================================

    data = data.replace(
        'href="https://t.me/ahb_panel"',
        'href="https://t.me/NovaTunneli"'
    )

    # =====================================================
    # لینک GitHub نمایشی
    # =====================================================

    data = data.replace(
        "github.com/ahb-panel/ahb_panel",
        "github.com/uxurx7rh7e7xr73uue73e8"
    )

    # =====================================================
    # CSS POMP NET
    # =====================================================

    if 'id="pompnet-css"' not in data:
        if "</head>" not in data:
            raise RuntimeError("ERROR: </head> پیدا نشد")

        style = (
            '<style id="pompnet-css">\n'
            + css +
            "\n</style>"
        )

        data = data.replace(
            "</head>",
            style + "\n</head>",
            1
        )

    # =====================================================
    # بنر POMP NET
    # =====================================================

    if 'id="pompnet-brand-banner"' not in data:
        banner = """
<div id="pompnet-brand-banner">
    ⚡ توسعه و طراحی توسط تیم
    <b>POMP NET</b>
    • با همکاری ویژه آقا امیر
    • Mohammad &amp; Amir
    • ساخته‌شده برای یک تجربه سریع، مدرن و حرفه‌ای
</div>
"""

        if "<body>" in data:
            data = data.replace(
                "<body>",
                "<body>\n" + banner,
                1
            )

    # =====================================================
    # ذخیره
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # =====================================================
    # تست نهایی Build
    # =====================================================

    check = MAIN.read_text(encoding="utf-8")

    required = [
        "APP_NAME = \"POMP NET\"",
        "@NovaTunneli",
        'id="pompnet-css"',
        'id="pompnet-brand-banner"',
    ]

    for item in required:
        if item not in check:
            raise RuntimeError(
                "BUILD CHECK FAILED: " + item
            )

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("CORE: PRESERVED")
    print("THEME: POMP NET")
    print("SUPPORT: @NovaTunneli")
    print("ADMIN: admin / admin")
    print("PORT: Railway $PORT")
    print("HEALTH: /health")
    print("=" * 60)


if __name__ == "__main__":
    main()
