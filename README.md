# MohammadAmir-PompNet

# 🚀 POMP NET

## MR: Mohammad Pomp NetPanel

### Mohammad & Amir

پنل اختصاصی POMP NET با حفظ هسته و قابلیت‌های اصلی پنل.

هدف پروژه:

- حفظ قابلیت‌های اصلی پنل
- تغییر کامل برند و مشخصات به POMP NET
- حفظ Subscription
- حفظ VLESS
- حفظ مدیریت کاربران
- حفظ ترافیک و تاریخ انقضا
- آماده‌سازی برای Deploy روی Railway
- بدون ساخت پنل فیک

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

MohammadAmir-PompNet

Base:

POMP NET Core

---

# ⚠️ معماری پروژه

این Repository شامل لایه اختصاصی POMP NET برای برندینگ، ظاهر و تنظیمات نمایشی پنل است.

در زمان Build، هسته اصلی برنامه دریافت و سپس Branding اختصاصی POMP NET روی آن اعمال می‌شود.

مراحل:

1. دریافت هسته اصلی
2. استفاده از نسخه مشخص
3. اجرای فایل Branding
4. اعمال برندینگ POMP NET
5. حفظ منطق اصلی برنامه
6. اجرای برنامه

منطق اصلی پنل برای تغییر برند بازنویسی یا شبیه‌سازی نمی‌شود.

---

# 🧩 فایل‌های Repository

فایل‌های اصلی این Repository:

- Dockerfile
- railway.json
- requirements.txt
- pompnet_brand.py
- README.md
- pompnet.css

فایل Branding وظیفه اعمال ظاهر و مشخصات اختصاصی POMP NET را دارد.

---

# 🛡️ حفظ قابلیت‌های اصلی

قابلیت‌های اصلی پنل نباید حذف یا خراب شوند.

از جمله:

- Dashboard
- Users
- VLESS
- VMess
- Trojan
- Shadowsocks
- XHTTP
- Xray
- Subscription
- Traffic
- Expiry
- Speed Limit
- Telegram
- Admin
- News

---

# 🎨 BRANDING

هویت پروژه:

POMP NET

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

MohammadAmir-PompNet

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

بعد از Deploy باید قابلیت‌های موجود بررسی شوند.

## Dashboard

- Dashboard
- وضعیت سرویس
- آمار

## Users

- ایجاد کاربر
- ویرایش
- حذف
- حجم
- تاریخ انقضا
- وضعیت کاربر

## Protocols

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
- امکانات موجود

## Admin

- Owner
- Admin
- مدیریت کاربران مدیریتی

## News

- News

---

# 🟢 اصل مهم پروژه

POMP NET یک پنل فیک نیست.

هدف:

حفظ قابلیت‌های واقعی پنل

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

اما اطلاعاتی که برنامه فقط روی فایل‌های محلی Container ذخیره می‌کند ممکن است بعد از تعویض یا حذف Container باقی نماند.

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

همچنین:

/health

را بررسی کنید.

---

# ❌ کارهایی که نباید انجام شوند

❌ حذف هسته اصلی

❌ ساخت main.py فیک

❌ ساخت pages.py فیک

❌ حذف requirements اصلی

❌ تغییر منطق اصلی فقط برای Branding

❌ تغییر Port به 443

❌ حذف Dockerfile

❌ حذف railway.json

---

# 🎯 ساختار نهایی

POMP NET Core

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

حفظ قابلیت‌های واقعی پنل همراه با برندینگ اختصاصی:

# POMP NET

### Mohammad & Amir
