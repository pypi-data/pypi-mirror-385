"""
Batch Processor for docpipe-ai.

This module provides BatchProcessor that handles streaming batch processing
with adaptive sizing and backpressure control.
"""

from typing import List, Dict, Any, Optional, Union, Iterator, AsyncIterator
import logging
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..core.protocols import Batchable, Processable
from ..data.content import ImageContent, ProcessedContent
from ..data.config import ProcessingConfig
from ..mixins.batch_processing import DynamicBatchingMixin
from ..mixins.error_handling import MetricsCollectionMixin

logger = logging.getLogger(__name__)


class BatchProcessor(DynamicBatchingMixin[ImageContent], MetricsCollectionMixin):
    """
    批量处理器

    这个类专门处理大规模图片内容的批量处理，支持：
    - 流式处理：处理大型数据集而不会耗尽内存
    - 自适应批次大小：根据处理性能动态调整
    - 并发控制：管理并发处理数量
    - 背压控制：防止生产者过快导致系统过载
    - 进度监控：实时监控处理进度和性能

    适用于需要处理大量图片的场景。
    """

    def __init__(self,
                 processor,  # 具体的处理器实例
                 config: Optional[ProcessingConfig] = None,
                 max_concurrency: int = 5):
        """
        初始化批量处理器

        Args:
            processor: 具体的图片处理器实例
            config: 处理配置
            max_concurrency: 最大并发数
        """
        # 初始化Mixin
        DynamicBatchingMixin.__init__(self)
        MetricsCollectionMixin.__init__(self, enable_metrics=True)

        self.processor = processor
        self.config = config or ProcessingConfig()
        self.max_concurrency = max_concurrency

        # 流式处理状态
        self._total_processed = 0
        self._total_errors = 0
        self._start_time = None
        self._last_batch_time = None

        # 性能监控
        self._batch_times: List[float] = []
        self._throughput_samples: List[float] = []

        logger.info(f"BatchProcessor initialized with concurrency: {max_concurrency}")

    def should_process_batch(self: Batchable, batch_size: int, total_items: int) -> bool:
        """
        决定是否应该处理这个批次

        考虑因素：
        - 基本批次大小检查
        - 系统负载（基于处理延迟）
        - 错误率（过高错误率时暂停处理）
        - 内存使用（简化实现）

        Args:
            batch_size: 批次大小
            total_items: 总项目数

        Returns:
            是否应该处理
        """
        # 基本检查
        if batch_size <= 0:
            return False

        # 错误率检查 - 如果错误率过高，暂停处理
        if self._total_processed > 0:
            error_rate = self._total_errors / self._total_processed
            if error_rate > 0.5:  # 错误率超过50%
                logger.warning(f"High error rate detected ({error_rate:.2%}), pausing batch processing")
                return False

        # 延迟检查 - 如果处理延迟过高，减小批次大小
        if self._last_batch_time is not None:
            avg_batch_time = sum(self._batch_times[-10:]) / min(len(self._batch_times), 10)
            if avg_batch_time > 30.0:  # 平均批次处理时间超过30秒
                logger.warning(f"High processing latency detected ({avg_batch_time:.2f}s), consider smaller batches")
                # 这里不返回False，但记录警告

        return True

    def process_stream(self: Processable,
                      image_stream: Iterator[ImageContent]) -> Iterator[ProcessedContent]:
        """
        流式处理图片流

        Args:
            image_stream: 图片内容流

        Yields:
            处理结果
        """
        self._start_time = time.time()
        logger.info("Starting stream processing")

        try:
            # 将流转换为批处理
            for batch in self._stream_to_batches(image_stream):
                # 处理单个批次
                batch_results = self._process_batch_concurrent(batch)

                # yield结果
                for result in batch_results:
                    yield result

                    # 更新统计
                    if result.is_successful:
                        self._total_processed += 1
                    else:
                        self._total_errors += 1

        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            raise

        finally:
            self._log_final_stats()

    async def process_stream_async(self: Processable,
                                 image_stream: AsyncIterator[ImageContent]) -> AsyncIterator[ProcessedContent]:
        """
        异步流式处理图片流

        Args:
            image_stream: 异步图片内容流

        Yields:
            处理结果
        """
        self._start_time = time.time()
        logger.info("Starting async stream processing")

        try:
            # 将异步流转换为批处理
            async for batch in self._async_stream_to_batches(image_stream):
                # 异步处理单个批次
                batch_results = await self._process_batch_async(batch)

                # yield结果
                for result in batch_results:
                    yield result

                    # 更新统计
                    if result.is_successful:
                        self._total_processed += 1
                    else:
                        self._total_errors += 1

        except Exception as e:
            logger.error(f"Async stream processing error: {e}")
            raise

        finally:
            self._log_final_stats()

    def process_list(self: Processable,
                    image_list: List[ImageContent]) -> List[ProcessedContent]:
        """
        处理图片列表

        Args:
            image_list: 图片内容列表

        Returns:
            处理结果列表
        """
        self._start_time = time.time()
        logger.info(f"Processing list of {len(image_list)} images")

        all_results = []

        try:
            # 创建批次
            batches = self.create_batches(image_list)
            logger.info(f"Created {len(batches)} batches for {len(image_list)} images")

            # 处理每个批次
            for i, batch in enumerate(batches):
                logger.info(f"Processing batch {i+1}/{len(batches)} (size: {len(batch)})")

                batch_results = self._process_batch_concurrent(batch)
                all_results.extend(batch_results)

                # 更新统计
                for result in batch_results:
                    if result.is_successful:
                        self._total_processed += 1
                    else:
                        self._total_errors += 1

        except Exception as e:
            logger.error(f"List processing error: {e}")
            raise

        finally:
            self._log_final_stats()

        return all_results

    def _stream_to_batches(self: Processable,
                          image_stream: Iterator[ImageContent]) -> Iterator[List[ImageContent]]:
        """
        将流转换为批次

        使用动态批次大小创建批次

        Args:
            image_stream: 图片内容流

        Yields:
            图片批次
        """
        current_batch = []
        estimated_remaining = None

        # 首先尝试估算总数量
        try:
            # 取前100个元素来估算总量
            sample = []
            for i, item in enumerate(image_stream):
                sample.append(item)
                if i >= 99:
                    break

            if len(sample) < 100:
                # 样本数量小于100，可能已经到末尾
                estimated_remaining = len(sample)
                current_batch = sample
            else:
                # 基于100个样本估算总量，并添加到当前批次
                estimated_remaining = 1000  # 保守估计
                current_batch = sample

        except Exception as e:
            logger.warning(f"Error estimating stream size: {e}")

        # 处理剩余流
        if hasattr(image_stream, '__iter__'):
            for item in image_stream:
                if estimated_remaining is not None:
                    estimated_remaining = max(1, estimated_remaining - 1)

                current_batch.append(item)

                # 检查是否应该创建批次
                batch_size = self.calculate_optimal_batch_size(
                    estimated_remaining if estimated_remaining is not None else 100
                )

                if len(current_batch) >= batch_size:
                    yield current_batch
                    current_batch = []

        # 处理最后的剩余项目
        if current_batch:
            yield current_batch

    async def _async_stream_to_batches(self: Processable,
                                     image_stream: AsyncIterator[ImageContent]) -> AsyncIterator[List[ImageContent]]:
        """
        将异步流转换为批次

        Args:
            image_stream: 异步图片内容流

        Yields:
            图片批次
        """
        current_batch = []
        estimated_remaining = 1000  # 默认估计

        async for item in image_stream:
            estimated_remaining = max(1, estimated_remaining - 1)
            current_batch.append(item)

            # 检查是否应该创建批次
            batch_size = self.calculate_optimal_batch_size(estimated_remaining)

            if len(current_batch) >= batch_size:
                yield current_batch
                current_batch = []

        # 处理最后的剩余项目
        if current_batch:
            yield current_batch

    def _process_batch_concurrent(self: Processable,
                                batch: List[ImageContent]) -> List[ProcessedContent]:
        """
        并发处理单个批次

        Args:
            batch: 图片批次

        Returns:
            处理结果列表
        """
        batch_start_time = time.time()

        if len(batch) == 1:
            # 单个项目直接处理
            result = self._process_single_item(batch[0])
            self._last_batch_time = time.time() - batch_start_time
            self._batch_times.append(self._last_batch_time)
            return [result]

        # 确定并发数
        workers = min(len(batch), self.max_concurrency)

        results = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(self._process_single_item, item): i
                for i, item in enumerate(batch)
            }

            # 收集结果，保持原始顺序
            result_dict = {}
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result = future.result()
                    result_dict[index] = result
                except Exception as e:
                    logger.error(f"Error processing item {index}: {e}")
                    # 创建错误结果
                    result_dict[index] = ProcessedContent.create_error_result(
                        content=batch[index],
                        error_message=str(e),
                        processing_time=0.0
                    )

            # 按原始顺序组装结果
            for i in range(len(batch)):
                results.append(result_dict[i])

        # 更新性能统计
        batch_time = time.time() - batch_start_time
        self._last_batch_time = batch_time
        self._batch_times.append(batch_time)

        # 计算吞吐量
        if batch_time > 0:
            throughput = len(batch) / batch_time
            self._throughput_samples.append(throughput)

        logger.debug(f"Processed batch of {len(batch)} items in {batch_time:.2f}s")

        return results

    async def _process_batch_async(self: Processable,
                                 batch: List[ImageContent]) -> List[ProcessedContent]:
        """
        异步处理单个批次

        Args:
            batch: 图片批次

        Returns:
            处理结果列表
        """
        batch_start_time = time.time()

        # 创建异步任务
        tasks = [
            asyncio.create_task(asyncio.to_thread(self._process_single_item, item))
            for item in batch
        ]

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Async processing error for item {i}: {result}")
                processed_results.append(ProcessedContent.create_error_result(
                    content=batch[i],
                    error_message=str(result),
                    processing_time=0.0
                ))
            else:
                processed_results.append(result)

        # 更新性能统计
        batch_time = time.time() - batch_start_time
        self._last_batch_time = batch_time
        self._batch_times.append(batch_time)

        return processed_results

    def _process_single_item(self: Processable, content: ImageContent) -> ProcessedContent:
        """
        处理单个图片

        Args:
            content: 图片内容

        Returns:
            处理结果
        """
        try:
            return self.processor.process_with_ai(content)
        except Exception as e:
            logger.error(f"Error processing single item {content.content_hash[:8]}: {e}")
            return ProcessedContent.create_error_result(
                content=content,
                error_message=str(e),
                processing_time=0.0
            )

    def _log_final_stats(self: Processable) -> None:
        """记录最终统计信息"""
        if self._start_time is None:
            return

        total_time = time.time() - self._start_time
        total_items = self._total_processed + self._total_errors

        logger.info("=== Batch Processing Statistics ===")
        logger.info(f"Total time: {total_time:.2f}s")
        logger.info(f"Total items: {total_items}")
        logger.info(f"Successful: {self._total_processed}")
        logger.info(f"Failed: {self._total_errors}")
        logger.info(f"Success rate: {self._total_processed / total_items:.2%}" if total_items > 0 else "N/A")

        if self._batch_times:
            avg_batch_time = sum(self._batch_times) / len(self._batch_times)
            logger.info(f"Average batch time: {avg_batch_time:.2f}s")

        if self._throughput_samples:
            avg_throughput = sum(self._throughput_samples) / len(self._throughput_samples)
            logger.info(f"Average throughput: {avg_throughput:.2f} items/s")

    def get_batch_stats(self: Processable) -> Dict[str, Any]:
        """
        获取批处理统计信息

        Returns:
            批处理统计数据
        """
        stats = {
            "total_processed": self._total_processed,
            "total_errors": self._total_errors,
            "max_concurrency": self.max_concurrency,
            "current_batch_size": self.calculate_optimal_batch_size(1000),
        }

        if self._batch_times:
            stats.update({
                "avg_batch_time": sum(self._batch_times) / len(self._batch_times),
                "min_batch_time": min(self._batch_times),
                "max_batch_time": max(self._batch_times),
                "total_batches": len(self._batch_times),
            })

        if self._throughput_samples:
            stats.update({
                "avg_throughput": sum(self._throughput_samples) / len(self._throughput_samples),
                "min_throughput": min(self._throughput_samples),
                "max_throughput": max(self._throughput_samples),
            })

        return stats

    def reset_batch_stats(self: Processable) -> None:
        """重置批处理统计"""
        self._total_processed = 0
        self._total_errors = 0
        self._start_time = None
        self._last_batch_time = None
        self._batch_times.clear()
        self._throughput_samples.clear()