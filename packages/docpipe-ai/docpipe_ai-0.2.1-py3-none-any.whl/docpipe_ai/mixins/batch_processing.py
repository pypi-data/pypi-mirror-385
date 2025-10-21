"""
Batch processing mixins for docpipe-ai.

This module provides Mixin implementations for different batch processing
strategies. These mixins can be combined with any class that implements
the Batchable protocol to add batch processing capabilities.
"""

from typing import TypeVar, Generic, List, Protocol, Dict, Any, Optional
import time
import logging
from abc import abstractmethod

from ..core.protocols import Batchable
from ..data.content import ImageContent

T = TypeVar('T')

logger = logging.getLogger(__name__)

class DynamicBatchingMixin(Generic[T]):
    """
    动态批量处理Mixin - 根据剩余数量动态调整批次大小

    这个Mixin实现了基于剩余元素数量的对数阶梯式批次大小调整策略。
    """

    def __init__(self: "Batchable"):
        """初始化动态批量处理"""
        self._batch_history: List[Dict[str, Any]] = []
        self._batch_start_time: Optional[float] = None

    def calculate_optimal_batch_size(self: "Batchable", remaining_items: int) -> int:
        """
        计算最优批次大小 - 对数阶梯式策略

        Args:
            remaining_items: 剩余要处理的元素数量

        Returns:
            最优批次大小
        """
        if remaining_items <= 10:
            return remaining_items  # 小文件：一次处理
        elif remaining_items <= 50:
            return 10  # 中小文件：较小批次
        elif remaining_items <= 200:
            return 25  # 中等文件：中等批次
        elif remaining_items <= 1000:
            return 50  # 大文件：较大批次
        else:
            return min(100, remaining_items)  # 超大文件：最大批次

    def create_batches(self: "Batchable", items: List[T]) -> List[List[T]]:
        """
        创建批次 - 使用动态批次大小

        Args:
            items: 要处理的项目列表

        Returns:
            批次列表
        """
        if not items:
            return []

        batches = []
        remaining = items.copy()
        batch_id = 0

        while remaining:
            batch_size = self.calculate_optimal_batch_size(len(remaining))

            # 使用协议方法决定是否应该处理这个批次
            if self.should_process_batch(batch_size, len(remaining)):
                batch = remaining[:batch_size]
                batches.append(batch)
                remaining = remaining[batch_size:]

                # 记录批次历史
                self._record_batch_history(batch_id, batch_size, len(remaining))
                batch_id += 1
            else:
                # 如果不应该处理，使用更小的批次
                smaller_size = max(1, batch_size // 2)
                batch = remaining[:smaller_size]
                batches.append(batch)
                remaining = remaining[smaller_size]

                self._record_batch_history(batch_id, smaller_size, len(remaining))
                batch_id += 1

        return batches

    def _record_batch_history(self: "Batchable", batch_id: int, batch_size: int, remaining_items: int) -> None:
        """记录批次历史"""
        self._batch_history.append({
            "batch_id": batch_id,
            "batch_size": batch_size,
            "remaining_items": remaining_items,
            "timestamp": time.time(),
        })

    def get_batch_statistics(self: "Batchable") -> Dict[str, Any]:
        """获取批次统计信息"""
        if not self._batch_history:
            return {}

        total_batches = len(self._batch_history)
        total_items = sum(h["batch_size"] for h in self._batch_history)
        avg_batch_size = total_items / total_batches if total_batches > 0 else 0

        return {
            "total_batches": total_batches,
            "total_items": total_items,
            "average_batch_size": avg_batch_size,
            "batch_sizes": [h["batch_size"] for h in self._batch_history],
            "processing_efficiency": self._calculate_efficiency()
        }

    def _calculate_efficiency(self: "Batchable") -> float:
        """计算处理效率"""
        if len(self._batch_history) < 2:
            return 1.0

        # 简单的效率计算：基于批次大小的一致性
        batch_sizes = [h["batch_size"] for h in self._batch_history]
        avg_size = sum(batch_sizes) / len(batch_sizes)

        if avg_size == 0:
            return 1.0

        variance = sum((size - avg_size) ** 2 for size in batch_sizes) / len(batch_sizes)
        std_dev = variance ** 0.5

        # 效率 = 1 - (标准差 / 平均值)，越稳定效率越高
        efficiency = max(0, 1 - (std_dev / avg_size))
        return round(efficiency, 3)


class FixedBatchingMixin(Generic[T]):
    """
    固定批量处理Mixin - 使用固定批次大小

    这个Mixin实现简单的固定批次大小策略，适合需要确定性行为的场景。
    """

    def __init__(self: "Batchable", fixed_batch_size: int = 10):
        """
        初始化固定批量处理

        Args:
            fixed_batch_size: 固定的批次大小
        """
        if fixed_batch_size < 1:
            raise ValueError("fixed_batch_size must be >= 1")
        self.fixed_batch_size = fixed_batch_size

    def calculate_optimal_batch_size(self: "Batchable", remaining_items: int) -> int:
        """
        计算最优批次大小 - 返回固定大小

        Args:
            remaining_items: 剩余要处理的元素数量

        Returns:
            固定的批次大小
        """
        return min(self.fixed_batch_size, remaining_items)

    def create_batches(self: "Batchable", items: List[T]) -> List[List[T]]:
        """
        创建批次 - 使用固定批次大小

        Args:
            items: 要处理的项目列表

        Returns:
            批次列表
        """
        if not items:
            return []

        batches = []
        for i in range(0, len(items), self.fixed_batch_size):
            batch = items[i:i + self.fixed_batch_size]

            if self.should_process_batch(len(batch), len(items) - i):
                batches.append(batch)
            else:
                # 如果不应该处理，跳过这个批次
                logger.warning(f"Skipping batch {i//self.fixed_batch_size + 1} due to should_process_batch")

        return batches


class AdaptiveBatchingMixin(Generic[T]):
    """
    自适应批量处理Mixin - 基于系统负载和内容特征自适应调整

    这个Mixin实现了基于系统负载、处理历史和内容特征的智能批次调整。
    """

    def __init__(self: "Batchable"):
        """初始化自适应批量处理"""
        self._performance_history: List[Dict[str, Any]] = []
        self._load_monitor = LoadMonitor()
        self._adaptive_config = AdaptiveConfig()

    def calculate_optimal_batch_size(self: "Batchable", remaining_items: int) -> int:
        """
        计算最优批次大小 - 自适应策略

        Args:
            remaining_items: 剩余要处理的元素数量

        Returns:
            最优批次大小
        """
        # 获取当前系统负载
        current_load = self._load_monitor.get_current_load()

        # 获取历史性能数据
        avg_performance = self._get_average_performance()

        # 计算基础批次大小
        base_size = self._calculate_base_batch_size(remaining_items)

        # 基于负载调整
        load_adjusted_size = self._adjust_for_load(base_size, current_load)

        # 基于性能历史调整
        performance_adjusted_size = self._adjust_for_performance(load_adjusted_size, avg_performance)

        # 应用最终调整
        final_size = self._apply_final_constraints(performance_adjusted_size, remaining_items)

        return final_size

    def create_batches(self: "Batchable", items: List[T]) -> List[List[T]]:
        """
        创建批次 - 使用自适应批次大小

        Args:
            items: 要处理的项目列表

        Returns:
            批次列表
        """
        if not items:
            return []

        batches = []
        remaining = items.copy()

        while remaining:
            batch_size = self.calculate_optimal_batch_size(len(remaining))

            if self.should_process_batch(batch_size, len(remaining)):
                batch = remaining[:batch_size]
                batches.append(batch)
                remaining = remaining[batch_size]

                # 记录批次信息用于后续优化
                self._record_batch_performance(batch, len(remaining))
            else:
                # 调整批次大小后重试
                adjusted_size = max(1, batch_size // 2)
                batch = remaining[:adjusted_size]
                batches.append(batch)
                remaining = remaining[adjusted_size]

        return batches

    def _calculate_base_batch_size(self: "Batchable", remaining_items: int) -> int:
        """计算基础批次大小"""
        if remaining_items <= self._adaptive_config.small_file_threshold:
            return remaining_items
        elif remaining_items <= self._adaptive_config.medium_file_threshold:
            return self._adaptive_config.medium_batch_size
        elif remaining_items <= self._adaptive_config.large_file_threshold:
            return self._adaptive_config.large_batch_size
        else:
            return self._adaptive_config.max_batch_size

    def _adjust_for_load(self: "Batchable", base_size: int, current_load: float) -> int:
        """基于系统负载调整批次大小"""
        if current_load > 0.8:
            # 高负载：减小批次
            return max(1, int(base_size * 0.6))
        elif current_load < 0.3:
            # 低负载：增大批次
            return int(base_size * 1.4)
        else:
            # 中等负载：保持不变
            return base_size

    def _adjust_for_performance(self: "Batchable", size: int, avg_performance: float) -> int:
        """基于历史性能调整批次大小"""
        if avg_performance > 0.9:
            # 性能很好：可以增大批次
            return int(size * 1.2)
        elif avg_performance < 0.5:
            # 性能较差：减小批次
            return max(1, int(size * 0.8))
        else:
            return size

    def _apply_final_constraints(self: "Batchable", size: int, remaining_items: int) -> int:
        """应用最终约束条件"""
        # 不能超过最大批次大小
        max_size = min(size, self._adaptive_config.max_batch_size)

        # 不能小于最小批次大小
        min_size = max(max_size, self._adaptive_config.min_batch_size)

        # 不能超过剩余项目数
        return min(min_size, remaining_items)

    def _record_batch_performance(self: "Batchable", batch: List[T], remaining_items: int) -> None:
        """记录批次性能"""
        self._performance_history.append({
            "batch_size": len(batch),
            "remaining_items": remaining_items,
            "timestamp": time.time(),
            # 性能指标会在实际处理后更新
        })

    def _get_average_performance(self: "Batchable") -> float:
        """获取平均性能"""
        if not self._performance_history:
            return 0.7  # 默认中等性能

        # 简单的性能指标：基于最近的批次大小趋势
        recent_history = self._performance_history[-10:]  # 最近10个批次
        if len(recent_history) < 2:
            return 0.7

        avg_size = sum(h["batch_size"] for h in recent_history) / len(recent_history)
        expected_size = self._adaptive_config.target_batch_size

        # 性能分数：批次大小越接近目标值，性能越好
        performance = 1.0 - abs(avg_size - expected_size) / expected_size
        return max(0, min(1, performance))

    def update_batch_performance(self: "Batchable", batch_id: int, processing_time: float, success: bool) -> None:
        """更新批次性能记录"""
        if batch_id < len(self._performance_history):
            self._performance_history[batch_id].update({
                "processing_time": processing_time,
                "success": success,
                "throughput": len(self._performance_history[batch_id]["batch"]) / processing_time if processing_time > 0 else 0
            })


class LoadMonitor:
    """系统负载监控器"""

    def __init__(self):
        self._load_samples: List[float] = []
        self._sample_window = 60  # 样本窗口大小（秒）

    def get_current_load(self) -> float:
        """获取当前系统负载"""
        # 简化实现：基于CPU和内存使用情况
        import psutil
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent

            # 综合负载指标
            current_load = (cpu_percent + memory_percent) / 200  # 归一化到0-1

            self._load_samples.append(current_load)

            # 保持样本窗口大小
            if len(self._load_samples) > self._sample_window:
                self._load_samples.pop(0)

            return current_load
        except ImportError:
            # 如果没有psutil，返回默认负载
            return 0.5


class AdaptiveConfig:
    """自适应配置"""

    def __init__(self):
        # 文件大小阈值
        self.small_file_threshold = 20
        self.medium_file_threshold = 200
        self.large_file_threshold = 1000

        # 批次大小配置
        self.min_batch_size = 1
        self.medium_batch_size = 25
        self.large_batch_size = 50
        self.max_batch_size = 100
        self.target_batch_size = 25