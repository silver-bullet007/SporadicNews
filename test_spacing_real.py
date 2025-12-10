import sys
sys.path.insert(0, 'c:\\Users\\Win10\\Desktop\\scratch')

from scraper import MintScraper
from image_gen import ImageGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("=" * 60)
print("TESTING IMAGE SPACING FIX")
print("=" * 60)

# Scrape real news
scraper = MintScraper()
stories = scraper.get_hot_topics()

if not stories:
    print("No stories found!")
    sys.exit(1)

print(f"\nFound {len(stories)} stories. Using the first one for testing...")
story = stories[0]

print(f"\nStory: {story['headline'][:60]}...")

# Generate image
gen = ImageGenerator()
result = gen.get_image_for_story(story)

if result:
    print("\n" + "=" * 60)
    print("SUCCESS! Image generated with improved spacing")
    print("=" * 60)
    print(f"Location: {result}")
    print("\nImprovements made:")
    print("  - Removed scale(1.1) transform that caused cutoff")
    print("  - Added 60px vertical padding to body")
    print("  - Added 10px top margin to 'SPORADIC NEWS' brand")
    print("  - Increased summary bottom margin to 40px")
    print("  - Adjusted card width to 950px")
    print("  - Reduced card padding to 40px")
    print("\nPlease check the generated image to verify spacing!")
else:
    print("\nFailed to generate image")
