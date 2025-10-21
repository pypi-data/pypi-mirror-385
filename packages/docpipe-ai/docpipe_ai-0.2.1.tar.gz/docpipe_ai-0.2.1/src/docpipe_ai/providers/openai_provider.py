"""
OpenAI Provider implementation for docpipe-ai.

This module provides OpenAI-specific implementation of the AI provider interface.
"""

import time
import base64
import logging
from typing import Dict, Any, Optional, List

from .base import BaseAIProvider, AIResponse, ProviderCapabilities
from ..data.content import ImageContent

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI AI提供商实现

    支持OpenAI GPT系列模型，包括多模态模型（GPT-4V等）。
    """

    def _initialize_client(self) -> None:
        """初始化OpenAI客户端"""
        try:
            import openai
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        client_kwargs = {}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key
        if self.api_base:
            client_kwargs["base_url"] = self.api_base

        # 添加其他参数，但只保留OpenAI支持的参数
        supported_params = ['organization', 'timeout', 'max_retries', 'default_headers']
        for key, value in self.extra_params.items():
            if key in supported_params:
                client_kwargs[key] = value

        self.client = openai.OpenAI(**client_kwargs)

    def _get_capabilities(self) -> ProviderCapabilities:
        """获取OpenAI提供商能力信息"""
        return ProviderCapabilities(
            supports_images=True,
            supports_streaming=True,
            max_tokens=4096,
            max_image_size=20 * 1024 * 1024,  # 20MB
            supported_formats=["image/jpeg", "image/png", "image/gif", "image/webp"],
            supports_system_prompt=True,
            supports_temperature=True,
            supports_max_tokens=True
        )

    def generate_text(self: "OpenAIProvider",
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
        start_time = time.time()

        try:
            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
            }

            if max_tokens is not None:
                request_params["max_tokens"] = max_tokens
            if temperature is not None:
                request_params["temperature"] = temperature

            # 添加其他参数
            request_params.update(kwargs)

            # 发送请求
            response = self.client.chat.completions.create(**request_params)

            # 解析响应
            choice = response.choices[0]
            generated_text = choice.message.content or ""
            response_time = time.time() - start_time

            return AIResponse(
                text=generated_text,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None,
                finish_reason=choice.finish_reason,
                response_time=response_time
            )

        except Exception as e:
            logger.error(f"Error generating text with OpenAI: {e}")
            raise

    def generate_text_with_image(self: "OpenAIProvider",
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
        start_time = time.time()

        try:
            # 检查图片大小
            if len(image_data) > self.capabilities.max_image_size:
                raise ValueError(f"Image size {len(image_data)} exceeds maximum {self.capabilities.max_image_size}")

            # 编码图片
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"{image_format};base64,{image_base64}"

            # 构建消息内容
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{image_url}", "detail": "low"}}
            ]

            # 构建消息
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_content})

            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
            }

            if max_tokens is not None:
                request_params["max_tokens"] = max_tokens
            if temperature is not None:
                request_params["temperature"] = temperature

            # 添加其他参数
            request_params.update(kwargs)

            # 发送请求
            response = self.client.chat.completions.create(**request_params)

            # 解析响应
            choice = response.choices[0]
            generated_text = choice.message.content or ""
            response_time = time.time() - start_time

            return AIResponse(
                text=generated_text,
                model=response.model,
                usage=response.usage.model_dump() if response.usage else None,
                finish_reason=choice.finish_reason,
                response_time=response_time
            )

        except Exception as e:
            logger.error(f"Error generating text with image using OpenAI: {e}")
            raise

    def _requires_api_key(self: "OpenAIProvider") -> bool:
        """OpenAI通常需要API密钥"""
        # 对于本地部署或特殊API端点可能不需要
        return not (self.api_base and ("localhost" in self.api_base or "127.0.0.1" in self.api_base))

    def get_available_models(self: "OpenAIProvider") -> List[str]:
        """
        获取可用模型列表

        Returns:
            模型名称列表
        """
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id.lower()]
        except Exception as e:
            logger.warning(f"Failed to retrieve available models: {e}")
            # 返回已知的常见模型
            return [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4-turbo",
                "gpt-4-vision-preview",
                "gpt-3.5-turbo",
            ]

    def estimate_tokens(self: "OpenAIProvider", text: str) -> int:
        """
        估算文本的token数量

        这是一个粗略估算，实际token数量可能会有差异

        Args:
            text: 文本内容

        Returns:
            估算的token数量
        """
        # 简单的token估算：中文字符约1.5 tokens，英文单词约1.3 tokens
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_words = len(text.split()) - chinese_chars  # 粗略估算

        return int(chinese_chars * 1.5 + english_words * 1.3)

    def validate_image_format(self: "OpenAIProvider", image_format: str) -> bool:
        """
        验证图片格式是否受支持

        Args:
            image_format: 图片格式

        Returns:
            是否支持该格式
        """
        return image_format.lower() in [fmt.lower() for fmt in self.capabilities.supported_formats]