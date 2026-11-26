#!/usr/bin/env python3
"""Adds premium POMP NET typography and visual polish to the existing info page."""
from pathlib import Path
import re
import py_compile
import tempfile

target = Path("/app/main.py")
if not target.is_file():
    raise SystemExit("POMP NET subscription UI: /app/main.py not found")
source = target.read_text(encoding="utf-8")

# Railway terminates public HTTPS on 443; make that public subscription port explicit.
old_sub_url = 'sub_url = f"https://{host}/sub/{uid}"'
new_sub_url = 'sub_url = f"https://{host}:443/sub/{uid}"'
if source.count(old_sub_url) == 1:
    source = source.replace(old_sub_url, new_sub_url, 1)
elif new_sub_url not in source:
    raise SystemExit("POMP NET subscription UI: expected subscription URL builder not found")

match = re.search(r'(?m)^    info_html = f"""', source)
if not match:
    raise SystemExit("POMP NET subscription UI: info_html template not found")
start = match.end()
end = source.find('"""', start)
if end < 0:
    raise SystemExit("POMP NET subscription UI: info_html closing delimiter not found")
html = source[start:end]

if "POMP NET MOHAMMAD" not in html or "pompnet-sub-mark" not in html:
    raise SystemExit("POMP NET subscription UI: expected branded subscription page is missing")

marker = 'id="pompnet-subscription-special-style"'
if marker not in html:
    if "</head>" not in html:
        raise SystemExit("POMP NET subscription UI: head element missing")
    font_link = '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">\n'
    premium_style = """<style id="pompnet-subscription-special-style">
/* POMP NET MOHAMMAD — premium subscription identity */
:root {{ --pn-violet:#963cff; --pn-blue:#168cff; --pn-ink:#070510; }}
html,body {{ font-family:'Vazirmatn','Space Grotesk',sans-serif !important; }}
body {{ background:radial-gradient(ellipse at 12% 0%,rgba(117,48,210,.22),transparent 38%),radial-gradient(ellipse at 92% 8%,rgba(22,140,255,.16),transparent 34%),#050509 !important; }}
.card,.section,.stat,.hero {{ background:linear-gradient(145deg,rgba(22,17,39,.97),rgba(8,10,22,.97)) !important; border-color:rgba(151,89,255,.24) !important; box-shadow:0 14px 42px rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.04) !important; }}
.brand-mark {{ filter:drop-shadow(0 0 18px rgba(150,60,255,.38)); }}
.brand-name {{ color:#c4a5ff !important; letter-spacing:1.6px; }}
.brand-sub {{ color:#80baff !important; letter-spacing:.4px; }}
h1,.section-title h2 {{ font-family:'Vazirmatn',sans-serif !important; letter-spacing:-.3px; }}
.btn {{ background:linear-gradient(105deg,#7432df,#168cff) !important; box-shadow:0 8px 26px rgba(110,57,230,.30) !important; }}
.btn.secondary {{ background:linear-gradient(105deg,#4f2c9f,#7432df) !important; }}
.ring-progress {{ stroke:#963cff !important; }}
.badge,.vip {{ border-color:rgba(150,60,255,.38) !important; }}
.field,.link-row,.qr-box,.server {{ border-color:rgba(150,60,255,.18) !important; }}
.footer b {{ color:#c4a5ff !important; }}
@media(max-width:620px) {{ .brand-mark {{ transform:scale(.96); }} .section {{ border-radius:19px !important; }} }}
</style>"""
    html = html.replace("</head>", font_link + premium_style + "</head>", 1)

updated = source[:start] + html + source[end:]
if updated != source:
    with tempfile.TemporaryDirectory(prefix="pompnet-sub-ui-") as folder:
        candidate = Path(folder) / "main.py"
        candidate.write_text(updated, encoding="utf-8")
        py_compile.compile(str(candidate), doraise=True)
    target.write_text(updated, encoding="utf-8")

py_compile.compile(str(target), doraise=True)
print("POMP NET subscription page: brand, fonts and premium style verified.")
