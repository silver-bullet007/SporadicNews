import logging
from processor import ContentProcessor
from twitter_bot import TwitterBot
from image_gen import ImageGenerator
from scraper import MintScraper
import os
import sys
import time

# Fix Windows console encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_post():
    logging.info("Starting Full System Test Run...")
    
    # 1. Scrape Real Content
    scraper = MintScraper()
    stories = scraper.get_hot_topics()
    
    if not stories:
        logging.error("No stories found. Aborting test.")
        return

    processor = ContentProcessor()
    gen = ImageGenerator()
    
    selected_story = None
    
    # 2. Find first self-contained story
    for story in stories:
        logging.info(f"Checking story: {story['headline']}")
        
        # Filter Logic
        if processor.is_story_self_contained(story['headline'], story['summary']):
            logging.info(">>> Story APPROVED by Filter.")
            selected_story = story
            break
        else:
            logging.info(">>> Story REJECTED by Filter (Not self-contained).")
            
    if not selected_story:
        logging.warning("No self-contained stories found in the top batch. Using the first story as fallback for visual test.")
        selected_story = stories[0]

    logging.info(f"Selected Story: {selected_story['headline']}")

    # 3. Process Content (Generate Tweet Text)
    tweet_body = processor.process_content(selected_story['headline'], selected_story['summary'])
    
    logging.info("Generated Tweet Body:")
    print("-" * 20)
    print(tweet_body)
    print("-" * 20)

    # 4. Generate Image (HTML Card)
    logging.info("Generating News Card...")
    image_path = gen.get_image_for_story(selected_story)
    
    if image_path:
        logging.info(f"Generated Image Path: {image_path}")
        # Copy to a fixed name for the walkthrough
        import shutil
        dest_path = r"C:\Users\Win10\.gemini\antigravity\brain\f4b407a4-25fb-4e63-8096-1b36c0828b89\final_test_card.png"
        shutil.copy(image_path, dest_path)
        logging.info(f"Image copied to artifact: {dest_path}")
    else:
        logging.error("Failed to generate image.")

    # 5. Post to Twitter (SKIPPED as per user request, but logic is ready)
    logging.info("Skipping actual Twitter post as requested.")

if __name__ == "__main__":
    test_post()
