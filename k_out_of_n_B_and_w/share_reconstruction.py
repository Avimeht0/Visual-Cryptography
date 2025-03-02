import numpy as np
import tkinter as tk
from tkinter import filedialog, simpledialog
from PIL import Image
from image_processing import display_image

def reconstruct_image(selected_shares):
    """Reconstruct the image from selected shares."""
    height, full_width = selected_shares[0].shape
    num_subpixels = full_width // selected_shares[0].shape[1]
    width = full_width // num_subpixels
    reconstructed = np.zeros((height, width), dtype=int)

    for i in range(height):
        for j in range(width):
            subpixel_sum = np.zeros(num_subpixels, dtype=int)
            for share in selected_shares:
                subpixel_sum |= share[i, j * num_subpixels: (j + 1) * num_subpixels]
            reconstructed[i, j] = 1 if np.sum(subpixel_sum) == num_subpixels else 0

    return reconstructed

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
