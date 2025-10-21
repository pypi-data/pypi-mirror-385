"""
API module for docpipe-ai.

This module provides simplified interfaces for using docpipe-ai
without needing to understand the underlying Protocol-oriented architecture.
"""

from .simple_interface import (
    SimpleProcessor,
    process_image,
    process_images,
    process_file,
    create_openai_processor,
    create_anthropic_processor,
    create_processor_from_env
)

__all__ = [
    "SimpleProcessor",
    "process_image",
    "process_images",
    "process_file",
    "create_openai_processor",
    "create_anthropic_processor",
    "create_processor_from_env",
]