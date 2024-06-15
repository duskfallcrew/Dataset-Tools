import os
import subprocess
import sys
import PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTextEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QComboBox, QListWidgetItem, QGridLayout
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from PIL import Image, ImageQt


# Function to install required packages
def install_packages():
    packages = ['pillow', 'numpy', 'matplotlib', 'PyQt6']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

# Install required packages if not already installed
install_packages()

# Main window class
class ImageTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Text Editor")
        self.setGeometry(100, 100, 1200, 900)

        self.current_theme = themes["Light Theme"]  # Start with Light Theme

        self.init_ui()
        self.populate_listboxes()
        self.populate_image_gallery()  # New: Populate image gallery
        self.apply_theme()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QHBoxLayout(central_widget)

        # Left side layout (image display and text entry)
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Image display area
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.image_label)

        # Text display and entry area
        self.text_label = QLabel("Text:")
        left_layout.addWidget(self.text_label)

        self.text_box = QTextEdit()
        left_layout.addWidget(self.text_box)

        # Save and Close buttons
        button_layout = QHBoxLayout()
        left_layout.addLayout(button_layout)

        self.button_save = QPushButton("Save", clicked=self.save_text)
        button_layout.addWidget(self.button_save)

        self.close_button = QPushButton("Close", clicked=self.close)
        button_layout.addWidget(self.close_button)

        # Right side layout (listboxes and theme selection)
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        # Listbox to display images
        self.file_listbox = QListWidget()
        right_layout.addWidget(self.file_listbox)

        # Listbox to display text files
        self.text_file_listbox = QListWidget()
        right_layout.addWidget(self.text_file_listbox)

        # Image gallery
        self.image_gallery = QListWidget()
        right_layout.addWidget(self.image_gallery)

        # Populate image gallery
        self.populate_image_gallery()

        # Theme selection combobox
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(list(themes.keys()))
        self.theme_combobox.setCurrentIndex(2)  # Set default theme
        self.theme_combobox.currentIndexChanged.connect(self.change_theme)
        right_layout.addWidget(self.theme_combobox)

    # Function to load and display image
    def load_image(self, image_path):
        image = Image.open(image_path)
        pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio
        ))

    # Function to load and display text from file
    def load_text(self, text_path):
        with open(text_path, 'r') as file:
            text = file.read()
        self.text_box.clear()  # Clear previous text
        self.text_box.append(text)

    # Function to save edited text to file
    def save_text(self):
        if self.current_text_file:
            new_text = self.text_box.toPlainText()
            with open(self.current_text_file, 'w') as file:
                file.write(new_text)

    # Function to handle selecting an image and associated text
    def select_image(self):
        image_path = self.file_listbox.currentItem().text()
        if image_path:
            self.current_image_path = image_path
            self.current_text_file = os.path.splitext(image_path)[0] + '.txt'
            self.load_image(image_path)
            self.load_text_if_available(os.path.splitext(image_path)[0])

    # Function to load text if available
    def load_text_if_available(self, base_filename):
        text_file = base_filename + '.txt'
        if os.path.exists(text_file):
            self.load_text(text_file)
        else:
            self.text_box.clear()  # Clear text box if no matching text file

    # Function to list all image files in the current directory
    def list_images_in_directory(self):
        images = []
        for file in os.listdir():
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                images.append(file)
        return images

    # Function to list all text files in the current directory
    def list_text_files_in_directory(self):
        text_files = []
        for file in os.listdir():
            if file.lower().endswith('.txt'):
                text_files.append(file)
        return text_files

    # Function to close the application
    def close(self):
        self.close()

    # Function to populate listboxes with image and text files
    def populate_listboxes(self):
        self.file_listbox.clear()
        self.text_file_listbox.clear()

        images = self.list_images_in_directory()
        text_files = self.list_text_files_in_directory()

        self.file_listbox.addItems(images)
        self.text_file_listbox.addItems(text_files)

    # Function to populate the image gallery
    def populate_image_gallery(self):
        self.image_gallery.clear()

        images = self.list_images_in_directory()
        for image in images:
            item = QListWidgetItem(QIcon(image), os.path.basename(image))
            self.image_gallery.addItem(item)

    # Function to apply current theme colors to widgets
    def apply_theme(self):
        style_sheet = f"""
            background-color: {self.current_theme["bg"]};
            color: {self.current_theme["fg"]};
        """
        self.setStyleSheet(style_sheet)

        self.image_label.setStyleSheet(style_sheet)
        self.text_label.setStyleSheet(style_sheet)
        self.text_box.setStyleSheet(f"""
            background-color: {self.current_theme["text_bg"]};
            color: {self.current_theme["text_fg"]};
        """)
        self.button_save.setStyleSheet(f"""
            background-color: {self.current_theme["button_bg"]};
            color: {self.current_theme["button_fg"]};
        """)
        self.close_button.setStyleSheet(f"""
            background-color: {self.current_theme["button_bg"]};
            color: {self.current_theme["button_fg"]};
        """)

        # Ensure button text visibility
        self.button_save.setStyleSheet(f"""
            color: {"black" if self.current_theme["button_bg"] in ["white", "lightgrey", "lightblue", "#d8bfd8"] else "white"};
        """)
        self.close_button.setStyleSheet(f"""
            color: {"black" if self.current_theme["button_bg"] in ["white", "lightgrey", "lightblue", "#d8bfd8"] else "white"};
        """)

    # Function to change theme
    def change_theme(self, index):
        selected_theme = self.theme_combobox.currentText()
        self.current_theme = themes[selected_theme]
        self.apply_theme()

    # Main function to run the application
    def run(self):
        self.show()
        sys.exit(app.exec())

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
           "Lavender": {
        "bg": "#e6e6fa",
        "fg": "black",
        "text_bg": "#d8bfd8",
        "text_fg": "black",
        "button_bg": "#d8bfd8",
        "button_fg": "black",
    },
    "Night Sky": {
        "bg": "#1a1a2e",
        "fg": "white",
        "text_bg": "#1a1a2e",
        "text_fg": "white",
        "button_bg": "#242943",
        "button_fg": "white",
    },
    "Fire Red": {
        "bg": "#8b0000",
        "fg": "white",
        "text_bg": "#660000",
        "text_fg": "white",
        "button_bg": "#660000",
        "button_fg": "white",
    },
    "Forest Green": {
        "bg": "#228b22",
        "fg": "white",
        "text_bg": "#006400",
        "text_fg": "white",
        "button_bg": "#006400",
        "button_fg": "white",
    },
    "Sunset Orange": {
        "bg": "#ff7f50",
        "fg": "black",
        "text_bg": "#ff6347",
        "text_fg": "black",
        "button_bg": "#ff6347",
        "button_fg": "black",
    },
    "Pride Month": {
        "bg": "#fbfbfb",
        "fg": "black",
        "text_bg": "#f7931e",
        "text_fg": "black",
        "button_bg": "#662d91",
        "button_fg": "white",
    },
}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = ImageTextEditor()
    editor.run()
