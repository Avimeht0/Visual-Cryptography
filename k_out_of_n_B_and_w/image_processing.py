import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def binary_image_from_path(image_path, threshold=128):
    """Convert an image to a binary image."""
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    binary_image = np.array(image) > threshold  # Convert to binary
    return binary_image.astype(int)

def save_share(share, filename):
    """Save a share as an image, converting it to uint8 format."""
    share = (share * 255).astype(np.uint8)  # Convert binary to grayscale and ensure uint8 format
    img = Image.fromarray(share)
    img.save(filename)

def display_image(image, title):
    """Display an image."""
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()
