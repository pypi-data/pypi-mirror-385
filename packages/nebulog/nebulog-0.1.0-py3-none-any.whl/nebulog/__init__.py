"""Extension for Loguru to better integrate Rich outputs in logging messages."""

import atexit
import sys

from loguru import logger
from loguru._defaults import LOGURU_AUTOINIT, LOGURU_LEVEL

from nebulog.config import install
from nebulog.handler import NebulogHandler

# Placeholder for poetry-dynamic-versioning, do not change:
# https://github.com/mtkennerly/poetry-dynamic-versioning#installation
__version__ = "0.1.0"

__all__ = ["NebulogHandler", "install", "logger"]

if LOGURU_AUTOINIT and sys.stderr:
    install(level=LOGURU_LEVEL)

atexit.register(logger.remove)
