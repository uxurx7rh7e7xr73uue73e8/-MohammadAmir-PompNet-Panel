from pathlib import Path
import json
import os
import py_compile
import re
import tempfile

ROOT = Path("/app")
BOT = ROOT / "telegram_bot.py"
NEWS = ROOT / "news.json"
MAIN = ROOT / "main.py"
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
                'desc="از ای اچ بی بات"',
                'desc="از POMP NET MOHAMMAD — SUPER JINX"',
            ),
            (
                'label = data.get("label") or "px-" + os.urandom(3).hex()',
                'label = data.get("label") or "⚡👑 POMP-NET-MOHAMMAD-SUPER-JINX-" + os.urandom(3).hex().upper()',
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
        "⚡👑 POMP-NET-MOHAMMAD-SUPER-JINX-",
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


def patch_core_config_names():
    if not MAIN.is_file():
        raise SystemExit("SAFE STOP: main.py not found for config-name branding")
    source = MAIN.read_text(encoding="utf-8")
    marker = "# POMP NET MOHAMMAD SUPER JINX DEFAULT CONFIG NAMES"
    if marker not in source:
        pattern = re.compile(
            r"def random_config_name\(existing=None\):\n.*?(?=\ndef sanitize_config_name\()",
            re.S,
        )
        replacement = '''# POMP NET MOHAMMAD SUPER JINX DEFAULT CONFIG NAMES
def random_config_name(existing=None):
    existing = existing or set()
    prefix = "⚡👑 POMP-NET-MOHAMMAD-SUPER-JINX-"
    alphabet = string.ascii_uppercase + string.digits
    for _ in range(80):
        suffix = "".join(secrets.choice(alphabet) for _ in range(8))
        name = prefix + suffix
        if name not in existing:
            return name
    return prefix + secrets.token_hex(6).upper()

'''
        source, count = pattern.subn(lambda _match: replacement, source, count=1)
        if count != 1:
            raise SystemExit("SAFE STOP: random_config_name function not found exactly once")
        with tempfile.TemporaryDirectory(prefix="pompnet-name-check-") as folder:
            candidate = Path(folder) / "main.py"
            candidate.write_text(source, encoding="utf-8")
            py_compile.compile(str(candidate), doraise=True)
        atomic_write(MAIN, source)

    saved = MAIN.read_text(encoding="utf-8")
    if marker not in saved or 'prefix = "⚡👑 POMP-NET-MOHAMMAD-SUPER-JINX-"' not in saved:
        raise SystemExit("SAFE STOP: branded default config name validation failed")
    py_compile.compile(str(MAIN), doraise=True)


def patch_dashboard_protocol_picker():
    if not MAIN.is_file():
        raise SystemExit("SAFE STOP: main.py not found for protocol chooser")
    source = MAIN.read_text(encoding="utf-8")
    marker = "POMP NET SUPER JINX LIVE PROTOCOL PICKER"
    if marker not in source:
        pattern = re.compile(
            r'(?m)^DASHBOARD_HTML\s*=\s*r?(?P<q>"""|\'\'\')'
        )
        match = pattern.search(source)
        if not match:
            raise SystemExit("SAFE STOP: DASHBOARD_HTML not found")
        quote = match.group("q")
        start = match.end()
        end = source.find(quote, start)
        if end < 0:
            raise SystemExit("SAFE STOP: DASHBOARD_HTML closing quote not found")
        html = source[start:end]

        create_anchor = '<section class="page" id="page-create">'
        g2_anchor = '<div class="g2">'
        page_pos = html.find(create_anchor)
        grid_pos = html.find(g2_anchor, page_pos)
        if page_pos < 0 or grid_pos < 0:
            raise SystemExit("SAFE STOP: config creation page anchor missing")

        toolbar = """<!-- POMP NET SUPER JINX LIVE PROTOCOL PICKER -->
<div class="pn-protocol-toolbar">
  <div class="pn-protocol-copy">
    <b>مرکز پروتکل‌های SUPER JINX</b>
    <small>فهرست زنده از هستهٔ پنل · انتخاب برای ساخت دستی و خودکار</small>
  </div>
  <button type="button" class="pn-protocol-open" onclick="openJinxProtocols()">⚡ انتخاب پروتکل</button>
</div>
<div class="pn-protocol-modal" id="pnProtocolModal" aria-hidden="true">
  <div class="pn-protocol-backdrop" onclick="closeJinxProtocols()"></div>
  <section class="pn-protocol-dialog" role="dialog" aria-modal="true" aria-labelledby="pnProtocolTitle">
    <button type="button" class="pn-protocol-close" onclick="closeJinxProtocols()" aria-label="بستن">×</button>
    <span class="pn-protocol-kicker">POMP NET · SUPER JINX</span>
    <h3 id="pnProtocolTitle">پروتکل اتصال را انتخاب کن</h3>
    <p>پروتکل‌های فعال از API پنل خوانده می‌شوند. با انتخاب چند مورد، برای هر پروتکل یک اشتراک مستقل و واقعی ساخته می‌شود.</p>
    <div class="pn-protocol-actions">
      <button type="button" class="pn-protocol-select-all" onclick="selectAllJinxProtocols()">انتخاب همه</button>
      <button type="button" class="pn-protocol-clear" onclick="clearJinxProtocols()">پاک کردن انتخاب</button>
    </div>
    <div id="pnProtocolOptions" class="pn-protocol-options"><div class="pn-protocol-loading">در حال دریافت پروتکل‌ها…</div></div>
    <button type="button" class="pn-protocol-create-all" onclick="createSelectedJinxProtocols()">⚡ ساخت اشتراک برای پروتکل‌های انتخاب‌شده</button>
    <small class="pn-protocol-note">هر پروتکل در کانفیگ/اشتراک جدا ساخته می‌شود؛ همهٔ پروتکل‌ها داخل یک URI واحد ادغام نمی‌شوند.</small>
  </section>
</div>
"""
        html = html[:grid_pos] + toolbar + html[grid_pos:]

        css = """
/* POMP NET SUPER JINX LIVE PROTOCOL PICKER */
.pn-protocol-toolbar{display:flex;align-items:center;justify-content:space-between;gap:14px;margin:0 0 16px;padding:16px 18px;border:1px solid rgba(139,53,255,.28);border-radius:18px;background:linear-gradient(110deg,rgba(25,13,45,.98),rgba(7,13,28,.98));box-shadow:0 12px 32px rgba(0,0,0,.24),inset 0 1px rgba(255,255,255,.05)}
.pn-protocol-copy b{display:block;color:#fff;font-size:14px;font-weight:900}
.pn-protocol-copy small{display:block;margin-top:5px;color:#a99cbd;font-size:11px}
.pn-protocol-open{border:1px solid rgba(139,53,255,.42);border-radius:12px;padding:11px 16px;background:linear-gradient(100deg,#8b35ff,#168cff);color:#fff;font:800 12px Vazirmatn,sans-serif;white-space:nowrap;box-shadow:0 8px 24px rgba(139,53,255,.22)}
.pn-protocol-modal{display:none;position:fixed;inset:0;z-index:9999;align-items:center;justify-content:center;padding:16px}
.pn-protocol-modal.open{display:flex}
.pn-protocol-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.78);backdrop-filter:blur(8px)}
.pn-protocol-dialog{position:relative;width:min(100%,560px);max-height:min(82vh,720px);overflow:auto;padding:24px;border:1px solid rgba(139,53,255,.38);border-radius:22px;background:linear-gradient(145deg,#171026,#080a14);box-shadow:0 30px 90px rgba(0,0,0,.6),0 0 50px rgba(139,53,255,.13)}
.pn-protocol-close{position:absolute;left:14px;top:12px;width:34px;height:34px;border:1px solid rgba(255,255,255,.12);border-radius:10px;background:rgba(255,255,255,.06);color:#fff;font-size:23px}
.pn-protocol-kicker{color:#b98cff;font:700 10px system-ui,sans-serif;letter-spacing:1.5px}
.pn-protocol-dialog h3{margin:9px 0 5px;color:#fff;font-size:20px}
.pn-protocol-dialog>p{margin:0 0 16px;color:#aaa0bd;font-size:12px;line-height:1.8}
.pn-protocol-options{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.pn-protocol-option{display:flex;align-items:center;gap:10px;min-width:0;text-align:right;padding:12px;border:1px solid rgba(255,255,255,.09);border-radius:14px;background:rgba(255,255,255,.035);color:#f8f4ff}
.pn-protocol-option.selected{border-color:rgba(139,53,255,.68);background:rgba(139,53,255,.15);box-shadow:inset 0 0 0 1px rgba(139,53,255,.12)}
.pn-protocol-option-icon{display:grid;place-items:center;flex:0 0 30px;height:30px;border-radius:10px;background:linear-gradient(140deg,#8b35ff,#168cff);font-size:18px}
.pn-protocol-option span:nth-child(2){min-width:0;flex:1}
.pn-protocol-option b{display:block;font-size:11px;overflow-wrap:anywhere}
.pn-protocol-option small{display:block;margin-top:3px;color:#a99cbd;font-size:9px;overflow-wrap:anywhere}
.pn-protocol-option i{color:#b98cff;font-style:normal;font-weight:900}
.pn-protocol-loading{grid-column:1/-1;padding:22px;text-align:center;color:#b98cff;border:1px dashed rgba(139,53,255,.25);border-radius:14px;font-size:12px}
.pn-protocol-actions{display:flex;gap:8px;margin:0 0 12px}
.pn-protocol-select-all,.pn-protocol-clear{flex:1;padding:10px 12px;border-radius:11px;border:1px solid rgba(139,53,255,.3);background:#100c1d;color:#e9ddff;font:800 11px Vazirmatn,sans-serif}
.pn-protocol-create-all{width:100%;margin-top:14px;padding:13px;border:0;border-radius:13px;background:linear-gradient(100deg,#168cff,#8b35ff);color:#fff;font:900 12px Vazirmatn,sans-serif;box-shadow:0 10px 26px rgba(139,53,255,.2)}
.pn-protocol-note{display:block;margin-top:9px;color:#9d91b2;font-size:10px;line-height:1.8}
.pn-protocol-option.selected i{color:#4be6a5}

@media(max-width:600px){.pn-protocol-toolbar{align-items:flex-start;flex-direction:column}.pn-protocol-open{width:100%}.pn-protocol-options{grid-template-columns:1fr}.pn-protocol-dialog{padding:20px 14px}}
"""
        if "</head>" not in html or "</body>" not in html:
            raise SystemExit("SAFE STOP: dashboard head/body markers missing")
        html = html.replace("</head>", '<style id="pn-super-jinx-protocol-css">\\n' + css + '\\n</style>\\n</head>', 1)

        script = """
<script id="pn-super-jinx-protocol-script">
window.__pnJinxProtocolList=[];
window.__pnJinxSelectedProtocols=new Set();
async function openJinxProtocols(){
  const modal=document.getElementById('pnProtocolModal');
  const box=document.getElementById('pnProtocolOptions');
  if(!modal||!box)return;
  modal.classList.add('open');modal.setAttribute('aria-hidden','false');
  box.innerHTML='<div class="pn-protocol-loading">در حال دریافت فهرست واقعی پروتکل‌ها…</div>';
  const result=await api('/api/protocols');
  const list=(result&&Array.isArray(result.protocols))?result.protocols.filter(p=>p&&p.id&&!String(p.id).endsWith('-demo')):[];
  window.__pnJinxProtocolList=list;
  if(!list.length){box.innerHTML='<div class="pn-protocol-loading">هیچ پروتکل قابل استفاده‌ای از هسته دریافت نشد.</div>';return;}
  const current=document.getElementById('cProto')?.value||document.getElementById('aProto')?.value||'';
  if(!window.__pnJinxSelectedProtocols.size&&current)window.__pnJinxSelectedProtocols.add(current);
  ['cProto','aProto'].forEach(id=>{
    const select=document.getElementById(id);
    if(select)list.forEach(p=>{if(![...select.options].some(o=>o.value===p.id))select.add(new Option(p.label||p.id,p.id));});
  });
  renderJinxProtocolOptions();
}
function renderJinxProtocolOptions(){
  const box=document.getElementById('pnProtocolOptions');
  if(!box)return;
  box.innerHTML=window.__pnJinxProtocolList.map(p=>{
    const id=String(p.id);const label=String(p.label||id);const selected=window.__pnJinxSelectedProtocols.has(id);
    return '<button type="button" class="pn-protocol-option '+(selected?'selected':'')+'" data-protocol="'+esc(id)+'" onclick="toggleJinxProtocol(this.dataset.protocol)" aria-pressed="'+(selected?'true':'false')+'"><span class="pn-protocol-option-icon">◇</span><span><b>'+esc(label)+'</b><small>'+esc(id)+'</small></span><i>'+(selected?'✓':'＋')+'</i></button>';
  }).join('');
}
function toggleJinxProtocol(protocol){
  const selected=window.__pnJinxSelectedProtocols;
  if(selected.has(protocol))selected.delete(protocol);else selected.add(protocol);
  const select=document.getElementById('cProto');
  if(select&&[...select.options].some(o=>o.value===protocol)){select.value=protocol;select.dispatchEvent(new Event('change',{bubbles:true}));}
  renderJinxProtocolOptions();
}
function selectAllJinxProtocols(){
  window.__pnJinxSelectedProtocols=new Set(window.__pnJinxProtocolList.map(p=>String(p.id)));
  renderJinxProtocolOptions();
  if(typeof toast==='function')toast('همهٔ پروتکل‌های قابل استفاده انتخاب شدند');
}
function clearJinxProtocols(){
  window.__pnJinxSelectedProtocols.clear();
  renderJinxProtocolOptions();
}
async function createSelectedJinxProtocols(){
  const protocols=[...window.__pnJinxSelectedProtocols];
  if(!protocols.length){if(typeof toast==='function')toast('ابتدا حداقل یک پروتکل انتخاب کن');return;}
  const count=Math.max(1,Math.min(40,Number(document.getElementById('cCount')?.value)||1));
  const base={
    category_id:document.getElementById('cGroup')?.value||'0',
    config_count:count,
    limit_value:Number(document.getElementById('cLimit')?.value)||0,
    limit_unit:document.getElementById('cUnit')?.value||'GB',
    expires_days:Number(document.getElementById('cDays')?.value)||0,
    ip_limit:Number(document.getElementById('cIp')?.value)||0,
    speed_limit_value:Number(document.getElementById('cSpeed')?.value)||0,
    speed_limit_unit:'MBIT'
  };
  const name=(document.getElementById('cName')?.value||'').trim();
  const created=[];let last=null;
  if(typeof toast==='function')toast('در حال ساخت اشتراک‌های چندپروتکلی…');
  for(const protocol of protocols){
    const label=(name?name+'-':'')+'⚡👑 POMP-NET-MOHAMMAD-SUPER-JINX-'+protocol.toUpperCase().replace(/[^A-Z0-9-]/g,'-');
    const result=await api('/api/links',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({...base,label,protocol})});
    if(result){created.push(protocol);last=result;}
  }
  if(last&&typeof showResult==='function')showResult(last);
  if(typeof refreshAll==='function')await refreshAll();
  if(typeof toast==='function')toast('ساخته‌شده: '+created.length+' از '+protocols.length+' پروتکل. هرکدام اشتراک جدا دارد.');
  if(created.length)closeJinxProtocols();
}
function closeJinxProtocols(){
  const modal=document.getElementById('pnProtocolModal');
  if(modal){modal.classList.remove('open');modal.setAttribute('aria-hidden','true');}
}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeJinxProtocols();});
</script>
"""
        html = html.replace("</body>", script + "\\n</body>", 1)
        if marker not in html:
            html = html.replace("</head>", "<!-- " + marker + " -->\\n</head>", 1)
        source = source[:start] + html + source[end:]

        with tempfile.TemporaryDirectory(prefix="pompnet-protocol-check-") as folder:
            candidate = Path(folder) / "main.py"
            candidate.write_text(source, encoding="utf-8")
            py_compile.compile(str(candidate), doraise=True)
        atomic_write(MAIN, source)

    saved = MAIN.read_text(encoding="utf-8")
    if marker not in saved or "pnProtocolModal" not in saved or "/api/protocols" not in saved:
        raise SystemExit("SAFE STOP: live protocol picker validation failed")
    py_compile.compile(str(MAIN), doraise=True)

def main():
    patch_bot()
    patch_news()
    patch_core_config_names()
    patch_dashboard_protocol_picker()
    print("POMP NET MOHAMMAD — SUPER JINX TELEGRAM BRAND: OK")
    print("BOT IDENTITY, WELCOME, AUTO CONFIG LABELS AND NEWS: VERIFIED")
    print("DASHBOARD LIVE PROTOCOL PICKER: VERIFIED")
    print("DEFAULT CONFIG NAMES: POMP NET SUPER JINX")
    print("TELEGRAM COMMANDS, CALLBACKS, PROTOCOL WIZARD AND CONFIG LOGIC: PRESERVED")
    print("UPSTREAM LICENSE AND COPYRIGHT NOTICES: PRESERVED")


if __name__ == "__main__":
    main()
