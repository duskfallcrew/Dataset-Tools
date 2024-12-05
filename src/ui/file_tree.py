from PyQt6.QtWidgets import (
    QTreeView, QFileSystemModel, QWidget,
    QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, QDir, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent
from pathlib import Path
import logging
from typing import Optional

class FileTreeNavigator(QWidget):
    """A cozy file tree for exploring our datasets! 🌳"""
    
    # Signals to tell others when interesting things happen
    folder_selected = pyqtSignal(str)  # When a folder is chosen
    file_selected = pyqtSignal(str)    # When a file is picked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger('DatasetViewer.FileTree')
        
        # Track our current state
        self.current_path: Optional[Path] = None
        self.favorite_paths = set()
        
        # Build our interface
        self._setup_ui()
        self._setup_model()
        self._setup_context_menu()
        
        self.logger.info("File tree navigator ready! 🌟")
    
    def _setup_ui(self):
        """Build our cozy navigation interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Quick access bar
        quick_bar = QWidget()
        quick_layout = QVBoxLayout(quick_bar)
        
        # Search box for quick filtering
        self.filter_box = QLineEdit()
        self.filter_box.setPlaceholderText("🔍 Filter files...")
        self.filter_box.textChanged.connect(self._apply_filter)
        quick_layout.addWidget(self.filter_box)
        
        # Home/favorites buttons
        self.home_button = QPushButton("🏠 Home")
        self.home_button.clicked.connect(self._go_home)
        quick_layout.addWidget(self.home_button)
        
        layout.addWidget(quick_bar)
        
        # The tree view itself
        self.tree_view = QTreeView()
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(20)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.clicked.connect(self._on_item_clicked)
        
        layout.addWidget(self.tree_view)
    
    def _setup_model(self):
        """Set up our file system model with smart filtering"""
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        
        # Only show directories and images
        self.model.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files)
        image_filters = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp"]
        self.model.setNameFilters(image_filters)
        self.model.setNameFilterDisables(False)  # Hide non-matching files
        
        # Only show the file name column
        self.tree_view.setModel(self.model)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)
    
    def _setup_context_menu(self):
        """Create our helpful right-click menu"""
        self.context_menu = QMenu(self)
        
        # Add some useful actions
        self.favorite_action = QAction("⭐ Add to Favorites", self)
        self.favorite_action.triggered.connect(self._toggle_favorite)
        self.context_menu.addAction(self.favorite_action)
        
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_context_menu)
    
    def _on_item_clicked(self, index):
        """Handle clicks on files and folders"""
        path = self.model.filePath(index)
        path_obj = Path(path)
        
        if path_obj.is_dir():
            self.folder_selected.emit(path)
            self.current_path = path_obj
        elif path_obj.is_file():
            self.file_selected.emit(path)
    
    def _apply_filter(self, text: str):
        """Filter the tree view based on search text"""
        if not text:
            # Reset to show everything
            self.model.setNameFilters(["*"])
            return
            
        # Filter based on text input
        filters = [f"*{text}*"]  # Simple wildcard filter
        self.model.setNameFilters(filters)
    
    def _go_home(self):
        """Jump back to home directory"""
        home = str(Path.home())
        index = self.model.index(home)
        self.tree_view.setCurrentIndex(index)
        self.tree_view.expand(index)
        self.folder_selected.emit(home)
    
    def _show_context_menu(self, position):
        """Show our context menu"""
        index = self.tree_view.indexAt(position)
        if index.isValid():
            path = self.model.filePath(index)
            is_favorite = path in self.favorite_paths
            
            # Update favorite action text
            self.favorite_action.setText(
                "⭐ Remove from Favorites" if is_favorite 
                else "⭐ Add to Favorites"
            )
            
            self.context_menu.exec(self.tree_view.viewport().mapToGlobal(position))
    
    def _toggle_favorite(self):
        """Add/remove from favorites"""
        index = self.tree_view.currentIndex()
        if index.isValid():
            path = self.model.filePath(index)
            if path in self.favorite_paths:
                self.favorite_paths.remove(path)
                self.logger.info(f"Removed from favorites: {path}")
            else:
                self.favorite_paths.add(path)
                self.logger.info(f"Added to favorites: {path}")
            
            # Update favorites display (we'll add this feature later!)
    
    def navigate_to(self, path: str):
        """Jump to a specific path"""
        index = self.model.index(path)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.tree_view.expand(index)
            self.folder_selected.emit(path)
    
    def get_current_path(self) -> Optional[Path]:
        """Get the currently selected path"""
        return self.current_path
