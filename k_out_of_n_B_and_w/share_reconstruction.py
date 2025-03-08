import numpy as np
from tkinter import filedialog, simpledialog
from PIL import Image
from image_processing import display_image
from utils import reconstruct_image

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