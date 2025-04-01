# import os
# import numpy as np
# from tkinter import filedialog, messagebox, simpledialog
# from PIL import Image
# import random
# from itertools import combinations, product
# from math import factorial, sqrt, exp, pi

# def binary_image_from_path(image_path, threshold=128):
#     """Convert an image to a binary image."""
#     image = Image.open(image_path).convert("L")  # Convert to grayscale
#     binary_image = np.array(image) > threshold  # Convert to binary
#     return binary_image.astype(int)

# def generate_subsets(k):
#     """Generate all subsets of even and odd cardinality."""
#     elements = list(range(k))
#     even_subsets = [set(comb) for r in range(0, k + 1, 2) for comb in combinations(elements, r)]
#     odd_subsets = [set(comb) for r in range(1, k + 1, 2) for comb in combinations(elements, r)]
#     return even_subsets, odd_subsets

# def construct_matrices(k):
#     """Construct C0 and C1 matrices based on even and odd subsets.
#     This follows Construction 2 from the paper (optimal k-out-k scheme)."""
#     even_subsets, odd_subsets = generate_subsets(k)
#     num_columns = len(even_subsets)  # = 2^(k-1)
#     C0 = np.zeros((k, num_columns), dtype=int)
#     C1 = np.zeros((k, num_columns), dtype=int)
    
#     for i in range(k):
#         for j, subset in enumerate(even_subsets):
#             if i in subset:
#                 C0[i, j] = 1
#         for j, subset in enumerate(odd_subsets):
#             if i in subset:
#                 C1[i, j] = 1
#     return C0, C1

# # =============================================
# # Original function - doesn't meet paper requirements
# # =============================================
# def generate_random_functions(n, k):
#     """Original implementation - creates random mappings.
#     Problem: Doesn't guarantee the paper's requirement that for any subset B of size k,
#     the probability that h(B) yields q distinct values is the same for all h in H."""
#     return [lambda x, k=k: random.randint(0, k - 1) for _ in range(n * k)]

# # =============================================
# # New function that follows paper requirements
# # =============================================
# def generate_hash_family(n, k):
#     """Generates a collection H of functions mapping {1..n} -> {1..k} that satisfies:
#     1. For all h in H, h: {1..n} -> {1..k}
#     2. For all subsets B of size k, the probability that h(B) has q distinct values is β_q
#     This implementation uses all possible functions (n^k) which satisfies the requirement."""
#     return list(product(range(k), repeat=n))  # All possible functions

# def save_share(share, filename):
#     """Save a share as an image, converting it to uint8 format."""
#     share = (share * 255).astype(np.uint8)
#     img = Image.fromarray(share)
#     img.save(filename)

# def calculate_paper_parameters(k, n):
#     """Calculates the exact parameters from Theorem 6:
#     m = n^k * 2^{k-1}
#     α = (2e^{-k})/sqrt(2πk)
#     r = n^k * (2^{k-1}!)"""
#     m = (n ** k) * (2 ** (k - 1))
#     alpha = (2 * exp(-k)) / sqrt(2 * pi * k)
#     r = (n ** k) * factorial(2 ** (k - 1))
#     return m, alpha, r

# # =============================================
# # Original share construction - has several deviations from paper
# # =============================================
# # def construct_shares_k_out_n(image, k, n, image_label):
# #     """Original implementation has these issues:
# #     1. Uses random functions instead of proper hash family
# #     2. Permutes columns which isn't in the paper's general construction
# #     3. Doesn't track the required parameters (m', α', r')"""
# #     height, width = image.shape
# #     C0, C1 = construct_matrices(k)
# #     num_subpixels = C0.shape[1]
# #     shares = np.zeros((n, height, width * num_subpixels), dtype=int)
# #     H = generate_random_functions(n, k)  # Problem: Uses random functions

# #     for i in range(height):
# #         for j in range(width):
# #             pixel = image[i, j]
# #             subpixel_pattern = C0 if pixel == 0 else C1
# #             # Problem: Paper doesn't permute columns in general construction
# #             permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
# #             for participant in range(n):
# #                 h = H[random.randint(0, len(H) - 1)]
# #                 row_index = h(participant)
# #                 shares[participant, i, j * num_subpixels: (j + 1) * num_subpixels] = permuted_pattern[row_index]

# #     os.makedirs("shares", exist_ok=True)
# #     image_share_dir = os.path.join("shares", image_label)
# #     os.makedirs(image_share_dir, exist_ok=True)
    
# #     for i in range(n):
# #         filename = os.path.join(image_share_dir, f"{image_label}_Share_{i + 1}.png")
# #         save_share(shares[i], filename)
    
# #     messagebox.showinfo("Success", "Shares generated successfully!")

# # =============================================
# # New function that follows paper exactly
# # =============================================
# def construct_shares_paper_compliant(image, k, n, image_label):
#     """Strict implementation following paper's construction:
#     1. Uses proper hash family H
#     2. Follows exact matrix construction S^b_t[i,(j,h)] = T^b_t[h(i),j]
#     3. Tracks all required parameters"""
#     height, width = image.shape
#     C0, C1 = construct_matrices(k)
#     m = C0.shape[1]  # = 2^{k-1}
    
