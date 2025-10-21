"""
Validation mixins for docpipe-ai.

This module provides Mixin implementations for content validation.
These mixins can be combined with any class that implements the ContentValidator protocol
to add validation capabilities.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
import logging
import imghdr
import struct
import io
from abc import abstractmethod

from ..core.protocols import ContentValidator
from ..data.content import ImageContent, ContentFormat, ImageMetadata

logger = logging.getLogger(__name__)

class ContentValidationMixin:
    """
    内容验证Mixin - 提供通用的内容验证功能

    这个Mixin实现了基础的格式、大小和质量验证。
    """

    def __init__(self: "ContentValidator",
                 min_size_bytes: int = 100,
                 max_size_bytes: int = 50 * 1024 * 1024,  # 50MB
                 allowed_formats: Optional[List[ContentFormat]] = None):
        """
        初始化内容验证

        Args:
            min_size_bytes: 最小文件大小（字节）
            max_size_bytes: 最大文件大小（字节）
            allowed_formats: 允许的格式列表，None表示允许所有格式
        """
        self.min_size_bytes = min_size_bytes
        self.max_size_bytes = max_size_bytes
        self.allowed_formats = allowed_formats or [
            ContentFormat.PNG, ContentFormat.JPEG, ContentFormat.GIF,
            ContentFormat.BMP, ContentFormat.WEBP, ContentFormat.TIFF
        ]

    def validate_content(self: "ContentValidator", content: ImageContent) -> Tuple[bool, List[str]]:
        """
        验证图片内容

        Args:
            content: 要验证的图片内容

        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []

        # 1. 基础验证
        if not content.binary_data:
            errors.append("图片数据为空")
            return False, errors

        # 2. 大小验证
        size_errors = self._validate_size(content)
        errors.extend(size_errors)

        # 3. 格式验证
        format_errors = self._validate_format(content)
        errors.extend(format_errors)

        # 4. 完整性验证
        integrity_errors = self._validate_integrity(content)
        errors.extend(integrity_errors)

        # 5. 元数据验证
        metadata_errors = self._validate_metadata(content)
        errors.extend(metadata_errors)

        is_valid = len(errors) == 0
        if is_valid:
            logger.debug(f"Content validation passed for {content.content_hash[:8]}")
        else:
            logger.warning(f"Content validation failed: {errors}")

        return is_valid, errors

    def _validate_size(self: "ContentValidator", content: ImageContent) -> List[str]:
        """验证文件大小"""
        errors = []
        size = len(content.binary_data)

        if size < self.min_size_bytes:
            errors.append(f"文件过小: {size} 字节 < {self.min_size_bytes} 字节")

        if size > self.max_size_bytes:
            errors.append(f"文件过大: {size} 字节 > {self.max_size_bytes} 字节")

        return errors

    def _validate_format(self: "ContentValidator", content: ImageContent) -> List[str]:
        """验证文件格式"""
        errors = []

        # 尝试检测实际格式
        detected_format = self._detect_format(content.binary_data)
        if detected_format == ContentFormat.UNKNOWN:
            errors.append("无法识别的图片格式")
            return errors

        # 检查是否在允许列表中
        if detected_format not in self.allowed_formats:
            allowed_names = [fmt.value for fmt in self.allowed_formats]
            errors.append(f"不支持的格式: {detected_format.value}, 允许的格式: {allowed_names}")

        # 如果有元数据，检查元数据格式是否一致
        if content.metadata and content.metadata.format != ContentFormat.UNKNOWN:
            if content.metadata.format != detected_format:
                errors.append(
                    f"元数据格式不一致: 元数据={content.metadata.format.value}, "
                    f"实际={detected_format.value}"
                )

        return errors

    def _validate_integrity(self: "ContentValidator", content: ImageContent) -> List[str]:
        """验证文件完整性"""
        errors = []

        try:
            # 使用PIL尝试打开图片（如果可用）
            try:
                from PIL import Image
                img = Image.open(io.BytesIO(content.binary_data))
                img.verify()  # 验证图片但不加载像素数据
            except ImportError:
                logger.debug("PIL not available, skipping advanced integrity check")
            except Exception as e:
                errors.append(f"图片完整性验证失败: {e}")

        except Exception as e:
            errors.append(f"完整性检查异常: {e}")

        return errors

    def _validate_metadata(self: "ContentValidator", content: ImageContent) -> List[str]:
        """验证元数据"""
        errors = []

        if not content.metadata:
            return errors  # 元数据是可选的

        metadata = content.metadata

        # 验证尺寸信息
        if metadata.width_pixels is not None:
            if metadata.width_pixels <= 0:
                errors.append("图片宽度必须大于0")
            if metadata.width_pixels > 50000:  # 合理的上限
                errors.append(f"图片宽度过大: {metadata.width_pixels}px")

        if metadata.height_pixels is not None:
            if metadata.height_pixels <= 0:
                errors.append("图片高度必须大于0")
            if metadata.height_pixels > 50000:  # 合理的上限
                errors.append(f"图片高度过大: {metadata.height_pixels}px")

        # 验证DPI
        if metadata.dpi is not None:
            if metadata.dpi <= 0:
                errors.append("DPI必须大于0")
            if metadata.dpi > 10000:  # 合理的上限
                errors.append(f"DPI过大: {metadata.dpi}")

        # 验证大小一致性
        if metadata.size_bytes > 0 and metadata.size_bytes != len(content.binary_data):
            errors.append(
                f"元数据大小不一致: 元数据={metadata.size_bytes}, "
                f"实际={len(content.binary_data)}"
            )

        return errors

    def _detect_format(self: "ContentValidator", data: bytes) -> ContentFormat:
        """检测图片格式"""
        if not data:
            return ContentFormat.UNKNOWN

        # 使用imghdr检测格式
        try:
            format_name = imghdr.what(None, h=data)
        except (TypeError, AttributeError):
            # 如果imghdr无法处理bytes数据，返回未知
            format_name = None

        # 将imghdr格式映射到ContentFormat
        format_mapping = {
            'png': ContentFormat.PNG,
            'jpeg': ContentFormat.JPEG,
            'jpg': ContentFormat.JPEG,
            'gif': ContentFormat.GIF,
            'bmp': ContentFormat.BMP,
            'tiff': ContentFormat.TIFF,
            'webp': ContentFormat.WEBP,
        }

        detected_format = format_mapping.get(format_name, ContentFormat.UNKNOWN)

        # 如果imghdr无法识别，尝试基于文件头检测
        if detected_format == ContentFormat.UNKNOWN:
            detected_format = self._detect_by_signature(data)

        return detected_format

    def _detect_by_signature(self: "ContentValidator", data: bytes) -> ContentFormat:
        """基于文件头检测格式"""
        if len(data) < 8:
            return ContentFormat.UNKNOWN

        # 常见图片格式的文件头
        signatures = {
            b'\x89PNG\r\n\x1a\n': ContentFormat.PNG,
            b'\xff\xd8\xff': ContentFormat.JPEG,
            b'GIF87a': ContentFormat.GIF,
            b'GIF89a': ContentFormat.GIF,
            b'BM': ContentFormat.BMP,
            b'II*\x00': ContentFormat.TIFF,
            b'MM\x00*': ContentFormat.TIFF,
            b'RIFF': ContentFormat.WEBP,  # 需要进一步检查
        }

        for signature, format_type in signatures.items():
            if data.startswith(signature):
                # 对于WEBP，需要进一步验证
                if format_type == ContentFormat.WEBP and len(data) >= 12:
                    if data[8:12] == b'WEBP':
                        return ContentFormat.WEBP
                else:
                    return format_type

        return ContentFormat.UNKNOWN

    def get_validation_stats(self: "ContentValidator") -> Dict[str, Any]:
        """
        获取验证统计信息

        Returns:
            验证统计数据
        """
        return {
            "min_size_bytes": self.min_size_bytes,
            "max_size_bytes": self.max_size_bytes,
            "allowed_formats": [fmt.value for fmt in self.allowed_formats],
            "validation_enabled": True
        }


