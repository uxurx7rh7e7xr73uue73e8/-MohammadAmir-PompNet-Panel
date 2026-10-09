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

    if re.search(
        r'<style\b[^>]*\bid=["\']'
        + re.escape(css_id)
        + r'["\']',
        html,
        re.I,
    ):
        return data

    if "</head>" not in html:
        raise RuntimeError(f"ERROR: </head> داخل {variable} پیدا نشد")

    tag = f'<style id="{css_id}">\n{css}\n</style>\n'
    html = html.replace("</head>", tag + "</head>", 1)

    return data[:start] + html + data[end:]


def inject_login_assets(data: str, login_css: str, login_js: str):
    block = get_html_block(data, "LOGIN_HTML")

    if not block:
        raise RuntimeError("ERROR: LOGIN_HTML پیدا نشد")

    start, end, _ = block
    html = data[start:end]

    if 'id="pompnet-login-css"' not in html:
        if "</head>" not in html:
            raise RuntimeError("ERROR: </head> داخل LOGIN_HTML پیدا نشد")

        html = html.replace(
            "</head>",
            '<style id="pompnet-login-css">\n'
            + login_css
            + "\n</style>\n</head>",
            1,
        )

    if 'id="pompnet-login-js"' not in html:
        if "</body>" not in html:
            raise RuntimeError("ERROR: </body> داخل LOGIN_HTML پیدا نشد")

        html = html.replace(
            "</body>",
            '<script id="pompnet-login-js">\n'
            + login_js
            + "\n</script>\n</body>",
            1,
        )

    return data[:start] + html + data[end:]


def replace_constant(data: str, name: str, value: str):
    pattern = re.compile(
        rf'^{re.escape(name)}\s*=\s*["\'][^"\']*["\']',
        re.M,
    )

    updated, count = pattern.subn(
        f'{name} = "{value}"',
        data,
        count=1,
    )

    if count != 1:
        raise RuntimeError(
            f"ERROR: مقدار {name} پیدا نشد؛ عملیات متوقف شد."
        )

    return updated


def atomic_write(path: Path, content: str):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            dir=str(path.parent),
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())

        os.replace(str(temp_path), str(path))

    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def remove_creator_banners(data: str, variable: str):
    """حذف متن سازنده و بنرهای مشخص‌شده، فقط از HTML صفحه موردنظر."""

    block = get_html_block(data, variable)

    if not block:
        raise RuntimeError(f"ERROR: {variable} پیدا نشد")

    start, end, _ = block
    html = data[start:end]

    # حذف دقیق متن، حتی اگر فاصله‌ها یا نوع نیم‌فاصله فرق داشته باشد.
    credit_patterns = [
        r'✦\s*کدنویسی\s*شده\s*توسط\s*تیم\s*پمپ[\s‌]*نت'
        r'\s*[•·\-–—]?\s*محمد\s*و\s*امیر\s*✦?',
        r'کدنویسی\s*شده\s*توسط\s*تیم\s*پمپ[\s‌]*نت'
        r'\s*[•·\-–—]?\s*محمد\s*و\s*امیر',
        r'کدنویسی\s*شده\s*توسط\s*تیم\s*پمپ[\s‌]*نت',
        r'کدنویسی\s*شده\s*توسط\s*پمپ[\s‌]*نت',
        r'Created\s+By\s+POMP\s+NET',
        r'Coded\s+by\s+POMP\s+NET(?:\s+team)?',
    ]

    for pattern in credit_patterns:
        html = re.sub(
            pattern,
            "",
            html,
            flags=re.I,
        )

    # حذف بنرهای مشخص، بدون دست‌زدن به بقیه عناصر صفحه.
    for banner_id in (
        "pompnet-brand-banner",
        "pompnet-sub-brand-banner",
    ):
        pattern = (
            r'<([a-z][a-z0-9]*)\b'
            r'(?=[^>]*\bid=["\']'
            + re.escape(banner_id)
            + r'["\'])[^>]*>.*?</\1\s*>'
        )

        html = re.sub(
            pattern,
            "",
            html,
            count=1,
            flags=re.I | re.S,
        )

    return data[:start] + html + data[end:]


