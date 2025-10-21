"""
Enhanced type definitions for Protocol-oriented docpipe-ai.

Provides Protocol-oriented types, data structures, and common annotations.
"""

from typing import Protocol, runtime_checkable, TypeVar, Generic, Dict, Any, List, Iterator, Union, Optional
from pathlib import Path
from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum

# === Type Variables ===

T = TypeVar('T')
ContentType = TypeVar('ContentType')
ProcessType = TypeVar('ProcessType')

# === Enums ===

class ContentFormat(str, Enum):
    """内容格式枚举"""
    PNG = "png"
    JPEG = "jpeg"
    GIF = "gif"
    BMP = "bmp"
    WEBP = "webp"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

# === Core Data Structures ===

@dataclass
class BoundingBox:
    """边界框"""
    x: float
    y: float
    width: float
    height: float

    def to_list(self) -> List[float]:
        """转换为列表格式 [x, y, width, height]"""
        return [self.x, self.y, self.width, self.height]

    @classmethod
    def from_list(cls, bbox_list: List[float]) -> "BoundingBox":
        """从列表创建"""
        if len(bbox_list) != 4:
            raise ValueError(f"Bounding box must have 4 elements, got {len(bbox_list)}")
        return cls(x=bbox_list[0], y=bbox_list[1], width=bbox_list[2], height=bbox_list[3])

@dataclass
class ImageMetadata:
    """图片元数据"""
    format: ContentFormat = ContentFormat.UNKNOWN
    size_bytes: int = 0
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    color_space: Optional[str] = None
    dpi: Optional[float] = None

@dataclass
class ImageContent:
    """图片内容对象"""
    binary_data: bytes
    page: int
    bbox: BoundingBox
    doc_id: Optional[str] = None
    metadata: Optional[ImageMetadata] = None

    def __post_init__(self):
        """后处理：确保数据有效性"""
        if not self.binary_data:
            raise ValueError("binary_data cannot be empty")
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not isinstance(self.bbox, BoundingBox):
            self.bbox = BoundingBox.from_list(self.bbox) if isinstance(self.bbox, list) else BoundingBox(0, 0, 100, 100)

@dataclass
class ProcessingMetrics:
    """处理指标"""
    processing_time: float
    confidence: float
    token_usage: int = 0
    cache_hit: bool = False
    retry_count: int = 0

@dataclass
class ProcessedContent:
    """处理后的内容对象"""
    original: ImageContent
    processed_text: str
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    metrics: Optional[ProcessingMetrics] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """后处理：确保数据一致性"""
        if self.status == ProcessingStatus.COMPLETED and not self.processed_text.strip():
            self.status = ProcessingStatus.FAILED
            self.error_message = "Empty processed text"
        elif self.status == ProcessingStatus.FAILED and not self.error_message:
            self.error_message = "Processing failed"

# === Protocol Definitions ===

@runtime_checkable
class Batchable(Protocol):
    """可批量处理的协议"""

    @abstractmethod
    def should_process_batch(self, batch_size: int, total_items: int) -> bool:
        """判断是否应该处理这个批次"""
        ...

@runtime_checkable
class AIProcessable(Protocol):
    """AI可处理的协议"""

    @abstractmethod
    def prepare_ai_request(self, content: ImageContent) -> Dict[str, Any]:
        """准备AI请求"""
        ...

    @abstractmethod
    def parse_ai_response(self, response: str) -> str:
        """解析AI响应"""
        ...

@runtime_checkable
class Cacheable(Protocol):
    """可缓存的协议"""

    @abstractmethod
    def get_cache_key(self, content: ImageContent) -> str:
        """获取缓存键"""
        ...

    @abstractmethod
    def is_cache_valid(self, content: ImageContent, cached_result: ProcessedContent) -> bool:
        """检查缓存是否有效"""
        ...

@runtime_checkable
class Processable(Protocol):
    """可处理的协议"""

    @abstractmethod
    def can_process(self, content: ImageContent) -> bool:
        """判断是否可以处理该内容"""
        ...

# === Legacy Type Support ===

# Document block type (legacy support)
DocumentBlock = Dict[str, Any]

# Stream types (legacy support)
DocumentStream = Iterator[DocumentBlock]
ProcessedStream = Iterator[DocumentBlock]

# === Configuration Types ===

@dataclass
class ProcessingConfig:
    """处理配置"""
    max_concurrency: int = 5
    batch_size_strategy: str = "dynamic"  # dynamic, fixed, adaptive
    ai_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    language: str = "zh"  # zh, en
    enable_caching: bool = True
    retry_attempts: int = 3
    timeout_seconds: int = 30
    max_tokens: int = 500
    temperature: float = 0.7

@dataclass
class BatchConfig:
    """批次配置"""
    max_size: int = 100
    min_size: int = 1
    strategy: str = "dynamic"
    adaptive_threshold: int = 50
    max_wait_time: float = 30.0

@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    max_size: int = 1000
    ttl_seconds: int = 3600
    key_prefix: str = "docpipe_ai"

# === Type Aliases ===

# Content types
ImageList = List[ImageContent]
ProcessedImageList = List[ProcessedContent]
ContentIterator = Iterator[ImageContent]
ProcessedIterator = Iterator[ProcessedContent]

# File path types (legacy support)
FilePath = Union[str, Path]

# OpenAI types (legacy support)
OpenAIParams = Dict[str, Any]
ModelName = str
APIKey = Optional[str]
APIBase = Optional[str]

# Batch processing types (legacy support)
BatchSize = int
ConcurrencyLevel = Optional[int]
PeekHeadSize = int

# === Generic Types ===

ProcessorType = TypeVar('ProcessorType', bound=Processable)
BatchProcessorType = TypeVar('BatchProcessorType', bound=Batchable)
AIProcessorType = TypeVar('AIProcessorType', bound=AIProcessable)
CacheProcessorType = TypeVar('CacheProcessorType', bound=Cacheable)