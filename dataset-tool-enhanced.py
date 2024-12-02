import os
import sys
import time  # This is our new friend for the save feedback!
from dataclasses import dataclass
from typing import Optional, Dict
from PyQt6.QtCore import Qt, QSize  # See? No QTimer here anymore!
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QListWidget, QComboBox,
    QScrollArea, QSplitter, QTabWidget, QSizePolicy, QFileDialog
)
from PyQt6.QtGui import QPixmap, QIcon
from PIL import Image, ImageQt

@dataclass
class TagInfo:
    """Keeps track of our tag data - because organization is good!"""
    name: str
    category: str
    count: int = 0
    last_used: Optional[str] = None

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Dataset Viewer")
        self.setMinimumSize(1200, 800)
        
        # Keep track of important stuff
        self.current_image: Optional[str] = None
        self.current_folder = os.getcwd()
        self.tags: Dict[str, TagInfo] = {}
        self.current_theme = "light"
        
        # Set up our UI and initialize everything
        self.init_ui()
        self.setup_themes()
        self.refresh_file_list()
    
    def init_ui(self):
        """Set up our main user interface"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Main splitter for resizable panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Set up all our panels
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set initial sizes (20% | 60% | 20%)
        total_width = self.width()
        self.main_splitter.setSizes([
            int(total_width * 0.2),
            int(total_width * 0.6),
            int(total_width * 0.2)
        ])
        
        # Add everything to main layout
        main_layout.addWidget(self.main_splitter)
        
        # Add theme selector at bottom
        self.setup_theme_selector()
    
    def setup_left_panel(self):
        """Set up file browser with folder picker"""
        self.left_panel = QWidget()
        layout = QVBoxLayout(self.left_panel)
        
        # Folder picker section
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("📁 Current Folder:")
        self.folder_button = QPushButton("Choose Folder")
        self.folder_button.clicked.connect(self.pick_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)
        
        # Path display
        self.path_label = QLabel(self.current_folder)
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_image)
        self.file_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.file_list)
        
        # Quick tags section
        tag_label = QLabel("🏷️ Quick Tags")
        self.quick_tags = QListWidget()
        layout.addWidget(tag_label)
        layout.addWidget(self.quick_tags)
    
    def setup_center_panel(self):
        """Set up image viewer and metadata display"""
        self.center_panel = QWidget()
        layout = QVBoxLayout(self.center_panel)
        
        # Scrollable image viewer
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        scroll.setWidget(self.image_label)
        
        # Tabs for image and metadata
        tabs = QTabWidget()
        tabs.addTab(scroll, "🖼️ Image")
        
        # Metadata tab
        self.metadata_widget = QWidget()
        self.metadata_layout = QVBoxLayout(self.metadata_widget)
        tabs.addTab(self.metadata_widget, "📊 Metadata")
        
        layout.addWidget(tabs)
    
    def setup_right_panel(self):
        """Set up caption editor and tag categories"""
        self.right_panel = QWidget()
        layout = QVBoxLayout(self.right_panel)
        
        # Caption editor
        caption_label = QLabel("✏️ Caption")
        self.text_edit = QTextEdit()
        self.text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # Tag categories
        self.tag_tabs = QTabWidget()
        for category in ["Style", "Content", "Technical"]:
            tab = QListWidget()
            tab.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            self.tag_tabs.addTab(tab, category)
        
        # Save button
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        
        # Add everything to layout
        layout.addWidget(caption_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.tag_tabs)
        layout.addWidget(self.save_btn)
    
    def pick_folder(self):
        """Open folder picker dialog"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Your Dataset Folder",
            self.current_folder,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.current_folder = folder
            self.path_label.setText(folder)
            self.refresh_file_list()
    
    def refresh_file_list(self):
        """Update file list with images from current folder"""
        self.file_list.clear()
        
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        try:
            # Get list of files and sort them
            files = sorted([f for f in os.listdir(self.current_folder) 
                          if f.lower().endswith(image_extensions)])
            
            # Add them to the list
            for filename in files:
                self.file_list.addItem(filename)
            
            # Update status with count
            status = f"Found {self.file_list.count()} images! ✨"
            self.path_label.setText(f"{self.current_folder}\n{status}")
            
        except Exception as e:
            self.path_label.setText(f"Oops! Couldn't read folder: {e}")
    
    def load_image(self, item):
        """Load and display selected image"""
        image_path = os.path.join(self.current_folder, item.text())
        try:
            image = Image.open(image_path)
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
            
            # Scale while maintaining aspect ratio
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.current_image = image_path
            
            # Load associated caption
            self.load_metadata(image_path)
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def load_metadata(self, path):
        """Load image caption and metadata"""
        caption_path = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.clear()
    
    def save_changes(self):
        """Save caption changes"""
        if self.current_image:
            caption_path = os.path.splitext(self.current_image)[0] + '.txt'
            try:
                with open(caption_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                self.save_btn.setText("✅ Saved!")
                QApplication.processEvents()
                time.sleep(1)
                self.save_btn.setText("💾 Save Changes")
            except Exception as e:
                print(f"Error saving caption: {e}")
                self.save_btn.setText("❌ Error!")
                QApplication.processEvents()
                time.sleep(1)
                self.save_btn.setText("💾 Save Changes")
    
    def setup_themes(self):
        """Set up color themes"""
        self.themes = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "accent": "#4a9eff"
            },
            "dark": {
                "bg": "#1a1a1a",
                "fg": "#ffffff",
                "accent": "#66b3ff"
            },
            "cozy": {
                "bg": "#f5e6d3",
                "fg": "#2d2d2d",
                "accent": "#ff7e67"
            }
        }
    
    def setup_theme_selector(self):
        """Add theme selector dropdown"""
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        self.centralWidget().layout().addLayout(theme_layout)
    
    def apply_theme(self, theme_name):
        """Apply selected theme"""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            style = f"""
                QWidget {{
                    background-color: {theme['bg']};
                    color: {theme['fg']};
                }}
                QPushButton {{
                    background-color: {theme['accent']};
                    border-radius: 4px;
                    padding: 6px;
                }}
                QListWidget, QTextEdit {{
                    border: 1px solid {theme['accent']};
                    border-radius: 4px;
                }}
            """
            self.setStyleSheet(style)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
