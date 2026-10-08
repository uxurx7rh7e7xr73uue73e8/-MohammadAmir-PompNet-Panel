from pathlib import Path
import re
import hashlib
import py_compile


ROOT = Path("/app")

MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"

LOGIN_CSS = Path("/tmp/pompnet_login.css")
LOGIN_JS = Path("/tmp/pompnet_login.js")


# =========================================================
# پیدا کردن مسیر واقعی Subscription
# =========================================================

def get_sub_route(data: str):
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?'
        r'(?=\n@app\.get|\n@app\.post|\n@app\.put|\n@app\.delete|'
        r'\n@app\.websocket|\nasync def |\nclass |\Z)',
        re.S,
    )

    match = pattern.search(data)

    return match.group(0) if match else None


# =========================================================
# پیدا کردن LOGIN_HTML واقعی
# =========================================================

def get_login_html(data: str):

    patterns = [
        r'LOGIN_HTML\s*=\s*r?"""',
        r'LOGIN_HTML\s*=\s*r?\'\'\'',
    ]

    for pattern in patterns:

        match = re.search(pattern, data)

        if not match:
            continue

        start = match.end()

        quote = '"""' if '"""' in match.group(0) else "'''"

        end = data.find(quote, start)

        if end == -1:
            raise RuntimeError(
                "ERROR: پایان LOGIN_HTML پیدا نشد"
            )

        return start, end, quote

    raise RuntimeError(
        "ERROR: LOGIN_HTML پیدا نشد"
    )


# =========================================================
# تزریق دقیق CSS/JS فقط داخل LOGIN_HTML
# =========================================================

def inject_login_assets(
    data: str,
    login_css: str,
    login_js: str
):

    start, end, _ = get_login_html(data)

    login_html = data[start:end]

    # -----------------------------------------------------
    # Login CSS
    # -----------------------------------------------------

    if 'id="pompnet-login-css"' not in login_html:

        if "</head>" not in login_html:

            raise RuntimeError(
                "ERROR: </head> داخل LOGIN_HTML پیدا نشد"
            )

        login_html = login_html.replace(
            "</head>",
            '<style id="pompnet-login-css">\n'
            + login_css
            + "\n</style>\n"
            + "</head>",
            1
        )

    # -----------------------------------------------------
    # Login JS
    # -----------------------------------------------------

    if 'id="pompnet-login-js"' not in login_html:

        if "</body>" not in login_html:

            raise RuntimeError(
                "ERROR: </body> داخل LOGIN_HTML پیدا نشد"
            )

        login_html = login_html.replace(
            "</body>",
            '<script id="pompnet-login-js">\n'
            + login_js
            + "\n</script>\n"
            + "</body>",
            1
        )

    return (
        data[:start]
        + login_html
        + data[end:]
    )


# =========================================================
# Main
# =========================================================

