import logging
import sys
import traceback
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any
from src.SharedKernel.base.Container import Singleton

# Define custom METRIC logging level
METRIC_LEVEL = 25
logging.addLevelName(METRIC_LEVEL, "METRIC")

# ==============================
# Interface
# ==============================
class ILogger(ABC):
    """Interface for logger implementation."""

    @abstractmethod
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message."""
        pass

    @abstractmethod
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log error message."""
        pass

    @abstractmethod
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""
        pass

    @abstractmethod
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""
        pass

    @abstractmethod
    def metric(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log metric message."""
        pass

# ==============================
# Implementation
# ==============================
@Singleton
class Logger(ILogger):
    """Logger implementation using Python's logging module."""

    def __init__(self, name: str = __name__) -> None:
        """Initialize logger with name."""
        if not logging.getLogger().handlers:
            setup_logging()
        self._logger = logging.getLogger(name)

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(message, *args, **kwargs)

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(message, *args, **kwargs)

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(message, *args, **kwargs)

    def metric(self, message: str, *args: Any, **kwargs: Any) -> None:
        """Log metric message at custom METRIC level."""
        self._logger.log(METRIC_LEVEL, message, *args, **kwargs)

def setup_logging() -> None:
    """Configure basic logging for the application."""
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with red color for ERROR level, blue for INFO level, and purple for METRIC level."""
        
        RED = '\033[91m'
        BLUE = '\033[94m'
        GREEN = '\033[38;2;120;66;245m'
        RESET = '\033[0m'
        
        def format(self, record):
            message = record.getMessage()
            
            if record.levelno == logging.ERROR:
                # Use traceback to get caller information
                tb = traceback.extract_stack()
                # Find the caller frame (skip logging frames)
                for frame in reversed(tb):
                    if 'logging' not in frame.filename and 'Logger.py' not in frame.filename:
                        file_path = frame.filename
                        line_no = frame.lineno
                        
                        # Try to extract feature folder and filename
                        if 'src' in file_path:
                            try:
                                parts = file_path.split('src\\')
                                if len(parts) > 1:
                                    relative_path = parts[1].replace('\\', '/')
                                    return f"{self.RED}[ERROR]: {relative_path}:{line_no} - {message}{self.RESET}"
                            except:
                                pass
                        
                        return f"{self.RED}[ERROR]: {file_path}:{line_no} - {message}{self.RESET}"
                
                return f"{self.RED}[ERROR]: {message}{self.RESET}"
            elif record.levelno == logging.INFO:
                return f"{self.BLUE}[INFO]: {message}{self.RESET}"
            elif record.levelno == METRIC_LEVEL:
                return f"{self.GREEN}[METRIC]: {message}{self.RESET}"
            else:
                return f"{message}"
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())
    
    # Remove existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
    
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def get_logger(name: str) -> Logger:
    """
    Get a Logger instance with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured Logger instance.
    """
    return Logger(name)


# Setup logging when module is imported
setup_logging()


# Default logger for the module
logger = get_logger(__name__)
