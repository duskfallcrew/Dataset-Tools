import os
import sys
import json
import time
import psutil
from functools import lru_cache
from dataclasses import dataclass, asdict
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPlainTextEdit, QPushButton, QListWidget, QScrollArea,
    QSizePolicy, QProgressBar, QStatusBar, QFileDialog, QListWidgetItem,
    QSlider, QSpinBox, QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from PIL import Image, ImageQt

def check_requirements():
    """Makes sure we have all our tools before starting!"""
    required_packages = {
        'PyQt6': 'PyQt6',
        'Pillow': 'PIL',
        'psutil': 'psutil'
    }
    
    missing = []
    for package, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing required packages: {', '.join(missing)}")
        try:
            import subprocess
            for package in missing:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print("All set! Requirements installed successfully!")
        except Exception as e:
            print(f"Couldn't install requirements: {e}")
            sys.exit(1)

@dataclass
class ViewerConfig:
    """Our app's preferences!"""
    max_memory_mb: int = 500
    thumbnail_size: int = 100
    window_width: int = 1200
    window_height: int = 800
    
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
        self.config = ViewerConfig.load()
        self.setWindowTitle("Dataset Viewer")
        self.setMinimumSize(self.config.window_width, self.config.window_height)
        
        # Initialize our trackers
        self.current_folder = os.getcwd()
        self.image_cache = {}
        self.current_image = None
        
        self.init_ui()
        self.setup_memory_monitor()
        self.load_folder(self.current_folder)

    def init_ui(self):
        """Setting up our workspace"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Folder controls
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("📁 Choose Folder")
        self.folder_button.clicked.connect(self.choose_folder)
        self.status_label = QLabel("Ready!")
        folder_layout.addWidget(self.folder_button)
        folder_layout.addWidget(self.status_label, stretch=1)
        
        # Progress tracking
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side: Image list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        self.file_list = QListWidget()
        self.file_list.setIconSize(QSize(self.config.thumbnail_size, 
                                       self.config.thumbnail_size))
        self.file_list.itemClicked.connect(self.safe_load_image)
        left_layout.addWidget(self.file_list)
        
        # Center: Image preview
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.scroll_area.setWidget(self.image_label)
        
        # Right: Text editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.text_edit = QPlainTextEdit()
        self.save_button = QPushButton("💾 Save")
        self.save_button.clicked.connect(self.safe_save_text)
        right_layout.addWidget(QLabel("Caption:"))
        right_layout.addWidget(self.text_edit)
        right_layout.addWidget(self.save_button)
        
        # Put it all together
        content_layout.addWidget(left_panel, stretch=1)
        content_layout.addWidget(self.scroll_area, stretch=2)
        content_layout.addWidget(right_panel, stretch=1)
        
        layout.addLayout(folder_layout)
        layout.addWidget(self.progress_bar)
        layout.addLayout(content_layout)
        
        self.statusBar().showMessage("Ready!")

    def setup_memory_monitor(self):
        """Sets up our memory watchdog"""
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.check_memory)
        self.memory_timer.start(5000)  # Check every 5 seconds
    
    def check_memory(self):
        """Keeps an eye on memory usage"""
        process = psutil.Process()
        memory_use = process.memory_info().rss / 1024 / 1024
        self.statusBar().showMessage(f"Memory: {memory_use:.1f}MB")
        
        if memory_use > self.config.max_memory_mb:
            self.cleanup_cache()
    
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
        self.progress_bar.show()
        self.file_list.clear()
        
        try:
            files = [f for f in os.listdir(folder_path)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            self.progress_bar.setMaximum(len(files))
            
            for i, file in enumerate(files):
                image_path = os.path.join(folder_path, file)
                thumb = self.create_thumbnail(image_path)
                if thumb:
                    item = QListWidgetItem(QIcon(thumb), file)
                    self.file_list.addItem(item)
                self.progress_bar.setValue(i + 1)
            
            self.progress_bar.hide()
            self.status_label.setText(f"Found {len(files)} images")
            
        except Exception as e:
            self.progress_bar.hide()
            QMessageBox.warning(self, "Oops!", f"Trouble loading folder: {e}")
    
    def safe_load_image(self, item):
        """Safely loads selected image"""
        image_path = os.path.join(self.current_folder, item.text())
        
        try:
            with Image.open(image_path) as img:
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, 'WHITE')
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(img))
                scaled = pixmap.scaled(
                    self.scroll_area.viewport().size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
                self.current_image = image_path
                self.load_text(image_path)
                
        except Exception as e:
            QMessageBox.warning(self, "Oops!", f"Trouble loading image: {e}")
    
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
                ratio = min(size/img.width, size/img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                thumb = img.resize(new_size, Image.Resampling.LANCZOS)
                
                return QPixmap.fromImage(ImageQt.ImageQt(thumb))
        except Exception as e:
            print(f"Thumbnail creation error for {image_path}: {e}")
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
            QMessageBox.warning(self, "Oops!", f"Trouble loading caption: {e}")
    
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
            
        except Exception as e:
            QMessageBox.warning(self, "Oops!", f"Trouble saving caption: {e}")
    
    def cleanup_cache(self):
        """Cleans up memory when needed"""
        self.image_cache.clear()
        self.create_thumbnail.cache_clear()
    
    def resizeEvent(self, event):
        """Handles window resizing"""
        super().resizeEvent(event)
        if self.current_image and self.image_label.pixmap():
            scaled = self.image_label.pixmap().scaled(
                self.scroll_area.viewport().size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)

if __name__ == '__main__':
    check_requirements()
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
