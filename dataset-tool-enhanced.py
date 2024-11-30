import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QListWidget, QComboBox,
    QScrollArea, QSplitter, QFrame, QTabWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QResizeEvent
from PIL import Image, ImageQt

@dataclass
class TagInfo:
    """Stores information about a tag"""
    name: str
    category: str
    count: int = 0
    last_used: Optional[str] = None

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Dataset Viewer")
        self.setMinimumSize(1200, 800)
        
        # Track state
        self.current_image: Optional[str] = None
        self.tags: Dict[str, TagInfo] = {}
        self.current_theme = "light"
        
        self.init_ui()
        self.setup_themes()
        
    def init_ui(self):
        # Main container
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create main splitter for resizable panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel (file browser + tags)
        self.setup_left_panel()
        
        # Center panel (image viewer + metadata)
        self.setup_center_panel()
        
        # Right panel (tag editor + stats)
        self.setup_right_panel()
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set initial splitter sizes (20% | 60% | 20%)
        total_width = self.width()
        self.main_splitter.setSizes([
            int(total_width * 0.2),
            int(total_width * 0.6),
            int(total_width * 0.2)
        ])
        
        # Add everything to main layout
        main_layout.addWidget(self.main_splitter)
        
        # Theme selector at bottom
        self.setup_theme_selector()
    
    def setup_left_panel(self):
        """Setup file browser and quick-access tags"""
        self.left_panel = QWidget()
        layout = QVBoxLayout(self.left_panel)
        
        # File browser
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_image)
        layout.addWidget(QLabel("📁 Files"))
        layout.addWidget(self.file_list)
        
        # Quick tags
        self.quick_tags = QListWidget()
        layout.addWidget(QLabel("🏷️ Quick Tags"))
        layout.addWidget(self.quick_tags)
    
    def setup_center_panel(self):
        """Setup image viewer and metadata display"""
        self.center_panel = QWidget()
        layout = QVBoxLayout(self.center_panel)
        
        # Image viewer in scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        self.image_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(
            QWidget.SizePolicy.Policy.Expanding,
            QWidget.SizePolicy.Policy.Expanding
        )
        scroll.setWidget(self.image_label)
        
        # Tabs for image view and metadata
        tabs = QTabWidget()
        tabs.addTab(scroll, "🖼️ Image")
        
        # Metadata tab
        self.metadata_widget = QWidget()
        self.metadata_layout = QVBoxLayout(self.metadata_widget)
        tabs.addTab(self.metadata_widget, "📊 Metadata")
        
        layout.addWidget(tabs)
    
    def setup_right_panel(self):
        """Setup tag editor and statistics"""
        self.right_panel = QWidget()
        layout = QVBoxLayout(self.right_panel)
        
        # Caption/tag editor
        self.text_edit = QTextEdit()
        layout.addWidget(QLabel("✏️ Caption"))
        layout.addWidget(self.text_edit)
        
        # Tag categories
        self.tag_tabs = QTabWidget()
        categories = ["Style", "Content", "Technical"]
        for category in categories:
            tab = QListWidget()
            self.tag_tabs.addTab(tab, category)
        layout.addWidget(self.tag_tabs)
        
        # Save button
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        layout.addWidget(self.save_btn)
    
    def setup_themes(self):
        """Initialize theme system"""
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
        """Add theme selector to bottom of window"""
        theme_layout = QHBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(QLabel("🎨 Theme:"))
        theme_layout.addWidget(self.theme_combo)
        self.centralWidget().layout().addLayout(theme_layout)
    
    def load_image(self, item):
        """Load and display an image"""
        path = item.text()
        try:
            image = Image.open(path)
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
            
            # Scale while maintaining aspect ratio
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.current_image = path
            
            # Load associated caption/tags
            self.load_metadata(path)
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def load_metadata(self, path):
        """Load image metadata and caption"""
        # Load caption file if exists
        caption_path = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r') as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.clear()
            
        # TODO: Add EXIF/PNG info parsing here
    
    def save_changes(self):
        """Save caption and tag changes"""
        if self.current_image:
            caption_path = os.path.splitext(self.current_image)[0] + '.txt'
            with open(caption_path, 'w') as f:
                f.write(self.text_edit.toPlainText())
            # TODO: Add tag saving logic
    
    def apply_theme(self, theme_name):
        """Apply selected theme to all widgets"""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {theme['bg']};
                    color: {theme['fg']};
                }}
                QPushButton {{
                    background-color: {theme['accent']};
                    border-radius: 4px;
                    padding: 6px;
                }}
            """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DatasetViewer()
    window.show()
    sys.exit(app.exec())
