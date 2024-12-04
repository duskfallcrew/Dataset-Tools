from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QStatusBar,
    QMenuBar, QMenu, QAction, QFileDialog,
    QSplitter, QLabel, QShortcut, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize, QTimer, QSettings
from PyQt6.QtGui import QIcon, QPixmap, QKeySequence
from PIL import Image, ImageQt
from pathlib import Path
import json

class DatasetViewerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set up our app icon first! ✨
        self.setup_app_icon()
        
        self.logger = get_logger("MainWindow")
        self.memory_manager = get_memory_manager()
        
        # Settings and theme setup
        self.settings = QSettings("DuskfallCrew", "DatasetViewer")
        self.theme_manager = ThemeManager()
        
        # Initialize window
        self.setWindowTitle("Dataset Viewer ✨")
        self.setMinimumSize(QSize(1200, 800))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        
        # State tracking
        self.current_folder = str(Path.home())
        self.current_image = None
        
        # Set up all components
        self.setup_menu()
        self.setup_theme_menu()
        self.setup_layout()
        self.setup_file_tree()
        self.setup_thumbnail_grid()
        self.setup_metadata_panel()
        self.setup_status_bar()
        self.setup_monitoring()
        self.setup_shortcuts()
        
        # Apply saved theme
        saved_theme = self.settings.value('theme', 'Comfort Dark')
        self.change_theme(saved_theme)
        
        self.logger.info("Dataset Viewer ready to explore! 🌟")
    
    def setup_app_icon(self):
        """Give our app its special identity! ✨"""
        icon_path = Path(__file__).parent.parent / "resources" / "app_icon.png"
        if icon_path.exists():
            app_icon = QIcon(str(icon_path))
            self.setWindowIcon(app_icon)
            QApplication.setWindowIcon(app_icon)
        else:
            self.logger.warning("Couldn't find our icon! 🎨")
    
    def setup_layout(self):
        """Create our cozy workspace"""
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.main_splitter)
        
        # Left panel (file tree)
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.main_splitter.addWidget(self.left_panel)
        
        # Center area with preview and grid
        self.center_container = QWidget()
        self.center_layout = QVBoxLayout(self.center_container)
        
        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(400)
        self.image_preview.setStyleSheet("border: 1px solid #ccc;")
        self.center_layout.addWidget(self.image_preview)
        
        # Thumbnail grid
        self.grid_container = QWidget()
        self.grid_layout = QVBoxLayout(self.grid_container)
        self.center_layout.addWidget(self.grid_container)
        
        self.main_splitter.addWidget(self.center_container)
        
        # Right panel (metadata)
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.main_splitter.addWidget(self.right_panel)
        
        # Set proportions
        self.main_splitter.setSizes([200, 600, 300])
        self.center_layout.setStretch(0, 2)  # Preview gets more space
        self.center_layout.setStretch(1, 1)  # Grid gets less
    
    def setup_menu(self):
        """Create our menu system"""
        self.menubar = self.menuBar()
        
        # File Menu
        file_menu = self.menubar.addMenu("&File")
        
        open_action = QAction("Open Folder", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.choose_folder)
        file_menu.addAction(open_action)
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View Menu
        self.view_menu = self.menubar.addMenu("&View")
        
        # Help Menu
        help_menu = self.menubar.addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_shortcuts(self):
        """Set up our keyboard shortcuts"""
        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_image)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.previous_image)
        QShortcut(QKeySequence("Up"), self).activated.connect(self.prev_row)
        QShortcut(QKeySequence("Down"), self).activated.connect(self.next_row)
        QShortcut(QKeySequence("Home"), self).activated.connect(self.first_image)
        QShortcut(QKeySequence("End"), self).activated.connect(self.last_image)
    
    def setup_monitoring(self):
        """Monitor system resources"""
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.update_status)
        self.monitor_timer.start(2000)  # Update every 2 seconds
    
    def update_status(self):
        """Update status bar with system info"""
        mem_stats = self.memory_manager.get_stats()
        self.status_bar.showMessage(
            f"Memory: {mem_stats['current_memory_mb']:.1f}MB | "
            f"Cache: {mem_stats['cache_items']} items"
        )
    
    def choose_folder(self):
        """Open folder picker"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Dataset Folder",
            self.current_folder
        )
        if folder:
            self.current_folder = folder
            self.memory_manager.clear_cache()
            self.load_folder(folder)
    
    def show_settings(self):
        """Show settings dialog (to be implemented)"""
        self.status_bar.showMessage("Settings coming soon! ⚙️")
    
    def show_about(self):
        """Show about dialog (to be implemented)"""
        self.status_bar.showMessage("About dialog coming soon! ℹ️")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.logger.info("Shutting down...")
        self.memory_manager.shutdown()
        self.settings.sync()
        event.accept()

# Only if running directly
if __name__ == '__main__':
    app = QApplication([])
    window = DatasetViewerWindow()
    window.show()
    app.exec()
