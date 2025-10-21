"""
Base processor classes for docpipe-ai.

This module provides abstract base classes for processors that combine
protocols and mixins in a standardized way.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Iterator
from abc import ABC, abstractmethod
import logging

from ..core.protocols import CompleteProcessor
from ..data.content import ImageContent, ProcessedContent

logger = logging.getLogger(__name__)


class BaseProcessor(ABC):
    """
    Base processor class that provides common functionality.

    This class defines the standard interface that all processors should follow,
    while allowing specific implementations to handle different types of content
    and processing strategies.
    """

    def __init__(self):
        """Initialize the base processor."""
        self._processor_stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }

    @abstractmethod
    def process_single(self, content: ImageContent) -> ProcessedContent:
        """
        Process a single content item.

        Args:
            content: The content to process

        Returns:
            Processed content result
        """
        pass

    @abstractmethod
    def process_batch(self, contents: List[ImageContent]) -> List[ProcessedContent]:
        """
        Process a batch of content items.

        Args:
            contents: List of content items to process

        Returns:
            List of processed content results
        """
        pass

    def process_iterator(self, contents: Iterator[ImageContent]) -> Iterator[ProcessedContent]:
        """
        Process content from an iterator.

        Args:
            contents: Iterator of content items

        Yields:
            Processed content results
        """
        # Convert iterator to list for batch processing
        # Note: For large datasets, this might need memory optimization
        content_list = list(contents)

        # Process as batch
        results = self.process_batch(content_list)

        # Yield results one by one
        for result in results:
            yield result

    def get_base_stats(self) -> Dict[str, Any]:
        """
        Get base processor statistics.

        Returns:
            Dictionary with basic processing statistics
        """
        stats = self._processor_stats.copy()

        if stats['total_processed'] > 0:
            stats['success_rate'] = stats['successful_processed'] / stats['total_processed']
            stats['failure_rate'] = stats['failed_processed'] / stats['total_processed']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0

        return stats

    def reset_base_stats(self) -> None:
        """Reset base processor statistics."""
        self._processor_stats = {
            'total_processed': 0,
            'successful_processed': 0,
            'failed_processed': 0,
            'total_processing_time': 0.0,
            'average_processing_time': 0.0
        }

    def _update_stats(self, success: bool, processing_time: float) -> None:
        """
        Update processing statistics.

        Args:
            success: Whether processing was successful
            processing_time: Time taken for processing
        """
        self._processor_stats['total_processed'] += 1
        self._processor_stats['total_processing_time'] += processing_time

        if success:
            self._processor_stats['successful_processed'] += 1
        else:
            self._processor_stats['failed_processed'] += 1

        # Update average processing time
        if self._processor_stats['total_processed'] > 0:
            self._processor_stats['average_processing_time'] = (
                self._processor_stats['total_processing_time'] /
                self._processor_stats['total_processed']
            )

    def __str__(self) -> str:
        """String representation of the processor."""
        return f"{self.__class__.__name__}(processed={self._processor_stats['total_processed']})"

    def __repr__(self) -> str:
        """Detailed string representation of the processor."""
        return f"{self.__class__.__name__}(stats={self._processor_stats})"