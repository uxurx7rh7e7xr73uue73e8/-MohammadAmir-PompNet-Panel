# MohammadAmir-PompNet-Nexus

# 🚀 POMP NET

## MR: Mohammad Pomp NetPanel

### Mohammad & Amir

پنل POMP NET بر پایه هسته اصلی AHBPanel.

هدف پروژه:

- حفظ هسته اصلی AHBPanel
- حفظ قابلیت‌های اصلی
- تغییر برند و مشخصات به POMP NET
- آماده‌سازی برای Deploy روی Railway
- بدون بازنویسی فیک پنل

---

# 👑 BRAND

## POMP NET

### MR: Mohammad Pomp NetPanel

### Mohammad & Amir

---

## 👤 AMIR

Telegram:

@vpnstan2

Channel:

https://t.me/vpnstan1

---

## 🚀 POMP NET

Channel:

https://t.me/pompnet

Group:

https://t.me/+UV34C7Ohs9hiZTc0

---

## 🛟 SUPPORT

@NovaTunneli

Support:

https://t.me/NovaTunneli

---

## 💻 GITHUB

https://github.com/uxurx7rh7e7xr73uue73e8

---

# 📦 PROJECT

Repository:

MohammadAmir-PompNet-Nexus

Base:

AHBPanel

---

# ⚠️ معماری پروژه

این Repository یک Fork کامل از سورس AHBPanel نیست.

برای جلوگیری از کپی و نگهداری چند نسخه از هسته اصلی، Docker هنگام Build نسخه مشخص‌شده AHBPanel را دریافت می‌کند.

سپس:

1. سورس اصلی دریافت می‌شود.
2. نسخه مشخص AHBPanel استفاده می‌شود.
3. فایل Branding اجرا می‌شود.
4. فقط مشخصات نمایشی POMP NET تغییر می‌کند.
5. برنامه اصلی اجرا می‌شود.

بنابراین هسته اصلی پنل بازنویسی یا شبیه‌سازی نمی‌شود.

---

# 🧩 فایل‌های Repository

فایل‌های اصلی این Repository:

- Dockerfile
- railway.json
- requirements.txt
- pompnet_brand.py
- README.md

هسته اصلی AHBPanel در زمان Docker Build دریافت می‌شود.

بنابراین نباید فایل‌های اصلی AHBPanel را به صورت فیک یا ناقص به Repository اضافه کرد.

---

# 🛡️ حفظ هسته اصلی

فایل‌های اصلی AHBPanel نباید حذف یا بازنویسی شوند.

از جمله:

- main.py
- pages.py
- relay_vless.py
- speed_limit.py
- telegram_bot.py
- xhttp_siz10.py
- news.json

این فایل‌ها توسط Docker از نسخه اصلی پروژه دریافت می‌شوند.

---

# 🎨 BRANDING

هویت پروژه:

AHBPanel

به:

POMP NET

تغییر داده می‌شود.

عنوان:

MR: Mohammad Pomp NetPanel

تیم:

Mohammad & Amir

پشتیبانی:

@NovaTunneli

کانال:

https://t.me/pompnet

---

# 🔐 ADMIN LOGIN

برای ورود اولیه:

Username:

admin

Password:

admin

مقدار رمز از متغیر زیر دریافت می‌شود:

ADMIN_PASSWORD

برای تست اولیه Railway:

ADMIN_PASSWORD=admin

بعد از ورود اولیه بهتر است رمز تغییر داده شود.

---

# 🚂 RAILWAY DEPLOYMENT

## مرحله 1

وارد Railway شوید.

New Project

سپس:

Deploy from GitHub Repo

را انتخاب کنید.

Repository:

MohammadAmir-PompNet-Nexus

---

# ⚙️ مرحله 2 — Variables

در Railway وارد:

Service

↓

Variables

شوید.

برای ورود اولیه:

ADMIN_PASSWORD=admin

قرار دهید.

---

# 🔌 مرحله 3 — PORT

برنامه باید روی Port اختصاص داده‌شده توسط Railway اجرا شود.

Dockerfile پروژه از:

0.0.0.0

و:

$PORT

استفاده می‌کند.

بنابراین نباید Port ثابت مثل:

443

تنظیم شود.

---

# ▶️ مرحله 4 — DEPLOY

بعد از اتصال GitHub:

Deploy

را انجام دهید.

مراحل:

BUILD

↓

DEPLOY

