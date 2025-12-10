import time
import logging
import os
import argparse
import shutil
import uuid
from datetime import datetime

import config
from scraper import MintScraper
from processor import ContentProcessor
from image_gen import ImageGenerator
from twitter_bot import TwitterBot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Directories for queued posts and archived posts
QUEUE_DIR = "queue"
ARCHIVE_DIR = "archive"
MAX_POSTS_PER_DAY = 10

def ensure_dirs():
    for d in (QUEUE_DIR, ARCHIVE_DIR):
        if not os.path.exists(d):
            os.makedirs(d)

ensure_dirs()

def get_today_date_str():
    """Returns today's date in YYYYMMDD format."""
    return datetime.now().strftime("%Y%m%d")

def count_todays_posts():
    """Count PNG files in the queue folder with today's date."""
    today = get_today_date_str()
    count = 0
    
    # Count only in queue (not archive)
    if os.path.exists(QUEUE_DIR):
        for f in os.listdir(QUEUE_DIR):
            if f.startswith(f"post_{today}_") and f.endswith('.png'):
                count += 1
    
    return count

def save_to_queue(image_path: str, tweet_body: str):
    """Copy the generated image and write the tweet caption to the queue folder.
    Each post gets a unique base name with date prefix so we can track daily limits.
    """
    try:
        today = get_today_date_str()
        unique_id = uuid.uuid4().hex[:12]  # Shorter ID
        base_name = f"post_{today}_{unique_id}"
        
        dest_image = os.path.join(QUEUE_DIR, f"{base_name}.png")
        shutil.copy2(image_path, dest_image)
        caption_path = os.path.join(QUEUE_DIR, f"{base_name}.txt")
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(tweet_body)
        logging.info(f"Saved post to queue: {dest_image} & {caption_path}")
    except Exception as e:
        logging.error(f"Failed to save post to queue: {e}")

def main(dry_run=False, run_once=False):
    logging.info("Starting Sporadic News Bot (producer)...")
    
    scraper = MintScraper()
    processor = ContentProcessor()
    image_gen = ImageGenerator()
    # TwitterBot is not used here; posting is delegated to the consumer script.

    while True:
        try:
            # Check daily limit at the start of each cycle
            todays_count = count_todays_posts()
            logging.info(f"Posts created today: {todays_count}/{MAX_POSTS_PER_DAY}")
            
            if todays_count >= MAX_POSTS_PER_DAY:
                logging.info(f"Daily limit of {MAX_POSTS_PER_DAY} posts reached. Skipping execution.")
                if run_once:
                    break
                # Sleep for a longer period since we've hit the limit
                logging.info("Sleeping for 1 hour before checking again...")
                time.sleep(3600)
                continue
            
            logging.info("Scraping for new stories...")
            stories = scraper.get_hot_topics()

            if not stories:
                logging.info("No new stories found. Sleeping for 15 minutes.")
                if run_once:
                    break
                time.sleep(900)
                continue

            posted_any = False
            for story in stories:
                logging.info(f"Evaluating story: {story['headline']}")

                # Filter self‑contained stories
                if not processor.is_story_self_contained(story['headline'], story['summary']):
                    logging.info("Skipping story: not self‑contained.")
                    scraper.mark_story_as_seen(story)
                    continue

                # Rewrite headline for engagement
                story['headline'] = processor.rewrite_headline(story['headline'])

                # Generate image (news card)
                image_path = image_gen.get_image_for_story(story)
                if not image_path:
                    logging.warning("Skipping story due to image generation failure.")
                    scraper.mark_story_as_seen(story)
                    continue

                # Build tweet text
                tweet_body = processor.process_content(story['headline'], story['summary'])

                # Save to queue (or dry‑run output)
                if dry_run:
                    logging.info("[DRY RUN] Would save to queue instead of posting.")
                save_to_queue(image_path, tweet_body)
                scraper.mark_story_as_seen(story)
                posted_any = True
                break  # Only queue one post per run

            if posted_any:
                logging.info(f"Sleeping for {config.LOOP_SLEEP_SECONDS} seconds before next cycle.")
                if run_once:
                    break
                time.sleep(config.LOOP_SLEEP_SECONDS)
            else:
                logging.info("No suitable stories this cycle. Sleeping for 15 minutes.")
                if run_once:
                    break
                time.sleep(900)

            # Force garbage collection
            import gc
            gc.collect()

        except KeyboardInterrupt:
            logging.info("Producer stopped by user.")
            break
        except Exception as e:
            logging.error(f"Unexpected error in producer loop: {e}")
            if run_once:
                break
            time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sporadic News Producer")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing to queue (just log actions)")
    parser.add_argument("--once", action="store_true", help="Execute a single production cycle and exit")
    args = parser.parse_args()
    main(dry_run=args.dry_run, run_once=args.once)
