# MohammadAmir-PompNet-Nexus

# POMP NET

## MR: Mohammad Pomp NetPanel

### Mohammad & Amir

This project keeps the original AHBPanel core and applies
POMP NET branding.

## ADMIN LOGIN

Username:

admin

Password:

admin

## SUPPORT

@NovaTunneli

## AMIR

@vpnstan2

Telegram:
https://t.me/vpnstan1

## POMP NET

Channel:
https://t.me/pompnet

Group:
https://t.me/+UV34C7Ohs9hiZTc0

## GITHUB

https://github.com/uxurx7rh7e7xr73uue73e8

## PROJECT

MohammadAmir-PompNet-Nexus

## DEPLOYMENT

Designed for Railway.

No Railway Volume is required for the initial deployment.

The original application is downloaded during the Docker build.

## IMPORTANT

The original application logic and features are preserved.

Only branding, support information and visible project identity
are customized for Mohammad & Amir / POMP NET.

🚀 آموزش کامل Fork → Railway → POMP NET

📌 پروژه

MohammadAmir-PompNet-Nexus

مبنای پروژه:

AHBPanel

---

🟣 مرحله 1 — Fork کردن پروژه

اول وارد پروژه اصلی AHBPanel در GitHub شو.

بالای صفحه روی:

Fork

بزن.

در صفحه‌ای که باز می‌شود:

Owner

اکانت GitHub خودت

Repository name

MohammadAmir-PompNet-Nexus

بعد:

Create fork

را بزن.

---

🟣 مرحله 2 — بررسی Fork

بعد از Fork باید وارد Repository خودت شوی.

فایل‌های اصلی پروژه باید همچنان وجود داشته باشند.

تقریباً:

main.py
pages.py
requirements.txt
relay_vless.py
speed_limit.py
telegram_bot.py
xhttp_siz10.py
news.json
README.md

❗ هیچ فایل اصلی را حذف نکن.

❗ پوشه یا فایل جدید را بدون نیاز اضافه نکن.

هدف:

همان پنل اصلی + تغییر برندینگ POMP NET

---

🟣 مرحله 3 — تغییر برند

در فایل‌های اصلی فقط قسمت‌های مربوط به برندینگ را تغییر بده.

نام:

POMP NET

عنوان:

MR: Mohammad Pomp NetPanel

تیم:

Mohammad & Amir

امیر:

@vpnstan2

کانال امیر:

https://t.me/vpnstan1

کانال POMP NET:

https://t.me/pompnet

گروه:

https://t.me/+UV34C7Ohs9hiZTc0

پشتیبانی:

@NovaTunneli

GitHub:

https://github.com/uxurx7rh7e7xr73uue73e8

---

🟣 مرحله 4 — Commit

بعد از تغییرات:

Commit changes

پیام Commit:

POMP NET branding

---

🚂 مرحله 5 — اتصال GitHub به Railway

وارد Railway شو.

New Project

سپس:

Deploy from GitHub Repo

را انتخاب کن.

Repository:

MohammadAmir-PompNet-Nexus

را انتخاب کن.

اگر Railway درخواست دسترسی GitHub کرد:

Configure GitHub App

را بزن و دسترسی Repository را فعال کن.

---

⚙️ مرحله 6 — تنظیمات Railway

بعد از ساخته شدن Service:

Variables

اگر پروژه نیاز داشت، متغیرها را اینجا قرار بده.

برای ورود مالک:

ADMIN_PASSWORD=admin

اگر خود سورس پروژه مقدار پیش‌فرض رمز را مدیریت می‌کند، همان تنظیمات سورس را نگه دار.

---

🔌 مرحله 7 — Port

در Railway نباید یک Port ثابت مثل:

443

برای Web Service تنظیم کنی.

برنامه باید روی:

0.0.0.0:$PORT

گوش بدهد.

Railway مقدار "$PORT" را خودش مشخص می‌کند.

---

▶️ مرحله 8 — Deploy

برو:

Deployments

و منتظر بمان تا:

BUILD
   ↓
DEPLOY
   ↓
SUCCESS

نمایش داده شود.

اگر:

FAILED

شد، وارد:

View Logs

شو.

---

🌐 مرحله 9 — ساخت Domain

بعد از Deploy موفق:

Service
↓
Settings
↓
Networking
↓
Generate Domain

Railway یک Domain HTTPS می‌دهد.

مثلاً:

https://xxxxx.up.railway.app

