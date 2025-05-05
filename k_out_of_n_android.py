import numpy as np
from PIL import Image
import os
from itertools import combinations
import random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image as KivyImage
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.metrics import dp
import io

class SelectableShareItem(BoxLayout):
    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        
        self.checkbox = CheckBox(size_hint=(0.2, 1))
        self.add_widget(self.checkbox)
        
        self.label = Label(text=filename, size_hint=(0.8, 1), halign='left')
        self.add_widget(self.label)
        
        self.filename = filename

class SecretSharingApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        self.title_label = Label(text="Secret Sharing Scheme", font_size=dp(24), size_hint=(1, None), height=dp(50))
        self.layout.add_widget(self.title_label)
        
        # Share Construction
        self.construct_btn = Button(text="Share Construction", size_hint=(1, None), height=dp(50))
        self.construct_btn.bind(on_press=self.show_construction_popup)
        self.layout.add_widget(self.construct_btn)
        
        # Share Reconstruction
        self.reconstruct_btn = Button(text="Share Reconstruction", size_hint=(1, None), height=dp(50))
        self.reconstruct_btn.bind(on_press=self.show_reconstruction_popup)
        self.layout.add_widget(self.reconstruct_btn)
        
        return self.layout
    
    def show_construction_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # File chooser
        self.file_chooser = FileChooserListView(filters=['*.png', '*.jpg', '*.jpeg'])
        self.file_chooser.bind(selection=self.show_selected_image)
        content.add_widget(self.file_chooser)
        
        # Image preview
        self.image_preview = KivyImage(size_hint=(1, None), height=dp(200))
        content.add_widget(self.image_preview)
        
        # Parameters
        params_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50))
        params_layout.add_widget(Label(text="k (min shares):", size_hint=(0.5, 1)))
        self.k_input = TextInput(text='2', input_filter='int', multiline=False, size_hint=(0.5, 1))
        params_layout.add_widget(self.k_input)
        
        params_layout.add_widget(Label(text="n (total shares):", size_hint=(0.5, 1)))
        self.n_input = TextInput(text='3', input_filter='int', multiline=False, size_hint=(0.5, 1))
        params_layout.add_widget(self.n_input)
        content.add_widget(params_layout)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50))
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Generate Shares")
        
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        confirm_btn.bind(on_press=self.generate_shares)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        self.popup = Popup(title="Share Construction", content=content, size_hint=(0.9, 0.9))
        self.popup.open()
    
    def show_selected_image(self, instance, value):
        if value:
            try:
                img_path = value[0]
                img = Image.open(img_path)
                img.thumbnail((400, 400))  # Resize for preview
                
                # Convert to texture
                buf = io.BytesIO()
                img.save(buf, format='png')
                buf.seek(0)
                
                texture = Texture.create(size=img.size, colorfmt='rgba')
                texture.blit_buffer(buf.read(), colorfmt='rgba', bufferfmt='ubyte')
                self.image_preview.texture = texture
            except Exception as e:
                print(f"Error loading image: {e}")

    def show_reconstruction_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Directory chooser
        self.dir_chooser = FileChooserListView(path=os.getcwd(), dirselect=True)
        self.dir_chooser.bind(selection=lambda x, y: self.refresh_shares_list())
        content.add_widget(self.dir_chooser)
        
        # Share selection area
        share_select_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(200))
        
        # Scrollable list of shares
        scroll = ScrollView()
        self.share_list = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.share_list.bind(minimum_height=self.share_list.setter('height'))
        scroll.add_widget(self.share_list)
        share_select_layout.add_widget(scroll)
        
        # Refresh button
        refresh_btn = Button(text="Refresh Shares List", size_hint=(1, None), height=dp(40))
        refresh_btn.bind(on_press=lambda x: self.refresh_shares_list())
        share_select_layout.add_widget(refresh_btn)
        
        content.add_widget(share_select_layout)
        
        # Parameters
        params_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50))
        params_layout.add_widget(Label(text="k (shares to use):", size_hint=(0.5, 1)))
        self.recon_k_input = TextInput(text='2', input_filter='int', multiline=False, size_hint=(0.5, 1))
        params_layout.add_widget(self.recon_k_input)
        content.add_widget(params_layout)
        
        # Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50))
        cancel_btn = Button(text="Cancel")
        confirm_btn = Button(text="Reconstruct Image")
        
        cancel_btn.bind(on_press=lambda x: self.popup.dismiss())
        confirm_btn.bind(on_press=self.reconstruct_image)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(confirm_btn)
        content.add_widget(btn_layout)
        
        self.popup = Popup(title="Share Reconstruction", content=content, size_hint=(0.9, 0.9))
        self.popup.open()
        Clock.schedule_once(lambda dt: self.refresh_shares_list(), 0.1)
    
    def refresh_shares_list(self, *args):
        self.share_list.clear_widgets()
        if hasattr(self, 'dir_chooser') and self.dir_chooser.path:
            directory = self.dir_chooser.path
            files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            for file in sorted(files):
                item = SelectableShareItem(file)
                self.share_list.add_widget(item)
    
    def get_selected_shares(self):
        selected = []
        if hasattr(self, 'share_list'):
            for child in self.share_list.children:
                if isinstance(child, SelectableShareItem) and child.checkbox.active:
                    selected.append(child.filename)
        return selected
    
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
        share = (share * 255).astype(np.uint8)
        img = Image.fromarray(share)
        img.save(filename)
    
    def generate_shares(self, instance):
        """Generate and save shares."""
        try:
            if not self.file_chooser.selection:
                self.show_message("Error", "Please select an image first")
                return
            
            file_path = self.file_chooser.selection[0]
            
            try:
                k = int(self.k_input.text)
                n = int(self.n_input.text)
            except ValueError:
                self.show_message("Error", "Please enter valid numbers for k and n")
                return
            
            if k <= 0 or n <= 0 or k > n:
                self.show_message("Error", "k must be positive and ≤ n")
                return
            
            # Create image-specific directory inside shares folder
            image_name = os.path.splitext(os.path.basename(file_path))[0]
            shares_dir = os.path.join(os.path.dirname(file_path), "shares", image_name)
            os.makedirs(shares_dir, exist_ok=True)
            
            binary_image = self.binary_image_from_path(file_path)
            height, width = binary_image.shape
            
            C0, C1 = self.construct_matrices(k)
            num_subpixels = C0.shape[1]
            shares = np.zeros((n, height, width * num_subpixels), dtype=int)
            H = self.generate_random_functions(n, k)
            
            for i in range(height):
                for j in range(width):
                    pixel = binary_image[i, j]
                    subpixel_pattern = C0 if pixel == 0 else C1
                    permuted_pattern = subpixel_pattern[:, np.random.permutation(num_subpixels)]
                    for participant in range(n):
                        h = H[random.randint(0, len(H) - 1)]
                        row_index = h(participant)
                        shares[participant, i, j * num_subpixels: (j + 1) * num_subpixels] = permuted_pattern[row_index]
            
            # Save shares in the image-specific directory
            for i in range(n):
                filename = os.path.join(shares_dir, f"{image_name}_Share_{i + 1}.png")
                self.save_share(shares[i], filename)
            
            self.show_message("Success", f"Shares generated in:\n{shares_dir}")
            self.popup.dismiss()
        except Exception as e:
            self.show_message("Error", f"Failed to generate shares: {str(e)}")
    
    def reconstruct_image(self, instance):
        """Handle the reconstruction process."""
        try:
            directory = self.dir_chooser.path
            selected_files = self.get_selected_shares()
            
            try:
                k = int(self.recon_k_input.text)
            except ValueError:
                self.show_message("Error", "Please enter a valid number for k")
                return
            
            if len(selected_files) < k:
                self.show_message("Error", f"You need at least {k} shares to reconstruct")
                return
            
            # Load the selected shares
            selected_paths = [os.path.join(directory, f) for f in selected_files[:k]]
            selected_shares = [np.array(Image.open(f).convert("L")) > 128 for f in selected_paths]
            selected_shares = [share.astype(int) for share in selected_shares]
            
            # Reconstruct using your preferred method
            reconstructed_image = self.reconstruct_image_from_shares(selected_shares)
            
            # Flip the image vertically to correct orientation
            reconstructed_image = np.flipud(reconstructed_image)
            
            # Save the reconstructed image in the same directory as the shares
            output_path = os.path.join(directory, "reconstructed.png")
            Image.fromarray((reconstructed_image * 255).astype(np.uint8)).save(output_path)
            
            # Show the reconstructed image
            self.show_reconstructed_image(reconstructed_image, output_path)
            
        except Exception as e:
            self.show_message("Error", f"Failed to reconstruct image: {str(e)}")

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

    def show_reconstructed_image(self, image, path):
        """Display the reconstructed image in a popup."""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Image display
        img_texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt='luminance')
        img_texture.blit_buffer((image * 255).astype(np.uint8).tobytes(), colorfmt='luminance', bufferfmt='ubyte')
        img_widget = KivyImage(texture=img_texture, size_hint=(1, 1))
        content.add_widget(img_widget)
        
        # Path label
        content.add_widget(Label(text=f"Saved to:\n{path}", size_hint=(1, None), height=dp(40)))
        
        # Close button
        close_btn = Button(text="Close", size_hint=(1, None), height=dp(40))
        popup = Popup(title="Reconstructed Image", content=content, size_hint=(0.9, 0.9))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        content.add_widget(Label(text=message, size_hint=(1, 1)))
        
        ok_btn = Button(text="OK", size_hint=(1, None), height=dp(40))
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.5))
        ok_btn.bind(on_press=popup.dismiss)
        content.add_widget(ok_btn)
        
        popup.open()

if __name__ == "__main__":
    SecretSharingApp().run()