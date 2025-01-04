from importlib.metadata import version, PackageNotFoundError # setuptools-scm versioning
try:
    __version__ = version("dataset-tools")
except PackageNotFoundError:
    # package is not installed
    pass

import logging
import logging
from logging import Logger
import sys

log_level = "INFO"
msg_init = None
from rich.logging import RichHandler
from rich.console import Console
from rich.logging import RichHandler
handler = RichHandler(console=Console(stderr=True))

if handler is None:
    handler = logging.StreamHandler(sys.stdout)
    handler.propagate = False

formatter = logging.Formatter(
    fmt="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)
logging.root.setLevel(log_level)
logging.root.addHandler(handler)

if msg_init is not None:
    logger = logging.getLogger(__name__)
    logger.info(msg_init)

log_level = getattr(logging, log_level)
logger = logging.getLogger(__name__)

