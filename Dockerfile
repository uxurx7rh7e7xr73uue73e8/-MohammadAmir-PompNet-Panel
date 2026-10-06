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

# دریافت هسته اصلی پنل از نسخه ثابت
RUN git clone \
      https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git \
      /tmp/ahbpanel \
    && cd /tmp/ahbpanel \
    && git checkout f95c118169fd6c66e6e5b155a716cbdfc6e330c7 \
    && cp -a . /app/ \
    && rm -rf /tmp/ahbpanel \
    && test -f /app/main.py

# فایل‌های POMP NET
COPY pompnet.css /app/pompnet.css
COPY pompnet_brand.py /tmp/pompnet_brand.py
COPY requirements.txt /app/requirements.txt

# بررسی کامل
RUN test -f /app/main.py \
    && test -f /app/pompnet.css \
    && test -f /tmp/pompnet_brand.py \
    && test -f /app/requirements.txt

# اعمال برندینگ
RUN python /tmp/pompnet_brand.py

# نصب وابستگی‌ها
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

# پورت پنل
EXPOSE 8080

# اجرای مستقیم روی 8080
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
