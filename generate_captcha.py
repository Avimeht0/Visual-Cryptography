from captcha.image import ImageCaptcha
import random
import string
from PIL import Image, ImageDraw, ImageFont

def generate_captcha(text=None, width=200, height=100, font_size=50):
    """Generate a black and white CAPTCHA image and save it with the text as filename."""
    image = ImageCaptcha(width=width, height=height, font_sizes=[font_size])
    
    if text is None:
        text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))  # Random 5-character CAPTCHA
    
    captcha_image = image.generate_image(text).convert("L")  # Convert to black and white (grayscale)
    
    # Add text to the image
    draw = ImageDraw.Draw(captcha_image)
    font = ImageFont.load_default()  # Default font (you can specify a TTF font if needed)
    
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    position = ((width - text_width) // 2, (height - text_height) // 2)
    draw.text(position, text, font=font, fill=0)  # Write text in black
    
    output_file = f"{text}.png"  # Save file with CAPTCHA text as the filename
    captcha_image.save(output_file)
    print(f"CAPTCHA generated: {text} (saved as {output_file})")
    
if __name__ == "__main__":
    generate_captcha()
