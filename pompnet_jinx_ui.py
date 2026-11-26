from pathlib import Path
import hashlib
import py_compile
import re
import tempfile

MAIN = Path("/app/main.py")
MARKER = "POMP NET SUPER JINX INFO PAGE"

SUB_PATTERN = re.compile(
    r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?'
    r'(?=\n@app\.get|\n@app\.post|\n@app\.put|'
    r'\n@app\.delete|\n@app\.websocket|\nasync def |\nclass |\Z)',
    re.S,
)

def atomic_write(path: Path, content: str):
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="",
        dir=str(path.parent), prefix=f".{path.name}.",
        suffix=".tmp", delete=False,
    ) as handle:
        temp = Path(handle.name)
        handle.write(content)
        handle.flush()
    temp.replace(path)

def main():
    if not MAIN.is_file():
        raise SystemExit("ERROR: /app/main.py not found")

    original = MAIN.read_text(encoding="utf-8")
    if MARKER in original:
        print("POMP NET SUPER JINX INFO PAGE: ALREADY INSTALLED")
        return

    sub_match = SUB_PATTERN.search(original)
    if not sub_match:
        raise SystemExit("SAFE STOP: original /sub/{uuid} route not found")
    sub_hash_before = hashlib.sha256(sub_match.group(0).encode()).hexdigest()

    route_start = original.find('@app.get(\n    "/info/{uid}"')
    if route_start < 0:
        raise SystemExit("SAFE STOP: existing /info/{uid} route not found")
    route_end = original.find("# SUB GROUP API", route_start)
    if route_end < 0:
        raise SystemExit("SAFE STOP: end of existing info page not found")

    block = original[route_start:route_end]

    old_decorator = '@app.get(\n    "/info/{uid}",\n    response_class=HTMLResponse,\n)\nasync def info_page('
    new_decorator = '@app.get("/pass/{uid}", response_class=HTMLResponse)\n' + old_decorator
    if block.count(old_decorator) != 1:
        raise SystemExit("SAFE STOP: info page decorator did not match exactly once")
    block = block.replace(old_decorator, new_decorator, 1)

    replacements = {
        'snapshot.get("label", "AHB Panel")': 'snapshot.get("label", "POMP NET MOHAMMAD")',
        '<title>{label} | AHB PANEL</title>': '<title>{label} | POMP NET MOHAMMAD — SUPER JINX</title>',
        '<div class="brand-mark">AHB</div>': '<div class="brand-mark">POMP</div>',
        '<div class="brand-name">PANEL</div>': '<div class="brand-name">NET · SUPER JINX</div>',
        '<div class="brand-sub">اتصال سریع، بدون محدودیت</div>': '<div class="brand-sub">POMP NET MOHAMMAD</div>',
        '<h1>طرح ویژه</h1>': '<h1>اشتراک SUPER JINX</h1>',
        '<b>AHB PANEL</b>': '<b>POMP NET MOHAMMAD — SUPER JINX</b>',
    }

    for old, new in replacements.items():
        if old not in block:
            raise SystemExit(f"SAFE STOP: expected info-page marker missing: {old}")
        block = block.replace(old, new)

    server_section = re.compile(
        r'  <section class="card section">\s*'
        r'<div class="section-title"><h2>سرورهای فعال</h2>.*?</section>',
        re.S,
    )
    replacement_section = """  <section class="card section">
    <div class="section-title"><h2>پروفایل اتصال واقعی</h2><span>JINX CONNECTION</span></div>
    <div class="fields">
      <div class="field"><span class="field-label">پروتکل</span><span class="field-value">{protocol}</span></div>
      <div class="field"><span class="field-label">پورت اتصال</span><span class="field-value">{escape_html(str(snapshot.get("port", 443)))}</span></div>
      <div class="field"><span class="field-label">اثر انگشت</span><span class="field-value">{fingerprint}</span></div>
      <div class="field"><span class="field-label">محدودیت IP</span><span class="field-value">{escape_html(ip_limit)}</span></div>
      <div class="field"><span class="field-label">محدودیت اتصال</span><span class="field-value">{escape_html(conn_limit)}</span></div>
      <div class="field"><span class="field-label">IPهای ثبت‌شده</span><span class="field-value">{unique_ips}</span></div>
    </div>
  </section>"""
    block, section_count = server_section.subn(replacement_section, block, count=1)
    if section_count != 1:
        raise SystemExit("SAFE STOP: demo server cards were not found exactly once")

    theme_css = r"""
/* POMP NET SUPER JINX INFO PAGE */
:root{{--bg:#050509;--card:rgba(17,12,31,.94);--card2:rgba(20,13,37,.88);--line:rgba(139,53,255,.24);--text:#f7f4ff;--muted:#a99cbd;--blue:#168cff;--purple:#8b35ff;--pink:#8b35ff;--green:#16e6a0}}
body{{background:radial-gradient(900px 500px at 8% -10%,rgba(139,53,255,.20),transparent 58%),radial-gradient(700px 500px at 100% 12%,rgba(22,140,255,.14),transparent 58%),#050509}}
.brand-mark{{font-size:29px;letter-spacing:-1px;background:linear-gradient(110deg,#fff 10%,#b98cff 55%,#168cff);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 0 25px rgba(139,53,255,.22)}}
.brand-name{{font-size:11px;letter-spacing:1.8px;color:#d9c8ff}}
.brand-sub{{color:#a99cbd}}
.hero{{background:radial-gradient(circle at 0% 100%,rgba(22,140,255,.20),transparent 48%),radial-gradient(circle at 100% 0%,rgba(139,53,255,.30),transparent 46%),linear-gradient(135deg,rgba(16,10,31,.98),rgba(8,12,28,.98))}}
.card{{border-color:rgba(139,53,255,.20);background:linear-gradient(145deg,rgba(24,15,43,.88),rgba(8,8,15,.94));box-shadow:0 20px 65px rgba(0,0,0,.30)}}
.btn{{background:linear-gradient(100deg,#8b35ff,#168cff);box-shadow:0 9px 30px rgba(139,53,255,.22)}}
.btn.secondary{{background:linear-gradient(100deg,#5520a8,#8b35ff)}}
.stat:nth-child(2) .stat-icon{{color:#b98cff;background:rgba(139,53,255,.12);border-color:rgba(139,53,255,.22)}}
.stat:nth-child(4) .stat-icon{{color:#168cff;background:rgba(22,140,255,.12);border-color:rgba(22,140,255,.22)}}
.field{{border-color:rgba(139,53,255,.12);background:rgba(5,5,12,.62)}}
.link-row{{border-color:rgba(139,53,255,.14);background:rgba(5,5,12,.62)}}
.bottom{{background:rgba(5,5,9,.94);border-top-color:rgba(139,53,255,.18)}}
.nav.active{{color:#b98cff}}
"""
    if "</style>" not in block:
        raise SystemExit("SAFE STOP: info-page style block not found")
    block = block.replace("</style>", theme_css + "\n</style>", 1)
    block = block.replace("<head>", "<head>\n<!-- " + MARKER + " -->", 1)

    updated = original[:route_start] + block + original[route_end:]

    sub_after = SUB_PATTERN.search(updated)
    if not sub_after:
        raise SystemExit("SAFE STOP: /sub/{uuid} disappeared")
    sub_hash_after = hashlib.sha256(sub_after.group(0).encode()).hexdigest()
    if sub_hash_before != sub_hash_after:
        raise SystemExit("SAFE STOP: /sub/{uuid} route changed")

    if '/pass/{uid}' not in updated or 'JINX CONNECTION' not in updated:
        raise SystemExit("SAFE STOP: JINX PASS UI validation failed")

    with tempfile.TemporaryDirectory(prefix="pompnet-jinx-check-") as folder:
        candidate = Path(folder) / "main.py"
        candidate.write_text(updated, encoding="utf-8")
        py_compile.compile(str(candidate), doraise=True)

    atomic_write(MAIN, updated)
    py_compile.compile(str(MAIN), doraise=True)

    print("POMP NET SUPER JINX INFO PAGE: OK")
    print("READ-ONLY /info PAGE DESIGN: UPDATED")
    print("ALIAS /pass/{uid}: ADDED")
    print("REAL /sub/{uuid} ROUTE: HASH-PRESERVED")
    print("STATIC FAKE SERVER STATUS CARDS: REMOVED")

if __name__ == "__main__":
    main()
