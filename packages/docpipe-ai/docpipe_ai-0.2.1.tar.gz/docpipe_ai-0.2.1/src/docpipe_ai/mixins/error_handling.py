"""
Error handling mixins for docpipe-ai.

This module provides Mixin implementations for error handling strategies.
These mixins can be combined with any class that implements the ErrorHandler protocol
to add error handling capabilities.
"""

from typing import Dict, Any, List, Optional, Callable, Type, Union
import time
import logging
import random
from abc import abstractmethod
from enum import Enum
import threading

from ..core.protocols import ErrorHandler
from ..data.content import ImageContent, ProcessedContent, ProcessingStatus

logger = logging.getLogger(__name__)

class ErrorCategory(str, Enum):
    """错误分类枚举"""
    NETWORK = "network"
    API_LIMIT = "api_limit"
    AUTHENTICATION = "authentication"
    CONTENT_VALIDATION = "content_validation"
    PROCESSING = "processing"
    MEMORY = "memory"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"

class RetryStrategy(str, Enum):
    """重试策略枚举"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    JITTER_BACKOFF = "jitter_backoff"
    NO_RETRY = "no_retry"

class RetryHandlerMixin:
    """
    重试处理Mixin - 提供智能重试功能

    这个Mixin实现了多种重试策略，包括指数退避、线性退避等。
    """

    def __init__(self: "ErrorHandler",
                 max_retries: int = 3,
                 base_delay: float = 1.0,
                 max_delay: float = 60.0,
                 retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
                 jitter: bool = True,
                 retry_on_errors: Optional[List[Type[Exception]]] = None):
        """
        初始化重试处理

        Args:
            max_retries: 最大重试次数
            base_delay: 基础延迟时间（秒）
            max_delay: 最大延迟时间（秒）
            retry_strategy: 重试策略
            jitter: 是否添加随机抖动
            retry_on_errors: 需要重试的异常类型列表
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_strategy = retry_strategy
        self.jitter = jitter
        self.retry_on_errors = retry_on_errors or [
            ConnectionError, TimeoutError, OSError
        ]

        # 统计信息
        self._retry_stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "retry_by_category": {}
        }

    def handle_error_with_retry(self: "ErrorHandler",
                              error: Exception,
                              content: ImageContent,
                              attempt: int) -> Dict[str, Any]:
        """
        处理错误并决定是否重试

        Args:
            error: 发生的异常
            content: 正在处理的内容
            attempt: 当前尝试次数

        Returns:
            重试决策信息
        """
        # 分类错误
        error_category = self._categorize_error(error)

        # 决定是否重试
        should_retry = self._should_retry(error, error_category, attempt)

        # 计算延迟时间
        delay = self._calculate_delay(attempt) if should_retry else 0.0

        # 更新统计
        self._update_retry_stats(error_category, should_retry)

        retry_info = {
            "should_retry": should_retry,
            "delay": delay,
            "error_category": error_category,
            "attempt": attempt,
            "max_retries": self.max_retries,
            "error_message": str(error),
            "error_type": type(error).__name__
        }

        logger.info(f"Retry decision: {retry_info}")
        return retry_info

    def execute_with_retry(self: "ErrorHandler",
                          func: Callable,
                          content: ImageContent,
                          *args, **kwargs) -> Any:
        """
        执行函数并在失败时重试

        Args:
            func: 要执行的函数
            content: 要处理的内容
            *args, **kwargs: 函数参数

        Returns:
            函数执行结果

        Raises:
            最后一次执行的异常（如果所有重试都失败）
        """
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                result = func(content, *args, **kwargs)

                # 如果不是第一次尝试，记录成功重试
                if attempt > 0:
                    self._retry_stats["successful_retries"] += 1
                    logger.info(f"Retry successful on attempt {attempt + 1}")

                return result

            except Exception as e:
                last_exception = e

                # 获取重试决策
                retry_info = self.handle_error_with_retry(e, content, attempt)

                if not retry_info["should_retry"]:
                    break

                # 等待后重试
                if retry_info["delay"] > 0:
                    logger.warning(
                        f"Retrying in {retry_info['delay']:.2f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    time.sleep(retry_info["delay"])

        # 所有重试都失败
        self._retry_stats["failed_retries"] += 1
        logger.error(f"All retry attempts failed for {content.content_hash[:8]}")
        raise last_exception

    def _categorize_error(self: "ErrorHandler", error: Exception) -> ErrorCategory:
        """分类错误类型"""
        error_type = type(error).__name__
        error_message = str(error).lower()

        # 网络相关错误
        if any(keyword in error_message for keyword in [
            "connection", "network", "dns", "socket", "unreachable"
        ]) or isinstance(error, ConnectionError):
            return ErrorCategory.NETWORK

        # API限制错误
        if any(keyword in error_message for keyword in [
            "rate limit", "quota", "too many requests", "429"
        ]):
            return ErrorCategory.API_LIMIT

        # 认证错误
        if any(keyword in error_message for keyword in [
            "authentication", "authorization", "unauthorized", "401", "403"
        ]):
            return ErrorCategory.AUTHENTICATION

        # 内容验证错误
        if any(keyword in error_message for keyword in [
            "invalid content", "corrupted", "malformed", "validation"
        ]):
            return ErrorCategory.CONTENT_VALIDATION

        # 处理错误
        if any(keyword in error_message for keyword in [
            "processing", "internal", "server error", "500"
        ]):
            return ErrorCategory.PROCESSING

        # 内存错误
        if any(keyword in error_message for keyword in [
            "memory", "out of memory", "allocation"
        ]) or isinstance(error, MemoryError):
            return ErrorCategory.MEMORY

        # 超时错误
        if "timeout" in error_message or isinstance(error, TimeoutError):
            return ErrorCategory.TIMEOUT

        return ErrorCategory.UNKNOWN

    def _should_retry(self: "ErrorHandler", error: Exception,
                     error_category: ErrorCategory, attempt: int) -> bool:
        """决定是否应该重试"""
        # 检查重试次数限制
        if attempt >= self.max_retries:
            return False

        # 检查异常类型
        if not any(isinstance(error, error_type) for error_type in self.retry_on_errors):
            return False

        # 根据错误类别决定
        no_retry_categories = {
            ErrorCategory.AUTHENTICATION,  # 认证错误重试无意义
            ErrorCategory.CONTENT_VALIDATION,  # 内容问题重试无意义
        }

        if error_category in no_retry_categories:
            return False

        return True

    def _calculate_delay(self: "ErrorHandler", attempt: int) -> float:
        """计算延迟时间"""
        if self.retry_strategy == RetryStrategy.NO_RETRY:
            return 0.0

        elif self.retry_strategy == RetryStrategy.FIXED_INTERVAL:
            delay = self.base_delay

        elif self.retry_strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.base_delay * (attempt + 1)

        elif self.retry_strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.base_delay * (2 ** attempt)

        elif self.retry_strategy == RetryStrategy.JITTER_BACKOFF:
            base_delay = self.base_delay * (2 ** attempt)
            # 添加±50%的随机抖动
            jitter_factor = 0.5 + random.random()  # 0.5 to 1.5
            delay = base_delay * jitter_factor

        else:
            delay = self.base_delay

        # 应用最大延迟限制
        delay = min(delay, self.max_delay)

        return delay

    def _update_retry_stats(self: "ErrorHandler", error_category: ErrorCategory, will_retry: bool) -> None:
        """更新重试统计"""
        if will_retry:
            self._retry_stats["total_retries"] += 1

            category_stats = self._retry_stats["retry_by_category"]
            if error_category not in category_stats:
                category_stats[error_category] = 0
            category_stats[error_category] += 1

    def get_retry_stats(self: "ErrorHandler") -> Dict[str, Any]:
        """获取重试统计信息"""
        stats = self._retry_stats.copy()
        stats.update({
            "max_retries": self.max_retries,
            "base_delay": self.base_delay,
            "max_delay": self.max_delay,
            "retry_strategy": self.retry_strategy.value,
            "jitter_enabled": self.jitter
        })
        return stats

    def reset_retry_stats(self: "ErrorHandler") -> None:
        """重置重试统计"""
        self._retry_stats = {
            "total_retries": 0,
            "successful_retries": 0,
            "failed_retries": 0,
            "retry_by_category": {}
        }


class FallbackHandlerMixin:
    """
    降级处理Mixin - 提供降级和回退功能

    这个Mixin实现了多种降级策略，当主要处理方式失败时提供备选方案。
    """

    def __init__(self: "ErrorHandler",
                 enable_fallback: bool = True,
                 fallback_strategies: Optional[List[str]] = None,
                 fallback_timeout: float = 30.0):
        """
        初始化降级处理

        Args:
            enable_fallback: 是否启用降级
            fallback_strategies: 降级策略列表
            fallback_timeout: 降级处理超时时间
        """
        self.enable_fallback = enable_fallback
        self.fallback_strategies = fallback_strategies or [
            "cache_fallback",
            "simple_description",
            "placeholder_text",
            "skip_processing"
        ]
        self.fallback_timeout = fallback_timeout

        # 统计信息
        self._fallback_stats = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "fallback_by_strategy": {}
        }

    def handle_with_fallback(self: "ErrorHandler",
                           error: Exception,
                           content: ImageContent,
                           primary_func: Callable) -> ProcessedContent:
        """
        在主处理失败时尝试降级处理

        Args:
            error: 主处理失败时的异常
            content: 要处理的内容
            primary_func: 主处理函数

        Returns:
            处理结果（可能来自降级策略）
        """
        if not self.enable_fallback:
            # 如果没有降级，创建错误结果
            return ProcessedContent.create_error_result(
                original=content,
                error_message=f"Primary processing failed: {error}",
                processing_time=0.0
            )

        self._fallback_stats["total_fallbacks"] += 1

        # 尝试各种降级策略
        for strategy in self.fallback_strategies:
            try:
                result = self._execute_fallback_strategy(strategy, content, error)
                if result:
                    self._fallback_stats["successful_fallbacks"] += 1
                    logger.info(f"Fallback strategy '{strategy}' succeeded")
                    return result

            except Exception as fallback_error:
                logger.warning(
                    f"Fallback strategy '{strategy}' failed: {fallback_error}"
                )
                continue

        # 所有降级策略都失败
        self._fallback_stats["failed_fallbacks"] += 1
        logger.error("All fallback strategies failed")

        return ProcessedContent.create_error_result(
            original=content,
            error_message=f"All processing methods failed. Primary error: {error}",
            processing_time=0.0
        )

    def _execute_fallback_strategy(self: "ErrorHandler",
                                 strategy: str,
                                 content: ImageContent,
                                 original_error: Exception) -> Optional[ProcessedContent]:
        """执行特定的降级策略"""
        if strategy == "cache_fallback":
            return self._cache_fallback(content)

        elif strategy == "simple_description":
            return self._simple_description_fallback(content)

        elif strategy == "placeholder_text":
            return self._placeholder_text_fallback(content)

        elif strategy == "skip_processing":
            return self._skip_processing_fallback(content, original_error)

        else:
            logger.warning(f"Unknown fallback strategy: {strategy}")
            return None

    def _cache_fallback(self: "ErrorHandler", content: ImageContent) -> Optional[ProcessedContent]:
        """缓存降级：尝试从缓存获取结果"""
        try:
            # 这里假设处理器有缓存功能
            if hasattr(self, 'get') and hasattr(self, 'get_cache_key'):
                cached_result = self.get(content)
                if cached_result:
                    logger.info("Using cached result as fallback")
                    return cached_result
        except Exception as e:
            logger.debug(f"Cache fallback failed: {e}")
        return None

    def _simple_description_fallback(self: "ErrorHandler", content: ImageContent) -> ProcessedContent:
        """简单描述降级：基于元数据生成简单描述"""
        try:
            # 基于图片基本信息生成描述
            page = content.page
            bbox = content.bbox.to_list()
            size = len(content.binary_data)

            # 如果有元数据，使用元数据信息
            if content.metadata:
                format_info = content.metadata.format.value
                if content.metadata.width_pixels and content.metadata.height_pixels:
                    size_info = f"{content.metadata.width_pixels}x{content.metadata.height_pixels}"
                else:
                    size_info = "unknown size"
                description = f"第{page}页的{format_info}格式图片，位置{bbox}，{size_info}，约{size}字节"
            else:
                description = f"第{page}页的图片，位置{bbox}，约{size}字节"

            return ProcessedContent(
                original=content,
                processed_text=description,
                status=ProcessingStatus.COMPLETED,
                metrics=None  # 可以添加简单的指标
            )

        except Exception as e:
            logger.error(f"Simple description fallback failed: {e}")
            raise

    def _placeholder_text_fallback(self: "ErrorHandler", content: ImageContent) -> ProcessedContent:
        """占位符降级：返回固定的占位符文本"""
        placeholder = f"[图片内容 - 第{content.page}页]"

        return ProcessedContent(
            original=content,
            processed_text=placeholder,
            status=ProcessingStatus.COMPLETED,
            metrics=None
        )

    def _skip_processing_fallback(self: "ErrorHandler", content: ImageContent,
                                 original_error: Exception) -> ProcessedContent:
        """跳过处理降级：标记为跳过但保留原始内容"""
        return ProcessedContent(
            original=content,
            processed_text="",
            status=ProcessingStatus.SKIPPED,
            error_message=f"Skipped due to processing error: {original_error}",
            metrics=None
        )

    def get_fallback_stats(self: "ErrorHandler") -> Dict[str, Any]:
        """获取降级统计信息"""
        stats = self._fallback_stats.copy()
        stats.update({
            "fallback_enabled": self.enable_fallback,
            "available_strategies": self.fallback_strategies,
            "fallback_timeout": self.fallback_timeout
        })
        return stats

    def reset_fallback_stats(self: "ErrorHandler") -> None:
        """重置降级统计"""
        self._fallback_stats = {
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "fallback_by_strategy": {}
        }


