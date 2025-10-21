"""
Simple Interface for docpipe-ai.

This module provides easy-to-use functions that hide the complexity
of the Protocol-oriented architecture while maintaining its power.
"""

import os
from typing import List, Dict, Any, Optional, Union, Iterator
from pathlib import Path
import logging

from ..data.content import ImageContent, ProcessedContent, BoundingBox, ContentFormat, ImageMetadata
from ..data.config import ProcessingConfig, AIProviderConfig
from ..processors.adaptive_image_processor import AdaptiveImageProcessor
from ..processors.batch_processor import BatchProcessor
from ..providers.factory import ProviderFactory

logger = logging.getLogger(__name__)


class SimpleProcessor:
    """
    简化的图片处理器

    这个类提供了一个简单易用的接口，隐藏了Protocol-oriented架构的复杂性，
    同时保留了其强大的功能。适合快速集成和简单使用场景。
    """

    def __init__(self,
                 provider: str = "openai",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 cache_enabled: bool = True,
                 max_concurrency: int = 5,
                 **kwargs):
        """
        初始化简单处理器

        Args:
            provider: AI提供商名称 ("openai", "anthropic")
            model: 模型名称，如果为None则使用默认模型
            api_key: API密钥，如果为None则从环境变量获取
            api_base: API基础URL
            cache_enabled: 是否启用缓存
            max_concurrency: 最大并发数
            **kwargs: 其他参数
        """
        # 创建AI提供商
        self.provider = ProviderFactory.create_provider(
            provider_name=provider,
            model_name=model,
            api_key=api_key,
            api_base=api_base,
            **kwargs
        )

        # 创建处理配置
        config = ProcessingConfig(
            ai_provider=provider,
            model_name=model or self.provider.model_name,
            enable_caching=cache_enabled,
            enable_metrics=True,
            max_concurrency=max_concurrency
        )

        # 创建AI提供商配置
        ai_config = AIProviderConfig(
            provider_name=provider,
            model_name=model or self.provider.model_name,
            api_key=api_key,
            api_base=api_base
        )

        # 创建自适应处理器
        self.processor = AdaptiveImageProcessor(
            ai_client=self.provider.client,
            config=config,
            ai_config=ai_config
        )

        # 创建批处理器
        self.batch_processor = BatchProcessor(
            processor=self.processor,
            config=config,
            max_concurrency=max_concurrency
        )

        logger.info(f"SimpleProcessor initialized with {provider}/{self.provider.model_name}")

    def process_image(self,
                     image_data: bytes,
                     page: int = 1,
                     bbox: Optional[List[float]] = None,
                     **metadata) -> ProcessedContent:
        """
        处理单个图片

        Args:
            image_data: 图片二进制数据
            page: 页码
            bbox: 边界框 [x, y, width, height]
            **metadata: 其他元数据

        Returns:
            处理结果
        """
        # 创建ImageContent对象
        content = self._create_image_content(image_data, page, bbox, **metadata)

        # 处理图片
        return self.processor.process_batch([content])[0]

    def process_images(self,
                      image_list: List[Dict[str, Any]]) -> List[ProcessedContent]:
        """
        批量处理图片

        Args:
            image_list: 图片数据列表，每个元素为包含 image_data 的字典

        Returns:
            处理结果列表
        """
        # 转换为ImageContent对象列表
        contents = []
        for i, img_data in enumerate(image_list):
            if isinstance(img_data, dict):
                content = self._create_image_content(
                    image_data=img_data.get("image_data", b""),
                    page=img_data.get("page", i + 1),
                    bbox=img_data.get("bbox"),
                    **img_data.get("metadata", {})
                )
            else:
                # 如果直接传入字节数据
                content = self._create_image_content(
                    image_data=img_data,
                    page=i + 1
                )
            contents.append(content)

        # 批量处理
        return self.processor.process_batch(contents)

    def process_image_stream(self,
                           image_stream: Iterator[Dict[str, Any]]) -> Iterator[ProcessedContent]:
        """
        流式处理图片

        Args:
            image_stream: 图片数据流

        Yields:
            处理结果
        """
        def content_generator():
            for i, img_data in enumerate(image_stream):
                if isinstance(img_data, dict):
                    yield self._create_image_content(
                        image_data=img_data.get("image_data", b""),
                        page=img_data.get("page", i + 1),
                        bbox=img_data.get("bbox"),
                        **img_data.get("metadata", {})
                    )
                else:
                    yield self._create_image_content(
                        image_data=img_data,
                        page=i + 1
                    )

        return self.batch_processor.process_stream(content_generator())

    def process_file(self,
                    file_path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
        """
        处理文件（与原有接口兼容）

        Args:
            file_path: 文件路径

        Yields:
            处理后的文档块
        """
        try:
            import docpipe as dp
        except ImportError:
            raise ImportError("docpipe package is required for file processing. Install with: pip install docpipe-mini")

        # 使用docpipe解析文件
        chunks = dp.serialize(str(file_path))

        # 转换为图片内容流
        def extract_images():
            for chunk in chunks:
                if hasattr(chunk, 'binary_data') and chunk.binary_data and chunk.type != 'text':
                    # 创建ImageContent
                    content = self._create_image_content(
                        image_data=chunk.binary_data,
                        page=getattr(chunk, 'page', 1),
                        bbox=getattr(chunk, 'bbox', [0, 0, 100, 100]),
                        format=chunk.type
                    )
                    yield content

        # 处理图片流
        processed_results = list(self.batch_processor.process_stream(extract_images()))

        # 将结果转换回原始格式
        result_index = 0
        for chunk in chunks:
            if hasattr(chunk, 'binary_data') and chunk.binary_data and chunk.type != 'text':
                # 使用处理结果
                if result_index < len(processed_results):
                    processed_text = processed_results[result_index].processed_text
                    result_index += 1
                else:
                    processed_text = ""

                block = {
                    "doc_id": getattr(chunk, 'doc_id', f"chunk_{result_index}"),
                    "page": getattr(chunk, 'page', 1),
                    "bbox": getattr(chunk, 'bbox', [0, 0, 100, 100]),
                    "type": chunk.type,
                    "text": processed_text
                }
                yield block
            else:
                # 文本块直接透传
                block = {
                    "doc_id": getattr(chunk, 'doc_id', "text_chunk"),
                    "page": getattr(chunk, 'page', 1),
                    "bbox": getattr(chunk, 'bbox', [0, 0, 100, 100]),
                    "type": "text",
                    "text": getattr(chunk, 'text', "")
                }
                yield block

    def _create_image_content(self,
                            image_data: bytes,
                            page: int = 1,
                            bbox: Optional[List[float]] = None,
                            format: str = "image",
                            **metadata) -> ImageContent:
        """
        创建ImageContent对象

        Args:
            image_data: 图片二进制数据
            page: 页码
            bbox: 边界框
            format: 格式
            **metadata: 其他元数据

        Returns:
            ImageContent对象
        """
        # 边界框
        if bbox:
            bbox_obj = BoundingBox.from_list(bbox)
        else:
            bbox_obj = BoundingBox(0, 0, 100, 100)

        # 图片元数据
        img_metadata = ImageMetadata(
            format=ContentFormat(format.lower()) if format.lower() in [f.value for f in ContentFormat] else ContentFormat.UNKNOWN,
            size_bytes=len(image_data),
            **metadata
        )

        return ImageContent(
            binary_data=image_data,
            page=page,
            bbox=bbox_obj,
            metadata=img_metadata
        )

    def get_stats(self) -> Dict[str, Any]:
        """
        获取处理统计信息

        Returns:
            统计信息字典
        """
        return {
            "processor_stats": self.processor.get_processor_stats(),
            "batch_stats": self.batch_processor.get_batch_stats(),
            "provider_info": self.provider.get_model_info(),
        }

    def reset_stats(self) -> None:
        """重置统计信息"""
        self.processor.reset_all_stats()
        self.batch_processor.reset_batch_stats()

    def close(self) -> None:
        """关闭处理器并清理资源"""
        if self.provider:
            self.provider.close()
        logger.info("SimpleProcessor closed")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 便利函数

def process_image(image_data: bytes,
                 provider: str = "openai",
                 model: Optional[str] = None,
                 api_key: Optional[str] = None,
                 **kwargs) -> str:
    """
    处理单个图片的便利函数

    Args:
        image_data: 图片二进制数据
        provider: AI提供商
        model: 模型名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        生成的文本描述
    """
    with SimpleProcessor(provider=provider, model=model, api_key=api_key, **kwargs) as processor:
        result = processor.process_image(image_data)
        return result.processed_text


def process_images(image_list: List[Dict[str, Any]],
                  provider: str = "openai",
                  model: Optional[str] = None,
                  api_key: Optional[str] = None,
                  **kwargs) -> List[str]:
    """
    批量处理图片的便利函数

    Args:
        image_list: 图片数据列表
        provider: AI提供商
        model: 模型名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        生成的文本描述列表
    """
    with SimpleProcessor(provider=provider, model=model, api_key=api_key, **kwargs) as processor:
        results = processor.process_images(image_list)
        return [result.processed_text for result in results]


def process_file(file_path: Union[str, Path],
                provider: str = "openai",
                model: Optional[str] = None,
                api_key: Optional[str] = None,
                **kwargs) -> Iterator[Dict[str, Any]]:
    """
    处理文件的便利函数

    Args:
        file_path: 文件路径
        provider: AI提供商
        model: 模型名称
        api_key: API密钥
        **kwargs: 其他参数

    Yields:
        处理后的文档块
    """
    with SimpleProcessor(provider=provider, model=model, api_key=api_key, **kwargs) as processor:
        yield from processor.process_file(file_path)


# 快速配置函数

def create_openai_processor(model: str = "gpt-4o-mini",
                          api_key: Optional[str] = None,
                          **kwargs) -> SimpleProcessor:
    """
    创建OpenAI处理器的便利函数

    Args:
        model: 模型名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        配置好的处理器
    """
    return SimpleProcessor(provider="openai", model=model, api_key=api_key, **kwargs)


def create_anthropic_processor(model: str = "claude-3-sonnet-20240229",
                             api_key: Optional[str] = None,
                             **kwargs) -> SimpleProcessor:
    """
    创建Anthropic处理器的便利函数

    Args:
        model: 模型名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        配置好的处理器
    """
    return SimpleProcessor(provider="anthropic", model=model, api_key=api_key, **kwargs)


def create_processor_from_env() -> SimpleProcessor:
    """
    从环境变量创建处理器

    环境变量：
    - DOPIPE_AI_PROVIDER: AI提供商
    - DOPIPE_AI_MODEL: 模型名称
    - OPENAI_API_KEY / ANTHROPIC_API_KEY: API密钥
    - OPENAI_API_BASE / ANTHROPIC_API_BASE: API基础URL

    Returns:
        配置好的处理器
    """
    provider = os.getenv("DOPIPE_AI_PROVIDER", "openai")
    model = os.getenv("DOPIPE_AI_MODEL")

    return SimpleProcessor(provider=provider, model=model)