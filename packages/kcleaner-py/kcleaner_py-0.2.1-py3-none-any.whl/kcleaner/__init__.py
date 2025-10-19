"""
Secure CLI tool to identify and delete KATE backup files (*.~ and .*~) with user confirmation.
"""

from .cli import CliHandler
from .core.styles import SmartStyles
from .core.types import ConfigData
from .utils.logging_utils import LoggingContext, setup_logging
from .utils.validator import SystemValidator
from .utils.file_utils import FileSystemHandler

main = CliHandler().run

__version__ = "0.2.0"
__all__ = [
    "SmartStyles",
    "ConfigData",
    "LoggingContext",
    "setup_logging",
    "SystemValidator",
    "FileSystemHandler",
]
