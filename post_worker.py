import os
import time
import logging
import shutil
import config
from twitter_bot import TwitterBot

# Directories (must match producer)
QUEUE_DIR = "queue"
ARCHIVE_DIR = "archive"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def ensure_dirs():
    for d in (QUEUE_DIR, ARCHIVE_DIR):
        if not os.path.exists(d):
            os.makedirs(d)

ensure_dirs()

def process_queue():
    """Process all items in queue once and exit."""
    bot = TwitterBot()
    try:
        # Find all .png files in queue
        png_files = [f for f in os.listdir(QUEUE_DIR) if f.lower().endswith('.png')]
        if not png_files:
            logging.info("Queue is empty.")
            return
        
        for png in png_files:
            base = os.path.splitext(png)[0]
            txt_path = os.path.join(QUEUE_DIR, f"{base}.txt")
            png_path = os.path.join(QUEUE_DIR, png)
            
            if not os.path.isfile(txt_path):
                logging.warning(f"Caption file missing for {png}, skipping.")
                continue
            
            # Read caption
            with open(txt_path, 'r', encoding='utf-8') as f:
                tweet_body = f.read()
            
            # Post to Twitter
            logging.info(f"Posting {png}...")
            success = bot.post_tweet(tweet_body, png_path)
            
            if success:
                # Move both files to archive
                archive_png = os.path.join(ARCHIVE_DIR, png)
                archive_txt = os.path.join(ARCHIVE_DIR, f"{base}.txt")
                shutil.move(png_path, archive_png)
                shutil.move(txt_path, archive_txt)
                logging.info(f"Posted and archived {png} and its caption.")
                # Only post one item per run
                break
            else:
                logging.error(f"Failed to post {png}. Will retry later.")
                # Do not remove files; will retry on next timer trigger
                
    except Exception as e:
        logging.error(f"Unexpected error in consumer: {e}")

if __name__ == "__main__":
    process_queue()
