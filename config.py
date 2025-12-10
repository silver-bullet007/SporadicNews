# Configuration Settings

# Twitter/X API Credentials
# Get these from https://developer.twitter.com/en/portal/dashboard
TWITTER_API_KEY = "C8PRp9nguaZjThlWubzxje2f4"
TWITTER_API_SECRET = "cIk15JYFuB7eBOpKkKLKPAm7SZ59kerSU0Akuu0PH7RLLDEXPx"
TWITTER_ACCESS_TOKEN = "1429331059234074629-q6WuW5Si6NUrHF8xZBfPwSdxNUpNAr"
TWITTER_ACCESS_TOKEN_SECRET = "1LSuJBSHQ20rnn5n7VL4iBN7F18g8fDRnQKg49pA3wdPw"
TWITTER_BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAALTA5gEAAAAAMeA7GvvZVS0Fs2%2F3zHsE9fpFk28%3DNTna3p5JJQMKZgwMr93g4mToiZXbknbl7pRZ6YVABaMSMxV6IF"

# LLM Credentials (choose one)
# Google Gemini
GEMINI_API_KEY = "AIzaSyD1AcXDm-P6I1_k2TNlQEKYwh9B8TX_W44"

# Image Generation Credentials
# (Usually same as OpenAI if using DALL-E)
IMAGE_GEN_API_KEY = "AIzaSyD1AcXDm-P6I1_k2TNlQEKYwh9B8TX_W44"

# Bot Settings
POSTS_PER_DAY = 10
# Calculate sleep time in seconds: 24 hours * 60 mins * 60 secs / posts
LOOP_SLEEP_SECONDS = (24 * 60 * 60) / POSTS_PER_DAY 

# Scraper Settings
TARGET_URL = "https://www.livemint.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
