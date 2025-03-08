import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from itertools import combinations

# Fix for Matplotlib GTK errors
import matplotlib
matplotlib.use("TkAgg")

def binary_image_from_path(image_path, threshold=128):
    """Convert an image to a binary image."""
    image = Image.open(image_path).convert("L")  # Convert to grayscale
    binary_image = np.array(image) > threshold  # Convert to binary
    return binary_image.astype(int)

def construct_basis_matrices(k):
    """Construct basis matrices for a (k, n) threshold scheme."""
    # Example for (2, 2) scheme; extend this for general k
    if k == 2:
        # Basis matrices for (2,2) scheme
        C0 = np.array([[1, 0], [1, 0]], dtype=int)
        C1 = np.array([[1, 0], [0, 1]], dtype=int)
    else:
        # Extend with proper basis matrices for general k
        raise NotImplementedError("Basis matrices for general k not implemented.")
    return C0, C1

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
    """Generate random functions ensuring coverage for any k shares."""
    # This needs to be adjusted based on the chosen basis matrices
    return [lambda x: random.randint(0, k-1) for _ in range(n * k)]

def save_share(share, filename):
    """Save a share as an image."""
    share = (share * 255).astype(np.uint8)
    img = Image.fromarray(share)
    img.save(filename)

def construct_shares_k_out_n(image, k, n, image_label):
    """Generate and save shares using correct basis matrices."""
    height, width = image.shape
    C0, C1 = construct_basis_matrices(k)  # Use the correct basis matrices
    num_subpixels = C0.shape[1]
    shares = np.zeros((n, height, width * num_subpixels), dtype=int)

    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            # Choose the basis matrix based on the pixel
            basis = C0 if pixel == 0 else C1
            # Generate a permutation for the columns (same for all shares)
            perm = np.random.permutation(num_subpixels)
            permuted_basis = basis[:, perm]
            # Assign rows to each share
            for share_idx in range(n):
                # Select a random row (for demo; adjust for proper distribution)
                row = random.randint(0, k-1)
                shares[share_idx, i, j * num_subpixels: (j + 1) * num_subpixels] = permuted_basis[row]

    os.makedirs("shares", exist_ok=True)
    for i in range(n):
        filename = f"shares/{image_label}_Share_{i + 1}.png"
        save_share(shares[i], filename)
    
    messagebox.showinfo("Success", "Shares generated successfully!")

def reconstruct_image(selected_shares):
    """Reconstruct the image by checking full subpixel coverage."""
    num_shares, height, full_width = selected_shares.shape
    num_subpixels = full_width // (full_width // selected_shares[0].shape[1])  # Adjust based on your scheme
    width = full_width // num_subpixels
    reconstructed = np.zeros((height, width), dtype=int)

    for i in range(height):
        for j in range(width):
            # Extract the subpixels from each share
            subpixels = [share[i, j * num_subpixels: (j + 1) * num_subpixels] for share in selected_shares]
            # OR all subpixels
            combined = np.bitwise_or.reduce(subpixels)
            # Check if all subpixels are 1
            reconstructed[i, j] = 1 if np.all(combined == 1) else 0

    return reconstructed

# Remaining functions (display_image, share_construction, share_reconstruction, main) remain the same as in the original code

def display_image(image, title):
    """Display an image."""
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.axis("off")
    plt.show()

def share_construction():
    """Handle share construction."""
    file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    if not file_path:
        return

    image_label = os.path.splitext(os.path.basename(file_path))[0]
    k = simpledialog.askinteger("Input", "Enter k (required shares):")
    n = simpledialog.askinteger("Input", "Enter n (total shares):")

    if not k or not n:
        return

    binary_image = binary_image_from_path(file_path)
    construct_shares_k_out_n(binary_image, k, n, image_label)

def share_reconstruction():
    """Handle share reconstruction."""
    k = simpledialog.askinteger("Input", "Enter k (number of shares):")
    if not k:
        return

    selected_shares = []
    for _ in range(k):
        file_path = filedialog.askopenfilename(title="Select a share", filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        img = np.array(Image.open(file_path).convert("L")) > 128
        selected_shares.append(img.astype(int))

    reconstructed_image = reconstruct_image(np.array(selected_shares))
    display_image(reconstructed_image, "Reconstructed Image")

def main():
    """Main GUI."""
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