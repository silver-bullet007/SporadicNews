import requests
import os
import logging
import config
import time
from html2image import Html2Image
from PIL import Image, ImageOps

class ImageGenerator:
    def __init__(self):
        self.image_dir = "images"
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
            
        self.hti = Html2Image(output_path=self.image_dir)
        # Configure for better quality and size
        self.hti.size = (1080, 1350) 

    def download_image(self, url, filename):
        """Downloads an image from a URL."""
        try:
            logging.info(f"Downloading image from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            filepath = os.path.join(self.image_dir, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Post-process image to fit frame
            self.process_image(filepath)
            
            return filepath
        except Exception as e:
            logging.error(f"Error downloading image: {e}")
            return None

    def process_image(self, filepath):
        """Resizes and crops image to fit the card frame (800x500)."""
        try:
            target_size = (800, 500)
            with Image.open(filepath) as img:
                # Convert to RGB if necessary (e.g. for PNGs with transparency)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Smart crop/resize
                # centering=(0.5, 0.2) biases towards the top (good for faces)
                processed_img = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.2))
                
                processed_img.save(filepath, quality=95)
                logging.info(f"Processed image to {target_size}")
        except Exception as e:
            logging.error(f"Error processing image: {e}")

    def get_html_template(self, headline, summary, image_path, credit_html, date_str):
        # Convert local image path to absolute file URI for HTML
        abs_image_path = os.path.abspath(image_path).replace("\\", "/")
        image_src = f"file:///{abs_image_path}"
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Social News Card</title>
  <style>
    :root {{
      --bg-gradient: radial-gradient(circle at top left, #1a1f35, #0f1419);
      --card-bg: #0b1020;
      --card-gradient: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
      --accent: #ffce00;
      --accent-soft: rgba(255, 206, 0, 0.2);
      --text-main: #ffffff;
      --text-muted: #c7c9d9;
      --border-subtle: rgba(255,255,255,0.08);
      --shadow-strong: 0 24px 60px rgba(0,0,0,0.5);
      --radius-lg: 28px;
      --radius-md: 18px;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      width: 1080px;
      height: 1350px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: transparent;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      overflow: hidden;
      padding: 60px 0; /* Add vertical padding for breathing room */
    }}

    .news-card {{
      position: relative;
      width: 950px; /* Adjusted width to better fit canvas */
      background: var(--card-bg);
      background-image: var(--card-gradient);
      border-radius: var(--radius-lg);
      padding: 40px; /* Reduced padding to fit more content */
      color: var(--text-main);
      box-shadow: var(--shadow-strong);
      overflow: hidden;
      border: 1px solid rgba(255,255,255,0.06);
      /* Removed scale transform to prevent cutoff */
    }}

    /* Decorative shapes */
    .news-card::before,
    .news-card::after {{
      content: "";
      position: absolute;
      border-radius: 999px;
      filter: blur(0);
      opacity: 0.4;
      z-index: 0;
    }}

    .news-card::before {{
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, #ff8a00, transparent 65%);
      top: -100px;
      right: -100px;
    }}

    .news-card::after {{
      width: 450px;
      height: 450px;
      background: radial-gradient(circle, #4f46e5, transparent 65%);
      bottom: -150px;
      left: -150px;
    }}

    .card-inner {{
      position: relative;
      z-index: 1; 
    }}

    /* Top row */
    .card-top {{
      display: flex;
      justify-content: flex-end; /* Align brand to right since badge is gone */
      align-items: center;
      margin-bottom: 30px;
      margin-top: 10px; /* Add top margin for spacing from card edge */
    }}

    .brand {{
      font-size: 24px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      color: var(--text-muted);
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-mark {{
      width: 30px;
      height: 30px;
      border-radius: 8px;
      background: linear-gradient(135deg, #ff8a00, #e52e71);
    }}

    /* Headline */
    .headline {{
      font-size: 52px;
      line-height: 1.2;
      font-weight: 700;
      margin-bottom: 20px;
    }}

    .meta {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 24px;
      color: var(--text-muted);
      margin-bottom: 30px;
    }}

    .meta .dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--text-muted);
      opacity: 0.7;
    }}

    /* Image / media */
    .media-wrapper {{
      border-radius: var(--radius-md);
      overflow: hidden;
      position: relative;
      margin-bottom: 30px;
      border: 1px solid rgba(255,255,255,0.12);
      height: 500px;
    }}

    .media-wrapper img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: top center; /* Ensure faces are visible */
      display: block;
    }}

    .media-tag {{
      position: absolute;
      left: 20px;
      bottom: 20px;
      padding: 8px 16px;
      font-size: 18px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      border-radius: 999px;
      background: rgba(5,7,18,0.76);
      border: 1px solid rgba(255,255,255,0.1);
      backdrop-filter: blur(8px);
    }}

    /* Summary text */
    .summary {{
      font-size: 28px;
      line-height: 1.5;
      color: var(--text-muted);
      margin-bottom: 40px; /* Increased bottom margin for more breathing room */
    }}

    /* Credits row */
    .credits-row {{
      display: flex;
      justify-content: flex-end; /* Align handle to right */
      align-items: flex-end;
      font-size: 20px;
      color: var(--text-muted);
      margin-top: 40px;
      border-top: 1px solid var(--border-subtle);
      padding-top: 20px;
    }}

    .social-handle {{
      font-weight: 500;
      text-align: right;
    }}
  </style>
