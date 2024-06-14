import os # Function that says where you are in life, and don't move this anywhere else
import subprocess
import tkinter as tk # Fuction that calls for dominos pizza
from tkinter import filedialog, ttk
from PIL import Image, ImageTk # Function that calls the feds on a criminal XD jk


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
    image = image.resize((300, 300))  # Resize image as needed
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
def save_text(text_path, new_text):
    with open(text_path, 'a') as file:
        file.write(new_text + '\n')

# Function to handle adding text to file
def add_text():
    new_text = entry_text.get()
    save_text(current_text_file, new_text)
    load_text(current_text_file)

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

# Define colors for different themes
themes = {
    "Beetlejuice Inspired": {
        "bg": "purple",
        "fg": "lime",
        "text_bg": "black",
        "text_fg": "lime",
        "entry_bg": "black",
        "entry_fg": "lime",
        "button_bg": "black",
        "button_fg": "lime",
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
    button_add_start.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
    button_add_end.configure(bg=current_theme["button_bg"], fg=current_theme["button_fg"])
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

# Image display area
image_label = tk.Label(root, bg=current_theme["bg"], fg=current_theme["fg"])
image_label.pack(pady=10)

# Text display and entry area
text_frame = tk.Frame(root, bg=current_theme["bg"])
text_frame.pack(pady=10)

text_label = tk.Label(text_frame, text="Text:", bg=current_theme["bg"], fg=current_theme["fg"])
text_label.grid(row=0, column=0, padx=10)

text_box = tk.Text(text_frame, width=40, height=10, bg=current_theme["text_bg"], fg=current_theme["text_fg"])
text_box.grid(row=0, column=1, padx=10)

# Entry for adding new text
entry_text = tk.Entry(root, width=50, bg=current_theme["entry_bg"], fg=current_theme["entry_fg"])
entry_text.pack(pady=10)

# Buttons for actions
button_select = tk.Button(root, text="Select Image", command=select_image, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_select.pack(pady=5)

button_add_start = tk.Button(root, text="Add to Start", command=add_text, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_add_start.pack(pady=5)

button_add_end = tk.Button(root, text="Add to End", command=add_text, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_add_end.pack(pady=5)

# Toggle theme button
button_toggle_theme = tk.Button(root, text="Toggle Theme", command=change_theme, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
button_toggle_theme.pack(pady=5)

# Close button
def close_app():
    root.destroy()

close_button = tk.Button(root, text="Close", command=close_app, bg=current_theme["button_bg"], fg=current_theme["button_fg"])
close_button.pack(pady=5)

# Theme selection combobox
theme_combobox = ttk.Combobox(root, values=list(themes.keys()), state="readonly")
theme_combobox.current(2)  # Default selection: Light Theme
theme_combobox.bind("<<ComboboxSelected>>", change_theme)
theme_combobox.pack(pady=5)

# Listbox to display images in current directory
file_listbox = tk.Listbox(root, selectmode=tk.SINGLE, bg=current_theme["bg"], fg=current_theme["fg"])
file_listbox.pack(pady=10)

# Function to update file listbox with images in current directory
def update_image_list():
    file_listbox.delete(0, tk.END)
    images = list_images_in_directory()
    for image in images:
        file_listbox.insert(tk.END, image)

update_image_list()

# Run the GUI
root.mainloop()
