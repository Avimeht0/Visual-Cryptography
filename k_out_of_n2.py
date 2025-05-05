# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image
# import os
# from itertools import combinations
# import random 
# import tkinter as tk
# from tkinter import filedialog, messagebox, simpledialog

# # Fix for Matplotlib GTK errors
# import matplotlib
# matplotlib.use("TkAgg")

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
#     """Construct C0 and C1 matrices based on even and odd subsets."""
#     even_subsets, odd_subsets = generate_subsets(k)
#     num_columns = len(even_subsets)
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

# def generate_random_functions(n, k):
#     """Generate a collection of random functions mapping {1..n} -> {1..k}."""
#     return [lambda x, k=k: random.randint(0, k - 1) for _ in range(n * k)]

# def save_share(share, filename):
#     """Save a share as an image, converting it to uint8 format."""
#     share = (share * 255).astype(np.uint8)  # Convert binary to grayscale and ensure uint8 format
#     img = Image.fromarray(share)
#     img.save(filename)

# def construct_shares_k_out_n(image, k, n, image_label):
#     """Generate and save shares."""
#     height, width = image.shape
#     C0, C1 = construct_matrices(k)
#     num_subpixels = C0.shape[1]
#     shares = np.zeros((n, height, width * num_subpixels), dtype=int)
#     H = generate_random_functions(n, k)

#     for i in range(height):
#         for j in range(width):
#             pixel = image[i, j]
#             subpixel_pattern = C0 if pixel == 0 else C1
#             permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
#             for participant in range(n):
#                 h = H[random.randint(0, len(H) - 1)]
#                 row_index = h(participant)
#                 shares[participant, i, j * num_subpixels: (j + 1) * num_subpixels] = permuted_pattern[row_index]

#     # Create the main shares directory if it doesn't exist
#     os.makedirs("shares", exist_ok=True)
    
#     # Create a subdirectory named after the image label inside the shares directory
#     image_share_dir = os.path.join("shares", image_label)
#     os.makedirs(image_share_dir, exist_ok=True)
    
#     # Save each share in the image-specific directory
#     for i in range(n):
#         filename = os.path.join(image_share_dir, f"{image_label}_Share_{i + 1}.png")
#         save_share(shares[i], filename)
    
#     messagebox.showinfo("Success", "Shares generated successfully!")


# def reconstruct_image(selected_shares):
#     """Reconstruct the image from selected shares, simulating physical stacking."""
#     height, full_width = selected_shares[0].shape
#     num_subpixels = full_width // selected_shares[0].shape[1]
#     width = full_width // num_subpixels
#     reconstructed = np.zeros((height, width), dtype=int)

#     for i in range(height):
#         for j in range(width):
#             stacked_subpixels = np.zeros(num_subpixels, dtype=int)
#             for share in selected_shares:
#                 stacked_subpixels = np.logical_or(stacked_subpixels, share[i, j * num_subpixels: (j + 1) * num_subpixels])
#             reconstructed[i, j] = 1 if np.any(stacked_subpixels) else 0  # Black if at least one subpixel is black

#     return reconstructed


# def display_image(image, title):
#     """Display an image."""
#     plt.imshow(image, cmap="gray")
#     plt.title(title)
#     plt.axis("off")
#     plt.show()

# def share_construction():
#     """Handle the share construction process through GUI."""
#     file_path = filedialog.askopenfilename(title="Select an image", filetypes=[("Image files", "*.jpeg"),("Image files", "*.png")])
#     if not file_path:
#         return

#     image_label = os.path.splitext(os.path.basename(file_path))[0]
#     k = simpledialog.askinteger("Input", "Enter the minimum number of shares required for reconstruction (k):")
#     n = simpledialog.askinteger("Input", "Enter the total number of shares to generate (n):")

#     if not k or not n:
#         return

#     binary_image = binary_image_from_path(file_path)
#     construct_shares_k_out_n(binary_image, k, n, image_label)



# def share_reconstruction():
#     """Handle the share reconstruction process through GUI."""
#     k = simpledialog.askinteger("Input", "Enter the number of shares you want to use for reconstruction (k):")
#     if not k:
#         return

#     # Step 1: Select directory
#     directory = filedialog.askdirectory(title="Select Directory Containing PNG Shares")
#     if not directory:
#         return

#     # Step 2: List PNG and JPG files
#     files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
#     if len(files) < k:
#         messagebox.showerror("Error", f"Not enough PNG or JPG files. Found: {len(files)}")
#         return
#     # Step 3: Listbox window for share selection
#     selection_window = tk.Tk()
#     selection_window.title("Select Shares")