#     # Generate proper function collection H
#     H = generate_hash_family(n, k)
#     l = len(H)  # = n^k
    
#     # Calculate paper parameters
#     m_prime, alpha_prime, r_prime = calculate_paper_parameters(k, n)
    
#     # Initialize shares (n x height x (width*m_prime))
#     shares = np.zeros((n, height, width * m_prime), dtype=np.uint8)
    
#     # For each pixel in original image
#     for y in range(height):
#         for x in range(width):
#             pixel = image[y, x]
#             base_matrix = C0 if pixel == 0 else C1
            
#             # For each function h in H
#             for h_idx, h in enumerate(H):
#                 # For each subpixel in base matrix
#                 for subpixel in range(m):
#                     col = h_idx * m + subpixel
#                     for participant in range(n):
#                         row = h[participant]  # h maps participant to row
#                         shares[participant, y, x * m_prime + col] = base_matrix[row, subpixel]
    
#     # Save parameters
#     os.makedirs("shares", exist_ok=True)
#     image_share_dir = os.path.join("shares", f"paper_compliant_k{k}_n{n}_{image_label}")
#     os.makedirs(image_share_dir, exist_ok=True)
    
#     with open(os.path.join(image_share_dir, "parameters.txt"), "w") as f:
#         f.write(f"k={k}, n={n}\n")
#         f.write(f"m'={m_prime}, alpha'={alpha_prime:.6f}, r'={r_prime}\n")
#         f.write(f"Base m={m}, l={l}\n")
    
#     # Save shares
#     for i in range(n):
#         filename = os.path.join(image_share_dir, f"share_{i+1}.png")
#         save_share(shares[i], filename)
    
#     messagebox.showinfo("Success", 
#                        f"Paper-compliant shares generated\nm'={m_prime}, alpha'={alpha_prime:.4f}")

# def share_construction():
#     """Handle the share construction process through GUI."""
#     file_path = filedialog.askopenfilename(title="Select an image", 
#                                          filetypes=[("Image files", "*.jpeg"), ("Image files", "*.png")])
#     if not file_path:
#         return

#     image_label = os.path.splitext(os.path.basename(file_path))[0]
#     k = simpledialog.askinteger("Input", "Enter minimum shares for reconstruction (k):")
#     n = simpledialog.askinteger("Input", "Enter total shares to generate (n):")

#     if not k or not n:
#         return

#     binary_image = binary_image_from_path(file_path)
    
#     # Keeping original function call
#     # construct_shares_k_out_n(binary_image, k, n, image_label)
    
#     # Adding new paper-compliant option
#     # if messagebox.askyesno("Construction Method", 
#     #                       "Use paper-compliant construction? (Required for theoretical guarantees)"):
#     construct_shares_paper_compliant(binary_image, k, n, image_label)



# # import os
# # import numpy as np
# # from tkinter import filedialog, messagebox, simpledialog
# # from PIL import Image
# # import random
# # from itertools import combinations, product
# # from math import factorial, log, log2, sqrt, exp, pi

# # def binary_image_from_path(image_path, threshold=128):
# #     """Convert an image to a binary image."""
# #     image = Image.open(image_path).convert("L")  # Convert to grayscale
# #     binary_image = np.array(image) > threshold  # Convert to binary
# #     return binary_image.astype(int)

# # def generate_subsets(k):
# #     """Generate all subsets of even and odd cardinality."""
# #     elements = list(range(k))
# #     even_subsets = [set(comb) for r in range(0, k + 1, 2) for comb in combinations(elements, r)]
# #     odd_subsets = [set(comb) for r in range(1, k + 1, 2) for comb in combinations(elements, r)]
# #     return even_subsets, odd_subsets

# # def construct_matrices(k):
# #     """Construct C0 and C1 matrices based on even and odd subsets.
# #     This follows Construction 2 from the paper (optimal k-out-k scheme)."""
# #     even_subsets, odd_subsets = generate_subsets(k)
# #     num_columns = len(even_subsets)  # = 2^(k-1)
# #     C0 = np.zeros((k, num_columns), dtype=int)
# #     C1 = np.zeros((k, num_columns), dtype=int)
    
# #     for i in range(k):
# #         for j, subset in enumerate(even_subsets):
# #             if i in subset:
# #                 C0[i, j] = 1
# #         for j, subset in enumerate(odd_subsets):
# #             if i in subset:
# #                 C1[i, j] = 1
# #     return C0, C1


# # def save_share(share, filename):
# #     """Save a share as an image, converting it to uint8 format."""
# #     share = (share * 255).astype(np.uint8)
# #     img = Image.fromarray(share)
# #     img.save(filename)


# # import mmh3  # MurmurHash for universal hashing

# # import mmh3
# # import numpy as np
# # import math

# # def generate_hash_family_theorem7(n, k):
# #     """Generates a hash family of size l = O(log n * 2^{O(k log k)})"""
# #     # Calculate l as integer
# #     log_n = math.ceil(math.log2(n)) if n > 1 else 1
# #     exponent = k * math.ceil(math.log2(k)) if k > 1 else 1
# #     l = log_n * (2 ** exponent)
    
