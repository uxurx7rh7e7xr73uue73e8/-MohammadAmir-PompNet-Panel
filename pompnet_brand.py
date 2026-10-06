from pathlib import Path
import re

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def replace_once(data, pattern, replacement):
    return re.sub(
        pattern,
        replacement,
        data,
        count=1
    )


def main():

    # -----------------------------
    # بررسی فایل‌ها
    # -----------------------------

    if not MAIN.exists():
        raise RuntimeError("ERROR: /app/main.py پیدا نشد")

    if not CSS.exists():
        raise RuntimeError("ERROR: /app/pompnet.css پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    # -----------------------------
    # نام پنل
    # -----------------------------

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

    # -----------------------------
    # پشتیبانی
    # -----------------------------

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

    # -----------------------------
    # برندینگ
    # -----------------------------

    replacements = {
        "Created By Ahb": "Created By POMP NET",
        "Created By AHB": "Created By POMP NET",
        "AHB Panel": "POMP NET",
        "AHB PANEL": "POMP NET",
        "@ahb_panel": "@NovaTunneli",
        "https://t.me/ahbpanel": "https://t.me/NovaTunneli",
    }

    for old, new in replacements.items():
        data = data.replace(old, new)

    # -----------------------------
    # CSS
    # -----------------------------

    if 'id="pompnet-css"' not in data:

        if "</head>" not in data:
            raise RuntimeError(
                "ERROR: تگ </head> پیدا نشد"
            )

        style = (
            '<style id="pompnet-css">\n'
            + css +
            '\n</style>'
        )

        data = data.replace(
            "</head>",
            style + "\n</head>",
            1
        )

    # -----------------------------
    # Banner
    # -----------------------------

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

    # -----------------------------
    # ذخیره
    # -----------------------------

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    print("=" * 60)
    print("POMP NET BUILD OK")
    print("main.py ........ OK")
    print("CSS ............ OK")
    print("Branding ....... OK")
    print("Port ........... 8080")
    print("Admin .......... admin / admin")
    print("Core ........... PRESERVED")
    print("=" * 60)


if __name__ == "__main__":
    main()
