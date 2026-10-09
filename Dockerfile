FROM python:3.11-slim

ARG AHB_CORE_COMMIT=f95c118169fd6c66e6e5b155a716cbdfc6e330c7
ARG XRAY_VERSION=26.7.28

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONHASHSEED=random

ENV PORT=8080
ENV DATA_DIR=/app/data
ENV ADMIN_USERNAME=admin

# رمزها و کلیدهای امنیتی را در Railway Variables تنظیم کن.
# هیچ رمز ثابت مدیریتی در Image قرار نمی‌گیرد.

ENV POMPNET_MAX_WS_CONNECTIONS=256
ENV POMPNET_WS_HANDSHAKE_LIMIT=60
ENV POMPNET_WS_HANDSHAKE_WINDOW=60
ENV POMPNET_HSTS=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
       curl \
       unzip \
    && rm -rf /var/lib/apt/lists/*

# دریافت نسخه مشخص‌شده هسته اصلی پنل
RUN git clone \
      https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git \
      /tmp/ahb-core \
    && cd /tmp/ahb-core \
    && git checkout --detach "${AHB_CORE_COMMIT}" \
    && cp -a . /app/ \
    && rm -rf /tmp/ahb-core \
    && test -f /app/main.py

# نصب Xray
RUN arch="$(uname -m)" \
    && case "$arch" in \
        x86_64) XRAY_ARCH="64" ;; \
        aarch64) XRAY_ARCH="arm64-v8a" ;; \
        armv7l) XRAY_ARCH="arm32-v7a" ;; \
        *) echo "Unsupported architecture: $arch" && exit 1 ;; \
       esac \
    && curl -fL \
       "https://github.com/XTLS/Xray-core/releases/download/v${XRAY_VERSION}/Xray-linux-${XRAY_ARCH}.zip" \
       -o /tmp/xray.zip \
    && mkdir -p /tmp/xray \
    && unzip -q /tmp/xray.zip -d /tmp/xray \
    && test -f /tmp/xray/xray \
    && install -m 0755 /tmp/xray/xray /usr/local/bin/xray \
    && /usr/local/bin/xray version \
    && rm -rf /tmp/xray /tmp/xray.zip

# فایل‌های برند POMP NET
COPY pompnet.css /app/pompnet.css
COPY pompnet_login.css /tmp/pompnet_login.css
COPY pompnet_login.js /tmp/pompnet_login.js

COPY pompnet_brand.py /tmp/pompnet_brand.py
COPY pompnet_brand_fix.py /tmp/pompnet_brand_fix.py

COPY pompnet_security.py /app/pompnet_security.py
COPY pompnet_xray.py /app/pompnet_xray.py
COPY xray_manager.py /app/xray_manager.py
COPY pompnet_runtime.py /app/pompnet_runtime.py
COPY app_wrapper.py /app/app_wrapper.py
COPY requirements.txt /app/requirements.txt

# اصلاح ورود
COPY pompnet_login_patch.py /tmp/pompnet_login_patch.py
COPY pompnet_login_credit.py /tmp/pompnet_login_credit.py

# بررسی وجود فایل‌های ضروری
RUN test -f /app/main.py \
    && test -f /app/pompnet_security.py \
    && test -f /app/pompnet_xray.py \
    && test -f /app/xray_manager.py \
    && test -f /app/pompnet_runtime.py \
    && test -f /app/app_wrapper.py \
    && test -f /app/pompnet.css \
    && test -f /app/requirements.txt \
    && test -f /tmp/pompnet_brand.py \
    && test -f /tmp/pompnet_brand_fix.py \
    && test -f /tmp/pompnet_login_patch.py \
    && test -f /tmp/pompnet_login_credit.py \
    && /usr/local/bin/xray version

# اصلاح ظاهر بدون حذف مسیرهای اصلی پنل
RUN python /tmp/pompnet_brand.py \
    && python /tmp/pompnet_brand_fix.py

# اصلاح ورود واقعی
RUN python /tmp/pompnet_login_patch.py

# اعتبار برند در صفحه ورود
RUN python /tmp/pompnet_login_credit.py

# وابستگی‌ها
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# بررسی نحو فایل‌های Python
RUN python -m py_compile \
    /app/main.py \
    /app/pompnet_security.py \
    /app/pompnet_xray.py \
    /app/xray_manager.py \
    /app/pompnet_runtime.py \
    /app/app_wrapper.py \
    /tmp/pompnet_brand.py \
    /tmp/pompnet_brand_fix.py \
    /tmp/pompnet_login_patch.py \
    /tmp/pompnet_login_credit.py

# اجرای برنامه با کاربر غیر root
RUN useradd \
      --system \
      --uid 10001 \
      --create-home \
      --home-dir /home/pompnet \
      pompnet \
    && mkdir -p /app/data \
    && chown -R 10001:10001 /app /home/pompnet \
    && chmod 700 /app/data

USER 10001:10001

EXPOSE 8080

CMD ["sh", "-c", "exec python -m uvicorn app_wrapper:app --host 0.0.0.0 --port ${PORT:-8080}"]
