import config
import logging
import os

try:
    import tweepy
except ImportError:
    tweepy = None

class TwitterBot:
    def __init__(self):
        if tweepy:
            # Authenticate to Twitter
            try:
                self.client = tweepy.Client(
                    bearer_token=config.TWITTER_BEARER_TOKEN,
                    consumer_key=config.TWITTER_API_KEY,
                    consumer_secret=config.TWITTER_API_SECRET,
                    access_token=config.TWITTER_ACCESS_TOKEN,
                    access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET
                )
                
                # For media upload, we need API v1.1 auth as well
                auth = tweepy.OAuth1UserHandler(
                    config.TWITTER_API_KEY,
                    config.TWITTER_API_SECRET,
                    config.TWITTER_ACCESS_TOKEN,
                    config.TWITTER_ACCESS_TOKEN_SECRET
                )
                self.api = tweepy.API(auth)
                
                logging.info("Twitter Bot initialized.")
            except Exception as e:
                logging.error(f"Error initializing Twitter Bot: {e}")
                self.client = None
                self.api = None
        else:
            logging.warning("Tweepy not installed. Bot running in MOCK mode.")
            self.client = None
            self.api = None

    def post_tweet(self, text, image_path=None):
        """Posts a tweet with optional image."""
        if not tweepy:
            logging.info(f"[MOCK] Would post tweet: {text}")
            if image_path:
                logging.info(f"[MOCK] With image: {image_path}")
            return True

        if not self.client or not self.api:
            logging.error("Twitter client not authenticated. Cannot post.")
            return False

        try:
            media_id = None
            if image_path and os.path.exists(image_path):
                logging.info(f"Uploading image: {image_path}")
                media = self.api.media_upload(image_path)
                media_id = media.media_id
            
            logging.info(f"Posting tweet: {text}")
            if media_id:
                response = self.client.create_tweet(text=text, media_ids=[media_id])
            else:
                response = self.client.create_tweet(text=text)
                
            logging.info(f"Tweet posted successfully! ID: {response.data['id']}")
            return True
            
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
            return False

if __name__ == "__main__":
    # Test (This will fail without real keys, but verifies structure)
    bot = TwitterBot()
    bot.post_tweet("Hello World! This is a test from my automated bot. #Test")
