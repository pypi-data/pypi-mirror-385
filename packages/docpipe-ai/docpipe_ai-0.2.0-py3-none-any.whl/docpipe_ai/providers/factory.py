"""
Provider Factory for docpipe-ai.

This module provides a factory class for creating AI provider instances
with consistent configuration and error handling.
"""

import os
from typing import Dict, Any, Optional, Type, Union
import logging

from .base import BaseAIProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from ..data.config import AIProviderConfig

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    AI提供商工厂类

    提供统一的接口来创建不同类型的AI提供商实例。
    支持从配置、环境变量或直接参数创建实例。
    """

    # 注册的提供商类型
    _providers: Dict[str, Type[BaseAIProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[BaseAIProvider]) -> None:
        """
        注册新的AI提供商类型

        Args:
            name: 提供商名称
            provider_class: 提供商类
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered AI provider: {name}")

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """
        获取可用的提供商列表

        Returns:
            提供商名称列表
        """
        return list(cls._providers.keys())

    @classmethod
    def create_provider(cls,
                       provider_name: str,
                       model_name: Optional[str] = None,
                       api_key: Optional[str] = None,
                       api_base: Optional[str] = None,
                       config: Optional[AIProviderConfig] = None,
                       **kwargs) -> BaseAIProvider:
        """
        创建AI提供商实例

        Args:
            provider_name: 提供商名称
            model_name: 模型名称
            api_key: API密钥
            api_base: API基础URL
            config: 提供商配置对象
            **kwargs: 其他参数

        Returns:
            AI提供商实例

        Raises:
            ValueError: 如果提供商名称不支持
            ImportError: 如果缺少必需的依赖包
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"Unsupported provider: {provider_name}. Available providers: {available}")

        provider_class = cls._providers[provider_name]

        # 从配置或参数获取设置
        if config:
            model_name = model_name or config.model_name
            api_key = api_key or config.api_key
            api_base = api_base or config.api_base

            # 合并额外参数
            provider_specific_config = config.get_provider_config()
            kwargs = {**provider_specific_config, **kwargs}

        # 设置默认值
        if not model_name:
            model_name = cls._get_default_model(provider_name)

        # 从环境变量获取API密钥
        if not api_key:
            api_key = cls._get_api_key_from_env(provider_name)

        # 从环境变量获取API基础URL
        if not api_base:
            api_base = cls._get_api_base_from_env(provider_name)

        logger.info(f"Creating {provider_name} provider with model: {model_name}")

        try:
            provider = provider_class(
                model_name=model_name,
                api_key=api_key,
                api_base=api_base,
                **kwargs
            )

            # 验证配置
            validation_errors = provider.validate_config()
            if validation_errors:
                logger.warning(f"Provider configuration validation warnings: {validation_errors}")

            return provider

        except ImportError as e:
            logger.error(f"Missing dependencies for {provider_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to create {provider_name} provider: {e}")
            raise

    @classmethod
    def create_from_config(cls, config: AIProviderConfig) -> BaseAIProvider:
        """
        从配置对象创建AI提供商

        Args:
            config: AI提供商配置

        Returns:
            AI提供商实例
        """
        return cls.create_provider(
            provider_name=config.provider_name,
            model_name=config.model_name,
            api_key=config.api_key,
            api_base=config.api_base,
            config=config
        )

    @classmethod
    def create_from_env(cls,
                       provider_name: Optional[str] = None,
                       model_name: Optional[str] = None) -> BaseAIProvider:
        """
        从环境变量创建AI提供商

        Args:
            provider_name: 提供商名称，如果为None则从环境变量读取
            model_name: 模型名称，如果为None则从环境变量读取

        Returns:
            AI提供商实例
        """
        # 从环境变量获取提供商名称
        if not provider_name:
            provider_name = os.getenv("DOPIPE_AI_PROVIDER", "openai")

        # 从环境变量获取模型名称
        if not model_name:
            model_name = os.getenv("DOPIPE_AI_MODEL")

        return cls.create_provider(
            provider_name=provider_name,
            model_name=model_name
        )

    @classmethod
    def create_openai_provider(cls,
                             model: str = "gpt-4o-mini",
                             api_key: Optional[str] = None,
                             api_base: Optional[str] = None,
                             **kwargs) -> OpenAIProvider:
        """
        创建OpenAI提供商的便利方法

        Args:
            model: 模型名称
            api_key: API密钥
            api_base: API基础URL
            **kwargs: 其他参数

        Returns:
            OpenAI提供商实例
        """
        return cls.create_provider(
            provider_name="openai",
            model_name=model,
            api_key=api_key,
            api_base=api_base,
            **kwargs
        )

    @classmethod
    def create_anthropic_provider(cls,
                                 model: str = "claude-3-sonnet-20240229",
                                 api_key: Optional[str] = None,
                                 api_base: Optional[str] = None,
                                 **kwargs) -> AnthropicProvider:
        """
        创建Anthropic提供商的便利方法

        Args:
            model: 模型名称
            api_key: API密钥
            api_base: API基础URL
            **kwargs: 其他参数

        Returns:
            Anthropic提供商实例
        """
        return cls.create_provider(
            provider_name="anthropic",
            model_name=model,
            api_key=api_key,
            api_base=api_base,
            **kwargs
        )

    @classmethod
    def _get_default_model(cls, provider_name: str) -> str:
        """
        获取提供商的默认模型

        Args:
            provider_name: 提供商名称

        Returns:
            默认模型名称
        """
        default_models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-sonnet-20240229",
        }
        return default_models.get(provider_name, "default")

    @classmethod
    def _get_api_key_from_env(cls, provider_name: str) -> Optional[str]:
        """
        从环境变量获取API密钥

        Args:
            provider_name: 提供商名称

        Returns:
            API密钥
        """
        env_keys = {
            "openai": ["OPENAI_API_KEY"],
            "anthropic": ["ANTHROPIC_API_KEY"],
        }

        if provider_name not in env_keys:
            return None

        for env_key in env_keys[provider_name]:
            api_key = os.getenv(env_key)
            if api_key:
                return api_key

        return None

    @classmethod
    def _get_api_base_from_env(cls, provider_name: str) -> Optional[str]:
        """
        从环境变量获取API基础URL

        Args:
            provider_name: 提供商名称

        Returns:
            API基础URL
        """
        env_keys = {
            "openai": ["OPENAI_API_BASE", "OPENAI_BASE_URL"],
            "anthropic": ["ANTHROPIC_API_BASE"],
        }

        if provider_name not in env_keys:
            return None

        for env_key in env_keys[provider_name]:
            api_base = os.getenv(env_key)
            if api_base:
                return api_base

        return None

    @classmethod
    def test_provider(cls, provider: BaseAIProvider) -> Dict[str, Any]:
        """
        测试AI提供商连接和基本功能

        Args:
            provider: AI提供商实例

        Returns:
            测试结果
        """
        result = {
            "provider": str(provider),
            "connection_test": False,
            "text_generation_test": False,
            "capabilities": provider.get_model_info(),
            "errors": []
        }

        try:
            # 测试连接
            result["connection_test"] = provider.test_connection()
        except Exception as e:
            result["errors"].append(f"Connection test failed: {e}")

        try:
            # 测试文本生成
            test_prompt = "请用中文回答：1+1等于几？"
            response = provider.generate_text(test_prompt, max_tokens=50)
            result["text_generation_test"] = len(response.text.strip()) > 0
            result["sample_response"] = response.text[:100]  # 只保存前100个字符
        except Exception as e:
            result["errors"].append(f"Text generation test failed: {e}")

        return result

    @classmethod
    def get_provider_recommendations(cls, use_case: str = "image_processing") -> Dict[str, Any]:
        """
        根据使用场景获取提供商推荐

        Args:
            use_case: 使用场景

        Returns:
            推荐信息
        """
        recommendations = {
            "image_processing": {
                "recommended_providers": ["openai", "anthropic"],
                "models": {
                    "openai": {
                        "fast": "gpt-4o-mini",
                        "quality": "gpt-4o",
                        "budget": "gpt-3.5-turbo"
                    },
                    "anthropic": {
                        "fast": "claude-3-haiku-20240307",
                        "quality": "claude-3-opus-20240229",
                        "balanced": "claude-3-sonnet-20240229"
                    }
                },
                "notes": "Both providers support vision processing. OpenAI gpt-4o models offer good performance for image analysis."
            },
            "text_only": {
                "recommended_providers": ["openai", "anthropic"],
                "models": {
                    "openai": {
                        "fast": "gpt-3.5-turbo",
                        "quality": "gpt-4",
                        "latest": "gpt-4o"
                    },
                    "anthropic": {
                        "fast": "claude-3-haiku-20240307",
                        "quality": "claude-3-opus-20240229",
                        "balanced": "claude-3-sonnet-20240229"
                    }
                },
                "notes": "Both providers offer excellent text processing capabilities. Choice depends on specific requirements and cost considerations."
            }
        }

        return recommendations.get(use_case, recommendations["image_processing"])