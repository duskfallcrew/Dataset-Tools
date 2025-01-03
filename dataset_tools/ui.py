from importlib import metadata
from pprint import PrettyPrinter
from xml.dom.minidom import parseString
from dataset_tools.__init__ import logger
import pprint

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
from dataset_tools.widgets import FileLoader
import imghdr
from dataset_tools.metadata_parser import parse_metadata, open_jpg_header
import re

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
        self.metadata_box.setMinimumWidth(400)
        right_layout.addWidget(self.metadata_box)

        # Prompt Text
        self.prompt_text = QLabel()
        self.prompt_text.setText("Prompt Info will show here")
        self.prompt_text.setMinimumWidth(400)
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
            metadata = self.load_metadata(file_path)
            self.display_metadata(metadata, file_path)

        if file_path.lower().endswith('.txt'):
            # Load the text file
            self.load_text_file(file_path)

    def load_metadata(self, file_path):
        metadata = None
        try:
            if imghdr.what(file_path) == 'png':
                metadata = parse_metadata(file_path)

            elif imghdr.what(file_path) in ['jpeg', 'jpg']:
                metadata = open_jpg_header(file_path)

        except IndexError as error_log:
            logger.info(f"Unexpected list position, out of range error for metadata in {file_path} : {error_log}")
            logger.debug(error_log)
            metadata = None
            pass
        except UnboundLocalError as error_log:
            logger.info(f"Variable not declared while extracting metadata from {file_path} : {error_log}")
            logger.debug(error_log)
            metadata = None
            pass
        except ValueError as error_log:
            logger.info(f"Invalid dictionary formatting while extracting metadata from{file_path} : {error_log}")
            logger.debug(error_log)
            metadata = None
            pass

        else:
            return metadata
        return None

    def display_metadata(self, metadata, file_path):
        if metadata is not None:
            prompt_keys = ['Positive prompt', 'Negative prompt']
            try:
                generation_data = "\n".join(f"{k}: {v}" for k, v in metadata.items() if k not in prompt_keys)
                self.metadata_box.setText(pprint.pformat(generation_data))

            except AttributeError as error_log:
                logger.info(f"'items' attribute cannot be applied to type {type(metadata)} from {file_path, metadata}  : {error_log}")
                logger.debug(error_log)
                pass

            try:
                prompt_data = '\n'.join(f"{metadata.get(k)}" for k in metadata if k in prompt_keys)
                self.text_content.setText(pprint.pformat(prompt_data))
            except TypeError:
                logger.info(f"Invalid data in prompt fields {type(metadata)} from {file_path, metadata}  : {error_log}")

            except AttributeError as error_log:
                logger.info(f"attribute cannot be applied to type {type(metadata)} from {file_path, metadata}  : {error_log}")
                logger.debug(error_log)
                pass

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