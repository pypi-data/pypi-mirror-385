"""
AI processing mixins for docpipe-ai.

This module provides Mixin implementations for different AI providers
and processing strategies. These mixins can be combined with any class that
implements the AIProcessable protocol to add AI processing capabilities.
"""

from typing import Protocol, Dict, Any, Optional, Union
import time
import base64
import logging
from abc import abstractmethod

from ..core.protocols import AIProcessable
from ..data.content import ImageContent, ProcessedContent, ProcessingMetrics, ProcessingStatus, ContentFormat

logger = logging.getLogger(__name__)

class OpenAIProcessingMixin:
    """
    OpenAI处理Mixin - 提供OpenAI API集成功能

    这个Mixin实现了与OpenAI API交互的通用逻辑，包括请求准备、
    响应解析和错误处理。
    """

    def __init__(self: "AIProcessable", ai_client, model_name: str = "gpt-4o-mini"):
        """
        初始化OpenAI处理

        Args:
            ai_client: OpenAI客户端实例
            model_name: 模型名称
        """
        self.ai_client = ai_client
        self.model_name = model_name
        self._request_count = 0

    def prepare_ai_request(self: "AIProcessable", content: ImageContent) -> Dict[str, Any]:
        """
        准备OpenAI请求数据

        Args:
            content: 图片内容

        Returns:
            OpenAI API请求数据
        """
        try:
            # 准备系统提示词
            system_prompt = self._get_system_prompt()

            # 准备用户提示词
            user_prompt = self._create_user_prompt(content)

            # 构建消息列表
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 如果是图片，添加图片数据
            if content.binary_data:
                image_message = self._create_image_message(content)
                if image_message:
                    # 对于图片，content必须是数组格式
                    messages[1]["content"] = [
                        {"type": "text", "text": user_prompt},
                        image_message
                    ]

            # 构建请求参数
            request_data = {
                "model": self.model_name,
                "messages": messages,
                "max_tokens": self._get_max_tokens(),
                "temperature": self._get_temperature(),
            }

            # 添加可选参数
            optional_params = self._get_optional_parameters()
            request_data.update(optional_params)

            self._request_count += 1
            return request_data

        except Exception as e:
            logger.error(f"Error preparing OpenAI request: {e}")
            raise

    def parse_ai_response(self: "AIProcessable", response: str) -> str:
        """
        解析OpenAI响应

        Args:
            response: OpenAI API响应文本

        Returns:
            解析后的文本
        """
        try:
            # 清理响应文本
            cleaned_text = response.strip()

            # 移除可能的JSON包装
            if cleaned_text.startswith('{"') and cleaned_text.endswith('"}'):
                try:
                    import json
                    parsed = json.loads(cleaned_text)
                    if isinstance(parsed, dict) and "text" in parsed:
                        cleaned_text = parsed["text"]
                except json.JSONDecodeError:
                    pass  # 如果不是有效JSON，保持原样

            # 清理多余的空白字符
            cleaned_text = ' '.join(cleaned_text.split())

            return cleaned_text

        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            raise

    def calculate_confidence(self: "AIProcessable", content: ImageContent, result: str) -> float:
        """
        计算置信度分数

        Args:
            content: 原始内容
            result: 处理结果

        Returns:
            置信度分数（0.0-1.0）
        """
        try:
            # 基于结果长度的基础置信度
            if len(result) < 10:
                base_confidence = 0.3
            elif len(result) < 50:
                base_confidence = 0.7
            elif len(result) < 200:
                base_confidence = 0.9
            else:
                base_confidence = 1.0

            # 基于内容大小的调整
            content_size = len(content.binary_data)
            if content_size < 1024:  # 小于1KB
                size_adjustment = 0.8
            elif content_size < 10 * 1024:  # 小于10KB
                size_adjustment = 0.9
            elif content_size < 100 * 1024:  # 小于100KB
                size_adjustment = 1.0
            else:  # 大图片
                size_adjustment = 0.85

            # 基于请求成功率的调整
            success_adjustment = min(1.0, self._request_count / max(1, self._get_error_count()))

            final_confidence = base_confidence * size_adjustment * success_adjustment
            return min(1.0, max(0.0, final_confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5

    def _get_system_prompt(self: "AIProcessable") -> str:
        """获取系统提示词"""
        return """你是一个专业的文档内容分析AI助手。你的任务是分析文档中的图片、表格等非文本内容，并生成清晰的中文描述。

要求：
- 使用中文进行描述
- 描述要简洁但详细
- 专注于主要内容和用途
- 使用中性、客观的语言
- 包含有助于理解内容的相关细节
- 避免无意义的填充内容"""

    def _create_user_prompt(self: "AIProcessable", content: ImageContent) -> str:
        """创建用户提示词"""
        prompt = f"请分析这张图片并提供清晰、简洁的中文描述。\n\n"
        prompt += f"图片信息：\n"
        prompt += f"- 页码：第 {content.page} 页\n"
        prompt += f"- 边界框：{content.bbox.to_list()}\n"
        prompt += f"- 大小：{len(content.binary_data)} 字节\n"

        if content.metadata:
            prompt += f"- 格式：{content.metadata.format.value}\n"
            if content.metadata.width_pixels and content.metadata.height_pixels:
                prompt += f"- 分辨率：{content.metadata.width_pixels}x{content.metadata.height_pixels}\n"

        prompt += f"\n请用中文描述这张图片展示的内容，保持客观中性的表达方式。"

        return prompt

    def _create_image_message(self: "AIProcessable", content: ImageContent) -> Optional[Dict[str, str]]:
        """创建图片消息"""
        try:
            # 编码图片数据
            image_base64 = base64.b64encode(content.binary_data).decode('utf-8')

            # 推断图片格式
            image_format = "image/jpeg"  # 默认JPEG
            if content.metadata and content.metadata.format != ContentFormat.UNKNOWN:
                format_mapping = {
                    ContentFormat.PNG: "image/png",
                    ContentFormat.JPEG: "image/jpeg",
                    ContentFormat.GIF: "image/gif",
                    ContentFormat.BMP: "image/bmp",
                    ContentFormat.WEBP: "image/webp",
                }
                image_format = format_mapping.get(content.metadata.format, "image/jpeg")

            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_format};base64,{image_base64}",
                    "detail": "low"  # 使用低分辨率以节省成本
                }
            }

        except Exception as e:
            logger.error(f"Error creating image message: {e}")
            return None

    def _get_max_tokens(self: "AIProcessable") -> int:
        """获取最大token数"""
        return 500  # 默认值，可以被子类重写

    def _get_temperature(self: "AIProcessable") -> float:
        """获取温度参数"""
        return 0.7  # 默认值，可以被子类重写

    def _get_optional_parameters(self: "AIProcessable") -> Dict[str, Any]:
        """获取可选参数"""
        return {}

    def _get_error_count(self: "AIProcessable") -> int:
        """获取错误计数"""
        return 0  # 默认值，可以被子类重写

    def _call_ai_service(self: "AIProcessable", request_data: Dict[str, Any]) -> str:
        """
        调用OpenAI API服务

        Args:
            request_data: OpenAI API请求数据

        Returns:
            AI响应文本
        """
        try:
            logger.debug(f"Calling OpenAI API with model: {self.model_name}")

            # 调用OpenAI API
            response = self.ai_client.chat.completions.create(**request_data)

            # 解析响应
            if response.choices and response.choices[0].message:
                generated_text = response.choices[0].message.content or ""

                # 记录请求统计
                self._request_count += 1
                logger.debug(f"OpenAI API call successful, request count: {self._request_count}")

                return generated_text
            else:
                raise ValueError("Empty response from OpenAI API")

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise


