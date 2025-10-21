"""
Configuration classes for docpipe-ai.

This module defines configuration classes that control the behavior
of processing components in the Protocol-oriented architecture.
"""

from typing import Optional, Dict, Any, Literal
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum

# === Enums for Configuration ===

class ResponseFormatType(str, Enum):
    """Response format types for AI processing."""
    TEXT = "text"
    JSON = "json"
    STRUCTURED = "structured"

class ContentAnalysisType(str, Enum):
    """Types of content analysis to perform."""
    GENERAL = "general"
    CONTRACT = "contract"
    TABLE = "table"
    DOCUMENT = "document"
    CUSTOM = "custom"

# === Configuration Classes ===

@dataclass
class ProcessingConfig:
    """处理配置"""
    # Core processing settings
    max_concurrency: int = 5
    language: str = "zh"  # zh, en
    enable_caching: bool = True

    # AI provider settings
    ai_provider: str = "openai"
    model_name: str = "gpt-4o-mini"

    # Processing behavior
    retry_attempts: int = 3
    timeout_seconds: int = 30
    max_tokens: int = 500
    temperature: float = 0.7

    # Batch processing settings
    batch_size_strategy: str = "dynamic"  # dynamic, fixed, adaptive

    # Performance settings
    enable_metrics: bool = True
    log_level: str = "INFO"

    # Content filtering
    min_content_size: int = 100  # Minimum bytes to process
    max_content_size: Optional[int] = None  # Maximum bytes to process

    # Structured output settings
    response_format: ResponseFormatType = ResponseFormatType.TEXT
    content_analysis_type: ContentAnalysisType = ContentAnalysisType.GENERAL
    custom_schema: Optional[Dict[str, Any]] = None  # Custom JSON schema for structured output
    include_confidence_scores: bool = True
    include_processing_metadata: bool = True

    def __post_init__(self):
        """验证配置"""
        if self.max_concurrency < 1:
            raise ValueError("max_concurrency must be >= 1")
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts must be >= 0")
        if self.timeout_seconds < 1:
            raise ValueError("timeout_seconds must be >= 1")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if self.batch_size_strategy not in ["dynamic", "fixed", "adaptive"]:
            raise ValueError("batch_size_strategy must be one of: dynamic, fixed, adaptive")
        if self.language not in ["zh", "en"]:
            raise ValueError("language must be 'zh' or 'en'")
        if self.min_content_size < 0:
            raise ValueError("min_content_size must be >= 0")
        if self.max_content_size is not None and self.max_content_size <= 0:
            raise ValueError("max_content_size must be > 0 if specified")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "max_concurrency": self.max_concurrency,
            "language": self.language,
            "enable_caching": self.enable_caching,
            "ai_provider": self.ai_provider,
            "model_name": self.model_name,
            "retry_attempts": self.retry_attempts,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "batch_size_strategy": self.batch_size_strategy,
            "enable_metrics": self.enable_metrics,
            "log_level": self.log_level,
            "min_content_size": self.min_content_size,
            "max_content_size": self.max_content_size,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingConfig":
        """从字典创建配置"""
        return cls(**data)

    @classmethod
    def from_env(cls) -> "ProcessingConfig":
        """从环境变量创建配置"""
        import os

        return cls(
            max_concurrency=int(os.getenv("DOPIPE_AI_MAX_CONCURRENCY", "5")),
            language=os.getenv("DOPIPE_AI_LANGUAGE", "zh"),
            enable_caching=os.getenv("DOPIPE_AI_ENABLE_CACHING", "true").lower() == "true",
            ai_provider=os.getenv("DOPIPE_AI_PROVIDER", "openai"),
            model_name=os.getenv("DOPIPE_AI_MODEL", "gpt-4o-mini"),
            retry_attempts=int(os.getenv("DOPIPE_AI_RETRY_ATTEMPTS", "3")),
            timeout_seconds=int(os.getenv("DOPIPE_AI_TIMEOUT", "30")),
            max_tokens=int(os.getenv("DOPIPE_AI_MAX_TOKENS", "500")),
            temperature=float(os.getenv("DOPIPE_AI_TEMPERATURE", "0.7")),
            batch_size_strategy=os.getenv("DOPIPE_AI_BATCH_STRATEGY", "dynamic"),
            enable_metrics=os.getenv("DOPIPE_AI_ENABLE_METRICS", "true").lower() == "true",
            log_level=os.getenv("DOPIPE_AI_LOG_LEVEL", "INFO"),
        )

    @classmethod
    def create_fast_config(cls) -> "ProcessingConfig":
        """创建快速处理配置"""
        return cls(
            max_concurrency=10,
            language="zh",
            enable_caching=True,
            model_name="gpt-4o-mini",
            retry_attempts=1,
            timeout_seconds=15,
            max_tokens=200,
            temperature=0.5,
            batch_size_strategy="adaptive",
        )

    @classmethod
    def create_quality_config(cls) -> "ProcessingConfig":
        """创建高质量处理配置"""
        return cls(
            max_concurrency=2,
            language="zh",
            enable_caching=True,
            model_name="gpt-4o",
            retry_attempts=5,
            timeout_seconds=60,
            max_tokens=1000,
            temperature=0.3,
            batch_size_strategy="dynamic",
        )

    @classmethod
    def create_structured_output_config(cls,
                                       analysis_type: ContentAnalysisType = ContentAnalysisType.GENERAL,
                                       model_name: str = "gpt-4o") -> "ProcessingConfig":
        """创建结构化输出配置"""
        from .schemas import create_image_analysis_schema, create_contract_analysis_schema

        # Select appropriate schema based on analysis type
        if analysis_type == ContentAnalysisType.CONTRACT:
            custom_schema = create_contract_analysis_schema()
        elif analysis_type == ContentAnalysisType.TABLE:
            custom_schema = create_image_analysis_schema()  # Can be enhanced for table-specific schema
        else:
            custom_schema = create_image_analysis_schema()

        return cls(
            max_concurrency=3,
            language="zh",
            enable_caching=True,
            model_name=model_name,
            retry_attempts=3,
            timeout_seconds=45,
            max_tokens=1500,
            temperature=0.2,  # Lower temperature for more consistent structured output
            batch_size_strategy="dynamic",
            response_format=ResponseFormatType.STRUCTURED,
            content_analysis_type=analysis_type,
            custom_schema=custom_schema,
            include_confidence_scores=True,
            include_processing_metadata=True,
        )

    @classmethod
    def create_contract_analysis_config(cls) -> "ProcessingConfig":
        """创建合同分析专用配置"""
        return cls.create_structured_output_config(
            analysis_type=ContentAnalysisType.CONTRACT,
            model_name="gpt-4o"
        )

    @classmethod
    def create_table_extraction_config(cls) -> "ProcessingConfig":
        """创建表格提取专用配置"""
        return cls.create_structured_output_config(
            analysis_type=ContentAnalysisType.TABLE,
            model_name="gpt-4o-mini"
        )

