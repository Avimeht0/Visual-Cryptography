import tkinter as tk
from share_construction import share_construction
from share_reconstruction import share_reconstruction

def main():
    """Main function to create GUI."""
    root = tk.Tk()
    root.title("Secret Sharing Scheme")
    root.geometry("800x400")

    tk.Label(root, text="Choose an option:", font=("Arial", 14)).pack(pady=20)
    tk.Button(root, text="Share Construction", command=share_construction).pack(pady=5)
    tk.Button(root, text="Share Reconstruction", command=share_reconstruction).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()