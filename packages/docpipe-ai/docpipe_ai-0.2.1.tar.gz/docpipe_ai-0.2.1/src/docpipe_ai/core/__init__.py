"""
Core protocols and interfaces for docpipe-ai.

This module provides the fundamental Protocol definitions that define
capabilities and contracts for the Protocol-oriented + Mixin architecture.
"""

from .protocols import (
    Batchable,
    AIProcessable,
    Cacheable,
    Processable,
    ContentValidator,
    ErrorHandler,
    MetricsCollector,
)

__all__ = [
    "Batchable",
    "AIProcessable",
    "Cacheable",
    "Processable",
    "ContentValidator",
    "ErrorHandler",
    "MetricsCollector",
]