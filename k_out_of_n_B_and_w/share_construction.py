import numpy as np
import os
from tkinter import filedialog, simpledialog, messagebox
from image_processing import binary_image_from_path, save_share
from utils import construct_matrices, generate_random_functions
from PIL import Image

def construct_shares_k_out_n(image, k, n, image_label):
    """Generate and save shares."""
    height, width = image.shape
    C0, C1 = construct_matrices(k)
    num_subpixels = C0.shape[1]
    shares = np.zeros((n, height, width * num_subpixels), dtype=int)
    H = generate_random_functions(n, k)

    for i in range(height):
        for j in range(width):
            pixel = image[i, j]
            subpixel_pattern = C0 if pixel == 0 else C1
            permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
            for participant in range(n):
                h = H[np.random.randint(len(H))]
                row_index = h(participant)
                shares[participant, i, j * num_subpixels: (j + 1) * num_subpixels] = permuted_pattern[row_index]

    os.makedirs("shares", exist_ok=True)
    for i in range(n):
        filename = f"shares/{image_label}_Share_{i + 1}.png"
        save_share(shares[i], filename)
    
    messagebox.showinfo("Success", "Shares generated successfully!")

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
