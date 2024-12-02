import os
import sys
import json
import time
import psutil
import logging
from functools import lru_cache
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Tuple, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, 
    QLabel, QPlainTextEdit, QPushButton, 
    QListWidget, QScrollArea, QSizePolicy, 
    QProgressBar, QStatusBar, QFileDialog, 
    QListWidgetItem, QSlider, QSpinBox, 
    QCheckBox, QGroupBox, QMessageBox,
    QFrame
)
from PyQt6.QtCore import (
    Qt, QSize, QTimer, 
    QMimeData, QPoint,
    QMargins
)
from PyQt6.QtGui import (
    QPixmap, QIcon, QKeySequence, 
    QShortcut, QImage, QPalette,
    QColor, QDragEnterEvent, QDropEvent,
    QFont
)
from PIL import Image, ImageQt

def setup_logging():
    """Sets up our friendly debug output system!"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger('DatasetViewer')

def check_requirements():
    """Makes sure we have all our tools ready!"""
    logger = logging.getLogger('DatasetViewer')
    required_packages = {
        'PyQt6': 'PyQt6',
        'Pillow': 'PIL',
        'psutil': 'psutil'
    }
    
    missing = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
            logger.info(f"Found {package} ✓")
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.warning(f"Need to install: {', '.join(missing)}")
        try:
            import subprocess
            for package in missing:
                logger.info(f"Installing {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            logger.info("All packages installed successfully!")
        except Exception as e:
            logger.error(f"Package installation failed: {e}")
            sys.exit(1)

@dataclass
class ViewerConfig:
    """Our app's preferences!"""
    max_memory_mb: int = 500
    thumbnail_size: int = 120
    window_width: int = 1200
    window_height: int = 800
    grid_spacing: int = 10
    thumbnail_padding: int = 40
    
    @classmethod
    def load(cls, path: str = "viewer_config.json") -> 'ViewerConfig':
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return cls(**json.load(f))
        except Exception as e:
            print(f"Using default settings: {e}")
        return cls()
    
    def save(self, path: str = "viewer_config.json") -> None:
        try:
            with open(path, 'w') as f:
                json.dump(asdict(self), f, indent=2)
        except Exception as e:
            print(f"Couldn't save settings: {e}")

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logging()
        self.logger.info("Starting Dataset Viewer!")
        self.config = ViewerConfig.load()
        
        self.setWindowTitle("Dataset Viewer")
        self.setMinimumSize(self.config.window_width, self.config.window_height)
        
        self.valid_image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        self.valid_text_extensions = ('.txt',)
        
        self.current_folder = os.getcwd()
        self.image_cache = {}
        self.current_image = None
        
        self.init_ui()
        self.setup_memory_monitor()
        self.setup_shortcuts()
        self.load_folder(self.current_folder)

    def init_ui(self):
        """Setting up our workspace!"""
        self.logger.info("Setting up the interface...")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(QMargins(10, 10, 10, 10))
        
        # Folder controls
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("📁 Choose Folder")
        self.folder_button.setMinimumHeight(40)
        self.folder_button.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_button)
        main_layout.addLayout(folder_layout)
        
        # Image preview
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        preview_frame.setMinimumHeight(400)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        preview_layout.addWidget(self.image_label)
        main_layout.addWidget(preview_frame)

        # Caption area
        caption_frame = QFrame()
        caption_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        caption_layout = QHBoxLayout(caption_frame)
        
        caption_label = QLabel("Caption:")
        caption_label.setMinimumWidth(60)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setMinimumHeight(100)
        self.save_button = QPushButton("💾 Save")
        self.save_button.setMinimumWidth(80)
        self.save_button.clicked.connect(self.safe_save_text)
        
        caption_layout.addWidget(caption_label)
        caption_layout.addWidget(self.text_edit)
        caption_layout.addWidget(self.save_button)
        main_layout.addWidget(caption_frame)
        
        # Thumbnail grid
        grid_frame = QFrame()
        grid_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        grid_layout = QVBoxLayout(grid_frame)
        
        self.image_grid = QListWidget()
        self.image_grid.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_grid.setIconSize(QSize(self.config.thumbnail_size, self.config.thumbnail_size))
        
        # Fix the zigzag!
        fixed_width = self.config.thumbnail_size + self.config.thumbnail_padding
        fixed_height = self.config.thumbnail_size + self.config.thumbnail_padding + 20
        self.image_grid.setGridSize(QSize(fixed_width, fixed_height))
        
        self.image_grid.setResizeMode(QListWidget.ResizeMode.Fixed)
        self.image_grid.setMovement(QListWidget.Movement.Static)
        self.image_grid.setFlow(QListWidget.Flow.LeftToRight)
        self.image_grid.setWrapping(True)
        self.image_grid.setSpacing(self.config.grid_spacing)
        self.image_grid.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.image_grid.setUniformItemSizes(True)
        
        self.image_grid.itemClicked.connect(self.safe_load_image)
        grid_layout.addWidget(self.image_grid)
        main_layout.addWidget(grid_frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        self.statusBar().showMessage("Ready!")

    def setup_shortcuts(self):
        """Setting up keyboard shortcuts!"""
        self.logger.info("Setting up keyboard shortcuts...")
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.choose_folder)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.safe_save_text)
        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_image)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.previous_image)

    def setup_memory_monitor(self):
        """Setting up memory monitoring!"""
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.check_memory)
        self.memory_timer.start(5000)

    def check_memory(self):
        """Checking memory usage"""
        process = psutil.Process()
        memory_use = process.memory_info().rss / 1024 / 1024
        self.statusBar().showMessage(f"Memory: {memory_use:.1f}MB")
        
        if memory_use > self.config.max_memory_mb:
            self.cleanup_cache()

    def get_valid_files(self, folder_path: str) -> Tuple[List[str], List[str]]:
        """Finding valid images and captions"""
        self.logger.info(f"Scanning folder: {folder_path}")
        image_files = []
        text_files = []
        
        try:
            for file in os.listdir(folder_path):
                lower_file = file.lower()
                if lower_file.endswith(self.valid_image_extensions):
                    image_files.append(file)
                elif lower_file.endswith(self.valid_text_extensions):
                    text_files.append(file)
                    
            image_files.sort()
            text_files.sort()
            self.logger.info(f"Found {len(image_files)} images and {len(text_files)} captions")
            return image_files, text_files
            
        except Exception as e:
            self.logger.error(f"Folder scanning error: {e}")
            return [], []

    def choose_folder(self):
        """Opens folder picker"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Folder",
            self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.cleanup_cache()
            self.load_folder(folder)

    def load_folder(self, folder_path):
        """Loads images from selected folder"""
        self.logger.info(f"Loading folder: {folder_path}")
        self.progress_bar.show()
        self.image_grid.clear()
        
        image_files, text_files = self.get_valid_files(folder_path)
        
        if not image_files:
            self.statusBar().showMessage("No images found!")
            self.progress_bar.hide()
            return
            
        self.progress_bar.setMaximum(len(image_files))
        
        for i, file in enumerate(image_files, 1):
            self.logger.info(f"Processing image {i}/{len(image_files)}: {file}")
            image_path = os.path.join(folder_path, file)
            thumb = self.create_thumbnail(image_path)
            if thumb:
                item = QListWidgetItem(QIcon(thumb), os.path.splitext(file)[0])
                self.image_grid.addItem(item)
            self.progress_bar.setValue(i)
            QApplication.processEvents()
        
        self.progress_bar.hide()
        self.statusBar().showMessage(f"Loaded {len(image_files)} images!")

    def safe_load_image(self, item):
        """Safely loads selected image"""
        if not item:
            return
            
        image_path = os.path.join(self.current_folder, item.text() + '.jpg')  # Add file extension check if needed
        self.current_image = image_path
        
        try:
            with Image.open(image_path) as img:
                self.logger.info(f"Loading image: {image_path}")
                # Get widget dimensions
                label_size = self.image_label.size()
                max_size = (label_size.width(), label_size.height())
                
                # Convert to RGB if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize while maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to Qt
                qimage = ImageQt.ImageQt(img)
                pixmap = QPixmap.fromImage(qimage)
                
                # Scale and set with proper alignment
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                
                # Load associated text
                self.load_text(image_path)
                    
        except Exception as e:
            self.logger.error(f"Error loading image: {e}")
            self.statusBar().showMessage(f"Couldn't load image: {str(e)}")

    @lru_cache(maxsize=100)
    def create_thumbnail(self, image_path):
        """Creates thumbnails efficiently"""
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, 'WHITE')
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                size = self.config.thumbnail_size
                img.thumbnail((size, size))
                
                return QPixmap.fromImage(ImageQt.ImageQt(img))
        except Exception as e:
            self.logger.error(f"Thumbnail creation error for {image_path}: {e}")
            return None

    def load_text(self, image_path):
        """Loads caption if it exists"""
        text_path = os.path.splitext(image_path)[0] + '.txt'
        try:
            if os.path.exists(text_path):
                with open(text_path, 'r', encoding='utf-8') as f:
                    self.text_edit.setPlainText(f.read())
            else:
                self.text_edit.clear()
        except Exception as e:
            self.logger.error(f"Error loading caption: {e}")

    def safe_save_text(self):
        """Safely saves caption text"""
        if not self.current_image:
            return
            
        text_path = os.path.splitext(self.current_image)[0] + '.txt'
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            
            self.save_button.
          def safe_save_text(self):
        """Safely saves caption text"""
        if not self.current_image:
            return
            
        text_path = os.path.splitext(self.current_image)[0] + '.txt'
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            
            self.save_button.setText("✅ Saved!")
            QTimer.singleShot(2000, lambda: self.save_button.setText("💾 Save"))
            self.logger.info(f"Saved caption to: {text_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving caption: {e}")
            self.statusBar().showMessage(f"Couldn't save caption: {str(e)}")
    
    def next_image(self):
        """Move to next image"""
        current_row = self.image_grid.currentRow()
        if current_row < self.image_grid.count() - 1:
            self.image_grid.setCurrentRow(current_row + 1)
            self.safe_load_image(self.image_grid.currentItem())

    def previous_image(self):
        """Move to previous image"""
        current_row = self.image_grid.currentRow()
        if current_row > 0:
            self.image_grid.setCurrentRow(current_row - 1)
            self.safe_load_image(self.image_grid.currentItem())
    
    def cleanup_cache(self):
        """Cleans up memory when needed"""
        self.logger.info("Cleaning up cache...")
        self.image_cache.clear()
        self.create_thumbnail.cache_clear()
    
    def resizeEvent(self, event):
        """Handles window resizing"""
        super().resizeEvent(event)
        if self.current_image and self.image_label.pixmap():
            pixmap = self.image_label.pixmap()
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

if __name__ == '__main__':
    check_requirements()
    app = QApplication(sys.argv)
    
    # Add some style to our app
    app.setStyle('Fusion')
    
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
