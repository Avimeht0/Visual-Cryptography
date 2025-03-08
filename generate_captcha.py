from captcha.image import ImageCaptcha
import random
import string

# Function to generate a random string for the captcha text
def random_string(length=5):
    letters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# Function to generate black-and-white captcha
def generate_captcha(text):
    image = ImageCaptcha(width=280, height=90, font_sizes=[40])
    
    # Set background color to white and text color to black
    image_background_color = (255, 255, 255)  # White background
    text_color = (0, 0, 0)  # Black text
    
    # Write the captcha text on the image
    captcha_image = image.generate_image(text)
    
    # Convert image to black and white (thresholding)
    captcha_image = captcha_image.convert("1")  # 1 is for 1-bit pixels (black and white)
    
    # Save the generated captcha image
    captcha_image.save(f'captcha_{text}.png')

    print(f"Captcha image saved as captcha_{text}.png")

# Generate a random captcha text
captcha_text = random_string()  # Generate random text
generate_captcha(captcha_text)  # Generate and save the captcha
