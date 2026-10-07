from pathlib import Path
import re
import hashlib
import py_compile

ROOT = Path("/app")
MAIN = ROOT / "main.py"
CSS = ROOT / "pompnet.css"


def get_sub_route(data):
    pattern = re.compile(
        r'@app\.get\(\s*["\']/sub/\{uuid\}["\'].*?(?=\n@app\.get|\n@app\.post|\n@app\.websocket|\nasync def |\Z)',
        re.S,
    )
    m = pattern.search(data)
    return m.group(0) if m else None


def replace_info_html(data):

    marker = 'info_html = f"""'
    start = data.find(marker)

    if start == -1:
        raise RuntimeError("ERROR: info_html پیدا نشد")

    end = data.find('"""', start + len(marker))

    if end == -1:
        raise RuntimeError("ERROR: پایان info_html پیدا نشد")

    template = r'''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#05020d">
<title>POMP NET PANEL</title>

<style>
*{box-sizing:border-box}

html,body{
margin:0;
min-height:100%;
}

body{
font-family:Tahoma,Vazirmatn,Arial,sans-serif;
color:#fff;
background:
radial-gradient(circle at 10% 5%,rgba(124,58,237,.28),transparent 30%),
radial-gradient(circle at 95% 15%,rgba(37,99,235,.25),transparent 30%),
linear-gradient(135deg,#020106,#090414 50%,#020617);
}

.pn{
width:min(1080px,94%);
margin:auto;
padding:18px 0 45px;
}

.card{
border:1px solid rgba(139,92,246,.22);
border-radius:24px;
background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025));
box-shadow:0 18px 60px rgba(0,0,0,.35);
backdrop-filter:blur(18px);
}

.header{
padding:24px;
position:relative;
overflow:hidden;
background:
radial-gradient(circle at 100% 0,rgba(124,58,237,.28),transparent 45%),
radial-gradient(circle at 0 100%,rgba(37,99,235,.22),transparent 45%),
rgba(8,4,18,.75);
}

.header:after{
content:"";
position:absolute;
width:190px;
height:190px;
right:-80px;
top:-100px;
border-radius:50%;
background:#7c3aed;
opacity:.12;
filter:blur(45px);
}

.logo{
display:flex;
align-items:center;
gap:14px;
position:relative;
z-index:1;
}

.logo-icon{
width:60px;
height:60px;
border-radius:18px;
display:grid;
place-items:center;
font-size:29px;
background:linear-gradient(135deg,#7c3aed,#2563eb);
box-shadow:0 10px 35px rgba(124,58,237,.4);
}

.title{
font-size:27px;
font-weight:900;
letter-spacing:.5px;
}

.subtitle{
color:#a7a2b7;
font-size:12px;
margin-top:5px;
}

.status{
display:inline-flex;
align-items:center;
gap:8px;
margin-top:17px;
padding:8px 14px;
border-radius:999px;
background:rgba(34,197,94,.10);
border:1px solid rgba(34,197,94,.25);
color:#86efac;
font-size:12px;
font-weight:900;
}

.dot{
width:8px;
height:8px;
border-radius:50%;
background:#22c55e;
box-shadow:0 0 12px #22c55e;
}

.stats{
display:grid;
grid-template-columns:repeat(4,1fr);
gap:12px;
margin-top:14px;
}

.stat{
padding:17px;
}

.label{
color:#9993aa;
font-size:11px;
margin-bottom:8px;
}

.value{
font-size:17px;
font-weight:900;
word-break:break-word;
}

.main{
display:grid;
grid-template-columns:330px 1fr;
gap:14px;
margin-top:14px;
}

.usage{
padding:22px;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
min-height:320px;
}

.section-title{
font-size:16px;
font-weight:900;
margin-bottom:16px;
}

.ring{
width:185px;
height:185px;
border-radius:50%;
display:grid;
place-items:center;
background:
conic-gradient(
#8b5cf6 0deg,
#2563eb __USAGE__%,
rgba(255,255,255,.07) __USAGE__%,
rgba(255,255,255,.07) 100%
);
box-shadow:0 0 55px rgba(124,58,237,.20);
}

.ring-inner{
width:157px;
height:157px;
border-radius:50%;
background:#08050f;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
border:1px solid rgba(255,255,255,.06);
}

.percent{
font-size:30px;
font-weight:900;
}

.percent-small{
color:#9993aa;
font-size:11px;
margin-top:4px;
}

.info{
padding:21px;
}

.rows{
display:grid;
gap:8px;
}

.row{
display:flex;
align-items:center;
justify-content:space-between;
gap:15px;
padding:12px 13px;
border-radius:14px;
background:rgba(255,255,255,.035);
border:1px solid rgba(255,255,255,.055);
}

.row span:first-child{
color:#9892a6;
font-size:11px;
white-space:nowrap;
}

.row span:last-child{
font-size:12px;
font-weight:700;
word-break:break-all;
direction:ltr;
text-align:left;
}

.links{
padding:21px;
margin-top:14px;
}

.input-row{
display:flex;
gap:8px;
margin:7px 0 13px;
}

.input{
flex:1;
min-width:0;
padding:13px;
border-radius:13px;
border:1px solid rgba(255,255,255,.08);
background:#05030a;
color:#ddd;
direction:ltr;
outline:none;
font-size:11px;
}

.copy{
border:0;
border-radius:13px;
padding:0 18px;
color:#fff;
font-weight:900;
background:linear-gradient(135deg,#7c3aed,#2563eb);
cursor:pointer;
}

.support{
display:block;
text-decoration:none;
text-align:center;
padding:14px;
border-radius:15px;
margin-top:5px;
color:#fff;
font-weight:900;
background:linear-gradient(135deg,rgba(124,58,237,.42),rgba(37,99,235,.32));
border:1px solid rgba(139,92,246,.30);
}

.footer{
text-align:center;
color:#716b80;
font-size:10px;
padding-top:15px;
}

@media(max-width:850px){
.stats{grid-template-columns:repeat(2,1fr)}
.main{grid-template-columns:1fr}
}

@media(max-width:520px){
.pn{width:92%}
.header{padding:19px}
.title{font-size:22px}
.stats{gap:8px}
.stat{padding:14px}
.value{font-size:14px}
.usage{min-height:280px}
.ring{width:165px;height:165px}
.ring-inner{width:141px;height:141px}
.input-row{flex-direction:column}
.copy{min-height:44px}
}
</style>
</head>

<body>

<div class="pn">

<section class="card header">

<div class="logo">

<div class="logo-icon">
⚡
</div>

<div>

<div class="title">
POMP NET
</div>

<div class="subtitle">
Fast • Secure • Unlimited VPN
</div>

</div>

</div>

<div class="status">
<span class="dot"></span>
__STATUS__
</div>

</section>


<section class="stats">

<div class="card stat">
<div class="label">کاربر</div>
<div class="value">__LABEL__</div>
</div>

<div class="card stat">
<div class="label">حجم مصرف شده</div>
<div class="value">__USED__</div>
</div>

<div class="card stat">
<div class="label">حجم کل</div>
<div class="value">__TOTAL__</div>
</div>

<div class="card stat">
<div class="label">حجم باقی مانده</div>
<div class="value">__REMAINING__</div>
</div>

</section>


<section class="main">

<div class="card usage">

<div class="section-title">
مصرف اینترنت
</div>

<div class="ring">

<div class="ring-inner">

<div class="percent">
__USAGE__%
</div>

<div class="percent-small">
مصرف شده
</div>

</div>

</div>

</div>


<div class="card info">

<div class="section-title">
اطلاعات اشتراک
</div>

<div class="rows">

<div class="row">
<span>تاریخ انقضا</span>
<span>__EXPIRY__</span>
</div>

<div class="row">
<span>زمان باقی مانده</span>
<span>__EXPIRY_REMAINING__</span>
</div>

<div class="row">
<span>Protocol</span>
<span>__PROTOCOL__</span>
</div>

<div class="row">
<span>Fingerprint</span>
<span>__FINGERPRINT__</span>
</div>

<div class="row">
<span>IP Limit</span>
<span>__IP_LIMIT__</span>
</div>

<div class="row">
<span>Connection Limit</span>
<span>__CONN_LIMIT__</span>
</div>

<div class="row">
<span>Speed Limit</span>
<span>__SPEED_LIMIT__</span>
</div>

</div>

</div>

</section>


<section class="card links">

<div class="section-title">
لینک‌های اتصال
</div>

<div class="label">
VLESS
</div>

<div class="input-row">

<input
class="input"
id="pomp-vless"
value="__VLESS__"
readonly
>

<button
class="copy"
onclick="copyPomp('pomp-vless',this)"
>
کپی
</button>

</div>


<div class="label">
Subscription
</div>

<div class="input-row">

<input
class="input"
id="pomp-sub"
value="__SUB__"
readonly
>

<button
class="copy"
onclick="copyPomp('pomp-sub',this)"
>
کپی
</button>

</div>


<a
class="support"
href="https://t.me/NovaTunneli"
target="_blank"
rel="noopener"
>
💬 پشتیبانی POMP NET
</a>

</section>


<div class="footer">
POMP NET • Mohammad &amp; Amir
</div>

</div>


<script>
function copyPomp(id,button){

const input=document.getElementById(id);

if(!input)return;

if(navigator.clipboard){

navigator.clipboard.writeText(input.value)
.then(function(){

const old=button.innerText;

button.innerText="کپی شد ✓";

setTimeout(function(){
button.innerText=old;
},1500);

});

}else{

input.select();
document.execCommand("copy");

}

}
</script>

</body>
</html>
'''

    values = {
        "__STATUS__": "{status_text}",
        "__LABEL__": "{label}",
        "__USED__": "{used_e}",
        "__TOTAL__": "{total_e}",
        "__REMAINING__": "{remaining_e}",
        "__USAGE__": "{usage_percent}",
        "__EXPIRY__": "{expiry_e}",
        "__EXPIRY_REMAINING__": "{expiry_remaining_e}",
        "__PROTOCOL__": "{protocol}",
        "__FINGERPRINT__": "{fingerprint}",
        "__IP_LIMIT__": "{ip_limit}",
        "__CONN_LIMIT__": "{conn_limit}",
        "__SPEED_LIMIT__": "{speed_limit}",
        "__VLESS__": "{vless_e}",
        "__SUB__": "{sub_e}",
    }

    for old, new in values.items():
        template = template.replace(old, new)

    new_block = 'info_html = f"""' + template + '"""'

    return data[:start] + new_block + data[end + 3:]


