#!/usr/bin/env python3
"""POMP NET subscription info-page visual polish; preserves all link data/routes."""
from pathlib import Path

target = Path("/app/main.py")
if not target.is_file():
    raise SystemExit("POMP NET subscription UI: /app/main.py not found")

source = target.read_text(encoding="utf-8")
updated = source

# Change only visible identity in the existing subscription information page.
replacements = {
    '<div class="brand-mark">AHB</div>': '<div class="brand-mark">POMP</div>',
    '<div class="brand-name">PANEL</div>': '<div class="brand-name">NET MOHAMMAD</div>',
    '<b>AHB PANEL</b>': '<b>POMP NET MOHAMMAD</b>',
    'snapshot.get("label", "AHB Panel")': 'snapshot.get("label", "POMP NET")',
}
for old, new in replacements.items():
    count = updated.count(old)
    if count != 1:
        # The default label is Python code, while other strings are HTML;
        # fail closed if the pinned source changes unexpectedly.
        raise SystemExit(f"POMP NET subscription UI: expected one occurrence, got {count}: {old}")
    updated = updated.replace(old, new, 1)

style_marker = "</style>"
style_addition = """
/* POMP NET NEXUS — premium subscription identity */
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --pn-violet:#963cff; --pn-blue:#168cff; --pn-ink:#070510; }
html,body { font-family:'Vazirmatn','Space Grotesk',sans-serif !important; }
body { background:radial-gradient(ellipse at 12% 0%,rgba(117,48,210,.22),transparent 38%),radial-gradient(ellipse at 92% 8%,rgba(22,140,255,.16),transparent 34%),#050509 !important; }
.card,.section,.stat,.hero { background:linear-gradient(145deg,rgba(22,17,39,.96),rgba(8,10,22,.96)) !important; border-color:rgba(151,89,255,.22) !important; box-shadow:0 14px 42px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.035) !important; }
.brand-mark { font-family:'Space Grotesk','Vazirmatn',sans-serif !important; letter-spacing:2px; color:#fff !important; text-shadow:0 0 24px rgba(150,60,255,.75),0 0 42px rgba(22,140,255,.25); }
.brand-name { color:#b995ff !important; letter-spacing:1.5px; }
h1,.section-title h2 { font-family:'Vazirmatn',sans-serif !important; }
.btn { background:linear-gradient(105deg,#7432df,#168cff) !important; box-shadow:0 8px 26px rgba(110,57,230,.28) !important; }
.btn.secondary { background:linear-gradient(105deg,#4f2c9f,#7432df) !important; }
.ring-progress { stroke:#963cff !important; }
.badge,.vip { border-color:rgba(150,60,255,.35) !important; }
.field,.link-row,.qr-box,.server { border-color:rgba(150,60,255,.16) !important; }
.footer b { color:#b995ff !important; }
"""
if updated.count(style_marker) != 1:
    raise SystemExit("POMP NET subscription UI: expected one style closing tag")
if "POMP NET NEXUS — premium subscription identity" not in updated:
    updated = updated.replace(style_marker, style_addition + "\\n" + style_marker, 1)

if updated != source:
    target.write_text(updated, encoding="utf-8")
    print("POMP NET subscription info page branded and restyled.")
else:
    print("POMP NET subscription UI already applied.")