#     listbox = tk.Listbox(selection_window, selectmode=tk.MULTIPLE, width=50, height=15)
#     for file in files:
#         listbox.insert(tk.END, file)
#     listbox.pack(padx=10, pady=10)

#     def confirm_selection():
#         selected_indices = listbox.curselection()
#         selected_files = [os.path.join(directory, files[i]) for i in selected_indices]

#         print(f"Selected files: {selected_files}")  # Debugging output

#         if len(selected_files) == k:
#             selection_window.destroy()
#             try:
#                 selected_shares = [np.array(Image.open(f).convert("L")) > 128 for f in selected_files]
#                 selected_shares = [share.astype(int) for share in selected_shares]
#                 reconstructed_image = reconstruct_image(selected_shares)
                
#                 # Step 4: Save the reconstructed image in the same directory
#                 reconstructed_image_path = os.path.join(directory, "reconstructed_image.png")
                
#                 # Convert reconstructed image to a PIL image and save it
#                 reconstructed_image_pil = Image.fromarray((reconstructed_image * 255).astype(np.uint8))
#                 reconstructed_image_pil.save(reconstructed_image_path)

#                 # Show success message with the path of the saved image
#                 messagebox.showinfo("Success", f"Reconstructed image saved at:\n{reconstructed_image_path}")

#                 # Optionally, display the reconstructed image
#                 display_image(reconstructed_image, "Reconstructed Image")
#             except Exception as e:
#                 messagebox.showerror("Error", f"Failed to process images: {e}")
#         else:
#             messagebox.showwarning("Warning", f"Please select exactly {k} shares. Currently selected: {len(selected_files)}.")

#     confirm_btn = tk.Button(selection_window, text="Confirm Selection", command=confirm_selection)
#     confirm_btn.pack(pady=5)

#     selection_window.mainloop()


# def main():
#     """Main function to create GUI."""
#     root = tk.Tk()
#     root.title("Secret Sharing Scheme")
#     root.geometry("400x200")

#     tk.Label(root, text="Choose an option:", font=("Arial", 14)).pack(pady=20)
#     tk.Button(root, text="Share Construction", command=share_construction).pack(pady=5)
#     tk.Button(root, text="Share Reconstruction", command=share_reconstruction).pack(pady=5)
#     tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

#     root.mainloop()

# if __name__ == "__main__":
#     main()

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.image import Image as KivyImage
import os
import numpy as np
from PIL import Image
from itertools import combinations
import random

