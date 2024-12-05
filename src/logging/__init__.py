# src/logging/__init__.py

# Our main logging tools - like having a really organized notekeeper
from .setup import get_logger, setup_logging

# We'll let other code know about our logging levels
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