class AnthropicProcessingMixin:
    """
    Anthropic处理Mixin - 提供Anthropic API集成功能

    这个Mixin实现了与Anthropic Claude API交互的通用逻辑。
    """

    def __init__(self: "AIProcessable", ai_client, model_name: str = "claude-3-sonnet-20240229"):
        """
        初始化Anthropic处理

        Args:
            ai_client: Anthropic客户端实例
            model_name: 模型名称
        """
        self.ai_client = ai_client
        self.model_name = model_name
        self._request_count = 0

    def prepare_ai_request(self: "AIProcessable", content: ImageContent) -> Dict[str, Any]:
        """
        准备Anthropic请求数据

        Args:
            content: 图片内容

        Returns:
            Anthropic API请求数据
        """
        try:
            # 准备系统提示词
            system_prompt = self._get_system_prompt()

            # 准备用户提示词
            user_prompt = self._create_user_prompt(content)

            # 构建消息列表
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt}
                    ]
                }
            ]

            # 如果是图片，添加图片数据
            if content.binary_data:
                image_message = self._create_image_message(content)
                if image_message:
                    messages[0]["content"].append(image_message)

            # 构建请求参数
            request_data = {
                "model": self.model_name,
                "max_tokens": self._get_max_tokens(),
                "temperature": self._get_temperature(),
                "messages": messages,
            }

            # 添加系统提示词
            if system_prompt:
                request_data["system"] = system_prompt

            self._request_count += 1
            return request_data

        except Exception as e:
            logger.error(f"Error preparing Anthropic request: {e}")
            raise

    def parse_ai_response(self: "AIProcessable", response: str) -> str:
        """
        解析Anthropic响应

        Args:
            response: Anthropic API响应文本

        Returns:
            解析后的文本
        """
        try:
            # Anthropic直接返回文本内容
            cleaned_text = response.strip()
            return cleaned_text

        except Exception as e:
            logger.error(f"Error parsing Anthropic response: {e}")
            raise

    def calculate_confidence(self: "AIProcessable", content: ImageContent, result: str) -> float:
        """
        计算置信度分数

        Args:
            content: 原始内容
            result: 处理结果

        Returns:
            置信度分数（0.0-1.0）
        """
        # 类似OpenAI的实现
        try:
            if len(result) < 10:
                base_confidence = 0.4
            elif len(result) < 50:
                base_confidence = 0.8
            elif len(result) < 200:
                base_confidence = 0.95
            else:
                base_confidence = 1.0

            # 基于请求成功率的调整
            success_adjustment = min(1.0, self._request_count / max(1, self._get_error_count()))

            final_confidence = base_confidence * success_adjustment
            return min(1.0, max(0.0, final_confidence))

        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.6

    def _get_system_prompt(self: "AIProcessable") -> str:
        """获取系统提示词"""
        return """你是Claude，一个专业的文档内容分析AI助手。请用中文分析图片内容并提供清晰描述。"""

    def _create_user_prompt(self: "AIProcessable", content: ImageContent) -> str:
        """创建用户提示词"""
        return f"请分析第{content.page}页的这张图片内容，用中文进行描述。"

    def _create_image_message(self: "AIProcessable", content: ImageContent) -> Optional[Dict[str, Any]]:
        """创建图片消息"""
        # 类似OpenAI的实现
        try:
            image_base64 = base64.b64encode(content.binary_data).decode('utf-8')
            media_type = "image/jpeg"  # 默认格式

            if content.metadata and content.metadata.format != ContentFormat.UNKNOWN:
                format_mapping = {
                    ContentFormat.PNG: "image/png",
                    ContentFormat.JPEG: "image/jpeg",
                    ContentFormat.GIF: "image/gif",
                    ContentFormat.BMP: "image/bmp",
                    ContentFormat.WEBP: "image/webp",
                }
                media_type = format_mapping.get(content.metadata.format, "image/jpeg")

            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_base64
                }
            }

        except Exception as e:
            logger.error(f"Error creating image message: {e}")
            return None

    def _get_max_tokens(self: "AIProcessable") -> int:
        """获取最大token数"""
        return 500

    def _get_temperature(self: "AIProcessable") -> float:
        """获取温度参数"""
        return 0.7

    def _get_error_count(self: "AIProcessable") -> int:
        """获取错误计数"""
        return 0


