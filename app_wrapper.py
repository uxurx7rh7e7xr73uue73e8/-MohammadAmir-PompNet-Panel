import html
import hmac
import os

from fastapi import Header, HTTPException
from fastapi.responses import HTMLResponse
from main import app
import main as panel

from pompnet_security import install_security


# ============================================================
# POMP NET SECURITY
# ============================================================

# امنیت روی همان اپ اصلی اعمال می‌شود؛ مسیرها و APIهای اصلی دست‌نخورده‌اند.
install_security(app)


# ============================================================
# RAILWAY HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():
    """مسیر عمومی سلامت Railway؛ بدون نیاز به Login یا Xray."""

    return {
        "ok": True,
        "service": "POMP NET MOHAMMAD — SUPER JINX",
        "status": "healthy",
    }


# ============================================================
# READ-ONLY POMP NET DASHBOARD PREVIEW
# ============================================================

@app.get("/pompnet-preview", response_class=HTMLResponse)
async def pompnet_dashboard_preview():
    """
    پیش‌نمایش فقط‌خواندنی است.
    فقط آمار تجمیعی را نشان می‌دهد و هیچ شناسه، لینک اشتراک،
    اطلاعات شخصی یا عملیات مدیریتی را افشا/اجرا نمی‌کند.
    """

    links = getattr(panel, "LINKS", {})
    if not isinstance(links, dict):
        links = {}

    active_count = 0
    used_total = 0
    protocols = set()
    ports = set()

    for item in links.values():
        if not isinstance(item, dict):
            continue

        try:
            if panel.is_link_allowed(item):
                active_count += 1
        except Exception:
            pass

        try:
            used_total += max(0, int(item.get("used_bytes", 0) or 0))
        except (TypeError, ValueError):
            pass

        protocol = str(item.get("protocol") or "نامشخص").strip()
        if protocol:
            protocols.add(protocol)

        try:
            port = int(item.get("port", 0) or 0)
            if 1 <= port <= 65535:
                ports.add(port)
        except (TypeError, ValueError):
            pass

    total_count = len(links)
    connections_count = len(getattr(panel, "connections", {}) or {})
    app_port = int(os.getenv("PORT", getattr(panel, "PORT", 8080)) or 8080)

    try:
        traffic_text = panel.fmt_bytes(used_total)
    except Exception:
        traffic_text = f"{used_total} B"

    protocol_html = "".join(
        f'<span class="pill">{html.escape(value)}</span>'
        for value in sorted(protocols)
    ) or '<span class="muted">هنوز پروتکلی ثبت نشده است</span>'

    port_html = "".join(
        f'<span class="pill port">{port}</span>'
        for port in sorted(ports)
    ) or '<span class="muted">هنوز پورتی ثبت نشده است</span>'

    page = f"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#050509">
