#!/bin/bash
# File: deploy/ubuntu24.04/installer.sh

# ISSUE: Missing error handling and proper paths
set -e  # Exit on error

# Create user and directories
sudo useradd -r -s /bin/false srt-monitor || true
sudo mkdir -p /opt/srt-monitor/app /opt/srt-monitor/static /var/lib/srt-monitor /var/log/srt-monitor
sudo chown -R srt-monitor:srt-monitor /opt/srt-monitor /var/lib/srt-monitor /var/log/srt-monitor

# Install dependencies
echo "Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential

# Create virtual environment
sudo -u srt-monitor python3 -m venv /opt/srt-monitor/venv

# Install Python packages
sudo -u srt-monitor /opt/srt-monitor/venv/bin/pip install --upgrade pip
sudo -u srt-monitor /opt/srt-monitor/venv/bin/pip install -r /opt/srt-monitor/app/requirements.txt

# Install the service
sudo cp deploy/ubuntu24.04/srt-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable srt-monitor
echo "Installation complete!"
