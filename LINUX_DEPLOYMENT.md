# Linux Server Deployment Checklist

## Pre-Deployment

### 1. Server Requirements
- [ ] Linux server with systemd (Ubuntu 18.04+, Debian 10+, CentOS 7+, etc.)
- [ ] Python 3.7 or higher installed
- [ ] Git installed (for cloning the repository)
- [ ] Sudo access

### 2. Install Dependencies

```bash
# Update package list
sudo apt update  # Ubuntu/Debian
sudo yum update  # CentOS/RHEL

# Install Python and pip
sudo apt install python3 python3-pip  # Ubuntu/Debian
sudo yum install python3 python3-pip  # CentOS/RHEL

# Install required Python packages
cd /path/to/sporadic_news
pip3 install -r requirements.txt
```

### 3. Configure API Keys

Edit `config.py` with your credentials:
```bash
nano config.py
```

Required:
- [ ] `GEMINI_API_KEY` - Google Gemini API key
- [ ] `TWITTER_API_KEY` - Twitter API key
- [ ] `TWITTER_API_SECRET` - Twitter API secret
- [ ] `TWITTER_ACCESS_TOKEN` - Twitter access token
- [ ] `TWITTER_ACCESS_SECRET` - Twitter access token secret

## Deployment Steps

### 1. Upload Project to Server

```bash
# Option A: Clone from Git
git clone <your-repo-url> /home/yourusername/sporadic_news
cd /home/yourusername/sporadic_news

# Option B: Upload via SCP
scp -r /local/path/sporadic_news user@server:/home/yourusername/
```

### 2. Test Components

```bash
cd /home/yourusername/sporadic_news

# Test scraper
python3 scraper.py

# Test producer (generate one post)
python3 main.py --once

# Check queue
ls -lh queue/

# Test consumer (post to Twitter)
python3 post_worker.py

# Check archive
ls -lh archive/
```

### 3. Install Systemd Services

```bash
cd systemd
chmod +x install_systemd.sh manage.sh
sudo ./install_systemd.sh
```

### 4. Enable and Start Services

```bash
# Enable services to start on boot
sudo systemctl enable producer.timer
sudo systemctl enable consumer.timer

# Start services
sudo systemctl start producer.timer
sudo systemctl start consumer.timer

# Verify status
./manage.sh status
```

### 5. Verify Operation

```bash
# Check timers are active
systemctl list-timers

# View recent logs
./manage.sh logs

# Follow logs in real-time (Ctrl+C to exit)
./manage.sh logs producer
./manage.sh logs consumer
```

## Post-Deployment

### Monitoring

```bash
# Check service status
./manage.sh status

# View logs
./manage.sh logs

# Check queue
ls -lh queue/

# Check archive
ls -lh archive/

# Monitor Twitter account
# Visit: https://twitter.com/sporadicnews
```

### Maintenance Schedule

**Daily:**
- [ ] Check logs for errors: `./manage.sh logs`
- [ ] Verify posts on Twitter

**Weekly:**
- [ ] Review `seen_hashes.txt` size
- [ ] Clean up old images: `rm -rf images/*`
- [ ] Optional: Clear archive: `rm -rf archive/*`

**Monthly:**
- [ ] Review API usage quotas
- [ ] Check disk space: `df -h`
- [ ] Update dependencies: `pip3 install -r requirements.txt --upgrade`

### Troubleshooting

**Services not running:**
```bash
./manage.sh status
sudo journalctl -u producer.service -n 50
sudo journalctl -u consumer.service -n 50
```

**No posts generated:**
```bash
# Test manually
./manage.sh test-producer
./manage.sh logs producer
```

**Posts not posting:**
```bash
# Test manually
./manage.sh test-consumer
./manage.sh logs consumer
```

**API quota exceeded:**
- Check Gemini quota: https://ai.dev/usage
- Check Twitter rate limits
- Adjust timer frequency if needed

### Adjusting Schedules

Edit timer files and reload:
```bash
# Edit timers
sudo nano /etc/systemd/system/producer.timer
sudo nano /etc/systemd/system/consumer.timer

# Reload and restart
sudo systemctl daemon-reload
./manage.sh restart
```

## Security Checklist

- [ ] `config.py` has restricted permissions: `chmod 600 config.py`
- [ ] API keys are not in version control
- [ ] Server has firewall enabled
- [ ] SSH key authentication enabled
- [ ] Regular security updates applied

## Backup

```bash
# Backup configuration
cp config.py config.py.backup

# Backup seen hashes
cp seen_hashes.txt seen_hashes.txt.backup

# Backup archive (optional)
tar -czf archive_backup_$(date +%Y%m%d).tar.gz archive/
```

## Uninstall

```bash
# Stop and remove services
cd /home/yourusername/sporadic_news/systemd
./manage.sh uninstall

# Remove project (optional)
cd ~
rm -rf sporadic_news
```

## Support Commands

```bash
# Service management
./manage.sh start|stop|restart|status|enable|disable

# View logs
./manage.sh logs [producer|consumer]

# Manual execution
./manage.sh test-producer
./manage.sh test-consumer

# System info
systemctl list-timers
journalctl -u producer.service --since today
journalctl -u consumer.service --since today
```

## Success Criteria

- [ ] Both timers show as "active" in `systemctl list-timers`
- [ ] Producer generates posts in `queue/` folder
- [ ] Consumer posts to Twitter and moves files to `archive/`
- [ ] No errors in logs
- [ ] Posts appear on @sporadicnews Twitter account
- [ ] Services restart automatically after server reboot
