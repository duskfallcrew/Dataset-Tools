import os
import sys
import gc  # For explicit garbage collection when we need it
from dataclasses import dataclass
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QListWidget, QScrollArea,
    QSizePolicy, QProgressBar, QStatusBar
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image, ImageQt
import psutil  # For monitoring system resources

@dataclass
class ImageInfo:
    """Keeps track of our image data - like a little passport for each image!"""
    path: str
    width: int
    height: int
    pixmap: Optional[QPixmap] = None
    last_accessed: float = 0  # We'll use this to know which images we can forget about

class MemoryFriendlyViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Cozy Dataset Viewer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Our image memory management stuff
        self.image_cache: Dict[str, ImageInfo] = {}
        self.max_cache_size = 5  # We'll only keep 5 images in memory at a time
        self.current_image_path: Optional[str] = None
        
        # Set up our cozy UI
        self.init_ui()
        
        # Set up our memory watchdog
        self.setup_memory_monitor()
        
        # Load those images!
        self.load_images()

    def init_ui(self):
        """Sets up our user interface - like arranging furniture in a cozy room!"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left side - Our image list and preview
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Status bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        # Image list
        self.image_list = QListWidget()
        self.image_list.itemClicked.connect(self.safe_show_image)
        
        # Scrollable image preview
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.scroll_area.setWidget(self.image_preview)
        
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(QLabel("Images:"))
        left_layout.addWidget(self.image_list)
        left_layout.addWidget(self.scroll_area)
        
        # Right side - Text editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.text_edit = QTextEdit()
        self.save_button = QPushButton("💾 Save Caption")
        self.save_button.clicked.connect(self.safe_save_text)
        
        right_layout.addWidget(QLabel("Caption:"))
        right_layout.addWidget(self.text_edit)
        right_layout.addWidget(self.save_button)
        
        # Put it all together
        layout.addWidget(left_panel, stretch=2)
        layout.addWidget(right_panel, stretch=1)
        
        # Status bar for memory info
        self.statusBar().showMessage("Ready to rock! 🚀")

    def setup_memory_monitor(self):
        """Sets up our memory watchdog - like having a friendly bouncer at a club!"""
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.check_memory_usage)
        self.memory_timer.start(5000)  # Check every 5 seconds

    def check_memory_usage(self):
        """Keeps an eye on our memory usage - like watching your snack supplies!"""
        process = psutil.Process()
        memory_use = process.memory_info().rss / 1024 / 1024  # Convert to MB
        self.statusBar().showMessage(f"Memory usage: {memory_use:.1f}MB | Cache size: {len(self.image_cache)} images")
        
        # If we're using too much memory, let's clean up
        if memory_use > 500:  # 500MB threshold
            self.cleanup_cache()
            gc.collect()  # Tell Python to take out the trash

    def cleanup_cache(self):
        """Cleans up our image cache - like tidying your room but for computer memory!"""
        if len(self.image_cache) > self.max_cache_size:
            # Find images we haven't looked at in a while
            current_images = sorted(
                self.image_cache.items(),
                key=lambda x: x[1].last_accessed
            )[:-self.max_cache_size]
            
            # Forget about them (but keep the size info!)
            for path, info in current_images:
                if path != self.current_image_path:
                    info.pixmap = None

    def safe_show_image(self, item):
        """Shows an image safely - like carefully opening a precious photo album!"""
        try:
            image_path = item.text()
            self.current_image_path = image_path
            
            # Load or retrieve image info
            if image_path not in self.image_cache:
                self.load_image_info(image_path)
            elif self.image_cache[image_path].pixmap is None:
                self.load_image_info(image_path)
            
            # Update the display
            self.update_image_display()
            self.load_caption(image_path)
            
        except Exception as e:
            print(f"Oops! Something went wrong showing the image: {e}")
            self.statusBar().showMessage("Had a little trouble with that image 😅")

    def load_image_info(self, path: str):
        """Loads image information carefully - like reading a delicate old book!"""
        try:
            with Image.open(path) as img:
                # Handle different image types
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, 'WHITE')
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Convert to Qt
                qim = ImageQt.ImageQt(img)
                pixmap = QPixmap.fromImage(QImage(qim))
                
                # Store the info
                self.image_cache[path] = ImageInfo(
                    path=path,
                    width=img.width,
                    height=img.height,
                    pixmap=pixmap
                )
        except Exception as e:
            print(f"Couldn't load image {path}: {e}")
            self.statusBar().showMessage("That image was a bit camera shy 📸")

    def update_image_display(self):
        """Updates the image display - like adjusting a picture frame!"""
        if not self.current_image_path or self.current_image_path not in self.image_cache:
            return
            
        info = self.image_cache[self.current_image_path]
        if info.pixmap:
            # Scale it to fit
            viewport_size = self.scroll_area.viewport().size()
            scaled_pixmap = info.pixmap.scaled(
                viewport_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_preview.setPixmap(scaled_pixmap)

    def load_images(self):
        """Loads images from the current folder - like browsing a photo album!"""
        try:
            self.progress_bar.show()
            files = [f for f in os.listdir() if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.progress_bar.setMaximum(len(files))
            
            for i, file in enumerate(files):
                self.image_list.addItem(file)
                self.progress_bar.setValue(i + 1)
            
            self.progress_bar.hide()
        except Exception as e:
            print(f"Couldn't load images: {e}")
            self.statusBar().showMessage("Had some trouble finding images 🔍")

    def safe_save_text(self):
        """Saves captions safely - like writing in your diary with care!"""
        try:
            if not self.current_image_path:
                return
                
            text_path = os.path.splitext(self.current_image_path)[0] + '.txt'
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            
            self.save_button.setText("✅ Saved!")
            QTimer.singleShot(2000, lambda: self.save_button.setText("💾 Save Caption"))
            
        except Exception as e:
            print(f"Couldn't save caption: {e}")
            self.statusBar().showMessage("Oops, had trouble saving that caption 📝")

    def load_caption(self, image_path: str):
        """Loads captions - like reading notes from a friend!"""
        try:
            text_path = os.path.splitext(image_path)[0] + '.txt'
            if os.path.exists(text_path):
                with open(text_path, 'r', encoding='utf-8') as f:
                    self.text_edit.setText(f.read())
            else:
                self.text_edit.clear()
        except Exception as e:
            print(f"Couldn't load caption: {e}")
            self.statusBar().showMessage("That caption was playing hide and seek 🙈")

    def resizeEvent(self, event):
        """Handles window resizing - like adjusting your glasses to see better!"""
        super().resizeEvent(event)
        self.update_image_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MemoryFriendlyViewer()
    window.show()
    sys.exit(app.exec())
