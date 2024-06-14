import subprocess
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

# Function to install required packages
def install_packages():
    packages = ['pillow', 'numpy', 'matplotlib', 'tkinter']
    for package in packages:
        try:
            subprocess.check_call(['pip', 'install', package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

# Install required packages if not already installed
install_packages()

# Function to load and display image
def load_image(image_path):
    image = Image.open(image_path)
    image = image.resize((400, 300))  # Resize image as needed
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo  # Keep reference to avoid garbage collection

# Function to load and display text from file
def load_text(text_path):
    with open(text_path, 'r') as file:
        text = file.read()
    text_box.delete('1.0', tk.END)  # Clear previous text
    text_box.insert(tk.END, text)

# Function to save edited text to file
def save_text(text_path):
    new_text = text_box.get('1.0', tk.END)
    with open(text_path, 'w') as file:
        file.write(new_text)

# Function to handle selecting an image and associated text
def select_image(event=None):
    global current_image_path, current_text_file
    image_path = file_listbox.get(tk.ACTIVE)
    if image_path:
        current_image_path = image_path
        current_text_file = os.path.splitext(image_path)[0] + '.txt'  # Use os.path here
        load_image(image_path)
        load_text_if_available(os.path.splitext(image_path)[0])

# Function to load text if available
def load_text_if_available(base_filename):
    # Check current directory for text file with matching base filename
    text_file = base_filename + '.txt'
    if os.path.exists(text_file):
        load_text(text_file)
    else:
        text_box.delete('1.0', tk.END)  # Clear text box if no matching text file

# Function to list all image files in the current directory
def list_images_in_directory():
    images = []
    for file in os.listdir():
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            images.append(file)
    return images

# Function to list all text files in the current directory
def list_text_files_in_directory():
    text_files = []
    for file in os.listdir():
        if file.lower().endswith('.txt'):
            text_files.append(file)
    return text_files

# Create main window
root = tk.Tk()
root.title("Image Text Editor")
root.geometry("800x600")  # Set initial window size

# Define colors for different themes
themes = {
    "Beetlejuice Inspired": {
        "bg": "#202020",   # Dark gray background
        "fg": "#80FF00",   # Bright green foreground
        "text_bg": "#303030",  # Slightly lighter gray for text background
        "text_fg": "#80FF00",  # Bright green for text foreground
        "entry_bg": "#303030",  # Same as text background
        "entry_fg": "#80FF00",  # Same as text foreground
        "button_bg": "#303030",  # Same as text background
        "button_fg": "#80FF00",  # Same as text foreground
    },
    "Dark Theme": {
        "bg": "black",
        "fg": "white",
        "text_bg": "grey",
        "text_fg": "white",
        "entry_bg": "grey",
        "entry_fg": "white",
        "button_bg": "darkgrey",
        "button_fg": "white",
    },
    "Light Theme": {
        "bg": "white",
        "fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "entry_bg": "white",
        "entry_fg": "black",
        "button_bg": "lightgrey",
        "button_fg": "black",
    },
    "Windows XP Inspired": {
        "bg": "lightblue",
        "fg": "black",
        "text_bg": "lightblue",
        "text_fg": "black",
        "entry_bg": "lightblue",
        "entry_fg": "black",
        "button_bg": "lightgrey",
        "button_fg": "black",
    },
}

current_theme = themes["Light Theme"]  # Start with Light Theme

# Function to apply current theme colors to widgets
def apply_theme():
    root.configure(bg=current_theme["bg"])
    image_label.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    text_label.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    text_box.configure(bg=current_theme["text_bg"], fg=current_theme["text_fg"])
    entry_text.configure(bg=current_theme["entry_bg"], fg=current_theme["entry_fg"])
    button_select.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    button_save.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    button_toggle_theme.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    file_listbox.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    text_file_listbox.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    close_button.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])

# Function to change theme
def change_theme(event=None):
    global current_theme
    selected_theme = theme_combobox.get()
    current_theme = themes[selected_theme]
    apply_theme()

    # Adjust button text colors based on theme
    button_select.configure(fg=current_theme["button_fg"])
    button_save.configure(fg=current_theme["button_fg"])
    button_toggle_theme.configure(fg=current_theme["button_fg"])
    close_button.configure(fg=current_theme["button_fg"])

    # Update listbox colors if needed
    file_listbox.configure(bg=current_theme["bg"], fg=current_theme["fg"])
    text_file_listbox.configure(bg=current_theme["bg"], fg=current_theme["fg"])

# Image display area
image_label = tk.Label(root, bg=current_theme["bg"], fg=current_theme["fg"])
image_label.pack(pady=10)

# Text display and entry area
text_frame = tk.Frame(root, bg=current_theme["bg"])
text_frame.pack(pady=10)

text_label = tk.Label(text_frame, text="Text:", bg=current_theme["bg"], fg=current_theme["fg"])
text_label.grid(row=0, column=0, padx=10)

text_box = tk.Text(text_frame, width=60, height=10, bg=current_theme["text_bg"], fg=current_theme["text_fg"])
text_box.grid(row=0, column=1, padx=10)

# Save button
button_save = tk.Button(root, text="Save", command=lambda: save_text(current_text_file), bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_save.pack(pady=5)

# Button to select image
button_select = tk.Button(root, text="Select Image", command=select_image, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_select.pack(pady=5)

# Toggle theme button
button_toggle_theme = tk.Button(root, text="Toggle Theme", command=change_theme, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_toggle_theme.pack(pady=5)

# Close button
def close():
    root.destroy()

# Run the GUI
root.mainloop()
