import logging
from processor import ContentProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_filter():
    logging.info("Starting Filter Test...")
    processor = ContentProcessor()
    
    # Case 1: Self-Contained Story
    headline_1 = "Rare Blue Supermoon Visible Tonight"
    summary_1 = "Stargazers are in for a treat tonight as a rare Blue Supermoon illuminates the sky. This phenomenon occurs when a second full moon appears in a single month while being at its closest point to Earth."
    
    logging.info(f"Testing Story 1: {headline_1}")
    result_1 = processor.is_story_self_contained(headline_1, summary_1)
    logging.info(f"Result 1 (Expected True): {result_1}")
    
    # Case 2: Clickbait / Not Self-Contained
    headline_2 = "You Won't Believe What This Actor Did!"
    summary_2 = "A famous Hollywood actor was spotted doing something shocking in public yesterday. Fans are going crazy over the photos."
    
    logging.info(f"Testing Story 2: {headline_2}")
    result_2 = processor.is_story_self_contained(headline_2, summary_2)
    logging.info(f"Result 2 (Expected False): {result_2}")

    # Case 3: Listicle (User Request)
    headline_3 = "Top 10 Foods for Weight Loss"
    summary_3 = "Here are the top 10 foods you should eat to lose weight fast. Number 7 will surprise you!"
    
    logging.info(f"Testing Story 3: {headline_3}")
    result_3 = processor.is_story_self_contained(headline_3, summary_3)
    logging.info(f"Result 3 (Expected False): {result_3}")

    # Case 4: Sports Result (Self-Contained)
    headline_4 = "India Wins Cricket World Cup"
    summary_4 = "India defeated Australia by 6 wickets in the final match to lift the World Cup trophy. Virat Kohli was named Player of the Match."
    
    logging.info(f"Testing Story 4: {headline_4}")
    result_4 = processor.is_story_self_contained(headline_4, summary_4)
    logging.info(f"Result 4 (Expected True): {result_4}")

    # Case 5: Complex Geopolitical Analysis (Not Self-Contained)
    headline_5 = "The Implications of New Trade Policy"
    summary_5 = "The new trade policy announced today has far-reaching consequences for the global economy. Experts argue it could shift alliances and impact currency values in unexpected ways."
    
    logging.info(f"Testing Story 5: {headline_5}")
    result_5 = processor.is_story_self_contained(headline_5, summary_5)
    logging.info(f"Result 5 (Expected False): {result_5}")

if __name__ == "__main__":
    test_filter()
