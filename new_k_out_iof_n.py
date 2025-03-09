import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Fix for Matplotlib GTK errors
import matplotlib
matplotlib.use("TkAgg")

def binary_image_from_path(image_path, threshold=128):
    """Convert an image to a binary image."""
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    binary_image = np.array(image) > threshold  # Convert to binary
    return binary_image.astype(int)

def generate_shares(image, k, n):
    """Generate n shares for the image using modular arithmetic."""
    height, width = image.shape
    prime = 257  # A prime number larger than the maximum pixel value (255)
    shares = np.zeros((n, height, width), dtype=int)

    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            coefficients = [random.randint(0, prime - 1) for _ in range(k - 1)]
            coefficients.insert(0, pixel)  # First coefficient is the pixel value

            for share_idx in range(n):
                x = share_idx + 1
                y = sum(coeff * (x ** idx) for idx, coeff in enumerate(coefficients)) % prime
                shares[share_idx, i, j] = y

    return shares

def reconstruct_image(selected_shares):
    """Reconstruct the image from k selected shares using Lagrange interpolation."""
    k = len(selected_shares)
    height, width = selected_shares[0].shape
    prime = 257
    reconstructed = np.zeros((height, width), dtype=int)

    for i in range(height):
        for j in range(width):
            x_values = [share_idx + 1 for share_idx in range(k)]
            y_values = [selected_shares[share_idx][i, j] for share_idx in range(k)]

            # Lagrange interpolation to recover the original pixel
            secret = 0
            for idx in range(k):
                numerator, denominator = 1, 1
                for m in range(k):
                    if m != idx:
                        numerator = (numerator * (-x_values[m])) % prime
                        denominator = (denominator * (x_values[idx] - x_values[m])) % prime
                term = (y_values[idx] * numerator * pow(denominator, -1, prime)) % prime
                secret = (secret + term) % prime

            reconstructed[i, j] = secret

    return reconstructed

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

def share_construction():
    """Handle the share construction process through GUI."""
    file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpeg"), ("Image files", "*.png")])
    if not file_path:
        return

    image_label = os.path.splitext(os.path.basename(file_path))[0]
    k = simpledialog.askinteger("Input", "Enter the minimum number of shares required for reconstruction (k):")
    n = simpledialog.askinteger("Input", "Enter the total number of shares to generate (n):")

    if not k or not n:
        return

    binary_image = binary_image_from_path(file_path)
    shares = generate_shares(binary_image, k, n)

    os.makedirs("shares", exist_ok=True)
    for i, share in enumerate(shares):
        filename = f"shares/{image_label}_Share_{i + 1}.png"
        save_share(share, filename)
    
    messagebox.showinfo("Success", "Shares generated successfully!")

def share_reconstruction():
    """Handle the share reconstruction process through GUI."""
    k = simpledialog.askinteger("Input", "Enter the number of shares you want to use for reconstruction (k):")
    if not k:
        return

    selected_shares = []
    for i in range(k):
        file_path = filedialog.askopenfilename(title=f"Select share {i + 1}", filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        selected_shares.append(np.array(Image.open(file_path).convert("L")) > 128)

    selected_shares = [share.astype(int) for share in selected_shares]
    reconstructed_image = reconstruct_image(selected_shares)
    display_image(reconstructed_image, "Reconstructed Image")

def main():
    """Main function to create GUI."""
    root = tk.Tk()
    root.title("Secret Sharing Scheme")
    root.geometry("400x200")

    tk.Label(root, text="Choose an option:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Share Construction", command=share_construction).pack(pady=5)
    tk.Button(root, text="Share Reconstruction", command=share_reconstruction).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()