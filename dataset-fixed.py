import os
import sys
import json
import time
import psutil
import logging
from functools import lru_cache
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Tuple, List, Union
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, 
    QLabel, QPlainTextEdit, QPushButton, 
    QListWidget, QScrollArea, QSizePolicy, 
    QProgressBar, QStatusBar, QFileDialog, 
    QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QSize, QTimer, QMargins
from PyQt6.QtGui import QPixmap, QIcon, QKeySequence, QShortcut
from PIL import Image, ImageQt

@dataclass
class ViewerConfig:
    """Configuration settings for the viewer"""
    max_memory_mb: int = 500
    thumbnail_size: int = 120
    window_width: int = 1200
    window_height: int = 800
    grid_spacing: int = 10
    thumbnail_padding: int = 40
    supported_formats: tuple = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
    
    @classmethod
    def load(cls, path: str = "viewer_config.json") -> 'ViewerConfig':
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return cls(**json.load(f))
        except Exception as e:
            logging.warning(f"Using default settings: {e}")
        return cls()

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        # Create the logger first
        self.logger = self.setup_logging()
        self.logger.info("Starting Dataset Viewer!")
        
        # Then load config
        self.config = ViewerConfig.load()
        
        # Initialize state
        self.current_folder = str(Path.cwd())
        self.current_image: Optional[str] = None
        self.thumbnail_cache = {}
        
        # Set up UI
        self.setWindowTitle("Dataset Viewer")
        self.setMinimumSize(self.config.window_width, self.config.window_height)
        self.init_ui()
        
        # Start monitoring
        self.setup_memory_monitor()
        
        # Load initial folder
        self.load_folder(self.current_folder)
        
        # Set up shortcuts LAST - after all methods are defined
        self.setup_shortcuts()  # The key change is right here!

    # Our other methods follow...

    def setup_logging(self) -> logging.Logger:
        """Sets up our logging system"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"dataset_viewer_{time.strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        return logging.getLogger('DatasetViewer')

    def setup_memory_monitor(self):
        """Set up memory usage monitoring"""
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.check_memory)
        self.memory_timer.start(5000)  # Check every 5 seconds

    def check_memory(self):
        """Monitor memory usage and clean up if needed"""
        process = psutil.Process()
        memory_use = process.memory_info().rss / 1024 / 1024  # Convert to MB
        self.statusBar().showMessage(f"Memory usage: {memory_use:.1f}MB")
        
        if memory_use > self.config.max_memory_mb:
            self.logger.info("Memory threshold reached, cleaning cache...")
            self.cleanup_cache()

    def cleanup_cache(self):
        """Clear image caches to free memory"""
        self.thumbnail_cache.clear()
        self.logger.info("Cache cleared")

    def init_ui(self):
        """Initialize the user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(QMargins(10, 10, 10, 10))
        
        # Add components
        self.setup_folder_controls(layout)
        self.setup_image_preview(layout)
        self.setup_caption_area(layout)
        self.setup_thumbnail_grid(layout)
        
        # Progress tracking
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.statusBar().showMessage("Ready!")

    def setup_folder_controls(self, parent_layout: QVBoxLayout):
        """Set up folder selection controls"""
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("Choose Folder")
        self.folder_button.setMinimumHeight(40)
        self.folder_button.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_button)
        parent_layout.addLayout(folder_layout)

    def setup_image_preview(self, parent_layout: QVBoxLayout):
        """Set up the image preview area"""
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        preview_frame.setMinimumHeight(400)
        preview_layout = QVBoxLayout(preview_frame)
        
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        preview_layout.addWidget(self.image_label)
        parent_layout.addWidget(preview_frame)

    def setup_caption_area(self, parent_layout: QVBoxLayout):
        """Set up the caption editing area"""
        caption_frame = QFrame()
        caption_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        caption_layout = QHBoxLayout(caption_frame)
        
        caption_label = QLabel("Caption:")
        caption_label.setMinimumWidth(60)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setMinimumHeight(100)
        
        self.save_button = QPushButton("Save")
        self.save_button.setMinimumWidth(80)
        self.save_button.clicked.connect(self.safe_save_text)
        
        caption_layout.addWidget(caption_label)
        caption_layout.addWidget(self.text_edit)
        caption_layout.addWidget(self.save_button)
        parent_layout.addWidget(caption_frame)

    def setup_thumbnail_grid(self, parent_layout: QVBoxLayout):
        """Set up the thumbnail grid"""
        grid_frame = QFrame()
        grid_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        grid_layout = QVBoxLayout(grid_frame)
        
        self.image_grid = QListWidget()
        self.image_grid.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_grid.setIconSize(QSize(
            self.config.thumbnail_size,
            self.config.thumbnail_size
        ))
        
        # Fix grid alignment
        grid_size = QSize(
            self.config.thumbnail_size + self.config.thumbnail_padding,
            self.config.thumbnail_size + self.config.thumbnail_padding + 20
        )
        self.image_grid.setGridSize(grid_size)
        
        # Configure grid behavior
        self.image_grid.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_grid.setMovement(QListWidget.Movement.Static)
        self.image_grid.setFlow(QListWidget.Flow.LeftToRight)
        self.image_grid.setWrapping(True)
        self.image_grid.setSpacing(self.config.grid_spacing)
        self.image_grid.setUniformItemSizes(True)
        
        self.image_grid.itemClicked.connect(self.safe_load_image)
        grid_layout.addWidget(self.image_grid)
        parent_layout.addWidget(grid_frame)

    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.choose_folder)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.safe_save_text)
        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_image)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.previous_image)

    def choose_folder(self):
        """Open folder selection dialog"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Dataset Folder",
            self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.cleanup_cache()
            self.load_folder(folder)

    def load_folder(self, folder_path: str) -> None:
        """Load all images from a folder"""
        self.logger.info(f"Loading folder: {folder_path}")
        self.progress_bar.show()
        self.image_grid.clear()
        
        try:
            # Get all image files
            image_files = []
            for file in os.listdir(folder_path):
                if file.lower().endswith(self.config.supported_formats):
                    image_files.append(file)
            
            if not image_files:
                self.statusBar().showMessage("No images found")
                self.progress_bar.hide()
                return
            
            # Process images
            self.progress_bar.setMaximum(len(image_files))
            for i, file in enumerate(sorted(image_files), 1):
                image_path = os.path.join(folder_path, file)
                thumb = self.create_thumbnail(image_path)
                if thumb:
                    item = QListWidgetItem(
                        QIcon(thumb),
                        os.path.splitext(file)[0]
                    )
                    self.image_grid.addItem(item)
                self.progress_bar.setValue(i)
                QApplication.processEvents()
            
            self.statusBar().showMessage(f"Loaded {len(image_files)} images")
            
        except Exception as e:
            self.logger.error(f"Failed to load folder: {e}")
            self.statusBar().showMessage(f"Folder loading failed: {str(e)}")
        finally:
            self.progress_bar.hide()

    def create_thumbnail(self, image_path: str) -> Optional[QPixmap]:
        """Create a thumbnail for an image"""
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
            self.logger.error(f"Failed to create thumbnail for {image_path}: {e}")
            return None

    def safe_load_image(self, item: QListWidgetItem) -> None:
        """Safely load and display an image"""
        if not item:
            return
        
        # Find the actual image file
        base_name = item.text()
        image_path = None
        for ext in self.config.supported_formats:
            test_path = os.path.join(self.current_folder, base_name + ext)
            if os.path.exists(test_path):
                image_path = test_path
                break
        
        if not image_path:
            self.statusBar().showMessage(f"Could not find image for {base_name}")
            return
        
        self.current_image = image_path
        try:
            with Image.open(image_path) as img:
                # Convert if needed
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Get dimensions
                label_size = self.image_label.size()
                img.thumbnail((label_size.width(), label_size.height()))
                
                # Convert and display
                qimage = ImageQt.ImageQt(img)
                pixmap = QPixmap.fromImage(qimage)
                
                scaled_pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                
                # Load caption
                self.load_text(image_path)
                
        except Exception as e:
            self.logger.error(f"Failed to load {image_path}: {e}")
            self.statusBar().showMessage(f"Image loading failed: {str(e)}")

    def load_text(self, image_path: str) -> None:
        """Load caption text if it exists"""
        text_path = os.path.splitext(image_path)[0] + '.txt'
        try:
            if os.path.exists(text_path):
                with open(text_path, 'r', encoding='utf-8') as f:
                    self.text_edit.setPlainText(f.read())
            else:
                self.text_edit.clear()
        except Exception as e:
            self.logger.error(f"Failed to load caption: {e}")

    def safe_save_text(self) -> None:
        """Safely save the caption text"""
        if not self.current_image:
            return
        
        text_path = os.path.splitext(self.current_image)[0] + '.txt'
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            
            self.save_button.setText("Saved!")
            QTimer.singleShot(2000, lambda: self.save_button.setText("Save"))
            self.logger.info(f"Saved caption to: {text_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save caption: {e}")
            self.statusBar().showMessage(f"Caption save failed: {str(e)}")

    def next_image(self) -> None:
        """Move to next image"""
        current_row = self.image_grid.currentRow()
        if current_row < self.image_grid.count() - 1:
            self.image_grid.setCurrentRow(current_row + 1)
            self.safe_load_image(self.image_grid.currentItem())

def previous_image(self) -> None:
    """Move to previous image"""
    current_row = self.image_grid.currentRow()
    if current_row > 0:
        self.image_grid.setCurrentRow(current_row - 1)
        self.safe_load_image(self.image_grid.currentItem())

def resizeEvent(self, event) -> None:
    """Handle window resizing gracefully"""
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
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
