import logging
import sys
from scraper import MintScraper
from processor import ContentProcessor
from image_gen import ImageGenerator
from twitter_bot import TwitterBot

# Fix Windows console encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def full_run_test():
    """
    Runs the complete pipeline once and shows all output.
    Does not actually post to Twitter.
    """
    print("\n" + "="*80)
    print("FULL PIPELINE TEST RUN")
    print("="*80 + "\n")
    
    # Initialize modules
    logging.info("Initializing modules...")
    scraper = MintScraper()
    processor = ContentProcessor()
    image_gen = ImageGenerator()
    bot = TwitterBot()
    
    # Step 1: Scrape stories
    print("\n" + "-"*80)
    print("STEP 1: SCRAPING NEWS FROM LIVEMINT")
    print("-"*80)
    logging.info("Scraping for stories...")
    stories = scraper.get_hot_topics()
    
    if not stories:
        logging.error("No stories found. Aborting.")
        return
    
    logging.info(f"✓ Found {len(stories)} stories")
    print("\nStories found:")
    for i, story in enumerate(stories[:5], 1):  # Show first 5
        print(f"  {i}. {story['headline'][:80]}...")
    
    # Step 2: Filter for self-contained story
    print("\n" + "-"*80)
    print("STEP 2: FILTERING FOR SELF-CONTAINED STORIES")
    print("-"*80)
    
    selected_story = None
    for i, story in enumerate(stories, 1):
        logging.info(f"\n[{i}/{len(stories)}] Checking: {story['headline'][:60]}...")
        
        if processor.is_story_self_contained(story['headline'], story['summary']):
            logging.info("  ✓ Story APPROVED (self-contained)")
            selected_story = story
            break
        else:
            logging.info("  ✗ Story REJECTED (not self-contained)")
    
    if not selected_story:
        logging.warning("No self-contained stories found. Using first story as fallback.")
        selected_story = stories[0]
    
    # Mark as seen so we don't pick it up again
    scraper.mark_story_as_seen(selected_story)
    
    # Step 3: Display selected story
    print("\n" + "-"*80)
    print("STEP 3: SELECTED STORY")
    print("-"*80)
    print(f"\nHeadline: {selected_story['headline']}")
    print(f"\nSummary: {selected_story['summary'][:200]}...")
    print(f"\nImage URL: {selected_story.get('image_url', 'N/A')}")
    print(f"Image Credit: {selected_story.get('image_credit', 'N/A')}")
    
    # Step 3.5: Rewrite Headline
    print("\n" + "-"*80)
    print("STEP 3.5: REWRITING HEADLINE")
    print("-"*80)
    logging.info("Rewriting headline for better engagement...")
    original_headline = selected_story['headline']
    new_headline = processor.rewrite_headline(original_headline)
    selected_story['headline'] = new_headline # Update story with new headline
    
    print(f"Original: {original_headline}")
    print(f"New     : {new_headline}")

    # Step 4: Process content (generate tweet)
    print("\n" + "-"*80)
    print("STEP 4: GENERATING TWEET TEXT")
    print("-"*80)
    logging.info("Processing content...")
    tweet_body = processor.process_content(selected_story['headline'], selected_story['summary'])
    
    print("\n" + "="*80)
    print("GENERATED TWEET:")
    print("="*80)
    print(tweet_body)
    print("="*80)
    
    # Step 5: Generate image
    print("\n" + "-"*80)
    print("STEP 5: GENERATING NEWS CARD IMAGE")
    print("-"*80)
    logging.info("Generating news card...")
    image_path = image_gen.get_image_for_story(selected_story)
    
    if image_path:
        logging.info(f"✓ Image generated: {image_path}")
        print(f"\n✓ News card saved to: {image_path}")
    else:
        logging.error("✗ Failed to generate image")
        print("\n✗ Image generation failed (likely no image URL available)")
    
    # Step 6: Show what would be posted
    print("\n" + "-"*80)
    print("STEP 6: TWITTER POSTING (DRY RUN)")
    print("-"*80)
    
    if image_path:
        print("\n[DRY RUN] Would post to Twitter:")
        print(f"\nTweet Text:\n{tweet_body}")
        print(f"\nWith Image: {image_path}")
        print("\n✓ All steps completed successfully!")
    else:
        print("\n⚠ Cannot post without image. Would skip this story.")
    
    # Final summary
    print("\n" + "="*80)
    print("PIPELINE SUMMARY")
    print("="*80)
    print(f"Stories scraped: {len(stories)}")
    print(f"Selected story: {selected_story['headline'][:60]}...")
    print(f"Tweet generated: {'✓' if tweet_body else '✗'}")
    print(f"Image generated: {'✓' if image_path else '✗'}")
    print(f"Ready to post: {'✓' if (tweet_body and image_path) else '✗'}")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        full_run_test()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        logging.error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
