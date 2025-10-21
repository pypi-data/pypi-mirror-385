"""
Structured output schemas for AI processing results.

This module defines Pydantic models for structured AI responses,
enabling type-safe and validated output from AI processors.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Content types extracted from images."""
    TABLE = "table"
    TEXT = "text"
    NON_TEXT = "non_text"
    MIXED = "mixed"


class ContentDetails(BaseModel):
    """Detailed content analysis from image processing."""
    table_content: Optional[str] = Field(None, description="Table content extracted from the image")
    text_content: Optional[str] = Field(None, description="Text content extracted from the image")
    non_text_content: Optional[str] = Field(None, description="Non-text content (diagrams, charts, etc.) from the image")
    content_summary: Optional[str] = Field(None, description="Brief summary of the content")
    key_elements: List[str] = Field(default_factory=list, description="Key elements identified in the image")
    document_structure: Optional[str] = Field(None, description="Document structure information (headers, sections, etc.)")


class ProcessingMetadata(BaseModel):
    """Metadata about the AI processing."""
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the analysis")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    model_used: Optional[str] = Field(None, description="AI model used for processing")
    content_density: Optional[str] = Field(None, description="Content density (low, medium, high)")
    language_detected: Optional[str] = Field(None, description="Primary language detected")
    content_quality: Optional[str] = Field(None, description="Quality assessment of the content")


class StructuredImageResult(BaseModel):
    """Structured result from AI image processing."""
    # Original image reference
    image_id: str = Field(..., description="Unique identifier for the processed image")
    original_image_hash: str = Field(..., description="Hash of the original image for reference")

    # Primary extracted content
    summary_text: str = Field(..., description="Main summary text extracted from the image")
    content_type: ContentType = Field(..., description="Primary content type identified")

    # Detailed content analysis
    content_details: ContentDetails = Field(..., description="Detailed content analysis")

    # Processing metadata
    processing_metadata: ProcessingMetadata = Field(..., description="Processing metadata and quality metrics")

    # Additional information
    tags: List[str] = Field(default_factory=list, description="Tags associated with the content")
    categories: List[str] = Field(default_factory=list, description="Content categories")

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            ContentType: lambda v: v.value
        }


class BatchProcessingResult(BaseModel):
    """Result for batch processing of multiple images."""
    batch_id: str = Field(..., description="Unique identifier for the batch")
    total_images: int = Field(..., description="Total number of images in batch")
    successful_count: int = Field(..., description="Number of successfully processed images")
    failed_count: int = Field(..., description="Number of failed processing attempts")

    results: List[StructuredImageResult] = Field(..., description="Individual processing results")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Processing errors if any")

    batch_summary: str = Field(..., description="Summary of the entire batch processing")
    total_processing_time: Optional[float] = Field(None, description="Total processing time for the batch")

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_images == 0:
            return 0.0
        return (self.successful_count / self.total_images) * 100.0


# Response format schemas for different AI providers
class ResponseFormatSchema(BaseModel):
    """Schema for defining expected response format from AI providers."""
    type: str = Field("json_object", description="Response format type")
    json_schema: Dict[str, Any] = Field(..., description="JSON schema for the response")

    @classmethod
    def for_structured_result(cls) -> "ResponseFormatSchema":
        """Create response format for structured image result."""
        return cls(
            type="json_object",
            json_schema=StructuredImageResult.model_json_schema()
        )


# Utility functions for schema management
def create_image_analysis_schema() -> Dict[str, Any]:
    """Create a simplified schema for basic image analysis."""
    return {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Brief summary of what's in the image"
            },
            "content_type": {
                "type": "string",
                "enum": ["table", "text", "non_text", "mixed"],
                "description": "Primary type of content in the image"
            },
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key points or information extracted from the image"
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1,
                "description": "Confidence score of the analysis"
            }
        },
        "required": ["summary", "content_type", "key_points", "confidence"]
    }


def create_contract_analysis_schema() -> Dict[str, Any]:
    """Create schema specifically for contract/document analysis."""
    return {
        "type": "object",
        "properties": {
            "document_type": {
                "type": "string",
                "description": "Type of document (contract, invoice, form, etc.)"
            },
            "title": {
                "type": "string",
                "description": "Document title or main heading"
            },
            "parties": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Parties mentioned in the document"
            },
            "key_terms": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key terms or amounts mentioned"
            },
            "dates": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Important dates mentioned"
            },
            "summary": {
                "type": "string",
                "description": "Detailed summary of the document content"
            },
            "page_number": {
                "type": "integer",
                "description": "Page number if visible"
            }
        },
        "required": ["document_type", "summary"]
    }