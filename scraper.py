import requests
from bs4 import BeautifulSoup, SoupStrainer
import json
import config
import logging
import hashlib
import os
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

SEEN_HASHES_FILE = "seen_hashes.txt"

class MintScraper:
    def __init__(self):
        self.url = config.TARGET_URL
        self.headers = {"User-Agent": config.USER_AGENT}
        self.seen_hashes = self.load_seen_hashes()

    def load_seen_hashes(self):
        """Loads seen hashes from file."""
        if not os.path.exists(SEEN_HASHES_FILE):
            return set()
        
        seen = set()
        try:
            with open(SEEN_HASHES_FILE, 'r') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if parts:
                        seen.add(parts[0]) # The hash is the first part
        except Exception as e:
            logging.error(f"Error loading seen hashes: {e}")
        return seen

    def save_hash(self, hash_val):
        """Saves a hash to the file with a timestamp."""
        try:
            with open(SEEN_HASHES_FILE, 'a') as f:
                f.write(f"{hash_val},{int(time.time())}\n")
        except Exception as e:
            logging.error(f"Error saving hash: {e}")

    def fetch_home_data(self):
        """Fetches the homepage and extracts the __NEXT_DATA__ JSON blob."""
        try:
            logging.info(f"Fetching {self.url}...")
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            
            # Optimization: Only parse the specific script tag we need
            strainer = SoupStrainer('script', id='__NEXT_DATA__')
            soup = BeautifulSoup(response.content, 'html.parser', parse_only=strainer)
            next_data_tag = soup.find('script', id='__NEXT_DATA__')
            
            if next_data_tag:
                return json.loads(next_data_tag.string)
            else:
                logging.error("Could not find __NEXT_DATA__ script tag.")
                return None
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return None

    def extract_image_info(self, story):
        """Extracts image URL and credit from a story object."""
        image_url = None
        image_credit = None
        
        # Try top-level image field (could be dict or string)
        img_data = story.get('image')
        if isinstance(img_data, dict):
            image_url = img_data.get('url')
            # sometimes credit is in metadata
            meta = img_data.get('imageMetaData', {})
            if meta:
                 image_credit = meta.get('credit')
        elif isinstance(img_data, str):
            image_url = img_data
            
        # Fallback to 'imageId' if URL not found (LiveMint constructs URLs from IDs)
        if not image_url and story.get('imageId'):
            # Example construction (needs verification, but often standard)
            # For now, we'll leave it as None if we can't find a direct URL
            pass

        # Try to find credit in other fields if not found
        if not image_credit:
            image_credit = story.get('imageCaption') # Sometimes credit is in caption
            
        return image_url, image_credit

    def get_hot_topics(self):
        """Parses the data to find trending/latest stories."""
        data = self.fetch_home_data()
        if not data:
            return []

        stories_list = []
        try:
            page_props = data.get('props', {}).get('pageProps', {})
            home_data = page_props.get('homeData', {})
            main_content = home_data.get('mainContent', [])
            
            # Iterate through sections to find stories
            for section in main_content:
                content = section.get('content', [])
                if isinstance(content, list):
                    for item in content:
                        # We only want items that look like stories
                        if 'headline' in item and 'url' in item:
                            img_url, img_credit = self.extract_image_info(item)
                            
                            # Clean HTML from headline
                            headline_raw = item.get('headline', '')
                            headline_clean = BeautifulSoup(headline_raw, 'html.parser').get_text()
                            
                            summary_raw = item.get('summary') or item.get('subHeadline') or ''
                            summary_clean = BeautifulSoup(summary_raw, 'html.parser').get_text()
                            
                            story = {
                                'headline': headline_clean,
                                'url': item.get('url'),
                                'summary': summary_clean,
                                'image_url': img_url,
                                'image_credit': img_credit,
                                'is_credited': bool(img_credit)
                            }
                            
                            # Clean up URL
                            if story['url'] and not story['url'].startswith('http'):
                                story['url'] = "https://www.livemint.com" + story['url']
                            
                            # User Request: Skip if no image
                            if not story['image_url']:
                                logging.debug(f"Skipping story without image: {story['headline']}")
                                continue

                            # Deduplication Check
                            story_hash = hashlib.md5(story['url'].encode('utf-8')).hexdigest()
                            if story_hash in self.seen_hashes:
                                logging.debug(f"Skipping seen story: {story['headline']}")
                                continue
                                
                            # Add to list and mark as seen
                            # Note: We don't save to file immediately here to avoid partial writes if we only want to save *processed* stories.
                            # BUT, the user asked to ensure we don't scrape news that has already been scraped.
                            # So we should probably mark it as seen. 
                            # However, usually we only want to mark it as seen if we actually *use* it.
                            # But the prompt says "ensure that you do not scrape news that has already been scraped".
                            # If I mark it as seen here, I might mark stories I never post.
                            # Let's assume for now we mark them as seen if we scrape them and they are valid candidates.
                            # Actually, it's better to only mark the one we *select* to post.
                            # But the user said "any new data scrape are not from that unique id".
                            # If I mark all scraped stories as seen, I will run out of stories very fast if I only post one at a time.
                            # Let's only mark the stories that are *returned* as candidates.
                            # Or better, let's just implement the mechanism and maybe only save the hash when we actually *select* the story in the main loop?
                            # The user said "ensure that you do not scrape news that has already been scraped".
                            # This implies filtering at the scraping level.
                            # If I filter everything I see, next time I run I won't see them.
                            # If I only post 1 story per run, I should probably only mark that 1 story as seen.
                            # BUT, the user's request is about the *scraping* process.
                            # "ensure that you do not scrape news that has already been scraped"
                            # This suggests that if I've seen it before, I shouldn't return it.
                            # I will add the hash to the story object so the caller can decide when to save it.
                            # OR, I can just save it here.
                            # If I save it here, I will consume 10-20 stories per run.
                            # If I run this every hour, I might exhaust the front page.
                            # I'll stick to the user's instruction: "ensure that you do not scrape news that has already been scraped".
                            # I will filter out seen ones. I will NOT save them here automatically unless I'm sure.
                            # Wait, "lets put the unique id list in a file".
                            # I'll add a method `mark_story_as_seen(story)` that the main script can call.
                            # But the user said "ensure that you do not scrape...".
                            # So `get_hot_topics` MUST filter.
                            # Who adds to the file?
                            # I'll add a `save_seen_story(story)` method and call it from `main.py` or `full_run_test.py` when a story is selected.
                            # This seems safer to avoid burning through content.
                            
                            story['hash'] = story_hash
                            stories_list.append(story)
                            
            logging.info(f"Extracted {len(stories_list)} stories.")
            return stories_list

        except Exception as e:
            logging.error(f"Error parsing stories: {e}")
            return []

    def mark_story_as_seen(self, story):
        """Marks a story as seen by saving its hash."""
        if 'hash' in story:
            self.seen_hashes.add(story['hash'])
            self.save_hash(story['hash'])

if __name__ == "__main__":
    # Test the scraper
    scraper = MintScraper()
    stories = scraper.get_hot_topics()
    
    print(f"Found {len(stories)} stories.")
    for i, s in enumerate(stories[:5]):
        try:
            print(f"\n{i+1}. {s['headline']}")
            print(f"   URL: {s['url']}")
            print(f"   Image: {s['image_url']}")
            print(f"   Credit: {s['image_credit']} (Credited: {s['is_credited']})")
        except UnicodeEncodeError:
            print(f"\n{i+1}. [Headline contains special characters]")

