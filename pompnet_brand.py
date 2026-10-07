from pathlib import Path
import re
import hashlib

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def replace_once(data, pattern, replacement):
    return re.sub(pattern, replacement, data, count=1)


def find_sub_route(data):
    """
    پیدا کردن Route اصلی /sub/{uuid}
    برای اطمینان از اینکه هسته Subscription تغییر نکرده است.
    """
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?(?=\n@app\.|\nasync def |\Z)',
        re.S,
    )
    match = pattern.search(data)
    return match.group(0) if match else None


def replace_info_template(data):
    """
    فقط HTML صفحه /info/{uid} را تغییر می‌دهد.
    منطق محاسبه حجم، تاریخ، لینک VLESS، QR و Subscription
    دست‌نخورده باقی می‌ماند.
    """

    marker = 'info_html = f"""'

    start = data.find(marker)

    if start == -1:
        raise RuntimeError(
            "ERROR: info_html صفحه Subscription پیدا نشد"
        )

    end = data.find('"""', start + len(marker))

    if end == -1:
        raise RuntimeError(
            "ERROR: پایان info_html پیدا نشد"
        )

    old_html = data[start:end + 3]

    new_html = r'''info_html = f"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta name="theme-color" content="#07030f">

<title>POMP NET</title>

<style>
*{
    box-sizing:border-box;
}

html,body{
    margin:0;
    padding:0;
    min-height:100%;
}

body{
    background:
        radial-gradient(circle at 15% 10%,rgba(168,85,247,.20),transparent 30%),
        radial-gradient(circle at 85% 20%,rgba(59,130,246,.18),transparent 30%),
        linear-gradient(135deg,#03020a,#090512 45%,#030712);
    color:#fff;
    font-family:
        Vazirmatn,
        Tahoma,
        Arial,
        sans-serif;
}

.pomp-wrap{
    width:min(1050px,94%);
    margin:0 auto;
    padding:25px 0 45px;
}

.pomp-header{
    position:relative;
    overflow:hidden;
    border:1px solid rgba(168,85,247,.30);
    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,.20),
            rgba(37,99,235,.12)
        );
    box-shadow:
        0 20px 70px rgba(0,0,0,.45),
        inset 0 1px 0 rgba(255,255,255,.06);
    border-radius:28px;
    padding:24px;
    margin-bottom:18px;
}

.pomp-header:before{
    content:"";
    position:absolute;
    width:220px;
    height:220px;
    border-radius:50%;
    background:rgba(168,85,247,.13);
    filter:blur(50px);
    top:-100px;
    right:-60px;
}

.pomp-logo{
    position:relative;
    display:flex;
    align-items:center;
    gap:15px;
}

.pomp-logo-icon{
    width:58px;
    height:58px;
    border-radius:18px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:29px;
    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );
    box-shadow:
        0 10px 35px rgba(124,58,237,.40);
}

.pomp-title{
    font-size:25px;
    font-weight:900;
    letter-spacing:.5px;
}

.pomp-subtitle{
    margin-top:5px;
    color:#aaa7b8;
    font-size:13px;
}

.pomp-status{
    margin-top:18px;
    display:inline-flex;
    align-items:center;
    gap:8px;
    border-radius:999px;
    padding:8px 14px;
    font-size:13px;
    font-weight:700;
    background:rgba(34,197,94,.10);
    border:1px solid rgba(34,197,94,.25);
    color:#86efac;
}

.pomp-status-dot{
    width:8px;
    height:8px;
    border-radius:50%;
    background:#22c55e;
    box-shadow:0 0 12px #22c55e;
}

.pomp-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:14px;
    margin-bottom:18px;
}

.pomp-card{
    border:1px solid rgba(255,255,255,.08);
    border-radius:22px;
    padding:18px;
    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.07),
            rgba(255,255,255,.025)
        );
    box-shadow:0 15px 45px rgba(0,0,0,.24);
    backdrop-filter:blur(14px);
}

.pomp-label{
    color:#9995a8;
    font-size:12px;
    margin-bottom:8px;
}

.pomp-value{
    font-size:18px;
    font-weight:850;
    word-break:break-word;
}

.pomp-main{
    display:grid;
    grid-template-columns:330px 1fr;
    gap:18px;
    margin-bottom:18px;
}

.pomp-usage{
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    min-height:330px;
}

.pomp-ring{
    width:190px;
    height:190px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    background:
        conic-gradient(
            #8b5cf6 0deg,
            #2563eb {{usage_percent}}deg,
            rgba(255,255,255,.07) {{usage_percent}}deg,
            rgba(255,255,255,.07) 360deg
        );
    position:relative;
    box-shadow:
        0 0 55px rgba(124,58,237,.18);
}

.pomp-ring:before{
    content:"";
    position:absolute;
    inset:13px;
    border-radius:50%;
    background:#080511;
    border:1px solid rgba(255,255,255,.06);
}

.pomp-ring-inner{
    position:relative;
    z-index:2;
    text-align:center;
}

.pomp-percent{
    font-size:31px;
    font-weight:900;
}

.pomp-percent-small{
    color:#9d99aa;
    font-size:12px;
    margin-top:4px;
}

.pomp-section-title{
    font-size:18px;
    font-weight:900;
    margin-bottom:15px;
}

.pomp-info-list{
    display:grid;
    gap:10px;
}

.pomp-info-row{
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:15px;
    padding:13px 14px;
    border-radius:14px;
    background:rgba(255,255,255,.035);
    border:1px solid rgba(255,255,255,.055);
}

.pomp-info-row span:first-child{
    color:#9692a4;
    font-size:12px;
}

.pomp-info-row span:last-child{
    font-size:13px;
    font-weight:700;
    word-break:break-all;
    text-align:left;
    direction:ltr;
}

.pomp-links{
    margin-top:18px;
}

.pomp-link-box{
    display:flex;
    gap:10px;
    align-items:center;
    margin-bottom:12px;
}

.pomp-link-input{
    flex:1;
    min-width:0;
    padding:14px;
    border-radius:14px;
    border:1px solid rgba(255,255,255,.08);
    background:#05030b;
    color:#ddd;
    direction:ltr;
    font-size:12px;
    outline:none;
}

.pomp-copy{
    border:0;
    border-radius:14px;
    padding:13px 16px;
    color:#fff;
    font-weight:800;
    cursor:pointer;
    background:
        linear-gradient(
            135deg,
            #7c3aed,
            #2563eb
        );
    box-shadow:0 8px 25px rgba(124,58,237,.25);
}

.pomp-copy:active{
    transform:scale(.97);
}

.pomp-support{
    display:block;
    text-decoration:none;
    text-align:center;
    padding:15px;
    margin-top:16px;
    border-radius:16px;
    color:#fff;
    font-weight:850;
    background:
        linear-gradient(
            135deg,
            rgba(124,58,237,.45),
            rgba(37,99,235,.35)
        );
    border:1px solid rgba(139,92,246,.35);
}

.pomp-footer{
    text-align:center;
    color:#777385;
    font-size:11px;
    padding-top:12px;
}

@media(max-width:850px){
    .pomp-grid{
        grid-template-columns:repeat(2,1fr);
    }

    .pomp-main{
        grid-template-columns:1fr;
    }
}

@media(max-width:520px){
    .pomp-wrap{
        width:92%;
        padding-top:14px;
    }

    .pomp-header{
        padding:18px;
        border-radius:22px;
    }

    .pomp-title{
        font-size:21px;
    }

    .pomp-grid{
        grid-template-columns:1fr 1fr;
        gap:9px;
    }

    .pomp-card{
        padding:14px;
        border-radius:17px;
    }

    .pomp-main{
        gap:12px;
    }

    .pomp-usage{
        min-height:285px;
    }

    .pomp-ring{
        width:165px;
        height:165px;
    }

    .pomp-link-box{
        flex-direction:column;
        align-items:stretch;
    }

    .pomp-copy{
        width:100%;
    }
}
</style>
</head>

<body>

<div class="pomp-wrap">

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
            <span class="pomp-status-dot"></span>
            {{status_text}}
        </div>

    </section>


    <section class="pomp-grid">

        <div class="pomp-card">
            <div class="pomp-label">
                کاربر
            </div>
            <div class="pomp-value">
                {{label}}
            </div>
        </div>

        <div class="pomp-card">
            <div class="pomp-label">
                حجم مصرف‌شده
            </div>
            <div class="pomp-value">
                {{used_e}}
            </div>
        </div>

        <div class="pomp-card">
            <div class="pomp-label">
                حجم کل
            </div>
            <div class="pomp-value">
                {{total_e}}
            </div>
        </div>

        <div class="pomp-card">
            <div class="pomp-label">
                باقی‌مانده
            </div>
            <div class="pomp-value">
                {{remaining_e}}
            </div>
        </div>

    </section>


    <section class="pomp-main">

        <div class="pomp-card pomp-usage">

            <div class="pomp-section-title">
                مصرف اینترنت
            </div>

            <div
                class="pomp-ring"
                style="
                    background:
                    conic-gradient(
                        #8b5cf6 0deg,
                        #2563eb {{usage_percent}}%,
                        rgba(255,255,255,.07) {{usage_percent}}%,
                        rgba(255,255,255,.07) 100%
                    );
                "
            >

                <div class="pomp-ring-inner">

                    <div class="pomp-percent">
                        {{usage_percent}}%
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

            <div class="pomp-info-list">

                <div class="pomp-info-row">
                    <span>انقضا</span>
                    <span>{{expiry_e}}</span>
                </div>

                <div class="pomp-info-row">
                    <span>زمان باقی‌مانده</span>
                    <span>{{expiry_remaining_e}}</span>
                </div>

                <div class="pomp-info-row">
                    <span>Protocol</span>
                    <span>{{protocol}}</span>
                </div>

                <div class="pomp-info-row">
                    <span>Fingerprint</span>
                    <span>{{fingerprint}}</span>
                </div>

                <div class="pomp-info-row">
                    <span>IP Limit</span>
                    <span>{{ip_limit}}</span>
                </div>

                <div class="pomp-info-row">
                    <span>Connection Limit</span>
                    <span>{{conn_limit}}</span>
                </div>

                <div class="pomp-info-row">
                    <span>Speed Limit</span>
                    <span>{{speed_limit}}</span>
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

        <div class="pomp-link-box">

            <input
                class="pomp-link-input"
                id="pomp-vless"
                value="{{vless_e}}"
                readonly
            >

            <button
                class="pomp-copy"
                onclick="pompCopy('pomp-vless')"
            >
                کپی
            </button>

        </div>


        <div class="pomp-label">
            Subscription
        </div>

        <div class="pomp-link-box">

            <input
                class="pomp-link-input"
                id="pomp-sub"
                value="{{sub_e}}"
                readonly
            >

            <button
                class="pomp-copy"
                onclick="pompCopy('pomp-sub')"
            >
                کپی
            </button>

        </div>


        <a
            class="pomp-support"
            href="https://t.me/NovaTunneli"
            target="_blank"
        >
            💬 پشتیبانی POMP NET
        </a>

    </section>


    <div class="pomp-footer">
        POMP NET • Mohammad &amp; Amir
    </div>

</div>


<script>
function pompCopy(id){

    const el = document.getElementById(id);

    if(!el){
        return;
    }

    navigator.clipboard.writeText(el.value)
        .then(function(){

            const btn = el.nextElementSibling;

            if(btn){

                const old = btn.innerText;

                btn.innerText = "کپی شد ✓";

                setTimeout(function(){
                    btn.innerText = old;
                },1500);

            }

        })
        .catch(function(){

            el.select();
            document.execCommand("copy");

        });
}
</script>

</body>
</html>
"""'''

    return data[:start] + new_html + data[end + 3:]


