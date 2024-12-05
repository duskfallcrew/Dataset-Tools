from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QStatusBar
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon

from ..utils import get_memory_manager, get_logger
from ..themes import get_current_theme
from .image_grid import VirtualizedImageGrid
from .metadata_panel import MetadataPanel
from .file_tree import FileTreeNavigator

class DatasetViewerWindow(QMainWindow):
    """Our cozy main window - where all the magic happens! ✨"""
    
    def __init__(self):
        super().__init__()
        # Get our helpers ready
        self.logger = get_logger()
        self.memory_manager = get_memory_manager()
        self.current_theme = get_current_theme()
        
        # Set up our window
        self.setup_window()
        self.setup_layout()
        self.setup_components()
        self.setup_monitoring()
        
        self.logger.info("Main window ready for action! 🎉")
    
    def setup_window(self):
        """Get our window looking just right"""
        self.setWindowTitle("Dataset Viewer ✨")
        self.setMinimumSize(QSize(1200, 800))
        
        # Set up our main container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
    
    def setup_layout(self):
        """Create our cozy workspace with flexible panels"""
        # Main splitter for resizable sections
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.main_splitter)
        
        # Create our panels
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        
        self.center_panel = QWidget()
        self.center_layout = QVBoxLayout(self.center_panel)
        
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        
        # Add panels to splitter
        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.center_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set nice proportions
        self.main_splitter.setSizes([200, 600, 300])
    
    def setup_components(self):
        """Add all our lovely components"""
        # File tree (left panel)
        self.file_tree = FileTreeNavigator()
        self.left_layout.addWidget(self.file_tree)
        
        # Image preview and grid (center panel)
        self.preview = QLabel()
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(400)
        self.center_layout.addWidget(self.preview)
        
        self.image_grid = VirtualizedImageGrid()
        self.center_layout.addWidget(self.image_grid)
        
        # Metadata panel (right panel)
        self.metadata = MetadataPanel()
        self.right_layout.addWidget(self.metadata)
        
        # Status bar at the bottom
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
    
    def setup_monitoring(self):
        """Keep an eye on system resources"""
        self.monitor = QTimer()
        self.monitor.timeout.connect(self.update_status)
        self.monitor.start(2000)  # Update every 2 seconds
    
    def update_status(self):
        """Update our status display"""
        memory_usage = self.memory_manager.get_current_usage()
        self.status_bar.showMessage(f"Memory usage: {memory_usage:.1f}MB")
    
    def closeEvent(self, event):
        """Clean up when closing"""
        self.logger.info("Thanks for visiting! Come back soon! 👋")
        self.memory_manager.cleanup()
        event.accept()
