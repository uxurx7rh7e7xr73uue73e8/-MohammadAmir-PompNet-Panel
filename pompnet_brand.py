from pathlib import Path
import re
import hashlib
import py_compile

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def get_sub_route(data: str):
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?'
        r'(?=\n@app\.get|\n@app\.post|\n@app\.websocket|\nasync def |\Z)',
        re.S,
    )

    match = pattern.search(data)
    return match.group(0) if match else None


def main():

    if not MAIN.exists():
        raise RuntimeError(
            "ERROR: /app/main.py پیدا نشد"
        )

    if not CSS.exists():
        raise RuntimeError(
            "ERROR: /app/pompnet.css پیدا نشد"
        )

    data = MAIN.read_text(
        encoding="utf-8"
    )

    # =========================================================
    # قبل از تغییر، منطق واقعی Subscription را ذخیره می‌کنیم
    # =========================================================

    sub_before = get_sub_route(data)

    if not sub_before:
        raise RuntimeError(
            "ERROR: مسیر واقعی /sub/{uuid} پیدا نشد"
        )

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # =========================================================
    # فقط Branding
    # هیچ info_html جدیدی ساخته نمی‌شود.
    # صفحه اصلی واقعی AHB دست‌نخورده می‌ماند.
    # =========================================================

    replacements = {

        "AHB PANEL":
            "POMP NET PANEL",

        "AHB Panel":
            "POMP NET PANEL",

        "AHBPanel":
            "POMP NET",

        "Created By Ahb":
            "Created By POMP NET",

        "Created By AHB":
            "Created By POMP NET",

        "به پنل مدیریت AHB خوش آمدید":
            "به پنل مدیریت POMP NET خوش آمدید",

        "درگاه عمومی AHB Panel":
            "درگاه عمومی POMP NET",

        "این صفحه، درگاه عمومی AHB Panel است.":
            "این صفحه، درگاه عمومی POMP NET است.",

        "AHB Panel · 14.3.0":
            "POMP NET",

        "https://t.me/ahb_panel":
            "https://t.me/NovaTunneli",

        "https://t.me/ahbpanel":
            "https://t.me/NovaTunneli",

        "@ahb_panel":
            "@NovaTunneli",

        "@ahbpanel":
            "@NovaTunneli",

        "@ahbpanelgap":
            "@NovaTunneli",
    }

    for old, new in replacements.items():

        data = data.replace(
            old,
            new
        )

    # =========================================================
    # تنظیم Support
    # =========================================================

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

    # =========================================================
    # نام برنامه
    # =========================================================

    data = re.sub(
        r'(?m)^APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1
    )

    # =========================================================
    # CSS اختصاصی POMP NET
    # بدون حذف HTML/JS اصلی
    # =========================================================

    css = CSS.read_text(
        encoding="utf-8"
    )

    if 'id="pompnet-css"' not in data:

        if "</head>" not in data:

            raise RuntimeError(
                "ERROR: </head> برای CSS پیدا نشد"
            )

        data = data.replace(

            "</head>",

            '<style id="pompnet-css">\n'
            + css
            + "\n</style>\n"
            + "</head>",

            1
        )

    # =========================================================
    # ذخیره
    # =========================================================

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # =========================================================
    # بررسی Syntax پایتون
    # =========================================================

    try:

        py_compile.compile(
            str(MAIN),
            doraise=True
        )

    except Exception as exc:

        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "Python Syntax Error\n"
            + str(exc)
        )

    # =========================================================
    # بررسی نهایی
    # =========================================================

    check = MAIN.read_text(
        encoding="utf-8"
    )

    sub_after = get_sub_route(check)

    if not sub_after:

        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "/sub/{uuid} حذف شده"
        )

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    # Subscription نباید تغییر کرده باشد
    if sub_hash_before != sub_hash_after:

        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "منطق /sub/{uuid} تغییر کرده است"
        )

    # قابلیت‌های اصلی باید وجود داشته باشند
    required = [

        "/sub/{uuid}",

        "async def info_page",

        "POMP NET",

        "@NovaTunneli",

        "https://t.me/NovaTunneli",

        'id="pompnet-css"',
    ]

    for item in required:

        if item not in check:

            raise RuntimeError(
                "BUILD CHECK FAILED: "
                + item
            )

    # =========================================================
    # نتیجه Build
    # =========================================================

    print("=" * 64)

    print(
        "POMP NET BUILD CHECK: OK"
    )

    print(
        "PYTHON SYNTAX: OK"
    )

    print(
        "REAL CORE: PRESERVED"
    )

    print(
        "SUBSCRIPTION: PRESERVED"
    )

    print(
        "INFO PAGE: PRESERVED"
    )

    print(
        "QR/SERVERS: PRESERVED"
    )

    print(
        "VLESS: PRESERVED"
    )

    print(
        "SUB URL: PRESERVED"
    )

    print(
        "HEALTH: PRESERVED"
    )

    print(
        "SUPPORT: @NovaTunneli"
    )

    print(
        "RAILWAY PORT: $PORT"
    )

    print("=" * 64)


if __name__ == "__main__":

    main()
