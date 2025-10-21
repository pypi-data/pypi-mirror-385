"""
Base pipeline interface for docpipe-ai.

Defines the abstract BasePipeline class that all pipeline implementations must follow.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Iterator, Any, Optional, Union
from pathlib import Path


class BasePipeline(ABC):
    """
    Abstract base class for all docpipe-ai pipelines.

    Defines the common interface that all pipeline implementations must follow.
    Pipelines are responsible for processing document blocks and updating
    only the 'text' field while preserving all other fields.
    """

    @abstractmethod
    def iter_file(self, file_path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
        """
        Process a file and return an iterator of processed blocks.

        Args:
            file_path: Path to the file to process

        Returns:
            Iterator of dictionaries where only the 'text' field is updated.
            All other fields (type, bbox, page, etc.) remain unchanged.

        Example:
            >>> pipeline = OpenAIPipeline(model="gpt-4o")
            >>> for block in pipeline.iter_file("document.pdf"):
            ...     print(block)
            {'doc_id': '...', 'page': 1, 'bbox': [...], 'type': 'image', 'text': 'AI generated description'}
        """
        pass

    @abstractmethod
    def iter_stream(self, stream: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Process a stream of document blocks.

        Args:
            stream: Iterator of document blocks to process

        Returns:
            Iterator of processed blocks where only the 'text' field is updated.

        Example:
            >>> blocks = docpipe_mini("document.pdf")  # Returns Iterator[Dict]
            >>> pipeline = OpenAIPipeline(model="gpt-4o")
            >>> processed = pipeline.iter_stream(blocks)
            >>> for block in processed:
            ...     print(block['text'])  # AI-generated text
        """
        pass

    def _should_process_block(self, block: Dict[str, Any]) -> bool:
        """
        Determine if a block should be processed.

        Default implementation processes blocks with empty or whitespace-only text.
        Subclasses can override for custom logic.

        Args:
            block: Document block dictionary

        Returns:
            True if the block should be processed, False otherwise
        """
        text = block.get("text", "")
        return not text or text.strip() == ""

    def _preserve_block_structure(self, block: Dict[str, Any], new_text: str) -> Dict[str, Any]:
        """
        Create a new block with updated text while preserving all other fields.

        Args:
            block: Original document block
            new_text: New text to assign to the 'text' field

        Returns:
            New block dictionary with updated text field
        """
        # Create a copy to avoid mutating the original
        result = block.copy()
        result["text"] = new_text
        return result

    def _validate_block_schema(self, block: Dict[str, Any]) -> bool:
        """
        Validate that a block follows the expected schema.

        Args:
            block: Document block to validate

        Returns:
            True if the block schema is valid, False otherwise
        """
        # Basic validation - check for required fields
        required_fields = ["doc_id", "type", "text"]
        return all(field in block for field in required_fields)


class PipelineConfig:
    """
    Configuration container for pipeline parameters.

    Provides a common way to manage configuration across different pipeline types.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        max_concurrency: Optional[int] = None,
        peek_head: int = 200,
        max_batch_size: int = 100,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs: Any
    ):
        """
        Initialize pipeline configuration.

        Args:
            model: Model name to use for processing
            max_concurrency: Maximum number of concurrent operations
            peek_head: Number of items to sample when estimating iterator length
            max_batch_size: Maximum batch size for processing
            api_key: API key for authentication
            api_base: Custom API base URL
            **kwargs: Additional configuration parameters
        """
        self.model = model
        self.max_concurrency = max_concurrency
        self.peek_head = peek_head
        self.max_batch_size = max_batch_size
        self.api_key = api_key
        self.api_base = api_base
        self.extra_params = kwargs

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default."""
        if hasattr(self, key):
            return getattr(self, key)
        return self.extra_params.get(key, default)

    def update(self, **kwargs: Any) -> PipelineConfig:
        """Create a new config with updated parameters."""
        new_params = self.extra_params.copy()
        new_params.update(kwargs)

        return PipelineConfig(
            model=kwargs.get("model", self.model),
            max_concurrency=kwargs.get("max_concurrency", self.max_concurrency),
            peek_head=kwargs.get("peek_head", self.peek_head),
            max_batch_size=kwargs.get("max_batch_size", self.max_batch_size),
            api_key=kwargs.get("api_key", self.api_key),
            api_base=kwargs.get("api_base", self.api_base),
            **{k: v for k, v in new_params.items()
               if k not in ["model", "max_concurrency", "peek_head", "max_batch_size", "api_key", "api_base"]}
        )