@dataclass
class BatchConfig:
    """批次配置"""
    max_size: int = 100
    min_size: int = 1
    strategy: str = "dynamic"
    adaptive_threshold: int = 50
    max_wait_time: float = 30.0
    balance_factor: float = 0.8

    def __post_init__(self):
        """验证配置"""
        if self.max_size < self.min_size:
            raise ValueError("max_size must be >= min_size")
        if self.min_size < 1:
            raise ValueError("min_size must be >= 1")
        if self.strategy not in ["dynamic", "fixed", "adaptive"]:
            raise ValueError("strategy must be one of: dynamic, fixed, adaptive")
        if self.adaptive_threshold < 0:
            raise ValueError("adaptive_threshold must be >= 0")
        if self.max_wait_time < 0:
            raise ValueError("max_wait_time must be >= 0")
        if not 0 < self.balance_factor <= 1:
            raise ValueError("balance_factor must be between 0 and 1")

    def calculate_batch_size(self, remaining_items: int, processing_load: float = 0.0) -> int:
        """根据策略计算批次大小"""
        if self.strategy == "fixed":
            return min(self.max_size, remaining_items)

        elif self.strategy == "dynamic":
            if remaining_items <= 10:
                return remaining_items
            elif remaining_items <= 50:
                return min(10, remaining_items)
            elif remaining_items <= 200:
                return min(25, remaining_items)
            elif remaining_items <= 1000:
                return min(50, remaining_items)
            else:
                return min(self.max_size, remaining_items)

        elif self.strategy == "adaptive":
            # 基于负载的自适应策略
            base_size = self.calculate_dynamic_base_size(remaining_items)

            # 负载调整
            if processing_load > 0.8:
                # 高负载：减小批次
                return max(self.min_size, int(base_size * 0.7))
            elif processing_load < 0.3:
                # 低负载：增大批次
                return min(self.max_size, int(base_size * 1.3))
            else:
                # 中等负载：使用基础大小
                return base_size

        return self.min_size

    def calculate_dynamic_base_size(self, remaining_items: int) -> int:
        """计算动态基础批次大小"""
        if remaining_items <= self.adaptive_threshold:
            return remaining_items
        elif remaining_items <= 200:
            return min(25, remaining_items)
        elif remaining_items <= 1000:
            return min(50, remaining_items)
        else:
            return self.max_size

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "max_size": self.max_size,
            "min_size": self.min_size,
            "strategy": self.strategy,
            "adaptive_threshold": self.adaptive_threshold,
            "max_wait_time": self.max_wait_time,
            "balance_factor": self.balance_factor,
        }

