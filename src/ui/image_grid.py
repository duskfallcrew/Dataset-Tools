from dataclasses import dataclass
from typing import Optional, Dict
from pathlib import Path
import time

from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from ..utils import get_memory_manager, get_logger
from ..utils.image import create_thumbnail

@dataclass
class ImageLoadRequest:
    """Keeps track of what images we want to load - like a friendly to-do list! 📝"""
    path: Path
    timestamp: float = field(default_factory=time.time)
    priority: int = 0  # Higher numbers = load sooner!

class VirtualizedImageGrid(QListWidget):
    """Our smart image grid that's gentle on memory 🎨"""
    
    # Let others know when interesting things happen
    thumbnail_loaded = pyqtSignal(str)  # When a new thumbnail is ready
    loading_progress = pyqtSignal(int, int)  # Current progress, total images
    
    def __init__(self, thumbnail_size: QSize = QSize(120, 120)):
        super().__init__()
        # Get our helpers
        self.memory_manager = get_memory_manager()
        self.logger = get_logger()
        
        # Remember what size we want our thumbnails
        self.thumbnail_size = thumbnail_size
        
        # Keep track of what we're loading
        self.load_queue: Dict[str, ImageLoadRequest] = {}
        
        # Set up how our grid looks and behaves
        self.setup_grid()
        self.setup_loading_timer()
        
        self.logger.info("Image grid ready for photos! 📸")
    
    def setup_grid(self):
        """Make our grid look and feel just right"""
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setIconSize(self.thumbnail_size)
        self.setSpacing(10)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setWrapping(True)
        self.setUniformItemSizes(True)
        
        # Smart selection behavior
        self.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
    
    def setup_loading_timer(self):
        """Set up our smart loading system"""
        self._load_timer = QTimer()
        self._load_timer.timeout.connect(self._process_load_queue)
        self._load_timer.start(100)  # Check queue every 100ms
    
    def load_folder(self, folder_path: str):
        """Load up a folder of images"""
        self.clear()  # Start fresh!
        folder = Path(folder_path)
        
        # Look for image files
        image_files = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
        total_images = len(image_files)
        
        self.logger.info(f"Found {total_images} images in {folder}")
        
        # Add placeholders for each image
        for i, path in enumerate(image_files):
            self._add_image_placeholder(path)
            self.loading_progress.emit(i + 1, total_images)
    
    def _add_image_placeholder(self, path: Path):
        """Add a temporary placeholder while the real thumbnail loads"""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, str(path))
        item.setSizeHint(self.thumbnail_size)
        self.addItem(item)
        
        # Queue this image for loading
        self.queue_thumbnail(path)
    
    def queue_thumbnail(self, path: Path, priority: int = 0):
        """Add an image to our loading queue"""
        key = str(path)
        if key not in self.load_queue:
            self.load_queue[key] = ImageLoadRequest(path, priority=priority)
    
    def _process_load_queue(self):
        """Check our queue and load any pending thumbnails"""
        if not self.load_queue:
            return
        
        # Process highest priority items first
        current_item = max(
            self.load_queue.values(),
            key=lambda x: (x.priority, -x.timestamp)
        )
        path_key = str(current_item.path)
        
        try:
            # Try to load the thumbnail
            thumb = self._load_thumbnail(current_item.path)
            if thumb:
                self._update_thumbnail(current_item.path, thumb)
                self.thumbnail_loaded.emit(path_key)
        except Exception as e:
            self.logger.error(f"Couldn't load {path_key}: {e}")
        finally:
            # Remove from queue either way
            del self.load_queue[path_key]
    
    def _load_thumbnail(self, path: Path) -> Optional[QPixmap]:
        """Create or retrieve a thumbnail"""
        cache_key = f"thumb_{path}"
        
        # Check if we already have it
        if thumb := self.memory_manager.get_item(cache_key):
            return thumb
            
        # Create new thumbnail
        if thumb := create_thumbnail(path, self.thumbnail_size):
            self.memory_manager.cache_item(cache_key, thumb)
            return thumb
        
        return None
    
    def _update_thumbnail(self, path: Path, thumb: QPixmap):
        """Update an item with its thumbnail"""
        path_str = str(path)
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == path_str:
                item.setIcon(QIcon(thumb))
                break
    
    def cleanup(self):
        """Clean up when we're done"""
        self._load_timer.stop()
        self.clear()
        self.load_queue.clear()
