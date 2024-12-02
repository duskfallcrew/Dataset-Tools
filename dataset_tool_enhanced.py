import os
import sys
import time
import psutil
from functools import lru_cache
from dataclasses import dataclass
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QListWidget, QScrollArea,
    QSplitter, QFileDialog, QSizePolicy, QListWidgetItem, QProgressBar,
    QStatusBar
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon
from PIL import Image, ImageQt

def check_requirements():
    """Makes sure we have all our tools before starting! 🛠️"""
    required_packages = {
        'PyQt6': 'PyQt6',
        'Pillow': 'PIL',
        'psutil': 'psutil'  # For monitoring system resources
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
            print("✨ All set! Requirements installed successfully!")
        except Exception as e:
            print(f"Oops! Couldn't install requirements: {e}")
            sys.exit(1)

class ResourceMonitor:
    """Keeps an eye on our system resources - like a friendly system guardian! 👀"""
    @staticmethod
    def get_memory_usage():
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024  # Convert to MB

    @staticmethod
    def get_cpu_usage():
        return psutil.cpu_percent(interval=0.1)

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Dataset Viewer")
        self.setMinimumSize(1200, 800)
        
        # Initialize our trackers
        self.current_image = None
        self.current_folder = os.getcwd()
        self.thumbnail_cache = {}
        self.max_cache_size = 100
        
        # Set up our UI
        self.init_ui()
        self.setup_resource_monitoring()
        self.refresh_file_list()
    
    def init_ui(self):
        """Sets up our cozy interface 🏠"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left side: Thumbnail grid
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Folder controls with status
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("📁 Choose Folder")
        self.folder_button.clicked.connect(self.pick_folder)
        self.status_label = QLabel("Ready to load images!")
        folder_layout.addWidget(self.folder_button)
        folder_layout.addWidget(self.status_label, stretch=1)
        
        # Progress tracking
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        # Our gorgeous thumbnail grid
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.file_list.setIconSize(QSize(150, 150))
        self.file_list.setGridSize(QSize(180, 200))
        self.file_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.file_list.setWrapping(True)
        self.file_list.setSpacing(10)
        self.file_list.setMovement(QListWidget.Movement.Static)
        self.file_list.itemClicked.connect(self.load_image)
        
        left_layout.addLayout(folder_layout)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.file_list)
        
        # Center: Image preview
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.image_scroll.setWidget(self.image_label)
        
        # Right side: Caption editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(200)
        self.save_btn = QPushButton("💾 Save Caption")
        self.save_btn.clicked.connect(self.save_changes)
        
        right_layout.addWidget(QLabel("Caption:"))
        right_layout.addWidget(self.text_edit)
        right_layout.addWidget(self.save_btn)
        right_layout.addStretch()
        
        # Layout with nice proportions
        layout.addWidget(left_panel, stretch=3)
        layout.addWidget(self.image_scroll, stretch=4)
        layout.addWidget(right_panel, stretch=1)
        
        # Status bar for resource monitoring
        self.statusBar().showMessage("Ready!")
    
    def setup_resource_monitoring(self):
        """Sets up our friendly system monitor 📊"""
        self.resource_timer = QTimer()
        self.resource_timer.timeout.connect(self.update_resource_status)
        self.resource_timer.start(2000)  # Update every 2 seconds
    
    def update_resource_status(self):
        """Keeps us informed about system resources"""
        memory = ResourceMonitor.get_memory_usage()
        cpu = ResourceMonitor.get_cpu_usage()
        self.statusBar().showMessage(
            f"Memory: {memory:.1f}MB | CPU: {cpu}% | Cache: {len(self.thumbnail_cache)} thumbnails"
        )
    
    @lru_cache(maxsize=1)  # Cache the last processed image
    def process_image(self, image_path, size):
        """Processes images efficiently - like a tiny image laboratory! 🔬"""
        try:
            with Image.open(image_path) as img:
                # Handle transparency
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, 'WHITE')
                    background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Calculate proportional size
                ratio = min(size/img.width, size/img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                
                # Smooth resize
                return img.resize(new_size, Image.Resampling.LANCZOS)
        except Exception as e:
            print(f"Image processing hiccup: {e}")
            return None
    
    def create_thumbnail(self, image_path):
        """Creates our lovely thumbnails ✨"""
        if image_path in self.thumbnail_cache:
            return self.thumbnail_cache[image_path]
        
        thumb = self.process_image(image_path, 150)
        if thumb:
            qt_thumb = ImageQt.ImageQt(thumb)
            self.thumbnail_cache[image_path] = qt_thumb
            self.cleanup_cache()
            return qt_thumb
        return None
    
    def cleanup_cache(self):
        """Keeps our memory usage friendly 🧹"""
        if len(self.thumbnail_cache) > self.max_cache_size:
            # Remove oldest items
            while len(self.thumbnail_cache) > self.max_cache_size * 0.75:
                self.thumbnail_cache.popitem()
    
    def refresh_file_list(self):
        """Updates our thumbnail grid with fresh content 🔄"""
        self.file_list.clear()
        self.status_label.setText("Loading images...")
        self.progress_bar.show()
        
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        try:
            files = sorted([f for f in os.listdir(self.current_folder) 
                          if f.lower().endswith(image_extensions)])
            
            total_files = len(files)
            self.progress_bar.setMaximum(total_files)
            
            for i, filename in enumerate(files):
                filepath = os.path.join(self.current_folder, filename)
                thumb = self.create_thumbnail(filepath)
                
                if thumb:
                    icon = QIcon(QPixmap.fromImage(thumb))
                    item = QListWidgetItem(icon, filename)
                    item.setToolTip(filename)
                    self.file_list.addItem(item)
                
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()
            
            self.status_label.setText(f"Found {total_files} images! ✨")
            self.progress_bar.hide()
            
        except Exception as e:
            self.status_label.setText(f"Oops! Error reading folder: {e}")
            self.progress_bar.hide()
    
    def load_image(self, item):
        """Displays our selected image in all its glory 🖼️"""
        image_path = os.path.join(self.current_folder, item.text())
        try:
            img = self.process_image(image_path, 1200)  # Larger size for display
            if img:
                pixmap = QPixmap.fromImage(ImageQt.ImageQt(img))
                scaled = pixmap.scaled(
                    self.image_scroll.viewport().size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled)
                self.current_image = image_path
                self.load_caption(image_path)
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def load_caption(self, path):
        """Loads any existing caption 📝"""
        caption_path = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.clear()
    
    def save_changes(self):
        """Saves our brilliant captions! 💾"""
        if self.current_image:
            caption_path = os.path.splitext(self.current_image)[0] + '.txt'
            try:
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.save_btn.setText("✅ Saved!")
                QApplication.processEvents()
                time.sleep(1)
                self.save_btn.setText("💾 Save Caption")
            except Exception as e:
                print(f"Error saving caption: {e}")
    
    def pick_folder(self):
        """Let's find those images! 🔍"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Your Dataset Folder",
            self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.thumbnail_cache.clear()  # Clear cache for new folder
            self.refresh_file_list()

if __name__ == '__main__':
    # Make sure we've got all our tools!
    check_requirements()
    
    # Fire up our app!
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
