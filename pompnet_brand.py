from pathlib import Path
import re
import hashlib
import py_compile
import os
import tempfile


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
            raise RuntimeError(
                f"ERROR: پایان {variable} پیدا نشد"
            )

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
        raise RuntimeError(
            f"ERROR: {variable} پیدا نشد"
        )

    start, end, _ = block
    html = data[start:end]

    for old, new in replacements.items():
        html = html.replace(old, new)

    return data[:start] + html + data[end:]


def inject_css(data: str, variable: str, css: str, css_id: str):
    block = get_html_block(data, variable)

    if not block:
        raise RuntimeError(
            f"ERROR: {variable} پیدا نشد"
        )

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
        raise RuntimeError(
            "ERROR: LOGIN_HTML پیدا نشد"
        )

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
    # این تابع برای سازگاری با ساختار قبلی نگه داشته شده است.
    # در main() دیگر فراخوانی نمی‌شود و بنری اضافه نمی‌کند.
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
        html = html[:insert_at] + banner + html[insert_at:]
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


def replace_constant(data: str, name: str, value: str):
    pattern = re.compile(
        rf'^{re.escape(name)}\s*=\s*["\'][^"\']*["\']',
        re.M
    )

    updated, count = pattern.subn(
        f'{name} = "{value}"',
        data,
        count=1
    )

    if count != 1:
        raise RuntimeError(
            f"ERROR: مقدار {name} پیدا نشد؛ "
            "برای جلوگیری از تغییر اشتباه، عملیات متوقف شد."
        )

    return updated


