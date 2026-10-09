FROM python:3.11-slim

ARG AHB_CORE_COMMIT=f95c118169fd6c66e6e5b155a716cbdfc6e330c7
ARG XRAY_VERSION=26.7.28

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    DATA_DIR=/data \
    POMPNET_MAX_WS_CONNECTIONS=256 \
    POMPNET_WS_HANDSHAKE_LIMIT=60 \
    POMPNET_WS_HANDSHAKE_WINDOW=60 \
    POMPNET_HSTS=1 \
    ADMIN_USERNAME=admin \
    ADMIN_PASSWORD=admin

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git ca-certificates curl unzip \
    && rm -rf /var/lib/apt/lists/*

# دریافت هسته واقعی پنل در نسخه مشخص
RUN git clone \
      https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git \
      /tmp/panel-core \
    && cd /tmp/panel-core \
    && git checkout --detach "${AHB_CORE_COMMIT}" \
    && cp -a . /app/ \
    && rm -rf /tmp/panel-core \
    && test -f /app/main.py

# نصب هسته Xray
RUN arch="$(uname -m)" \
    && case "$arch" in \
        x86_64) XRAY_ARCH="64" ;; \
        aarch64) XRAY_ARCH="arm64-v8a" ;; \
        armv7l) XRAY_ARCH="arm32-v7a" ;; \
        *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
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

# فایل‌های پوسته و برند POMP NET
COPY pompnet.css /app/pompnet.css
COPY pompnet_login.css /tmp/pompnet_login.css
COPY pompnet_login.js /tmp/pompnet_login.js
COPY pompnet_brand.py /tmp/pompnet_brand.py
COPY pompnet_brand_fix.py /tmp/pompnet_brand_fix.py
COPY pompnet_login_patch.py /tmp/pompnet_login_patch.py
COPY pompnet_login_credit.py /tmp/pompnet_login_credit.py

# ماژول‌های موجود پروژه
COPY pompnet_security.py /app/pompnet_security.py
COPY pompnet_xray.py /app/pompnet_xray.py
COPY xray_manager.py /app/xray_manager.py
COPY pompnet_runtime.py /app/pompnet_runtime.py
COPY app_wrapper.py /app/app_wrapper.py
COPY requirements.txt /app/requirements.txt

# بررسی فایل‌های لازم
RUN test -f /app/main.py \
    && test -f /app/pompnet.css \
    && test -f /tmp/pompnet_login.css \
    && test -f /tmp/pompnet_login.js \
    && test -f /tmp/pompnet_brand.py \
    && test -f /tmp/pompnet_brand_fix.py \
    && test -f /tmp/pompnet_login_patch.py \
    && test -f /tmp/pompnet_login_credit.py \
    && test -f /app/pompnet_security.py \
    && test -f /app/pompnet_xray.py \
    && test -f /app/xray_manager.py \
    && test -f /app/pompnet_runtime.py \
    && test -f /app/app_wrapper.py \
    && test -f /app/requirements.txt

# اعمال برندینگ و وصله‌های ورود
RUN python /tmp/pompnet_brand.py \
    && python /tmp/pompnet_brand_fix.py \
    && python /tmp/pompnet_login_patch.py \
    && python /tmp/pompnet_login_credit.py

# نصب وابستگی‌ها
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# بررسی نگارش پایتون
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

RUN mkdir -p /data \
    && chmod 700 /data

EXPOSE 8080

# اجرای اپ واقعی با پورت Railway
CMD ["sh", "-c", "exec python -m uvicorn app_wrapper:app --host 0.0.0.0 --port ${PORT:-8080}"]
