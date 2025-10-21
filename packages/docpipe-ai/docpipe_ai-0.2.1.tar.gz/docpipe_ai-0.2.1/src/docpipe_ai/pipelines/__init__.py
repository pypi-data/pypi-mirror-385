"""
Pipeline implementations for docpipe-ai.

This package contains various pipeline implementations that can process document blocks
using different AI backends while maintaining the same interface.
"""

from ._base import BasePipeline, PipelineConfig
from .openai_compat import OpenAIPipeline

__all__ = ["BasePipeline", "PipelineConfig", "OpenAIPipeline"]