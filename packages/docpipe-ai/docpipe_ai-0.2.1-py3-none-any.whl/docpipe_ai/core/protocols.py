"""
Core Protocol definitions for docpipe-ai Protocol-oriented + Mixin architecture.

This module defines the fundamental capabilities and contracts that components
must adhere to. Protocols define "what" a component can do, while Mixins provide
"how" it does it.
"""

from typing import Protocol, runtime_checkable, Dict, Any, List, Optional, Union
from abc import abstractmethod
from .._types import ImageContent, ProcessedContent, ProcessingMetrics

# === Core Capability Protocols ===

@runtime_checkable
class Batchable(Protocol):
    """
    Protocol for components that can process items in batches.

    Components implementing this protocol can dynamically adjust their
    batch processing strategy based on content characteristics and system load.
    """

    @abstractmethod
    def should_process_batch(self, batch_size: int, total_items: int) -> bool:
        """
        Determine whether a batch should be processed.

        Args:
            batch_size: Size of the current batch
            total_items: Total number of items remaining

        Returns:
            True if the batch should be processed, False otherwise
        """
        ...

    @abstractmethod
    def calculate_optimal_batch_size(self, remaining_items: int) -> int:
        """
        Calculate the optimal batch size for remaining items.

        Args:
            remaining_items: Number of items remaining to process

        Returns:
            Optimal batch size
        """
        ...

@runtime_checkable
class AIProcessable(Protocol):
    """
    Protocol for components that can interact with AI providers.

    Components implementing this protocol can prepare AI requests,
    parse responses, and handle AI-specific logic.
    """

    @abstractmethod
    def prepare_ai_request(self, content: ImageContent) -> Dict[str, Any]:
        """
        Prepare AI request data for the given content.

        Args:
            content: Image content to process

        Returns:
            AI request data dictionary
        """
        ...

    @abstractmethod
    def parse_ai_response(self, response: str) -> str:
        """
        Parse and clean AI response.

        Args:
            response: Raw AI response string

        Returns:
            Parsed and cleaned response text
        """
        ...

    @abstractmethod
    def calculate_confidence(self, content: ImageContent, result: str) -> float:
        """
        Calculate confidence score for the processing result.

        Args:
            content: Original content
            result: Processing result

        Returns:
            Confidence score between 0.0 and 1.0
        """
        ...

@runtime_checkable
class Cacheable(Protocol):
    """
    Protocol for components that can cache and retrieve results.

    Components implementing this protocol can improve performance by
    caching processing results and avoiding redundant AI calls.
    """

    @abstractmethod
    def get_cache_key(self, content: ImageContent) -> str:
        """
        Generate a unique cache key for the given content.

        Args:
            content: Content to generate cache key for

        Returns:
            Unique cache key string
        """
        ...

    @abstractmethod
    def is_cache_valid(self, content: ImageContent, cached_result: ProcessedContent) -> bool:
        """
        Check if cached result is still valid for the given content.

        Args:
            content: Current content
            cached_result: Previously cached result

        Returns:
            True if cache is valid, False otherwise
        """
        ...

@runtime_checkable
class Processable(Protocol):
    """
    Protocol for components that can process content.

    Components implementing this protocol can determine if they can
    process specific types of content and execute the processing.
    """

    @abstractmethod
    def can_process(self, content: ImageContent) -> bool:
        """
        Determine if the component can process the given content.

        Args:
            content: Content to check

        Returns:
            True if content can be processed, False otherwise
        """
        ...

# === Supporting Protocols ===

@runtime_checkable
class ContentValidator(Protocol):
    """
    Protocol for content validation.

    Components implementing this protocol can validate input content
    before processing to ensure data integrity and compatibility.
    """

    @abstractmethod
    def validate_content(self, content: ImageContent) -> List[str]:
        """
        Validate content and return list of validation errors.

        Args:
            content: Content to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        ...

    @abstractmethod
    def detect_image_format(self, binary_data: Union[bytes, str]) -> Dict[str, Any]:
        """
        Detect image format and provide detailed format information.

        Args:
            binary_data: Binary image data (bytes or base64 string)

        Returns:
            Dictionary containing format information:
            {
                'format': 'jpeg|png|gif|bmp|tiff|unknown',
                'confidence': 'high|medium|low',
                'mime_type': 'image/jpeg|image/png|...',
                'details': 'Additional format-specific information'
            }
        """
        ...

@runtime_checkable
class ErrorHandler(Protocol):
    """
    Protocol for error handling and recovery.

    Components implementing this protocol can handle processing errors,
    implement retry logic, and provide graceful fallbacks.
    """

    @abstractmethod
    def handle_processing_error(self, content: ImageContent, error: Exception) -> ProcessedContent:
        """
        Handle processing errors and create fallback result.

        Args:
            content: Content that failed to process
            error: Exception that occurred

        Returns:
            Fallback processed content with error information
        """
        ...

    @abstractmethod
    def should_retry(self, content: ImageContent, error: Exception, attempt: int) -> bool:
        """
        Determine if processing should be retried.

        Args:
            content: Content that failed to process
            error: Exception that occurred
            attempt: Current attempt number

        Returns:
            True if should retry, False otherwise
        """
        ...

@runtime_checkable
class MetricsCollector(Protocol):
    """
    Protocol for metrics collection and monitoring.

    Components implementing this protocol can collect performance metrics,
    processing statistics, and monitoring data.
    """

    @abstractmethod
    def collect_processing_metrics(self, content: ImageContent, result: ProcessedContent) -> ProcessingMetrics:
        """
        Collect metrics for a processing operation.

        Args:
            content: Original content
            result: Processing result

        Returns:
            Processing metrics
        """
        ...

    @abstractmethod
    def record_batch_metrics(self, batch_size: int, processing_time: float, success_count: int) -> None:
        """
        Record batch processing metrics.

        Args:
            batch_size: Size of the processed batch
            processing_time: Time taken to process the batch
            success_count: Number of successfully processed items
        """
        ...

# === Composite Protocols ===

@runtime_checkable
class CompleteProcessor(Batchable, AIProcessable, Cacheable, Processable, ContentValidator, ErrorHandler, MetricsCollector, Protocol):
    """
    Composite protocol that includes all core capabilities.

    Components implementing this protocol provide a complete set of
    capabilities for processing content with batching, AI integration,
    caching, validation, error handling, and metrics collection.
    """
    pass

# === Protocol Utilities ===

def protocol_check(obj: Any, protocol: type) -> bool:
    """
    Utility function to check if an object implements a protocol.

    Args:
        obj: Object to check
        protocol: Protocol class to check against

    Returns:
        True if object implements protocol, False otherwise
    """
    try:
        return isinstance(obj, protocol)
    except TypeError:
        return False

def get_protocol_capabilities(obj: Any) -> List[str]:
    """
    Get list of protocols that an object implements.

    Args:
        obj: Object to check

    Returns:
        List of protocol names that the object implements
    """
    protocols = []

    # Check against known protocols
    if protocol_check(obj, Batchable):
        protocols.append("Batchable")
    if protocol_check(obj, AIProcessable):
        protocols.append("AIProcessable")
    if protocol_check(obj, Cacheable):
        protocols.append("Cacheable")
    if protocol_check(obj, Processable):
        protocols.append("Processable")
    if protocol_check(obj, ContentValidator):
        protocols.append("ContentValidator")
    if protocol_check(obj, ErrorHandler):
        protocols.append("ErrorHandler")
    if protocol_check(obj, MetricsCollector):
        protocols.append("MetricsCollector")
    if protocol_check(obj, CompleteProcessor):
        protocols.append("CompleteProcessor")

    return protocols