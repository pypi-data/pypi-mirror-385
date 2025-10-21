"""
Mixin implementations for docpipe-ai Protocol-oriented architecture.

This module provides reusable Mixin classes that implement specific
capabilities defined in the core protocols. Mixins provide the "how"
while protocols define the "what".
"""

from .batch_processing import (
    DynamicBatchingMixin,
    FixedBatchingMixin,
    AdaptiveBatchingMixin,
)

from .ai_processing import (
    OpenAIProcessingMixin,
    AnthropicProcessingMixin,
    GenericAIProcessingMixin,
)

from .caching import (
    MemoryCacheMixin,
    RedisCacheMixin,
    FileCacheMixin,
)

from .validation import (
    ContentValidationMixin,
    ImageValidationMixin,
)

from .error_handling import (
    RetryHandlerMixin,
    FallbackHandlerMixin,
    MetricsCollectionMixin,
)

__all__ = [
    # Batch processing mixins
    "DynamicBatchingMixin",
    "FixedBatchingMixin",
    "AdaptiveBatchingMixin",

    # AI processing mixins
    "OpenAIProcessingMixin",
    "AnthropicProcessingMixin",
    "GenericAIProcessingMixin",

    # Caching mixins
    "MemoryCacheMixin",
    "RedisCacheMixin",
    "FileCacheMixin",

    # Validation mixins
    "ContentValidationMixin",
    "ImageValidationMixin",

    # Error handling mixins
    "RetryHandlerMixin",
    "FallbackHandlerMixin",
    "MetricsCollectionMixin",
]