from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton,
    QGroupBox, QFormLayout, QLineEdit,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Dict
import json

@dataclass
class ImageMetadata:
    """All the cozy details about our images! 📝"""
    # Basic info
    filename: str
    path: Path
    size_bytes: int = 0
    dimensions: tuple[int, int] = (0, 0)
    format: str = ""
    
    # Dataset-specific info
    caption: str = ""
    tags: list[str] = field(default_factory=list)
    category: str = ""
    
    # AI generation info (if applicable)
    prompt: str = ""
    negative_prompt: str = ""
    model: str = ""
    
    def to_dict(self) -> Dict:
        """Pack up our metadata for storage"""
        return {
            "basic_info": {
                "filename": self.filename,
                "size_bytes": self.size_bytes,
                "dimensions": self.dimensions,
                "format": self.format
            },
            "dataset_info": {
                "caption": self.caption,
                "tags": self.tags,
                "category": self.category
            },
            "ai_info": {
                "prompt": self.prompt,
                "negative_prompt": self.negative_prompt,
                "model": self.model
            }
        }

class MetadataPanel(QWidget):
    """Our friendly metadata editor! 📝"""
    
    # Let others know when we make changes
    metadata_updated = pyqtSignal(ImageMetadata)
    caption_updated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_metadata: Optional[ImageMetadata] = None
        
        # Create our cozy editing space
        self._setup_ui()
        
    def _setup_ui(self):
        """Build our editing interface"""
        layout = QVBoxLayout(self)
        
        # Make everything scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Caption editing section
        caption_group = QGroupBox("Caption ✍️")
        caption_layout = QVBoxLayout()
        
        self.caption_edit = QTextEdit()
        self.caption_edit.setPlaceholderText("Describe this image...")
        self.caption_edit.textChanged.connect(self._on_caption_changed)
        
        caption_layout.addWidget(self.caption_edit)
        caption_group.setLayout(caption_layout)
        self.content_layout.addWidget(caption_group)
        
        # Tags section
        tags_group = QGroupBox("Tags 🏷️")
        tags_layout = QVBoxLayout()
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Add tags (comma separated)")
        self.tags_edit.textChanged.connect(self._on_tags_changed)
        
        tags_layout.addWidget(self.tags_edit)
        tags_group.setLayout(tags_layout)
        self.content_layout.addWidget(tags_group)
        
        # AI info section (if available)
        ai_group = QGroupBox("AI Generation Info 🤖")
        ai_layout = QFormLayout()
        
        self.prompt_edit = QLineEdit()
        self.negative_prompt_edit = QLineEdit()
        self.model_edit = QLineEdit()
        
        ai_layout.addRow("Prompt:", self.prompt_edit)
        ai_layout.addRow("Negative:", self.negative_prompt_edit)
        ai_layout.addRow("Model:", self.model_edit)
        
        ai_group.setLayout(ai_layout)
        self.content_layout.addWidget(ai_group)
        
        # File info display
        info_group = QGroupBox("Image Info 🖼️")
        info_layout = QFormLayout()
        
        self.filename_label = QLabel()
        self.size_label = QLabel()
        self.dimensions_label = QLabel()
        self.format_label = QLabel()
        
        info_layout.addRow("File:", self.filename_label)
        info_layout.addRow("Size:", self.size_label)
        info_layout.addRow("Dimensions:", self.dimensions_label)
        info_layout.addRow("Format:", self.format_label)
        
        info_group.setLayout(info_layout)
        self.content_layout.addWidget(info_group)
        
        # Save button
        self.save_button = QPushButton("💾 Save Changes")
        self.save_button.clicked.connect(self._save_metadata)
        self.content_layout.addWidget(self.save_button)
        
        # Some breathing room at the bottom
        self.content_layout.addStretch()
