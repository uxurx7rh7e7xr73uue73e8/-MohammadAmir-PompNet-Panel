FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# رمز را در Railway Environment Variables تعیین کن
ENV ADMIN_PASSWORD=admin

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# AHB CORE واقعی
# فقط هسته اصلی AHB گرفته می‌شود
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
# POMP NET BRAND
# ============================================================

COPY pompnet.css /app/pompnet.css
COPY pompnet_login.css /tmp/pompnet_login.css
COPY pompnet_login.js /tmp/pompnet_login.js
COPY pompnet_brand.py /tmp/pompnet_brand.py
COPY requirements.txt /app/requirements.txt

# بررسی فایل‌ها
RUN test -f /app/main.py \
    && test -f /app/pompnet.css \
    && test -f /tmp/pompnet_login.css \
    && test -f /tmp/pompnet_login.js \
    && test -f /tmp/pompnet_brand.py \
    && test -f /app/requirements.txt

# ============================================================
# فقط تغییر ظاهر و برند
# قابلیت‌های اصلی AHB دست‌نخورده می‌مانند
# ============================================================

RUN python /tmp/pompnet_brand.py

# نصب وابستگی‌های خود هسته
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# Railway پورت را از PORT می‌دهد
EXPOSE 8080

CMD ["sh", "-c", "exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
