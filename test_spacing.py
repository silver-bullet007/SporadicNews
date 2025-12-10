import sys
sys.path.insert(0, 'c:\\Users\\Win10\\Desktop\\scratch')

from image_gen import ImageGenerator
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a test story with realistic content
test_story = {
    'headline': 'India\'s Economic Growth Surges to 7.8% in Latest Quarter',
    'summary': 'The Indian economy demonstrated robust growth in Q3, driven by strong consumer spending and increased manufacturing output across key sectors.',
    'image_url': 'https://images.livemint.com/img/2024/12/03/1600x900/PTI12-01-2024-000025B-0_1733042408497_1733042427076.jpg',
    'image_credit': 'PTI',
    'is_credited': True
}

print("Generating test news card with improved spacing...")
gen = ImageGenerator()
result = gen.get_image_for_story(test_story)

if result:
    print(f"SUCCESS! Generated image at: {result}")
    print(f"\nImage should now have:")
    print("   - Proper spacing above 'SPORADIC NEWS' brand")
    print("   - Proper spacing below the summary text")
    print("   - No cutoff at top or bottom")
    print("   - All content visible within the frame")
else:
    print("Failed to generate image")
