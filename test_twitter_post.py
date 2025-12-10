import logging
import sys
from twitter_bot import TwitterBot
from image_gen import ImageGenerator

# Fix Windows console encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_twitter_posting():
    """
    Test the Twitter posting functionality with a sample post.
    This simulates what happens after content is generated.
    """
    logging.info("=== Testing Twitter Posting Functionality ===")
    
    # Sample data (simulating what would come from processor)
    sample_tweet_text = """𝐓𝐞𝐬𝐭 𝐏𝐨𝐬𝐭 𝐟𝐫𝐨𝐦 𝐍𝐞𝐰𝐬 𝐁𝐨𝐭

🚨 This is a test post to verify Twitter API integration. The bot is checking if it can successfully post content with images to Twitter/X platform.

#Test #NewsBot #Automation #Twitter #API #Integration #Tech #Update"""
    
    # Step 1: Create a local test image instead of downloading
    logging.info("Step 1: Creating local test image...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        # Create images directory if it doesn't exist
        os.makedirs("images", exist_ok=True)
        
        # Create a simple test image
        img = Image.new('RGB', (1600, 900), color=(26, 31, 53))
        draw = ImageDraw.Draw(img)
        
        # Add some text to the image
        try:
            # Try to use a default font
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
        
        # Draw text in the center
        text = "TEST NEWS IMAGE"
        # Get text bbox for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((1600 - text_width) // 2, (900 - text_height) // 2)
        draw.text(position, text, fill=(255, 255, 255), font=font)
        
        # Save the image
        test_image_path = "images/test_background.jpg"
        img.save(test_image_path)
        logging.info(f"✓ Created test image: {test_image_path}")
        
    except Exception as e:
        logging.error(f"Failed to create test image: {e}")
        return False
    
    # Step 2: Generate news card using the test image
    logging.info("\nStep 2: Generating news card...")
    gen = ImageGenerator()
    
    # Manually create the news card using the local test image
    image_path = gen.create_news_card(
        headline='Test News Post',
        background_path=test_image_path,
        credit='Test Credit',
        summary='This is a test post to verify the Twitter posting functionality.'
    )
    
    if not image_path:
        logging.error("Failed to generate news card. Aborting.")
        return False
    
    logging.info(f"✓ News card created: {image_path}")
    
    # Step 3: Initialize Twitter Bot
    logging.info("\nStep 3: Initializing Twitter Bot...")
    bot = TwitterBot()
    
    # Check if bot is in mock mode or real mode
    if not bot.client:
        logging.warning("⚠ Twitter Bot is in MOCK mode (tweepy not installed or credentials invalid)")
        logging.info("The bot will simulate posting without actually posting to Twitter.")
    else:
        logging.info("✓ Twitter Bot initialized with real credentials")
    
    # Step 4: Attempt to post
    logging.info("\nStep 4: Attempting to post to Twitter...")
    logging.info(f"Tweet text:\n{'-'*50}\n{sample_tweet_text}\n{'-'*50}")
    logging.info(f"Image: {image_path}")
    
    try:
        success = bot.post_tweet(sample_tweet_text, image_path)
        
        if success:
            logging.info("\n✓✓✓ SUCCESS! Tweet posted successfully!")
            return True
        else:
            logging.error("\n✗✗✗ FAILED! Tweet posting failed.")
            logging.error("Check the error messages above for details.")
            return False
            
    except Exception as e:
        logging.error(f"\n✗✗✗ EXCEPTION occurred during posting: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logging.info("Starting Twitter Posting Test...\n")
    result = test_twitter_posting()
    
    if result:
        logging.info("\n" + "="*60)
        logging.info("TEST PASSED: Twitter posting is working correctly!")
        logging.info("="*60)
    else:
        logging.info("\n" + "="*60)
        logging.info("TEST FAILED: There are issues with Twitter posting.")
        logging.info("Review the error messages above to diagnose the problem.")
        logging.info("="*60)
