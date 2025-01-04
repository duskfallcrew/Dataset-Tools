import sys
import logging
from dataset_tools import logger
from dataset_tools.ui import MainWindow  # Import our main window class
import argparse

def main():
    parser = argparse.ArgumentParser(description="Set the logging level via command line")

    parser.add_argument('--log', default='WARNING', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')

    args = parser.parse_args()

    log_level = getattr(logging, args.log.upper())
    logger = logging.getLogger(__name__)

    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow() # Initialize our main window.
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
