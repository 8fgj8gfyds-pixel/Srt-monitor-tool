#!/bin/bash

# SRT Monitoring System - Ubuntu 24.04 Automated Installer
# Version: 2.0
# Author: 8fgj8gfyds-pixel
# License: MIT

set -e  # Exit on error

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for root
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}This installer must be run as root!${NC}"
    echo "Please use: sudo $0"
    exit 1
fi

# Check Ubuntu version
UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
if [[ "$UBUNTU_VERSION" != "24.04" ]]; then
    echo -e "${YELLOW}Warning: This script is optimized for Ubuntu 24.04${NC}"
    echo -n "Continue anyway? (y/N): "
    read answer
    if [[ ! "$answer" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}SRT Monitoring System Installer${NC}"
echo -e "${BLUE}Ubuntu 24.04${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Create installation directory
INSTALL_DIR="/opt/srt-monitor"
APP_DIR="$INSTALL_DIR/app"
LOG_DIR="/var/log/srt-monitor"
DATA_DIR="/var/lib/srt-monitor"

echo -e "${BLUE}Creating installation directories...${NC}"
mkdir -p "$APP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR/pcap_captures"
mkdir -p "$DATA_DIR/reports"

# Install system dependencies
echo -e "${BLUE}Updating system packages...${NC}"
apt-get update -y

echo -e "${BLUE}Installing system dependencies...${NC}"
apt-get install -y \
    python3 python3-pip python3-venv \
    git wget curl build-essential \
    libssl-dev libffi-dev \
    tcpdump tshark wireshark \
    ffmpeg nginx

# Install SRT from Haivision
echo -e "${BLUE}Installing SRT tools from Haivision...${NC}"
wget -q https://github.com/Haivision/srt/archive/refs/tags/v1.5.1.tar.gz -O /tmp/srt.tar.gz
tar -xzf /tmp/srt.tar.gz -C /tmp/
cd /tmp/srt-1.5.1
./configure --prefix=/usr/local --enable-apps
make -j$(nproc)
sudo make install
sudo ldconfig
cd /opt/srt-monitor
rm -rf /tmp/srt.tar.gz /tmp/srt-1.5.1

# Install Python dependencies
echo -e "${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv "$APP_DIR/venv"
source "$APP_DIR/venv/bin/activate"

echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"

# Install the application files
echo -e "${BLUE}Installing application files...${NC}"
cat > "$APP_DIR/config.py" << 'CONFIG_EOF'
# SRT Monitor Configuration
SECRET_KEY = 'your-secret-key-change-this'
DEBUG = False
HOST = '0.0.0.0'
PORT = 5000
LOG_FILE = '/var/log/srt-monitor/app.log'
DATA_DIR = '/var/lib/srt-monitor'
CONFIG_EOF

# Copy application files (you'll need to upload these)
# For now, we'll create placeholder files
cat > "$APP_DIR/app.py" << 'APP_EOF'
from flask import Flask
app = Flask(__name__)
@app.route('/')
def index():
    return "SRT Monitor is running!"
APP_EOF

# Copy service file
echo -e "${BLUE}Configuring systemd service...${NC}"
cat > /etc/systemd/system/srt-monitor.service << 'SERVICE_EOF'
[Unit]
Description=SRT Monitoring System
After=network.target

[Service]
User=srt-monitor
Group=srt-monitor
WorkingDirectory=/opt/srt-monitor/app
Environment="PATH=/opt/srt-monitor/app/venv/bin"
ExecStart=/opt/srt-monitor/app/venv/bin/python /opt/srt-monitor/app/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Create service user
echo -e "${BLUE}Creating service user...${NC}"
id -u srt-monitor >/dev/null 2>&1 || useradd -r -s /bin/false srt-monitor
chown -R srt-monitor:srt-monitor "$INSTALL_DIR"
chown -R srt-monitor:srt-monitor "$LOG_DIR"
chown -R srt-monitor:srt-monitor "$DATA_DIR"

# Configure firewall
echo -e "${BLUE}Configuring firewall...${NC}"
ufw allow 5000/tcp
ufw allow 9000/tcp  # Iperf default port
ufw --force enable

# Enable and start service
echo -e "${BLUE}Starting SRT Monitor service...${NC}"
systemctl daemon-reload
systemctl enable srt-monitor
systemctl start srt-monitor

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SRT Monitoring System Installed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Access the web interface at: ${BLUE}http://localhost:5000${NC}"
echo ""
echo -e "Service commands:"
echo -e "  sudo systemctl start srt-monitor"
echo -e "  sudo systemctl stop srt-monitor"
echo -e "  sudo systemctl restart srt-monitor"
echo -e "  sudo systemctl status srt-monitor"
echo ""
echo -e "View logs:"
echo -e "  sudo journalctl -u srt-monitor -f"
echo ""