class ImageValidationMixin:
    """
    图片验证Mixin - 提供专门的图片验证功能

    这个Mixin提供了更深入的图片质量、分辨率和内容验证。
    """

    def __init__(self: "ContentValidator",
                 min_width: int = 10,
                 min_height: int = 10,
                 max_width: int = 10000,
                 max_height: int = 10000,
                 min_aspect_ratio: float = 0.1,
                 max_aspect_ratio: float = 10.0,
                 check_corruption: bool = True):
        """
        初始化图片验证

        Args:
            min_width: 最小宽度
            min_height: 最小高度
            max_width: 最大宽度
            max_height: 最大高度
            min_aspect_ratio: 最小宽高比
            max_aspect_ratio: 最大宽高比
            check_corruption: 是否检查损坏文件
        """
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio
        self.check_corruption = check_corruption

    def validate_image_properties(self: "ContentValidator", content: ImageContent) -> Tuple[bool, List[str]]:
        """
        验证图片属性

        Args:
            content: 要验证的图片内容

        Returns:
            (是否有效, 错误消息列表)
        """
        errors = []

        try:
            # 尝试加载图片获取实际属性
            actual_width, actual_height = self._get_image_dimensions(content)

            if actual_width and actual_height:
                # 验证尺寸
                size_errors = self._validate_dimensions(actual_width, actual_height)
                errors.extend(size_errors)

                # 验证宽高比
                ratio_errors = self._validate_aspect_ratio(actual_width, actual_height)
                errors.extend(ratio_errors)

                # 验证与元数据的一致性
                consistency_errors = self._validate_metadata_consistency(
                    content, actual_width, actual_height
                )
                errors.extend(consistency_errors)

            else:
                errors.append("无法获取图片尺寸信息")

        except Exception as e:
            errors.append(f"图片属性验证异常: {e}")

        is_valid = len(errors) == 0
        if is_valid:
            logger.debug(f"Image validation passed for {content.content_hash[:8]}")
        else:
            logger.warning(f"Image validation failed: {errors}")

        return is_valid, errors

    def _get_image_dimensions(self: "ContentValidator", content: ImageContent) -> Tuple[Optional[int], Optional[int]]:
        """获取图片实际尺寸"""
        try:
            # 首先尝试使用PIL
            try:
                from PIL import Image
                with Image.open(io.BytesIO(content.binary_data)) as img:
                    return img.size[0], img.size[1]
            except ImportError:
                logger.debug("PIL not available for dimension detection")

            # 备用方法：基于格式特定的头部信息
            return self._get_dimensions_from_header(content)
        except Exception as e:
            logger.error(f"Error getting image dimensions: {e}")
            return None, None

    def _get_dimensions_from_header(self: "ContentValidator", content: ImageContent) -> Tuple[Optional[int], Optional[int]]:
        """从文件头获取尺寸信息"""
        data = content.binary_data

        if content.metadata and content.metadata.format in [ContentFormat.PNG, ContentFormat.JPEG, ContentFormat.BMP]:
            format_type = content.metadata.format
        else:
            format_type = self._detect_format(data)

        try:
            if format_type == ContentFormat.PNG and len(data) >= 24:
                # PNG: 宽度和高度在第13-16和17-20字节
                width = struct.unpack('>I', data[16:20])[0]
                height = struct.unpack('>I', data[20:24])[0]
                return width, height

            elif format_type == ContentFormat.JPEG and len(data) >= 10:
                # JPEG: 需要查找SOF标记
                return self._extract_jpeg_dimensions(data)

            elif format_type == ContentFormat.BMP and len(data) >= 18:
                # BMP: 宽度和高度在第18-21和22-25字节
                width = struct.unpack('<I', data[18:22])[0]
                height = struct.unpack('<I', data[22:26])[0]
                return width, height

        except Exception as e:
            logger.debug(f"Error extracting dimensions from header: {e}")

        return None, None

    def _extract_jpeg_dimensions(self: "ContentValidator", data: bytes) -> Tuple[Optional[int], Optional[int]]:
        """从JPEG文件提取尺寸"""
        i = 0
        while i < len(data) - 1:
            if data[i] == 0xFF:
                marker = data[i + 1]
                if marker == 0xC0 or marker == 0xC2:  # SOF markers
                    if i + 9 < len(data):
                        height = struct.unpack('>H', data[i + 5:i + 7])[0]
                        width = struct.unpack('>H', data[i + 7:i + 9])[0]
                        return width, height
                i += 1
            else:
                i += 1
        return None, None

    def _validate_dimensions(self: "ContentValidator", width: int, height: int) -> List[str]:
        """验证图片尺寸"""
        errors = []

        if width < self.min_width:
            errors.append(f"图片宽度过小: {width}px < {self.min_width}px")

        if height < self.min_height:
            errors.append(f"图片高度过小: {height}px < {self.min_height}px")

        if width > self.max_width:
            errors.append(f"图片宽度过大: {width}px > {self.max_width}px")

        if height > self.max_height:
            errors.append(f"图片高度过大: {height}px > {self.max_height}px")

        return errors

    def _validate_aspect_ratio(self: "ContentValidator", width: int, height: int) -> List[str]:
        """验证宽高比"""
        errors = []

        if height == 0:
            errors.append("图片高度为0")
            return errors

        aspect_ratio = width / height

        if aspect_ratio < self.min_aspect_ratio:
            errors.append(f"宽高比过小: {aspect_ratio:.2f} < {self.min_aspect_ratio:.2f}")

        if aspect_ratio > self.max_aspect_ratio:
            errors.append(f"宽高比过大: {aspect_ratio:.2f} > {self.max_aspect_ratio:.2f}")

        return errors

    def _validate_metadata_consistency(self: "ContentValidator", content: ImageContent,
                                     actual_width: int, actual_height: int) -> List[str]:
        """验证元数据一致性"""
        errors = []

        if not content.metadata:
            return errors

        metadata = content.metadata

        # 检查宽度一致性
        if metadata.width_pixels is not None and metadata.width_pixels != actual_width:
            errors.append(
                f"宽度不一致: 元数据={metadata.width_pixels}px, "
                f"实际={actual_width}px"
            )

        # 检查高度一致性
        if metadata.height_pixels is not None and metadata.height_pixels != actual_height:
            errors.append(
                f"高度不一致: 元数据={metadata.height_pixels}px, "
                f"实际={actual_height}px"
            )

        # 检查像素总数合理性
        total_pixels = actual_width * actual_height
        if metadata.megapixels is not None:
            expected_pixels = int(metadata.megapixels * 1_000_000)
            if abs(total_pixels - expected_pixels) > expected_pixels * 0.1:  # 10%误差
                errors.append(
                    f"像素数不一致: 元数据={expected_pixels}, "
                    f"实际={total_pixels}"
                )

        return errors

    def check_image_corruption(self: "ContentValidator", content: ImageContent) -> bool:
        """
        检查图片是否损坏

        Args:
            content: 图片内容

        Returns:
            True表示图片可能损坏，False表示看起来正常
        """
        if not self.check_corruption:
            return False

        try:
            # 使用PIL进行深度验证
            try:
                from PIL import Image
                with Image.open(io.BytesIO(content.binary_data)) as img:
                    # 尝试加载第一行像素
                    img.load()
                    return False
            except Exception:
                return True

        except Exception as e:
            logger.debug(f"Corruption check error: {e}")
            return True  # 保守策略：如果无法验证，认为可能损坏

    def _detect_format(self: "ContentValidator", data: bytes) -> ContentFormat:
        """检测图片格式（复用ContentValidationMixin的逻辑）"""
        if not data:
            return ContentFormat.UNKNOWN

        format_name = imghdr.what(None, h=data)

        format_mapping = {
            'png': ContentFormat.PNG,
            'jpeg': ContentFormat.JPEG,
            'jpg': ContentFormat.JPEG,
            'gif': ContentFormat.GIF,
            'bmp': ContentFormat.BMP,
            'tiff': ContentFormat.TIFF,
            'webp': ContentFormat.WEBP,
        }

        return format_mapping.get(format_name, ContentFormat.UNKNOWN)

    def get_validation_config(self: "ContentValidator") -> Dict[str, Any]:
        """
        获取验证配置

        Returns:
            验证配置信息
        """
        return {
            "min_width": self.min_width,
            "min_height": self.min_height,
            "max_width": self.max_width,
            "max_height": self.max_height,
            "min_aspect_ratio": self.min_aspect_ratio,
            "max_aspect_ratio": self.max_aspect_ratio,
            "check_corruption": self.check_corruption
        }