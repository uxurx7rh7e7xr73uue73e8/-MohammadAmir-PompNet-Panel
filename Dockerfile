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

# دریافت هسته اصلی پنل بدون دستکاری قابلیت‌های آن
RUN git clone \
      https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git \
      /tmp/panel-core \
    && cd /tmp/panel-core \
    && git checkout f95c118169fd6c66e6e5b155a716cbdfc6e330c7 \
    && cp -a . /app/ \
    && rm -rf /tmp/panel-core \
    && test -f /app/main.py

# پوسته POMP NET
COPY pompnet.css /app/pompnet.css
COPY pompnet_brand.py /tmp/pompnet_brand.py
COPY requirements.txt /app/requirements.txt

# بررسی فایل‌های ضروری
RUN test -f /app/main.py \
    && test -f /app/pompnet.css \
    && test -f /tmp/pompnet_brand.py \
    && test -f /app/requirements.txt

# اعمال برندینگ بدون تغییر منطق پنل
RUN python /tmp/pompnet_brand.py

# نصب وابستگی‌ها
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8080

# Railway PORT را خودش تعیین می‌کند
CMD ["sh", "-c", "exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