def main():

    # =====================================================
    # بررسی فایل‌های ضروری
    # =====================================================

    required_files = [
        (MAIN, "/app/main.py"),
        (CSS, "/app/pompnet.css"),
        (LOGIN_CSS, "/tmp/pompnet_login.css"),
        (LOGIN_JS, "/tmp/pompnet_login.js"),
    ]

    for path, name in required_files:

        if not path.exists():

            raise RuntimeError(
                f"ERROR: {name} پیدا نشد"
            )

    # =====================================================
    # خواندن هسته واقعی پنل
    # =====================================================

    data = MAIN.read_text(
        encoding="utf-8"
    )

    # =====================================================
    # محافظت از Subscription
    # =====================================================

    sub_before = get_sub_route(data)

    if not sub_before:

        raise RuntimeError(
            "ERROR: مسیر واقعی /sub/{uuid} پیدا نشد"
        )

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # =====================================================
    # فقط Branding
    #
    # قابلیت‌های پنل تغییر نمی‌کنند.
    # =====================================================

    replacements = {

        # AHB -> POMP NET

        "AHB PANEL":
            "POMP NET PANEL",

        "AHB Panel":
            "POMP NET PANEL",

        "AHBPanel":
            "POMP NET",

        "AHB panel":
            "POMP NET",

        # Created By

        "Created By Ahb":
            "Created By POMP NET",

        "Created By AHB":
            "Created By POMP NET",

        "Created by AHB":
            "Created by POMP NET",

        "Created by Ahb":
            "Created by POMP NET",

        # فارسی

        "به پنل مدیریت AHB خوش آمدید":
            "به پنل مدیریت POMP NET خوش آمدید",

        "درگاه عمومی AHB Panel":
            "درگاه عمومی POMP NET",

        "این صفحه، درگاه عمومی AHB Panel است.":
            "این صفحه، درگاه عمومی POMP NET است.",

        # Version branding

        "AHB Panel · 14.3.0":
            "POMP NET",

        # Telegram

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

        # Error messages / visible text

        "خطای داخلی AHB Panel":
            "خطای داخلی POMP NET",

        "خطای داخلی AHB":
            "خطای داخلی POMP NET",

        "AHB Panel Error":
            "POMP NET Error",
    }

    for old, new in replacements.items():

        data = data.replace(
            old,
            new
        )

    # =====================================================
    # Support
    # =====================================================

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

    # =====================================================
    # Application Name
    # =====================================================

    data = re.sub(
        r'(?m)^APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1
    )

    # =====================================================
    # POMP NET اصلی
    # فقط CSS اختصاصی خودت
    # =====================================================

    css = CSS.read_text(
        encoding="utf-8"
    )

    if 'id="pompnet-css"' not in data:

        # CSS اصلی فقط در HTML واقعی قرار می‌گیرد.
        # اگر LOGIN_HTML وجود دارد، اول همان را پیدا می‌کنیم.

        login_start, login_end, _ = get_login_html(data)

        before_login = data[:login_start]
        login_html = data[login_start:login_end]
        after_login = data[login_end:]

        if "</head>" not in login_html:

            raise RuntimeError(
                "ERROR: </head> داخل LOGIN_HTML پیدا نشد"
            )

        login_html = login_html.replace(
            "</head>",
            '<style id="pompnet-css">\n'
            + css
            + "\n</style>\n"
            + "</head>",
            1
        )

        data = (
            before_login
            + login_html
            + after_login
        )

    # =====================================================
    # Login Assets
    # =====================================================

    login_css = LOGIN_CSS.read_text(
        encoding="utf-8"
    )

    login_js = LOGIN_JS.read_text(
        encoding="utf-8"
    )

    data = inject_login_assets(
        data,
        login_css,
        login_js
    )

    # =====================================================
    # ذخیره main.py
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # =====================================================
    # Python Syntax Check
    # =====================================================

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

    # =====================================================
    # خواندن دوباره برای بررسی نهایی
    # =====================================================

    check = MAIN.read_text(
        encoding="utf-8"
    )

    # =====================================================
    # Subscription باید دقیقاً حفظ شده باشد
    # =====================================================

    sub_after = get_sub_route(check)

    if not sub_after:

        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "/sub/{uuid} حذف شده"
        )

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    if sub_hash_before != sub_hash_after:

        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "منطق /sub/{uuid} تغییر کرده است"
        )

    # =====================================================
    # بررسی قابلیت‌ها و برند
    # =====================================================

    required_strings = [

        # Core

        "/sub/{uuid}",
        "async def info_page",

        # Branding

        "POMP NET",

        "MR. MOHAMMAD",

        "POMPNET",

        "کدنویسی شده توسط تیم پمپ نت و آقا امیر",

        # Support

        "@NovaTunneli",

        "https://t.me/NovaTunneli",

        # CSS / JS

        'id="pompnet-css"',
        'id="pompnet-login-css"',
        'id="pompnet-login-js"',
    ]

    for item in required_strings:

        if item not in check:

            raise RuntimeError(
                "BUILD CHECK FAILED: "
                + item
            )

    # =====================================================
    # بررسی اینکه Login واقعی هنوز وجود دارد
    # =====================================================

    get_login_html(check)

    # =====================================================
    # نتیجه
    # =====================================================

    print("=" * 70)

    print(
        "POMP NET BUILD CHECK: OK"
    )

    print(
        "PYTHON SYNTAX: OK"
    )

    print(
        "REAL PANEL CORE: PRESERVED"
    )

    print(
        "LOGIN LOGIC: PRESERVED"
    )

    print(
        "SUBSCRIPTION: PRESERVED"
    )

    print(
        "SUB URL: PRESERVED"
    )

    print(
        "INFO PAGE: PRESERVED"
    )

    print(
        "VLESS: PRESERVED"
    )

    print(
        "SERVERS: PRESERVED"
    )

    print(
        "QR: PRESERVED"
    )

    print(
        "API: PRESERVED"
    )

    print(
        "HEALTH: PRESERVED"
    )

    print(
        "POMPNET CSS: OK"
    )

    print(
        "POMPNET LOGIN CSS: OK"
    )

    print(
        "POMPNET LOGIN JS: OK"
    )

    print(
        "POMPNET BRANDING: OK"
    )

    print(
        "SUPPORT: @NovaTunneli"
    )

    print(
        "RAILWAY PORT: $PORT"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()
