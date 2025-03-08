import os
import numpy as np
from tkinter import filedialog, messagebox, simpledialog
from image_processing import binary_image_from_path
from utils import construct_shares_k_out_n

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