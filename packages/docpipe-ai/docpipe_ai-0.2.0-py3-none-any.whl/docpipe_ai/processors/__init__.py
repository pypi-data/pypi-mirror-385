"""
Processor implementations for docpipe-ai.

This module provides concrete processor implementations that combine protocols
and mixins to create specialized processing capabilities.
"""

from .base_processor import BaseProcessor
from .adaptive_image_processor import AdaptiveImageProcessor
from .batch_processor import BatchProcessor

__all__ = [
    "BaseProcessor",
    "AdaptiveImageProcessor",
    "BatchProcessor",
]