def fix_dashboard_layout(css: str) -> str:
    """افزودن اصلاحات واکنش‌گرا به CSS داشبورد."""

    marker = "/* POMP NET DASHBOARD RESPONSIVE FIX */"

    if marker in css:
        return css

    layout_css = r"""

/* POMP NET DASHBOARD RESPONSIVE FIX */
html,
body {
    max-width: 100%;
    min-height: 100%;
    overflow-x: hidden;
}

* {
    box-sizing: border-box;
}

img,
video,
canvas,
svg {
    max-width: 100%;
}

table {
    max-width: 100%;
}

@media (max-width: 768px) {
    .dashboard,
    .dashboard-container,
    .dashboard-content,
    .main-content,
    .content-wrapper,
    .container {
        max-width: 100%;
        min-width: 0;
    }

    .dashboard,
    .dashboard-container,
    .dashboard-content,
    .main-content,
    .content-wrapper {
        padding-left: 12px;
        padding-right: 12px;
    }

    table {
        display: block;
        width: 100%;
        overflow-x: auto;
    }

    input,
    select,
    textarea,
    button {
        max-width: 100%;
    }
}
"""
    return css.rstrip() + "\n\n" + marker + "\n" + layout_css


def main():
    for path in (MAIN, CSS, LOGIN_CSS, LOGIN_JS):
        if not path.exists():
            raise RuntimeError(f"ERROR: فایل موردنیاز پیدا نشد: {path}")

    original_data = MAIN.read_text(encoding="utf-8")
    data = original_data

    # محافظت از مسیر Subscription
    sub_before = get_sub_route(original_data)

    if not sub_before:
        raise RuntimeError("ERROR: مسیر واقعی /sub/{uuid} پیدا نشد")

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    ui_replacements = {
        "AHB PANEL": "POMP NET",
        "AHB Panel": "POMP NET",
        "AHBPanel": "POMP NET",
        "AHB panel": "POMP NET",
        "ای اچ بی پنل": "POMP NET",

        "✦ کدنویسی شده توسط تیم پمپ‌نت • محمد و امیر ✦": "",
        "کدنویسی شده توسط تیم پمپ‌نت • محمد و امیر": "",
        "کدنویسی شده توسط تیم پمپ نت • محمد و امیر": "",
        "کدنویسی شده توسط پمپ نت و امیر": "",
        "کدنویسی شده توسط تیم پمپ نت": "",
        "کدنویسی شده توسط تیم پمپ‌نت": "",
        "کدنویسی شده توسط پمپ‌نت": "",
        "Created By Ahb": "",
        "Created By AHB": "",
        "Created by AHB": "",
        "Created by Ahb": "",
        "Coded by POMP NET team": "",
        "coded by POMP NET team": "",
        "Coded by POMP NET": "",

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
        "DASHBOARD_HTML",
    )

    for page in pages:
        data = replace_inside_html(data, page, ui_replacements)

    # جایگزینی برند قدیمی فقط در HTML صفحات شناخته‌شده
    for page in pages:
        block = get_html_block(data, page)

        if not block:
            raise RuntimeError(f"ERROR: {page} پیدا نشد")

        start, end, _ = block
        html = data[start:end]

        html = re.sub(
            r"(?<![A-Za-z0-9_])AHBPanel(?![A-Za-z0-9_])",
            "POMP NET",
            html,
        )
        html = re.sub(
            r"(?<![A-Za-z0-9_])AHB(?![A-Za-z0-9_])",
            "POMP NET",
            html,
        )

        data = data[:start] + html + data[end:]

    # حذف متن سازنده از داشبورد و صفحه سابسکریپشن
    for page in ("DASHBOARD_HTML", "PUBLIC_SUB_HTML"):
        data = remove_creator_banners(data, page)

    data = replace_constant(data, "APP_NAME", "POMP NET")
    data = replace_constant(data, "SUPPORT_USERNAME", "@NovaTunneli")
    data = replace_constant(
        data,
        "SUPPORT_URL",
        "https://t.me/NovaTunneli",
    )

    # خواندن و اصلاح CSS
    css = CSS.read_text(encoding="utf-8")
    css = fix_dashboard_layout(css)

    # درج CSS اصلاح‌شده در صفحات HTML
    css_pages = (
        ("LANDING_HTML", "pompnet-landing-css"),
        ("LOGIN_HTML", "pompnet-main-login-css"),
        ("PUBLIC_SUB_HTML", "pompnet-public-sub-css"),
        ("DASHBOARD_HTML", "pompnet-dashboard-css"),
    )

    for page, css_id in css_pages:
        data = inject_css(data, page, css, css_id)

    login_css = LOGIN_CSS.read_text(encoding="utf-8")
    login_js = LOGIN_JS.read_text(encoding="utf-8")

    data = inject_login_assets(data, login_css, login_js)

    # بررسی عدم تغییر مسیر سابسکریپشن
    sub_after = get_sub_route(data)

    if not sub_after:
        raise RuntimeError("BUILD CHECK FAILED: مسیر Subscription حذف شده است")

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    if sub_hash_before != sub_hash_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: مسیر Subscription تغییر کرده است"
        )

    # بررسی سینتکس Python پیش از ذخیره
    with tempfile.TemporaryDirectory(prefix="pompnet-check-") as temp_dir:
        candidate = Path(temp_dir) / "main.py"
        candidate.write_text(data, encoding="utf-8")
        py_compile.compile(str(candidate), doraise=True)

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
        if item not in data:
            raise RuntimeError(
                f"BUILD CHECK FAILED: مورد ضروری پیدا نشد: {item}"
            )

    # بررسی متن سازنده و برند قدیمی در صفحات
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
        "کدنویسی شده توسط تیم پمپ‌نت",
        "کدنویسی شده توسط تیم پمپ نت",
        "محمد و امیر",
    )

    for page in pages:
        block = get_html_block(data, page)

        if not block:
            raise RuntimeError(f"BUILD CHECK FAILED: {page} پیدا نشد")

        start, end, _ = block
        html = data[start:end]

        for item in forbidden:
            if item in html:
                raise RuntimeError(
                    f"BUILD CHECK FAILED: عبارت ناخواسته در {page}: {item}"
                )

    # ذخیره CSS با پشتیبان ویرایش‌نشده
    css_backup = CSS.with_suffix(".css.before-pompnet-fix.bak")

    if not css_backup.exists():
        atomic_write(css_backup, CSS.read_text(encoding="utf-8"))

    atomic_write(CSS, css)

    # ذخیره main.py فقط پس از عبور از بررسی‌ها
    main_backup = MAIN.with_suffix(".py.before-pompnet-brand.bak")

    if not main_backup.exists():
        atomic_write(main_backup, original_data)

    atomic_write(MAIN, data)

    # بررسی مجدد فایل ذخیره‌شده
    saved_data = MAIN.read_text(encoding="utf-8")
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
            "POST-WRITE CHECK FAILED: هش مسیر Subscription تغییر کرده است"
        )

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("PYTHON SYNTAX: OK")
    print("DASHBOARD CREATOR TEXT: REMOVED")
    print("DASHBOARD RESPONSIVE CSS: ADDED")
    print("SUPPORT: @NovaTunneli")
    print("SUBSCRIPTION ROUTE: PRESERVED")
    print("BACKUPS: CREATED IF NOT ALREADY PRESENT")
    print("=" * 60)


if __name__ == "__main__":
    main()
