import sys
from PyQt6.QtWidgets import QApplication
from ui import MainWindow  # Import our main window class

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow() # Initialize our main window.
    window.show()
    sys.exit(app.exec())