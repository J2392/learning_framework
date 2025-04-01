# utils/__init__.py

"""
Utils package initialization
"""

from .logger import setup_logger
from .error_handlers import (
    handle_400_error,
    handle_404_error,
    handle_500_error
)

__all__ = [
    'setup_logger',
    'handle_400_error',
    'handle_404_error',
    'handle_500_error'
]