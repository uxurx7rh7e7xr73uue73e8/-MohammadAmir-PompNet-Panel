from pathlib import Path
import re
import hashlib
import py_compile
import os
import base64
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



def apply_super_jinx_identity(data: str) -> str:
    """Brand new configuration remarks and add a dashboard identity banner."""
    name_pattern = re.compile(
        r"def random_config_name\(existing=None\):.*?\n\ndef now_ir\(\):",
        re.S,
    )
    replacement = '''def random_config_name(existing=None):
    existing = existing or set()
    for _ in range(80):
        name = "POMP-NET-MOHAMMAD-SUPER-JINX-" + secrets.token_hex(3).upper()
        if name not in existing:
            return name
    return "POMP-NET-MOHAMMAD-SUPER-JINX-" + secrets.token_hex(5).upper()


def sanitize_config_name(name: str) -> str:
    prefix = "POMP-NET-MOHAMMAD-SUPER-JINX"
    cleaned = "".join(
        ch for ch in str(name or "")
        if ch.isascii() and (ch.isalnum() or ch in "-_")
    ).strip("-_")
    if not cleaned or cleaned == prefix:
        return random_config_name()
    if cleaned.upper().startswith(prefix):
        return cleaned[:40]
    suffix = cleaned[:12].strip("-_")
    return (prefix + ("-" + suffix if suffix else "-" + secrets.token_hex(2).upper()))[:40]


def auto_config_name() -> str:
    return random_config_name()


def now_ir():'''
    data, count = name_pattern.subn(replacement, data, count=1)
    if count != 1:
        raise RuntimeError("SAFE STOP: config-name functions did not match exactly once")

    data = data.replace(
        'mix_label = "Mix-" + random_config_name()[:6]',
        'mix_label = "POMP-NET-MOHAMMAD-SUPER-JINX-MIX-" + secrets.token_hex(2).upper()',
    )

    banner = """<div id="pompnet-super-jinx-banner" role="region" aria-label="POMP NET SUPER JINX">
  <div class="pn-jinx-mark" aria-hidden="true"><img alt="" src="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20512%20512%22%3E%0A%3Cdefs%3E%0A%20%3ClinearGradient%20id%3D%22bg%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%2307152b%22%2F%3E%3Cstop%20offset%3D%22.52%22%20stop-color%3D%22%23100a2a%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23210b3b%22%2F%3E%3C%2FlinearGradient%3E%0A%20%3ClinearGradient%20id%3D%22wing%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%2325baff%22%2F%3E%3Cstop%20offset%3D%22.48%22%20stop-color%3D%22%237552ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23d45bff%22%2F%3E%3C%2FlinearGradient%3E%0A%20%3ClinearGradient%20id%3D%22metal%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%220%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%23fff%22%2F%3E%3Cstop%20offset%3D%22.4%22%20stop-color%3D%22%23c9d9ff%22%2F%3E%3Cstop%20offset%3D%22.72%22%20stop-color%3D%22%238b63ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23fff%22%2F%3E%3C%2FlinearGradient%3E%0A%20%3CradialGradient%20id%3D%22core%22%3E%3Cstop%20stop-color%3D%22%23ffffff%22%2F%3E%3Cstop%20offset%3D%22.25%22%20stop-color%3D%22%237de4ff%22%2F%3E%3Cstop%20offset%3D%22.62%22%20stop-color%3D%22%235e48ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23170b35%22%2F%3E%3C%2FradialGradient%3E%0A%20%3Cfilter%20id%3D%22glow%22%3E%3CfeGaussianBlur%20stdDeviation%3D%2210%22%20result%3D%22b%22%2F%3E%3CfeMerge%3E%3CfeMergeNode%20in%3D%22b%22%2F%3E%3CfeMergeNode%20in%3D%22SourceGraphic%22%2F%3E%3C%2FfeMerge%3E%3C%2Ffilter%3E%0A%3C%2Fdefs%3E%0A%3Crect%20x%3D%2212%22%20y%3D%2212%22%20width%3D%22488%22%20height%3D%22488%22%20rx%3D%22112%22%20fill%3D%22url(%23bg)%22%20stroke%3D%22url(%23wing)%22%20stroke-width%3D%2210%22%2F%3E%0A%3Ccircle%20cx%3D%22256%22%20cy%3D%22256%22%20r%3D%22205%22%20fill%3D%22none%22%20stroke%3D%22%238a63ff%22%20stroke-opacity%3D%22.22%22%20stroke-width%3D%223%22%2F%3E%0A%3Cg%20filter%3D%22url(%23glow)%22%20fill%3D%22url(%23wing)%22%20stroke%3D%22%23a6dfff%22%20stroke-opacity%3D%22.45%22%20stroke-width%3D%223%22%3E%0A%20%3Cpath%20d%3D%22M230%20248C174%20191%20119%20145%2053%20127c32%2050%2057%2085%2099%20117-45-22-83-31-124-30%2049%2038%2091%2063%20145%2075-37-4-70%201-103%2013%2061%2023%20111%2031%20166%2015z%22%2F%3E%0A%20%3Cpath%20d%3D%22M282%20248c56-57%20111-103%20177-121-32%2050-57%2085-99%20117%2045-22%2083-31%20124-30-49%2038-91%2063-145%2075%2037-4%2070%201%20103%2013-61%2023-111%2031-166%2015z%22%2F%3E%0A%20%3Cpath%20d%3D%22M221%20267c-56%201-111%2018-164%2053%2050%205%2088%203%20132-7-37%2021-63%2045-85%2075%2064-18%20112-41%20155-82z%22%2F%3E%0A%20%3Cpath%20d%3D%22M291%20267c56%201%20111%2018%20164%2053-50%205-88%203-132-7%2037%2021%2063%2045%2085%2075-64-18-112-41-155-82z%22%2F%3E%0A%3C%2Fg%3E%0A%3Cg%20filter%3D%22url(%23glow)%22%3E%0A%20%3Cpath%20d%3D%22M180%20153l25-59%2051%2044%2051-44%2025%2059-25%2022H205z%22%20fill%3D%22url(%23metal)%22%20stroke%3D%22%239feaff%22%20stroke-width%3D%225%22%2F%3E%0A%20%3Ccircle%20cx%3D%22205%22%20cy%3D%22105%22%20r%3D%2210%22%20fill%3D%22%23fff%22%2F%3E%3Ccircle%20cx%3D%22256%22%20cy%3D%22137%22%20r%3D%2212%22%20fill%3D%22%23fff%22%2F%3E%3Ccircle%20cx%3D%22307%22%20cy%3D%22105%22%20r%3D%2210%22%20fill%3D%22%23fff%22%2F%3E%0A%20%3Cpath%20d%3D%22M256%20165l89%2082-29%20125-60%2050-60-50-29-125z%22%20fill%3D%22url(%23core)%22%20stroke%3D%22url(%23metal)%22%20stroke-width%3D%229%22%2F%3E%0A%20%3Cpath%20d%3D%22M256%20202l-24%2062%2031-8-12%2070%2042-82-32%208%2018-50z%22%20fill%3D%22%23fff%22%20filter%3D%22url(%23glow)%22%2F%3E%0A%3C%2Fg%3E%0A%3Cpath%20d%3D%22M256%2034v34M239%2051h34M62%20256h34M416%20256h34M256%20416v34%22%20stroke%3D%22%23b7eaff%22%20stroke-width%3D%224%22%20stroke-linecap%3D%22round%22%20opacity%3D%22.7%22%2F%3E%0A%3C%2Fsvg%3E"></div>
  <div class="pn-jinx-copy">
    <strong>POMP NET MOHAMMAD <em>SUPER JINX</em></strong>
    <small>قدرت ساخت، آزادی انتخاب، کنترل در دستان تو</small>
    <p>پنل مدیریت و اشتراک اختصاصی محمد؛ مدیریت کانفیگ‌ها، کاربران و سرویس‌ها در یک محیط یکپارچه.</p>
  </div>
  <span class="pn-jinx-status"><i></i> SUPER JINX SYSTEM</span>
</div>"""
    # SUPER JINX SHARED WINGED ARTWORK
    login_js_source = LOGIN_JS.read_text(encoding="utf-8")
    logo_match = re.search(r"const logoSvg = [\x60]([\s\S]*?)[\x60];", login_js_source)
    if not logo_match:
        raise RuntimeError("SAFE STOP: shared SUPER JINX logo artwork not found")
    logo_b64 = base64.b64encode(logo_match.group(1).encode("utf-8")).decode("ascii")
    logo_uri = "data:image/svg+xml;base64," + logo_b64
    mark_pattern = re.compile(
        r'(<div class="pn-jinx-mark" aria-hidden="true"><img alt="" src=")[^"]+("></div>)'
    )
    banner, logo_count = mark_pattern.subn(
        lambda match: match.group(1) + logo_uri + match.group(2),
        banner,
        count=1,
    )
    if logo_count != 1:
        raise RuntimeError("SAFE STOP: dashboard logo image anchor did not match exactly once")

    page = "DASHBOARD_HTML"
    block = get_html_block(data, page)
    if not block:
        raise RuntimeError("SAFE STOP: dashboard page not found for brand banner")
    start, end, _ = block
    html = data[start:end]
    if 'id="pompnet-super-jinx-banner"' not in html:
        main_anchor = '<main class="main" id="main">'
        if main_anchor not in html:
            raise RuntimeError("SAFE STOP: dashboard main container not found")
        html = html.replace(main_anchor, main_anchor + "\n" + banner, 1)
        data = data[:start] + html + data[end:]
    return data


