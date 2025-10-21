"""
Base AI Provider for docpipe-ai.

This module defines the abstract base class for all AI providers,
ensuring consistent interface across different implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
import logging
from dataclasses import dataclass

from ..data.content import ImageContent, ProcessedContent, ProcessingStatus, ContentFormat

logger = logging.getLogger(__name__)


@dataclass
class AIResponse:
    """AI响应数据结构"""
    text: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    response_time: Optional[float] = None
    confidence: Optional[float] = None


@dataclass
class ProviderCapabilities:
    """提供商能力描述"""
    supports_images: bool = False
    supports_streaming: bool = False
    max_tokens: Optional[int] = None
    max_image_size: Optional[int] = None  # 字节
    supported_formats: List[str] = None
    supports_system_prompt: bool = True
    supports_temperature: bool = True
    supports_max_tokens: bool = True


class BaseAIProvider(ABC):
    """
    AI提供商基类

    定义所有AI提供商必须实现的通用接口，确保一致性。
    """

    def __init__(self,
                 model_name: str,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 **kwargs):
        """
        初始化AI提供商

        Args:
            model_name: 模型名称
            api_key: API密钥
            api_base: API基础URL
            **kwargs: 其他提供商特定参数
        """
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        self.extra_params = kwargs

        # 初始化客户端
        self.client = None
        self._initialize_client()

        # 获取能力信息
        self.capabilities = self._get_capabilities()

        logger.info(f"Initialized {self.__class__.__name__} with model: {model_name}")

    @abstractmethod
    def _initialize_client(self) -> None:
        """初始化AI客户端 - 子类必须实现"""
        pass

    @abstractmethod
    def _get_capabilities(self) -> ProviderCapabilities:
        """获取提供商能力信息 - 子类必须实现"""
        pass

    @abstractmethod
    def generate_text(self: "BaseAIProvider",
                     prompt: str,
                     system_prompt: Optional[str] = None,
                     max_tokens: Optional[int] = None,
                     temperature: Optional[float] = None,
                     **kwargs) -> AIResponse:
        """
        生成文本响应

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            AI响应
        """
        pass

    @abstractmethod
    def generate_text_with_image(self: "BaseAIProvider",
                               prompt: str,
                               image_data: bytes,
                               image_format: str = "image/jpeg",
                               system_prompt: Optional[str] = None,
                               max_tokens: Optional[int] = None,
                               temperature: Optional[float] = None,
                               **kwargs) -> AIResponse:
        """
        生成包含图片的文本响应

        Args:
            prompt: 用户提示词
            image_data: 图片二进制数据
            image_format: 图片格式
            system_prompt: 系统提示词
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            AI响应
        """
        pass

    def process_image_content(self: "BaseAIProvider",
                            content: ImageContent,
                            system_prompt: Optional[str] = None,
                            max_tokens: Optional[int] = None,
                            temperature: Optional[float] = None,
                            **kwargs) -> ProcessedContent:
        """
        处理图片内容

        这是一个便利方法，将ImageContent转换为处理所需的格式，
        并调用适当的生成方法。

        Args:
            content: 图片内容
            system_prompt: 系统提示词
            max_tokens: 最大token数
            temperature: 温度参数
            **kwargs: 其他参数

        Returns:
            处理后的内容
        """
        import time
        start_time = time.time()

        try:
            # 创建提示词
            prompt = self._create_image_prompt(content)

            # 处理图片
            response = self.generate_text_with_image(
                prompt=prompt,
                image_data=content.binary_data,
                image_format=self._get_image_format(content),
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            # 创建处理结果
            processing_time = time.time() - start_time

            return ProcessedContent(
                original=content,
                processed_text=response.text,
                status=ProcessingStatus.COMPLETED,
                error_message=None,
                processing_id=f"{self.model_name}_{content.content_hash[:8]}_{int(time.time() * 1000)}"
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error processing image content: {e}")

            return ProcessedContent.create_error_result(
                content=content,
                error_message=str(e),
                processing_time=processing_time
            )

    def _create_image_prompt(self: "BaseAIProvider", content: ImageContent) -> str:
        """
        为图片内容创建提示词

        Args:
            content: 图片内容

        Returns:
            提示词文本
        """
        prompt = f"请分析这张图片并提供清晰、简洁的中文描述。\n\n"
        prompt += f"图片信息：\n"
        prompt += f"- 页码：第 {content.page} 页\n"
        prompt += f"- 边界框：{content.bbox.to_list()}\n"
        prompt += f"- 大小：{len(content.binary_data)} 字节\n"

        if content.metadata:
            prompt += f"- 格式：{content.metadata.format.value}\n"
            if content.metadata.width_pixels and content.metadata.height_pixels:
                prompt += f"- 分辨率：{content.metadata.width_pixels}x{content.metadata.height_pixels}\n"

        prompt += f"\n请用中文描述这张图片展示的内容，保持客观中性的表达方式。"

        return prompt

    def _get_image_format(self: "BaseAIProvider", content: ImageContent) -> str:
        """
        获取图片格式字符串

        Args:
            content: 图片内容

        Returns:
            图片格式字符串
        """
        if content.metadata and content.metadata.format != ContentFormat.UNKNOWN:
            format_mapping = {
                ContentFormat.PNG: "image/png",
                ContentFormat.JPEG: "image/jpeg",
                ContentFormat.GIF: "image/gif",
                ContentFormat.BMP: "image/bmp",
                ContentFormat.WEBP: "image/webp",
                ContentFormat.TIFF: "image/tiff",
            }
            return format_mapping.get(content.metadata.format, "image/jpeg")

        return "image/jpeg"

    def validate_config(self: "BaseAIProvider") -> List[str]:
        """
        验证配置

        Returns:
            错误信息列表，空列表表示验证通过
        """
        errors = []

        # 基本验证
        if not self.model_name:
            errors.append("Model name is required")

        if self.capabilities.supports_images:
            # 如果支持图片，检查图片相关能力
            if self.capabilities.max_image_size and self.capabilities.max_image_size <= 0:
                errors.append("Invalid max_image_size")

        # 检查必需参数
        if self._requires_api_key() and not self.api_key:
            errors.append(f"API key is required for {self.__class__.__name__}")

        return errors

    def _requires_api_key(self: "BaseAIProvider") -> bool:
        """
        是否需要API密钥

        子类可以重写此方法

        Returns:
            是否需要API密钥
        """
        return True

    def get_model_info(self: "BaseAIProvider") -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        return {
            "provider": self.__class__.__name__,
            "model_name": self.model_name,
            "capabilities": {
                "supports_images": self.capabilities.supports_images,
                "supports_streaming": self.capabilities.supports_streaming,
                "max_tokens": self.capabilities.max_tokens,
                "max_image_size": self.capabilities.max_image_size,
                "supported_formats": self.capabilities.supported_formats,
                "supports_system_prompt": self.capabilities.supports_system_prompt,
                "supports_temperature": self.capabilities.supports_temperature,
                "supports_max_tokens": self.capabilities.supports_max_tokens,
            },
            "api_base": self.api_base,
        }

    def test_connection(self: "BaseAIProvider") -> bool:
        """
        测试连接

        尝试发送一个简单的请求来验证连接是否正常

        Returns:
            连接是否正常
        """
        try:
            # 发送一个简单的文本请求
            response = self.generate_text(
                prompt="Hello, please respond with 'OK' to confirm the connection is working.",
                max_tokens=10
            )
            return "OK" in response.text.upper()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def close(self: "BaseAIProvider") -> None:
        """
        关闭连接和清理资源

        子类可以重写此方法来实现特定的清理逻辑
        """
        if hasattr(self.client, 'close'):
            self.client.close()
        self.client = None
        logger.info(f"Closed {self.__class__.__name__} connection")

    def __enter__(self: "BaseAIProvider"):
        """上下文管理器入口"""
        return self

    def __exit__(self: "BaseAIProvider", exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

    def __repr__(self: "BaseAIProvider") -> str:
        """字符串表示"""
        return f"{self.__class__.__name__}(model='{self.model_name}')"