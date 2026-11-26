from pathlib import Path
import json
import os
import py_compile
import tempfile

ROOT = Path("/app")
BOT = ROOT / "telegram_bot.py"
NEWS = ROOT / "news.json"
MARKER = "# POMP NET SUPER JINX TELEGRAM BRAND"

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
    raise SystemExit(f"SAFE STOP: expected one branding marker; found {count}: {old[:90]}")

def patch_bot():
    if not BOT.is_file():
        raise SystemExit("SAFE STOP: telegram_bot.py not found")
    source = BOT.read_text(encoding="utf-8")
    if MARKER not in source:
        changes = (
            ('BOT_NAME = "ای اچ بی بات"', 'BOT_NAME = "POMP NET MOHAMMAD"'),
            ('BOT_NAME_EN = "AHB BOT"', 'BOT_NAME_EN = "POMP NET SUPER JINX"'),
            ('از ای اچ بی بات', 'از ربات POMP NET MOHAMMAD'),
            ('مدیریت کامل پنل AHBPanel از تلگرام', 'مدیریت کامل POMP NET SUPER JINX از تلگرام'),
            ('label = data.get("label") or "px-" + os.urandom(3).hex()',
             'label = data.get("label") or f"Mohammad Pomp Net | SUPER JINX-{os.urandom(2).hex()}"'),
            ('✏️ نام کانفیگ را بفرست (یا دکمه رندوم):',
             '✏️ نام کانفیگ را بفرست (پیشنهاد: Mohammad Pomp Net | SUPER JINX):'),
            ('st["data"]["label"] = "px" + os.urandom(4).hex()',
             'st["data"]["label"] = f"Mohammad Pomp Net | SUPER JINX-{os.urandom(2).hex()}"'),
            ('f"✨ پنل مدیریت کامل از تلگرام\\n"',
             'f"✨ پنل مدیریت کامل از تلگرام\\n"\n        f"⚡ قدرت ساخت، آزادی انتخاب، کنترل در دستان تو\\n"'),
            ('f"🗂 گروه‌های ساب: <b>{len(SUBS)}</b>"',
             'f"🗂 گروه‌های ساب: <b>{len(SUBS)}</b>\\n"\n        f"⚡ POMP NET MOHAMMAD — SUPER JINX"'),
        )
        for old, new in changes:
            source = replace_once(source, old, new)
        source = MARKER + "\n" + source
        with tempfile.TemporaryDirectory(prefix="pompnet-bot-check-") as folder:
            candidate = Path(folder) / "telegram_bot.py"
            candidate.write_text(source, encoding="utf-8")
            py_compile.compile(str(candidate), doraise=True)
        atomic_write(BOT, source)

    saved = BOT.read_text(encoding="utf-8")
    required = (
        'BOT_NAME = "POMP NET MOHAMMAD"',
        'BOT_NAME_EN = "POMP NET SUPER JINX"',
        'Mohammad Pomp Net | SUPER JINX',
        'مدیریت کامل POMP NET SUPER JINX از تلگرام',
        'POMP NET MOHAMMAD — SUPER JINX',
    )
    if any(x not in saved for x in required):
        raise SystemExit("SAFE STOP: Telegram brand validation failed")
    if any(x in saved for x in ("AHB BOT", "ای اچ بی بات", "AHBPanel")):
        raise SystemExit("SAFE STOP: old Telegram branding remains")
    py_compile.compile(str(BOT), doraise=True)

def patch_news():
    if not NEWS.is_file():
        raise SystemExit("SAFE STOP: news.json not found")
    data = json.loads(NEWS.read_text(encoding="utf-8"))
    data["title"] = "اطلاعیه رسمی POMP NET MOHAMMAD — SUPER JINX"
    message = str(data.get("message") or "").replace("@ahb_panel", "@NovaTunneli")
    if "POMP NET MOHAMMAD — SUPER JINX" not in message:
        message = message.rstrip() + (
            "\n\n━━━━━━━━━━━━━━━━━━"
            "\nPOMP NET MOHAMMAD — SUPER JINX"
            "\nقدرت ساخت، آزادی انتخاب، کنترل در دستان تو"
            "\nپشتیبانی: @NovaTunneli"
            "\nکانال رسمی: @pompnet"
        )
    data["message"] = message
    atomic_write(NEWS, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    saved = json.loads(NEWS.read_text(encoding="utf-8"))
    if "@ahb_panel" in saved["message"] or "POMP NET MOHAMMAD" not in saved["title"]:
        raise SystemExit("SAFE STOP: news branding validation failed")

def main():
    patch_bot()
    patch_news()
    print("POMP NET SUPER JINX TELEGRAM BRAND: OK")
    print("BOT IDENTITY, CONFIG LABELS AND NEWS: VERIFIED")
    print("TELEGRAM COMMANDS AND CONFIG CREATION LOGIC: PRESERVED")

if __name__ == "__main__":
    main()
