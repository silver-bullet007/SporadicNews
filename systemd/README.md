# Sporadic News - Systemd Service & Timer Setup

This folder contains systemd service and timer files for automating the Sporadic News bot on Linux systems.

## Files Overview

### Producer (Content Generation)
- **producer.service** - Service definition for generating news posts
- **producer.timer** - Timer to run producer every 2 hours

### Consumer (Twitter Posting)
- **consumer.service** - Service definition for posting queued content to Twitter
- **consumer.timer** - Timer to check queue and post every 30 minutes

### Helper Scripts
- **install_systemd.sh** - Automated installation script
- **manage.sh** - Service management helper

## Quick Installation (Recommended)

### Automated Installation

```bash
cd systemd
chmod +x install_systemd.sh manage.sh
sudo ./install_systemd.sh
```

This script will:
- Automatically detect your username and project path
- Update all service files with correct paths
- Copy files to `/etc/systemd/system/`
- Reload systemd daemon

After installation:
```bash
# Enable and start services
sudo systemctl enable producer.timer consumer.timer
sudo systemctl start producer.timer consumer.timer

# Check status
./manage.sh status
```

### Using the Management Script

```bash
# Start services
./manage.sh start

# Stop services
./manage.sh stop

# View status
./manage.sh status

# View logs
./manage.sh logs
./manage.sh logs producer  # Follow producer logs
./manage.sh logs consumer  # Follow consumer logs

# Test manually
./manage.sh test-producer
./manage.sh test-consumer

# Enable on boot
./manage.sh enable

# Uninstall
./manage.sh uninstall
```

## Manual Installation

```bash
# Copy service files
sudo cp producer.service /etc/systemd/system/
sudo cp producer.timer /etc/systemd/system/
sudo cp consumer.service /etc/systemd/system/
sudo cp consumer.timer /etc/systemd/system/

# Reload systemd to recognize new files
sudo systemctl daemon-reload
```

### 3. Enable and Start Services

```bash
# Enable timers to start on boot
sudo systemctl enable producer.timer
sudo systemctl enable consumer.timer

# Start timers immediately
sudo systemctl start producer.timer
sudo systemctl start consumer.timer
```

### 4. Verify Status

```bash
# Check timer status
sudo systemctl status producer.timer
sudo systemctl status consumer.timer

# List all active timers
systemctl list-timers

# View logs
sudo journalctl -u producer.service -f
sudo journalctl -u consumer.service -f
```

## Customizing Schedule

### Producer Timer (producer.timer)
Edit the `OnCalendar` line to change frequency:
- Every 2 hours: `OnCalendar=*-*-* 00/2:00:00`
- Every 4 hours: `OnCalendar=*-*-* 00/4:00:00`
- Every hour: `OnCalendar=hourly`
- Specific times: `OnCalendar=*-*-* 08,12,16,20:00:00` (8am, 12pm, 4pm, 8pm)

### Consumer Timer (consumer.timer)
Edit the `OnCalendar` line to change frequency:
- Every 30 minutes: `OnCalendar=*-*-* *:00/30:00`
- Every 15 minutes: `OnCalendar=*-*-* *:00/15:00`
- Every hour: `OnCalendar=hourly`

After editing, reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart producer.timer
sudo systemctl restart consumer.timer
```

## Manual Execution

Run services manually for testing:
```bash
# Generate a post manually
sudo systemctl start producer.service

# Process queue manually
sudo systemctl start consumer.service
```

## Troubleshooting

### Check Service Logs
```bash
# Recent logs
sudo journalctl -u producer.service -n 50
sudo journalctl -u consumer.service -n 50

# Follow logs in real-time
sudo journalctl -u producer.service -f
```

### Disable Services
```bash
sudo systemctl stop producer.timer
sudo systemctl stop consumer.timer
sudo systemctl disable producer.timer
sudo systemctl disable consumer.timer
```

## Notes

- The producer runs with `Type=oneshot` and `--once` flag to generate one post per execution
- The consumer can run as a continuous service (`Type=simple`) or be triggered by timer
- Logs are sent to systemd journal (view with `journalctl`)
- Timers persist across reboots with `Persistent=true`
