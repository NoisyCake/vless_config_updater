#!/bin/bash

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
ExecStart=${DOCKER_PATH} run --rm --env-file .env -v ${PROJECT_DIR}/logs:/app/logs noisycake/vless_config_updater:1.0.0
EOF
echo "Service file was created"

# Create systemd timer file
cat > /etc/systemd/system/vless_config_updater.timer <<EOF
[Unit]
Description=Run vless_config_updater every 30 minutes

[Timer]
OnBootSec=10min
OnUnitActiveSec=30min
AccuracySec=1min

[Install]
WantedBy=timers.target
EOF
echo "Timer file was created"


# Activate timer
systemctl daemon-reload
systemctl enable --now vless_config_updater.timer

echo "Service is active. Checking:"
systemctl status vless_config_updater.timer
