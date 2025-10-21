"""
Data structures and configuration classes for docpipe-ai.

This module provides the core data structures used throughout the
Protocol-oriented + Mixin architecture.
"""

from .content import (
    BoundingBox,
    ImageMetadata,
    ImageContent,
    ProcessedContent,
    ProcessingMetrics,
)

from .config import (
    ProcessingConfig,
    BatchConfig,
    CacheConfig,
    AIProviderConfig,
)

__all__ = [
    # Content structures
    "BoundingBox",
    "ImageMetadata",
    "ImageContent",
    "ProcessedContent",
    "ProcessingMetrics",

    # Configuration classes
    "ProcessingConfig",
    "BatchConfig",
    "CacheConfig",
    "AIProviderConfig",
]