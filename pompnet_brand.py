from pathlib import Path
import re
import hashlib
import py_compile

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"
LOGIN_CSS = Path("/tmp/pompnet_login.css")
LOGIN_JS = Path("/tmp/pompnet_login.js")


def get_html_block(data: str, variable: str):
    patterns = [
        rf'{re.escape(variable)}\s*=\s*r?"""',
        rf"{re.escape(variable)}\s*=\s*r?'''",
    ]

    for pattern in patterns:
        match = re.search(pattern, data)

        if not match:
            continue

        quote = '"""' if '"""' in match.group(0) else "'''"
        start = match.end()
        end = data.find(quote, start)

        if end == -1:
            raise RuntimeError(f"ERROR: پایان {variable} پیدا نشد")

        return start, end, quote

    return None


def get_sub_route(data: str):
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?'
        r'(?=\n@app\.get|\n@app\.post|\n@app\.put|'
        r'\n@app\.delete|\n@app\.websocket|\nasync def |\nclass |\Z)',
        re.S,
    )

    match = pattern.search(data)

    return match.group(0) if match else None


def replace_inside_html(data: str, variable: str, replacements: dict):
    block = get_html_block(data, variable)

    if not block:
        raise RuntimeError(f"ERROR: {variable} پیدا نشد")

    start, end, _ = block
    html = data[start:end]

    for old, new in replacements.items():
        html = html.replace(old, new)

    return data[:start] + html + data[end:]


def inject_css(data: str, variable: str, css: str, css_id: str):
    block = get_html_block(data, variable)

    if not block:
        raise RuntimeError(f"ERROR: {variable} پیدا نشد")

    start, end, _ = block
    html = data[start:end]

    if f'id="{css_id}"' in html:
        return data

    if "</head>" not in html:
        raise RuntimeError(
            f"ERROR: </head> داخل {variable} پیدا نشد"
        )

    tag = (
        f'<style id="{css_id}">\n'
        f'{css}\n'
        f'</style>\n'
    )

    html = html.replace(
        "</head>",
        tag + "</head>",
        1
    )

    return data[:start] + html + data[end:]


def inject_login_assets(data: str, login_css: str, login_js: str):
    block = get_html_block(data, "LOGIN_HTML")

    if not block:
        raise RuntimeError("ERROR: LOGIN_HTML پیدا نشد")

    start, end, _ = block
    html = data[start:end]

    if 'id="pompnet-login-css"' not in html:
        if "</head>" not in html:
            raise RuntimeError(
                "ERROR: </head> داخل LOGIN_HTML پیدا نشد"
            )

        html = html.replace(
            "</head>",
            '<style id="pompnet-login-css">\n'
            + login_css
            + "\n</style>\n</head>",
            1
        )

    if 'id="pompnet-login-js"' not in html:
        if "</body>" not in html:
            raise RuntimeError(
                "ERROR: </body> داخل LOGIN_HTML پیدا نشد"
            )

        html = html.replace(
            "</body>",
            '<script id="pompnet-login-js">\n'
            + login_js
            + "\n</script>\n</body>",
            1
        )

    return data[:start] + html + data[end:]


def inject_banner(data: str, variable: str, element_id: str, text: str):
    block = get_html_block(data, variable)

    if not block:
        raise RuntimeError(
            f"ERROR: {variable} پیدا نشد"
        )

    start, end, _ = block
    html = data[start:end]

    if f'id="{element_id}"' in html:
        return data

    banner = f'''
<div id="{element_id}">
    <span class="pompnet-banner-text">
        {text}
    </span>
</div>
'''

    body_match = re.search(
        r"<body\b[^>]*>",
        html,
        re.I
    )

    if body_match:
        insert_at = body_match.end()

        html = (
            html[:insert_at]
            + banner
            + html[insert_at:]
        )

    else:
        main_match = re.search(
            r"<main\b",
            html,
            re.I
        )

        if not main_match:
            raise RuntimeError(
                f"ERROR: محل Banner در {variable} پیدا نشد"
            )

        html = (
            html[:main_match.start()]
            + banner
            + "\n"
            + html[main_match.start():]
        )

    return data[:start] + html + data[end:]