class GenericAIProcessingMixin:
    """
    通用AI处理Mixin - 提供AI处理的基础框架

    这个Mixin提供了通用的AI处理流程，可以被特定的AI提供商Mixin继承。
    """

    def process_with_ai(self: "AIProcessable", content: ImageContent) -> ProcessedContent:
        """
        使用AI处理单个内容

        Args:
            content: 要处理的内容

        Returns:
            处理后的内容
        """
        start_time = time.time()
        retry_count = 0
        max_retries = self._get_max_retries()

        while retry_count <= max_retries:
            try:
                # 准备AI请求
                request_data = self.prepare_ai_request(content)

                # 调用AI服务
                response = self._call_ai_service(request_data)

                # 解析响应
                processed_text = self.parse_ai_response(response)

                # 计算置信度
                confidence = self.calculate_confidence(content, processed_text)

                # 创建处理指标
                metrics = ProcessingMetrics(
                    processing_time=time.time() - start_time,
                    confidence=confidence,
                    retry_count=retry_count,
                )

                # 返回成功结果
                return ProcessedContent(
                    original=content,
                    processed_text=processed_text,
                    status=ProcessingStatus.COMPLETED,
                    metrics=metrics
                )

            except Exception as e:
                retry_count += 1
                if retry_count <= max_retries:
                    logger.warning(f"AI processing attempt {retry_count} failed: {e}, retrying...")
                    time.sleep(self._get_retry_delay(retry_count))
                else:
                    logger.error(f"AI processing failed after {max_retries} attempts: {e}")

                    # 创建失败结果
                    error_metrics = ProcessingMetrics(
                        processing_time=time.time() - start_time,
                        confidence=0.0,
                        retry_count=retry_count,
                    )

                    return ProcessedContent.create_error_result(
                        original=content,
                        error_message=str(e),
                        processing_time=error_metrics.processing_time
                    )

    def _call_ai_service(self: "AIProcessable", request_data: Dict[str, Any]) -> str:
        """
        调用AI服务 - 需要子类实现

        Args:
            request_data: 请求数据

        Returns:
            AI响应文本
        """
        raise NotImplementedError("Subclass must implement _call_ai_service")

    def _get_max_retries(self: "AIProcessable") -> int:
        """获取最大重试次数"""
        return 3

    def _get_retry_delay(self: "AIProcessable", attempt: int) -> float:
        """获取重试延迟时间"""
        return min(60, 2 ** attempt)  # 指数退避