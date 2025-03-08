import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def binary_image_from_path(image_path, threshold=128):
    """Convert an image to a binary image."""
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    binary_image = np.array(image) > threshold  # Convert to binary
    return binary_image.astype(int)

def display_image(image, title):
    """Display an image."""
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()