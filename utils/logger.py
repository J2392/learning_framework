# utils/logger.py
"""
Logging configuration
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logger(name: str = __name__, 
                log_file: Optional[str] = None,
                level: int = logging.DEBUG) -> logging.Logger:
    """
    Set up logger with consistent configuration
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # Create file handler if log file specified
    if log_file:
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger

# Create default logger
logger = setup_logger(
    'learning_framework',
    os.path.join('logs', 'app.log')
)