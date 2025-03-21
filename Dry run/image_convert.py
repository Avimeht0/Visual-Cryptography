from PIL import Image
import numpy as np

def binary_image_from_path(image_path, threshold=128):
    """Convert an image to a binary image."""
    
    # Step 1: Open the image
    print("Opening the image...")
    image = Image.open(image_path)
    print(f"Image opened: {image.size} size, {image.mode} mode")
    
    # Step 2: Convert the image to grayscale (L mode)
    print("Converting the image to grayscale...")
    grayscale_image = image.convert("L")
    print(f"Grayscale image created: {grayscale_image.size} size, {grayscale_image.mode} mode")
    
    # Step 3: Convert the grayscale image to a NumPy array
    print("Converting grayscale image to a NumPy array...")
    grayscale_array = np.array(grayscale_image)
    print(f"NumPy array shape: {grayscale_array.shape}")
    
    # Step 4: Create a binary image based on the threshold
    print(f"Applying threshold: {threshold}...")
    binary_image = grayscale_array > threshold  # This will create True/False values
    print(f"Binary image (True/False array) shape: {binary_image.shape}")
    
    # Step 5: Convert the True/False to 1/0
    print("Converting True/False to 1/0...")
    binary_image_int = binary_image.astype(int)
    print("Binary image (0/1 array) ready.")
    
    return binary_image_int

# Call the function with your image file
image_path = "/home/arvind/Visual-Cryptography/archive/samples/2b827.png"  # Replace with the actual path to your image
binary_image = binary_image_from_path(image_path)

# To check the result:
print("Binary image output (part of it):")
print(binary_image[:10, :100])  # Print a small part of the binary image for inspection
