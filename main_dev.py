import os
import subprocess
import sys
import requests
from PIL import Image, ImageQt
from PyQt6.QtCore import Qt, QSize, QFile, QTextStream
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QListWidget, QComboBox, QListWidgetItem, QGridLayout, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QPixmap, QIcon


# Function to install required packages
def install_packages():
    packages = ['pillow', 'numpy', 'matplotlib', 'PyQt6', 'requests']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

# Install required packages if not already installed
install_packages()

# Function to download a file from a URL
def download_file(url, local_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_path, 'wb') as file:
            file.write(response.content)
        return local_path
    else:
        raise Exception(f"Failed to download file from {url}")

class ImageTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Earth & Dusk's Dataset Tools: Image & Caption Editor")
        self.setGeometry(100, 100, 1200, 900)

        self.current_theme = themes["Light Theme"]  # Start with Light Theme

        self.init_ui()
        self.populate_listboxes()
        self.populate_image_gallery()  # Populate image gallery
        self.apply_theme()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout(central_widget)  # Main layout is vertical

        # Top layout for image display and text entry
        top_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)

        # Image display area
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setScaledContents(True)  # Ensure image scales with QLabel
        top_layout.addWidget(self.image_label)

        # Text display and entry area
        self.text_label = QLabel("Text:")
        top_layout.addWidget(self.text_label)

        self.text_box = QTextEdit()
        self.text_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        top_layout.addWidget(self.text_box)

        # Save and Close buttons
        button_layout = QHBoxLayout()
        top_layout.addLayout(button_layout)

        self.button_save = QPushButton("Save", clicked=self.save_text)
        button_layout.addWidget(self.button_save)

        self.close_button = QPushButton("Close", clicked=self.close_app)
        button_layout.addWidget(self.close_button)

        # Middle layout for listbox and image gallery
        middle_layout = QHBoxLayout()
        main_layout.addLayout(middle_layout)

        # Listbox to display text files
        self.text_file_listbox = QListWidget()
        middle_layout.addWidget(self.text_file_listbox)

        # Image gallery grid layout
        gallery_container = QWidget()
        self.gallery_layout = QGridLayout(gallery_container)
        self.image_gallery = QListWidget()
        self.image_gallery.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gallery_layout.addWidget(self.image_gallery, 0, 0)  # Add gallery to grid layout
        middle_layout.addWidget(gallery_container)

        # Image selection button
        self.select_image_button = QPushButton("Select Image", clicked=self.select_image_from_gallery)
        main_layout.addWidget(self.select_image_button)

        # Theme selection combobox
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItems(list(themes.keys()))
        self.theme_combobox.setCurrentIndex(0)  # Set default theme
        self.theme_combobox.currentIndexChanged.connect(self.change_theme)
        main_layout.addWidget(self.theme_combobox)

        # Links and Credits
        discord_link = QLabel('<a href="https://discord.gg/5t2kYxt7An">Earth & Dusk Discord</a>')
        discord_link.setOpenExternalLinks(True)
        main_layout.addWidget(discord_link)

        github_link = QLabel('<a href="https://github.com/duskfallcrew/Dataset-Tools">Duskfall Crew\'s GitHub</a>')
        github_link.setOpenExternalLinks(True)
        main_layout.addWidget(github_link)

        donation_link = QLabel('<a href="https://ko-fi.com/duskfallcrew/">Donate to Duskfall Crew</a>')
        donation_link.setOpenExternalLinks(True)
        main_layout.addWidget(donation_link)

    # Function to load and display image
    def load_image(self, image_path):
        image = Image.open(image_path)
        pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
        self.image_label.setPixmap(pixmap.scaled(
            self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding
        ))

    # Function to load and display text from file
    def load_text(self, text_path):
        with open(text_path, 'r') as file:
            text = file.read()
        self.text_box.clear()  # Clear previous text
        self.text_box.append(text)

    # Function to save edited text to file
    def save_text(self):
        if hasattr(self, 'current_text_file') and self.current_text_file:
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

    # Function to handle selecting an image from the gallery
    def select_image_from_gallery(self):
        selected_items = self.image_gallery.selectedItems()
        if selected_items:
            image_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
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
    def close_app(self):
        QApplication.quit()  # Quit the application gracefully

    # Function to populate listboxes with image and text files
    def populate_listboxes(self):
        self.text_file_listbox.clear()

        text_files = self.list_text_files_in_directory()
        self.text_file_listbox.addItems(text_files)

    # Function to populate the image gallery
    def populate_image_gallery(self):
        images = self.list_images_in_directory()
        for index, image in enumerate(images):
            item = QListWidgetItem(QIcon(image), os.path.basename(image))
            item.setData(Qt.ItemDataRole.UserRole, image)
            self.image_gallery.addItem(item)
            self.image_gallery.setItemWidget(item, QLabel(os.path.basename(image)))

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
            color: {"black" if self.current_theme["button_bg"] in ["white", "lightgrey", "lightblue", "lightgreen"] else "white"};
        """)

        self.close_button.setStyleSheet(f"""
            background-color: {self.current_theme["button_bg"]};
            color: {"black" if self.current_theme["button_bg"] in ["white", "lightgrey", "lightblue", "lightgreen"] else "white"};
        """)

        self.select_image_button.setStyleSheet(f"""
            background-color: {self.current_theme["button_bg"]};
            color: {"black" if self.current_theme["button_bg"] in ["white", "lightgrey", "lightblue", "lightgreen"] else "white"};
        """)

    # Function to handle changing themes
    def change_theme(self):
        selected_theme = self.theme_combobox.currentText()
        self.current_theme = themes[selected_theme]
        self.apply_theme()

# Define theme colors - Themes not working currently are commented out, will be working on more eventually.
themes = {
    "Light Theme": {
        "bg": "white",
        "fg": "black",
        "text_bg": "white",
        "text_fg": "black",
        "button_bg": "lightgrey",
        "button_fg": "black"
    },
    "Dark Theme": {
        "bg": "black",
        "fg": "white",
        "text_bg": "black",
        "text_fg": "white",
        "button_bg": "darkgrey",
        "button_fg": "white"
    },
    "Pastel Theme v2": {
        "bg": "lightyellow",
        "fg": "darkslateblue",
        "text_bg": "lightyellow",
        "text_fg": "darkslateblue",
        "button_bg": "lightblue",
        "button_fg": "darkslateblue"
    },
    "Beetlejuice Inspired": {
        "bg": "#202020",
        "fg": "#80FF00",
        "text_bg": "#303030",
        "text_fg": "#80FF00",
        "button_bg": "#303030",
        "button_fg": "#80FF00",
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
    #  Commented out the themes that i'm struggling with.
    #      "Pride Month Wonky": {
    #           "bg": "#fbfbfb",
    #           "fg": "black",
    #           "text_bg": "#f7931e",
    #           "text_fg": "black",
    #           "button_bg": "#662d91",
    #           "button_fg": "white",
    #       },
    #       "Pride Dark": {
    #          "bg": "#230026",
    #        "fg": "#051720",
    #           "text_bg": "#14291a",
    #           "text_fg": "#001b26",
    #           "button_bg": "#300507",
    #           "button_fg": "#000326",
    #       },
    #       "Pastel v1": {
    #           "bg": "#cdb4db",
    #           "fg": "#ffc8dd",
    #           "text_bg": "#bde0fe",
    #           "text_fg": "#001b26",
    #    "button_bg": "#a2d2ff",
    #           "button_fg": "#f6f1ee",
    #       },
    #"Dark Wine": {
    #    "bg": "#231c35",
    #    "fg": "#242039",
    #           "text_bg": "#2a2b47",
    #           "text_fg": "#484564",
    #           "button_bg": "#5b5271",
    #           "button_fg": "#6e5774",
    #       },
}
# Main exection just lets you know it's the main program, and that we're going to close it if you don't pay us money - I'm kidding.
# Main execution
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = ImageTextEditor()
    window.show()
    sys.exit(app.exec())