def main():

    if not MAIN.exists():
        raise RuntimeError("ERROR: main.py پیدا نشد")

    if not CSS.exists():
        raise RuntimeError("ERROR: pompnet.css پیدا نشد")

    data = MAIN.read_text(encoding="utf-8")

    # =====================================================
    # BACKUP منطقی داخل Build
    # =====================================================

    sub_before = get_sub_route(data)

    if not sub_before:
        raise RuntimeError("ERROR: /sub/{uuid} پیدا نشد")

    sub_hash_before = hashlib.sha256(
        sub_before.encode("utf-8")
    ).hexdigest()

    # =====================================================
    # Branding فقط
    # =====================================================

    replacements = {

        "AHB PANEL": "POMP NET PANEL",
        "AHB Panel": "POMP NET PANEL",

        "Created By Ahb": "Created By POMP NET",
        "Created By AHB": "Created By POMP NET",

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

    for old, new in replacements.items():
        data = data.replace(old, new)

    # =====================================================
    # APP Branding
    # فقط اگر متغیر وجود داشته باشد
    # =====================================================

    data = re.sub(
        r'APP_NAME\s*=\s*["\'][^"\']*["\']',
        'APP_NAME = "POMP NET"',
        data,
        count=1
    )

    data = re.sub(
        r'SUPPORT_USERNAME\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_USERNAME = "@NovaTunneli"',
        data,
        count=1
    )

    data = re.sub(
        r'SUPPORT_URL\s*=\s*["\'][^"\']*["\']',
        'SUPPORT_URL = "https://t.me/NovaTunneli"',
        data,
        count=1
    )

    # =====================================================
    # INFO PAGE
    # =====================================================

    data = replace_info_html(data)

    # =====================================================
    # Title
    # =====================================================

    data = re.sub(
        r"<title>.*?</title>",
        "<title>POMP NET PANEL</title>",
        data,
        flags=re.I,
        count=1
    )

    # =====================================================
    # POMP NET CSS
    # =====================================================

    css = CSS.read_text(encoding="utf-8")

    if 'id="pompnet-css"' not in data:

        if "</head>" in data:

            data = data.replace(
                "</head>",
                '<style id="pompnet-css">\n'
                + css +
                '\n</style>\n</head>',
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
    # Python Syntax Check
    # =====================================================

    try:
        py_compile.compile(
            str(MAIN),
            doraise=True
        )
    except Exception as e:
        raise RuntimeError(
            "BUILD CHECK FAILED: Python Syntax Error\n"
            + str(e)
        )

    # =====================================================
    # Subscription Protection
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

    # =====================================================
    # Required Checks
    # =====================================================

    required = [
        "/sub/{uuid}",
        'async def info_page',
        "POMP NET",
        "@NovaTunneli",
        "https://t.me/NovaTunneli",
        "pompnet-css",
    ]

    for item in required:

        if item not in check:

            raise RuntimeError(
                "BUILD CHECK FAILED: "
                + item
            )

    print("=" * 60)
    print("POMP NET BUILD CHECK: OK")
    print("PYTHON SYNTAX: OK")
    print("CORE: AHB PRESERVED")
    print("SUBSCRIPTION: PRESERVED")
    print("INFO PAGE: POMP NET")
    print("BRANDING: POMP NET")
    print("SUPPORT: @NovaTunneli")
    print("PORT: Railway $PORT")
    print("HEALTH: /health")
    print("=" * 60)


if __name__ == "__main__":
    main()
