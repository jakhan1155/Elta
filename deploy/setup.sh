#!/usr/bin/env bash
# Установка бота ELTA на чистый сервер Ubuntu 24.04.
# Запуск (от root, из папки с файлами бота):  bash deploy/setup.sh <домен или пусто>
# Без домена магазин получает постоянный адрес вида https://1-2-3-4.sslip.io (по IP сервера).
set -euo pipefail

APP=/opt/elta-bot
DOMAIN="${1:-}"

echo "== Пакеты"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q python3-venv python3-pip debian-keyring debian-archive-keyring apt-transport-https curl ufw

echo "== Caddy (HTTPS для мини-приложения, сертификат выпускается сам)"
if ! command -v caddy >/dev/null; then
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -q && apt-get install -y -q caddy
fi

if [ -z "$DOMAIN" ]; then
  IP=$(curl -4 -s https://api.ipify.org)
  DOMAIN="${IP//./-}.sslip.io"
fi
echo "== Адрес магазина: https://$DOMAIN"

echo "== Пользователь и файлы"
id elta >/dev/null 2>&1 || useradd --system --home "$APP" --shell /usr/sbin/nologin elta
mkdir -p "$APP"
cp -r ./* ./.env "$APP"/ 2>/dev/null || cp -r ./* "$APP"/
chown -R elta:elta "$APP"

echo "== Python-окружение"
sudo -u elta python3 -m venv "$APP/.venv"
sudo -u elta "$APP/.venv/bin/pip" install -q -r "$APP/backend/requirements.txt"

echo "== Настройки: постоянный адрес, без временного туннеля"
sed -i '/^WEBAPP_URL=/d;/^TUNNEL=/d;/^WEB_HOST=/d;/^WEB_PORT=/d' "$APP/backend/.env"
printf 'WEBAPP_URL=https://%s\nTUNNEL=off\nWEB_HOST=127.0.0.1\nWEB_PORT=8080\n' "$DOMAIN" >> "$APP/backend/.env"

echo "== Служба бота (автозапуск и перезапуск при сбое)"
cat > /etc/systemd/system/elta-bot.service <<EOF
[Unit]
Description=ELTA Telegram bot + mini app
After=network-online.target
Wants=network-online.target

[Service]
User=elta
WorkingDirectory=$APP/backend
ExecStart=$APP/.venv/bin/python $APP/backend/src/main.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

echo "== Caddy: https://$DOMAIN -> бот"
cat > /etc/caddy/Caddyfile <<EOF
$DOMAIN {
    encode gzip
    reverse_proxy 127.0.0.1:8080
}
EOF

echo "== Файрвол: только SSH и веб"
ufw allow OpenSSH >/dev/null; ufw allow 80/tcp >/dev/null; ufw allow 443/tcp >/dev/null; ufw --force enable >/dev/null

systemctl daemon-reload
systemctl enable --now elta-bot
systemctl restart caddy
sleep 5
systemctl --no-pager --lines=5 status elta-bot || true
echo "== Готово: https://$DOMAIN"