# #     hashes = []
# #     for seed in range(l):
# #         # Create closure to capture the seed value properly
# #         def make_hash(s):
# #             return lambda x: (mmh3.hash(str(x), s) % k)
# #         hashes.append(make_hash(seed))
# #     return hashes

# # def calculate_theorem7_parameters(k, n):
# #     """Calculates parameters for Theorem 7 scheme"""
# #     m_base = 2 ** (k-1)  # From Construction 2
# #     log_n = math.ceil(math.log2(n)) if n > 1 else 1
# #     exponent = k * math.ceil(math.log2(k)) if k > 1 else 1
# #     l = log_n * (2 ** exponent)
# #     m = m_base * l
# #     alpha = 2 ** (-k)  # 2^{-Ω(k)}
# #     r = math.factorial(m)
# #     return m, alpha, r

# # def construct_shares_paper_compliant(image, k, n, image_label):
# #     """Strict implementation following paper's construction"""
# #     height, width = image.shape
# #     C0, C1 = construct_matrices(k)
# #     m = C0.shape[1]  # = 2^{k-1}
    
# #     H = generate_hash_family_theorem7(n, k)
# #     l = len(H)
    
# #     m_prime, alpha_prime, r_prime = calculate_theorem7_parameters(k, n)
    
# #     # Initialize shares (n x height x (width*m_prime))
# #     shares = np.zeros((n, height, width * m_prime), dtype=np.uint8)
    
# #     for y in range(height):
# #         for x in range(width):
# #             pixel = image[y, x]
# #             base_matrix = C0 if pixel == 0 else C1
            
# #             for h_idx, h in enumerate(H):
# #                 for subpixel in range(m):
# #                     col = h_idx * m + subpixel
# #                     for participant in range(n):
# #                         row = h(participant)  # Call the hash function
# #                         shares[participant, y, x * m_prime + col] = base_matrix[row, subpixel]

    
# #     # Save parameters
# #     os.makedirs("shares", exist_ok=True)
# #     image_share_dir = os.path.join("shares", f"paper_compliant_k{k}_n{n}_{image_label}")
# #     os.makedirs(image_share_dir, exist_ok=True)
    
# #     with open(os.path.join(image_share_dir, "parameters.txt"), "w") as f:
# #         f.write(f"k={k}, n={n}\n")
# #         f.write(f"m'={m_prime}, alpha'={alpha_prime:.6f}, r'={r_prime}\n")
# #         f.write(f"Base m={m}, l={l}\n")
    
# #     # Save shares
# #     for i in range(n):
# #         filename = os.path.join(image_share_dir, f"share_{i+1}.png")
# #         save_share(shares[i], filename)
    
# #     messagebox.showinfo("Success", 
# #                        f"Paper-compliant shares generated\nm'={m_prime}, alpha'={alpha_prime:.4f}")

# # def share_construction():
# #     """Handle the share construction process through GUI."""
# #     file_path = filedialog.askopenfilename(title="Select an image", 
# #                                          filetypes=[("Image files", "*.jpeg"), ("Image files", "*.png")])
# #     if not file_path:
# #         return

# #     image_label = os.path.splitext(os.path.basename(file_path))[0]
# #     k = simpledialog.askinteger("Input", "Enter minimum shares for reconstruction (k):")
# #     n = simpledialog.askinteger("Input", "Enter total shares to generate (n):")

# #     if not k or not n:
# #         return

# #     binary_image = binary_image_from_path(file_path)
    
    
# #     construct_shares_paper_compliant(binary_image, k, n, image_label)


from PIL import Image, ImageDraw, ImageFont
import random
import string

def generate_bw_captcha(width=200, height=80, length=6):
    # Create a blank black and white image
    image = Image.new('1', (width, height), color=1)  # 1 for white background
    draw = ImageDraw.Draw(image)
    
    # Generate random text (uppercase letters and digits)
    characters = string.ascii_uppercase + string.digits
    captcha_text = ''.join(random.choice(characters) for _ in range(length))
    
    try:
        # Try to use a built-in font
        font = ImageFont.load_default()
        # For better results, you can specify a font file:
        # font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    # Calculate text size using getbbox (new method)
    bbox = draw.textbbox((0, 0), captcha_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Draw the text in black
    draw.text((x, y), captcha_text, font=font, fill=0)  # 0 for black
    
    # Add some noise (random pixels)
    for _ in range(int(width * height * 0.02)):  # 2% noise
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        draw.point((x, y), fill=random.choice([0, 1]))
    
    # Add some random lines
    for _ in range(3):
        x1 = random.randint(0, width-1)
        y1 = random.randint(0, height-1)
        x2 = random.randint(0, width-1)
        y2 = random.randint(0, height-1)
        draw.line((x1, y1, x2, y2), fill=0, width=1)
    
    return image, captcha_text

# Generate and save the CAPTCHA
if __name__ == "__main__":
    captcha_image, captcha_text = generate_bw_captcha()
    print(f"Generated CAPTCHA text: {captcha_text}")
    captcha_image.save("bw_captcha.png")
    captcha_image.show()
