FROM python:3.12-slim-bookworm

# G1 install test / Step 9 (20.0) — appointment_jitsi 19.0→20.0. Resep identik optional_field_save
# (belum ada image resmi `odoo:20.0`). Build dari source native-target (odoo20) yang di-mount lewat
# docker-compose.20.0.yml; enterprise20 di-mount terpisah (dependency `appointment` OEEL-1).
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
