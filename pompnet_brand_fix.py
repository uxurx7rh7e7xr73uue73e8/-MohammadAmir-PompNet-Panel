from pathlib import Path
import hashlib
import py_compile
import re
import tempfile

MAIN = Path("/app/main.py")

PAGES = (
    "LANDING_HTML",
    "LOGIN_HTML",
    "PUBLIC_SUB_HTML",
    "DASHBOARD_HTML",
)

REPLACEMENTS = {
    "AHB PANEL": "POMP NET",
    "AHB Panel": "POMP NET",
    "AHBPanel": "POMP NET",
    "AHB panel": "POMP NET",
    "AHB Panel Error": "POMP NET Error",
    "خطای داخلی AHB Panel": "خطای داخلی POMP NET",
    "خطای داخلی AHB": "خطای داخلی POMP NET",
    "به پنل مدیریت AHB خوش آمدید":
        "به پنل مدیریت POMP NET خوش آمدید",
    "درگاه عمومی AHB Panel":
        "درگاه عمومی POMP NET",
    "این صفحه، درگاه عمومی AHB Panel است.":
        "این صفحه، درگاه عمومی POMP NET است.",
    "https://t.me/ahb_panel":
        "https://t.me/NovaTunneli",
    "https://t.me/ahbpanel":
        "https://t.me/NovaTunneli",
    "@ahb_panel": "@NovaTunneli",
    "@ahbpanel": "@NovaTunneli",
    "https://github.com/ahb-panel/ahb_panel":
        "https://github.com/uxurx7rh7e7xr73uue73e8/-MohammadAmir-PompNet-Panel",
}


def get_html_block(source, name):
    pattern = (
        rf"(?m)^{re.escape(name)}\s*=\s*r?"
        rf"(?P<quote>'''|\"\"\")"
    )
    match = re.search(pattern, source)

    if not match:
        raise RuntimeError(
            f"صفحه {name} پیدا نشد؛ عملیات متوقف شد."
        )

    quote = match.group("quote")
    start = match.end()
    end = source.find(quote, start)

    if end < 0:
        raise RuntimeError(
            f"پایان HTML صفحه {name} پیدا نشد."
        )

    return start, end, source[start:end]


def get_subscription_route(source):
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?'
        r'(?=\n@app\.get|\n@app\.post|\n@app\.put|'
        r'\n@app\.delete|\n@app\.websocket|\nasync def |\nclass |\Z)',
        re.S,
    )

    match = pattern.search(source)

    if not match:
        raise RuntimeError(
            "مسیر ساب‌اسکریپشن پیدا نشد؛ عملیات متوقف شد."
        )

    return match.group(0)


def main():
    if not MAIN.is_file():
        raise RuntimeError(
            "فایل /app/main.py پیدا نشد."
        )

    original = MAIN.read_text(encoding="utf-8")

    route_before = hashlib.sha256(
        get_subscription_route(original).encode("utf-8")
    ).hexdigest()

    updated = original

    for page_name in PAGES:
        start, end, html = get_html_block(
            updated,
            page_name,
        )

        for old, new in REPLACEMENTS.items():
            html = html.replace(old, new)

        updated = updated[:start] + html + updated[end:]

    route_after = hashlib.sha256(
        get_subscription_route(updated).encode("utf-8")
    ).hexdigest()

    if route_before != route_after:
        raise RuntimeError(
            "مسیر ساب‌اسکریپشن تغییر کرده؛ ذخیره انجام نشد."
        )

    for page_name in PAGES:
        get_html_block(updated, page_name)

    with tempfile.TemporaryDirectory() as temp_dir:
        candidate = Path(temp_dir) / "main.py"
        candidate.write_text(updated, encoding="utf-8")
        py_compile.compile(str(candidate), doraise=True)

    if updated != original:
        MAIN.write_text(updated, encoding="utf-8")

    saved = MAIN.read_text(encoding="utf-8")

    py_compile.compile(
        str(MAIN),
        doraise=True,
    )

    route_saved = hashlib.sha256(
        get_subscription_route(saved).encode("utf-8")
    ).hexdigest()

    if route_saved != route_before:
        raise RuntimeError(
            "بررسی نهایی ساب‌اسکریپشن ناموفق بود."
        )

    print("POMP NET: بررسی برند انجام شد.")
    print("PYTHON SYNTAX: OK")
    print("SUBSCRIPTION ROUTE: PRESERVED")
    print("HTML PAGES: CHECKED")


if __name__ == "__main__":
    main()
