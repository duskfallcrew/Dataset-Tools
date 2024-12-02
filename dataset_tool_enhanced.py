import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QListWidget, QScrollArea,
    QSplitter, QFileDialog, QSizePolicy, QListWidgetItem, QProgressBar
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PIL import Image, ImageQt

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Viewer")
        self.setMinimumSize(1200, 800)
        
        self.current_image = None
        self.current_folder = os.getcwd()
        
        self.init_ui()
        self.refresh_file_list()
    
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left side: Our gorgeous grid of thumbnails
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Folder selection with status
        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("📁 Choose Folder")
        self.folder_button.clicked.connect(self.pick_folder)
        self.status_label = QLabel("Ready to load images!")
        folder_layout.addWidget(self.folder_button)
        folder_layout.addWidget(self.status_label, stretch=1)
        
        # Loading progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        
        # Configure our thumbnail grid
        self.file_list = QListWidget()
        self.file_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.file_list.setIconSize(QSize(150, 150))
        self.file_list.setGridSize(QSize(180, 200))
        self.file_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.file_list.setWrapping(True)
        self.file_list.setSpacing(10)
        self.file_list.setMovement(QListWidget.Movement.Static)
        self.file_list.itemClicked.connect(self.load_image)
        
        # Add everything to left panel
        left_layout.addLayout(folder_layout)
        left_layout.addWidget(self.progress_bar)
        left_layout.addWidget(self.file_list)
        
        # Center: Big image preview
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, 
            QSizePolicy.Policy.Expanding
        )
        self.image_scroll.setWidget(self.image_label)
        
        # Right side: Caption panel
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
        
        # Set up main layout with nice proportions
        layout.addWidget(left_panel, stretch=3)
        layout.addWidget(self.image_scroll, stretch=4)
        layout.addWidget(right_panel, stretch=1)
    
    def create_thumbnail(self, image_path):
        """Makes our pretty thumbnails"""
        try:
            with Image.open(image_path) as img:
                # Handle transparency
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Create proportional thumbnail
                img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                return ImageQt.ImageQt(img)
        except Exception as e:
            print(f"Couldn't make thumbnail for {image_path}: {e}")
            return None
    
    def refresh_file_list(self):
        """Updates our grid of thumbnails"""
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
        """Shows our selected image"""
        image_path = os.path.join(self.current_folder, item.text())
        try:
            image = Image.open(image_path)
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
            
            # Scale to fit while keeping quality
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
        """Loads any existing caption"""
        caption_path = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.clear()
    
    def save_changes(self):
        """Saves our caption"""
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
        """Lets us choose where to look for images"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Your Dataset Folder",
            self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.refresh_file_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
