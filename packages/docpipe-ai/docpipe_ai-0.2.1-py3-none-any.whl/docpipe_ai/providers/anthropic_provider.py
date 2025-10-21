"""
Anthropic Provider implementation for docpipe-ai.

This module provides Anthropic-specific implementation of the AI provider interface.
"""

import time
import base64
from typing import Dict, Any, Optional, List

from .base import BaseAIProvider, AIResponse, ProviderCapabilities
from ..data.content import ImageContent


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic AI提供商实现

    支持Claude系列模型，包括多模态模型（Claude 3等）。
    """

    def _initialize_client(self) -> None:
        """初始化Anthropic客户端"""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")

        client_kwargs = {}
        if self.api_key:
            client_kwargs["api_key"] = self.api_key
        if self.api_base:
            client_kwargs["base_url"] = self.api_base

        # 添加其他参数
        client_kwargs.update(self.extra_params)

        self.client = anthropic.Anthropic(**client_kwargs)

    def _get_capabilities(self) -> ProviderCapabilities:
        """获取Anthropic提供商能力信息"""
        return ProviderCapabilities(
            supports_images=True,
            supports_streaming=True,
            max_tokens=4096,
            max_image_size=5 * 1024 * 1024,  # 5MB
            supported_formats=["image/jpeg", "image/png", "image/gif", "image/webp"],
            supports_system_prompt=True,
            supports_temperature=True,
            supports_max_tokens=True
        )

    def generate_text(self: "AnthropicProvider",
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
            messages = [{"role": "user", "content": prompt}]

            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens or 1000,
            }

            if system_prompt:
                request_params["system"] = system_prompt
            if temperature is not None:
                request_params["temperature"] = temperature

            # 添加其他参数（排除Anthropic不支持的参数）
            anthropic_kwargs = {k: v for k, v in kwargs.items()
                              if k not in ["max_tokens", "temperature", "system"]}
            request_params.update(anthropic_kwargs)

            # 发送请求
            response = self.client.messages.create(**request_params)

            # 解析响应
            generated_text = response.content[0].text if response.content else ""
            response_time = time.time() - start_time

            return AIResponse(
                text=generated_text,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens if response.usage else None,
                    "completion_tokens": response.usage.output_tokens if response.usage else None,
                    "total_tokens": (response.usage.input_tokens + response.usage.output_tokens)
                                  if response.usage else None,
                },
                finish_reason=response.stop_reason,
                response_time=response_time
            )

        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {e}")
            raise

    def generate_text_with_image(self: "AnthropicProvider",
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

            # 确定媒体类型
            media_type = image_format
            if not media_type.startswith("image/"):
                media_type = f"image/{media_type}"

            # 构建消息内容
            content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_base64
                    }
                },
                {"type": "text", "text": prompt}
            ]

            # 构建消息
            messages = [{"role": "user", "content": content}]

            # 构建请求参数
            request_params = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": max_tokens or 1000,
            }

            if system_prompt:
                request_params["system"] = system_prompt
            if temperature is not None:
                request_params["temperature"] = temperature

            # 添加其他参数
            anthropic_kwargs = {k: v for k, v in kwargs.items()
                              if k not in ["max_tokens", "temperature", "system"]}
            request_params.update(anthropic_kwargs)

            # 发送请求
            response = self.client.messages.create(**request_params)

            # 解析响应
            generated_text = response.content[0].text if response.content else ""
            response_time = time.time() - start_time

            return AIResponse(
                text=generated_text,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens if response.usage else None,
                    "completion_tokens": response.usage.output_tokens if response.usage else None,
                    "total_tokens": (response.usage.input_tokens + response.usage.output_tokens)
                                  if response.usage else None,
                },
                finish_reason=response.stop_reason,
                response_time=response_time
            )

        except Exception as e:
            logger.error(f"Error generating text with image using Anthropic: {e}")
            raise

    def _requires_api_key(self: "AnthropicProvider") -> bool:
        """Anthropic需要API密钥"""
        return True

    def get_available_models(self: "AnthropicProvider") -> List[str]:
        """
        获取可用模型列表

        Returns:
            模型名称列表
        """
        # Anthropic的模型列表是固定的，没有公开的API来查询
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def estimate_tokens(self: "AnthropicProvider", text: str) -> int:
        """
        估算文本的token数量

        这是一个粗略估算，实际token数量可能会有差异

        Args:
            text: 文本内容

        Returns:
            估算的token数量
        """
        # Claude的token估算可能与GPT略有不同
        # 中文字符约2 tokens，英文单词约1.3 tokens
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        english_words = len(text.split()) - chinese_chars

        return int(chinese_chars * 2.0 + english_words * 1.3)

    def validate_image_format(self: "AnthropicProvider", image_format: str) -> bool:
        """
        验证图片格式是否受支持

        Args:
            image_format: 图片格式

        Returns:
            是否支持该格式
        """
        return image_format.lower() in [fmt.lower() for fmt in self.capabilities.supported_formats]

    def get_model_context_length(self: "AnthropicProvider", model: Optional[str] = None) -> int:
        """
        获取模型的上下文长度

        Args:
            model: 模型名称，如果为None则使用当前模型

        Returns:
            上下文长度（token数）
        """
        model = model or self.model_name

        # Claude 3系列的上下文长度
        context_lengths = {
            "claude-3-5-sonnet-20241022": 200000,
            "claude-3-5-haiku-20241022": 200000,
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
        }

        return context_lengths.get(model, 200000)  # 默认200k tokens