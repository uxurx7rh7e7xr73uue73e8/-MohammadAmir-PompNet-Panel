FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
       curl \
       unzip \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# AHB CORE واقعی
# ============================================================

RUN git clone \
      https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git \
      /tmp/ahb-core \
    && cd /tmp/ahb-core \
    && git checkout f95c118169fd6c66e6e5b155a716cbdfc6e330c7 \
    && cp -a . /app/ \
    && rm -rf /tmp/ahb-core \
    && test -f /app/main.py

# ============================================================
# Xray Core
# ============================================================

ARG XRAY_VERSION=26.7.28

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

# ============================================================
# POMP NET FILES
# ============================================================

COPY pompnet.css /app/pompnet.css
COPY pompnet_login.css /tmp/pompnet_login.css
COPY pompnet_login.js /tmp/pompnet_login.js
COPY pompnet_brand.py /tmp/pompnet_brand.py

COPY pompnet_xray.py /app/pompnet_xray.py
COPY xray_manager.py /app/xray_manager.py
COPY pompnet_runtime.py /app/pompnet_runtime.py
COPY app_wrapper.py /app/app_wrapper.py

COPY requirements.txt /app/requirements.txt

# ============================================================
# بررسی فایل‌ها
# ============================================================

RUN test -f /app/main.py \
    && test -f /app/pompnet.css \
    && test -f /app/pompnet_xray.py \
    && test -f /app/xray_manager.py \
    && test -f /app/pompnet_runtime.py \
    && test -f /app/app_wrapper.py \
    && test -f /tmp/pompnet_brand.py \
    && test -f /app/requirements.txt \
    && /usr/local/bin/xray version

# ============================================================
# برند POMP NET
# ============================================================

RUN python /tmp/pompnet_brand.py

# ============================================================
# Syntax Check
# ============================================================

RUN python -m py_compile \
    /app/main.py \
    /app/pompnet_xray.py \
    /app/xray_manager.py \
    /app/pompnet_runtime.py \
    /app/app_wrapper.py

# ============================================================
# Python Dependencies
# ============================================================

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8080

# Railway خودش PORT را تعیین می‌کند
CMD ["sh", "-c", "exec python -m uvicorn app_wrapper:app --host 0.0.0.0 --port ${PORT:-8080}"]
