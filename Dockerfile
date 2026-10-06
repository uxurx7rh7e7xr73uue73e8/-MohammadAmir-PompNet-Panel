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

RUN git clone https://github.com/uxurx7rh7e7xr73uue73e8/ahbpanel.git /tmp/ahbpanel \
    && cd /tmp/ahbpanel \
    && git checkout f95c118169fd6c66e6e5b155a716cbdfc6e330c7 \
    && cp -a . /app/ \
    && rm -rf /app/.git /tmp/ahbpanel

COPY pompnet_brand.py /tmp/pompnet_brand.py

RUN python /tmp/pompnet_brand.py

RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
