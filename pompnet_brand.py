from pathlib import Path
import re
import hashlib

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def replace_once(data, pattern, replacement):
    return re.sub(pattern, replacement, data, count=1)


def get_sub_route(data):
    """
    کل تابع /sub/{uuid} را پیدا می‌کند.
    برای اطمینان از اینکه منطق Subscription تغییر نکرده است.
    """
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?(?=\n@app\.get|\n@app\.post|\n@app\.websocket|\nasync def |\Z)',
        re.S,
    )
    match = pattern.search(data)
    return match.group(0) if match else None


def replace_info_html(data):
    """
    فقط HTML صفحه /info/{uid} را عوض می‌کند.
    محاسبه حجم، تاریخ، لینک VLESS و Subscription
    از کد اصلی AHB باقی می‌ماند.
    """

    start = data.find('info_html = f"""')

    if start == -1:
        raise RuntimeError(
            "ERROR: info_html پیدا نشد"
        )

    end = data.find('"""', start + len('info_html = f"""'))

    if end == -1:
        raise RuntimeError(
            "ERROR: پایان info_html پیدا نشد"
        )

    old_block = data[start:end + 3]

    new_block = '''info_html = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#07030f">

<title>POMP NET PANEL</title>

<style>
* {
    box-sizing: border-box;
}

html,
body {
    margin: 0;
    padding: 0;
    min-height: 100%;
}

body {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(124,58,237,.22),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(37,99,235,.20),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #03020a,
            #090512 50%,
            #020617
        );

    color: #fff;

    font-family:
        Vazirmatn,
        Tahoma,
        Arial,
        sans-serif;
}

.pomp-container {
    width: min(1050px, 94%);
    margin: auto;
    padding: 20px 0 45px;
}

.pomp-header {
    position: relative;
    overflow: hidden;

    padding: 24px;

    border-radius: 26px;

    border: 1px solid rgba(139,92,246,.30);

    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,.20),
            rgba(37,99,235,.12)
        );

    box-shadow:
        0 20px 70px rgba(0,0,0,.45),
        inset 0 1px 0 rgba(255,255,255,.06);
}

.pomp-header::before {
    content: "";

    position: absolute;

    width: 220px;
    height: 220px;

    border-radius: 50%;

    background: rgba(124,58,237,.14);

    filter: blur(55px);

    top: -110px;
    right: -70px;
}

.pomp-logo {
    position: relative;

    display: flex;
    align-items: center;

    gap: 14px;
}

.pomp-logo-icon {
    width: 60px;
    height: 60px;

    border-radius: 19px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 30px;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );

    box-shadow:
        0 12px 35px rgba(124,58,237,.42);
}

.pomp-title {
    font-size: 26px;
    font-weight: 900;
}

.pomp-subtitle {
    margin-top: 5px;

    color: #aaa7b8;

    font-size: 13px;
}

.pomp-status {
    position: relative;

    display: inline-flex;
    align-items: center;

    gap: 8px;

    margin-top: 18px;

    padding: 8px 14px;

    border-radius: 999px;

    color: #86efac;

    background: rgba(34,197,94,.10);

    border: 1px solid rgba(34,197,94,.25);

    font-size: 13px;
    font-weight: 800;
}

.pomp-dot {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: #22c55e;

    box-shadow:
        0 0 13px #22c55e;
}

.pomp-stats {
    display: grid;

    grid-template-columns:
        repeat(4, 1fr);

    gap: 13px;

    margin-top: 15px;
}

.pomp-card {
    padding: 18px;

    border-radius: 21px;

    border: 1px solid rgba(255,255,255,.08);

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.07),
            rgba(255,255,255,.025)
        );

    box-shadow:
        0 15px 45px rgba(0,0,0,.24);

    backdrop-filter: blur(14px);
}

.pomp-label {
    color: #9995a8;

    font-size: 12px;

    margin-bottom: 8px;
}

.pomp-value {
    font-size: 18px;

    font-weight: 900;

    word-break: break-word;
}

.pomp-main {
    display: grid;

    grid-template-columns:
        330px 1fr;

    gap: 15px;

    margin-top: 15px;
}

.pomp-usage {
    min-height: 330px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;
}

.pomp-section-title {
    font-size: 18px;

    font-weight: 900;

    margin-bottom: 15px;
}

.pomp-ring {
    width: 190px;
    height: 190px;

    border-radius: 50%;

    display: flex;

    align-items: center;
    justify-content: center;

    background:
        conic-gradient(
            #8b5cf6 0deg,
            #2563eb {{usage_percent}}%,
            rgba(255,255,255,.07)
                {{usage_percent}}%,
            rgba(255,255,255,.07) 100%
        );

    box-shadow:
        0 0 55px rgba(124,58,237,.18);
}

.pomp-ring-inner {
    width: 162px;
    height: 162px;

    border-radius: 50%;

    display: flex;

    flex-direction: column;

    align-items: center;
    justify-content: center;

    background: #080511;

    border: 1px solid rgba(255,255,255,.06);
}

.pomp-percent {
    font-size: 31px;

    font-weight: 900;
}

.pomp-percent-small {
    margin-top: 4px;

    color: #9995a8;

    font-size: 12px;
}

.pomp-info {
    display: grid;

    gap: 9px;
}

.pomp-row {
    display: flex;

    justify-content: space-between;

    align-items: center;

    gap: 15px;

    padding: 13px;

    border-radius: 14px;

    background:
        rgba(255,255,255,.035);

    border: 1px solid rgba(255,255,255,.055);
}

.pomp-row span:first-child {
    color: #9692a4;

    font-size: 12px;
}

.pomp-row span:last-child {
    color: #fff;

    font-size: 13px;

    font-weight: 700;

    word-break: break-all;

    text-align: left;

    direction: ltr;
}

.pomp-links {
    margin-top: 15px;
}

.pomp-input-row {
    display: flex;

    gap: 9px;

    margin-bottom: 13px;
}

.pomp-input {
    flex: 1;

    min-width: 0;

    padding: 14px;

    border-radius: 14px;

    border: 1px solid rgba(255,255,255,.08);

    background: #05030b;

    color: #ddd;

    direction: ltr;

    outline: none;

    font-size: 12px;
}

.pomp-copy {
    border: 0;

    border-radius: 14px;

    padding: 0 18px;

    color: #fff;

    font-weight: 900;

    cursor: pointer;

    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );
}

.pomp-support {
    display: block;

    text-decoration: none;

    text-align: center;

    margin-top: 15px;

    padding: 15px;

    border-radius: 16px;

    color: #fff;

    font-weight: 900;

    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,.45),
            rgba(37,99,235,.35)
        );

    border: 1px solid rgba(139,92,246,.35);
}

.pomp-footer {
    padding-top: 14px;

    text-align: center;

    color: #777385;

    font-size: 11px;
}

@media(max-width:850px) {

    .pomp-stats {
        grid-template-columns:
            repeat(2,1fr);
    }

    .pomp-main {
        grid-template-columns: 1fr;
    }
}

@media(max-width:520px) {

    .pomp-container {
        width: 92%;
    }

    .pomp-header {
        padding: 18px;
    }

    .pomp-title {
        font-size: 22px;
    }

    .pomp-stats {
        gap: 8px;
    }

    .pomp-card {
        padding: 14px;
        border-radius: 17px;
    }

    .pomp-ring {
        width: 165px;
        height: 165px;
    }

    .pomp-ring-inner {
        width: 141px;
        height: 141px;
    }

    .pomp-input-row {
        flex-direction: column;
    }

    .pomp-copy {
        min-height: 45px;
    }
}
</style>
</head>

<body>

<div class="pomp-container">

<section class="pomp-header">

    <div class="pomp-logo">

        <div class="pomp-logo-icon">
            ⚡
        </div>

        <div>

            <div class="pomp-title">
                POMP NET
            </div>

            <div class="pomp-subtitle">
                Fast • Secure • Unlimited VPN
            </div>

        </div>

    </div>

    <div class="pomp-status">

        <span class="pomp-dot"></span>

        {status_text}

    </div>

</section>


<section class="pomp-stats">

    <div class="pomp-card">

        <div class="pomp-label">
            کاربر
        </div>

        <div class="pomp-value">
            {label}
        </div>

    </div>


    <div class="pomp-card">

        <div class="pomp-label">
            مصرف شده
        </div>

        <div class="pomp-value">
            {used_e}
        </div>

    </div>


    <div class="pomp-card">

        <div class="pomp-label">
            حجم کل
        </div>

        <div class="pomp-value">
            {total_e}
        </div>

    </div>


    <div class="pomp-card">

        <div class="pomp-label">
            باقی‌مانده
        </div>

        <div class="pomp-value">
            {remaining_e}
        </div>

    </div>

</section>


<section class="pomp-main">


<div class="pomp-card pomp-usage">

    <div class="pomp-section-title">
        مصرف اینترنت
    </div>

    <div class="pomp-ring">

        <div class="pomp-ring-inner">

            <div class="pomp-percent">
                {usage_percent}%
            </div>

            <div class="pomp-percent-small">
                مصرف شده
            </div>

        </div>

    </div>

</div>


<div class="pomp-card">

    <div class="pomp-section-title">
        اطلاعات اشتراک
    </div>

    <div class="pomp-info">


        <div class="pomp-row">
            <span>انقضا</span>
            <span>{expiry_e}</span>
        </div>


        <div class="pomp-row">
            <span>زمان باقی‌مانده</span>
            <span>{expiry_remaining_e}</span>
        </div>


        <div class="pomp-row">
            <span>Protocol</span>
            <span>{protocol}</span>
        </div>


        <div class="pomp-row">
            <span>Fingerprint</span>
            <span>{fingerprint}</span>
        </div>


        <div class="pomp-row">
            <span>IP Limit</span>
            <span>{ip_limit}</span>
        </div>


        <div class="pomp-row">
            <span>Connection Limit</span>
            <span>{conn_limit}</span>
        </div>


        <div class="pomp-row">
            <span>Speed Limit</span>
            <span>{speed_limit}</span>
        </div>


    </div>

</div>

</section>


<section class="pomp-card pomp-links">

    <div class="pomp-section-title">
        لینک‌های اتصال
    </div>


    <div class="pomp-label">
        VLESS
    </div>

    <div class="pomp-input-row">

        <input
            class="pomp-input"
            id="pomp-vless"
            value="{vless_e}"
            readonly
        >

        <button
            class="pomp-copy"
            onclick="copyPomp('pomp-vless',this)"
        >
            کپی
        </button>

    </div>


    <div class="pomp-label">
        Subscription
    </div>

    <div class="pomp-input-row">

        <input
            class="pomp-input"
            id="pomp-sub"
            value="{sub_e}"
            readonly
        >

        <button
            class="pomp-copy"
            onclick="copyPomp('pomp-sub',this)"
        >
            کپی
        </button>

    </div>


    <a
        class="pomp-support"
        href="https://t.me/NovaTunneli"
        target="_blank"
        rel="noopener"
    >
        💬 پشتیبانی POMP NET
    </a>

</section>


<div class="pomp-footer">
    POMP NET • Mohammad &amp; Amir
</div>

</div>


<script>

function copyPomp(id,button){

    const input =
        document.getElementById(id);

    if(!input){
        return;
    }

    navigator.clipboard
        .writeText(input.value)
        .then(function(){

            const old =
                button.innerText;

            button.innerText =
                "کپی شد ✓";

            setTimeout(function(){

                button.innerText =
                    old;

            },1500);

        })
        .catch(function(){

            input.select();

            document.execCommand(
                "copy"
            );

        });
}

</script>

</body>
</html>
"""'''

    return data[:start] + new_block + data[end + 3:]


