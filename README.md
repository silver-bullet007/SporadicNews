# Sporadic News Bot

A fully automated news aggregation and social media posting bot that scrapes trending news, generates professional news cards, and posts to Twitter.

## 🚀 Features

- **Automated Scraping**: Fetches trending news stories from LiveMint
- **AI-Powered Filtering**: Uses Gemini AI to select self-contained stories suitable for social media
- **Content Generation**: Rewrites headlines and generates engaging tweet text
- **Professional News Cards**: Creates beautiful HTML-based news cards with images
- **Deduplication**: Hash-based tracking ensures no duplicate posts
- **Producer-Consumer Architecture**: Separate generation and posting for reliability
- **Production Ready**: Includes systemd services and timers for Linux deployment

## 📋 Quick Start

### Prerequisites

- Python 3.7+
- API Keys:
  - Google Gemini API (for AI processing)
  - Twitter API v2 (for posting)

### Installation

```bash
# Clone or download the project
cd sporadic_news

# Install dependencies
pip install -r requirements.txt

# Configure API keys
nano config.py  # Add your API keys
```

### Test Run

```bash
# Generate a post
python main.py --once

# Check the queue
ls queue/

# Post to Twitter
python post_worker.py

# Check the archive
ls archive/
```

## 🏗️ Architecture

### Producer (`main.py`)
- Scrapes news from LiveMint
- Filters self-contained stories using AI
- Rewrites headlines for engagement
- Generates news card images (1080x1350px)
- Saves posts to `queue/` folder

### Consumer (`post_worker.py`)
- Monitors `queue/` folder
- Posts to Twitter with image and caption
- Archives successful posts
- Retries failed posts automatically

### Data Flow
```
LiveMint → Scraper → AI Filter → Headline Rewrite → Image Gen → Queue
                                                                    ↓
                                                         Twitter ← Consumer
```

## 📁 Project Structure

```
sporadic_news/
├── main.py              # Producer script
├── post_worker.py       # Consumer script
├── scraper.py           # News scraping logic
├── processor.py         # AI content processing
├── image_gen.py         # News card generation
├── twitter_bot.py       # Twitter API integration
├── config.py            # API keys and settings
├── requirements.txt     # Python dependencies
├── queue/               # Pending posts (auto-created)
├── archive/             # Posted content (auto-created)
├── images/              # Downloaded images
├── seen_hashes.txt      # Deduplication tracking
├── systemd/             # Linux deployment files
│   ├── producer.service
│   ├── producer.timer
│   ├── consumer.service
│   ├── consumer.timer
│   ├── install_systemd.sh
│   ├── manage.sh
│   └── README.md
├── README.md            # This file
├── DEPLOYMENT.md        # General deployment guide
└── LINUX_DEPLOYMENT.md  # Linux-specific deployment checklist
```

## 🐧 Linux Server Deployment

### Automated Installation

```bash
cd systemd
chmod +x install_systemd.sh manage.sh
sudo ./install_systemd.sh
```

### Enable and Start Services

```bash
# Enable services to start on boot
sudo systemctl enable producer.timer consumer.timer

# Start services
sudo systemctl start producer.timer consumer.timer

# Check status
./manage.sh status
```

### Management Commands

```bash
./manage.sh start          # Start services
./manage.sh stop           # Stop services
./manage.sh status         # View status
./manage.sh logs           # View logs
./manage.sh logs producer  # Follow producer logs
./manage.sh test-producer  # Run producer manually
```

**For detailed deployment instructions, see:**
- [`LINUX_DEPLOYMENT.md`](LINUX_DEPLOYMENT.md) - Complete Linux deployment checklist
- [`systemd/README.md`](systemd/README.md) - Systemd service documentation
- [`DEPLOYMENT.md`](DEPLOYMENT.md) - General deployment guide

## ⚙️ Configuration

### Timing

**Producer** (generates posts):
- Default: Every 2 hours
- Edit: `systemd/producer.timer`

**Consumer** (posts to Twitter):
- Default: Every 30 minutes
- Edit: `systemd/consumer.timer`

### API Quotas

The bot handles API rate limits gracefully:
- Falls back to original content if AI quota exceeded
- Logs warnings for monitoring
- Continues processing without interruption

## 📊 Monitoring

```bash
# Check service status
./manage.sh status

# View recent logs
./manage.sh logs

# Follow logs in real-time
./manage.sh logs producer
./manage.sh logs consumer

# Check queue
ls -lh queue/

# Check archive
ls -lh archive/

# List active timers
systemctl list-timers
```

## 🔧 Maintenance

### Weekly Tasks

```bash
# Optional: Clear seen hashes to allow re-scraping
rm seen_hashes.txt

# Clean up old images
rm -rf images/*

# Optional: Archive cleanup
rm -rf archive/*
```

### Troubleshooting

**No posts generated:**
```bash
./manage.sh test-producer
./manage.sh logs producer
```

**Posts not posting:**
```bash
./manage.sh test-consumer
./manage.sh logs consumer
```

**Check API quotas:**
- Gemini: https://ai.dev/usage
- Twitter: Check developer dashboard

## 📝 License

This project is for educational and personal use.

## 🤝 Contributing

Contributions welcome! Please test thoroughly before submitting PRs.

## ⚠️ Disclaimer

- Respect API rate limits and terms of service
- Ensure compliance with content licensing
- Monitor bot behavior regularly
- Use responsibly

---

**Twitter**: [@sporadicnews](https://twitter.com/sporadicnews)