class MetricsCollectionMixin:
    """
    指标收集Mixin - 提供处理指标收集功能

    这个Mixin收集和处理各种性能指标，用于监控和优化。
    """

    def __init__(self: "ErrorHandler",
                 enable_metrics: bool = True,
                 metrics_window_size: int = 1000):
        """
        初始化指标收集

        Args:
            enable_metrics: 是否启用指标收集
            metrics_window_size: 指标窗口大小
        """
        self.enable_metrics = enable_metrics
        self.metrics_window_size = metrics_window_size

        # 指标存储
        self._metrics_lock = threading.RLock()
        self._processing_metrics: List[Dict[str, Any]] = []
        self._error_metrics: List[Dict[str, Any]] = []
        self._performance_summary = {}

    def record_processing_metric(self: "ErrorHandler",
                                content: ImageContent,
                                result: ProcessedContent,
                                processing_time: float) -> None:
        """
        记录处理指标

        Args:
            content: 处理的内容
            result: 处理结果
            processing_time: 处理时间
        """
        if not self.enable_metrics:
            return

        with self._metrics_lock:
            metric = {
                "timestamp": time.time(),
                "content_size": len(content.binary_data),
                "content_hash": content.content_hash[:8],
                "page": content.page,
                "processing_time": processing_time,
                "status": result.status.value,
                "success": result.is_successful,
                "text_length": len(result.processed_text) if result.processed_text else 0,
                "confidence": result.metrics.confidence if result.metrics else 0.0,
                "cache_hit": result.metrics.cache_hit if result.metrics else False,
                "retry_count": result.metrics.retry_count if result.metrics else 0,
            }

            self._processing_metrics.append(metric)

            # 维护窗口大小
            if len(self._processing_metrics) > self.metrics_window_size:
                self._processing_metrics.pop(0)

            # 更新性能摘要
            self._update_performance_summary()

    def record_error_metric(self: "ErrorHandler",
                           error: Exception,
                           content: ImageContent,
                           context: Optional[Dict[str, Any]] = None) -> None:
        """
        记录错误指标

        Args:
            error: 发生的错误
            content: 处理的内容
            context: 上下文信息
        """
        if not self.enable_metrics:
            return

        with self._metrics_lock:
            error_metric = {
                "timestamp": time.time(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "content_size": len(content.binary_data),
                "content_hash": content.content_hash[:8],
                "page": content.page,
                "context": context or {},
            }

            self._error_metrics.append(error_metric)

            # 维护窗口大小
            if len(self._error_metrics) > self.metrics_window_size:
                self._error_metrics.pop(0)

    def get_metrics_summary(self: "ErrorHandler") -> Dict[str, Any]:
        """
        获取指标摘要

        Returns:
            详细的指标摘要
        """
        if not self.enable_metrics:
            return {"metrics_enabled": False}

        with self._metrics_lock:
            summary = {
                "metrics_enabled": True,
                "window_size": self.metrics_window_size,
                "total_processed": len(self._processing_metrics),
                "total_errors": len(self._error_metrics),
                "performance_summary": self._performance_summary.copy(),
            }

            # 添加错误分析
            if self._error_metrics:
                summary["error_analysis"] = self._analyze_errors()

            return summary

    def _update_performance_summary(self: "ErrorHandler") -> None:
        """更新性能摘要"""
        if not self._processing_metrics:
            return

        # 计算基本统计
        processing_times = [m["processing_time"] for m in self._processing_metrics]
        success_count = sum(1 for m in self._processing_metrics if m["success"])
        cache_hit_count = sum(1 for m in self._processing_metrics if m.get("cache_hit", False))

        self._performance_summary = {
            "avg_processing_time": sum(processing_times) / len(processing_times),
            "min_processing_time": min(processing_times),
            "max_processing_time": max(processing_times),
            "success_rate": success_count / len(self._processing_metrics),
            "cache_hit_rate": cache_hit_count / len(self._processing_metrics),
            "total_processed": len(self._processing_metrics),
            "throughput_per_second": len(self._processing_metrics) / (time.time() - self._processing_metrics[0]["timestamp"]) if len(self._processing_metrics) > 1 else 0,
        }

    def _analyze_errors(self: "ErrorHandler") -> Dict[str, Any]:
        """分析错误模式"""
        if not self._error_metrics:
            return {}

        # 按错误类型统计
        error_types = {}
        for metric in self._error_metrics:
            error_type = metric["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1

        # 按时间分析（最近N个错误）
        recent_errors = self._error_metrics[-10:] if len(self._error_metrics) >= 10 else self._error_metrics
        error_rate = len(recent_errors) / (time.time() - recent_errors[0]["timestamp"]) if len(recent_errors) > 1 else 0

        return {
            "error_types": error_types,
            "most_common_error": max(error_types.items(), key=lambda x: x[1])[0] if error_types else None,
            "recent_error_rate": error_rate,
            "total_unique_errors": len(error_types),
        }

    def reset_metrics(self: "ErrorHandler") -> None:
        """重置所有指标"""
        with self._metrics_lock:
            self._processing_metrics.clear()
            self._error_metrics.clear()
            self._performance_summary.clear()
            logger.info("Metrics reset")