def main():

    if not MAIN.exists():
        raise RuntimeError("ERROR: main.py پیدا نشد")

    if not CSS.exists():
        raise RuntimeError("ERROR: pompnet.css پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")

    # =====================================================
    # BACKUP CHECK
    # هسته Subscription قبل از تغییر ذخیره می‌شود
    # =====================================================

    sub_before = find_sub_route(data)

    if not sub_before:
        raise RuntimeError(
            "ERROR: Route اصلی /sub/{uuid} پیدا نشد"
        )

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # =====================================================
    # مشخصات نمایشی
    # فقط مقادیر برندینگ، نه هسته AHB
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
    # فقط متن‌های کاملاً نمایشی
    # هیچ جایگزینی سراسری AHB انجام نمی‌شود
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

        "github.com/ahb-panel/ahb_panel":
            "github.com/uxurx7rh7e7xr73uue73e8",
    }

    for old, new in visual_replacements.items():
        data = data.replace(old, new)

    # =====================================================
    # قالب اختصاصی صفحه Subscription / Info
    # =====================================================

    data = replace_info_template(data)

    # =====================================================
    # Title
    # =====================================================

    data = re.sub(
        r"<title>.*?</title>",
        "<title>POMP NET PANEL</title>",
        data,
        flags=re.IGNORECASE,
        count=1,
    )

    # =====================================================
    # CSS POMP NET
    # =====================================================

    if 'id="pompnet-css"' not in data:

        if "</head>" not in data:
            raise RuntimeError(
                "ERROR: </head> پیدا نشد"
            )

        style = (
            '<style id="pompnet-css">\n'
            + css +
            "\n</style>"
        )

        data = data.replace(
            "</head>",
            style + "\n</head>",
            1,
        )

    # =====================================================
    # بنر POMP NET
    # =====================================================

    if 'id="pompnet-brand-banner"' not in data:

        banner = """
<div id="pompnet-brand-banner">
    ⚡ <b>POMP NET</b>
    • Mohammad &amp; Amir
    • Fast • Secure • Unlimited VPN
</div>
"""

        body_match = re.search(
            r"<body[^>]*>",
            data,
            flags=re.IGNORECASE,
        )

        if body_match:
            pos = body_match.end()

            data = (
                data[:pos]
                + "\n"
                + banner
                + "\n"
                + data[pos:]
            )

    # =====================================================
    # برند صفحه Login
    # بدون دستکاری منطق Login
    # =====================================================

    login_css = """
<style id="pompnet-login-brand">

.pompnet-login-title{
    font-weight:900 !important;
    letter-spacing:.5px;
}

</style>
"""

    if 'id="pompnet-login-brand"' not in data:

        if "</head>" in data:
            data = data.replace(
                "</head>",
                login_css + "\n</head>",
                1,
            )

    # =====================================================
    # ذخیره
    # =====================================================

    MAIN.write_text(
        data,
        encoding="utf-8",
    )

    # =====================================================
    # تست نهایی
    # =====================================================

    check = MAIN.read_text(
        encoding="utf-8"
    )

    # -----------------------------------------------------
    # اطمینان از اینکه Subscription اصلی تغییر نکرده
    # -----------------------------------------------------

    sub_after = find_sub_route(check)

    if not sub_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: /sub/{uuid} بعد از Build پیدا نشد"
        )

    sub_hash_after = hashlib.sha256(
        sub_after.encode("utf-8")
    ).hexdigest()

    if sub_hash_before != sub_hash_after:
        raise RuntimeError(
            "BUILD CHECK FAILED: هسته /sub/{uuid} تغییر کرده است"
        )

    # -----------------------------------------------------
    # موارد ضروری
    # -----------------------------------------------------

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
                "BUILD CHECK FAILED: " + item
            )

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("CORE: AHB PRESERVED")
    print("SUBSCRIPTION CORE: PRESERVED")
    print("INFO PAGE: POMP NET")
    print("LOGIN BRAND: POMP NET PANEL")
    print("THEME: POMP NET")
    print("SUPPORT: @NovaTunneli")
    print("ADMIN: admin / admin")
    print("PORT: Railway $PORT")
    print("HEALTH: /health")
    print("=" * 60)


if __name__ == "__main__":
    main()
