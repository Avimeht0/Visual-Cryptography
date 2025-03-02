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

def binary_image_from_path(image_path):
    """Convert an image to a properly binarized image with adaptive thresholding."""
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    image = np.array(image)
    
    # Adaptive thresholding to prevent pixel loss
    threshold = np.mean(image)  # Dynamic threshold
    binary_image = (image > threshold).astype(int)
    
    return binary_image


def generate_matrices_2x2():
    """Generate structured subpixel matrices for visual secret sharing (2x2)."""
    C0 = np.array([[[0, 0], [1, 1]], [[1, 1], [0, 0]], [[0, 1], [0, 1]], [[1, 0], [1, 0]], [[1, 0], [0, 1]], [[0, 1], [1, 0]]])
    C1 = 1 - C0  # Complement matrices for black pixel encoding
    return C0, C1


def construct_shares_2x2(image, n, image_label):
    """Generate shares while preserving subpixel integrity."""
    height, width = image.shape
    C0, C1 = generate_matrices_2x2()
    num_patterns = C0.shape[0]
    
    shares = np.zeros((n, height, width, 2, 2), dtype=int)
    
    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            pattern_idx = random.randint(0, num_patterns - 1)  # Random pattern choice
            selected_pattern = C0[pattern_idx] if pixel == 0 else C1[pattern_idx]
            
            # Random column permutation for each share
            for s in range(n):
                shares[s, i, j] = selected_pattern
    
    os.makedirs("shares", exist_ok=True)
    for s in range(n):
        filename = f"shares/{image_label}_Share_{s + 1}.png"
        save_share(shares[s], filename)
    
    messagebox.showinfo("Success", "Shares generated successfully!")


def save_share(share, filename):
    """Save a share as an image."""
    share = (share * 255).astype(np.uint8)
    img = Image.fromarray(share.reshape(share.shape[0] * 2, share.shape[1] * 2))
    img.save(filename)


def reconstruct_image_2x2(selected_shares):
    """Reconstruct the image from stacked shares while maintaining subpixel alignment."""
    height, width, _, _ = selected_shares[0].shape
    reconstructed = np.zeros((height, width), dtype=int)
    
    for i in range(height):
        for j in range(width):
            stacked = np.bitwise_or.reduce([share[i, j] for share in selected_shares])
            reconstructed[i, j] = 1 if np.all(stacked == 1) else 0
    
    return reconstructed


def display_image(image, title):
    """Display an image."""
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()


def share_construction():
    """Handle the share construction process through GUI."""
    file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpeg;*.png")])
    if not file_path:
        return

    image_label = os.path.splitext(os.path.basename(file_path))[0]
    n = simpledialog.askinteger("Input", "Enter the total number of shares to generate (n):")
    
    if not n:
        return

    binary_image = binary_image_from_path(file_path)
    construct_shares_2x2(binary_image, n, image_label)


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
        selected_shares.append(np.array(Image.open(file_path).convert("L")).reshape(-1, 2, 2) > 128)
    
    selected_shares = [share.astype(int) for share in selected_shares]
    reconstructed_image = reconstruct_image_2x2(selected_shares)
    display_image(reconstructed_image, "Reconstructed Image")


def main():
    """Main function to create GUI."""
    root = tk.Tk()
    root.title("Visual Secret Sharing")
    root.geometry("400x200")

    tk.Label(root, text="Choose an option:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Share Construction", command=share_construction).pack(pady=5)
    tk.Button(root, text="Share Reconstruction", command=share_reconstruction).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
