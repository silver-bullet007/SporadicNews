#!/bin/bash
# Sporadic News - Systemd Installation Script
# Run this script on your Linux server to install the systemd services

set -e  # Exit on error

echo "==================================================================="
echo "Sporadic News Bot - Systemd Installation"
echo "==================================================================="
echo ""

# Get the current directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "Project directory: $PROJECT_DIR"
echo ""

# Get current user
CURRENT_USER=$(whoami)
echo "Running as user: $CURRENT_USER"
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then 
    echo "ERROR: This script must be run with sudo"
    echo "Usage: sudo ./install_systemd.sh"
    exit 1
fi

# Get the actual user (not root)
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER="$SUDO_USER"
else
    ACTUAL_USER="$CURRENT_USER"
fi

echo "Installing services for user: $ACTUAL_USER"
echo ""

# Find Python path
PYTHON_PATH=$(which python3)
if [ -z "$PYTHON_PATH" ]; then
    echo "ERROR: python3 not found in PATH"
    exit 1
fi
echo "Python path: $PYTHON_PATH"
echo ""

# Create temporary directory for modified service files
TMP_DIR=$(mktemp -d)
echo "Creating temporary files in: $TMP_DIR"

# Function to update service file
update_service_file() {
    local src=$1
    local dest=$2
    
    sed -e "s|YOUR_USERNAME|$ACTUAL_USER|g" \
        -e "s|/path/to/sporadic_news|$PROJECT_DIR|g" \
        -e "s|/usr/bin/python3|$PYTHON_PATH|g" \
        "$src" > "$dest"
}

# Update and copy service files
echo ""
echo "Updating service files with your configuration..."
update_service_file "$PROJECT_DIR/systemd/producer.service" "$TMP_DIR/producer.service"
update_service_file "$PROJECT_DIR/systemd/producer.timer" "$TMP_DIR/producer.timer"
update_service_file "$PROJECT_DIR/systemd/consumer.service" "$TMP_DIR/consumer.service"
update_service_file "$PROJECT_DIR/systemd/consumer.timer" "$TMP_DIR/consumer.timer"

# Copy files to systemd directory
echo "Copying files to /etc/systemd/system/..."
cp "$TMP_DIR/producer.service" /etc/systemd/system/
cp "$TMP_DIR/producer.timer" /etc/systemd/system/
cp "$TMP_DIR/consumer.service" /etc/systemd/system/
cp "$TMP_DIR/consumer.timer" /etc/systemd/system/

# Set proper permissions
chmod 644 /etc/systemd/system/producer.service
chmod 644 /etc/systemd/system/producer.timer
chmod 644 /etc/systemd/system/consumer.service
chmod 644 /etc/systemd/system/consumer.timer

# Clean up
rm -rf "$TMP_DIR"

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo ""
echo "==================================================================="
echo "Installation Complete!"
echo "==================================================================="
echo ""
echo "Configuration:"
echo "  User: $ACTUAL_USER"
echo "  Project: $PROJECT_DIR"
echo "  Python: $PYTHON_PATH"
echo ""
echo "Next steps:"
echo ""
echo "1. Enable timers to start on boot:"
echo "   sudo systemctl enable producer.timer"
echo "   sudo systemctl enable consumer.timer"
echo ""
echo "2. Start timers:"
echo "   sudo systemctl start producer.timer"
echo "   sudo systemctl start consumer.timer"
echo ""
echo "3. Check status:"
echo "   systemctl status producer.timer"
echo "   systemctl status consumer.timer"
echo "   systemctl list-timers"
echo ""
echo "4. View logs:"
echo "   sudo journalctl -u producer.service -f"
echo "   sudo journalctl -u consumer.service -f"
echo ""
echo "5. Test manually:"
echo "   sudo systemctl start producer.service"
echo "   sudo systemctl start consumer.service"
echo ""
echo "==================================================================="
