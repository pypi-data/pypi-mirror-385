"""
Caching mixins for docpipe-ai.

This module provides Mixin implementations for different caching strategies.
These mixins can be combined with any class that implements the Cacheable protocol
to add caching capabilities.
"""

from typing import Dict, Any, Optional, List, Union
import time
import json
import hashlib
import logging
from pathlib import Path
from abc import abstractmethod
import threading
from collections import OrderedDict

from ..core.protocols import Cacheable
from ..data.content import ImageContent, ProcessedContent

logger = logging.getLogger(__name__)

class MemoryCacheMixin:
    """
    内存缓存Mixin - 提供线程安全的内存缓存功能

    这个Mixin实现了LRU缓存策略，适合单进程应用场景。
    """

    def __init__(self: "Cacheable", max_size: int = 1000, ttl_seconds: int = 3600):
        """
        初始化内存缓存

        Args:
            max_size: 最大缓存条目数
            ttl_seconds: 缓存TTL（秒）
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._cache_lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get_cache_key(self: "Cacheable", content: ImageContent) -> str:
        """
        生成缓存键

        Args:
            content: 图片内容

        Returns:
            缓存键
        """
        # 基于内容哈希和元数据生成唯一键
        hash_input = f"{content.content_hash}_{content.page}_{content.bbox.to_list()}"
        cache_key = hashlib.md5(hash_input.encode()).hexdigest()
        return f"img_{cache_key}"

    def get(self: "Cacheable", content: ImageContent) -> Optional[ProcessedContent]:
        """
        从缓存获取处理结果

        Args:
            content: 图片内容

        Returns:
            缓存的处理结果，如果不存在或已过期则返回None
        """
        cache_key = self.get_cache_key(content)

        with self._cache_lock:
            if cache_key not in self._cache:
                self._misses += 1
                return None

            cache_entry = self._cache[cache_key]
            current_time = time.time()

            # 检查是否过期
            if current_time - cache_entry["timestamp"] > self.ttl_seconds:
                del self._cache[cache_key]
                self._misses += 1
                logger.debug(f"Cache entry expired for {cache_key}")
                return None

            # 移动到末尾（LRU更新）
            self._cache.move_to_end(cache_key)
            self._hits += 1

            logger.debug(f"Cache hit for {cache_key}")
            return cache_entry["data"]

    def put(self: "Cacheable", content: ImageContent, result: ProcessedContent) -> None:
        """
        将处理结果存入缓存

        Args:
            content: 原始图片内容
            result: 处理结果
        """
        cache_key = self.get_cache_key(content)

        with self._cache_lock:
            current_time = time.time()

            # 如果键已存在，更新它
            if cache_key in self._cache:
                self._cache[cache_key] = {
                    "data": result,
                    "timestamp": current_time
                }
                self._cache.move_to_end(cache_key)
            else:
                # 添加新条目
                self._cache[cache_key] = {
                    "data": result,
                    "timestamp": current_time
                }

                # 检查缓存大小限制
                while len(self._cache) > self.max_size:
                    oldest_key = next(iter(self._cache))
                    del self._cache[oldest_key]
                    logger.debug(f"Evicted oldest cache entry: {oldest_key}")

            logger.debug(f"Cached result for {cache_key}")

    def invalidate(self: "Cacheable", content: ImageContent) -> bool:
        """
        使特定内容的缓存失效

        Args:
            content: 图片内容

        Returns:
            是否成功删除缓存条目
        """
        cache_key = self.get_cache_key(content)

        with self._cache_lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                logger.debug(f"Invalidated cache for {cache_key}")
                return True
            return False

    def clear_cache(self: "Cacheable") -> int:
        """
        清空所有缓存

        Returns:
            清除的缓存条目数
        """
        with self._cache_lock:
            count = len(self._cache)
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info(f"Cleared {count} cache entries")
            return count

    def get_cache_stats(self: "Cacheable") -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计数据
        """
        with self._cache_lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            return {
                "cache_type": "memory",
                "total_entries": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "ttl_seconds": self.ttl_seconds,
                "memory_usage_mb": round(self._estimate_memory_usage() / 1024 / 1024, 2)
            }

    def _estimate_memory_usage(self: "Cacheable") -> int:
        """估算内存使用量（字节）"""
        import sys
        total_size = 0
        for cache_entry in self._cache.values():
            total_size += sys.getsizeof(cache_entry)
            # 估算数据结构大小
            if hasattr(cache_entry["data"], "__sizeof__"):
                total_size += cache_entry["data"].__sizeof__()
        return total_size


