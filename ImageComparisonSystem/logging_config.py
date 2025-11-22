"""
Logging configuration for Image Comparison Tool.
Provides centralized logging setup with both console and file output.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file. If provided, logs to file with rotation.
        console: Whether to output to console (default: True)
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logging(level=logging.DEBUG, log_file=Path("app.log"))
        >>> logger.info("Starting application")
    """
    logger = logging.getLogger("ImageComparison")
    logger.setLevel(logging.DEBUG)  # Logger catches everything, handlers filter
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '[%(levelname)-8s] %(name)s - %(message)s'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)-8s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation (optional)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # File gets everything
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger() -> logging.Logger:
    """
    Get the application logger.
    
    Returns:
        Logger instance (must be initialized with setup_logging first)
    """
    return logging.getLogger("ImageComparison")


# Log level constants for easy reference
LOG_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}
