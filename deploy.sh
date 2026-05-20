#!/bin/bash
set -e

APP_DIR="/opt/income_expense_bot"
SERVICE_NAME="income_expense_bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
ENV_FILE="${APP_DIR}/env.env"
REPO_URL="https://github.com/VovaZhukovsky/income_expense_bot.git"

# Clone or pull
if [ ! -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" init
  git -C "$APP_DIR" remote add origin "$REPO_URL"
  git -C "$APP_DIR" pull origin main
else
  git -C "$APP_DIR" pull origin main
fi

# Create env.env if missing
if [ ! -f "$ENV_FILE" ]; then
  echo "env.env not found at $ENV_FILE"
  exit 1
fi
sudo chown "$USER:$USER" "$ENV_FILE"
chmod 600 "$ENV_FILE"

# Create systemd service if missing
if [ ! -f "$SERVICE_FILE" ]; then
  sudo tee "$SERVICE_FILE" > /dev/null << SVCEOF
[Unit]
Description=Income Expense Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
EnvironmentFile=$ENV_FILE
ExecStart=/usr/bin/python3 $APP_DIR/income_expense_bot.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SVCEOF
  sudo systemctl daemon-reload
  sudo systemctl enable "${SERVICE_NAME}.service"
  echo "Service created and enabled"
fi

# Create logrotate config if missing
LOGROTATE_FILE="/etc/logrotate.d/${SERVICE_NAME}"
LOG_DIR="/var/log/${SERVICE_NAME}"
if [ ! -f "$LOGROTATE_FILE" ]; then
  sudo mkdir -p "$LOG_DIR"
  sudo chown "$USER:$USER" "$LOG_DIR"
  sudo tee "$LOGROTATE_FILE" > /dev/null << LREOF
${LOG_DIR}/${SERVICE_NAME}.log {
    rotate 12
    monthly
    compress
    missingok
    notifempty
}
LREOF
  echo "Logrotate config created"
fi

sudo systemctl restart "${SERVICE_NAME}.service"
sudo systemctl status "${SERVICE_NAME}.service" --no-pager
