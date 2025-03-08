import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
from itertools import combinations
import random
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def color_image_from_path(image_path):
    """Load a color image and split into R, G, B channels."""
    image = Image.open(image_path).convert("RGB")
    return np.array(image)

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

def construct_shares_k_out_n_color(image, k, n, image_label):
    """Generate and save shares for a color image."""
    height, width, _ = image.shape
    C0, C1 = construct_matrices(k)
    num_subpixels = C0.shape[1]
    shares = np.zeros((n, height, width * num_subpixels, 3), dtype=int)
    H = generate_random_functions(n, k)

    for c in range(3):  # Process R, G, and B channels separately
        for i in range(height):
            for j in range(width):
                pixel = image[i, j, c]
                subpixel_pattern = C0 if pixel < 128 else C1
                permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
                for participant in range(n):
                    h = H[random.randint(0, len(H) - 1)]
                    row_index = h(participant)
                    shares[participant, i, j * num_subpixels: (j + 1) * num_subpixels, c] = permuted_pattern[row_index]

    os.makedirs("shares", exist_ok=True)
    for i in range(n):
        filename = f"shares/{image_label}_Share_{i + 1}.png"
        save_share(shares[i], filename)
        print(f"Saved: {filename}")

    return shares

def reconstruct_image_color(selected_shares, k, n):
    """Reconstruct the color image from selected shares."""
    height, full_width, _ = selected_shares[0].shape
    num_subpixels = full_width // selected_shares[0].shape[1]
    width = full_width // num_subpixels
    reconstructed = np.zeros((height, width, 3), dtype=int)

    for c in range(3):  # Process R, G, and B channels separately
        for i in range(height):
            for j in range(width):
                subpixel_sum = np.zeros(num_subpixels, dtype=int)
                for share in selected_shares:
                    subpixel_sum |= share[i, j * num_subpixels: (j + 1) * num_subpixels, c]
                reconstructed[i, j, c] = 255 if np.sum(subpixel_sum) == num_subpixels else 0

    return reconstructed

class VisualCryptographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visual Cryptography")
        
        self.image_path = None
        self.shares = None  # Initialize shares as None
        
        # GUI Elements
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack()
        
        self.generate_button = tk.Button(root, text="Generate Shares", command=self.generate_shares)
        self.generate_button.pack()
        
        self.reconstruct_button = tk.Button(root, text="Reconstruct Image", command=self.reconstruct_image)
        self.reconstruct_button.pack()
        
        self.image_label = tk.Label(root)
        self.image_label.pack()
        
    def load_image(self):
        """Load an image from the file system."""
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            self.original_image = color_image_from_path(self.image_path)
            self.display_image_in_gui(self.original_image, "Original Image")
    
    def generate_shares(self):
        """Generate shares from the loaded image."""
        if not self.image_path:
            messagebox.showerror("Error", "Please load an image first.")
            return
        
        k = 2  # Minimum required shares for reconstruction
        n = 3  # Total number of shares
        
        self.shares = construct_shares_k_out_n_color(self.original_image, k, n, "Image1")
        messagebox.showinfo("Success", "Shares generated and saved in the 'shares' folder.")
    
    def reconstruct_image(self):
        """Reconstruct the image from the generated shares."""
        if self.shares is None:  # Check if shares are initialized
            messagebox.showerror("Error", "Please generate shares first.")
            return
        
        selected_shares = [self.shares[0], self.shares[1], self.shares[2]]
        reconstructed_image = reconstruct_image_color(selected_shares, k=2, n=3)
        self.display_image_in_gui(reconstructed_image, "Reconstructed Image")
    
    def display_image_in_gui(self, image, title):
        """Display an image in the GUI."""
        image = Image.fromarray(image.astype('uint8'))
        image.thumbnail((300, 300))  # Resize image to fit in the GUI
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo  # Keep a reference to avoid garbage collection
        self.image_label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = VisualCryptographyApp(root)
    root.mainloop()