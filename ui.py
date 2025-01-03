from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QListWidget,
    QAbstractItemView,
    QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from widgets import FileLoader
import os
import imghdr
from metadata_parser import parse_metadata
import json
import re
import logging

log_level = "INFO"
msg_init = None
log_level = getattr(logging, log_level)
logger = logging.getLogger(__name__)
if msg_init is not None:
    logger = logging.getLogger(__name__)
    logger.info(msg_init)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set a default font for the app
        # app_font = QFont("Arial", 12)
        # self.setFont(app_font)

        self.setWindowTitle("Dataset Viewer")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height
        self.setMinimumSize(800, 600)  # set minimum size for standard window.

        # Central widget to hold our layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Left panel layout
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel)

        # Folder Path Label
        self.current_folder_label = QLabel("Current Folder: None")
        left_layout.addWidget(self.current_folder_label)

        # Placeholder UI
        self.open_folder_button = QPushButton("Open Folder")
        self.open_folder_button.clicked.connect(self.open_folder)
        left_layout.addWidget(self.open_folder_button)

        # Placeholder label, you can remove this later
        self.message_label = QLabel("Select a folder!")
        left_layout.addWidget(self.message_label)

        # File list (replaced QLabel with QListWidget)
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.files_list.itemClicked.connect(self.on_file_selected)
        left_layout.addWidget(self.files_list)

        # Add a progress bar for file loading
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        left_layout.addWidget(self.progress_bar)

        # Right panel Layout
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        main_layout.addWidget(right_panel)

        # Image preview area
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(300)
        right_layout.addWidget(self.image_preview)


        # Metadata Box
        self.metadata_box = QTextEdit()
        self.metadata_box.setReadOnly(True)
        right_layout.addWidget(self.metadata_box)

        # Prompt Text
        self.prompt_text = QLabel()
        self.prompt_text.setText("Prompt Info will show here")
        right_layout.addWidget(self.prompt_text)


        # Text File Content Area
        self.text_content = QTextEdit()
        self.text_content.setReadOnly(True)
        right_layout.addWidget(self.text_content)


        self.file_loader = None
        self.file_list = []
        self.image_list = []
        self.text_files = []
        self.current_folder = None

    def open_folder(self):
        # Open a dialog to select the folder
        folder_path = QFileDialog.getExistingDirectory(self, "Select a folder")
        if folder_path:
            # Call the file loading function
            self.load_files(folder_path)

    def clear_files(self):
      if self.file_loader:
         self.file_loader.clear_files()
      self.file_list = []
      self.image_list = []
      self.text_files = []
      self.files_list.clear()
      self.image_preview.clear()
      self.text_content.clear()
      self.prompt_text.clear()
      self.metadata_box.clear()

    def load_files(self, folder_path):
        # Start background loading of files using QThread
        self.current_folder = folder_path
        self.current_folder_label.setText(f"Current Folder: {folder_path}")
        self.message_label.setText("Loading files...")
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        if self.file_loader:
            self.file_loader.finished.disconnect()
        self.file_loader = FileLoader(folder_path)
        self.file_loader.progress.connect(self.update_progress)
        self.file_loader.finished.connect(self.on_files_loaded)
        self.file_loader.start()

    def update_progress(self, progress):
        # Update progress bar
        self.progress_bar.setValue(progress)

    def on_files_loaded(self, image_list, text_files, loaded_folder):
        if self.current_folder != loaded_folder:
            # We are loading files from a different folder
            # than what's currently selected, so we need to ignore this.
            return
        self.image_list = image_list
        self.text_files = text_files
        # update the message and hide the loading bar
        self.message_label.setText(f"Loaded {len(self.image_list)} images and {len(self.text_files)} text files")
        self.progress_bar.hide()

        # Clear and populate the QListWidget
        self.files_list.clear()
        self.files_list.addItems(self.image_list)
        self.files_list.addItems(self.text_files)


    def on_file_selected(self, item):
      file_path = item.text()
      self.message_label.setText(f"Selected {file_path}")

      # Clear any previous selection
      self.image_preview.clear()
      self.text_content.clear()
      self.prompt_text.clear()
      self.metadata_box.clear()

      if file_path.lower().endswith(('.png','.jpg','.jpeg','.webp')):
         # Load the image
         self.load_image_preview(file_path)
         self.load_metadata(file_path)

      if file_path.lower().endswith('.txt'):
        # Load the text file
        self.load_text_file(file_path)

    def load_metadata(self, file_path):
      metadata = None
      try:
        if imghdr.what(file_path) == 'png':
             metadata = parse_metadata(file_path)

        elif imghdr.what(file_path) in ['jpeg', 'jpg']:
            # Add support for jpeg here later.
            print("no metadata support for jpeg yet")
            metadata = None
        else:
           metadata = None
      except Exception as e:
        print("Error loading metadata:", e)
        metadata = None

      if metadata is not None:
         self.metadata_box.setText(metadata)

         # check if the formatted metadata contains `prompt`, otherwise ignore it.
         if "prompt:" in metadata:
            try:
              # search for the string, and return it.
              prompt_regex = re.search(r"prompt: (.*?)\n", metadata)
              if prompt_regex is not None:
                  self.prompt_text.setText(prompt_regex.group(1))
            except Exception as e:
                print("Error getting prompt: ", e)
         else:
            self.prompt_text.setText("No Prompt found")
      else:
         self.metadata_box.setText("No metadata found")
         self.prompt_text.setText("No Prompt found")

    def load_image_preview(self, file_path):
        # load image file
        pixmap = QPixmap(file_path)
        # scale the image
        self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def load_text_file(self, file_path):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                self.text_content.setText(content)
        except Exception as e:
             self.text_content.setText(f"Error loading text file: {e}")