from captcha.image import ImageCaptcha
import random
import string
import os

# Function to generate a random CAPTCHA string
def generate_captcha_text(length=6):
    characters = string.ascii_uppercase + string.digits  # Characters for the CAPTCHA
    captcha_text = ''.join(random.choice(characters) for _ in range(length))
    return captcha_text

# Function to create a CAPTCHA image with the filename as the text
def generate_captcha_image():
    captcha_text = generate_captcha_text()  # Generate random text
    image = ImageCaptcha(width=280, height=90)
    
    # Directory to save the captcha
    captcha_directory = './captchas'  # Path to your 'captchas' directory

    # Ensure the directory exists
    if not os.path.exists(captcha_directory):
        os.makedirs(captcha_directory)  # Create the directory if it doesn't exist
    
    # File path where the image will be saved
    filename = os.path.join(captcha_directory, f'{captcha_text}.png')  # Save file inside 'captchas'
    
    # Generate and save the CAPTCHA image
    image.write(captcha_text, filename)  # Save the image with the filename
    print(f'Captcha text: {captcha_text}, saved as: {filename}')

# Generate and save CAPTCHA image
generate_captcha_image()