این آدرس پنل است.

---

🔐 مرحله 10 — ورود به پنل

اطلاعات اولیه:

Username: admin
Password: admin

اگر پنل فقط Password خواست:

admin

را وارد کن.

بعد از اولین ورود، رمز را تغییر بده.

---

🧪 مرحله 11 — چک کردن پنل

بعد از باز شدن پنل این قسمت‌ها را تست کن:

Dashboard

- باز شدن داشبورد
- آمار
- وضعیت سرویس

Users

- ساخت کاربر
- حذف/ویرایش
- حجم
- تاریخ انقضا
- وضعیت کاربر

Protocols

باید قابلیت‌های اصلی پروژه را بررسی کنی:

- VLESS
- VMess
- Trojan
- Shadowsocks
- XHTTP
- Xray

Subscription

- ساخت لینک
- نمایش Subscription
- کپی لینک
- QR

Traffic

- مصرف ترافیک
- محدودیت حجم
- وضعیت اتصال

Expiry

- تاریخ انقضا
- محدودیت زمانی

Speed

- محدودیت سرعت

Telegram

- تنظیمات Telegram
- Bot
- اعلان‌ها/امکانات موجود در نسخه اصلی

Admin

- حساب مالک
- حساب‌های مدیریتی
- تنظیمات مدیریت

---

🟢 قابلیت‌هایی که باید در نسخه POMP NET حفظ شوند

این پروژه قرار نیست پنل جدید و فیک باشد.

قابلیت‌های اصلی نسخه پایه باید حفظ شوند:

✅ Dashboard
✅ User Management
✅ VLESS
✅ VMess
✅ Trojan
✅ Shadowsocks
✅ XHTTP
✅ Xray
✅ Subscription
✅ QR Code
✅ Traffic
✅ Volume
✅ Expiry
✅ Speed Limit
✅ Telegram
✅ Admin Management
✅ News

---

❌ چه چیزهایی نباید حذف شوند؟

❌ main.py
❌ pages.py
❌ relay_vless.py
❌ speed_limit.py
❌ telegram_bot.py
❌ xhttp_siz10.py
❌ requirements.txt
❌ news.json

این فایل‌ها بخشی از سورس اصلی هستند و نباید برای تغییر ظاهر حذف شوند.

---

🎨 چیزهایی که قرار است تغییر کنند

فقط هویت پروژه:

AHBPanel
↓
POMP NET

و اطلاعات برند:

Mohammad & Amir

پشتیبانی:

@NovaTunneli

و لینک‌های Telegram مربوط به POMP NET.

منطق اصلی پنل نباید برای این تغییرات بازنویسی شود.

---

🔄 مرحله 12 — آپدیت خودکار

اگر Railway به GitHub وصل باشد:

GitHub
   ↓
Commit
   ↓
Railway
   ↓
Automatic Deploy

یعنی هر بار تغییرات را Push/Commit کنی، Railway می‌تواند نسخه جدید را Deploy کند.

---

💾 نکته مهم Storage

اگر Railway Volume اضافه نکنی، اطلاعاتی که برنامه فقط روی فایل‌های محلی کانتینر ذخیره می‌کند ممکن است با تعویض/حذف کانتینر باقی نماند.

برای تست اولیه:

Volume لازم نیست.

برای استفاده دائمی و جدی:

Storage دائمی باید بررسی شود.

---

🛠️ اگر پنل باز نشد

اول این موارد را بررسی کن:

Railway
↓
Service
↓
Deployments
↓
View Logs

اگر Build موفق بود ولی سایت باز نشد:

Settings
↓
Networking
↓
Domain

را بررسی کن.

اگر خطا وجود داشت، کل Logs را ارسال کن تا مشخص شود مشکل از Build، Port، Dependency یا Runtime است.

---

🎯 نتیجه نهایی

مسیر کامل:

AHBPanel
   ↓
Fork
   ↓
MohammadAmir-PompNet-Nexus
   ↓
Branding POMP NET
   ↓
GitHub
   ↓
Railway
   ↓
Build
   ↓
Deploy
   ↓
Generate Domain
   ↓
POMP NET Panel

🔐 ورود اولیه

Username: admin
Password: admin

👑 برند نهایی

POMP NET
MR: Mohammad Pomp NetPanel

Mohammad & Amir

هدف این است که هسته و قابلیت‌های اصلی پنل حفظ شوند و فقط مشخصات و برندینگ موردنظر تغییر کند.
