"""
Adaptive Image Processor for docpipe-ai.

This module provides AdaptiveImageProcessor that combines multiple protocols
and mixins to create a comprehensive image processing solution with
adaptive batch sizing, caching, validation, and error handling.
"""

from typing import List, Dict, Any, Optional, Union, Iterator
import logging
import time
from pathlib import Path

from ..core.protocols import (
    Batchable, AIProcessable, Cacheable, ContentValidator,
    ErrorHandler, CompleteProcessor
)
from ..data.content import ImageContent, ProcessedContent
from ..data.config import ProcessingConfig, AIProviderConfig
from ..mixins.batch_processing import DynamicBatchingMixin
from ..mixins.ai_processing import OpenAIProcessingMixin, GenericAIProcessingMixin
from ..mixins.structured_output import StructuredOutputMixin
from ..mixins.caching import MemoryCacheMixin
from ..mixins.validation import ContentValidationMixin, ImageValidationMixin
from ..mixins.error_handling import RetryHandlerMixin, FallbackHandlerMixin, MetricsCollectionMixin
from .base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class AdaptiveImageProcessor(
    BaseProcessor,
    # 批量处理能力
    DynamicBatchingMixin[ImageContent],
    # AI处理能力
    OpenAIProcessingMixin,
    GenericAIProcessingMixin,
    StructuredOutputMixin,
    # 缓存能力
    MemoryCacheMixin,
    # 验证能力
    ContentValidationMixin,
    ImageValidationMixin,
    # 错误处理能力
    RetryHandlerMixin,
    FallbackHandlerMixin,
    MetricsCollectionMixin,
):
    """
    自适应图片处理器

    这个类结合了多种协议和Mixin，提供完整的图片处理能力：
    - 动态批量处理：根据剩余数量自动调整批次大小
    - AI处理：支持OpenAI等多种AI提供商
    - 智能缓存：内存缓存提升性能
    - 内容验证：确保图片质量和格式正确
    - 错误处理：重试机制和降级策略
    - 指标收集：性能监控和优化

    该处理器遵循Protocol-oriented + Mixin设计模式：
    - 协议定义能力接口
    - Mixin提供具体实现
    - 零成本组合多种功能
    """

    def __init__(self,
                 ai_client,
                 config: Optional[ProcessingConfig] = None,
                 ai_config: Optional[AIProviderConfig] = None):
        """
        初始化自适应图片处理器

        Args:
            ai_client: AI客户端实例
            config: 处理配置
            ai_config: AI提供商配置
        """
        # 初始化基类
        BaseProcessor.__init__(self)

        # 处理配置
        self.config = config or ProcessingConfig.create_fast_config()
        self.ai_config = ai_config or AIProviderConfig.create_openai_config()

        # 初始化各个Mixin
        # 批量处理
        DynamicBatchingMixin.__init__(self)

        # AI处理
        OpenAIProcessingMixin.__init__(
            self,
            ai_client=ai_client,
            model_name=self.ai_config.model_name
        )

        # 缓存
        MemoryCacheMixin.__init__(
            self,
            max_size=1000,  # 默认值
            ttl_seconds=3600  # 默认值
        )

        # 验证
        ContentValidationMixin.__init__(
            self,
            min_size_bytes=self.config.min_content_size,
            max_size_bytes=self.config.max_content_size or 50 * 1024 * 1024
        )

        ImageValidationMixin.__init__(
            self,
            min_width=10,
            min_height=10,
            max_width=10000,
            max_height=10000
        )

        # 错误处理
        RetryHandlerMixin.__init__(
            self,
            max_retries=self.config.retry_attempts,
            base_delay=1.0,
            max_delay=30.0
        )

        FallbackHandlerMixin.__init__(
            self,
            enable_fallback=True,
            fallback_strategies=["cache_fallback", "simple_description", "placeholder_text"]
        )

        MetricsCollectionMixin.__init__(
            self,
            enable_metrics=self.config.enable_metrics,
            metrics_window_size=1000
        )

        logger.info(f"AdaptiveImageProcessor initialized with model: {self.ai_config.model_name}")

    def validate_content(self: ContentValidator, content: ImageContent) -> List[str]:
        """
        验证内容并返回验证错误列表

        Args:
            content: 要验证的内容

        Returns:
            验证错误消息列表（空列表表示有效）
        """
        # 使用 ContentValidationMixin 的验证逻辑
        is_valid, errors = ContentValidationMixin.validate_content(self, content)
        return errors if not is_valid else []

    def should_process_batch(self: Batchable, batch_size: int, total_items: int) -> bool:
        """
        决定是否应该处理这个批次

        Args:
            batch_size: 批次大小
            total_items: 总项目数

        Returns:
            是否应该处理
        """
        # 基本检查：批次必须包含内容
        if batch_size <= 0:
            return False

        # 系统负载检查（简化实现）
        # 这里可以添加更复杂的系统负载检测逻辑
        return True

    def process_single(self, content: ImageContent) -> ProcessedContent:
        """
        Process a single image content.

        Args:
            content: Image content to process

        Returns:
            Processed content result
        """
        return self._process_single_image_with_features(content)

    def process_batch(self, contents: List[ImageContent]) -> List[ProcessedContent]:
        """
        Batch process image contents.

        Args:
            contents: List of image contents to process

        Returns:
            List of processed content results
        """
        logger.info(f"Processing {len(contents)} images with adaptive batching")
        start_time = time.time()

        # Create batches
        batches = self.create_batches(contents)
        logger.info(f"Created {len(batches)} batches")

        results = []
        for i, batch in enumerate(batches):
            # logger.info(f"Processing batch {i+1}/{len(batches)} (size: {len(batch)})")

            # Process single batch
            batch_results = self._process_single_batch(batch)
            results.extend(batch_results)

        total_time = time.time() - start_time
        logger.info(f"Processed {len(contents)} images in {total_time:.2f}s")

        return results

    def process_image_list(self: CompleteProcessor,
                          image_contents: List[ImageContent]) -> List[ProcessedContent]:
        """
        批量处理图片列表 (legacy method for compatibility)

        Args:
            image_contents: 图片内容列表

        Returns:
            处理结果列表
        """
        return self.process_batch(image_contents)

    def _process_single_batch(self: CompleteProcessor,
                            batch: List[ImageContent]) -> List[ProcessedContent]:
        """
        处理单个批次

        Args:
            batch: 图片内容批次

        Returns:
            处理结果列表
        """
        batch_results = []

        for content in batch:
            try:
                # 处理单个图片
                result = self._process_single_image_with_features(content)
                batch_results.append(result)

            except Exception as e:
                logger.error(f"Error processing image {content.content_hash[:8]}: {e}")

                # 记录错误指标
                self.record_error_metric(e, content, {"batch_size": len(batch)})

                # 使用降级处理
                fallback_result = self.handle_with_fallback(e, content, self._process_single_image)
                batch_results.append(fallback_result)

        return batch_results

    def _process_single_image_with_features(self: CompleteProcessor,
                                          content: ImageContent) -> ProcessedContent:
        """
        使用完整功能处理单个图片

        Args:
            content: 图片内容

        Returns:
            处理结果
        """
        start_time = time.time()
        success = False

        try:
            # 1. 内容验证
            is_valid, validation_errors = self.validate_content(content)
            if not is_valid:
                logger.warning(f"Content validation failed: {validation_errors}")
                processing_time = time.time() - start_time
                self._update_stats(False, processing_time)
                return ProcessedContent.create_error_result(
                    original=content,
                    error_message=f"Content validation failed: {'; '.join(validation_errors)}",
                    processing_time=processing_time
                )

            # 2. 图片属性验证
            is_valid, image_errors = self.validate_image_properties(content)
            if not is_valid:
                logger.warning(f"Image validation failed: {image_errors}")
                # 对于图片验证失败，继续处理但记录警告

            # 3. 缓存检查
            cached_result = self.get(content)
            if cached_result:
                logger.debug(f"Using cached result for {content.content_hash[:8]}")
                processing_time = time.time() - start_time
                self._update_stats(True, processing_time)
                self.record_processing_metric(content, cached_result, processing_time)
                return cached_result

            # 4. 根据配置选择处理方式
            def process_with_ai_func(content: ImageContent) -> ProcessedContent:
                return self._process_with_ai_adaptive(content)

            result = self.execute_with_retry(process_with_ai_func, content)

            # 5. 缓存结果
            self.put(content, result)

            # 6. 记录指标
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            self.record_processing_metric(content, result, processing_time)

            success = True
            return result

        except Exception as e:
            # 记录错误和指标
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            self.record_error_metric(e, content)

            # 返回错误结果
            return ProcessedContent.create_error_result(
                content=content,
                error_message=str(e),
                processing_time=processing_time
            )

    def _process_single_image(self: CompleteProcessor, content: ImageContent) -> ProcessedContent:
        """
        简单的单个图片处理（用于降级）

        Args:
            content: 图片内容

        Returns:
            处理结果
        """
        return self.process_with_ai(content)

    def _process_with_ai_adaptive(self: CompleteProcessor, content: ImageContent) -> ProcessedContent:
        """
        根据配置自适应地选择AI处理方式

        Args:
            content: 图片内容

        Returns:
            处理结果
        """
        config = getattr(self, 'config', None)
        if not config:
            # 默认使用普通处理
            return self.process_with_ai(content)

        # 根据响应格式选择处理方式
        from ..data.config import ResponseFormatType
        if config.response_format == ResponseFormatType.STRUCTURED:
            return self._process_with_structured_output(content)
        else:
            return self.process_with_ai(content)

    def _process_with_structured_output(self: CompleteProcessor, content: ImageContent) -> ProcessedContent:
        """
        使用结构化输出处理图片

        Args:
            content: 图片内容

        Returns:
            处理结果
        """
        start_time = time.time()

        try:
            # 准备结构化请求
            request_data = self.prepare_structured_request(content)

            # 调用AI服务
            response_text = self._call_ai_service(request_data)

            # 处理结构化响应
            processing_time = time.time() - start_time
            result = self.process_structured_response(response_text, content, processing_time)

            logger.debug(f"Structured processing completed for {content.content_hash[:8]}")
            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Structured processing failed for {content.content_hash[:8]}: {e}")

            # 返回错误结果
            from ..data.content import ProcessedContent, ProcessingStatus
            return ProcessedContent.create_error_result(
                original=content,
                error_message=f"Structured processing failed: {str(e)}",
                processing_time=processing_time
            )

    def process_iterator(self: CompleteProcessor,
                        image_iterator: Iterator[ImageContent]) -> Iterator[ProcessedContent]:
        """
        处理图片迭代器

        Args:
            image_iterator: 图片内容迭代器

        Yields:
            处理结果
        """
        # 将迭代器转换为列表以进行批处理
        # 注意：对于大量数据，这里可能需要流式优化
        image_list = list(image_iterator)

        # 批量处理
        results = self.process_image_list(image_list)

        # 逐个yield结果
        for result in results:
            yield result

    def get_processor_stats(self: CompleteProcessor) -> Dict[str, Any]:
        """
        获取处理器综合统计信息

        Returns:
            综合统计数据
        """
        return {
            "config": self.config.to_dict(),
            "ai_config": {
                "provider": self.ai_config.provider_name,
                "model": self.ai_config.model_name,
            },
            "base_stats": self.get_base_stats(),
            "batch_stats": self.get_batch_statistics(),
            "cache_stats": self.get_cache_stats(),
            "validation_stats": self.get_validation_stats(),
            "retry_stats": self.get_retry_stats(),
            "fallback_stats": self.get_fallback_stats(),
            "metrics_summary": self.get_metrics_summary(),
        }

    def reset_all_stats(self: CompleteProcessor) -> None:
        """重置所有统计数据"""
        self.reset_base_stats()
        self.reset_retry_stats()
        self.reset_fallback_stats()
        self.reset_metrics()

    @classmethod
    def create_openai_processor(cls,
                              api_key: Optional[str] = None,
                              model: str = "gpt-4o-mini",
                              api_base: Optional[str] = None,
                              **kwargs) -> "AdaptiveImageProcessor":
        """
        创建OpenAI处理器实例

        Args:
            api_key: OpenAI API密钥
            model: 模型名称
            api_base: API基础URL（兼容参数名，会被转换为base_url）
            **kwargs: 其他配置参数

        Returns:
            配置好的处理器实例
        """
        import openai

        # 构建客户端参数
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key

        # 处理base_url参数（支持api_base和base_url两种命名）
        base_url = api_base or kwargs.get('base_url')
        if base_url:
            client_kwargs["base_url"] = base_url

        # 过滤其他OpenAI客户端支持的参数
        supported_params = ['organization', 'timeout', 'max_retries', 'default_headers']
        for key, value in kwargs.items():
            if key in supported_params:
                client_kwargs[key] = value

        client = openai.OpenAI(**client_kwargs)

        config = ProcessingConfig(
            ai_provider="openai",
            model_name=model,
            enable_caching=True,
            enable_metrics=True
        )

        ai_config = AIProviderConfig.create_openai_config(
            model_name=model,
            api_key=api_key
        )

        return cls(ai_client=client, config=config, ai_config=ai_config)

    @classmethod
    def create_anthropic_processor(cls,
                                 api_key: Optional[str] = None,
                                 model: str = "claude-3-sonnet-20240229",
                                 api_base: Optional[str] = None,
                                 **kwargs) -> "AdaptiveImageProcessor":
        """
        创建Anthropic处理器实例

        Args:
            api_key: Anthropic API密钥
            model: 模型名称
            api_base: API基础URL（兼容参数名，会被转换为base_url）
            **kwargs: 其他配置参数

        Returns:
            配置好的处理器实例
        """
        import anthropic

        # 构建客户端参数
        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key

        # 处理base_url参数（支持api_base和base_url两种命名）
        base_url = api_base or kwargs.get('base_url')
        if base_url:
            client_kwargs["base_url"] = base_url

        # 过滤其他Anthropic客户端支持的参数
        supported_params = ['timeout', 'max_retries']
        for key, value in kwargs.items():
            if key in supported_params:
                client_kwargs[key] = value

        client = anthropic.Anthropic(**client_kwargs)

        config = ProcessingConfig(
            ai_provider="anthropic",
            model_name=model,
            enable_caching=True,
            enable_metrics=True
        )

        ai_config = AIProviderConfig.create_anthropic_config(
            model_name=model,
            api_key=api_key
        )

        return cls(ai_client=client, config=config, ai_config=ai_config)