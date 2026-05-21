FROM python:3.12-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    aria2 \
    qbittorrent-nox \
    ffmpeg \
    libmagic1 \
    libmagic-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    && ln -s /usr/bin/aria2c /usr/local/bin/xria \
    && ln -s /usr/bin/qbittorrent-nox /usr/local/bin/xnox \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv .venv \
    && . .venv/bin/activate \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

RUN git clone --depth 1 https://github.com/sabnzbd/sabnzbd.git /opt/sabnzbd \
    && . .venv/bin/activate \
    && pip install --no-cache-dir -r /opt/sabnzbd/requirements.txt \
    && printf '#!/bin/sh\nexec /app/.venv/bin/python /opt/sabnzbd/SABnzbd.py "$@"\n' > /usr/local/bin/xnzb \
    && chmod +x /usr/local/bin/xnzb

COPY . .
RUN chmod +x start.sh

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8070
EXPOSE 8080
CMD ["bash", "start.sh"]
