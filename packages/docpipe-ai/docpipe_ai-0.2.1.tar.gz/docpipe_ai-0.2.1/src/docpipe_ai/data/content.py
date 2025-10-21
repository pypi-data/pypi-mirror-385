"""
Content data structures for docpipe-ai.

This module defines the core data structures for representing
content and processing results in the Protocol-oriented architecture.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time

# === Enums ===

class ContentFormat(str, Enum):
    """内容格式枚举"""
    PNG = "png"
    JPEG = "jpeg"
    GIF = "gif"
    BMP = "bmp"
    WEBP = "webp"
    TIFF = "tiff"
    UNKNOWN = "unknown"

class ProcessingStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"
    SKIPPED = "skipped"

# === Core Data Structures ===

@dataclass
class BoundingBox:
    """边界框"""
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self):
        """验证边界框数据"""
        if self.width < 0 or self.height < 0:
            raise ValueError("Width and height must be non-negative")
        if self.x < 0 or self.y < 0:
            raise ValueError("X and Y coordinates must be non-negative")

    def to_list(self) -> List[float]:
        """转换为列表格式 [x, y, width, height]"""
        return [self.x, self.y, self.width, self.height]

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height
        }

    @classmethod
    def from_list(cls, bbox_list: List[float]) -> "BoundingBox":
        """从列表创建"""
        if len(bbox_list) != 4:
            raise ValueError(f"Bounding box must have 4 elements, got {len(bbox_list)}")
        return cls(x=bbox_list[0], y=bbox_list[1], width=bbox_list[2], height=bbox_list[3])

    @classmethod
    def from_dict(cls, bbox_dict: dict) -> "BoundingBox":
        """从字典创建"""
        return cls(
            x=bbox_dict.get("x", 0),
            y=bbox_dict.get("y", 0),
            width=bbox_dict.get("width", 100),
            height=bbox_dict.get("height", 100)
        )

    def area(self) -> float:
        """计算面积"""
        return self.width * self.height

    def center(self) -> tuple[float, float]:
        """计算中心点"""
        return (self.x + self.width / 2, self.y + self.height / 2)

@dataclass
class ImageMetadata:
    """图片元数据"""
    format: ContentFormat = ContentFormat.UNKNOWN
    size_bytes: int = 0
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    color_space: Optional[str] = None
    dpi: Optional[float] = None
    compression: Optional[str] = None

    def __post_init__(self):
        """验证元数据"""
        if self.size_bytes < 0:
            raise ValueError("Size in bytes cannot be negative")
        if self.width_pixels is not None and self.width_pixels <= 0:
            raise ValueError("Width in pixels must be positive")
        if self.height_pixels is not None and self.height_pixels <= 0:
            raise ValueError("Height in pixels must be positive")
        if self.dpi is not None and self.dpi <= 0:
            raise ValueError("DPI must be positive")

    @property
    def megapixels(self) -> Optional[float]:
        """计算兆像素数"""
        if self.width_pixels and self.height_pixels:
            return (self.width_pixels * self.height_pixels) / 1_000_000
        return None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "format": self.format.value,
            "size_bytes": self.size_bytes,
            "width_pixels": self.width_pixels,
            "height_pixels": self.height_pixels,
            "color_space": self.color_space,
            "dpi": self.dpi,
            "compression": self.compression,
            "megapixels": self.megapixels
        }

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
            if isinstance(self.bbox, list):
                self.bbox = BoundingBox.from_list(self.bbox)
            elif isinstance(self.bbox, dict):
                self.bbox = BoundingBox.from_dict(self.bbox)
            else:
                self.bbox = BoundingBox(0, 0, 100, 100)

    @property
    def size_bytes(self) -> int:
        """获取二进制数据大小"""
        return len(self.binary_data)

    @property
    def content_hash(self) -> str:
        """计算内容哈希"""
        try:
            return hashlib.md5(self.binary_data).hexdigest()
        except TypeError:
            # 如果bytes类型有问题，转换为字符串再计算
            return hashlib.md5(str(self.binary_data).encode()).hexdigest()

    def generate_doc_id(self) -> str:
        """生成文档ID"""
        content_hash = self.content_hash[:8]
        return f"img_page{self.page}_{content_hash}"

    def to_dict(self) -> dict:
        """转换为字典格式"""
        # 只显示二进制数据的预览，避免输出大量内容
        binary_preview = self._get_binary_preview()

        return {
            "doc_id": self.doc_id or self.generate_doc_id(),
            "page": self.page,
            "bbox": self.bbox.to_list(),
            "binary_data": binary_preview,
            "size_bytes": self.size_bytes,
            "content_hash": self.content_hash,
            "metadata": self.metadata.to_dict() if self.metadata else None
        }

    def _get_binary_preview(self) -> str:
        """获取二进制数据的预览，避免输出完整内容"""
        if len(self.binary_data) <= 20:
            # 如果数据很小，显示全部但标记为小数据
            preview = self.binary_data.hex()
            return f"[{len(self.binary_data)} bytes] {preview}"
        else:
            # 始终只显示前10和后10字节，避免长输出
            start = self.binary_data[:10].hex()
            end = self.binary_data[-10:].hex()
            middle_len = len(self.binary_data) - 20
            return f"[{len(self.binary_data)} bytes] {start}...[{middle_len} bytes]...{end}"

    def __repr__(self) -> str:
        """字符串表示，避免输出大量二进制数据"""
        return (f"ImageContent(doc_id='{self.doc_id or 'unknown'}', "
                f"page={self.page}, size={self.size_bytes} bytes, "
                f"hash='{self.content_hash[:8]}', "
                f"bbox={self.bbox.to_list()})")

    @classmethod
    def from_dict(cls, data: dict) -> "ImageContent":
        """从字典创建"""
        # 处理边界框
        bbox_data = data.get("bbox", [0, 0, 100, 100])
        if isinstance(bbox_data, list):
            bbox = BoundingBox.from_list(bbox_data)
        else:
            bbox = BoundingBox.from_dict(bbox_data)

        # 处理元数据
        metadata_data = data.get("metadata")
        metadata = None
        if metadata_data:
            if isinstance(metadata_data, dict):
                format_value = metadata_data.get("format", "unknown")
                metadata_data["format"] = ContentFormat(format_value)
            metadata = ImageMetadata(**metadata_data) if isinstance(metadata_data, dict) else metadata_data

        return cls(
            binary_data=data.get("binary_data", b""),
            page=data.get("page", 1),
            bbox=bbox,
            doc_id=data.get("doc_id"),
            metadata=metadata
        )

@dataclass
class ProcessingMetrics:
    """处理指标"""
    processing_time: float
    confidence: float
    token_usage: int = 0
    cache_hit: bool = False
    retry_count: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    def __post_init__(self):
        """验证指标数据"""
        if self.processing_time < 0:
            raise ValueError("Processing time cannot be negative")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        if self.token_usage < 0:
            raise ValueError("Token usage cannot be negative")
        if self.retry_count < 0:
            raise ValueError("Retry count cannot be negative")

    @property
    def throughput(self) -> float:
        """计算吞吐量（tokens/秒）"""
        if self.processing_time > 0:
            return self.token_usage / self.processing_time
        return 0.0

    def finish_processing(self) -> None:
        """标记处理完成"""
        self.end_time = time.time()
        self.processing_time = self.end_time - self.start_time

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "processing_time": self.processing_time,
            "confidence": self.confidence,
            "token_usage": self.token_usage,
            "cache_hit": self.cache_hit,
            "retry_count": self.retry_count,
            "throughput": self.throughput,
            "start_time": self.start_time,
            "end_time": self.end_time
        }

@dataclass
class ProcessedContent:
    """处理后的内容对象"""
    original: ImageContent
    processed_text: str
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    metrics: Optional[ProcessingMetrics] = None
    error_message: Optional[str] = None
    processing_id: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None  # 新增：结构化数据字段

    def __post_init__(self):
        """后处理：确保数据一致性"""
        if self.status == ProcessingStatus.COMPLETED and not self.processed_text.strip():
            self.status = ProcessingStatus.FAILED
            self.error_message = "Empty processed text"
        elif self.status == ProcessingStatus.FAILED and not self.error_message:
            self.error_message = "Processing failed"

        # 生成处理ID
        if not self.processing_id:
            self.processing_id = f"proc_{self.original.content_hash[:8]}_{int(time.time() * 1000)}"

    @property
    def is_successful(self) -> bool:
        """判断处理是否成功"""
        return self.status in [ProcessingStatus.COMPLETED, ProcessingStatus.CACHED]

    @property
    def processing_duration(self) -> Optional[float]:
        """获取处理时长"""
        return self.metrics.processing_time if self.metrics else None

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "processing_id": self.processing_id,
            "original": self.original.to_dict(),
            "processed_text": self.processed_text,
            "status": self.status.value,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "error_message": self.error_message,
            "is_successful": self.is_successful,
            "processing_duration": self.processing_duration
        }

    @classmethod
    def create_error_result(cls, original: ImageContent, error_message: str, processing_time: float = 0.0) -> "ProcessedContent":
        """创建错误结果"""
        metrics = ProcessingMetrics(
            processing_time=processing_time,
            confidence=0.0,
            retry_count=0
        )

        return cls(
            original=original,
            processed_text="",
            status=ProcessingStatus.FAILED,
            metrics=metrics,
            error_message=error_message
        )

    @classmethod
    def create_cached_result(cls, original: ImageContent, cached_text: str, confidence: float = 1.0) -> "ProcessedContent":
        """创建缓存结果"""
        metrics = ProcessingMetrics(
            processing_time=0.001,  # 非常快的缓存命中时间
            confidence=confidence,
            cache_hit=True,
            retry_count=0
        )

        result = cls(
            original=original,
            processed_text=cached_text,
            status=ProcessingStatus.CACHED,
            metrics=metrics
        )
        return result

    def __repr__(self) -> str:
        """字符串表示，避免输出大量内容"""
        text_preview = self.processed_text[:50] + "..." if len(self.processed_text) > 50 else self.processed_text
        return (f"ProcessedContent(id='{self.processing_id}', "
                f"status='{self.status.value}', "
                f"text='{text_preview}', "
                f"original={repr(self.original)})")