def main():

    for path in (
        MAIN,
        CSS,
        LOGIN_CSS,
        LOGIN_JS
    ):
        if not path.exists():
            raise RuntimeError(
                f"ERROR: {path} پیدا نشد"
            )

    data = MAIN.read_text(
        encoding="utf-8"
    )

    # =========================================================
    # حفاظت از Subscription واقعی
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
    # فقط برند و متن‌های قابل مشاهده
    # =========================================================

    ui_replacements = {

        "AHB PANEL":
            "POMP NET",

        "AHB Panel":
            "POMP NET",

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

        "خطای داخلی AHB Panel":
            "خطای داخلی POMP NET",

        "خطای داخلی AHB":
            "خطای داخلی POMP NET",

        "AHB Panel Error":
            "POMP NET Error",

        "https://t.me/ahb_panel":
            "https://t.me/NovaTunneli",

        "https://t.me/ahbpanel":
            "https://t.me/NovaTunneli",

        "https://t.me/ahbpanelgap":
            "https://t.me/NovaTunneli",

        "https://t.me/logictop12":
            "https://t.me/NovaTunneli",

        "@ahb_panel":
            "@NovaTunneli",

        "@ahbpanel":
            "@NovaTunneli",

        "@ahbpanelgap":
            "@NovaTunneli",

        "reymit.ir/moditor":
            "@NovaTunneli",

        "https://github.com/ahb-panel/ahb_panel":
            "https://github.com/uxurx7rh7e7xr73uue73e8/-MohammadAmir-PompNet-Panel",

        "ahb-panel/ahb_panel":
            "uxurx7rh7e7xr73uue73e8/-MohammadAmir-PompNet-Panel",
    }

    for page in (
        "LANDING_HTML",
        "LOGIN_HTML",
        "PUBLIC_SUB_HTML",
        "DASHBOARD_HTML"
    ):

        data = replace_inside_html(
            data,
            page,
            ui_replacements
        )

    # =========================================================
    # حذف هر AHB مستقل باقی‌مانده فقط از HTML
    # =========================================================

    for page in (
        "LANDING_HTML",
        "LOGIN_HTML",
        "PUBLIC_SUB_HTML",
        "DASHBOARD_HTML"
    ):

        block = get_html_block(data, page)

        if not block:
            raise RuntimeError(
                f"ERROR: {page} پیدا نشد"
            )

        start, end, _ = block
        html = data[start:end]

        html = re.sub(
            r"(?<![A-Za-z0-9_])AHB(?![A-Za-z0-9_])",
            "POMP NET",
            html
        )

        html = re.sub(
            r"(?<![A-Za-z0-9_])AHBPanel(?![A-Za-z0-9_])",
            "POMP NET",
            html
        )

        data = (
            data[:start]
            + html
            + data[end:]
        )

    # =========================================================
    # نام نمایشی برنامه
    # =========================================================

    data = re.sub(
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1
    )

    # =========================================================
    # پشتیبانی POMP NET
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
    # CSS اصلی POMP NET
    # =========================================================

    css = CSS.read_text(
        encoding="utf-8"
    )

    for page, css_id in (
        (
            "LANDING_HTML",
            "pompnet-landing-css"
        ),
        (
            "LOGIN_HTML",
            "pompnet-main-login-css"
        ),
        (
            "PUBLIC_SUB_HTML",
            "pompnet-public-sub-css"
        ),
        (
            "DASHBOARD_HTML",
            "pompnet-dashboard-css"
        ),
    ):

        data = inject_css(
            data,
            page,
            css,
            css_id
        )

    # =========================================================
    # قالب Login اختصاصی
    # =========================================================

    data = inject_login_assets(
        data,
        LOGIN_CSS.read_text(
            encoding="utf-8"
        ),
        LOGIN_JS.read_text(
            encoding="utf-8"
        )
    )

    # =========================================================
    # برند POMP NET
    # =========================================================

    data = inject_banner(
        data,
        "DASHBOARD_HTML",
        "pompnet-brand-banner",
        "✦ کدنویسی شده توسط تیم پمپ‌نت • آقا امیر ✦"
    )

    data = inject_banner(
        data,
        "PUBLIC_SUB_HTML",
        "pompnet-sub-brand-banner",
        "✦ کدنویسی شده توسط تیم پمپ‌نت • آقا امیر ✦"
    )

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # =========================================================
    # Syntax Check
    # =========================================================

    py_compile.compile(
        str(MAIN),
        doraise=True
    )

    check = MAIN.read_text(
        encoding="utf-8"
    )

    # =========================================================
    # Subscription نباید تغییر کرده باشد
    # =========================================================

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
            "/sub/{uuid} تغییر کرده است"
        )

    # =========================================================
    # موارد ضروری
    # =========================================================

    required = (
        "/sub/{uuid}",
        "/api/login",
        "/api/setup/status",
        "POMP NET",
        "@NovaTunneli",
        'id="pompnet-main-login-css"',
        'id="pompnet-public-sub-css"',
        'id="pompnet-dashboard-css"',
        'id="pompnet-login-css"',
        'id="pompnet-login-js"',
        'id="pompnet-brand-banner"',
        'id="pompnet-sub-brand-banner"',
    )

    for item in required:

        if item not in check:
            raise RuntimeError(
                f"BUILD CHECK FAILED: {item}"
            )

    # =========================================================
    # هیچ برند قدیمی نباید در UI باقی بماند
    # =========================================================

    forbidden = (
        "AHB PANEL",
        "AHB Panel",
        "AHBPanel",
        "AHB panel",
        "ای اچ بی پنل",
        "https://t.me/ahb_panel",
        "https://t.me/ahbpanel",
        "https://t.me/logictop12",
        "ahb-panel/ahb_panel",
    )

    for page in (
        "LANDING_HTML",
        "LOGIN_HTML",
        "PUBLIC_SUB_HTML",
        "DASHBOARD_HTML"
    ):

        block = get_html_block(
            check,
            page
        )

        if not block:
            raise RuntimeError(
                f"BUILD CHECK FAILED: {page}"
            )

        start, end, _ = block
        html = check[start:end]

        for item in forbidden:

            if item in html:

                raise RuntimeError(
                    "BUILD CHECK FAILED: "
                    f"برند قدیمی در UI باقی مانده: {item}"
                )

    # =========================================================
    # نتیجه
    # =========================================================

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("REAL AHB CORE: PRESERVED")
    print("REAL LOGIN: PRESERVED")
    print("REAL DASHBOARD: PRESERVED")
    print("REAL SUBSCRIPTION: PRESERVED")
    print("REAL /sub/{uuid}: PRESERVED")
    print("PYTHON SYNTAX: OK")
    print("OLD UI BRANDING: REMOVED")
    print("SUPPORT: @NovaTunneli")
    print("BRAND: POMP NET")
    print("=" * 60)


if __name__ == "__main__":
    main()