class FileCacheMixin:
    """
    文件缓存Mixin - 提供基于文件的持久化缓存功能

    这个Mixin将缓存数据持久化到磁盘，适合跨会话缓存。
    """

    def __init__(self: "Cacheable", cache_dir: Union[str, Path],
                 max_files: int = 10000, ttl_seconds: int = 86400):
        """
        初始化文件缓存

        Args:
            cache_dir: 缓存目录路径
            max_files: 最大缓存文件数
            ttl_seconds: 缓存TTL（秒）
        """
        self.cache_dir = Path(cache_dir)
        self.max_files = max_files
        self.ttl_seconds = ttl_seconds

        # 确保缓存目录存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # 使用索引文件管理缓存元数据
        self._index_file = self.cache_dir / "cache_index.json"
        self._index_lock = threading.RLock()

        # 加载现有索引
        self._load_cache_index()

        # 统计信息
        self._hits = 0
        self._misses = 0

    def get_cache_key(self: "Cacheable", content: ImageContent) -> str:
        """
        生成缓存键

        Args:
            content: 图片内容

        Returns:
            缓存键
        """
        hash_input = f"{content.content_hash}_{content.page}_{content.bbox.to_list()}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def get(self: "Cacheable", content: ImageContent) -> Optional[ProcessedContent]:
        """
        从缓存获取处理结果

        Args:
            content: 图片内容

        Returns:
            缓存的处理结果，如果不存在或已过期则返回None
        """
        cache_key = self.get_cache_key(content)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with self._index_lock:
            # 检查索引中是否存在该键
            if cache_key not in self._cache_index:
                self._misses += 1
                return None

            cache_entry = self._cache_index[cache_key]
            current_time = time.time()

            # 检查是否过期
            if current_time - cache_entry["timestamp"] > self.ttl_seconds:
                self._remove_cache_entry(cache_key)
                self._misses += 1
                logger.debug(f"Cache entry expired for {cache_key}")
                return None

            # 检查文件是否存在
            if not cache_file.exists():
                self._remove_cache_entry(cache_key)
                self._misses += 1
                logger.warning(f"Cache file missing for {cache_key}")
                return None

            try:
                # 读取缓存文件
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                # 重建ProcessedContent对象
                result = self._deserialize_result(cache_data["result"])

                # 更新访问时间
                cache_entry["last_access"] = current_time
                self._save_cache_index()

                self._hits += 1
                logger.debug(f"Cache hit for {cache_key}")
                return result

            except Exception as e:
                logger.error(f"Error reading cache file {cache_file}: {e}")
                self._remove_cache_entry(cache_key)
                self._misses += 1
                return None

    def put(self: "Cacheable", content: ImageContent, result: ProcessedContent) -> None:
        """
        将处理结果存入缓存

        Args:
            content: 原始图片内容
            result: 处理结果
        """
        cache_key = self.get_cache_key(content)
        cache_file = self.cache_dir / f"{cache_key}.json"

        with self._index_lock:
            current_time = time.time()

            try:
                # 准备缓存数据
                cache_data = {
                    "cache_key": cache_key,
                    "content_hash": content.content_hash,
                    "result": self._serialize_result(result),
                    "metadata": {
                        "page": content.page,
                        "bbox": content.bbox.to_list(),
                        "content_size": len(content.binary_data)
                    }
                }

                # 写入缓存文件
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)

                # 更新索引
                self._cache_index[cache_key] = {
                    "timestamp": current_time,
                    "last_access": current_time,
                    "file_size": cache_file.stat().st_size
                }

                # 检查文件数量限制
                self._enforce_file_limit()

                self._save_cache_index()
                logger.debug(f"Cached result for {cache_key}")

            except Exception as e:
                logger.error(f"Error writing cache file {cache_file}: {e}")

    def invalidate(self: "Cacheable", content: ImageContent) -> bool:
        """
        使特定内容的缓存失效

        Args:
            content: 图片内容

        Returns:
            是否成功删除缓存条目
        """
        cache_key = self.get_cache_key(content)

        with self._index_lock:
            return self._remove_cache_entry(cache_key)

    def clear_cache(self: "Cacheable") -> int:
        """
        清空所有缓存

        Returns:
            清除的缓存条目数
        """
        with self._index_lock:
            count = len(self._cache_index)

            # 删除所有缓存文件
            for cache_key in list(self._cache_index.keys()):
                self._remove_cache_entry(cache_key)

            self._hits = 0
            self._misses = 0

            logger.info(f"Cleared {count} cache entries")
            return count

    def get_cache_stats(self: "Cacheable") -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计数据
        """
        with self._index_lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

            # 计算总文件大小
            total_size = sum(
                entry.get("file_size", 0)
                for entry in self._cache_index.values()
            )

            return {
                "cache_type": "file",
                "total_entries": len(self._cache_index),
                "max_files": self.max_files,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "ttl_seconds": self.ttl_seconds,
                "cache_dir": str(self.cache_dir),
                "total_size_mb": round(total_size / 1024 / 1024, 2)
            }

    def _load_cache_index(self: "Cacheable") -> None:
        """加载缓存索引"""
        if self._index_file.exists():
            try:
                with open(self._index_file, 'r', encoding='utf-8') as f:
                    self._cache_index = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading cache index: {e}")
                self._cache_index = {}
        else:
            self._cache_index = {}

    def _save_cache_index(self: "Cacheable") -> None:
        """保存缓存索引"""
        try:
            with open(self._index_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache index: {e}")

    def _remove_cache_entry(self: "Cacheable", cache_key: str) -> bool:
        """删除缓存条目"""
        if cache_key not in self._cache_index:
            return False

        try:
            # 删除缓存文件
            cache_file = self.cache_dir / f"{cache_key}.json"
            if cache_file.exists():
                cache_file.unlink()

            # 从索引中删除
            del self._cache_index[cache_key]

            logger.debug(f"Removed cache entry: {cache_key}")
            return True

        except Exception as e:
            logger.error(f"Error removing cache entry {cache_key}: {e}")
            return False

    def _enforce_file_limit(self: "Cacheable") -> None:
        """强制执行文件数量限制"""
        if len(self._cache_index) <= self.max_files:
            return

        # 按最后访问时间排序，删除最旧的条目
        sorted_entries = sorted(
            self._cache_index.items(),
            key=lambda x: x[1]["last_access"]
        )

        # 删除最旧的条目，直到数量符合限制
        excess_count = len(self._cache_index) - self.max_files
        for cache_key, _ in sorted_entries[:excess_count]:
            self._remove_cache_entry(cache_key)

        logger.info(f"Removed {excess_count} old cache entries to enforce file limit")

    def _serialize_result(self: "Cacheable", result: ProcessedContent) -> Dict[str, Any]:
        """序列化处理结果"""
        return result.to_dict()

    def _deserialize_result(self: "Cacheable", data: Dict[str, Any]) -> ProcessedContent:
        """反序列化处理结果"""
        return ProcessedContent.from_dict(data)


class RedisCacheMixin:
    """
    Redis缓存Mixin - 提供基于Redis的分布式缓存功能

    这个Mixin使用Redis作为缓存后端，适合多进程/多服务器部署。
    """

    def __init__(self: "Cacheable", redis_client=None, key_prefix: str = "docpipe_ai",
                 ttl_seconds: int = 3600, max_connections: int = 10):
        """
        初始化Redis缓存

        Args:
            redis_client: Redis客户端实例
            key_prefix: 键前缀
            ttl_seconds: 缓存TTL（秒）
            max_connections: 最大连接数
        """
        if redis_client is None:
            raise ValueError("redis_client is required for RedisCacheMixin")

        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.ttl_seconds = ttl_seconds
        self.max_connections = max_connections

        self._hits = 0
        self._misses = 0

    def get_cache_key(self: "Cacheable", content: ImageContent) -> str:
        """
        生成缓存键

        Args:
            content: 图片内容

        Returns:
            缓存键
        """
        hash_input = f"{content.content_hash}_{content.page}_{content.bbox.to_list()}"
        content_hash = hashlib.md5(hash_input.encode()).hexdigest()
        return f"{self.key_prefix}:image:{content_hash}"

    def get(self: "Cacheable", content: ImageContent) -> Optional[ProcessedContent]:
        """
        从缓存获取处理结果

        Args:
            content: 图片内容

        Returns:
            缓存的处理结果，如果不存在或已过期则返回None
        """
        cache_key = self.get_cache_key(content)

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data is None:
                self._misses += 1
                return None

            # 反序列化数据
            cache_json = json.loads(cached_data)
            result = self._deserialize_result(cache_json["result"])

            self._hits += 1
            logger.debug(f"Redis cache hit for {cache_key}")
            return result

        except Exception as e:
            logger.error(f"Error getting from Redis cache: {e}")
            self._misses += 1
            return None

    def put(self: "Cacheable", content: ImageContent, result: ProcessedContent) -> None:
        """
        将处理结果存入缓存

        Args:
            content: 原始图片内容
            result: 处理结果
        """
        cache_key = self.get_cache_key(content)

        try:
            # 准备缓存数据
            cache_data = {
                "cache_key": cache_key,
                "content_hash": content.content_hash,
                "result": self._serialize_result(result),
                "timestamp": time.time()
            }

            # 存储到Redis，设置TTL
            cache_json = json.dumps(cache_data, ensure_ascii=False)
            self.redis_client.setex(cache_key, self.ttl_seconds, cache_json)

            logger.debug(f"Cached result to Redis for {cache_key}")

        except Exception as e:
            logger.error(f"Error putting to Redis cache: {e}")

    def invalidate(self: "Cacheable", content: ImageContent) -> bool:
        """
        使特定内容的缓存失效

        Args:
            content: 图片内容

        Returns:
            是否成功删除缓存条目
        """
        cache_key = self.get_cache_key(content)

        try:
            result = self.redis_client.delete(cache_key)
            if result > 0:
                logger.debug(f"Invalidated Redis cache for {cache_key}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error invalidating Redis cache: {e}")
            return False

    def clear_cache(self: "Cacheable") -> int:
        """
        清空所有缓存

        Returns:
            清除的缓存条目数
        """
        try:
            # 查找所有相关键
            pattern = f"{self.key_prefix}:image:*"
            keys = self.redis_client.keys(pattern)

            if keys:
                count = self.redis_client.delete(*keys)
                self._hits = 0
                self._misses = 0
                logger.info(f"Cleared {count} Redis cache entries")
                return count

            return 0

        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return 0

    def get_cache_stats(self: "Cacheable") -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计数据
        """
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0.0

        try:
            # 获取Redis信息
            pattern = f"{self.key_prefix}:image:*"
            keys = self.redis_client.keys(pattern)

            # 获取内存使用情况
            info = self.redis_client.info("memory")
            memory_used = info.get("used_memory", 0)

            return {
                "cache_type": "redis",
                "total_entries": len(keys),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "ttl_seconds": self.ttl_seconds,
                "key_prefix": self.key_prefix,
                "redis_memory_mb": round(memory_used / 1024 / 1024, 2)
            }

        except Exception as e:
            logger.error(f"Error getting Redis stats: {e}")
            return {
                "cache_type": "redis",
                "total_entries": 0,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(hit_rate, 4),
                "error": str(e)
            }

    def _serialize_result(self: "Cacheable", result: ProcessedContent) -> Dict[str, Any]:
        """序列化处理结果"""
        return result.to_dict()

    def _deserialize_result(self: "Cacheable", data: Dict[str, Any]) -> ProcessedContent:
        """反序列化处理结果"""
        return ProcessedContent.from_dict(data)