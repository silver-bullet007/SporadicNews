# Sporadic News Bot - Production Deployment Guide

## Architecture Overview

The bot uses a **producer-consumer architecture** with two independent scripts:

1. **Producer (`main.py`)**: Scrapes news, generates posts, saves to queue
2. **Consumer (`post_worker.py`)**: Reads queue, posts to Twitter, archives

## Quick Start

### Test the System

```bash
# 1. Generate a post (producer)
python main.py --once

# 2. Check the queue
dir queue  # Windows
ls queue   # Linux

# 3. Post to Twitter (consumer)
python post_worker.py

# 4. Verify archive
dir archive  # Windows
ls archive   # Linux
```

## Production Deployment

### Linux (systemd)

See `systemd/README.md` for detailed instructions.

**Quick Setup:**
```bash
cd systemd
# Edit service files: update YOUR_USERNAME and /path/to/sporadic_news
sudo cp *.service *.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable producer.timer consumer.timer
sudo systemctl start producer.timer consumer.timer
```

**Monitor:**
```bash
systemctl list-timers
sudo journalctl -u producer.service -f
sudo journalctl -u consumer.service -f
```

### Windows (Task Scheduler)

**Producer Task:**
1. Open Task Scheduler
2. Create Basic Task → Name: "Sporadic News Producer"
3. Trigger: Daily, repeat every 2 hours
4. Action: Start a program
   - Program: `python.exe` (or full path to Python)
   - Arguments: `main.py --once`
   - Start in: `C:\path\to\sporadic_news`

**Consumer Task:**
1. Create Basic Task → Name: "Sporadic News Consumer"
2. Trigger: Daily, repeat every 30 minutes
3. Action: Start a program
   - Program: `python.exe`
   - Arguments: `post_worker.py`
   - Start in: `C:\path\to\sporadic_news`

## Configuration

### Timing Adjustments

**Producer Frequency** (how often to generate posts):
- Recommended: Every 2-4 hours
- Adjust in timer file or Task Scheduler

**Consumer Frequency** (how often to check queue):
- Recommended: Every 15-30 minutes
- Adjust in timer file or Task Scheduler

### API Rate Limits

The bot handles Gemini API quota limits gracefully:
- Falls back to original content if AI fails
- Continues processing even with errors
- Check logs for quota warnings

## Directory Structure

```
sporadic_news/
├── main.py              # Producer script
├── post_worker.py       # Consumer script
├── scraper.py           # News scraping
├── processor.py         # AI content processing
├── image_gen.py         # News card generation
├── twitter_bot.py       # Twitter posting
├── config.py            # API keys and settings
├── queue/               # Pending posts (auto-created)
├── archive/             # Posted content (auto-created)
├── images/              # Downloaded images
├── seen_hashes.txt      # Deduplication tracking
└── systemd/             # Service/timer files
    ├── producer.service
    ├── producer.timer
    ├── consumer.service
    ├── consumer.timer
    └── README.md
```

## Maintenance

### Weekly Cleanup

```bash
# Clear seen hashes (allows re-scraping old stories)
rm seen_hashes.txt

# Clean up old images
rm -rf images/*

# Archive cleanup (optional)
rm -rf archive/*
```

### Monitoring

**Check Queue Status:**
```bash
ls -lh queue/  # Should have .png and .txt pairs
```

**Check Logs:**
```bash
# Linux
sudo journalctl -u producer.service --since today
sudo journalctl -u consumer.service --since today

# Windows
# Check Task Scheduler history
```

**Verify Posts:**
- Check Twitter: @sporadicnews
- Check archive folder for posted content

## Troubleshooting

### No Posts Generated
1. Check Gemini API quota: https://ai.dev/usage
2. Check scraper: `python scraper.py`
3. Review logs for errors

### Posts Not Posting to Twitter
1. Verify Twitter API credentials in `config.py`
2. Check consumer logs
3. Manually run: `python post_worker.py`

### Queue Backing Up
- Consumer may be failing to post
- Check Twitter API rate limits
- Increase consumer frequency

### Duplicate Posts
- Ensure `seen_hashes.txt` is not deleted between runs
- Check that producer marks stories as seen

## Security Notes

- **Never commit `config.py`** with API keys
- Keep `.gitignore` updated
- Rotate API keys periodically
- Monitor API usage dashboards

## Performance

**Resource Usage:**
- RAM: ~100-200 MB per run
- Disk: ~1-2 MB per generated post
- Network: Minimal (only API calls and image downloads)

**Execution Time:**
- Producer: 5-15 seconds per post
- Consumer: 2-5 seconds per post

## Support

For issues or questions:
1. Check logs first
2. Review this documentation
3. Test components individually
4. Verify API credentials and quotas