def atomic_write(path: Path, content: str):
    """
    ابتدا فایل موقت می‌سازد و سپس با os.replace
    فایل نهایی را به‌صورت اتمیک جایگزین می‌کند.
    """

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)

            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(
            str(temp_path),
            str(path)
        )

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def main():

    # =========================================================
    # بررسی فایل‌های موردنیاز
    # =========================================================

    for path in (
        MAIN,
        CSS,
        LOGIN_CSS,
        LOGIN_JS
    ):
        if not path.exists():
            raise RuntimeError(
                f"ERROR: فایل موردنیاز پیدا نشد: {path}"
            )

    original_data = MAIN.read_text(
        encoding="utf-8"
    )

    data = original_data

    # =========================================================
    # حفاظت از مسیر Subscription
    # =========================================================

    sub_before = get_sub_route(original_data)

    if not sub_before:
        raise RuntimeError(
            "ERROR: مسیر واقعی /sub/{uuid} پیدا نشد"
        )

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # =========================================================
    # برند POMP NET و مشخصات پشتیبانی
    # =========================================================

    ui_replacements = {
        "AHB PANEL": "POMP NET",
        "AHB Panel": "POMP NET",
        "AHBPanel": "POMP NET",
        "AHB panel": "POMP NET",
        "ای اچ بی پنل": "آقای محمد پمپ‌نت پنل",
        "Created By Ahb": "Created By POMP NET",
        "Created By AHB": "Created By POMP NET",
        "Created by AHB": "Created by POMP NET",
        "Created by Ahb": "Created by POMP NET",
        "به پنل مدیریت AHB خوش آمدید":
            "به پنل مدیریت POMP NET خوش آمدید",
        "درگاه عمومی AHB Panel": "درگاه عمومی POMP NET",
        "این صفحه، درگاه عمومی AHB Panel است.":
            "این صفحه، درگاه عمومی POMP NET است.",
        "AHB Panel · 14.3.0": "POMP NET",
        "خطای داخلی AHB Panel": "خطای داخلی POMP NET",
        "خطای داخلی AHB": "خطای داخلی POMP NET",
        "AHB Panel Error": "POMP NET Error",
        "https://t.me/ahb_panel": "https://t.me/NovaTunneli",
        "https://t.me/ahbpanel": "https://t.me/NovaTunneli",
        "https://t.me/ahbpanelgap": "https://t.me/NovaTunneli",
        "https://t.me/logictop12": "https://t.me/NovaTunneli",
        "@ahb_panel": "@NovaTunneli",
        "@ahbpanel": "@NovaTunneli",
        "@ahbpanelgap": "@NovaTunneli",
        "reymit.ir/moditor": "@NovaTunneli",
        "https://github.com/ahb-panel/ahb_panel":
            "https://github.com/uxurx7rh7e7xr73uue73e8/-MohammadAmir-PompNet-Panel",
        "https://github.com/ahb-panell/ahb_panel":
            "https://github.com/uxurx7rh7e7xr73uue73e8/-MohammadAmir-PompNet-Panel",
        "ahb-panel/ahb_panel":
            "uxurx7rh7e7xr73uue73e8/-MohammadAmir-PompNet-Panel",
    }

    pages = (
        "LANDING_HTML",
        "LOGIN_HTML",
        "PUBLIC_SUB_HTML",
        "DASHBOARD_HTML"
    )

    for page in pages:
        data = replace_inside_html(
            data,
            page,
            ui_replacements
        )

    # =========================================================
    # جایگزینی AHB باقی‌مانده در HTML
    # =========================================================

    for page in pages:
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

        data = data[:start] + html + data[end:]

    # =========================================================
    # نام برنامه
    # =========================================================

    data = replace_constant(
        data,
        "APP_NAME",
        "آقای محمد پمپ‌نت پنل"
    )

    # =========================================================
    # پشتیبانی رسمی POMP NET
    # =========================================================

    data = replace_constant(
        data,
        "SUPPORT_USERNAME",
        "@NovaTunneli"
    )

    data = replace_constant(
        data,
        "SUPPORT_URL",
        "https://t.me/NovaTunneli"
    )

    # =========================================================
    # اضافه‌کردن CSS به صفحات موجود
    # =========================================================

    css = CSS.read_text(
        encoding="utf-8"
    )

    css_pages = (
        ("LANDING_HTML", "pompnet-landing-css"),
        ("LOGIN_HTML", "pompnet-main-login-css"),
        ("PUBLIC_SUB_HTML", "pompnet-public-sub-css"),
        ("DASHBOARD_HTML", "pompnet-dashboard-css"),
    )

    for page, css_id in css_pages:
        data = inject_css(
            data,
            page,
            css,
            css_id
        )

    # =========================================================
    # فایل‌های CSS و JavaScript صفحه ورود
    # =========================================================

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

    # =========================================================
    # حذف بنرهای قبلی از داشبورد و صفحه ساب
    # هیچ بنر جدیدی اضافه نمی‌شود.
    # =========================================================

    banner_ids = (
        "pompnet-brand-banner",
        "pompnet-sub-brand-banner",
    )

    for page in ("DASHBOARD_HTML", "PUBLIC_SUB_HTML"):
        block = get_html_block(data, page)

        if not block:
            raise RuntimeError(
                f"ERROR: {page} پیدا نشد"
            )

        start_html, end_html, _ = block
        html = data[start_html:end_html]

        for banner_id in banner_ids:
            banner_pattern = (
                r'<div\b(?=[^>]*\bid=["\']'
                + re.escape(banner_id)
                + r'["\'])[^>]*>.*?</div\s*>'
            )

            html = re.sub(
                banner_pattern,
                '',
                html,
                count=1,
                flags=re.I | re.S
            )

        data = data[:start_html] + html + data[end_html:]

    # =========================================================
    # بررسی مسیر Subscription قبل از ذخیره
    # =========================================================

    sub_after = get_sub_route(data)

    if not sub_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: مسیر /sub/{uuid} حذف شده است"
        )

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    if sub_hash_before != sub_hash_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "مسیر /sub/{uuid} تغییر کرده است"
        )

    # =========================================================
    # بررسی کد پایتون قبل از تغییر فایل اصلی
    # =========================================================

    with tempfile.TemporaryDirectory(
        prefix="pompnet-check-"
    ) as temp_dir:
        candidate = Path(temp_dir) / "main.py"

        candidate.write_text(
            data,
            encoding="utf-8"
        )

        py_compile.compile(
            str(candidate),
            doraise=True
        )

    check = data

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
    )

    for item in required:
        if item not in check:
            raise RuntimeError(
                f"BUILD CHECK FAILED: مورد ضروری پیدا نشد: {item}"
            )

    # =========================================================
    # بررسی برند قدیمی در رابط کاربری
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

    for page in pages:
        block = get_html_block(check, page)

        if not block:
            raise RuntimeError(
                f"BUILD CHECK FAILED: {page} پیدا نشد"
            )

        start, end, _ = block
        html = check[start:end]

        for item in forbidden:
            if item in html:
                raise RuntimeError(
                    "BUILD CHECK FAILED: "
                    f"برند قدیمی در {page} باقی مانده: {item}"
                )

    # =========================================================
    # بررسی نهایی حذف بنرهای سازنده
    # =========================================================

    for page in ("DASHBOARD_HTML", "PUBLIC_SUB_HTML"):
        block = get_html_block(check, page)

        if not block:
            raise RuntimeError(
                f"BUILD CHECK FAILED: {page} پیدا نشد"
            )

        start_html, end_html, _ = block
        html = check[start_html:end_html]

        for banner_id in banner_ids:
            if f'id="{banner_id}"' in html:
                raise RuntimeError(
                    f"BUILD CHECK FAILED: بنر {banner_id} "
                    f"در {page} باقی مانده است"
                )

    # =========================================================
    # ذخیره فقط پس از عبور از بررسی‌ها
    # =========================================================

    atomic_write(
        MAIN,
        check
    )

    # =========================================================
    # بررسی فایل ذخیره‌شده
    # =========================================================

    saved_data = MAIN.read_text(
        encoding="utf-8"
    )

    saved_sub = get_sub_route(saved_data)

    if not saved_sub:
        raise RuntimeError(
            "POST-WRITE CHECK FAILED: مسیر Subscription پیدا نشد"
        )

    saved_hash = hashlib.sha256(
        saved_sub.encode("utf-8")
    ).hexdigest()

    if saved_hash != sub_hash_before:
        raise RuntimeError(
            "POST-WRITE CHECK FAILED: "
            "هش مسیر Subscription تغییر کرده است"
        )

    # =========================================================
    # نتیجه
    # =========================================================

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("PYTHON SYNTAX: OK")
    print("APP NAME: UPDATED")
    print("SUPPORT: @NovaTunneli")
    print("BRANDING: POMP NET")
    print("LOGIN HTML: CHECKED")
    print("DASHBOARD HTML: CHECKED")
    print("SUBSCRIPTION HTML: CHECKED")
    print("SUBSCRIPTION ROUTE: PRESERVED")
    print("ATOMIC FILE WRITE: OK")
    print("=" * 60)


if __name__ == "__main__":
    main()
