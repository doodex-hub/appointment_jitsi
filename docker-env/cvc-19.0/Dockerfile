FROM python:3.12-slim-bookworm

# Cross-Version Compare (Step 10) — instance 19.0 SOURCE (read-only reference), resep sama dengan ../Dockerfile
# (dibangun dari source native-source odoo19 yang di-mount lewat
# docker-compose.cvc.yml; odoo19 + enterprise19 di-mount read-only.
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential python3-dev \
    libpq-dev libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev \
    libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev libffi-dev \
    fonts-dejavu-core fonts-freefont-ttf fonts-noto-core fonts-inconsolata \
    fonts-font-awesome fonts-roboto-unhinted gsfonts \
    postgresql-client \
    wget gnupg ca-certificates \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && pip install --no-cache-dir websocket-client

RUN useradd -ms /bin/bash odoo
USER odoo

ENTRYPOINT ["python3", "/opt/odoo/odoo-bin"]
