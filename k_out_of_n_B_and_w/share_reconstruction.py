# import numpy as np
# from tkinter import filedialog, simpledialog
# from PIL import Image
# from image_processing import display_image

# def reconstruct_image(selected_shares):
#     """Reconstruct the image from selected shares."""
#     height, full_width = selected_shares[0].shape
#     num_subpixels = full_width // selected_shares[0].shape[1]
#     width = full_width // num_subpixels
#     reconstructed = np.zeros((height, width), dtype=int)

#     for i in range(height):
#         for j in range(width):
#             subpixel_sum = np.zeros(num_subpixels, dtype=int)
#             for share in selected_shares:
#                 subpixel_sum |= share[i, j * num_subpixels: (j + 1) * num_subpixels]
#             reconstructed[i, j] = 1 if np.sum(subpixel_sum) == num_subpixels else 0

#     return reconstructed

# def share_reconstruction():
#     """Handle the share reconstruction process through GUI."""
#     k = simpledialog.askinteger("Input", "Enter the number of shares you want to use for reconstruction (k):")
#     if not k:
#         return

#     selected_shares = []
#     for i in range(k):
#         file_path = filedialog.askopenfilename(title=f"Select share {i + 1}", filetypes=[("PNG files", "*.png")])
#         if not file_path:
#             return
#         selected_shares.append(np.array(Image.open(file_path).convert("L")) > 128)

#     selected_shares = [share.astype(int) for share in selected_shares]
#     reconstructed_image = reconstruct_image(selected_shares)
#     display_image(reconstructed_image, "Reconstructed Image")


import numpy as np
from tkinter import filedialog, simpledialog
from PIL import Image
from image_processing import display_image

def reconstruct_image(selected_shares, d, alpha, m):
    """
    Reconstruct the image from selected shares using the thresholding rules.
    
    Parameters:
        selected_shares (list): List of k shares (each share is a 2D array of subpixels).
        d (int): Threshold for determining black pixels.
        alpha (float): Relative difference factor.
        m (int): Number of subpixels per pixel.
    
    Returns:
        reconstructed_image (numpy.ndarray): Reconstructed binary image.
    """
    # Step 1: Initialize the reconstructed image
    height, full_width = selected_shares[0].shape
    width = full_width // m
    reconstructed_image = np.zeros((height, width), dtype=int)

    # Step 2: Combine the shares
    for i in range(height):
        for j in range(width):
            # Extract the corresponding subpixels from each share
            subpixel_sum = np.zeros(m, dtype=int)
            for share in selected_shares:
                subpixel_sum |= share[i, j * m: (j + 1) * m]

            # Step 3: Calculate the Hamming weight
            H_V = np.sum(subpixel_sum)

            # Step 4: Apply the thresholding rules
            if H_V >= d:
                reconstructed_image[i, j] = 1  # Black pixel
            elif H_V < d - alpha * m:
                reconstructed_image[i, j] = 0  # White pixel

    # Step 5: Return the reconstructed image
    return reconstructed_image

def share_reconstruction():
    """Handle the share reconstruction process through GUI."""
    # Step 1: Get the number of shares (k) for reconstruction
    k = simpledialog.askinteger("Input", "Enter the number of shares you want to use for reconstruction (k):")
    if not k:
        return

    # Step 2: Load the selected shares
    selected_shares = []
    for i in range(k):
        file_path = filedialog.askopenfilename(title=f"Select share {i + 1}", filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        # Convert the share to a binary array
        share = np.array(Image.open(file_path).convert("L")) > 128
        selected_shares.append(share.astype(int))

    # Step 3: Calculate parameters (d, alpha, m) based on k
    m = 2 ** (k - 1)  # Number of subpixels per pixel
    d = m             # Threshold for black pixels
    alpha = 1 / (2 ** (k - 1))  # Relative difference factor

    # Step 4: Reconstruct the image
    reconstructed_image = reconstruct_image(selected_shares, d, alpha, m)

    # Step 5: Display the reconstructed image
    display_image(reconstructed_image, "Reconstructed Image")