class ThemeManager:
    """Manages our fancy game-inspired themes! ✨"""
    
    def __init__(self):
        # Base path for theme resources
        self.theme_path = Path("themes")
        
        # Theme-specific style templates
        self.style_templates = {
            "nier": """
                QMainWindow {
                    background-image: url(themes/nier/background.png);
                    background-repeat: no-repeat;
                    background-position: center;
                }
                
                QListWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 5px;
                }
                
                QPushButton {
                    background-color: rgba(200, 200, 200, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.5);
                    color: #ffffff;
                    padding: 5px 15px;
                    font-family: 'Arial';  /* We can change this to match Nier's font */
                }
                
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                
                QLabel#imageLabel {
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    background-color: rgba(0, 0, 0, 0.2);
                }
            """,
            
            "ffxiv": """
                QMainWindow {
                    background-image: url(themes/ffxiv/background.png);
                    border: 2px solid #8b7355;
                }
                
                QListWidget {
                    background-color: rgba(20, 20, 20, 0.8);
                    border: 1px solid #8b7355;
                    color: #e0c9a6;
                }
                
                QPushButton {
                    background-color: #2a2117;
                    border: 1px solid #8b7355;
                    color: #e0c9a6;
                    border-radius: 3px;
                }
                
                QPushButton:hover {
                    background-color: #3d3122;
                    border: 1px solid #c4a977;
                }
            """
        }
    
    def load_theme_resources(self, theme_name: str):
        """Loads all our pretty theme elements! 🎨"""
        theme_folder = self.theme_path / theme_name
        resources = {
            "background": theme_folder / "background.png",
            "button_normal": theme_folder / "button.png",
            "button_hover": theme_folder / "button_hover.png",
            "frame": theme_folder / "frame.png",
            "loading": theme_folder / "loading.gif"  # For our fancy loading animation!
        }
        return resources
    
    def apply_theme(self, widget, theme_name: str):
        """Makes everything look gorgeous! ✨"""
        if theme_name in self.style_templates:
            widget.setStyleSheet(self.style_templates[theme_name])