↓

RUNNING

---

# 🩺 HEALTH CHECK

پنل دارای Health Check است:

/health

در صورت موفق بودن:

HTTP 200

برمی‌گردد.

Railway از این مسیر برای بررسی وضعیت سرویس استفاده می‌کند.

---

# 🌐 مرحله 5 — DOMAIN

بعد از Deploy موفق:

Service

↓

Settings

↓

Networking

↓

Generate Domain

را انتخاب کنید.

Railway یک Domain HTTPS ایجاد می‌کند.

مثلاً:

https://xxxxx.up.railway.app

---

# 🔐 مرحله 6 — LOGIN

بعد از باز شدن پنل:

Username:

admin

Password:

admin

اگر ADMIN_PASSWORD در Railway تغییر کرده باشد، همان رمز جدید استفاده می‌شود.

---

# 🧪 بررسی پنل

بعد از Deploy باید قابلیت‌های موجود در نسخه اصلی بررسی شوند.

## Dashboard

- Dashboard
- وضعیت سرویس
- آمار موجود در نسخه اصلی

## Users

- ایجاد کاربر
- ویرایش
- حذف
- حجم
- تاریخ انقضا
- وضعیت کاربر

## Protocols

قابلیت‌های موجود در نسخه اصلی مانند:

- VLESS
- VMess
- Trojan
- Shadowsocks
- XHTTP
- Xray

## Subscription

- Subscription
- لینک اتصال
- Copy
- QR

## Traffic

- مصرف ترافیک
- Volume
- محدودیت حجم

## Expiry

- تاریخ انقضا
- محدودیت زمانی

## Speed

- Speed Limit

## Telegram

- Telegram
- Bot
- امکانات موجود در نسخه اصلی

## Admin

- Owner
- Admin
- مدیریت کاربران مدیریتی در صورت وجود در نسخه اصلی

## News

- News

---

# 🟢 اصل مهم پروژه

POMP NET قرار نیست یک پنل فیک باشد.

هدف:

AHBPanel Core

+

POMP NET Branding

است.

منطق اصلی برنامه نباید برای تغییر برند بازنویسی شود.

---

# 🔄 AUTO DEPLOY

در صورت اتصال صحیح GitHub به Railway:

GitHub

↓

Commit

↓

Railway

↓

Automatic Deploy

بنابراین تغییرات جدید Repository می‌توانند به صورت خودکار Deploy شوند.

---

# 💾 STORAGE

در Deploy اولیه Railway Volume الزامی نیست.

اما توجه کنید:

اطلاعاتی که برنامه فقط روی فایل‌های محلی کانتینر ذخیره می‌کند ممکن است بعد از تعویض یا حذف Container باقی نماند.

برای تست:

Volume لازم نیست.

برای استفاده دائمی:

Persistent Storage

باید در نظر گرفته شود.

---

# 🛠️ اگر پنل باز نشد

اول:

Railway

↓

Service

↓

Deployments

↓

View Logs

را بررسی کنید.

اگر Build موفق شد ولی پنل باز نشد:

Settings

↓

Networking

↓

Domain

را بررسی کنید.

همچنین Health Check:

/health

را بررسی کنید.

---

# ❌ کارهایی که نباید انجام شوند

❌ حذف هسته اصلی AHBPanel

❌ ساخت main.py فیک

❌ ساخت pages.py فیک

❌ حذف requirements اصلی

❌ تغییر منطق اصلی فقط برای Branding

❌ تغییر Port به 443

❌ حذف Dockerfile

❌ حذف railway.json

---

# 🎯 ساختار نهایی

AHBPanel

↓

Docker Build

↓

دریافت نسخه اصلی

↓

POMP NET Branding

↓

FastAPI / Uvicorn

↓

Railway

↓

HTTPS Domain

↓

POMP NET Panel

---

# 👑 FINAL BRAND

POMP NET

MR: Mohammad Pomp NetPanel

Mohammad & Amir

Support:

@NovaTunneli

Telegram:

https://t.me/pompnet

GitHub:

https://github.com/uxurx7rh7e7xr73uue73e8

---

# 🔐 INITIAL LOGIN

Username:

admin

Password:

admin

---

## هدف نهایی

حفظ هسته واقعی AHBPanel و تمام قابلیت‌های موجود در نسخه اصلی، همراه با برندینگ اختصاصی:

POMP NET

Mohammad & Amir
