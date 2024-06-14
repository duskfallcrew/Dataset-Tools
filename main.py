import subprocess
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os

# Function to install required packages
def install_packages():
    packages = ['pillow', 'numpy', 'matplotlib']
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
def save_text():
    if current_text_file:
        new_text = text_box.get('1.0', tk.END)
        with open(current_text_file, 'w') as file:
            file.write(new_text)

# Function to handle selecting an image and associated text
def select_image(event=None):
    global current_image_path, current_text_file
    image_path = file_listbox.get(tk.ACTIVE)
    if image_path:
        current_image_path = image_path
        current_text_file = os.path.splitext(image_path)[0] + '.txt'
        load_image(image_path)
        load_text_if_available(os.path.splitext(image_path)[0])

# Function to load text if available
def load_text_if_available(base_filename):
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

# Function to close the application
def close():
    root.destroy()

# Create main window
root = tk.Tk()
root.title("Image Text Editor")
root.geometry("1200x900")  # Set initial window size

# Define colors for different themes
themes = {
    "Beetlejuice Inspired": {
        "bg": "#202020",
        "fg": "#80FF00",
        "text_bg": "#303030",
        "text_fg": "#80FF00",
        "button_bg": "#303030",
        "button_fg": "#80FF00",
    },
    "Dark Theme": {
        "bg": "black",
        "fg": "white",
        "text_bg": "grey",
        "text_fg": "white",
        "button_bg": "darkgrey",
        "button_fg": "white",
    },
    "Light Theme": {
        "bg": "white",
        "fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "button_bg": "lightgrey",
        "button_fg": "black",
    },
    "Windows XP Inspired": {
        "bg": "lightblue",
        "fg": "black",
        "text_bg": "lightblue",
        "text_fg": "black",
        "button_bg": "lightgrey",
        "button_fg": "black",
    },
    "Ocean Blue": {
        "bg": "#0077be",
        "fg": "white",
        "text_bg": "#004c80",
        "text_fg": "white",
        "button_bg": "#004c80",
        "button_fg": "white",
    },
    "Mint Green": {
        "bg": "#8dd3c7",
        "fg": "black",
        "text_bg": "#5ba78a",
        "text_fg": "black",
        "button_bg": "#5ba78a",
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
    button_select.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    button_save.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    button_toggle_theme.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
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
button_save = tk.Button(root, text="Save", command=save_text, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_save.pack(pady=5)

# Button to select image
button_select = tk.Button(root, text="Select Image", command=select_image, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_select.pack(pady=5)

# Toggle theme button
button_toggle_theme = tk.Button(root, text="Toggle Theme", command=change_theme, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_toggle_theme.pack(pady=5)

# Close button
close_button = tk.Button(root, text="Close", command=close, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
close_button.pack(pady=5)

# Function to populate listboxes with image and text files
def populate_listboxes():
    images = list_images_in_directory()
    text_files = list_text_files_in_directory()

    file_listbox.delete(0, tk.END)
    text_file_listbox.delete(0, tk.END)

    for image in images:
        file_listbox.insert(tk.END, image)

    for text_file in text_files:
        text_file_listbox.insert(tk.END, text_file)

# Listbox to display images
file_listbox = tk.Listbox(root, width=30, height=20, bg=current_theme["bg"], fg=current_theme["fg"])
file_listbox.pack(side=tk.LEFT, padx=10, pady=10)

# Listbox to display text files
text_file_listbox = tk.Listbox(root, width=30, height=20, bg=current_theme["bg"], fg=current_theme["fg"])
text_file_listbox.pack(side=tk.RIGHT, padx=10, pady=10)

# Populate listboxes with initial image and text files
populate_listboxes()

# Theme selection combobox
theme_combobox = ttk.Combobox(root, values=list(themes.keys()))
theme_combobox.current(2)  # Set default theme
theme_combobox.pack(pady=10)
theme_combobox.bind("<<ComboboxSelected>>", change_theme)

# Apply initial theme colors
apply_theme()

# Run the GUI
root.mainloop()