<meta name="robots" content="noindex,nofollow">
<title>POMP NET MOHAMMAD — SUPER JINX | Dashboard Preview</title>
<style>
:root{{--bg:#050509;--card:#11101a;--line:rgba(139,53,255,.24);--text:#f6f3ff;--muted:#a59ab9;--purple:#8b35ff;--blue:#168cff;}}
*{{box-sizing:border-box}}
body{{margin:0;min-height:100vh;background:radial-gradient(900px 450px at 90% -10%,rgba(139,53,255,.22),transparent 65%),radial-gradient(700px 420px at 0% 30%,rgba(22,140,255,.13),transparent 65%),var(--bg);color:var(--text);font-family:Tahoma,Vazirmatn,system-ui,sans-serif}}
.wrap{{width:min(1120px,calc(100% - 28px));margin:auto;padding:28px 0 55px}}
header{{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:24px}}
.brand{{display:flex;align-items:center;gap:12px}}
.logo{{width:48px;height:48px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(145deg,#8b35ff,#168cff);font-weight:1000;font-size:18px;box-shadow:0 0 28px rgba(139,53,255,.32)}}
h1{{font-size:clamp(18px,4vw,25px);margin:0;font-weight:950}}
.sub{{font-size:11px;color:var(--muted);margin-top:5px}}
.badge{{border:1px solid rgba(139,53,255,.4);background:rgba(139,53,255,.12);color:#d7baff;padding:8px 12px;border-radius:999px;font-size:11px;font-weight:800;white-space:nowrap}}
.hero{{padding:22px;border:1px solid var(--line);border-radius:24px;background:linear-gradient(135deg,rgba(139,53,255,.16),rgba(22,140,255,.07)),rgba(15,13,23,.9);box-shadow:0 20px 60px rgba(0,0,0,.3)}}
.hero h2{{margin:0 0 8px;font-size:20px}}
.hero p{{margin:0;color:var(--muted);font-size:13px;line-height:2}}
.grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:13px;margin-top:15px}}
.card{{padding:18px;border:1px solid var(--line);border-radius:19px;background:linear-gradient(145deg,rgba(255,255,255,.045),rgba(255,255,255,.01)),var(--card);min-width:0}}
.label{{font-size:11px;color:var(--muted)}}
.value{{font-size:clamp(20px,4vw,29px);font-weight:950;margin-top:9px;overflow-wrap:anywhere}}
.section{{margin-top:15px;padding:20px;border:1px solid var(--line);border-radius:20px;background:rgba(17,16,26,.9)}}
.section h3{{margin:0 0 14px;font-size:14px}}
.pills{{display:flex;flex-wrap:wrap;gap:8px}}
.pill{{padding:8px 12px;border:1px solid rgba(139,53,255,.28);border-radius:12px;background:rgba(139,53,255,.1);font-size:11px;direction:ltr}}
.pill.port{{border-color:rgba(22,140,255,.28);background:rgba(22,140,255,.1)}}
.muted{{color:var(--muted);font-size:12px}}
.actions{{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}}
a.btn{{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;padding:12px 17px;border-radius:13px;background:linear-gradient(100deg,#8b35ff,#168cff);color:white;font-size:12px;font-weight:900}}
a.btn.secondary{{background:rgba(255,255,255,.06);border:1px solid var(--line)}}
.note{{margin-top:16px;padding:13px 15px;border-radius:14px;background:rgba(22,140,255,.07);border:1px solid rgba(22,140,255,.18);font-size:11px;line-height:2;color:#c7dfff}}
footer{{text-align:center;color:#776c8c;font-size:10px;margin-top:22px}}
@media(max-width:700px){{.wrap{{padding-top:17px}}header{{align-items:flex-start;flex-direction:column}}.grid{{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}}.card{{padding:14px}}.hero{{padding:18px}}}}
@media(max-width:390px){{.grid{{grid-template-columns:1fr 1fr}}.badge{{font-size:10px}}}}

/* SUPER JINX premium dashboard polish — presentation only */
:root{color-scheme:dark}
body{background-image:radial-gradient(900px 520px at 88% -8%,rgba(139,53,255,.25),transparent 62%),radial-gradient(680px 440px at 4% 24%,rgba(22,140,255,.16),transparent 66%),linear-gradient(180deg,#050509 0%,#090711 58%,#050509 100%)}
.wrap{max-width:1180px;padding-top:34px}
header{padding:14px 17px;border:1px solid rgba(139,53,255,.22);border-radius:20px;background:rgba(10,9,17,.82);box-shadow:0 14px 48px rgba(0,0,0,.28);backdrop-filter:blur(14px)}
.logo{position:relative;border:1px solid rgba(255,255,255,.22);background:linear-gradient(145deg,#8b35ff 0%,#5120a8 55%,#168cff 100%);box-shadow:0 0 0 5px rgba(139,53,255,.07),0 12px 32px rgba(139,53,255,.28)}
.logo:after{content:"";position:absolute;inset:-5px;border:1px solid rgba(139,53,255,.22);border-radius:19px}
.hero{position:relative;overflow:hidden;padding:clamp(22px,4vw,34px);background:radial-gradient(440px 210px at 100% 0%,rgba(139,53,255,.22),transparent 70%),linear-gradient(125deg,rgba(23,14,40,.97),rgba(8,12,25,.97));border-color:rgba(166,112,255,.32);box-shadow:0 24px 72px rgba(0,0,0,.38),inset 0 1px rgba(255,255,255,.05)}
.hero:after{content:"SUPER JINX";position:absolute;left:22px;bottom:8px;font:900 38px/1 system-ui;letter-spacing:5px;color:rgba(255,255,255,.025);pointer-events:none}
.hero h2{font-size:clamp(21px,4vw,29px);letter-spacing:-.5px}
.grid{gap:15px}
.card{position:relative;overflow:hidden;border-color:rgba(139,53,255,.22);background:linear-gradient(145deg,rgba(24,17,39,.96),rgba(10,10,18,.98));box-shadow:0 15px 38px rgba(0,0,0,.24),inset 0 1px rgba(255,255,255,.035);transition:transform .2s ease,border-color .2s ease}
.card:before{content:"";position:absolute;inset:0 0 auto;height:2px;background:linear-gradient(90deg,transparent,#8b35ff,#168cff,transparent);opacity:.72}
.card:hover{transform:translateY(-3px);border-color:rgba(139,53,255,.48)}
.value{font-variant-numeric:tabular-nums;letter-spacing:-.7px}
.section{border-color:rgba(139,53,255,.2);background:linear-gradient(145deg,rgba(19,14,31,.96),rgba(8,9,16,.96));box-shadow:0 14px 36px rgba(0,0,0,.2)}
.pill{border-radius:999px;background:rgba(139,53,255,.13);color:#e8d9ff}
.pill.port{color:#cbe5ff}
a.btn{box-shadow:0 9px 26px rgba(139,53,255,.23);transition:transform .18s ease,filter .18s ease}
a.btn:hover{transform:translateY(-2px);filter:brightness(1.12)}
a.btn.secondary{background:rgba(255,255,255,.045);box-shadow:none}
.note{border-color:rgba(22,140,255,.24);background:linear-gradient(110deg,rgba(22,140,255,.09),rgba(139,53,255,.06))}
footer{padding-top:16px;border-top:1px solid rgba(139,53,255,.13);letter-spacing:.3px}
@media(max-width:700px){.wrap{padding-top:14px}.grid{gap:10px}header{padding:12px;border-radius:16px}.hero:after{font-size:27px}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition:none!important;scroll-behavior:auto!important}}

</style>
</head>
<body>
<main class="wrap">
<header>
  <div class="brand"><div class="logo">PJ</div><div><h1>POMP NET MOHAMMAD</h1><div class="sub">SUPER JINX · پنل مدیریت و اشتراک</div></div></div>
  <div class="badge">پیش‌نمایش فقط‌خواندنی · READ ONLY</div>
</header>
<section class="hero">
  <h2>داشبورد نمایشی سوپر جینکس</h2>
  <p>این صفحه فقط آمار تجمیعی پردازش فعلی پنل را نمایش می‌دهد. ساخت، حذف، ویرایش کاربر یا تغییر تنظیمات از این صفحه انجام نمی‌شود و داشبورد اصلی دست‌نخورده باقی می‌ماند.</p>
  <div class="actions"><a class="btn" href="/dashboard">ورود به داشبورد اصلی</a><a class="btn secondary" href="/health">بررسی سلامت سرویس</a></div>
</section>
<section class="grid">
  <div class="card"><div class="label">کل کانفیگ‌ها</div><div class="value">{total_count}</div></div>
  <div class="card"><div class="label">کانفیگ‌های فعال</div><div class="value">{active_count}</div></div>
  <div class="card"><div class="label">ترافیک ثبت‌شده</div><div class="value">{html.escape(str(traffic_text))}</div></div>
  <div class="card"><div class="label">اتصال‌های جاری</div><div class="value">{connections_count}</div></div>
  <div class="card"><div class="label">پورت داخلی Railway</div><div class="value" dir="ltr">{app_port}</div></div>
  <div class="card"><div class="label">تعداد پروتکل‌ها</div><div class="value">{len(protocols)}</div></div>
</section>
<section class="section"><h3>پروتکل‌های ثبت‌شده</h3><div class="pills">{protocol_html}</div></section>
<section class="section"><h3>پورت‌های موجود در کانفیگ‌ها</h3><div class="pills">{port_html}</div></section>
<div class="note">نکته: این آمار از داده‌های موجود در حافظه‌ی پردازش خوانده می‌شود؛ این صفحه دیتابیس را تغییر نمی‌دهد و هیچ شناسه یا لینک خصوصی اشتراک را نمایش نمی‌دهد.</div>
<footer>POMP NET MOHAMMAD — SUPER JINX · قدرت ساخت، آزادی انتخاب، کنترل در دستان تو</footer>
</main>
</body>
</html>"""

    return HTMLResponse(
        page,
        headers={"Cache-Control": "no-store"},
    )


# ============================================================
# POMP NET STATUS TOKEN
# ============================================================

def status_token_ok(token: str | None):
    expected = os.getenv(
        "POMPNET_STATUS_TOKEN",
        "",
    ).strip()

    if not expected or not token:
        return False

    return hmac.compare_digest(token, expected)


# ============================================================
# POMP NET XRAY STATUS
# ============================================================

@app.get("/api/pompnet/xray")
async def pompnet_xray_status(
    x_pompnet_token: str | None = Header(default=None),
):
    """وضعیت Xray؛ هیچ WebSocket جدیدی تعریف نمی‌شود."""

    if not status_token_ok(x_pompnet_token):
        raise HTTPException(status_code=404, detail="not found")

    from pompnet_xray import get_xray_status
    return get_xray_status()


# ============================================================
# POMP NET SECURITY STATUS
# ============================================================

@app.get("/api/pompnet/security")
async def pompnet_security_status():
    return {
        "security": "enabled",
        "websocket_proxy": "ahb-core",
        "xray_public_port": False,
        "status_endpoint_protected": True,
    }