def main():

    if not MAIN.exists():
        raise RuntimeError(
            "ERROR: main.py پیدا نشد"
        )

    if not CSS.exists():
        raise RuntimeError(
            "ERROR: pompnet.css پیدا نشد"
        )

    data = MAIN.read_text(
        encoding="utf-8"
    )

    css = CSS.read_text(
        encoding="utf-8"
    )

    # =====================================================
    # محافظت از هسته Subscription
    # =====================================================

    sub_before = get_sub_route(data)

    if not sub_before:
        raise RuntimeError(
            "ERROR: /sub/{uuid} پیدا نشد"
        )

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # =====================================================
    # فقط تنظیمات برندینگ
    # =====================================================

    data = replace_once(
        data,
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"'
    )

    data = replace_once(
        data,
        r'APP_VERSION\s*=\s*["\'][^"\']*["\']',
        'APP_VERSION = "POMP NET"'
    )

    data = replace_once(
        data,
        r'SUPPORT_USERNAME\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_USERNAME = "@NovaTunneli"'
    )

    data = replace_once(
        data,
        r'SUPPORT_URL\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_URL = "https://t.me/NovaTunneli"'
    )

    # =====================================================
    # فقط متن‌های نمایشی
    # =====================================================

    visual_replacements = {

        "AHB PANEL":
            "POMP NET PANEL",

        "AHB Panel":
            "POMP NET PANEL",

        "Created By Ahb":
            "Created By POMP NET",

        "Created By AHB":
            "Created By POMP NET",

        "به پنل مدیریت AHB خوش آمدید":
            "به پنل مدیریت POMP NET خوش آمدید",

        "درگاه عمومی AHB Panel":
            "درگاه عمومی POMP NET",

        "@ahb_panel":
            "@NovaTunneli",

        "@ahbpanel":
            "@NovaTunneli",

        "@ahbpanelgap":
            "@NovaTunneli",

        "https://t.me/ahb_panel":
            "https://t.me/NovaTunneli",

        "https://t.me/ahbpanel":
            "https://t.me/NovaTunneli",

    }

    for old, new in visual_replacements.items():
        data = data.replace(
            old,
            new
        )

    # =====================================================
    # قالب واقعی /info/{uid}
    # =====================================================

    data = replace_info_html(data)

    # =====================================================
    # Title
    # =====================================================

    data = re.sub(
        r"<title>.*?</title>",
        "<title>POMP NET PANEL</title>",
        data,
        flags=re.IGNORECASE,
        count=1
    )

    # =====================================================
    # CSS اصلی POMP NET
    # =====================================================

    if 'id="pompnet-css"' not in data:

        if "</head>" not in data:
            raise RuntimeError(
                "ERROR: </head> پیدا نشد"
            )

        style = (
            '<style id="pompnet-css">\n'
            + css
            + "\n</style>"
        )

        data = data.replace(
            "</head>",
            style + "\n</head>",
            1
        )

    # =====================================================
    # بنر
    # =====================================================

    if 'id="pompnet-brand-banner"' not in data:

        banner = """
<div id="pompnet-brand-banner">
    ⚡ <b>POMP NET</b>
    • Mohammad &amp; Amir
    • Fast • Secure • Unlimited VPN
</div>
"""

        body = re.search(
            r"<body[^>]*>",
            data,
            flags=re.IGNORECASE
        )

        if body:

            pos = body.end()

            data = (
                data[:pos]
                + "\n"
                + banner
                + "\n"
                + data[pos:]
            )

    # =====================================================
    # Login Branding
    # منطق Login تغییر نمی‌کند
    # =====================================================

    login_css = """
<style id="pompnet-login-brand">

.pompnet-login-title {
    font-weight: 900 !important;
    letter-spacing: .5px !important;
}

</style>
"""

    if 'id="pompnet-login-brand"' not in data:

        if "</head>" in data:

            data = data.replace(
                "</head>",
                login_css + "\n</head>",
                1
            )

    # =====================================================
    # ذخیره
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8"
    )

    # =====================================================
    # تست Build
    # =====================================================

    check = MAIN.read_text(
        encoding="utf-8"
    )

    sub_after = get_sub_route(check)

    if not sub_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: /sub/{uuid} حذف شده"
        )

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    if sub_hash_before != sub_hash_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: "
            "/sub/{uuid} تغییر کرده است"
        )

    required = [
        'APP_NAME = "POMP NET"',
        '@NovaTunneli',
        'id="pompnet-css"',
        'id="pompnet-brand-banner"',
        'POMP NET',
        'async def info_page',
        '/sub/{uuid}',
    ]

    for item in required:

        if item not in check:

            raise RuntimeError(
                "BUILD CHECK FAILED: "
                + item
            )

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("CORE: AHB PRESERVED")
    print("SUBSCRIPTION: PRESERVED")
    print("INFO PAGE: POMP NET")
    print("LOGIN: POMP NET PANEL")
    print("THEME: POMP NET")
    print("SUPPORT: @NovaTunneli")
    print("ADMIN: admin / admin")
    print("PORT: Railway $PORT")
    print("HEALTH: /health")
    print("=" * 60)


if __name__ == "__main__":
    main()
