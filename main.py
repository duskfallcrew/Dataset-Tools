import subprocess
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

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
def select_image():
    global current_image_path, current_text_file
    image_path = filedialog.askopenfilename(title="Select Image File",
                                            filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
    if image_path:
        current_image_path = image_path
        current_text_file = os.path.splitext(image_path)[0] + '.txt'
        load_image(image_path)
        load_text(current_text_file)

# Create main window
root = tk.Tk()
root.title("Image Text Editor")

# Image display area
image_label = tk.Label(root)
image_label.pack(pady=10)

# Text display and entry area
text_frame = tk.Frame(root)
text_frame.pack(pady=10)

text_label = tk.Label(text_frame, text="Text:")
text_label.grid(row=0, column=0, padx=10)

text_box = tk.Text(text_frame, width=40, height=10)
text_box.grid(row=0, column=1, padx=10)

# Entry for adding new text
entry_text = tk.Entry(root, width=50)
entry_text.pack(pady=10)

# Buttons for actions
button_select = tk.Button(root, text="Select Image", command=select_image)
button_select.pack(pady=5)

button_add_start = tk.Button(root, text="Add to Start", command=add_text)
button_add_start.pack(pady=5)

button_add_end = tk.Button(root, text="Add to End", command=add_text)
button_add_end.pack(pady=5)

# Run the GUI
root.mainloop()
