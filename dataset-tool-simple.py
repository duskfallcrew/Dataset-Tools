import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QListWidget, QScrollArea,
    QSplitter, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PIL import Image, ImageQt

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Viewer")
        self.setMinimumSize(1200, 800)
        
        # Track our current state
        self.current_image = None
        self.current_folder = os.getcwd()
        
        # Build our interface
        self.init_ui()
        self.refresh_file_list()
    
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left side: File browser
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.folder_button = QPushButton("Choose Folder")
        self.folder_button.clicked.connect(self.pick_folder)
        
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_image)
        
        left_layout.addWidget(self.folder_button)
        left_layout.addWidget(self.file_list)
        
        # Center: Image viewer
        self.image_scroll = QScrollArea()
        self.image_scroll.setWidgetResizable(True)
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, 
                                     QSizePolicy.Policy.Expanding)
        self.image_scroll.setWidget(self.image_label)
        
        # Right side: Caption editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.text_edit = QTextEdit()
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        
        right_layout.addWidget(self.text_edit)
        right_layout.addWidget(self.save_btn)
        
        # Add everything to main layout
        layout.addWidget(left_panel, stretch=1)
        layout.addWidget(self.image_scroll, stretch=2)
        layout.addWidget(right_panel, stretch=1)
    
    def pick_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choose Folder", self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.refresh_file_list()
    
    def refresh_file_list(self):
        self.file_list.clear()
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        try:
            files = sorted([f for f in os.listdir(self.current_folder) 
                          if f.lower().endswith(image_extensions)])
            self.file_list.addItems(files)
        except Exception as e:
            print(f"Error reading folder: {e}")
    
    def load_image(self, item):
        image_path = os.path.join(self.current_folder, item.text())
        try:
            image = Image.open(image_path)
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
            
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.current_image = image_path
            
            # Load caption if it exists
            self.load_caption(image_path)
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def load_caption(self, path):
        caption_path = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.clear()
    
    def save_changes(self):
        if self.current_image:
            caption_path = os.path.splitext(self.current_image)[0] + '.txt'
            try:
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                print("Caption saved!")
            except Exception as e:
                print(f"Error saving caption: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
