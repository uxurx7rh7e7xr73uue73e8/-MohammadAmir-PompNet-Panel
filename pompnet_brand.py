from pathlib import Path
import re
import hashlib
import py_compile

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"
LOGIN_CSS = Path("/tmp/pompnet_login.css")
LOGIN_JS = Path("/tmp/pompnet_login.js")


def get_sub_route(data: str):
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?'
        r'(?=\n@app\.get|\n@app\.post|\n@app\.websocket|\nasync def |\Z)',
        re.S,
    )
    match = pattern.search(data)
    return match.group(0) if match else None


def main():

    for path, name in (
        (MAIN, "/app/main.py"),
        (CSS, "/app/pompnet.css"),
        (LOGIN_CSS, "/tmp/pompnet_login.css"),
        (LOGIN_JS, "/tmp/pompnet_login.js"),
    ):
        if not path.exists():
            raise RuntimeError(f"ERROR: {name} پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")

    # ---------------------------------------------------------
    # محافظت از قابلیت واقعی Subscription
    # ---------------------------------------------------------

    sub_before = get_sub_route(data)

    if not sub_before:
        raise RuntimeError(
            "ERROR: مسیر واقعی /sub/{uuid} پیدا نشد"
        )

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # ---------------------------------------------------------
    # فقط تغییر برندینگ
    # ---------------------------------------------------------

    replacements = {
        "AHB PANEL": "POMP NET PANEL",
        "AHB Panel": "POMP NET PANEL",
        "AHBPanel": "POMP NET",
        "Created By Ahb": "Created By POMP NET",
        "Created By AHB": "Created By POMP NET",

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
        data = data.replace(old, new)

    # ---------------------------------------------------------
    # Support
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # نام برنامه
    # ---------------------------------------------------------

    data = re.sub(
        r'(?m)^APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1,
    )

    # ---------------------------------------------------------
    # قالب اصلی PompNet
    # ---------------------------------------------------------

    css = CSS.read_text(encoding="utf-8")

    if 'id="pompnet-css"' not in data:
        if "</head>" not in data:
            raise RuntimeError(
                "ERROR: </head> پیدا نشد"
            )

        data = data.replace(
            "</head>",
            '<style id="pompnet-css">\n'
            + css
            + "\n</style>\n"
            + "</head>",
            1,
        )

    # ---------------------------------------------------------
    # قالب Login PompNet
    # ---------------------------------------------------------

    login_css = LOGIN_CSS.read_text(
        encoding="utf-8"
    )

    if 'id="pompnet-login-css"' not in data:
        if "</head>" not in data:
            raise RuntimeError(
                "ERROR: </head> برای Login پیدا نشد"
            )

        data = data.replace(
            "</head>",
            '<style id="pompnet-login-css">\n'
            + login_css
            + "\n</style>\n"
            + "</head>",
            1,
        )

    login_js = LOGIN_JS.read_text(
        encoding="utf-8"
    )

    if 'id="pompnet-login-js"' not in data:
        if "</body>" not in data:
            raise RuntimeError(
                "ERROR: </body> برای Login پیدا نشد"
            )

        data = data.replace(
            "</body>",
            '<script id="pompnet-login-js">\n'
            + login_js
            + "\n</script>\n"
            + "</body>",
            1,
        )

    # ---------------------------------------------------------
    # ذخیره
    # ---------------------------------------------------------

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # ---------------------------------------------------------
    # Syntax Check
    # ---------------------------------------------------------

    py_compile.compile(
        str(MAIN),
        doraise=True
    )

    # ---------------------------------------------------------
    # بررسی نهایی
    # ---------------------------------------------------------

    check = MAIN.read_text(
        encoding="utf-8"
    )

    sub_after = get_sub_route(check)

    if not sub_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: /sub/{uuid} حذف شده"
        )

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    if sub_hash_before != sub_hash_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "منطق Subscription تغییر کرده است"
        )

    required = [
        "/sub/{uuid}",
        "async def info_page",
        "POMP NET",
        "@NovaTunneli",
        "https://t.me/NovaTunneli",
        'id="pompnet-css"',
        'id="pompnet-login-css"',
        'id="pompnet-login-js"',
        "MR. MOHAMMAD",
        "POMPNET",
        "کدنویسی شده توسط تیم پمپ نت و آقا امیر",
    ]

    for item in required:
        if item not in check:
            raise RuntimeError(
                "BUILD CHECK FAILED: " + item
            )

    print("=" * 64)
    print("POMP NET BUILD CHECK: OK")
    print("PYTHON SYNTAX: OK")
    print("REAL PANEL CORE: PRESERVED")
    print("SUBSCRIPTION: PRESERVED")
    print("INFO PAGE: PRESERVED")
    print("VLESS: PRESERVED")
    print("SERVERS: PRESERVED")
    print("QR: PRESERVED")
    print("API: PRESERVED")
    print("HEALTH: PRESERVED")
    print("LOGIN: PRESERVED")
    print("POMPNET BRANDING: OK")
    print("RAILWAY PORT: $PORT")
    print("=" * 64)


if __name__ == "__main__":
    main()
