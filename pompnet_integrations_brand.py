from pathlib import Path
import json
import os
import py_compile
import re
import tempfile

ROOT = Path("/app")
BOT = ROOT / "telegram_bot.py"
NEWS = ROOT / "news.json"
MARKER = "# POMP NET MOHAMMAD — SUPER JINX TELEGRAM BRAND V2"


def atomic_write(path: Path, content: str):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="",
            dir=str(path.parent), prefix=f".{path.name}.",
            suffix=".tmp", delete=False,
        ) as f:
            tmp = Path(f.name)
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count == 1:
        return source.replace(old, new, 1)
    if count == 0 and new in source:
        return source
    raise SystemExit(
        f"SAFE STOP: expected exactly one branding target; found {count}: {old[:100]}"
    )


def patch_bot():
    if not BOT.is_file():
        raise SystemExit("SAFE STOP: telegram_bot.py not found in pinned panel core")

    source = BOT.read_text(encoding="utf-8")
    if MARKER not in source:
        changes = (
            ('BOT_NAME = "ای اچ بی بات"', 'BOT_NAME = "POMP NET MOHAMMAD"'),
            ('BOT_NAME_EN = "AHB BOT"', 'BOT_NAME_EN = "POMP NET SUPER JINX"'),
            (
                'description=f"{BOT_NAME} ({BOT_NAME_EN}) — مدیریت کامل پنل AHBPanel از تلگرام",',
                'description=f"{BOT_NAME} — {BOT_NAME_EN} | مدیریت پنل اختصاصی محمد از تلگرام | @pompnet",',
            ),
            (
                'label = data.get("label") or "px-" + os.urandom(3).hex()',
                'label = data.get("label") or "POMP-NET-MOHAMMAD-SUPER-JINX-" + os.urandom(3).hex().upper()',
            ),
        )
        for old, new in changes:
            source = replace_once(source, old, new)

        welcome_pattern = re.compile(
            r"def _welcome_text\(\) -> str:\n.*?(?=\n\ndef _stats_text\(\) -> str:)",
            re.S,
        )
        welcome = '''def _welcome_text() -> str:
    return (
        f"⚡ <b>POMP NET MOHAMMAD</b> · <b>SUPER JINX</b>\\n"
        f"{'─' * 22}\\n"
        f"قدرت ساخت، آزادی انتخاب، کنترل در دستان تو\\n\\n"
        f"✨ مدیریت واقعی پنل از تلگرام\\n"
        f"🟢 ساخت و مدیریت کانفیگ‌ها\\n"
        f"📊 آمار زنده · 🔌 اتصالات\\n"
        f"📢 عضویت اجباری · 🗂 مدیریت ساب\\n\\n"
        f"📣 کانال رسمی: @pompnet\\n"
        f"🛟 پشتیبانی: @NovaTunneli\\n\\n"
        f"از منوی زیر یک بخش را انتخاب کنید:"
    )
'''
        source, count = welcome_pattern.subn(lambda _match: welcome.rstrip(), source, count=1)
        if count != 1:
            raise SystemExit("SAFE STOP: Telegram welcome function did not match exactly once")

        source = MARKER + "\n" + source

        with tempfile.TemporaryDirectory(prefix="pompnet-bot-check-") as folder:
            candidate = Path(folder) / "telegram_bot.py"
            candidate.write_text(source, encoding="utf-8")
            py_compile.compile(str(candidate), doraise=True)

        atomic_write(BOT, source)

    saved = BOT.read_text(encoding="utf-8")
    required = (
        MARKER,
        'BOT_NAME = "POMP NET MOHAMMAD"',
        'BOT_NAME_EN = "POMP NET SUPER JINX"',
        "POMP-NET-MOHAMMAD-SUPER-JINX-",
        "مدیریت واقعی پنل از تلگرام",
        "@pompnet",
        "@NovaTunneli",
        "مدیریت پنل اختصاصی محمد از تلگرام",
    )
    if any(item not in saved for item in required):
        raise SystemExit("SAFE STOP: Telegram SUPER JINX brand validation failed")

    forbidden_product_branding = (
        "AHB BOT",
        "ای اچ بی بات",
        "AHBPanel",
        "پنل AHB",
    )
    if any(item in saved for item in forbidden_product_branding):
        raise SystemExit("SAFE STOP: old panel/bot product branding remains")

    py_compile.compile(str(BOT), doraise=True)


def patch_news():
    if not NEWS.is_file():
        raise SystemExit("SAFE STOP: news.json not found")

    data = json.loads(NEWS.read_text(encoding="utf-8"))
    data["title"] = "اطلاعیه رسمی POMP NET MOHAMMAD — SUPER JINX"

    message = str(data.get("message") or "")
    message = message.replace("@ahb_panel", "@NovaTunneli")
    message = message.replace("@ahbpanel", "@NovaTunneli")

    if "POMP NET MOHAMMAD — SUPER JINX" not in message:
        message = message.rstrip() + (
            "\n\n━━━━━━━━━━━━━━━━━━"
            "\n⚡ POMP NET MOHAMMAD — SUPER JINX"
            "\nقدرت ساخت، آزادی انتخاب، کنترل در دستان تو"
            "\nپشتیبانی: @NovaTunneli"
            "\nکانال رسمی: @pompnet"
        )

    data["message"] = message
    atomic_write(NEWS, json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    saved = json.loads(NEWS.read_text(encoding="utf-8"))
    if (
        "@ahb_panel" in saved["message"]
        or "POMP NET MOHAMMAD" not in saved["title"]
        or "@pompnet" not in saved["message"]
        or "@NovaTunneli" not in saved["message"]
    ):
        raise SystemExit("SAFE STOP: Telegram news branding validation failed")

def main():
    patch_bot()
    patch_news()
    print("POMP NET MOHAMMAD — SUPER JINX TELEGRAM BRAND: OK")
    print("BOT IDENTITY, WELCOME, AUTO CONFIG LABELS AND NEWS: VERIFIED")
    print("TELEGRAM COMMANDS, CALLBACKS, PROTOCOL WIZARD AND CONFIG LOGIC: PRESERVED")
    print("UPSTREAM LICENSE AND COPYRIGHT NOTICES: PRESERVED")


if __name__ == "__main__":
    main()
