import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
from itertools import combinations
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

# Fix for Matplotlib GTK errors
import matplotlib
matplotlib.use("TkAgg")

def binary_image_from_path(image_path):
    """Convert an image to a properly binarized image with adaptive thresholding."""
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    image = np.array(image)
    
    # Adaptive thresholding to prevent pixel loss
    threshold = np.mean(image)  # Dynamic threshold
    binary_image = (image > threshold).astype(int)
    
    return binary_image


def generate_subsets(k):
    """Generate all subsets of even and odd cardinality."""
    elements = list(range(k))
    even_subsets = [set(comb) for r in range(0, k + 1, 2) for comb in combinations(elements, r)]
    odd_subsets = [set(comb) for r in range(1, k + 1, 2) for comb in combinations(elements, r)]
    return even_subsets, odd_subsets

def construct_matrices(k):
    """Construct C0 and C1 matrices based on even and odd subsets."""
    even_subsets, odd_subsets = generate_subsets(k)
    num_columns = len(even_subsets)
    C0 = np.zeros((k, num_columns), dtype=int)
    C1 = np.zeros((k, num_columns), dtype=int)
    for i in range(k):
        for j, subset in enumerate(even_subsets):
            if i in subset:
                C0[i, j] = 1
        for j, subset in enumerate(odd_subsets):
            if i in subset:
                C1[i, j] = 1
    return C0, C1

def generate_random_functions(n, k):
    """Generate a collection of random functions mapping {1..n} -> {1..k}."""
    return [lambda x, k=k: random.randint(0, k - 1) for _ in range(n * k)]

def save_share(share, filename):
    """Save a share as an image, converting it to uint8 format."""
    share = (share * 255).astype(np.uint8)  # Convert binary to grayscale and ensure uint8 format
    img = Image.fromarray(share)
    img.save(filename)

def construct_shares_k_out_n(image, k, n, image_label):
    """Generate and save shares while maintaining subpixel integrity."""
    height, width = image.shape
    C0, C1 = construct_matrices(k)
    num_subpixels = C0.shape[1]

    # Shares are now stored as 3D arrays (preserve subpixel structures)
    shares = np.zeros((n, height, width, num_subpixels), dtype=int)

    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            subpixel_pattern = C0 if pixel == 0 else C1  # Select appropriate pattern
            permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
            
            for participant in range(n):
                row_index = participant % k  # Ensure subpixel alignment
                shares[participant, i, j, :] = permuted_pattern[row_index]

    # Save shares as images
    os.makedirs("shares", exist_ok=True)
    for i in range(n):
        filename = f"shares/{image_label}_Share_{i + 1}.png"
        save_share(shares[i].reshape(height, width * num_subpixels), filename)

    messagebox.showinfo("Success", "Shares generated successfully!")

def reconstruct_image(selected_shares):
    """Reconstruct the original image while preserving subpixel integrity."""
    height, full_width = selected_shares[0].shape
    num_subpixels = full_width // selected_shares[0].shape[1]
    width = full_width // num_subpixels
    
    # Correct subpixel alignment
    reconstructed = np.zeros((height, width), dtype=int)

    for i in range(height):
        for j in range(width):
            combined_subpixels = np.zeros(num_subpixels, dtype=int)
            
            # Use bitwise OR instead of simple sum
            for share in selected_shares:
                combined_subpixels |= share[i, j * num_subpixels: (j + 1) * num_subpixels]
            
            # If all subpixels are black, mark as black
            reconstructed[i, j] = 1 if np.all(combined_subpixels == 1) else 0

    return reconstructed


def display_image(image, title):
    """Display an image."""
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()

def share_construction():
    """Handle the share construction process through GUI."""
    file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpeg"),("Image files", "*.png")])
    if not file_path:
        return

    image_label = os.path.splitext(os.path.basename(file_path))[0]
    k = simpledialog.askinteger("Input", "Enter the minimum number of shares required for reconstruction (k):")
    n = simpledialog.askinteger("Input", "Enter the total number of shares to generate (n):")

    if not k or not n:
        return

    binary_image = binary_image_from_path(file_path)
    construct_shares_k_out_n(binary_image, k, n, image_label)

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
