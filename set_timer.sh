#!/bin/bash

set -e
# Environment vars upload
if [ -f .env ]
then
set -a
source .env
set +a
else
echo "No .env file found"
exit 1
fi


PROJECT_DIR=$(pwd)
echo "Current directory: $PROJECT_DIR"

DOCKER_PATH=$(which docker)
if [ -z "$DOCKER_PATH" ]
then
echo "ERROR: Docker not found. Make sure that it is installed and accessible."
exit 1
else
echo "Docker was found"
fi


# Create systemd service file
cat > /etc/systemd/system/vless_config_updater.service <<EOF
[Unit]
Description=Run Docker container for config updater
After=network.target

[Service]
Type=oneshot
WorkingDirectory=${PROJECT_DIR}
ExecStart=${DOCKER_PATH} run --rm --env-file .env -v ${PROJECT_DIR}/logs:/app/logs noisycake/vless_config_updater
EOF
echo "Service file was created"

# Create systemd timer file
cat > /etc/systemd/system/vless_config_updater.timer <<EOF
[Unit]
Description=Run vless_config_updater every ${UPDATE_DELAY} minute(s)

[Timer]
OnBootSec=10min
OnUnitActiveSec=${UPDATE_DELAY}min
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF
echo "Timer file was created"

# Create log cleaner systemd service
cat > /etc/systemd/system/vless_config_updater_log_cleaner.service <<EOF
[Unit]
Description=Clean logs older than ${LOG_RETENTION_DAYS} day(s)

[Service]
Type=oneshot
ExecStart=/usr/bin/fild ${PROJECT_DIR}/logs -type f -mtime +${LOG_RETENTION_DAYS} -delete
EOF
echo "Log cleaner service file was created"

# Create timer for log cleaner
cat > /etc/systemd/system/vless_config_updater_log_cleaner.timer <<EOF
[Unit]
Description=Run log cleaner every ${LOG_RETENTION_DAYS} day(s)

[Timer]
OnBootSec=15min
OnUnitActiveSec=${LOG_RETENTION_DAYS}d
Persistent=true

[Install]
WantedBy=timers.target
EOF
echo "Log cleaner timer file was created"

# Activate timer
systemctl daemon-reload
systemctl enable --now vless_config_updater.timer vless_config_updater_log_cleaner.timer

echo "Service is active. Checking:"
systemctl status vless_config_updater.timer