</head>
<body>
    <article class="news-card">
      <div class="card-inner">
        <!-- top row -->
        <header class="card-top">
          <div class="brand">
            <span class="brand-mark"></span>
            SPORADIC NEWS
          </div>
        </header>

        <!-- headline + meta -->
        <h1 class="headline">
          {headline}
        </h1>

        <div class="meta">
          <span>{date_str}</span>
        </div>

        <!-- image -->
        <div class="media-wrapper">
          <img src="{image_src}" alt="News image">
          {credit_html}
        </div>

        <!-- summary -->
        <p class="summary">
          {summary}
        </p>

        <!-- credits -->
        <footer class="credits-row">
          <div class="social-handle">
            @sporadicnews
          </div>
        </footer>
      </div>
    </article>
</body>
</html>
"""

    def create_news_card(self, headline, background_path, credit, summary):
        """Creates a news card using HTML template."""
        try:
            import datetime
            date_str = datetime.datetime.now().strftime("%B %d, %Y")
            
            # Prepare Credit HTML
            credit_html = ""
            if credit and credit.lower() != "unknown" and credit.strip():
                credit_html = f'<span class="media-tag">Photo • {credit}</span>'
            
            # Prepare HTML
            html_content = self.get_html_template(
                headline=headline,
                summary=summary,
                image_path=background_path,
                credit_html=credit_html,
                date_str=date_str
            )
            
            output_filename = f"article_card_{int(time.time())}.png"
            
            # Render
            # We screenshot the body to get the full card
            self.hti.screenshot(
                html_str=html_content,
                save_as=output_filename,
                size=(1080, 1350)
            )
            
            return os.path.join(self.image_dir, output_filename)
            
        except Exception as e:
            logging.error(f"Error creating HTML news card: {e}")
            return None

    def get_image_for_story(self, story):
        """
        Orchestrates image retrieval and card generation.
        """
        headline = story.get('headline', 'news')
        summary = story.get('summary', '')
        safe_filename = "".join([c for c in headline if c.isalnum() or c in (' ', '-', '_')]).rstrip()[:50] + ".jpg"
        
        background_path = None
        if story.get('image_url'):
            logging.info(f"Downloading image from {story['image_url']}")
            background_path = self.download_image(story['image_url'], safe_filename)
        
        if not background_path:
            logging.warning(f"Could not get image for story: {headline}. Skipping.")
            return None
        
        credit = story.get('image_credit')
            
        # Generate the card with summary
        return self.create_news_card(headline, background_path, credit, summary)

if __name__ == "__main__":
    # Test
    gen = ImageGenerator()
    
    story = {
        'headline': 'Test Clean Card',
        'summary': 'This card should have no "Latest News" badge, no "LiveMint" source, and a photo credit.',
        'image_url': 'https://www.livemint.com/lm-img/img/static/logo-mint2.svg',
        'image_credit': 'LiveMint',
        'is_credited': True
    }
    
    path = gen.get_image_for_story(story)
    print(f"Generated Image Path: {path}")
