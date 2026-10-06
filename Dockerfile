FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV ADMIN_PASSWORD=admin

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# =========================================================
# دریافت نسخه ثابت هسته اصلی پنل
# =========================================================

RUN set -eux; \
    git clone \
      --depth 1 \
      https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git \
      /tmp/ahbpanel; \
    cd /tmp/ahbpanel; \
    git fetch --depth 1 origin f95c118169fd6c66e6e5b155a716cbdfc6e330c7; \
    git checkout f95c118169fd6c66e6e5b155a716cbdfc6e330c7; \
    cp -a . /app/; \
    rm -rf /app/.git /tmp/ahbpanel

# =========================================================
# فایل‌های POMP NET
# =========================================================

COPY pompnet.css /app/pompnet.css
COPY pompnet_brand.py /tmp/pompnet_brand.py
COPY requirements.txt /app/requirements.txt

# =========================================================
# بررسی فایل‌های ضروری
# =========================================================

RUN test -f /app/main.py \
    && test -f /app/requirements.txt \
    && test -f /app/pompnet.css \
    && python --version

# =========================================================
# اعمال برندینگ
# =========================================================

RUN python /tmp/pompnet_brand.py

# =========================================================
# نصب وابستگی‌ها
# =========================================================

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# =========================================================
# Railway
# =========================================================

EXPOSE 8000

CMD ["sh", "-c", "exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
