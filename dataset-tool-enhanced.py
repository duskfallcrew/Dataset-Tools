import os
import sys
import time
from dataclasses import dataclass
from typing import Optional, Dict
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QListWidget, QComboBox,
    QScrollArea, QSplitter, QTabWidget, QSizePolicy, QFileDialog
)
from PyQt6.QtGui import QPixmap, QIcon
from PIL import Image, ImageQt

@dataclass
class TagInfo:
    """Our digital sticky notes for keeping track of tags! ✨"""
    name: str
    category: str
    count: int = 0
    last_used: Optional[str] = None

class DatasetViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Dataset Viewer")
        self.setMinimumSize(1200, 800)
        
        # Let's keep track of stuff!
        self.current_image: Optional[str] = None
        self.current_folder = os.getcwd()
        self.tags: Dict[str, TagInfo] = {}
        self.current_theme = "light"
        
        # Themes first - like picking your outfit before leaving the house!
        self.setup_themes()
        
        # Now we can build our beautiful UI
        self.init_ui()
        self.refresh_file_list()
    
    def setup_themes(self):
        """Setting up our color schemes because life's better in color! 🎨"""
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
    
    def init_ui(self):
        """Building our main interface - like setting up a cozy workspace! 🏠"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Our magical resizable panels
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Setting up all our cool panels
        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()
        
        # Adding panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Making things look nice (20% | 60% | 20%)
        total_width = self.width()
        self.main_splitter.setSizes([
            int(total_width * 0.2),
            int(total_width * 0.6),
            int(total_width * 0.2)
        ])
        
        # Add everything to main layout
        main_layout.addWidget(self.main_splitter)
        
        # Add our theme picker at the bottom
        self.setup_theme_selector()
    
    def setup_left_panel(self):
        """Setting up our file browser - like organizing your digital bookshelf! 📚"""
        self.left_panel = QWidget()
        layout = QVBoxLayout(self.left_panel)
        
        # Folder picker - because finding stuff should be easy!
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("📁 Current Folder:")
        self.folder_button = QPushButton("Choose Folder")
        self.folder_button.clicked.connect(self.pick_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)
        
        # Show where we are
        self.path_label = QLabel(self.current_folder)
        self.path_label.setWordWrap(True)
        layout.addWidget(self.path_label)
        
        # File list - where the magic happens!
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_image)
        self.file_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.file_list)
        
        # Quick tags for speedy tagging
        tag_label = QLabel("🏷️ Quick Tags")
        self.quick_tags = QListWidget()
        layout.addWidget(tag_label)
        layout.addWidget(self.quick_tags)
    
    def setup_center_panel(self):
        """Setting up our image viewer - the star of the show! 🌟"""
        self.center_panel = QWidget()
        layout = QVBoxLayout(self.center_panel)
        
        # Scrollable image viewer that plays nice with all sizes
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
        
        # Metadata tab for all the nerdy details
        self.metadata_widget = QWidget()
        self.metadata_layout = QVBoxLayout(self.metadata_widget)
        tabs.addTab(self.metadata_widget, "📊 Metadata")
        
        layout.addWidget(tabs)
    
    def setup_right_panel(self):
        """Setting up our caption editor - where the words flow! ✍️"""
        self.right_panel = QWidget()
        layout = QVBoxLayout(self.right_panel)
        
        # Caption editor that's ready for your thoughts
        caption_label = QLabel("✏️ Caption")
        self.text_edit = QTextEdit()
        self.text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        # Tag categories for organized chaos
        self.tag_tabs = QTabWidget()
        for category in ["Style", "Content", "Technical"]:
            tab = QListWidget()
            tab.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            self.tag_tabs.addTab(tab, category)
        
        # Save button that actually tells you what's happening
        self.save_btn = QPushButton("💾 Save Changes")
        self.save_btn.clicked.connect(self.save_changes)
        
        # Stack everything up nicely
        layout.addWidget(caption_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.tag_tabs)
        layout.addWidget(self.save_btn)
    
    def setup_theme_selector(self):
        """Adding our theme picker - because options are good! 🎨"""
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.themes.keys())
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        self.centralWidget().layout().addLayout(theme_layout)
    
    def pick_folder(self):
        """Let's find those images! 🔍"""
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
        """Update our file list - keeping things fresh! 🌱"""
        self.file_list.clear()
        
        image_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')
        
        try:
            # Get and sort our files
            files = sorted([f for f in os.listdir(self.current_folder) 
                          if f.lower().endswith(image_extensions)])
            
            # Pop them in the list
            for filename in files:
                self.file_list.addItem(filename)
            
            # Show how many we found
            status = f"Found {self.file_list.count()} images! ✨"
            self.path_label.setText(f"{self.current_folder}\n{status}")
            
        except Exception as e:
            self.path_label.setText(f"Oops! Couldn't read folder: {e}")
    
    def load_image(self, item):
        """Loading up those pixels! 🎨"""
        image_path = os.path.join(self.current_folder, item.text())
        try:
            image = Image.open(image_path)
            pixmap = QPixmap.fromImage(ImageQt.ImageQt(image))
            
            # Make it fit just right
            scaled = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled)
            self.current_image = image_path
            
            # Get the caption too!
            self.load_metadata(image_path)
            
        except Exception as e:
            print(f"Error loading image: {e}")
    
    def load_metadata(self, path):
        """Loading those captions! 📝"""
        caption_path = os.path.splitext(path)[0] + '.txt'
        if os.path.exists(caption_path):
            with open(caption_path, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
        else:
            self.text_edit.clear()
    
    def save_changes(self):
        """Saving your brilliant words! 💾"""
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
    
    def apply_theme(self, theme_name):
        """Making everything look pretty! 🎨"""
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