@dataclass
class CacheConfig:
    """缓存配置"""
    enabled: bool = True
    max_size: int = 1000
    ttl_seconds: int = 3600
    key_prefix: str = "docpipe_ai"
    storage_backend: str = "memory"  # memory, redis, file
    persist_to_disk: bool = False
    disk_cache_dir: Optional[Path] = None

    def __post_init__(self):
        """验证配置"""
        if self.max_size < 1:
            raise ValueError("max_size must be >= 1")
        if self.ttl_seconds < 0:
            raise ValueError("ttl_seconds must be >= 0")
        if self.storage_backend not in ["memory", "redis", "file"]:
            raise ValueError("storage_backend must be one of: memory, redis, file")
        if self.persist_to_disk and self.disk_cache_dir is None:
            # 设置默认缓存目录
            self.disk_cache_dir = Path.home() / ".docpipe_ai" / "cache"

    def get_cache_key(self, content_hash: str, content_type: str = "image") -> str:
        """生成缓存键"""
        return f"{self.key_prefix}:{content_type}:{content_hash}"

    def is_cache_valid(self, cache_time: float, current_time: float) -> bool:
        """检查缓存是否有效"""
        return (current_time - cache_time) < self.ttl_seconds

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "enabled": self.enabled,
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds,
            "key_prefix": self.key_prefix,
            "storage_backend": self.storage_backend,
            "persist_to_disk": self.persist_to_disk,
            "disk_cache_dir": str(self.disk_cache_dir) if self.disk_cache_dir else None,
        }

@dataclass
class AIProviderConfig:
    """AI提供商配置"""
    provider_name: str = "openai"
    model_name: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    max_tokens: int = 500
    temperature: float = 0.7

    # Provider-specific settings
    openai_config: Dict[str, Any] = field(default_factory=dict)
    anthropic_config: Dict[str, Any] = field(default_factory=dict)
    custom_config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """验证配置"""
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.timeout < 1:
            raise ValueError("timeout must be >= 1")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be >= 1")
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")

    def get_provider_config(self) -> Dict[str, Any]:
        """获取特定提供商的配置"""
        if self.provider_name == "openai":
            return self.openai_config
        elif self.provider_name == "anthropic":
            return self.anthropic_config
        else:
            return self.custom_config

    def set_provider_config(self, config: Dict[str, Any]) -> None:
        """设置特定提供商的配置"""
        if self.provider_name == "openai":
            self.openai_config.update(config)
        elif self.provider_name == "anthropic":
            self.anthropic_config.update(config)
        else:
            self.custom_config.update(config)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "openai_config": self.openai_config,
            "anthropic_config": self.anthropic_config,
            "custom_config": self.custom_config,
        }

    @classmethod
    def create_openai_config(cls, **kwargs) -> "AIProviderConfig":
        """创建OpenAI配置"""
        return cls(
            provider_name="openai",
            model_name=kwargs.get("model_name", "gpt-4o-mini"),
            api_key=kwargs.get("api_key"),
            api_base=kwargs.get("api_base", "https://api.openai.com/v1"),
            **{k: v for k, v in kwargs.items() if k not in ["provider_name", "model_name", "api_key", "api_base"]}
        )

    @classmethod
    def create_anthropic_config(cls, **kwargs) -> "AIProviderConfig":
        """创建Anthropic配置"""
        return cls(
            provider_name="anthropic",
            model_name=kwargs.get("model_name", "claude-3-sonnet-20240229"),
            api_key=kwargs.get("api_key"),
            api_base=kwargs.get("api_base", "https://api.anthropic.com"),
            **{k: v for k, v in kwargs.items() if k not in ["provider_name", "model_name", "api_key", "api_base"]}
        )