import numpy as np
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image
from image_processing import display_image
import os

def reconstruct_image(selected_shares, d, alpha, m):
    """
    Reconstruct the image from selected shares using the thresholding rules.
    
    Parameters:
        selected_shares (list): List of k shares (each share is a 2D array of subpixels).
        d (int): Threshold for determining black pixels.
        alpha (float): Relative difference factor.
        m (int): Number of subpixels per pixel.
    
    Returns:
        reconstructed_image (numpy.ndarray): Reconstructed binary image with the same size as the shares.
    """
    # Step 1: Initialize the reconstructed image with the same size as the shares
    height, full_width = selected_shares[0].shape
    reconstructed_image = np.zeros((height, full_width), dtype=int)

    # Step 2: Combine the shares
    for i in range(height):
        for j in range(full_width // m):  # Iterate over each pixel block
            # Extract the corresponding subpixels from each share
            subpixel_sum = np.zeros(m, dtype=int)
            for share in selected_shares:
                subpixel_sum |= share[i, j * m: (j + 1) * m]

            # Step 3: Calculate the Hamming weight
            H_V = np.sum(subpixel_sum)

            # Step 4: Apply the thresholding rules
            if H_V >= d:
                reconstructed_image[i, j * m: (j + 1) * m] = 1  # Black pixel (set all subpixels to 1)
            elif H_V < d - alpha * m:
                reconstructed_image[i, j * m: (j + 1) * m] = 0  # White pixel (set all subpixels to 0)

    # Step 5: Return the reconstructed image
    return reconstructed_image

def share_reconstruction():
    """Handle the share reconstruction process through GUI."""
    # Step 1: Get the number of shares (k) for reconstruction
    k = simpledialog.askinteger("Input", "Enter the number of shares you want to use for reconstruction (k):")
    if not k:
        return

    # Step 2: Load the selected shares and determine the folder path
    selected_shares = []
    share_folder = None  # To store the folder path of the shares

    for i in range(k):
        file_path = filedialog.askopenfilename(title=f"Select share {i + 1}", filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        
        # Convert the share to a binary array
        share = np.array(Image.open(file_path).convert("L")) > 128
        selected_shares.append(share.astype(int))

        # Determine the folder path of the shares
        if share_folder is None:
            share_folder = os.path.dirname(file_path)

    # Step 3: Calculate parameters (d, alpha, m) based on k
    m = 2 ** (k - 1)  # Number of subpixels per pixel
    d = m             # Threshold for black pixels
    alpha = 1 / (2 ** (k - 1))  # Relative difference factor

    # Step 4: Reconstruct the image
    reconstructed_image = reconstruct_image(selected_shares, d, alpha, m)

    # Step 5: Save the reconstructed image in the same folder as the shares
    if share_folder:
        reconstructed_image_path = os.path.join(share_folder, "reconstructed_image.png")
        reconstructed_image_pil = Image.fromarray((reconstructed_image * 255).astype(np.uint8))
        reconstructed_image_pil.save(reconstructed_image_path)
        messagebox.showinfo("Success", f"Reconstructed image saved at:\n{reconstructed_image_path}")
    else:
        messagebox.showerror("Error", "Could not determine the folder path for saving the reconstructed image.")

    # Step 6: Display the reconstructed image
    display_image(reconstructed_image, "Reconstructed Image")