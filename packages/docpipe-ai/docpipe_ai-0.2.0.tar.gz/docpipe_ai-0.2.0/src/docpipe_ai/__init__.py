"""
docpipe-ai: Protocol-oriented & Mixin-based AI content processor for docpipe-mini.

Main entry point for the docpipe-ai package.

This package provides a flexible, extensible architecture for AI-powered content analysis
with adaptive batch processing, caching, validation, and multi-provider support.
"""

# New Protocol-oriented API (recommended)
from .api import (
    SimpleProcessor,
    process_image,
    process_images,
    process_file,
    create_openai_processor,
    create_anthropic_processor,
    create_processor_from_env
)

# Core components for advanced usage
from .core.protocols import Batchable, AIProcessable, Cacheable, CompleteProcessor
from .data.content import ImageContent, ProcessedContent
from .data.config import ProcessingConfig, AIProviderConfig
from .processors.adaptive_image_processor import AdaptiveImageProcessor
from .providers.factory import ProviderFactory

# Legacy pipeline support (deprecated)
from .pipelines._base import BasePipeline, PipelineConfig
from .pipelines.openai_compat import OpenAIPipeline

__version__ = "0.2.0"

# Public API - recommended usage
__all__ = [
    # Simple API (recommended for most users)
    "SimpleProcessor",
    "process_image",
    "process_images",
    "process_file",
    "create_openai_processor",
    "create_anthropic_processor",
    "create_processor_from_env",

    # Core components (for advanced users)
    "Batchable",
    "AIProcessable",
    "Cacheable",
    "CompleteProcessor",
    "ImageContent",
    "ProcessedContent",
    "ProcessingConfig",
    "AIProviderConfig",
    "AdaptiveImageProcessor",
    "ProviderFactory",
]

# Legacy support (marked internal)
_legacy_all = ["BasePipeline", "PipelineConfig", "OpenAIPipeline"]