class SecretSharingApp(App):
    def build(self):
        self.title = "Secret Sharing Scheme"
        Window.size = (400, 600)
        
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.title_label = Label(text="Secret Sharing Scheme", font_size=24, size_hint=(1, 0.2))
        self.main_layout.add_widget(self.title_label)
        
        self.construction_btn = Button(text="Share Construction", size_hint=(1, 0.2))
        self.construction_btn.bind(on_press=self.show_construction)
        self.main_layout.add_widget(self.construction_btn)
        
        self.reconstruction_btn = Button(text="Share Reconstruction", size_hint=(1, 0.2))
        self.reconstruction_btn.bind(on_press=self.show_reconstruction)
        self.main_layout.add_widget(self.reconstruction_btn)
        
        return self.main_layout
    
    def show_construction(self, instance):
        self.clear_main_layout()
        
        back_btn = Button(text="Back", size_hint=(1, 0.1))
        back_btn.bind(on_press=self.back_to_main)
        self.main_layout.add_widget(back_btn)
        
        self.select_image_btn = Button(text="Select Image", size_hint=(1, 0.2))
        self.select_image_btn.bind(on_press=self.open_file_chooser)
        self.main_layout.add_widget(self.select_image_btn)
        
        self.k_input = TextInput(hint_text="Minimum shares for reconstruction (k)", size_hint=(1, 0.1))
        self.main_layout.add_widget(self.k_input)
        
        self.n_input = TextInput(hint_text="Total shares to generate (n)", size_hint=(1, 0.1))
        self.main_layout.add_widget(self.n_input)
        
        self.generate_btn = Button(text="Generate Shares", size_hint=(1, 0.2))
        self.generate_btn.bind(on_press=self.generate_shares)
        self.main_layout.add_widget(self.generate_btn)
        
    def show_reconstruction(self, instance):
        self.clear_main_layout()
        
        back_btn = Button(text="Back", size_hint=(1, 0.1))
        back_btn.bind(on_press=self.back_to_main)
        self.main_layout.add_widget(back_btn)
        
        self.k_recon_input = TextInput(hint_text="Number of shares for reconstruction (k)", size_hint=(1, 0.1))
        self.main_layout.add_widget(self.k_recon_input)
        
        self.select_shares_btn = Button(text="Select Shares Directory", size_hint=(1, 0.2))
        self.select_shares_btn.bind(on_press=self.open_dir_chooser)
        self.main_layout.add_widget(self.select_shares_btn)
        
        self.shares_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.shares_list.bind(minimum_height=self.shares_list.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 0.5))
        scroll.add_widget(self.shares_list)
        self.main_layout.add_widget(scroll)
        
        self.reconstruct_btn = Button(text="Reconstruct Image", size_hint=(1, 0.2))
        self.reconstruct_btn.bind(on_press=self.reconstruct_image)
        self.main_layout.add_widget(self.reconstruct_btn)
    
    def clear_main_layout(self):
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(Label(text="Secret Sharing Scheme", font_size=24, size_hint=(1, 0.2)))
    
    def back_to_main(self, instance):
        self.clear_main_layout()
        
        self.construction_btn = Button(text="Share Construction", size_hint=(1, 0.2))
        self.construction_btn.bind(on_press=self.show_construction)
        self.main_layout.add_widget(self.construction_btn)
        
        self.reconstruction_btn = Button(text="Share Reconstruction", size_hint=(1, 0.2))
        self.reconstruction_btn.bind(on_press=self.show_reconstruction)
        self.main_layout.add_widget(self.reconstruction_btn)
    
    def open_file_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(filters=["*.png", "*.jpg", "*.jpeg"])
        content.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint=(1, 0.2))
        select_btn = Button(text="Select")
        cancel_btn = Button(text="Cancel")
        
        def select(instance):
            if file_chooser.selection:
                self.selected_image_path = file_chooser.selection[0]
                self.select_image_btn.text = f"Selected: {os.path.basename(self.selected_image_path)}"
            popup.dismiss()
        
        select_btn.bind(on_press=select)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Select Image", content=content, size_hint=(0.9, 0.9))
        popup.open()
    
    def open_dir_chooser(self, instance):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView()
        content.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint=(1, 0.2))
        select_btn = Button(text="Select")
        cancel_btn = Button(text="Cancel")
        
        def select(instance):
            if file_chooser.path:
                self.shares_dir = file_chooser.path
                self.load_share_files()
                self.select_shares_btn.text = f"Selected: {os.path.basename(self.shares_dir)}"
            popup.dismiss()
        
        select_btn.bind(on_press=select)
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title="Select Shares Directory", content=content, size_hint=(0.9, 0.9))
        popup.open()
    
    def load_share_files(self):
        self.shares_list.clear_widgets()
        self.share_files = []
        self.selected_shares = []
        
        if hasattr(self, 'shares_dir'):
            for f in os.listdir(self.shares_dir):
                if f.lower().endswith('.png'):
                    full_path = os.path.join(self.shares_dir, f)
                    self.share_files.append(full_path)
                    
                    item = BoxLayout(size_hint_y=None, height=40)
                    cb = CheckBox(size_hint=(0.2, 1))
                    cb.bind(active=lambda instance, value, path=full_path: self.toggle_share(path, value))
                    item.add_widget(cb)
                    item.add_widget(Label(text=f, size_hint=(0.8, 1)))
                    self.shares_list.add_widget(item)
    
    def toggle_share(self, path, is_active):
        if is_active:
            if path not in self.selected_shares:
                self.selected_shares.append(path)
        else:
            if path in self.selected_shares:
                self.selected_shares.remove(path)
    
    def generate_shares(self, instance):
        try:
            k = int(self.k_input.text)
            n = int(self.n_input.text)
            
            if not hasattr(self, 'selected_image_path'):
                self.show_message("Error", "Please select an image first")
                return
                
            binary_image = self.binary_image_from_path(self.selected_image_path)
            image_label = os.path.splitext(os.path.basename(self.selected_image_path))[0]
            
            # Create shares directory structure like original code
            shares_dir = os.path.join(os.getcwd(), "shares")
            os.makedirs(shares_dir, exist_ok=True)
            
            # Create image-specific subdirectory
            image_share_dir = os.path.join(shares_dir, image_label)
            os.makedirs(image_share_dir, exist_ok=True)
            
            # Generate and save shares
            self.construct_shares_k_out_n(binary_image, k, n, image_share_dir, image_label)
            
            self.show_message("Success", f"Shares generated successfully in:\n{image_share_dir}")
            
        except ValueError:
            self.show_message("Error", "Please enter valid numbers for k and n")
        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")
    
    def reconstruct_image(self, instance):
        try:
            k = int(self.k_recon_input.text)
            
            if not hasattr(self, 'selected_shares') or len(self.selected_shares) < k:
                self.show_message("Error", f"Please select at least {k} shares")
                return
                
            if len(self.selected_shares) > k:
                self.show_message("Warning", f"Using first {k} of {len(self.selected_shares)} selected shares")
            
            selected_shares = [np.array(Image.open(f).convert("L")) > 128 for f in self.selected_shares[:k]]
            selected_shares = [share.astype(int) for share in selected_shares]
            
            reconstructed_image = self.reconstruct_image_from_shares(selected_shares)
            
            # Save the reconstructed image in the shares directory
            reconstructed_image_path = os.path.join(self.shares_dir, "reconstructed_image.png")
            reconstructed_image_pil = Image.fromarray((reconstructed_image * 255).astype(np.uint8))
            reconstructed_image_pil.save(reconstructed_image_path)
            
            # Display the image
            self.display_reconstructed_image(reconstructed_image)
            
            self.show_message("Success", f"Reconstructed image saved at:\n{reconstructed_image_path}")
            
        except ValueError:
            self.show_message("Error", "Please enter a valid number for k")
        except Exception as e:
            self.show_message("Error", f"An error occurred: {str(e)}")
    
    def display_reconstructed_image(self, image):
        buf = (image * 255).astype(np.uint8).tobytes()
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='luminance')
        texture.blit_buffer(buf, colorfmt='luminance', bufferfmt='ubyte')
        
        content = BoxLayout(orientation='vertical')
        img_widget = KivyImage(texture=texture)
        content.add_widget(img_widget)
        
        close_btn = Button(text="Close", size_hint=(1, 0.1))
        content.add_widget(close_btn)
        
        popup = Popup(title="Reconstructed Image", content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))
        
        ok_btn = Button(text="OK", size_hint=(1, 0.2))
        content.add_widget(ok_btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    # Secret Sharing Algorithm Functions
    
    def binary_image_from_path(self, image_path, threshold=128):
        """Convert an image to a binary image."""
        image = Image.open(image_path).convert("L")  # Convert to grayscale
        binary_image = np.array(image) > threshold  # Convert to binary
        return binary_image.astype(int)
    
    def generate_subsets(self, k):
        """Generate all subsets of even and odd cardinality."""
        elements = list(range(k))
        even_subsets = [set(comb) for r in range(0, k + 1, 2) for comb in combinations(elements, r)]
        odd_subsets = [set(comb) for r in range(1, k + 1, 2) for comb in combinations(elements, r)]
        return even_subsets, odd_subsets
    
    def construct_matrices(self, k):
        """Construct C0 and C1 matrices based on even and odd subsets."""
        even_subsets, odd_subsets = self.generate_subsets(k)
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
    
    def generate_random_functions(self, n, k):
        """Generate a collection of random functions mapping {1..n} -> {1..k}."""
        return [lambda x, k=k: random.randint(0, k - 1) for _ in range(n * k)]
    
    def save_share(self, share, filename):
        """Save a share as an image, converting it to uint8 format."""
        share = (share * 255).astype(np.uint8)  # Convert binary to grayscale and ensure uint8 format
        img = Image.fromarray(share)
        img.save(filename)
    
    def construct_shares_k_out_n(self, image, k, n, output_dir, image_label):
        """Generate and save shares with original file structure."""
        height, width = image.shape
        C0, C1 = self.construct_matrices(k)
        num_subpixels = C0.shape[1]
        shares = np.zeros((n, height, width * num_subpixels), dtype=int)
        H = self.generate_random_functions(n, k)
    
        for i in range(height):
            for j in range(width):
                pixel = image[i, j]
                subpixel_pattern = C0 if pixel == 0 else C1
                permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
                for participant in range(n):
                    h = H[random.randint(0, len(H) - 1)]
                    row_index = h(participant)
                    shares[participant, i, j * num_subpixels: (j + 1) * num_subpixels] = permuted_pattern[row_index]
        
        # Save each share in the specified directory
        for i in range(n):
            filename = os.path.join(output_dir, f"{image_label}_Share_{i + 1}.png")
            self.save_share(shares[i], filename)
    
    def reconstruct_image_from_shares(self, selected_shares):
        """Reconstruct the image from selected shares, simulating physical stacking."""
        height, full_width = selected_shares[0].shape
        num_subpixels = full_width // selected_shares[0].shape[1]
        width = full_width // num_subpixels
        reconstructed = np.zeros((height, width), dtype=int)
    
        for i in range(height):
            for j in range(width):
                stacked_subpixels = np.zeros(num_subpixels, dtype=int)
                for share in selected_shares:
                    stacked_subpixels = np.logical_or(stacked_subpixels, share[i, j * num_subpixels: (j + 1) * num_subpixels])
                reconstructed[i, j] = 1 if np.any(stacked_subpixels) else 0  # Black if at least one subpixel is black
    
        return reconstructed

if __name__ == '__main__':
    SecretSharingApp().run()