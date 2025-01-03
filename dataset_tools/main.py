import sys
import logging
from dataset_tools import logger
from dataset_tools.ui import MainWindow  # Import our main window class
import argparse
def main():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow() # Initialize our main window.
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":

    # Initialize the ArgumentParser object
    parser = argparse.ArgumentParser(description="Set the logging level via command line")

    # Add a command-line argument for the logging level
    parser.add_argument('--log', default='WARNING', help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Configure the logging level based on the parsed argument
    log_level = getattr(logging, args.log.upper())
    logger = logging.getLogger(__name__)

    main()
