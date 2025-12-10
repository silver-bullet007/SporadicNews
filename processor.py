import config
import logging
import openai
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class ContentProcessor:
    def __init__(self):
        self.provider = None
        if hasattr(config, 'OPENAI_API_KEY') and config.OPENAI_API_KEY and "YOUR_" not in config.OPENAI_API_KEY:
            self.provider = "openai"
            openai.api_key = config.OPENAI_API_KEY
            logging.info("ContentProcessor using OpenAI.")
        elif hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY and "YOUR_" not in config.GEMINI_API_KEY:
            if genai:
                self.provider = "gemini"
                genai.configure(api_key=config.GEMINI_API_KEY)
                logging.info("ContentProcessor using Gemini.")
            else:
                logging.warning("Gemini API key found but module not installed. Using MOCK mode.")
        else:
            logging.warning("No valid LLM API key found. Using MOCK mode.")

    def process_content(self, headline, summary):
        """
        Rewrites the news content for Twitter using an LLM.
        """
        prompt = f"""
        You are a social media manager for a news bot.
        Rewrite the following news story into a short, engaging caption.
        
        Rules:
        1. Do NOT use the prefix "Breaking:".
        2. **Headline**: Write the headline in **Unicode Bold** (e.g. 𝐇𝐞𝐚𝐝𝐥𝐢𝐧𝐞).
        3. **Summary**: Write a clear, informative summary (2-3 sentences) explaining the "Who, What, Why". 
           - Use **Emojis** (like siren, chart, flag) to make it visually appealing.
           - Do NOT end with "..." or a cliffhanger. Finish the thought completely.
        4. Add 2 newlines.
        5. **Hashtags**: Add 8-10 relevant trending hashtags (e.g. #News #India #Viral #StockMarket #Latest).
        
        Headline: {headline}
        Summary: {summary}
        
        Output format:
        <Unicode Bold Headline>
        <Complete Summary with Emojis>
        
        <Hashtags>
        """
        
        
        logging.info(f"Processing content for: {headline}")
        
        response_text = ""
        
        if self.provider == "openai":
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content.strip()
            except Exception as e:
                logging.error(f"OpenAI Error: {e}")
                
        elif self.provider == "gemini":
            try:
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content(prompt)
                response_text = response.text.strip()
            except Exception as e:
                logging.error(f"Gemini Error: {e}")
        
        if not response_text:
             # Mock response fallback - try to be smarter
            fallback_summary = summary[:250]
            last_period = fallback_summary.rfind('.')
            if last_period > 20: # Ensure we have at least some text
                fallback_summary = fallback_summary[:last_period+1]
            
            # Helper to bold text (Mathematical Alphanumeric Symbols)
            def to_bold(text):
                normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
                bold = "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"
                trans = str.maketrans(normal, bold)
                return text.translate(trans)

            bold_headline = to_bold(headline)
                
            return f"{bold_headline}\n\n\U0001F6A8 {fallback_summary}\n\n#News #Trending #India #Viral #Latest #Update #DailyNews #World"

        # Post-processing: Force remove "Breaking" if LLM ignores instruction
        cleaned_text = response_text.strip()
        if cleaned_text.lower().startswith("breaking:"):
            cleaned_text = cleaned_text[9:].strip()
        elif cleaned_text.lower().startswith("breaking"):
            cleaned_text = cleaned_text[8:].strip()
            
        return cleaned_text

    def rewrite_headline(self, headline):
        """
        Rewrites the headline to be catchy, punchy, and suitable for a card.
        Removes "10 key highlights", "Live updates", etc.
        """
        prompt = f"""
        You are a senior editor. Rewrite the following news headline to be catchy, punchy, and attention-grabbing for a social media graphic.
        
        Rules:
        1. **Remove Fluff**: STRICTLY REMOVE phrases like "10 key highlights", "Live updates", "Full list", "Here's why", "Check details".
        2. **Keep Facts**: Retain important numbers (e.g. "500 points", "₹2 lakh crore") and key entities.
        3. **Style**: Make it sound authoritative but engaging. Use active voice.
        4. **Length**: Keep it under 15 words.
        5. **Formatting**: Plain text only. No bolding, no "Breaking:", no emojis.
        
        Original Headline: {headline}
        
        New Headline:
        """
        
        logging.info(f"Rewriting headline: {headline}")
        
        response_text = ""
        
        if self.provider == "openai":
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content.strip()
            except Exception as e:
                logging.error(f"OpenAI Error in headline rewrite: {e}")
                
        elif self.provider == "gemini":
            try:
                model = genai.GenerativeModel('gemini-flash-latest')
                response = model.generate_content(prompt)
                response_text = response.text.strip()
            except Exception as e:
                logging.error(f"Gemini Error in headline rewrite: {e}")
        
        # Fallback if LLM fails or returns empty
        if not response_text:
            # Basic cleanup fallback
            cleaned = headline.split(" — ")[0] # Remove trailing part often used for "10 highlights"
            cleaned = cleaned.split(" | ")[0]
            return cleaned

        # Cleanup quotes if LLM adds them
        return response_text.strip('"').strip("'")

    def is_story_self_contained(self, headline, summary):
        """
        Determines if a story is self-contained (does not require clicking a link) using LLM.
        Returns True if self-contained, False otherwise.
        """
        prompt = f"""
        Analyze the following news story. Does the summary provide a complete picture of the event such that a reader does NOT need to read the full article to understand the core message?
        
        **Rules for "NO" (Not Self-Contained):**
        1. **Listicles/Guides**: Stories like "Top 10...", "5 Ways to...", "Best foods for..." are NOT self-contained. They require the full list.
        2. **Clickbait**: Headlines like "You won't believe...", "This is why..." are NOT self-contained.
        3. **Complex Analysis**: Deep dives or opinion pieces that need full context.
        
        Headline: {headline}
        Summary: {summary}
        
        Reply with ONLY 'YES' or 'NO'.
        """
        
        logging.info(f"Analyzing if story is self-contained: {headline}")
        
        response_text = ""
        
        if self.provider == "openai":
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content.strip().upper()
            except Exception as e:
                logging.error(f"OpenAI Error in filtering: {e}")
                return True # Default to True on error to avoid over-filtering
                
        elif self.provider == "gemini":
            try:
                if genai:
                    model = genai.GenerativeModel('gemini-flash-latest')
                    response = model.generate_content(prompt)
                    response_text = response.text.strip().upper()
                else:
                    return True # Mock mode
            except Exception as e:
                logging.error(f"Gemini Error in filtering: {e}")
                return True
        else:
            return True # Mock mode
            
        logging.info(f"Filter Result: {response_text}")
        return "YES" in response_text

if __name__ == "__main__":
    processor = ContentProcessor()
    tweet = processor.process_content("Stock Market Hits Record High", "The S&P 500 reached a new all-time high today driven by tech stocks.")
    print(f"Generated Tweet: {tweet}")