def main():
    for path in (MAIN, CSS, LOGIN_CSS, LOGIN_JS):
        if not path.exists():
            raise RuntimeError(f"ERROR: فایل موردنیاز پیدا نشد: {path}")

    original_data = MAIN.read_text(encoding="utf-8")
    data = original_data
    data = apply_super_jinx_identity(data)

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
            "به پنل پمپ نت محمد خوش آمدید",
        "به پنل مدیریت POMP NET خوش آمدید":
            "به پنل پمپ نت محمد خوش آمدید",
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

    # POMP NET SUPER JINX LANDING PORTAL DESIGN
    landing_logo = "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20512%20512%22%3E%0A%3Cdefs%3E%0A%20%3ClinearGradient%20id%3D%22bg%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%2307152b%22%2F%3E%3Cstop%20offset%3D%22.52%22%20stop-color%3D%22%23100a2a%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23210b3b%22%2F%3E%3C%2FlinearGradient%3E%0A%20%3ClinearGradient%20id%3D%22wing%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%221%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%2325baff%22%2F%3E%3Cstop%20offset%3D%22.48%22%20stop-color%3D%22%237552ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23d45bff%22%2F%3E%3C%2FlinearGradient%3E%0A%20%3ClinearGradient%20id%3D%22metal%22%20x1%3D%220%22%20y1%3D%220%22%20x2%3D%220%22%20y2%3D%221%22%3E%3Cstop%20stop-color%3D%22%23fff%22%2F%3E%3Cstop%20offset%3D%22.4%22%20stop-color%3D%22%23c9d9ff%22%2F%3E%3Cstop%20offset%3D%22.72%22%20stop-color%3D%22%238b63ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23fff%22%2F%3E%3C%2FlinearGradient%3E%0A%20%3CradialGradient%20id%3D%22core%22%3E%3Cstop%20stop-color%3D%22%23ffffff%22%2F%3E%3Cstop%20offset%3D%22.25%22%20stop-color%3D%22%237de4ff%22%2F%3E%3Cstop%20offset%3D%22.62%22%20stop-color%3D%22%235e48ff%22%2F%3E%3Cstop%20offset%3D%221%22%20stop-color%3D%22%23170b35%22%2F%3E%3C%2FradialGradient%3E%0A%20%3Cfilter%20id%3D%22glow%22%3E%3CfeGaussianBlur%20stdDeviation%3D%2210%22%20result%3D%22b%22%2F%3E%3CfeMerge%3E%3CfeMergeNode%20in%3D%22b%22%2F%3E%3CfeMergeNode%20in%3D%22SourceGraphic%22%2F%3E%3C%2FfeMerge%3E%3C%2Ffilter%3E%0A%3C%2Fdefs%3E%0A%3Crect%20x%3D%2212%22%20y%3D%2212%22%20width%3D%22488%22%20height%3D%22488%22%20rx%3D%22112%22%20fill%3D%22url(%23bg)%22%20stroke%3D%22url(%23wing)%22%20stroke-width%3D%2210%22%2F%3E%0A%3Ccircle%20cx%3D%22256%22%20cy%3D%22256%22%20r%3D%22205%22%20fill%3D%22none%22%20stroke%3D%22%238a63ff%22%20stroke-opacity%3D%22.22%22%20stroke-width%3D%223%22%2F%3E%0A%3Cg%20filter%3D%22url(%23glow)%22%20fill%3D%22url(%23wing)%22%20stroke%3D%22%23a6dfff%22%20stroke-opacity%3D%22.45%22%20stroke-width%3D%223%22%3E%0A%20%3Cpath%20d%3D%22M230%20248C174%20191%20119%20145%2053%20127c32%2050%2057%2085%2099%20117-45-22-83-31-124-30%2049%2038%2091%2063%20145%2075-37-4-70%201-103%2013%2061%2023%20111%2031%20166%2015z%22%2F%3E%0A%20%3Cpath%20d%3D%22M282%20248c56-57%20111-103%20177-121-32%2050-57%2085-99%20117%2045-22%2083-31%20124-30-49%2038-91%2063-145%2075%2037-4%2070%201%20103%2013-61%2023-111%2031-166%2015z%22%2F%3E%0A%20%3Cpath%20d%3D%22M221%20267c-56%201-111%2018-164%2053%2050%205%2088%203%20132-7-37%2021-63%2045-85%2075%2064-18%20112-41%20155-82z%22%2F%3E%0A%20%3Cpath%20d%3D%22M291%20267c56%201%20111%2018%20164%2053-50%205-88%203-132-7%2037%2021%2063%2045%2085%2075-64-18-112-41-155-82z%22%2F%3E%0A%3C%2Fg%3E%0A%3Cg%20filter%3D%22url(%23glow)%22%3E%0A%20%3Cpath%20d%3D%22M180%20153l25-59%2051%2044%2051-44%2025%2059-25%2022H205z%22%20fill%3D%22url(%23metal)%22%20stroke%3D%22%239feaff%22%20stroke-width%3D%225%22%2F%3E%0A%20%3Ccircle%20cx%3D%22205%22%20cy%3D%22105%22%20r%3D%2210%22%20fill%3D%22%23fff%22%2F%3E%3Ccircle%20cx%3D%22256%22%20cy%3D%22137%22%20r%3D%2212%22%20fill%3D%22%23fff%22%2F%3E%3Ccircle%20cx%3D%22307%22%20cy%3D%22105%22%20r%3D%2210%22%20fill%3D%22%23fff%22%2F%3E%0A%20%3Cpath%20d%3D%22M256%20165l89%2082-29%20125-60%2050-60-50-29-125z%22%20fill%3D%22url(%23core)%22%20stroke%3D%22url(%23metal)%22%20stroke-width%3D%229%22%2F%3E%0A%20%3Cpath%20d%3D%22M256%20202l-24%2062%2031-8-12%2070%2042-82-32%208%2018-50z%22%20fill%3D%22%23fff%22%20filter%3D%22url(%23glow)%22%2F%3E%0A%3C%2Fg%3E%0A%3Cpath%20d%3D%22M256%2034v34M239%2051h34M62%20256h34M416%20256h34M256%20416v34%22%20stroke%3D%22%23b7eaff%22%20stroke-width%3D%224%22%20stroke-linecap%3D%22round%22%20opacity%3D%22.7%22%2F%3E%0A%3C%2Fsvg%3E"
    landing_changes = {
        "<title>POMP NET</title>": "<title>POMP NET MOHAMMAD — SUPER JINX</title>",
        '<div class="card">': '<div class="card pompnet-entry-card">',
        '<div class="logo">P</div>': '<div class="logo pompnet-entry-logo"><img src="' + landing_logo + '" alt="POMP NET SUPER JINX"></div>',
        '<div class="brand-name">\nPOMP NET\n</div>': '<div class="brand-name">POMP NET MOHAMMAD</div>',
        '<div class="version">\n14.3.0\n</div>': '<div class="version">SUPER JINX · SECURE ACCESS</div>',
        '<div class="status">\n● سیستم آنلاین و فعال است\n</div>': '<div class="status">● درگاه رسمی ورود به پنل</div>',
        '<h1>\nبرای ورود به پنل\n<br>\nابتدا وارد شوید\n</h1>': '<h1>به دنیای SUPER JINX خوش آمدید</h1>',
        'این صفحه، درگاه عمومی POMP NET است.\nبرای دسترسی به داشبورد مدیریت از مسیر ورود استفاده کنید.': 'مرکز اختصاصی مدیریت کاربران، ساخت کانفیگ و اشتراک‌های POMP NET MOHAMMAD؛ برای ورود امن به داشبورد، ادامه دهید.',
        '<div class="path">\n/login\n</div>': '<div class="path">POMP NET MOHAMMAD · SUPER JINX</div>',
        'ورود به پنل': 'ورود امن به پنل',
        '<span>\\nPOMP NET\\n</span>': '<span>POMP NET MOHAMMAD — SUPER JINX</span>',
    }
    data = replace_inside_html(data, "LANDING_HTML", landing_changes)

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
