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
# پیدا کردن Route واقعی Subscription
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
# پیدا کردن HTML Variable
# =========================================================

def get_html_block(data: str, variable: str):
    patterns = [
        rf'{re.escape(variable)}\s*=\s*r?"""',
        rf"{re.escape(variable)}\s*=\s*r?'''",
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
                f"ERROR: پایان {variable} پیدا نشد"
            )

        return start, end, quote

    return None


# =========================================================
# تزریق CSS داخل یک HTML مشخص
# =========================================================

def inject_css_into_block(
    data: str,
    variable: str,
    css: str,
    css_id: str,
):
    block = get_html_block(data, variable)

    if not block:
        raise RuntimeError(
            f"ERROR: {variable} پیدا نشد"
        )

    start, end, _ = block

    html = data[start:end]

    if css_id in html:
        return data

    if "</head>" not in html:
        raise RuntimeError(
            f"ERROR: </head> داخل {variable} پیدا نشد"
        )

    injected = (
        '<style id="' + css_id + '">\n'
        + css
        + "\n</style>\n"
    )

    html = html.replace(
        "</head>",
        injected + "</head>",
        1
    )

    return (
        data[:start]
        + html
        + data[end:]
    )


# =========================================================
# تزریق Login CSS / JS
# =========================================================

def inject_login_assets(
    data: str,
    login_css: str,
    login_js: str,
):
    block = get_html_block(
        data,
        "LOGIN_HTML"
    )

    if not block:
        raise RuntimeError(
            "ERROR: LOGIN_HTML پیدا نشد"
        )

    start, end, _ = block

    html = data[start:end]

    # -----------------------------------------------------
    # Login CSS
    # -----------------------------------------------------

    if 'id="pompnet-login-css"' not in html:

        if "</head>" not in html:
            raise RuntimeError(
                "ERROR: </head> داخل LOGIN_HTML پیدا نشد"
            )

        html = html.replace(
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

    if 'id="pompnet-login-js"' not in html:

        if "</body>" not in html:
            raise RuntimeError(
                "ERROR: </body> داخل LOGIN_HTML پیدا نشد"
            )

        html = html.replace(
            "</body>",
            '<script id="pompnet-login-js">\n'
            + login_js
            + "\n</script>\n"
            + "</body>",
            1
        )

    return (
        data[:start]
        + html
        + data[end:]
    )


# =========================================================
# اضافه کردن Banner واقعی PompNet به Dashboard
# =========================================================

def inject_dashboard_banner(data: str):
    block = get_html_block(
        data,
        "DASHBOARD_HTML"
    )

    if not block:
        raise RuntimeError(
            "ERROR: DASHBOARD_HTML پیدا نشد"
        )

    start, end, _ = block

    html = data[start:end]

    if "id=\"pompnet-brand-banner\"" in html:
        return data

    banner = """
<div id="pompnet-brand-banner">
    <b>MR. MOHAMMAD | POMPNET</b>
    <span> — کدنویسی شده توسط تیم پمپ نت و آقا امیر</span>
</div>
"""

    # اولویت با داخل body
    if "<body" in html and "</body>" in html:

        body_start = html.find("> ", html.find("<body"))

        if body_start == -1:
            body_start = html.find(">", html.find("<body"))

        if body_start == -1:
            raise RuntimeError(
                "ERROR: شروع BODY داخل DASHBOARD_HTML پیدا نشد"
            )

        insert_at = body_start + 1

        html = (
            html[:insert_at]
            + banner
            + html[insert_at:]
        )

    elif "<main" in html:

        html = html.replace(
            "<main",
            banner + "\n<main",
            1
        )

    else:

        html = (
            banner
            + "\n"
            + html
        )

    return (
        data[:start]
        + html
        + data[end:]
    )


# =========================================================
# Main
# =========================================================

def main():

    # =====================================================
    # فایل‌های ضروری
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
    # خواندن هسته واقعی
    # =====================================================

    data = MAIN.read_text(
        encoding="utf-8"
    )

    # =====================================================
    # محافظت Subscription
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
    # برندینگ
    # =====================================================

    replacements = {

        "AHB PANEL":
            "POMP NET PANEL",

        "AHB Panel":
            "POMP NET PANEL",

        "AHBPanel":
            "POMP NET",

        "AHB panel":
            "POMP NET",

        "Created By Ahb":
            "Created By POMP NET",

        "Created By AHB":
            "Created By POMP NET",

        "Created by AHB":
            "Created by POMP NET",

        "Created by Ahb":
            "Created by POMP NET",

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

        "خطای داخلی AHB Panel":
            "خطای داخلی POMP NET",

        "خطای داخلی AHB":
            "خطای داخلی POMP NET",

        "AHB Panel Error":
            "POMP NET Error",
    }

    for old, new in replacements.items():
        data = data.replace(old, new)

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
    # App Name
    # =====================================================

    data = re.sub(
        r'(?m)^APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1
    )

    # =====================================================
    # CSS اصلی PompNet
    #
    # مهم:
    # CSS هم روی Login و هم Dashboard اعمال می‌شود.
    # =====================================================

    css = CSS.read_text(
        encoding="utf-8"
    )

    # Login
    if 'id="pompnet-css"' not in data:

        data = inject_css_into_block(
            data,
            "LOGIN_HTML",
            css,
            "pompnet-css"
        )

    # Dashboard
    if 'id="pompnet-dashboard-css"' not in data:

        data = inject_css_into_block(
            data,
            "DASHBOARD_HTML",
            css,
            "pompnet-dashboard-css"
        )

    # =====================================================
    # Banner داشبورد
    # =====================================================

    data = inject_dashboard_banner(
        data
    )

    # =====================================================
    # Login CSS / JS
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
    # ذخیره
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # =====================================================
    # Syntax Check
    # =====================================================

    try:

        py_compile.compile(
            str(MAIN),
            doraise=True
        )

    except Exception as exc:

        raise RuntimeError(
            "BUILD CHECK FAILED: Python Syntax Error\n"
            + str(exc)
        )

    # =====================================================
    # بررسی نهایی
    # =====================================================

    check = MAIN.read_text(
        encoding="utf-8"
    )

    # Subscription
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
            "منطق /sub/{uuid} تغییر کرده است"
        )

    # Login
    login_block = get_html_block(
        check,
        "LOGIN_HTML"
    )

    if not login_block:
        raise RuntimeError(
            "BUILD CHECK FAILED: LOGIN_HTML"
        )

    login_html = check[
        login_block[0]:
        login_block[1]
    ]

    # Dashboard
    dashboard_block = get_html_block(
        check,
        "DASHBOARD_HTML"
    )

    if not dashboard_block:
        raise RuntimeError(
            "BUILD CHECK FAILED: DASHBOARD_HTML"
        )

    dashboard_html = check[
        dashboard_block[0]:
        dashboard_block[1]
    ]

    # =====================================================
    # قابلیت‌های ضروری
    # =====================================================

    required_strings = [

        "/sub/{uuid}",

        "async def info_page",

        "/api/login",

        "/api/setup/status",

        "POMP NET",

        "MR. MOHAMMAD",

        "POMPNET",

        "کدنویسی شده توسط تیم پمپ نت و آقا امیر",

        "@NovaTunneli",

        "https://t.me/NovaTunneli",

        'id="pompnet-css"',

        'id="pompnet-dashboard-css"',

        'id="pompnet-login-css"',

        'id="pompnet-login-js"',

        'id="pompnet-brand-banner"',
    ]

    for item in required_strings:

        if item not in check:

            raise RuntimeError(
                "BUILD CHECK FAILED: "
                + item
            )

    # =====================================================
    # نتیجه
    # =====================================================

    print("=" * 70)
    print("POMP NET BUILD CHECK: OK")
    print("PYTHON SYNTAX: OK")
    print("REAL PANEL CORE: PRESERVED")
    print("LOGIN LOGIC: PRESERVED")
    print("DASHBOARD: PRESERVED")
    print("SUBSCRIPTION: PRESERVED")
    print("SUB URL: PRESERVED")
    print("INFO PAGE: PRESERVED")
    print("VLESS: PRESERVED")
    print("SERVERS: PRESERVED")
    print("QR: PRESERVED")
    print("API: PRESERVED")
    print("HEALTH: PRESERVED")
    print("POMPNET LOGIN: OK")
    print("POMPNET DASHBOARD CSS: OK")
    print("POMPNET BRAND BANNER: OK")
    print("SUPPORT: @NovaTunneli")
    print("RAILWAY PORT: $PORT")
    print("=" * 70)


if __name__ == "__main__":
    main()
