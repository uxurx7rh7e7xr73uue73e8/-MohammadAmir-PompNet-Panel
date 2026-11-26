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
        '<div class="brand-mark">AHB</div>': '<div class="brand-mark">PJ</div>',
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

    # Build cards from the same generator and parameters as the real /sub endpoint.
    data_anchor = '    unique_ips = len(unique_ips_for_uuid(uid))'
    data_replacement = '''    unique_ips = len(unique_ips_for_uuid(uid))

    config_count = max(1, min(40, int(snapshot.get("config_count") or 1)))
    clean_ips = snapshot.get("clean_ips") or []
    if clean_ips:
        config_hosts = list(clean_ips)
        while len(config_hosts) < config_count:
            config_hosts.extend(clean_ips)
        config_hosts = config_hosts[:config_count]
    else:
        config_hosts = [host] * config_count

    config_items = []
    for index, config_host in enumerate(config_hosts, start=1):
        config_name = f"POMP-NET-MOHAMMAD-SUPER-JINX-{index:02d}"
        config_value = generate_vless_link(
            uid, config_host, remark=config_name,
            protocol=snapshot.get("protocol", DEFAULT_PROTOCOL),
            fingerprint=snapshot.get("fingerprint", DEFAULT_FINGERPRINT),
            alpn=snapshot.get("alpn"), port=snapshot.get("port", DEFAULT_PORT),
        )
        config_items.append((config_name, config_value))

    config_cards_html = "".join(
        f'<article class="pn-config-row"><div class="pn-config-index">{index:02d}</div>'
        f'<div class="pn-config-main"><strong>{escape_html(name)}</strong>'
        f'<small>{protocol} · {escape_html(str(snapshot.get("port", DEFAULT_PORT)))}</small></div>'
        f'<div class="pn-config-actions">'
        f'<button type="button" class="pn-config-btn" data-config="{escape_html(value)}" onclick="copyConfig(this)">کپی</button>'
        f'<button type="button" class="pn-config-btn" data-config="{escape_html(value)}" onclick="openConfigQr(this.dataset.config)">QR</button>'
        f'</div></article>'
        for index, (name, value) in enumerate(config_items, start=1)
    )
    all_config_attr = escape_html("\\n".join(value for _, value in config_items))

'''
    if block.count(data_anchor) != 1:
        raise SystemExit("SAFE STOP: unique subscription info insertion point did not match exactly once")
    block = block.replace(data_anchor, data_replacement, 1)

    config_section = '''  <div class="pn-config-toolbar"><span>کانفیگ‌های واقعی این اشتراک</span><button type="button" class="pn-config-btn pn-copy-all" data-config="{all_config_attr}" onclick="copyConfig(this)">کپی همه</button></div>
  <div class="pn-config-list">{config_cards_html}</div>
'''
    profile_anchor = '  <section class="card section">\n    <div class="section-title"><h2>پروفایل اتصال واقعی</h2>'
    if block.count(profile_anchor) != 1:
        raise SystemExit("SAFE STOP: connection profile insertion point did not match exactly once")
    block = block.replace(profile_anchor, config_section + profile_anchor, 1)

    qr_old = "function makeQr(id){{const box=document.getElementById(id);if(!box)return;box.innerHTML='';try{{const qr=qrcode(0,'L');qr.addData(vlessUrl);qr.make();box.innerHTML=qr.createImgTag(5,8)}}catch(e){{box.textContent='QR unavailable'}}}}"
    qr_new = "function makeQr(id,value=vlessUrl){{const box=document.getElementById(id);if(!box)return;box.innerHTML='';try{{const qr=qrcode(0,'L');qr.addData(value);qr.make();box.innerHTML=qr.createImgTag(5,8)}}catch(e){{box.textContent='QR unavailable'}}}}\nfunction openConfigQr(value){{document.getElementById('modal').classList.add('show');makeQr('qr-modal',value)}}\nfunction copyConfig(btn){{const value=btn.dataset.config||'';if(!value)return;const done=()=>{{const old=btn.textContent;btn.textContent='✓ کپی شد';setTimeout(()=>btn.textContent=old,1400)}};if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(value).then(done).catch(()=>fallback(value,done));else fallback(value,done)}}"
    if block.count(qr_old) != 1:
        raise SystemExit("SAFE STOP: original QR helper did not match exactly once")
    block = block.replace(qr_old, qr_new, 1)

    theme_css = r"""

/* POMP NET SUPER JINX REAL CONFIG LIST */
.pn-config-toolbar{{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 12px;color:#b8accb;font-size:11px}}
.pn-config-list{{display:grid;gap:9px}}
.pn-config-row{{display:flex;align-items:center;gap:11px;min-width:0;padding:12px;border:1px solid rgba(139,53,255,.20);border-radius:16px;background:linear-gradient(110deg,rgba(139,53,255,.09),rgba(22,140,255,.045)),rgba(5,5,12,.72)}}
.pn-config-index{{flex:0 0 34px;height:34px;display:grid;place-items:center;border-radius:11px;background:rgba(139,53,255,.14);color:#b98cff;font-weight:900}}
.pn-config-main{{flex:1;min-width:0;display:grid;gap:4px}}
.pn-config-main strong{{font-size:12px;overflow-wrap:anywhere;color:#f5f0ff}}
.pn-config-main small{{font-size:9px;color:#a99cbd;direction:ltr;text-align:right}}
.pn-config-actions{{display:flex;gap:6px}}
.pn-config-btn{{border:1px solid rgba(139,53,255,.28);border-radius:11px;padding:9px 12px;background:rgba(139,53,255,.12);color:#e9dcff;font-family:inherit;font-size:10px;font-weight:700;cursor:pointer}}
.pn-config-btn:hover{{background:rgba(139,53,255,.22)}}
.pn-copy-all{{white-space:nowrap}}
@media(max-width:430px){{.pn-config-row{{gap:7px;padding:9px}}.pn-config-index{{flex-basis:29px;height:31px}}.pn-config-main strong{{font-size:10px}}.pn-config-btn{{padding:8px 9px;font-size:9px}}}}

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
